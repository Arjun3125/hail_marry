"""Assessment-generation orchestration extracted from HTTP routes."""
from __future__ import annotations

from src.domains.platform.schemas.ai_runtime import InternalAIQueryRequest
from src.domains.platform.services.ai_gateway import run_text_query


async def generate_subject_assessment(
    *,
    tenant_id: str,
    user_id: str,
    subject_id: str,
    subject_name: str,
    topic: str,
    num_questions: int,
) -> dict:
    n = max(1, min(num_questions, 15))
    prompt_query = (
        f"Generate exactly {n} multiple-choice questions about: {topic}. "
        f"Subject: {subject_name}. Format as JSON array."
    )
    result = await run_text_query(
        InternalAIQueryRequest(
            tenant_id=tenant_id,
            user_id=user_id,
            query=prompt_query,
            mode="quiz",
            subject_id=subject_id,
        )
    )
    return {
        "subject": subject_name,
        "topic": topic,
        "assessment": result.get("answer", ""),
        "citations": result.get("citations", []),
        "trace_id": result.get("trace_id", ""),
    }

