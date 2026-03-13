"""HyDE (Hypothetical Document Embeddings) — query transform for better retrieval.

Instead of searching with the raw question, we first generate a hypothetical
ideal answer, embed it, then search FAISS with that embedding. This dramatically
improves retrieval for complex, multi-hop, or abstract questions.
"""
import os
import re
from typing import Optional


# Whether HyDE is enabled (can be toggled via env var)
ENABLE_HYDE = os.getenv("ENABLE_HYDE", "true").lower() in ("true", "1", "yes")


def should_use_hyde(query: str) -> bool:
    """Heuristic: use HyDE for complex questions, skip for simple lookups.

    Returns True for:
    - Questions with multiple clauses (and, or, but)
    - Abstract/conceptual questions (why, how, compare, explain)
    - Long questions (>10 words)

    Returns False for:
    - Short factual lookups (what is X, define X)
    - Single-word queries
    """
    if not ENABLE_HYDE:
        return False

    query_lower = query.lower().strip()
    word_count = len(query_lower.split())

    # Too short — direct lookup is fine
    if word_count <= 3:
        return False

    # Complex question markers
    complex_markers = ["why", "how", "compare", "contrast", "explain", "analyze",
                       "relationship between", "difference between", "impact of",
                       "what would happen", "evaluate"]
    if any(marker in query_lower for marker in complex_markers):
        return True

    # Multi-clause questions
    if word_count > 10:
        return True

    # Contains conjunctions suggesting multi-part
    if any(conj in query_lower for conj in [" and ", " or ", " but ", " versus "]):
        return True

    return False


def generate_hypothetical_answer(query: str, mode: str = "qa") -> str:
    """Generate a hypothetical ideal answer to use as the search query.

    This is a template-based approach. In production with an available LLM,
    this would call the LLM to generate the hypothetical answer.

    The hypothetical answer doesn't need to be correct — it just needs to
    contain the right vocabulary/concepts so the embedding is closer to
    relevant documents.
    """
    # Template-based hypothetical answers by mode
    templates = {
        "qa": (
            "The answer to '{query}' involves several key concepts. "
            "First, we need to understand the fundamental principles. "
            "The main factors include the relevant definitions, formulas, "
            "and real-world applications. Specifically, {query}"
        ),
        "quiz": (
            "A comprehensive quiz about '{query}' would test understanding "
            "of core concepts, definitions, formulas, and their applications. "
            "Key topics include: {query}"
        ),
        "study_guide": (
            "A study guide for '{query}' covers the following areas: "
            "1. Basic definitions and terminology. "
            "2. Core principles and theories. "
            "3. Applications and examples. "
            "4. Common misconceptions. {query}"
        ),
    }

    template = templates.get(mode, templates["qa"])
    return template.format(query=query)


def hyde_transform(query: str, mode: str = "qa") -> str:
    """Full HyDE pipeline: decide → generate hypothetical → return search query.

    Returns the hypothetical answer if HyDE should be used,
    otherwise returns the original query unchanged.
    """
    if not should_use_hyde(query):
        return query

    hypothetical = generate_hypothetical_answer(query, mode)
    return hypothetical
