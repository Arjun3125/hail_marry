"""AI grading helper for teacher uploads."""
from __future__ import annotations

from pathlib import Path

from fastapi import HTTPException

from src.infrastructure.vector_store.ocr_service import extract_text_from_image, is_image_file
from src.domains.platform.services.trace_backend import record_trace_event

MAX_EXTRACTED_CHARS = 5000


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
    if is_image_file(file_name):
        try:
            extracted_text = extract_text_from_image(str(path))
            if extracted_text and len(extracted_text) > MAX_EXTRACTED_CHARS:
                extracted_text = extracted_text[:MAX_EXTRACTED_CHARS] + "…"
        except Exception as exc:
            error = str(exc)
    else:
        error = "Automatic grading currently supports image uploads only."

    result = {
        "status": "review_required",
        "file_name": file_name,
        "file_path": str(path),
        "extracted_text": extracted_text,
        "error": error,
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
