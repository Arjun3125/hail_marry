"""Application helpers for student assignment submissions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from src.domains.academic.models.assignment import Assignment, AssignmentSubmission
from src.domains.academic.models.core import Enrollment, Subject


@dataclass
class StudentAssignmentSubmissionError(Exception):
    status_code: int
    detail: str


async def submit_student_assignment(
    *,
    db: Session,
    tenant_id,
    student_id,
    assignment_uuid: UUID,
    file: Any,
    allowed_extensions: set[str],
    max_file_size: int,
    assignment_submission_dir: Path,
    sanitize_docx_bytes_fn,
    upload_validation_error_cls,
    logger,
) -> dict[str, Any]:
    enrollment = (
        db.query(Enrollment)
        .filter(
            Enrollment.tenant_id == tenant_id,
            Enrollment.student_id == student_id,
        )
        .first()
    )
    if not enrollment:
        raise StudentAssignmentSubmissionError(403, "Student is not enrolled in any class")

    assignment = (
        db.query(Assignment)
        .filter(
            Assignment.id == assignment_uuid,
            Assignment.tenant_id == tenant_id,
        )
        .first()
    )
    if not assignment:
        raise StudentAssignmentSubmissionError(404, "Assignment not found")

    subject = (
        db.query(Subject)
        .filter(
            Subject.id == assignment.subject_id,
            Subject.tenant_id == tenant_id,
        )
        .first()
    )
    if not subject or subject.class_id != enrollment.class_id:
        raise StudentAssignmentSubmissionError(403, "Not authorized to submit this assignment")

    existing_submission = (
        db.query(AssignmentSubmission)
        .filter(
            AssignmentSubmission.tenant_id == tenant_id,
            AssignmentSubmission.assignment_id == assignment_uuid,
            AssignmentSubmission.student_id == student_id,
        )
        .first()
    )
    if existing_submission and existing_submission.grade is not None:
        raise StudentAssignmentSubmissionError(409, "Assignment already graded. Resubmission is locked.")

    safe_filename = Path(file.filename or "").name
    if not safe_filename:
        raise StudentAssignmentSubmissionError(400, "Filename is required.")

    ext = safe_filename.split(".")[-1].lower() if "." in safe_filename else ""
    if ext not in allowed_extensions:
        raise StudentAssignmentSubmissionError(
            400,
            f"Only {', '.join(sorted(allowed_extensions))} files allowed.",
        )

    content = await file.read()
    if ext == "docx":
        try:
            content, _ = sanitize_docx_bytes_fn(content)
        except upload_validation_error_cls as exc:
            raise StudentAssignmentSubmissionError(400, str(exc))
    if len(content) > max_file_size:
        raise StudentAssignmentSubmissionError(400, "File exceeds 25MB limit.")

    ocr_processed = False
    ocr_review_required = False
    ocr_warning = None
    ocr_languages: list[str] = []
    ocr_preprocessing: list[str] = []
    ocr_confidence: float | None = None

    if ext in ("jpg", "jpeg", "png"):
        from src.infrastructure.vector_store.ocr_service import image_bytes_to_pdf, validate_image_size

        try:
            validate_image_size(content)
        except ValueError as exc:
            raise StudentAssignmentSubmissionError(400, str(exc))

        pdf_name = f"{tenant_id}_{student_id}_{assignment_uuid}_{uuid4().hex}_ocr.pdf"
        pdf_path = assignment_submission_dir / pdf_name
        try:
            ocr_result = image_bytes_to_pdf(
                content,
                str(pdf_path),
                suffix=f".{ext}",
                title=safe_filename,
                source_name=safe_filename,
            )
        except Exception:
            logger.exception("OCR processing failed")
            raise StudentAssignmentSubmissionError(
                500,
                "OCR processing failed. Please upload a clearer, higher-contrast image or a PDF.",
            )

        file_path = pdf_path
        safe_filename = pdf_name
        ocr_processed = True
        ocr_review_required = ocr_result.review_required
        ocr_warning = ocr_result.warning
        ocr_languages = ocr_result.languages
        ocr_preprocessing = ocr_result.preprocessing_applied
        ocr_confidence = getattr(ocr_result, "confidence", None)
    else:
        stored_name = f"{tenant_id}_{student_id}_{assignment_uuid}_{uuid4().hex}_{safe_filename}"
        file_path = assignment_submission_dir / stored_name
        with open(file_path, "wb") as fp:
            fp.write(content)

    now = datetime.now(timezone.utc)
    if existing_submission:
        existing_submission.submission_url = str(file_path)
        existing_submission.submitted_at = now
    else:
        existing_submission = AssignmentSubmission(
            tenant_id=tenant_id,
            assignment_id=assignment_uuid,
            student_id=student_id,
            submission_url=str(file_path),
            submitted_at=now,
        )
        db.add(existing_submission)

    db.commit()
    db.refresh(existing_submission)

    return {
        "success": True,
        "submission_id": str(existing_submission.id),
        "assignment_id": str(assignment_uuid),
        "file_name": safe_filename,
        "submitted_at": str(existing_submission.submitted_at),
        "status": "submitted",
        "ocr_processed": ocr_processed,
        "ocr_review_required": ocr_review_required,
        "ocr_warning": ocr_warning,
        "ocr_languages": ocr_languages,
        "ocr_preprocessing": ocr_preprocessing,
        "ocr_confidence": ocr_confidence,
    }
