"""Docs-as-AI chatbot — AI trained on VidyaOS documentation for self-service support."""
import os
from typing import Optional


# Paths to VidyaOS documentation for self-service support
DOCS_PATHS = [
    "documentation/",
    "README.md",
    "feature_guide.md",
    "STAR_FEATURES_ANALYSIS.md",
]

# FAQ database for quick responses
FAQ_DATABASE = {
    "how to create a tenant": {
        "answer": "Use the Self-Service Onboarding flow: POST /api/onboarding/register with school name, admin email, and password. The system will create tenant, admin user, and return login credentials.",
        "category": "onboarding",
    },
    "how to add students": {
        "answer": "Two methods: 1) CSV Import via POST /api/onboarding/import-students with a CSV file containing student_name, email, class_name columns. 2) Admission workflow via POST /api/admission/apply for individual applications.",
        "category": "students",
    },
    "how to set up ai": {
        "answer": "VidyaOS uses a self-hosted Ollama backend by default. Set OLLAMA_BASE_URL env var (default: http://localhost:11434). Upload documents via the document management endpoints, and they'll be automatically ingested for AI queries.",
        "category": "ai",
    },
    "how to collect fees": {
        "answer": "1) Create fee structures: POST /api/fees/structures. 2) Generate invoices: POST /api/fees/generate-invoices. 3) Record payments: POST /api/fees/payments. View reports at GET /api/fees/report.",
        "category": "fees",
    },
    "how to integrate third party llm": {
        "answer": "VidyaOS exposes an OpenAI-compatible API at POST /v1/chat/completions. You can switch providers via LLM_PROVIDER env var (ollama/openai/anthropic) or per-request via the 'provider' field. Register custom providers with ProviderRegistry.register().",
        "category": "ai",
    },
    "supported languages": {
        "answer": "Currently English (en), Hindi (hi), and Marathi (mr). Get translations via GET /api/i18n/translations/{locale}. Add new locales by creating a JSON file in backend/locales/.",
        "category": "i18n",
    },
    "how to manage library": {
        "answer": "Library management endpoints: POST /api/library/books (add book), GET /api/library/books (search catalog), POST /api/library/issue (issue book), POST /api/library/return/{id} (return), GET /api/library/stats (dashboard).",
        "category": "library",
    },
}


def search_docs_faq(query: str) -> Optional[dict]:
    """Search the FAQ database for a matching question."""
    query_lower = query.lower().strip()
    best_match = None
    best_score = 0

    for faq_key, faq_data in FAQ_DATABASE.items():
        # Simple keyword overlap scoring
        faq_words = set(faq_key.split())
        query_words = set(query_lower.split())
        overlap = len(faq_words & query_words)
        score = overlap / max(len(faq_words), 1)

        if score > best_score and score >= 0.3:
            best_score = score
            best_match = {
                "question": faq_key,
                "answer": faq_data["answer"],
                "category": faq_data["category"],
                "confidence": round(score, 2),
            }

    return best_match


def get_docs_categories() -> list[str]:
    """Get all FAQ categories."""
    return sorted(set(v["category"] for v in FAQ_DATABASE.values()))


def get_faqs_by_category(category: str) -> list[dict]:
    """Get all FAQs in a category."""
    return [
        {"question": k, "answer": v["answer"]}
        for k, v in FAQ_DATABASE.items()
        if v["category"] == category
    ]


async def generate_support_response(query: str) -> dict:
    """Generate a support response using FAQ matching and RAG over documentation."""
    # Step 1: Try FAQ first (fast path)
    faq_result = search_docs_faq(query)
    if faq_result and faq_result["confidence"] >= 0.7:
        return {
            "answer": faq_result["answer"],
            "source": "faq",
            "confidence": faq_result["confidence"],
            "category": faq_result["category"],
            "matched_question": faq_result["question"],
        }

    # Step 2: RAG over documentation files
    try:
        from src.infrastructure.vector_store.retrieval import retrieve_documents
        from src.infrastructure.llm.providers import get_llm_provider

        # Search for documentation in the 'vidyaos_docs' collection
        # Note: This assumes a 'vidyaos_docs' collection was indexed
        chunks = retrieve_documents(query, collection="vidyaos_docs", top_k=3)
        
        if chunks:
            context = "\n\n".join([c["text"] for c in chunks])
            llm = get_llm_provider()
            
            prompt = (
                "You are the VidyaOS Support Assistant. Use the following documentation sections "
                "to answer the user's question accurately.\n\n"
                f"Documentation Context:\n{context}\n\n"
                f"User Question: {query}\n\n"
                "Answer gracefully and provide step-by-step instructions if possible. "
                "If the answer is not in the context, say you don't know and suggest visiting /docs."
            )
            
            llm_response = await llm.generate(prompt, temperature=0.3)
            answer = llm_response.get("response", "").strip()
            
            return {
                "answer": answer,
                "source": "docs_rag",
                "confidence": 0.8,
                "category": "general",
                "matched_question": None,
            }
    except Exception:
        # Silently fail RAG and use fallback
        pass

    return {
        "answer": "I couldn't find a specific answer to your question in my current documentation. Please check our full guide at /docs or contact support for assistance.",
        "source": "fallback",
        "confidence": 0.0,
        "category": "general",
        "matched_question": None,
    }
