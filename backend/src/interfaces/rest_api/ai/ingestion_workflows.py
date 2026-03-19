"""Queued teacher ingestion workflows for documents and YouTube lectures."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from database import SessionLocal
from src.domains.platform.models.document import Document
from models.lecture import Lecture
from src.domains.platform.schemas.ai_runtime import (
    InternalTeacherDocumentIngestRequest,
    InternalTeacherYoutubeIngestRequest,
)
from src.domains.platform.services.webhooks import emit_webhook_event


def _chunk_payload(chunks: list[Any]) -> list[dict[str, Any]]:
    return [
        {
            "text": chunk.text,
            "document_id": chunk.document_id,
            "page_number": chunk.page_number,
            "section_title": chunk.section_title or "",
            "subject_id": chunk.subject_id or "",
            "source_file": chunk.source_file or "",
        }
        for chunk in chunks
    ]


async def execute_teacher_document_ingestion(request: InternalTeacherDocumentIngestRequest) -> dict:
    db = SessionLocal()
    try:
        from src.infrastructure.vector_store.ingestion import ingest_document
        from src.infrastructure.llm.providers import get_embedding_provider, get_vector_store_provider

        document = db.query(Document).filter(
            Document.id == UUID(str(request.document_id)),
            Document.tenant_id == UUID(str(request.tenant_id)),
        ).first()
        if not document:
            raise ValueError("Document record not found for queued ingestion.")

        chunks = ingest_document(
            file_path=request.file_path,
            document_id=request.document_id,
            tenant_id=request.tenant_id,
            subject_id=request.subject_id,
        )

        if chunks:
            texts = [chunk.text for chunk in chunks]
            embeddings = await get_embedding_provider().embed_batch(texts)
            store = get_vector_store_provider(request.tenant_id)
            store.add_chunks(_chunk_payload(chunks), embeddings)

        document.ingestion_status = "completed"
        document.chunk_count = len(chunks) if chunks else 0
        db.commit()

        try:
            await emit_webhook_event(
                db=db,
                tenant_id=document.tenant_id,
                event_type="document.ingested",
                data={
                    "document_id": str(document.id),
                    "file_name": document.file_name,
                    "uploaded_by": request.uploaded_by,
                    "chunks": document.chunk_count,
                },
            )
        except Exception:
            pass

        return {
            "success": True,
            "document_id": request.document_id,
            "chunks": len(chunks) if chunks else 0,
            "status": "completed",
            "macros_removed": request.macros_removed,
        }
    except Exception:
        document = db.query(Document).filter(
            Document.id == UUID(str(request.document_id)),
            Document.tenant_id == UUID(str(request.tenant_id)),
        ).first()
        if document:
            document.ingestion_status = "failed"
            db.commit()
        raise
    finally:
        db.close()


async def execute_teacher_youtube_ingestion(request: InternalTeacherYoutubeIngestRequest) -> dict:
    db = SessionLocal()
    try:
        from src.infrastructure.vector_store.ingestion import ingest_youtube
        from src.infrastructure.llm.providers import get_embedding_provider, get_vector_store_provider

        lecture = db.query(Lecture).filter(
            Lecture.id == UUID(str(request.lecture_id)),
            Lecture.tenant_id == UUID(str(request.tenant_id)),
        ).first()
        if not lecture:
            raise ValueError("Lecture record not found for queued ingestion.")

        chunks = ingest_youtube(
            url=request.url,
            document_id=request.lecture_id,
            tenant_id=request.tenant_id,
            subject_id=request.subject_id,
        )

        if chunks:
            texts = [chunk.text for chunk in chunks]
            embeddings = await get_embedding_provider().embed_batch(texts)
            store = get_vector_store_provider(request.tenant_id)
            store.add_chunks(_chunk_payload(chunks), embeddings)

        lecture.transcript_ingested = True
        db.commit()

        return {
            "success": True,
            "lecture_id": request.lecture_id,
            "chunks": len(chunks) if chunks else 0,
            "status": "completed",
        }
    finally:
        db.close()
