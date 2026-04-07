"""AI grading helper for teacher uploads."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import HTTPException

from src.domains.platform.services.trace_backend import record_trace_event
from src.infrastructure.vector_store.ocr_service import (
    extract_ocr_result_from_image_path,
    is_image_file,
)

MAX_EXTRACTED_CHARS = 5000


def _coerce_numeric(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


async def run_ai_grade(
    payload: dict,
    trace_id: str | None = None,
    tenant_id: str | None = None,
) -> dict:
    file_path = payload.get("file_path")
    file_name = payload.get("file_name") or (Path(file_path).name if file_path else "")
    if not file_path:
        raise HTTPException(status_code=400, detail="Missing file_path for AI grading job.")

    path = Path(file_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Grading file not found.")

    extracted_text = None
    error = None
    ocr_processed = False
    ocr_review_required = False
    ocr_warning = None
    ocr_languages: list[str] = []
    ocr_preprocessing: list[str] = []
    ocr_confidence: float | None = None
    if is_image_file(file_name):
        try:
            ocr_result = extract_ocr_result_from_image_path(str(path))
            extracted_text = ocr_result.text
            ocr_processed = ocr_result.used_ocr
            ocr_review_required = ocr_result.review_required
            ocr_warning = ocr_result.warning
            ocr_languages = ocr_result.languages
            ocr_preprocessing = ocr_result.preprocessing_applied
            ocr_confidence = ocr_result.confidence
            if extracted_text and len(extracted_text) > MAX_EXTRACTED_CHARS:
                extracted_text = extracted_text[:MAX_EXTRACTED_CHARS] + "..."
                ocr_warning = ocr_warning or "OCR output was truncated before AI grading."
        except Exception as exc:
            error = str(exc)
    else:
        error = "Automatic grading currently supports image uploads only."

    ai_feedback = None
    ai_score = None
    ai_max_score = None

    if extracted_text and not error:
        answer_key = payload.get("answer_key")
        rubric = payload.get("rubric")
        if answer_key:
            try:
                import json

                from src.infrastructure.llm.providers import get_llm_provider

                llm = get_llm_provider()
                grading_prompt = (
                    "You are a teacher grading a student's handwritten answer (extracted via OCR).\n"
                    f"Correct Answer Key: {answer_key}\n"
                    f"Grading Rubric: {rubric or 'Award partial marks for partially correct logic or steps.'}\n"
                    f"Student Answer: {extracted_text}\n\n"
                    "Evaluate the answer and return a JSON object with these EXACT keys:\n"
                    "{\"score\": <float>, \"max_score\": <float>, \"feedback\": \"<string>\"}"
                )

                llm_response = await llm.generate(grading_prompt, temperature=0.1)
                text_response = llm_response.get("response", "").strip()

                try:
                    if "```" in text_response:
                        text_response = text_response.split("```")[1].strip()
                        if text_response.startswith("json"):
                            text_response = text_response[4:].strip()

                    data = json.loads(text_response)
                    ai_score = data.get("score")
                    ai_max_score = data.get("max_score")
                    ai_feedback = data.get("feedback")
                except (json.JSONDecodeError, IndexError):
                    error = f"AI grading failed to parse response: {text_response[:100]}"
            except Exception as exc:
                error = f"AI grading execution error: {str(exc)}"

    expected_max_marks = _coerce_numeric(payload.get("exam_max_marks"))
    normalized_max_marks = ai_max_score if ai_max_score is not None else expected_max_marks
    proposed_mark = None
    if ai_score is not None:
        working_score = _coerce_numeric(ai_score)
        working_ai_max = _coerce_numeric(ai_max_score)
        if working_score is not None:
            if expected_max_marks is not None and working_ai_max and working_ai_max > 0:
                working_score = round((working_score / working_ai_max) * expected_max_marks)
            proposed_mark = max(0, int(round(working_score)))
            if expected_max_marks is not None:
                proposed_mark = min(proposed_mark, int(round(expected_max_marks)))

    review_status = "draft_ready" if proposed_mark is not None and not error else "manual_review_required"
    teacher_review = {
        "required": True,
        "finalized": False,
        "status": review_status,
        "proposed_mark": proposed_mark,
        "max_marks": int(round(normalized_max_marks)) if normalized_max_marks is not None else None,
        "exam_id": payload.get("exam_id"),
        "exam_name": payload.get("exam_name"),
        "student_id": payload.get("student_id"),
        "student_name": payload.get("student_name"),
        "answer_key_provided": bool(payload.get("answer_key")),
        "rubric_provided": bool(payload.get("rubric")),
        "notes": (
            "AI output is a draft recommendation and must be reviewed by a teacher before marks are finalized."
        ),
    }

    result = {
        "status": review_status,
        "file_name": file_name,
        "file_path": str(path),
        "extracted_text": extracted_text,
        "ai_score": ai_score,
        "ai_max_score": ai_max_score,
        "ai_feedback": ai_feedback,
        "review_required": True,
        "proposed_mark": proposed_mark,
        "teacher_review": teacher_review,
        "error": error,
        "ocr_processed": ocr_processed,
        "ocr_review_required": ocr_review_required,
        "ocr_warning": ocr_warning,
        "ocr_languages": ocr_languages,
        "ocr_preprocessing": ocr_preprocessing,
        "ocr_confidence": ocr_confidence,
    }

    record_trace_event(
        trace_id=trace_id,
        tenant_id=tenant_id,
        source="ai-grade",
        stage="ai_grade.completed" if not error else "ai_grade.partial",
        detail=error,
        metadata={"file_name": file_name},
    )
    return result
