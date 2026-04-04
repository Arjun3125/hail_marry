"""HyDE (Hypothetical Document Embeddings) — query transform for better retrieval.

Instead of searching with the raw question, we first generate a hypothetical
ideal answer, embed it, then search FAISS with that embedding. This dramatically
improves retrieval for complex, multi-hop, or abstract questions.
"""
import os
import re
from typing import Optional
from src.infrastructure.llm.providers import get_llm_provider

# Whether HyDE is enabled (can be toggled via env var)
ENABLE_HYDE = os.getenv("ENABLE_HYDE", "true").lower() in ("true", "1", "yes")

def should_use_hyde(query: str) -> bool:
    """Heuristic: use HyDE for complex questions, skip for simple lookups."""
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


async def generate_hypothetical_answer(query: str, mode: str = "qa") -> str:
    """Generate a hypothetical ideal answer via LLM to use as the search query."""
    llm = get_llm_provider()
    
    prompt_prefixes = {
        "qa": "Write a highly factual, extremely precise paragraph that directly answers the following question. Use academic terminology and core concepts. Question: ",
        "quiz": "Write a comprehensive summary of key bullet points, definitions, and concepts that would appear on a quiz about the following topic. Topic: ",
        "study_guide": "Write a structured syllabus and core principles guide covering the terminology and rules related to the following topic. Topic: ",
    }
    
    prefix = prompt_prefixes.get(mode, prompt_prefixes["qa"])
    prompt = f"{prefix}'{query}'"
    
    try:
        res = await llm.generate(prompt, temperature=0.7, max_new_tokens=400)
        return res["response"].strip()
    except Exception:
        # Fallback to the original exact match fallback logic if LLM crashes
        templates = {
            "qa": f"The answer to '{query}' involves several key concepts.",
            "quiz": f"Key concepts for a quiz on '{query}' include definitions.",
            "study_guide": f"A study guide for '{query}' covers core principles.",
        }
        return templates.get(mode, templates["qa"])


async def hyde_transform(query: str, mode: str = "qa") -> str:
    """Full HyDE pipeline: decide -> generate hypothetical -> return search query.

    Returns the hypothetical answer if HyDE should be used,
    otherwise returns the original query unchanged.
    """
    if not should_use_hyde(query):
        return query

    hypothetical = await generate_hypothetical_answer(query, mode)
    return hypothetical
