"""Application helpers for teacher document and YouTube ingestion flows."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4


@dataclass
class TeacherIngestionError(Exception):
    status_code: int
    detail: str


async def upload_teacher_document(
    *,
    db,
    current_user,
    file,
    allowed_extensions: set[str],
    max_file_size: int,
    upload_dir,
    sanitize_docx_bytes_fn,
    upload_validation_error_cls,
    resolve_upload_metrics_fn,
    evaluate_governance_fn,
    record_usage_event_fn,
    invalidate_tenant_cache_fn,
    emit_webhook_event_fn,
    document_model,
    logger,
) -> dict[str, Any]:
    """Upload and ingest teacher documents/images into the vector pipeline."""
    safe_filename = Path(file.filename or "").name
    if not safe_filename:
        raise TeacherIngestionError(400, "Filename is required.")

    ext = safe_filename.split(".")[-1].lower() if "." in safe_filename else ""
    if ext not in allowed_extensions:
        raise TeacherIngestionError(
            400,
            f"Only {', '.join(sorted(allowed_extensions))} files allowed.",
        )

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
            raise TeacherIngestionError(400, str(exc))
    if len(content) > max_file_size:
        raise TeacherIngestionError(400, "File exceeds 50MB limit.")

    upload_metrics = resolve_upload_metrics_fn(ext)
    for metric in upload_metrics:
        governance = evaluate_governance_fn(
            db,
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            metric=metric,
            mode=metric,
        )
        if not governance.allowed:
            raise TeacherIngestionError(429, governance.detail)

    if ext in ("jpg", "jpeg", "png"):
        from src.infrastructure.vector_store.ocr_service import image_bytes_to_pdf, validate_image_size

        try:
            validate_image_size(content)
        except ValueError as exc:
            raise TeacherIngestionError(400, str(exc))

        pdf_name = f"{current_user.tenant_id}_{current_user.id}_{uuid4().hex}_ocr.pdf"
        file_path = upload_dir / pdf_name
        try:
            ocr_result = image_bytes_to_pdf(
                content,
                str(file_path),
                suffix=f".{ext}",
                title=safe_filename,
                source_name=safe_filename,
            )
        except Exception:
            logger.exception("OCR processing failed for teacher upload")
            raise TeacherIngestionError(
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
        file_path = upload_dir / f"{current_user.tenant_id}_{current_user.id}_{uuid4().hex}_{safe_filename}"
        with open(file_path, "wb") as f:
            f.write(content)

    doc = document_model(
        tenant_id=current_user.tenant_id,
        uploaded_by=current_user.id,
        file_name=safe_filename,
        file_type=ext,
        storage_path=str(file_path),
        ingestion_status="processing",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    try:
        from src.infrastructure.vector_store.ingestion import ingest_document
        from src.infrastructure.llm.embeddings import generate_embeddings_batch
        from src.infrastructure.vector_store.vector_store import get_vector_store

        chunks = ingest_document(
            file_path=str(file_path),
            document_id=str(doc.id),
            tenant_id=str(current_user.tenant_id),
            notebook_id=str(doc.notebook_id) if doc.notebook_id else None,
        )

        if chunks:
            texts = [c.text for c in chunks]
            embeddings = await generate_embeddings_batch(texts)
            store = get_vector_store(str(current_user.tenant_id))
            chunk_dicts = [
                {
                    "text": c.text,
                    "document_id": c.document_id,
                    "page_number": c.page_number,
                    "section_title": c.section_title or "",
                    "subject_id": c.subject_id or "",
                    "notebook_id": c.notebook_id or "",
                    "source_file": c.source_file or "",
                }
                for c in chunks
            ]
            store.add_chunks(chunk_dicts, embeddings)

        invalidate_tenant_cache_fn(str(current_user.tenant_id))
        doc.ingestion_status = "completed"
        doc.chunk_count = len(chunks) if chunks else 0
        for metric in upload_metrics:
            record_usage_event_fn(
                db,
                tenant_id=current_user.tenant_id,
                user_id=current_user.id,
                metric=metric,
                metadata={
                    "route": "teacher.upload",
                    "file_type": ext,
                    "document_id": str(doc.id),
                    "ocr_processed": ocr_processed,
                },
            )
        db.commit()

        try:
            await emit_webhook_event_fn(
                db=db,
                tenant_id=current_user.tenant_id,
                event_type="document.ingested",
                data={
                    "document_id": str(doc.id),
                    "file_name": doc.file_name,
                    "uploaded_by": str(current_user.id),
                    "chunks": doc.chunk_count,
                },
            )
        except Exception:
            pass

        return {
            "success": True,
            "document_id": str(doc.id),
            "chunks": len(chunks),
            "status": "completed",
            "macros_removed": macros_removed,
            "ocr_processed": ocr_processed,
            "ocr_review_required": ocr_review_required,
            "ocr_warning": ocr_warning,
            "ocr_languages": ocr_languages,
            "ocr_preprocessing": ocr_preprocessing,
            "ocr_confidence": ocr_confidence,
        }
    except Exception:
        logger.exception("Teacher document ingestion failed", extra={"document_id": str(doc.id)})
        doc.ingestion_status = "failed"
        db.commit()
        return {
            "success": False,
            "document_id": str(doc.id),
            "error": "Document ingestion failed.",
            "status": "failed",
        }


async def ingest_teacher_youtube_video(
    *,
    db,
    current_user,
    title: str,
    url: str,
    subject_id: str | None,
    allowed_class_ids: set,
    get_subject_in_scope_fn,
    evaluate_governance_fn,
    record_usage_event_fn,
    invalidate_tenant_cache_fn,
    lecture_model,
) -> dict[str, Any]:
    """Ingest a teacher YouTube transcript and push chunks to vector store."""
    if not subject_id:
        raise TeacherIngestionError(400, "subject_id is required")

    governance = evaluate_governance_fn(
        db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        metric="youtube_ingestions",
        mode="youtube_ingestions",
    )
    if not governance.allowed:
        raise TeacherIngestionError(429, governance.detail)

    subject = get_subject_in_scope_fn(
        db=db,
        current_user=current_user,
        subject_id=subject_id,
        allowed_class_ids=allowed_class_ids,
    )
    subject_uuid = subject.id

    lecture = lecture_model(
        tenant_id=current_user.tenant_id,
        title=title,
        youtube_url=url,
        subject_id=subject_uuid,
        transcript_ingested=False,
    )
    db.add(lecture)
    db.commit()
    db.refresh(lecture)

    try:
        from src.infrastructure.vector_store.ingestion import ingest_youtube
        from src.infrastructure.llm.embeddings import generate_embeddings_batch
        from src.infrastructure.vector_store.vector_store import get_vector_store

        chunks = ingest_youtube(
            url=url,
            document_id=str(lecture.id),
            tenant_id=str(current_user.tenant_id),
            subject_id=str(subject_uuid),
        )
        if chunks:
            texts = [c.text for c in chunks]
            embeddings = await generate_embeddings_batch(texts)
            store = get_vector_store(str(current_user.tenant_id))
            chunk_dicts = [
                {
                    "text": c.text,
                    "document_id": c.document_id,
                    "page_number": c.page_number,
                    "section_title": c.section_title or "",
                    "subject_id": c.subject_id or "",
                    "source_file": c.source_file or "",
                }
                for c in chunks
            ]
            store.add_chunks(chunk_dicts, embeddings)

        invalidate_tenant_cache_fn(str(current_user.tenant_id))
        lecture.transcript_ingested = True
        record_usage_event_fn(
            db,
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            metric="youtube_ingestions",
            metadata={"route": "teacher.youtube", "lecture_id": str(lecture.id)},
        )
        db.commit()
        return {"success": True, "lecture_id": str(lecture.id), "chunks": len(chunks)}
    except Exception as exc:
        return {"success": False, "error": str(exc)}
