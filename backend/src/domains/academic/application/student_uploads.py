"""Application helpers for student upload ingestion workflows."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4
from typing import Any

from sqlalchemy.orm import Session

from src.domains.platform.models.document import Document


@dataclass
class StudentUploadError(Exception):
    status_code: int
    detail: str


async def ingest_student_upload(
    *,
    db: Session,
    tenant_id,
    user_id,
    file,
    allowed_extensions: set[str],
    max_file_size: int,
    upload_dir: Path,
    ocr_output_dir: Path,
    sanitize_docx_bytes_fn,
    upload_validation_error_cls,
    resolve_upload_metrics_fn,
    evaluate_governance_fn,
    record_usage_event_fn,
    invalidate_tenant_cache_fn,
    logger,
) -> dict[str, Any]:
    safe_filename = Path(file.filename or "").name
    if not safe_filename:
        raise StudentUploadError(400, "Filename is required.")

    ext = safe_filename.split(".")[-1].lower() if "." in safe_filename else ""
    if ext not in allowed_extensions:
        raise StudentUploadError(400, f"Only {', '.join(sorted(allowed_extensions))} files allowed.")

    content = await file.read()
    macros_removed = False
    ocr_processed = False
    ocr_review_required = False
    ocr_warning = None
    ocr_languages: list[str] = []
    ocr_preprocessing: list[str] = []
    ocr_confidence: float | None = None

    if ext == "docx":
        try:
            content, macros_removed = sanitize_docx_bytes_fn(content)
        except upload_validation_error_cls as exc:
            raise StudentUploadError(400, str(exc))
    if len(content) > max_file_size:
        raise StudentUploadError(400, "File exceeds 25MB limit.")

    upload_metrics = resolve_upload_metrics_fn(ext)
    for metric in upload_metrics:
        governance = evaluate_governance_fn(
            db,
            tenant_id=tenant_id,
            user_id=user_id,
            metric=metric,
            mode=metric,
        )
        if not governance.allowed:
            raise StudentUploadError(429, governance.detail)

    if ext in ("jpg", "jpeg", "png"):
        from src.infrastructure.vector_store.ocr_service import image_bytes_to_pdf, validate_image_size

        try:
            validate_image_size(content)
        except ValueError as exc:
            raise StudentUploadError(400, str(exc))

        pdf_name = f"{tenant_id}_{user_id}_{uuid4().hex}_ocr.pdf"
        file_path = ocr_output_dir / pdf_name
        try:
            ocr_result = image_bytes_to_pdf(
                content,
                str(file_path),
                suffix=f".{ext}",
                title=safe_filename,
                source_name=safe_filename,
            )
        except Exception:
            logger.exception("OCR processing failed for student upload")
            raise StudentUploadError(
                500,
                "OCR processing failed. Please upload a clearer, higher-contrast image or a PDF.",
            )

        safe_filename = pdf_name
        ext = "pdf"
        ocr_processed = True
        ocr_review_required = ocr_result.review_required
        ocr_warning = ocr_result.warning
        ocr_languages = ocr_result.languages
        ocr_preprocessing = ocr_result.preprocessing_applied
        ocr_confidence = getattr(ocr_result, "confidence", None)
    else:
        safe_name = f"{tenant_id}_{user_id}_{uuid4().hex}_{safe_filename}"
        file_path = upload_dir / safe_name
        with open(file_path, "wb") as fp:
            fp.write(content)

    doc = Document(
        tenant_id=tenant_id,
        uploaded_by=user_id,
        file_name=safe_filename,
        file_type=ext,
        storage_path=str(file_path),
        ingestion_status="processing",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    chunks_count = 0
    try:
        from src.infrastructure.vector_store.ingestion import ingest_document
        from src.infrastructure.llm.providers import get_embedding_provider, get_vector_store_provider

        chunks = ingest_document(
            file_path=str(file_path),
            document_id=str(doc.id),
            tenant_id=str(tenant_id),
            notebook_id=str(doc.notebook_id) if doc.notebook_id else None,
        )

        if chunks:
            texts = [chunk.text for chunk in chunks]
            embeddings = await get_embedding_provider().embed_batch(texts)
            store = get_vector_store_provider(str(tenant_id))
            chunk_dicts = [
                {
                    "text": chunk.text,
                    "document_id": chunk.document_id,
                    "page_number": chunk.page_number,
                    "section_title": chunk.section_title or "",
                    "subject_id": chunk.subject_id or "",
                    "notebook_id": chunk.notebook_id or "",
                    "source_file": chunk.source_file or "",
                }
                for chunk in chunks
            ]
            store.add_chunks(chunk_dicts, embeddings)
            chunks_count = len(chunks)

        invalidate_tenant_cache_fn(str(tenant_id))

        doc.ingestion_status = "completed"
        for metric in upload_metrics:
            record_usage_event_fn(
                db,
                tenant_id=tenant_id,
                user_id=user_id,
                metric=metric,
                metadata={
                    "route": "student.upload",
                    "file_type": ext,
                    "document_id": str(doc.id),
                    "ocr_processed": ocr_processed,
                },
            )
        db.commit()
    except Exception:
        logger.exception("Student document ingestion failed", extra={"document_id": str(doc.id)})
        doc.ingestion_status = "failed"
        db.commit()
        raise StudentUploadError(500, "Document ingestion failed.")

    return {
        "success": True,
        "document_id": str(doc.id),
        "file_name": safe_filename,
        "file_type": ext,
        "chunks": chunks_count,
        "macros_removed": macros_removed,
        "ocr_processed": ocr_processed,
        "ocr_review_required": ocr_review_required,
        "ocr_warning": ocr_warning,
        "ocr_languages": ocr_languages,
        "ocr_preprocessing": ocr_preprocessing,
        "ocr_confidence": ocr_confidence,
        "status": doc.ingestion_status,
    }
