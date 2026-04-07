"""Wiki Query Engine — wiki-first retrieval with RAG fallback.

Query flow:
  1. Search the wiki index + page content for relevant pages.
  2. If wiki results are rich enough (above confidence threshold), synthesize
     an answer purely from wiki content.
  3. If wiki coverage is thin, fall back to the traditional vector-RAG
     pipeline (``retrieve_context``) and merge the two sources for the final
     answer.

This module is designed as a drop-in enhancement to the existing retrieval
path.  Other code can call ``query()`` instead of ``retrieve_context()``
directly and get the wiki-first benefit transparently.
"""

import logging

from src.infrastructure.knowledge.wiki_manager import WikiManager

logger = logging.getLogger(__name__)

# Minimum number of wiki search hits to consider wiki coverage "sufficient"
WIKI_CONFIDENCE_THRESHOLD = 2
# Minimum aggregate score across matches
WIKI_SCORE_THRESHOLD = 0.4


class WikiQueryEngine:
    """Hybrid query engine: LLM-Wiki primary, vector-RAG fallback."""

    def __init__(
        self,
        tenant_id: str,
        notebook_id: str | None = None,
    ):
        self.tenant_id = tenant_id
        self.notebook_id = notebook_id
        self.wiki = WikiManager(tenant_id, notebook_id)

    # -- public API ---------------------------------------------------------

    async def query(
        self,
        query_text: str,
        *,
        top_k: int = 8,
        subject_id: str | None = None,
        max_wiki_pages: int = 5,
    ) -> dict:
        """Run a hybrid retrieval: wiki-first, RAG-fallback.

        Returns:
            {
                "source": "wiki" | "rag" | "hybrid",
                "wiki_results": [...],
                "rag_results": [...],
                "context_chunks": [...],   # unified list ready for the LLM
            }
        """
        # Step 1: search the wiki
        wiki_hits = self.wiki.search_pages(query_text, max_results=max_wiki_pages)
        wiki_coverage = self._assess_wiki_coverage(wiki_hits)

        context_chunks: list[dict] = []

        if wiki_coverage == "sufficient":
            # Wiki has enough — read the matched pages for full context
            page_names = [hit["page"] for hit in wiki_hits]
            wiki_context = self.wiki.read_pages_for_context(page_names)
            context_chunks = self._wiki_to_context_chunks(wiki_hits, wiki_context)

            self.wiki.append_log("query_wiki", f"'{query_text[:80]}' — {len(wiki_hits)} hits, wiki-only")
            return {
                "source": "wiki",
                "wiki_results": wiki_hits,
                "rag_results": [],
                "context_chunks": context_chunks,
            }

        # Step 2: wiki coverage is insufficient — invoke RAG fallback
        rag_results = await self._rag_fallback(
            query_text, top_k=top_k, subject_id=subject_id,
        )

        if wiki_hits:
            # Hybrid: combine wiki + RAG
            page_names = [hit["page"] for hit in wiki_hits]
            wiki_context = self.wiki.read_pages_for_context(page_names, max_chars=4000)
            wiki_chunks = self._wiki_to_context_chunks(wiki_hits, wiki_context)
            context_chunks = wiki_chunks + rag_results

            self.wiki.append_log(
                "query_hybrid",
                f"'{query_text[:80]}' — {len(wiki_hits)} wiki + {len(rag_results)} RAG",
            )
            return {
                "source": "hybrid",
                "wiki_results": wiki_hits,
                "rag_results": rag_results,
                "context_chunks": context_chunks,
            }

        # Purely RAG
        self.wiki.append_log("query_rag_fallback", f"'{query_text[:80]}' — RAG only")
        return {
            "source": "rag",
            "wiki_results": [],
            "rag_results": rag_results,
            "context_chunks": rag_results,
        }

    # -- wiki assessment ----------------------------------------------------

    def _assess_wiki_coverage(self, hits: list[dict]) -> str:
        """Determine whether wiki results are sufficient or need RAG supplement."""
        if len(hits) < WIKI_CONFIDENCE_THRESHOLD:
            return "insufficient"
        avg_score = sum(h.get("score", 0) for h in hits) / max(len(hits), 1)
        if avg_score < WIKI_SCORE_THRESHOLD:
            return "insufficient"
        return "sufficient"

    # -- RAG fallback -------------------------------------------------------

    async def _rag_fallback(
        self,
        query_text: str,
        *,
        top_k: int = 8,
        subject_id: str | None = None,
    ) -> list[dict]:
        """Call the existing vector-RAG retrieval pipeline."""
        try:
            from src.infrastructure.vector_store.retrieval import retrieve_context
            return await retrieve_context(
                query=query_text,
                tenant_id=self.tenant_id,
                top_k=top_k,
                subject_id=subject_id,
                notebook_id=self.notebook_id,
            )
        except Exception as exc:
            logger.warning("RAG fallback failed: %s", exc)
            return []

    # -- format helpers -----------------------------------------------------

    @staticmethod
    def _wiki_to_context_chunks(hits: list[dict], wiki_context: str) -> list[dict]:
        """Convert wiki search hits into the standard context-chunk format
        used by the rest of the codebase (same shape as RAG chunks)."""
        chunks: list[dict] = []
        # Split the concatenated context back into per-page segments
        segments = wiki_context.split("\n\n---")
        for i, segment in enumerate(segments):
            segment = segment.strip().lstrip("- ")
            if not segment:
                continue
            # Try to match back to a hit
            page_name = hits[i]["page"] if i < len(hits) else "wiki"
            score = hits[i].get("score", 1.0) if i < len(hits) else 1.0
            chunks.append({
                "text": segment[:3000],
                "citation": f"[wiki:{page_name}]",
                "source": f"wiki/{page_name}.md",
                "page": "1",
                "section": page_name,
                "score": round(score, 3),
                "vector_score": 0.0,
                "rerank_score": 0.0,
                "document_id": "",
                "compressed": False,
                "wiki_source": True,
            })
        return chunks


# ---------------------------------------------------------------------------
# Convenience function matching existing retrieval API
# ---------------------------------------------------------------------------

async def retrieve_with_wiki(
    query: str,
    tenant_id: str,
    top_k: int = 8,
    subject_id: str | None = None,
    notebook_id: str | None = None,
) -> list[dict]:
    """Drop-in replacement for ``retrieve_context`` that adds wiki-first logic."""
    engine = WikiQueryEngine(tenant_id, notebook_id)
    result = await engine.query(
        query,
        top_k=top_k,
        subject_id=subject_id,
    )
    return result["context_chunks"]
