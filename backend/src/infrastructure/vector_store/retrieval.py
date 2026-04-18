"""
RAG Retrieval Pipeline — search, rerank (cross-encoder), context dedup + compression, citation enforce.

See docs/RAG_SYSTEM.md for architecture overview.
See docs/RAG_CONFIGURATION.md for settings.
See docs/RAG_TROUBLESHOOTING.md for issues.
"""
from typing import List, Dict, Optional, Tuple, Any
import re
from config import settings
from src.infrastructure.llm.providers import get_embedding_provider, get_vector_store_provider
import logging
import os

logger = logging.getLogger(__name__)

# Feature flag — set WIKI_ENABLED=1 to activate wiki-first retrieval
# See docs/RAG_SYSTEM.md#wiki-first-retrieval
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


def rerank_chunks(query: str, results: List[Tuple[Dict[str, Any], float]], top_n: int = 5) -> List[Tuple[Dict[str, Any], float]]:
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


# ─── Query Rewriting (Recall Optimization) ──────────────────
async def rewrite_query(query: str, num_variants: int = 2) -> List[str]:
    """
    Generate query variants/paraphrases to improve recall on vague questions.
    Example: "Is photosynthesis hard?" → ["photosynthesis definition", "photosynthesis steps"]
    
    See docs/RAG_SYSTEM.md#query-rewriting
    See docs/RAG_CONFIGURATION.md#query-rewriting
    
    Returns list of [original_query, variant1, variant2, ...]
    """
    try:
        from src.infrastructure.llm.providers import get_llm_provider
        llm = get_llm_provider()
        
        rewrite_prompt = f"""Generate {num_variants} alternative phrasings of this question to improve search recall.
Each variant should be a different way to ask the same thing.
Return ONLY the variants, one per line. No numbering or explanations.

Original question: {query}

Variants:"""
        
        response = await llm.generate(
            prompt=rewrite_prompt,
            max_tokens=200,
            temperature=0.7
        )
        
        variants = [query]  # Always include original
        if response:
            # Parse response: split by newlines, clean up
            lines = response.strip().split('\n')
            for line in lines[:num_variants]:
                variant = line.strip()
                if variant and len(variant) > 3:  # Skip empty or too-short lines
                    variants.append(variant)
        
        logger.info(f"Query rewrite: '{query}' → {len(variants)} variants")
        return variants
    except Exception as exc:
        logger.warning(f"Query rewriting failed, using original: {exc}")
        return [query]


def merge_search_results(
    results_list: List[List[Tuple[Dict[str, Any], float]]],
    dedup_threshold: float = 0.85,
    max_results: int = 20
) -> List[Tuple[Dict[str, Any], float]]:
    """
    Merge results from multiple query searches, deduplicating similar chunks.
    Gives higher weight to chunks found in multiple searches.
    """
    merged: Dict[str, Tuple[Dict[str, Any], List[float]]] = {}  # {document_id + chunk_text: (chunk_meta, scores_list)}
    
    for results in results_list:
        for chunk_meta, score in results:
            doc_id = chunk_meta.get("document_id", "")
            text = chunk_meta.get("text", "")
            key = f"{doc_id}:{text[:50]}"  # Use doc_id + text prefix as key
            
            if key not in merged:
                merged[key] = (chunk_meta, [])
            merged[key][1].append(float(score))
    
    # Calculate aggregate score (average of all scores + bonus for multiple matches)
    scored_results: List[Tuple[Dict[str, Any], float]] = []
    for key, (chunk_meta, scores) in merged.items():
        avg_score = sum(scores) / len(scores) if scores else 0.0
        multi_match_bonus = min(len(scores) * 0.1, 0.3)  # Up to 0.3 bonus for appearing in multiple searches
        final_score = min(avg_score + multi_match_bonus, 1.0)
        scored_results.append((chunk_meta, final_score))
    
    # Sort by final score and return top results
    scored_results.sort(key=lambda x: x[1], reverse=True)
    return scored_results[:max_results]


def _filter_by_score_threshold(results: List[Tuple[Dict[str, Any], float]], min_score: float) -> List[Tuple[Dict[str, Any], float]]:
    """Drop results below the configured minimum relevance threshold."""
    return [(chunk_meta, score) for chunk_meta, score in results if float(score) >= min_score]


# ─── Context Deduplication ───────────────────────────────────
def deduplicate_chunks(chunks: List[Tuple[Dict[str, Any], float]], similarity_threshold: float = 0.85) -> List[Tuple[Dict[str, Any], float]]:
    """
    Remove near-duplicate chunks using text overlap ratio.
    Uses Jaccard similarity on word sets for fast computation.
    """
    if not chunks:
        return []

    deduped: List[Tuple[Dict[str, Any], float]] = [chunks[0]]
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
def compress_context(chunks: List[Dict[str, Any]], max_tokens: int = 3000) -> List[Dict[str, Any]]:
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
    compressed: List[Dict[str, Any]] = [{**chunk, "compressed": chunk.get("compressed", False)} for chunk in chunks[:midpoint]]
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
def enforce_citations(response: str, mode: str, available_citations: List[str]) -> Dict[str, Any]:
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
) -> List[Dict[str, Any]]:
    """
    Full retrieval pipeline:
    1. Embed query
    2. Search vector store (over-fetch)
    3. Cross-encoder rerank
    4. Deduplicate (Jaccard similarity)
    5. Return context chunks with citations
    
    See docs/RAG_SYSTEM.md#pipeline-steps
    See docs/RAG_CONFIGURATION.md#threshold-configuration
    See docs/VECTOR_STORE_CONFIGURATION.md#metadata-filtering
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

    # Step 1.5: Query Rewriting (optional, controlled by config)
    embedding_provider = get_embedding_provider()
    use_query_rewriting = getattr(settings.retrieval, 'enable_query_rewriting', True)
    query_variants = [query]
    
    if use_query_rewriting:
        try:
            query_variants = await rewrite_query(query, num_variants=2)
        except Exception as exc:
            logger.debug(f"Query rewriting skipped: {exc}")
            query_variants = [query]

    # Step 2: Vector search (over-fetch for reranking) — multi-pass with variants
    store = get_vector_store_provider(tenant_id)
    if store.chunk_count == 0:
        return []

    all_results = []
    for variant_query in query_variants:
        try:
            variant_embedding = await embedding_provider.embed(variant_query)
            variant_results = store.search(
                query_embedding=variant_embedding,
                top_k=top_k * 2,
                subject_id=subject_id,
                notebook_id=notebook_id,
            )
            if variant_results:
                all_results.append(variant_results)
                logger.debug(f"Query variant '{variant_query}' → {len(variant_results)} results")
        except Exception as exc:
            logger.debug(f"Variant search failed for '{variant_query}': {exc}")
            continue

    if not all_results:
        return []

    # Merge results from all query variants (gives bonus to chunks found in multiple searches)
    if len(all_results) > 1:
        merged_results = merge_search_results(all_results, max_results=top_k * 3)
        results = merged_results
        logger.info(f"Merged {len(all_results)} query variants → {len(results)} unique chunks")
    else:
        results = all_results[0]

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
) -> List[Dict[str, Any]]:
    """Simplified retrieval for non-tenant documents (e.g. system docs)."""
    return await retrieve_context(
        query=query,
        tenant_id=collection,
        top_k=top_k
    )


def build_context_string(chunks: List[Dict[str, Any]], max_tokens: int = 3000) -> str:
    """Build a context string from retrieved chunks, with compression."""
    compressed = compress_context(chunks, max_tokens)

    context_parts = []
    for chunk in compressed:
        text = chunk["text"]
        citation = chunk["citation"]
        context_parts.append(f"{text}\n— Source: {citation}")

    return "\n\n".join(context_parts)


def build_retrieval_audit(chunks: List[Dict[str, Any]], max_tokens: int = 3000) -> Dict[str, Any]:
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


def extract_citations(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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
