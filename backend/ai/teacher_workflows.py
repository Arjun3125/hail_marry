"""Teacher-facing AI generation workflows that are safe to run in the worker."""
from __future__ import annotations

from ai.workflows import execute_text_query
from schemas.ai_runtime import InternalAIQueryRequest, InternalTeacherAssessmentRequest


async def execute_teacher_assessment(request: InternalTeacherAssessmentRequest) -> dict:
    n = max(1, min(request.num_questions, 15))
    prompt_query = (
        f"Generate exactly {n} multiple-choice questions about: {request.topic}. "
        f"Subject: {request.subject_name}. Format as JSON array."
    )
    ai_result = await execute_text_query(
        InternalAIQueryRequest(
            query=prompt_query,
            mode="quiz",
            subject_id=request.subject_id,
            tenant_id=request.tenant_id,
        )
    )
    return {
        "success": True,
        "subject": request.subject_name,
        "topic": request.topic,
        "assessment": ai_result.get("answer", ""),
        "citations": ai_result.get("citations", []),
        "token_usage": ai_result.get("token_usage", 0),
        "citation_valid": ai_result.get("citation_valid", False),
    }
