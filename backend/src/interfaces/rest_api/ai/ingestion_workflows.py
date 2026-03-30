"""Queued teacher ingestion workflows for documents and YouTube lectures."""
from __future__ import annotations

import time
from typing import Any
from uuid import UUID

from database import SessionLocal
from src.domains.platform.models.document import Document
from src.domains.academic.models.lecture import Lecture
from src.infrastructure.llm.cache import invalidate_tenant_cache
from src.domains.platform.services.metrics_registry import observe_stage_latency
from src.domains.platform.schemas.ai_runtime import (
    InternalTeacherDocumentIngestRequest,
    InternalTeacherYoutubeIngestRequest,
    InternalWhatsAppMediaIngestRequest,
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
            "notebook_id": chunk.notebook_id or "",
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
            notebook_id=str(document.notebook_id) if document.notebook_id else None,
        )

        if chunks:
            texts = [chunk.text for chunk in chunks]
            embeddings = await get_embedding_provider().embed_batch(texts)
            store = get_vector_store_provider(request.tenant_id)
            store.add_chunks(_chunk_payload(chunks), embeddings)

        invalidate_tenant_cache(request.tenant_id)

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

        invalidate_tenant_cache(request.tenant_id)

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


async def execute_whatsapp_media_ingestion(request: InternalWhatsAppMediaIngestRequest) -> dict:
    db = SessionLocal()
    try:
        from src.infrastructure.vector_store.ingestion import ingest_media_transcript
        from src.infrastructure.llm.providers import get_embedding_provider, get_vector_store_provider
        from src.interfaces.whatsapp_bot.agent import run_whatsapp_agent

        document = db.query(Document).filter(
            Document.id == UUID(str(request.document_id)),
            Document.tenant_id == UUID(str(request.tenant_id)),
        ).first()
        if not document:
            raise ValueError("Document record not found for queued WhatsApp media ingestion.")

        transcription_started = time.perf_counter()
        try:
            chunks = ingest_media_transcript(
                file_path=request.file_path,
                document_id=request.document_id,
                tenant_id=request.tenant_id,
                notebook_id=str(document.notebook_id) if document.notebook_id else None,
            )
        except Exception:
            observe_stage_latency("whatsapp_media_ingest", "transcription", (time.perf_counter() - transcription_started) * 1000, "error")
            raise
        observe_stage_latency("whatsapp_media_ingest", "transcription", (time.perf_counter() - transcription_started) * 1000, "success")

        if chunks:
            texts = [chunk.text for chunk in chunks]
            embedding_started = time.perf_counter()
            try:
                embeddings = await get_embedding_provider().embed_batch(texts)
            except Exception:
                observe_stage_latency("whatsapp_media_ingest", "embedding", (time.perf_counter() - embedding_started) * 1000, "error")
                raise
            observe_stage_latency("whatsapp_media_ingest", "embedding", (time.perf_counter() - embedding_started) * 1000, "success")
            store = get_vector_store_provider(request.tenant_id)
            store.add_chunks(_chunk_payload(chunks), embeddings)

        invalidate_tenant_cache(request.tenant_id)

        document.ingestion_status = "completed"
        document.chunk_count = len(chunks) if chunks else 0
        db.commit()

        response_text = (
            f"Received *{request.display_name}* and added it to your knowledge base "
            "(transcript extracted). You can now ask questions about it in WhatsApp."
        )
        follow_up_message = (request.follow_up_message or "").strip()
        if follow_up_message and request.follow_up_user_id and request.role:
            follow_up_started = time.perf_counter()
            try:
                follow_up = await run_whatsapp_agent(
                    message=follow_up_message,
                    user_id=request.follow_up_user_id,
                    tenant_id=request.tenant_id,
                    role=request.role,
                    notebook_id=str(document.notebook_id) if document.notebook_id else None,
                    conversation_history=request.conversation_history[-10:],
                    session_id=None,
                    pending_confirmation_id=None,
                )
            except Exception:
                observe_stage_latency("whatsapp_media_ingest", "follow_up_generation", (time.perf_counter() - follow_up_started) * 1000, "error")
                raise
            observe_stage_latency("whatsapp_media_ingest", "follow_up_generation", (time.perf_counter() - follow_up_started) * 1000, "success")
            follow_up_text = str((follow_up or {}).get("response") or "").strip()
            if follow_up_text:
                response_text = f"{response_text}\n\n{follow_up_text}".strip()

        return {
            "success": True,
            "document_id": request.document_id,
            "chunks": len(chunks) if chunks else 0,
            "status": "completed",
            "response_text": response_text,
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
