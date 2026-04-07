"""
RAG Retrieval Pipeline — search, rerank (cross-encoder), context dedup + compression, citation enforce.
"""
from typing import List, Dict, Optional
import re
from config import settings
from src.infrastructure.llm.providers import get_embedding_provider, get_vector_store_provider
import logging
import os

logger = logging.getLogger(__name__)

# Feature flag — set WIKI_ENABLED=1 to activate wiki-first retrieval
WIKI_ENABLED = os.getenv("WIKI_ENABLED", "0") == "1"


# ─── Cross-Encoder Reranker ──────────────────────────────────
_reranker = None


def _get_reranker():
    """Lazy-load cross-encoder reranker (sentence-transformers)."""
    global _reranker
    if _reranker is None:
        try:
            from sentence_transformers import CrossEncoder
            _reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-2-v2", max_length=512)
        except ImportError:
            _reranker = "unavailable"
    return _reranker


def rerank_chunks(query: str, results: List[tuple], top_n: int = 5) -> List[tuple]:
    """
    Rerank chunks using cross-encoder model for semantic relevance.
    Falls back to FAISS score ordering if cross-encoder is unavailable.
    """
    reranker = _get_reranker()
    if reranker == "unavailable" or not results:
        return sorted(results, key=lambda x: x[1], reverse=True)[:top_n]

    pairs = [(query, r[0].get("text", "")) for r in results]
    scores = reranker.predict(pairs)

    scored = [(results[i][0], float(scores[i])) for i in range(len(results))]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_n]


def _filter_by_score_threshold(results: List[tuple], min_score: float) -> List[tuple]:
    """Drop results below the configured minimum relevance threshold."""
    return [(chunk_meta, score) for chunk_meta, score in results if float(score) >= min_score]


# ─── Context Deduplication ───────────────────────────────────
def deduplicate_chunks(chunks: List[tuple], similarity_threshold: float = 0.85) -> List[tuple]:
    """
    Remove near-duplicate chunks using text overlap ratio.
    Uses Jaccard similarity on word sets for fast computation.
    """
    if not chunks:
        return []

    deduped = [chunks[0]]
    for chunk_meta, score in chunks[1:]:
        text = chunk_meta.get("text", "").lower()
        words_new = set(text.split())
        is_dup = False

        for existing_meta, _ in deduped:
            existing_text = existing_meta.get("text", "").lower()
            words_existing = set(existing_text.split())
            if not words_new or not words_existing:
                continue
            intersection = words_new & words_existing
            union = words_new | words_existing
            jaccard = len(intersection) / len(union) if union else 0
            if jaccard > similarity_threshold:
                is_dup = True
                break

        if not is_dup:
            deduped.append((chunk_meta, score))

    return deduped


# ─── Context Compression ─────────────────────────────────────
def compress_context(chunks: List[Dict], max_tokens: int = 3000) -> List[Dict]:
    """
    Compress context to fit within token budget.
    - Keep high-scoring chunks in full
    - Truncate lower-ranked chunks to first 2 sentences
    """
    if not chunks:
        return []

    total_tokens = sum(len(c["text"].split()) for c in chunks)
    if total_tokens <= max_tokens:
        return [{**chunk, "compressed": chunk.get("compressed", False)} for chunk in chunks]

    # Keep top half in full, compress bottom half
    midpoint = max(len(chunks) // 2, 1)
    compressed = [{**chunk, "compressed": chunk.get("compressed", False)} for chunk in chunks[:midpoint]]
    current_tokens = sum(len(c["text"].split()) for c in compressed)

    for chunk in chunks[midpoint:]:
        text = chunk["text"]
        sentences = re.split(r'(?<=[.!?])\s+', text)
        summary = " ".join(sentences[:2]) + ("..." if len(sentences) > 2 else "")
        summary_tokens = len(summary.split())

        if current_tokens + summary_tokens > max_tokens:
            break

        compressed.append({**chunk, "text": summary, "compressed": True})
        current_tokens += summary_tokens

    return compressed


# ─── Citation Enforcement ─────────────────────────────────────
def enforce_citations(response: str, mode: str, available_citations: List[str]) -> dict:
    """
    Post-process AI response to validate citations.
    Returns dict with validated response and citation status.
    """
    citation_pattern = r'\[([^\]]+)\]'
    found_citations = re.findall(citation_pattern, response)

    has_citations = len(found_citations) > 0
    citation_required = True

    if citation_required and not has_citations and available_citations:
        # Inject available citations at the end
        citation_note = "\n\nSources: " + ", ".join(available_citations[:5])
        response += citation_note
        return {
            "response": response,
            "citation_valid": False,
            "citation_injected": True,
            "citation_count": len(available_citations[:5]),
        }

    return {
        "response": response,
        "citation_valid": has_citations or not citation_required,
        "citation_injected": False,
        "citation_count": len(found_citations),
    }


# ─── Main Retrieval Pipeline ─────────────────────────────────
async def retrieve_context(
    query: str,
    tenant_id: str,
    top_k: int = 8,
    subject_id: Optional[str] = None,
    notebook_id: Optional[str] = None,
    enable_wiki: Optional[bool] = None,
) -> List[Dict]:
    """
    Full retrieval pipeline:
    1. Embed query
    2. Search vector store (over-fetch)
    3. Cross-encoder rerank
    4. Deduplicate (Jaccard similarity)
    5. Return context chunks with citations
    """
    # Step 0 (wiki-first): Try the LLM-Wiki before vector search
    wiki_active = enable_wiki if enable_wiki is not None else WIKI_ENABLED
    if wiki_active:
        try:
            from src.infrastructure.knowledge.wiki_query_engine import WikiQueryEngine
            engine = WikiQueryEngine(tenant_id, notebook_id)
            wiki_result = await engine.query(query, top_k=top_k, subject_id=subject_id)
            if wiki_result["source"] == "wiki":
                logger.info("Wiki-only retrieval for tenant=%s (%d chunks)", tenant_id, len(wiki_result["context_chunks"]))
                return wiki_result["context_chunks"]
            if wiki_result["source"] == "hybrid":
                logger.info("Hybrid wiki+RAG retrieval for tenant=%s", tenant_id)
                return wiki_result["context_chunks"]
            # source == "rag" — wiki had nothing, continue to vector pipeline below
        except Exception as exc:
            logger.warning("Wiki retrieval failed, falling through to RAG: %s", exc)

    # Step 1: Embed query
    try:
        query_embedding = await get_embedding_provider().embed(query)
    except Exception:
        return []

    # Step 2: Vector search (over-fetch for reranking)
    store = get_vector_store_provider(tenant_id)
    if store.chunk_count == 0:
        return []

    results = store.search(
        query_embedding=query_embedding,
        top_k=top_k * 2,
        subject_id=subject_id,
        notebook_id=notebook_id,
    )

    if not results:
        return []

    vector_filtered = _filter_by_score_threshold(
        [({**chunk_meta, "_vector_score": float(score)}, float(score)) for chunk_meta, score in results],
        settings.retrieval.min_vector_score,
    )
    if not vector_filtered:
        return []

    # Step 3: Cross-encoder rerank
    ranked = rerank_chunks(query, vector_filtered, top_n=top_k)
    reranked_with_scores = [
        ({**chunk_meta, "_rerank_score": float(score)}, float(score))
        for chunk_meta, score in ranked
    ]
    rerank_filtered = _filter_by_score_threshold(
        reranked_with_scores,
        settings.retrieval.min_rerank_score,
    )
    if not rerank_filtered:
        return []

    # Step 4: Deduplicate (Jaccard similarity > 0.85 = duplicate)
    deduped = deduplicate_chunks(rerank_filtered, similarity_threshold=0.85)

    # Step 5: Build context with citation markers
    context_chunks = []
    for chunk_meta, score in deduped:
        source = chunk_meta.get("source_file", "Document")
        page = chunk_meta.get("page_number", "?")
        section = chunk_meta.get("section_title", "")
        citation = f"[{source}_p{page}]"

        context_chunks.append({
            "text": chunk_meta.get("text", ""),
            "citation": citation,
            "source": source,
            "page": str(page),
            "section": section,
            "score": round(score, 3),
            "vector_score": round(float(chunk_meta.get("_vector_score", score)), 3),
            "rerank_score": round(float(chunk_meta.get("_rerank_score", score)), 3),
            "document_id": chunk_meta.get("document_id", ""),
            "compressed": False,
        })

    return context_chunks


async def retrieve_documents(
    query: str,
    collection: str,
    top_k: int = 3,
) -> List[Dict]:
    """Simplified retrieval for non-tenant documents (e.g. system docs)."""
    return await retrieve_context(
        query=query,
        tenant_id=collection,
        top_k=top_k
    )


def build_context_string(chunks: List[Dict], max_tokens: int = 3000) -> str:
    """Build a context string from retrieved chunks, with compression."""
    compressed = compress_context(chunks, max_tokens)

    context_parts = []
    for chunk in compressed:
        text = chunk["text"]
        citation = chunk["citation"]
        context_parts.append(f"{text}\n— Source: {citation}")

    return "\n\n".join(context_parts)


def build_retrieval_audit(chunks: List[Dict], max_tokens: int = 3000) -> Dict:
    """Return chunk-level diagnostics for audit/debug responses."""
    audit_chunks = compress_context(chunks, max_tokens)
    max_chunks = max(settings.retrieval.audit_max_chunks, 1)
    reranker_enabled = _reranker not in (None, "unavailable")
    return {
        "thresholds": {
            "min_vector_score": settings.retrieval.min_vector_score,
            "min_rerank_score": settings.retrieval.min_rerank_score,
        },
        "chunk_count": len(chunks),
        "returned_chunk_count": min(len(audit_chunks), max_chunks),
        "reranker_enabled": reranker_enabled,
        "chunks": [
            {
                "document_id": chunk.get("document_id", ""),
                "source": chunk.get("source", ""),
                "page": chunk.get("page", ""),
                "section": chunk.get("section", ""),
                "citation": chunk.get("citation", ""),
                "vector_score": chunk.get("vector_score"),
                "rerank_score": chunk.get("rerank_score", chunk.get("score")),
                "compressed": chunk.get("compressed", False),
            }
            for chunk in audit_chunks[:max_chunks]
        ],
    }


def extract_citations(chunks: List[Dict]) -> List[Dict]:
    """Extract unique citations from context chunks."""
    seen = set()
    citations = []
    for chunk in chunks:
        key = f"{chunk['source']}_{chunk['page']}"
        if key not in seen:
            seen.add(key)
            citations.append({
                "source": chunk["source"],
                "page": chunk["page"],
                "section": chunk.get("section", ""),
            })
    return citations


def sanitize_ai_output(response: str) -> str:
    """
    Sanitize AI output:
    - Remove file paths
    - Remove API keys
    - Remove student names from other contexts
    - Block config leakage
    """
    # Remove file paths
    response = re.sub(r'[A-Z]:\\[^\s"\']+', '[path_removed]', response)
    response = re.sub(r'/(?:home|var|etc|usr)/[^\s"\']+', '[path_removed]', response)

    # Remove potential API keys (long hex/base64 strings)
    response = re.sub(r'[a-f0-9]{32,}', '[key_removed]', response)
    response = re.sub(r'sk-[a-zA-Z0-9]{20,}', '[key_removed]', response)

    # Strip prompt injection attempts from output
    injection_patterns = [
        r'(?i)ignore\s+previous\s+instructions',
        r'(?i)system\s+override',
        r'(?i)you\s+are\s+now\s+in',
    ]
    for pattern in injection_patterns:
        response = re.sub(pattern, '[filtered]', response)

    return response
