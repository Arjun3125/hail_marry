"""Background schedulers for doc watch and digest emails."""
from __future__ import annotations

import asyncio
import logging
from uuid import UUID

from config import settings
from database import SessionLocal
from src.domains.platform.models.document import Document
from src.domains.platform.schemas.ai_runtime import InternalTeacherDocumentIngestRequest
from src.domains.platform.services.ai_queue import JOB_TYPE_TEACHER_DOCUMENT_INGEST, enqueue_job
from src.domains.academic.services.digest_email import send_weekly_digests
from src.domains.platform.services.doc_watcher import mark_processed, run_watch_cycle

logger = logging.getLogger(__name__)


async def _wait_or_stop(stop_event: asyncio.Event, seconds: float) -> None:
    try:
        await asyncio.wait_for(stop_event.wait(), timeout=seconds)
    except asyncio.TimeoutError:
        return


def _run_doc_watch_cycle() -> None:
    result = run_watch_cycle()
    files = result.get("files", [])
    if not files:
        return

    if not settings.doc_watch.tenant_id or not settings.doc_watch.uploader_id:
        logger.warning("Doc watch skipped: DOC_WATCH_TENANT_ID or DOC_WATCH_UPLOADER_ID not set.")
        return

    try:
        tenant_id = UUID(settings.doc_watch.tenant_id)
        uploader_id = UUID(settings.doc_watch.uploader_id)
    except ValueError:
        logger.warning("Doc watch skipped: invalid DOC_WATCH_TENANT_ID or DOC_WATCH_UPLOADER_ID.")
        return

    db = SessionLocal()
    try:
        for item in files:
            existing = db.query(Document).filter(
                Document.tenant_id == tenant_id,
                Document.storage_path == item["path"],
            ).first()
            if existing:
                mark_processed(item["path"], item["hash"])
                continue

            doc = Document(
                tenant_id=tenant_id,
                uploaded_by=uploader_id,
                file_name=item["name"],
                file_type=item["extension"],
                storage_path=item["path"],
                ingestion_status="processing",
            )
            db.add(doc)
            db.commit()
            db.refresh(doc)

            payload = InternalTeacherDocumentIngestRequest(
                document_id=str(doc.id),
                file_path=item["path"],
                file_name=item["name"],
                subject_id=None,
                uploaded_by=str(uploader_id),
                macros_removed=False,
                tenant_id=str(tenant_id),
            )
            enqueue_job(
                JOB_TYPE_TEACHER_DOCUMENT_INGEST,
                payload.model_dump(),
                tenant_id=str(tenant_id),
                user_id=str(uploader_id),
            )
            mark_processed(item["path"], item["hash"])
    finally:
        db.close()


def _run_digest_cycle() -> None:
    if not settings.email.enabled:
        logger.warning("Digest email skipped: EMAIL_ENABLED is false.")
        return

    db = SessionLocal()
    try:
        stats = send_weekly_digests(db)
        logger.info("Weekly digest run completed: sent=%s skipped=%s", stats["sent"], stats["skipped"])
    finally:
        db.close()


async def run_doc_watch_loop(stop_event: asyncio.Event) -> None:
    interval = max(5, settings.doc_watch.poll_interval_seconds)
    while not stop_event.is_set():
        if settings.doc_watch.enabled and settings.doc_watch.dirs:
            await asyncio.to_thread(_run_doc_watch_cycle)
        await _wait_or_stop(stop_event, interval)


async def run_digest_loop(stop_event: asyncio.Event) -> None:
    interval = max(60, settings.digest_email.interval_minutes * 60)
    while not stop_event.is_set():
        if settings.digest_email.enabled:
            await asyncio.to_thread(_run_digest_cycle)
        await _wait_or_stop(stop_event, interval)


async def run_scheduled_notifications_loop(stop_event: asyncio.Event) -> None:
    """Run the scheduled notifications service (APScheduler).
    
    This loop keeps the APScheduler running for daily parent notifications:
    - 8 AM IST: Check for assignments due tomorrow
    - 9 AM IST: Check for low attendance
    """
    try:
        from src.domains.academic.services.scheduled_notifications import (
            run_scheduled_notifications_loop as run_scheduled_notifications,
        )

        await run_scheduled_notifications(stop_event)
    except Exception as e:
        logger.error(f"Scheduled notifications loop failed: {str(e)}")
        raise
