"""Redis-backed queue where the worker orchestrates execution through the dedicated AI service."""
from __future__ import annotations

import json
import time
import uuid
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import desc

from config import settings
from database import SessionLocal
from models.ai_job import AIJob, AIJobEvent
from models.audit_log import AuditLog
from schemas.ai_runtime import (
    InternalAIQueryRequest,
    InternalAudioOverviewRequest,
    InternalIngestURLRequest,
    InternalStudyToolGenerateRequest,
    InternalTeacherDocumentIngestRequest,
    InternalTeacherAssessmentRequest,
    InternalTeacherYoutubeIngestRequest,
    InternalVideoOverviewRequest,
)
from services.ai_gateway import (
    run_audio_overview,
    run_study_tool,
    run_teacher_assessment,
    run_teacher_document_ingestion,
    run_teacher_youtube_ingestion,
    run_text_query,
    run_url_ingestion,
    run_video_overview,
)
from services.telemetry import extract_context_from_traceparent, get_current_traceparent, get_tracer

_redis = None
_redis_available = None

JOB_KEY_PREFIX = "ai_job:"
USER_INDEX_PREFIX = "ai_jobs:user:"
TENANT_INDEX_PREFIX = "ai_jobs:tenant:"
TENANT_QUEUE_PREFIX = "ai_jobs:tenant_queue:"
TENANT_METRICS_PREFIX = "ai_jobs:metrics:tenant:"
GLOBAL_METRICS_KEY = "ai_jobs:metrics:global"
TENANT_RECENT_COMPLETED_PREFIX = "ai_jobs:recent_completed:"
TENANT_RECENT_FAILED_PREFIX = "ai_jobs:recent_failed:"
TENANT_DEAD_LETTER_PREFIX = "ai_jobs:dead_letter:"
READY_TENANTS_KEY = "ai_jobs:ready_tenants"
READY_TENANTS_ACTIVE_KEY = "ai_jobs:ready_tenants:active"
JOB_TYPE_QUERY = "text_query"
JOB_TYPE_AUDIO = "audio_overview"
JOB_TYPE_VIDEO = "video_overview"
JOB_TYPE_STUDY_TOOL = "study_tool"
JOB_TYPE_TEACHER_ASSESSMENT = "teacher_assessment"
JOB_TYPE_URL_INGEST = "url_ingest"
JOB_TYPE_TEACHER_DOCUMENT_INGEST = "teacher_document_ingest"
JOB_TYPE_TEACHER_YOUTUBE_INGEST = "teacher_youtube_ingest"
STATUS_QUEUED = "queued"
STATUS_RUNNING = "running"
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"
STATUS_CANCELLED = "cancelled"
STATUS_DEAD_LETTER = "dead_letter"
QUEUE_PAUSED_KEY = "ai_jobs:paused"
AI_SERVICE_JOB_TYPES = {
    JOB_TYPE_QUERY,
    JOB_TYPE_AUDIO,
    JOB_TYPE_VIDEO,
    JOB_TYPE_STUDY_TOOL,
    JOB_TYPE_TEACHER_ASSESSMENT,
    JOB_TYPE_URL_INGEST,
    JOB_TYPE_TEACHER_DOCUMENT_INGEST,
    JOB_TYPE_TEACHER_YOUTUBE_INGEST,
}
JOB_PRIORITIES = {
    JOB_TYPE_QUERY: 30,
    JOB_TYPE_AUDIO: 35,
    JOB_TYPE_VIDEO: 35,
    JOB_TYPE_STUDY_TOOL: 30,
    JOB_TYPE_TEACHER_ASSESSMENT: 20,
    JOB_TYPE_URL_INGEST: 50,
    JOB_TYPE_TEACHER_DOCUMENT_INGEST: 60,
    JOB_TYPE_TEACHER_YOUTUBE_INGEST: 60,
}
TERMINAL_STATUSES = {STATUS_COMPLETED, STATUS_FAILED, STATUS_CANCELLED, STATUS_DEAD_LETTER}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _utcnow_iso() -> str:
    return _utcnow().isoformat()


def _job_key(job_id: str) -> str:
    return f"{JOB_KEY_PREFIX}{job_id}"


def _user_index_key(user_id: str) -> str:
    return f"{USER_INDEX_PREFIX}{user_id}"


def _tenant_index_key(tenant_id: str) -> str:
    return f"{TENANT_INDEX_PREFIX}{tenant_id}"


def _tenant_queue_key(tenant_id: str) -> str:
    return f"{TENANT_QUEUE_PREFIX}{tenant_id}"


def _tenant_metrics_key(tenant_id: str) -> str:
    return f"{TENANT_METRICS_PREFIX}{tenant_id}"


def _tenant_recent_completed_key(tenant_id: str) -> str:
    return f"{TENANT_RECENT_COMPLETED_PREFIX}{tenant_id}"


def _tenant_recent_failed_key(tenant_id: str) -> str:
    return f"{TENANT_RECENT_FAILED_PREFIX}{tenant_id}"


def _tenant_dead_letter_key(tenant_id: str) -> str:
    return f"{TENANT_DEAD_LETTER_PREFIX}{tenant_id}"


def _get_redis_client():
    global _redis, _redis_available

    if _redis_available is None:
        try:
            import redis as redis_lib

            _redis = redis_lib.from_url(settings.redis.url, decode_responses=True)
            _redis.ping()
            _redis_available = True
        except Exception:
            _redis = None
            _redis_available = False

    return _redis if _redis_available else None


def _require_queue_client():
    if not settings.ai_queue.enabled:
        raise HTTPException(status_code=503, detail="AI job queue is disabled.")

    client = _get_redis_client()
    if not client:
        raise HTTPException(status_code=503, detail="Redis is unavailable for AI job queue.")
    return client


def _serialize_job(job: dict[str, Any]) -> str:
    return json.dumps(job)


def _deserialize_job(raw: str | None) -> dict[str, Any] | None:
    if not raw:
        return None
    return json.loads(raw)


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _duration_ms(started_at: str | None, completed_at: str | None) -> int | None:
    started = _parse_iso(started_at)
    completed = _parse_iso(completed_at)
    if not started or not completed:
        return None
    return max(int((completed - started).total_seconds() * 1000), 0)


def _append_event(job: dict[str, Any], stage: str, source: str, detail: str | None = None) -> None:
    events = job.setdefault("events", [])
    events.append(
        {
            "stage": stage,
            "source": source,
            "timestamp": _utcnow_iso(),
            "detail": detail,
        }
    )


def _job_uuid(job_id: str) -> UUID | None:
    try:
        return UUID(str(job_id))
    except (TypeError, ValueError):
        return None


def _maybe_uuid(value: str | None) -> UUID | None:
    if not value:
        return None
    try:
        return UUID(str(value))
    except (TypeError, ValueError):
        return None


def _record_audit_event(job: dict[str, Any], action: str, actor_user_id: str | None = None, detail: str | None = None) -> None:
    job_uuid = _job_uuid(job.get("job_id"))
    tenant_uuid = _maybe_uuid(job.get("tenant_id"))
    if not job_uuid or not tenant_uuid:
        return

    db = SessionLocal()
    try:
        db.add(
            AuditLog(
                tenant_id=tenant_uuid,
                user_id=_maybe_uuid(actor_user_id) or _maybe_uuid(job.get("user_id")),
                action=action,
                entity_type="ai_job",
                entity_id=job_uuid,
                metadata_={
                    "job_id": job.get("job_id"),
                    "job_type": job.get("job_type"),
                    "status": job.get("status"),
                    "trace_id": job.get("trace_id"),
                    "attempts": job.get("attempts", 0),
                    "worker_id": job.get("worker_id"),
                    "error": job.get("error"),
                    "detail": detail,
                },
            )
        )
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


def _persist_job_state(job: dict[str, Any]) -> None:
    job_uuid = _job_uuid(job.get("job_id"))
    tenant_uuid = _maybe_uuid(job.get("tenant_id"))
    if not job_uuid or not tenant_uuid:
        return

    db = SessionLocal()
    try:
        row = db.query(AIJob).filter(AIJob.id == job_uuid).first()
        if not row:
            row = AIJob(id=job_uuid, tenant_id=tenant_uuid)
            db.add(row)

        row.user_id = _maybe_uuid(job.get("user_id"))
        row.job_type = job.get("job_type")
        row.status = job.get("status")
        row.trace_id = job.get("trace_id")
        row.priority = job.get("priority")
        row.attempts = int(job.get("attempts", 0))
        row.max_retries = int(job.get("max_retries", settings.ai_queue.max_retries))
        row.worker_id = job.get("worker_id")
        row.error = job.get("error")
        row.request_payload = job.get("request")
        row.result_payload = job.get("result")

        created_at = _parse_iso(job.get("created_at"))
        updated_at = _parse_iso(job.get("updated_at"))
        started_at = _parse_iso(job.get("started_at"))
        completed_at = _parse_iso(job.get("completed_at"))
        if created_at:
            row.created_at = created_at
        if updated_at:
            row.updated_at = updated_at
        row.started_at = started_at
        row.completed_at = completed_at

        persisted_count = int(job.get("_persisted_event_count", 0))
        events = job.get("events", [])
        for event in events[persisted_count:]:
            event_timestamp = _parse_iso(event.get("timestamp")) or _utcnow()
            db.add(
                AIJobEvent(
                    ai_job_id=job_uuid,
                    tenant_id=tenant_uuid,
                    stage=event.get("stage", "unknown"),
                    source=event.get("source", "unknown"),
                    detail=event.get("detail"),
                    event_timestamp=event_timestamp,
                    payload=event,
                )
            )
        db.commit()
        job["_persisted_event_count"] = len(events)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _db_job_to_summary(row: AIJob) -> dict[str, Any]:
    duration_ms = None
    if row.started_at and row.completed_at:
        duration_ms = max(int((row.completed_at - row.started_at).total_seconds() * 1000), 0)
    return {
        "job_id": str(row.id),
        "job_type": row.job_type,
        "trace_id": row.trace_id,
        "status": row.status,
        "created_at": str(row.created_at) if row.created_at else None,
        "updated_at": str(row.updated_at) if row.updated_at else None,
        "started_at": str(row.started_at) if row.started_at else None,
        "completed_at": str(row.completed_at) if row.completed_at else None,
        "attempts": row.attempts,
        "max_retries": row.max_retries,
        "error": row.error,
        "priority": row.priority,
        "tenant_id": str(row.tenant_id),
        "user_id": str(row.user_id) if row.user_id else None,
        "worker_id": row.worker_id,
        "duration_ms": duration_ms,
        "result": row.result_payload,
        "request": row.request_payload,
    }


def _load_persisted_job(job_id: str, tenant_id: str | None = None) -> dict[str, Any] | None:
    job_uuid = _job_uuid(job_id)
    if not job_uuid:
        return None
    db = SessionLocal()
    try:
        query = db.query(AIJob).filter(AIJob.id == job_uuid)
        if tenant_id:
            tenant_uuid = _maybe_uuid(tenant_id)
            if not tenant_uuid:
                return None
            query = query.filter(AIJob.tenant_id == tenant_uuid)
        row = query.first()
        if not row:
            return None
        summary = _db_job_to_summary(row)
        events = db.query(AIJobEvent).filter(
            AIJobEvent.ai_job_id == row.id,
            AIJobEvent.tenant_id == row.tenant_id,
        ).order_by(AIJobEvent.event_timestamp.asc(), AIJobEvent.created_at.asc()).all()
        summary["events"] = [{
            "stage": event.stage,
            "source": event.source,
            "timestamp": event.event_timestamp.isoformat(),
            "detail": event.detail,
        } for event in events]
        summary["_persisted_event_count"] = len(summary["events"])
        return summary
    finally:
        db.close()


def _list_persisted_jobs_for_tenant(tenant_id: str, limit: int = 50) -> list[dict[str, Any]]:
    tenant_uuid = _maybe_uuid(tenant_id)
    if not tenant_uuid:
        return []
    db = SessionLocal()
    try:
        rows = db.query(AIJob).filter(
            AIJob.tenant_id == tenant_uuid,
        ).order_by(desc(AIJob.created_at)).limit(max(1, min(limit, 200))).all()
        return [_db_job_to_summary(row) for row in rows]
    finally:
        db.close()


def _metric_incr(client, tenant_id: str, field: str, delta: int) -> None:
    client.hincrby(_tenant_metrics_key(tenant_id), field, delta)
    client.hincrby(GLOBAL_METRICS_KEY, field, delta)


def _metric_getint(client, key: str, field: str) -> int:
    value = client.hget(key, field)
    return int(value or 0)


def _prune_recent_metrics(client, tenant_id: str) -> None:
    cutoff = time.time() - settings.ai_queue.metrics_window_seconds
    client.zremrangebyscore(_tenant_recent_completed_key(tenant_id), 0, cutoff)
    client.zremrangebyscore(_tenant_recent_failed_key(tenant_id), 0, cutoff)


def _job_priority(job_type: str) -> int:
    return JOB_PRIORITIES.get(job_type, 50)


def _priority_score(job_type: str) -> int:
    base = _job_priority(job_type)
    return base * 10**13 + int(time.time() * 1000)


def _ensure_capacity(client, tenant_id: str) -> None:
    total_pending = _metric_getint(client, GLOBAL_METRICS_KEY, "pending_depth")
    tenant_pending = _metric_getint(client, _tenant_metrics_key(tenant_id), "pending_depth")
    if total_pending >= settings.ai_queue.max_pending_jobs:
        raise HTTPException(status_code=429, detail="AI queue is full. Try again later.")
    if tenant_pending >= settings.ai_queue.max_pending_jobs_per_tenant:
        raise HTTPException(status_code=429, detail="Tenant AI queue limit reached. Wait for jobs to finish.")


def _register_ready_tenant(client, tenant_id: str) -> None:
    if not client.sismember(READY_TENANTS_ACTIVE_KEY, tenant_id):
        client.sadd(READY_TENANTS_ACTIVE_KEY, tenant_id)
        client.rpush(READY_TENANTS_KEY, tenant_id)


def _cleanup_missing_index_entries(client, index_key: str, members: list[str]) -> None:
    stale = [member for member in members if not client.get(_job_key(member))]
    if stale:
        client.zrem(index_key, *stale)


def _current_jobs_from_index(client, tenant_id: str, limit: int | None = None) -> list[dict[str, Any]]:
    index_key = _tenant_index_key(tenant_id)
    end = -1 if limit is None else max(limit - 1, 0)
    job_ids = client.zrevrange(index_key, 0, end)
    _cleanup_missing_index_entries(client, index_key, job_ids)
    jobs = []
    for job_id in client.zrevrange(index_key, 0, end):
        job = _deserialize_job(client.get(_job_key(job_id)))
        if job:
            jobs.append(job)
    return jobs


def build_public_job_response(job: dict[str, Any]) -> dict[str, Any]:
    status = job.get("status", "unknown")
    response = {
        "job_id": job["job_id"],
        "job_type": job["job_type"],
        "trace_id": job.get("trace_id"),
        "status": status,
        "created_at": job.get("created_at"),
        "updated_at": job.get("updated_at"),
        "started_at": job.get("started_at"),
        "completed_at": job.get("completed_at"),
        "attempts": job.get("attempts", 0),
        "max_retries": job.get("max_retries", settings.ai_queue.max_retries),
        "error": job.get("error"),
        "priority": job.get("priority"),
    }
    if status == STATUS_COMPLETED:
        response["result"] = job.get("result")
    if status in {STATUS_QUEUED, STATUS_RUNNING}:
        response["poll_after_ms"] = 2000
    return response


def _admin_job_summary(job: dict[str, Any]) -> dict[str, Any]:
    events = job.get("events", [])
    return {
        **build_public_job_response(job),
        "tenant_id": job.get("tenant_id"),
        "user_id": job.get("user_id"),
        "worker_id": job.get("worker_id"),
        "duration_ms": _duration_ms(job.get("started_at"), job.get("completed_at")),
        "last_event": events[-1] if events else None,
    }


def list_jobs_for_tenant(
    tenant_id: str,
    limit: int = 50,
    status: str | None = None,
    job_type: str | None = None,
) -> list[dict[str, Any]]:
    client = _get_redis_client()
    jobs = _current_jobs_from_index(client, tenant_id, limit=None) if client else []
    if status:
        jobs = [job for job in jobs if job.get("status") == status]
    if job_type:
        jobs = [job for job in jobs if job.get("job_type") == job_type]
    live_summaries = [_admin_job_summary(job) for job in jobs[: max(1, min(limit, 200))]]
    if len(live_summaries) >= limit:
        return live_summaries

    seen_job_ids = {job["job_id"] for job in live_summaries}
    persisted = _list_persisted_jobs_for_tenant(tenant_id, limit=max(1, min(limit * 2, 400)))
    for row in persisted:
        if row["job_id"] in seen_job_ids:
            continue
        if status and row.get("status") != status:
            continue
        if job_type and row.get("job_type") != job_type:
            continue
        live_summaries.append(row)
        if len(live_summaries) >= limit:
            break
    return live_summaries


def get_job(job_id: str) -> dict[str, Any] | None:
    client = _get_redis_client()
    if client:
        job = _deserialize_job(client.get(_job_key(job_id)))
        if job:
            return job
    return _load_persisted_job(job_id)


def get_job_detail_for_tenant(job_id: str, tenant_id: str) -> dict[str, Any] | None:
    job = get_job(job_id)
    if not job or job.get("tenant_id") != tenant_id:
        persisted = _load_persisted_job(job_id, tenant_id=tenant_id)
        if not persisted:
            return None
        return {
            **{k: persisted.get(k) for k in (
                "job_id", "job_type", "trace_id", "status", "created_at", "updated_at",
                "started_at", "completed_at", "attempts", "max_retries", "error", "priority",
                "tenant_id", "user_id", "worker_id", "duration_ms",
            )},
            "request": persisted.get("request"),
            "result": persisted.get("result"),
            "events": persisted.get("events", []),
        }
    return {
        **_admin_job_summary(job),
        "request": job.get("request"),
        "result": job.get("result"),
        "events": job.get("events", []),
    }


def get_queue_metrics(tenant_id: str) -> dict[str, Any]:
    client = _require_queue_client()
    _prune_recent_metrics(client, tenant_id)
    jobs = _current_jobs_from_index(client, tenant_id, limit=None)
    status_counts = Counter(job.get("status", "unknown") for job in jobs)
    type_counts = Counter(job.get("job_type", "unknown") for job in jobs)

    return {
        "pending_depth": _metric_getint(client, _tenant_metrics_key(tenant_id), "pending_depth"),
        "processing_depth": _metric_getint(client, _tenant_metrics_key(tenant_id), "processing_depth"),
        "tracked_jobs": client.zcard(_tenant_index_key(tenant_id)),
        "completed_last_window": client.zcard(_tenant_recent_completed_key(tenant_id)),
        "failed_last_window": client.zcard(_tenant_recent_failed_key(tenant_id)),
        "failure_rate_pct": round(
            (
                client.zcard(_tenant_recent_failed_key(tenant_id)) /
                max(client.zcard(_tenant_recent_completed_key(tenant_id)) + client.zcard(_tenant_recent_failed_key(tenant_id)), 1)
            ) * 100,
            1,
        ),
        "retry_count": _metric_getint(client, _tenant_metrics_key(tenant_id), "retry_total"),
        "stuck_jobs": len([
            job["job_id"]
            for job in jobs
            if job.get("status") == STATUS_RUNNING
            and _parse_iso(job.get("started_at"))
            and (_utcnow() - _parse_iso(job.get("started_at"))).total_seconds() >= settings.ai_queue.stuck_after_seconds
        ]),
        "stuck_job_ids": [
            job["job_id"]
            for job in jobs
            if job.get("status") == STATUS_RUNNING
            and _parse_iso(job.get("started_at"))
            and (_utcnow() - _parse_iso(job.get("started_at"))).total_seconds() >= settings.ai_queue.stuck_after_seconds
        ][:10],
        "dead_letter_count": client.zcard(_tenant_dead_letter_key(tenant_id)),
        "metrics_window_seconds": settings.ai_queue.metrics_window_seconds,
        "stuck_after_seconds": settings.ai_queue.stuck_after_seconds,
        "max_pending_jobs": settings.ai_queue.max_pending_jobs,
        "max_pending_jobs_per_tenant": settings.ai_queue.max_pending_jobs_per_tenant,
        "by_status": dict(status_counts),
        "by_type": dict(type_counts),
    }


def save_job(job: dict[str, Any]) -> None:
    client = _require_queue_client()
    _persist_job_state(job)
    client.setex(
        _job_key(job["job_id"]),
        settings.ai_queue.result_ttl_seconds,
        _serialize_job(job),
    )


def enqueue_job(
    job_type: str,
    payload: dict[str, Any],
    tenant_id: str,
    user_id: str,
    trace_id: str | None = None,
    source: str = "api",
) -> dict[str, Any]:
    client = _require_queue_client()
    _ensure_capacity(client, tenant_id)

    job_id = str(uuid.uuid4())
    now = _utcnow_iso()
    created_score = time.time()
    trace_id = trace_id or uuid.uuid4().hex[:12]
    job = {
        "job_id": job_id,
        "job_type": job_type,
        "priority": _job_priority(job_type),
        "trace_id": trace_id,
        "otel_traceparent": get_current_traceparent(),
        "status": STATUS_QUEUED,
        "tenant_id": tenant_id,
        "user_id": user_id,
        "worker_id": None,
        "request": payload,
        "result": None,
        "error": None,
        "attempts": 0,
        "max_retries": settings.ai_queue.max_retries,
        "created_at": now,
        "updated_at": now,
        "started_at": None,
        "completed_at": None,
        "events": [],
    }
    _append_event(job, "job.enqueued", source, f"Queued {job_type} with priority {job['priority']}")

    _persist_job_state(job)

    pipe = client.pipeline()
    pipe.setex(_job_key(job_id), settings.ai_queue.result_ttl_seconds, _serialize_job(job))
    pipe.zadd(_user_index_key(user_id), {job_id: created_score})
    pipe.expire(_user_index_key(user_id), settings.ai_queue.result_ttl_seconds)
    pipe.zadd(_tenant_index_key(tenant_id), {job_id: created_score})
    pipe.zadd(_tenant_queue_key(tenant_id), {job_id: _priority_score(job_type)})
    pipe.execute()

    _register_ready_tenant(client, tenant_id)
    _metric_incr(client, tenant_id, "pending_depth", 1)
    _metric_incr(client, tenant_id, "tracked_jobs_total", 1)
    _record_audit_event(job, "ai_job.enqueued", actor_user_id=user_id, detail=source)
    return build_public_job_response(job)

_CLAIM_JOB_LUA = """
local queue_key = KEYS[1]
local processing_key = KEYS[2]
local items = redis.call('ZPOPMIN', queue_key, 1)
if items and #items > 0 then
    local job_id = items[1]
    redis.call('LPUSH', processing_key, job_id)
    return job_id
end
return nil
"""

def _claim_next_job_for_tenant(client, tenant_id: str) -> str | None:
    job_id = client.eval(
        _CLAIM_JOB_LUA, 
        2, 
        _tenant_queue_key(tenant_id), 
        settings.ai_queue.processing_key
    )
    
    if not job_id:
        client.srem(READY_TENANTS_ACTIVE_KEY, tenant_id)
        return None

    # Handle byte decryption from Lua script if necessary
    if isinstance(job_id, bytes):
        job_id = job_id.decode("utf-8")

    _metric_incr(client, tenant_id, "pending_depth", -1)
    _metric_incr(client, tenant_id, "processing_depth", 1)

    if client.zcard(_tenant_queue_key(tenant_id)) > 0:
        client.rpush(READY_TENANTS_KEY, tenant_id)
    else:
        client.srem(READY_TENANTS_ACTIVE_KEY, tenant_id)
    return job_id


def is_queue_paused() -> bool:
    client = _get_redis_client()
    if not client:
        return False
    return client.get(QUEUE_PAUSED_KEY) == "1"


def pause_queue() -> None:
    client = _require_queue_client()
    client.set(QUEUE_PAUSED_KEY, "1")


def resume_queue() -> None:
    client = _require_queue_client()
    client.delete(QUEUE_PAUSED_KEY)


def drain_queue(tenant_id: str | None = None) -> int:
    client = _require_queue_client()
    drained = 0
    
    if tenant_id:
        targets = [tenant_id]
        client.srem(READY_TENANTS_ACTIVE_KEY, tenant_id)
        client.lrem(READY_TENANTS_KEY, 0, tenant_id)
    else:
        targets = client.smembers(READY_TENANTS_ACTIVE_KEY)
        client.delete(READY_TENANTS_ACTIVE_KEY)
        client.delete(READY_TENANTS_KEY)

    for target in targets:
        # Move all items from pending queue to dead letter immediately
        while True:
            items = client.zpopmin(_tenant_queue_key(target), 50)
            if not items:
                break
            for job_id, _ in items:
                job = get_job(job_id)
                if job:
                    _transition_to_terminal(job, STATUS_DEAD_LETTER, "Drained by superadmin")
                    save_job(job)
                    client.zadd(_tenant_dead_letter_key(target), {job_id: time.time()})
                drained += 1
        
        _metric_incr(client, target, "pending_depth", -drained)
        
    return drained


def claim_next_job(timeout_seconds: int | None = None) -> str | None:
    if is_queue_paused():
        return None
        
    client = _require_queue_client()
    timeout = settings.ai_queue.poll_timeout_seconds if timeout_seconds is None else timeout_seconds
    deadline = time.time() + max(timeout, 0)

    while True:
        tenant_id = client.lpop(READY_TENANTS_KEY)
        if tenant_id:
            job_id = _claim_next_job_for_tenant(client, tenant_id)
            if job_id:
                return job_id

        if timeout == 0 or time.time() >= deadline:
            return None
        time.sleep(min(1.0, max(deadline - time.time(), 0)))


def acknowledge_job(job_id: str) -> None:
    client = _require_queue_client()
    client.lrem(settings.ai_queue.processing_key, 1, job_id)


def recover_processing_jobs() -> int:
    client = _require_queue_client()
    recovered = 0
    while True:
        job_id = client.rpop(settings.ai_queue.processing_key)
        if not job_id:
            return recovered
        job = get_job(job_id)
        if not job:
            continue
        tenant_id = job.get("tenant_id")
        if not tenant_id:
            continue
        client.zadd(_tenant_queue_key(tenant_id), {job_id: _priority_score(job.get("job_type", "unknown"))})
        _register_ready_tenant(client, tenant_id)
        _metric_incr(client, tenant_id, "pending_depth", 1)
        _metric_incr(client, tenant_id, "processing_depth", -1)
        job["status"] = STATUS_QUEUED
        job["worker_id"] = None
        job["updated_at"] = _utcnow_iso()
        _append_event(job, "worker.recovered", "worker", "Recovered after worker restart")
        save_job(job)
        recovered += 1


async def _execute_job(job: dict[str, Any]) -> dict[str, Any]:
    job_type = job["job_type"]
    payload = job["request"]
    trace_id = job.get("trace_id")

    if job_type == JOB_TYPE_QUERY:
        return await run_text_query(InternalAIQueryRequest(**payload), trace_id=trace_id)
    if job_type == JOB_TYPE_AUDIO:
        return await run_audio_overview(InternalAudioOverviewRequest(**payload), trace_id=trace_id)
    if job_type == JOB_TYPE_VIDEO:
        return await run_video_overview(InternalVideoOverviewRequest(**payload), trace_id=trace_id)
    if job_type == JOB_TYPE_STUDY_TOOL:
        return await run_study_tool(InternalStudyToolGenerateRequest(**payload), trace_id=trace_id)
    if job_type == JOB_TYPE_TEACHER_ASSESSMENT:
        return await run_teacher_assessment(InternalTeacherAssessmentRequest(**payload), trace_id=trace_id)
    if job_type == JOB_TYPE_URL_INGEST:
        return await run_url_ingestion(InternalIngestURLRequest(**payload), trace_id=trace_id)
    if job_type == JOB_TYPE_TEACHER_DOCUMENT_INGEST:
        return await run_teacher_document_ingestion(InternalTeacherDocumentIngestRequest(**payload), trace_id=trace_id)
    if job_type == JOB_TYPE_TEACHER_YOUTUBE_INGEST:
        return await run_teacher_youtube_ingestion(InternalTeacherYoutubeIngestRequest(**payload), trace_id=trace_id)

    raise HTTPException(status_code=400, detail=f"Unsupported AI job type: {job_type}")


def _should_retry(exc: Exception) -> bool:
    if isinstance(exc, HTTPException):
        return exc.status_code >= 500
    return True


def _error_detail(exc: Exception) -> str:
    if isinstance(exc, HTTPException):
        return str(exc.detail)
    return str(exc) or exc.__class__.__name__


def _transition_to_terminal(job: dict[str, Any], status: str, detail: str | None = None) -> dict[str, Any]:
    job["status"] = status
    job["updated_at"] = _utcnow_iso()
    job["completed_at"] = job["updated_at"]
    if status == STATUS_COMPLETED:
        _append_event(job, "worker.completed", "worker", detail)
    elif status == STATUS_FAILED:
        _append_event(job, "worker.failed", "worker", detail)
    elif status == STATUS_CANCELLED:
        _append_event(job, "job.cancelled", "admin", detail)
    elif status == STATUS_DEAD_LETTER:
        _append_event(job, "job.dead_lettered", "admin", detail)
    return job


async def process_job(job_id: str, worker_id: str | None = None) -> dict[str, Any] | None:
    job = get_job(job_id)
    if not job:
        acknowledge_job(job_id)
        return None

    tracer = get_tracer("vidyaos.ai_queue")
    context = extract_context_from_traceparent(job.get("otel_traceparent"))

    async def _run() -> dict[str, Any]:
        nonlocal job
        now = _utcnow_iso()
        job["status"] = STATUS_RUNNING
        job["worker_id"] = worker_id or job.get("worker_id") or "ai-worker"
        job["started_at"] = job.get("started_at") or now
        job["updated_at"] = now
        job["attempts"] = int(job.get("attempts", 0)) + 1
        _append_event(job, "worker.started", "worker", f"Attempt {job['attempts']}")
        _append_event(job, "ai_service.requested", "worker", "Dispatching to dedicated AI service")
        save_job(job)
        _record_audit_event(job, "ai_job.started", detail=job["worker_id"])

        try:
            result = await _execute_job(job)
        except Exception as exc:
            retryable = _should_retry(exc)
            job["error"] = _error_detail(exc)
            acknowledge_job(job_id)
            _metric_incr(client := _require_queue_client(), job["tenant_id"], "processing_depth", -1)

            if retryable and job["attempts"] <= int(job.get("max_retries", settings.ai_queue.max_retries)):
                job["status"] = STATUS_QUEUED
                job["worker_id"] = None
                job["updated_at"] = _utcnow_iso()
                _append_event(job, "worker.retry_scheduled", "worker", job["error"])
                save_job(job)
                client.zadd(_tenant_queue_key(job["tenant_id"]), {job_id: _priority_score(job["job_type"])})
                _register_ready_tenant(client, job["tenant_id"])
                _metric_incr(client, job["tenant_id"], "pending_depth", 1)
                _metric_incr(client, job["tenant_id"], "retry_total", 1)
                _record_audit_event(job, "ai_job.retry_scheduled", detail=job["error"])
            else:
                job = _transition_to_terminal(job, STATUS_FAILED, job["error"])
                save_job(job)
                client.zadd(_tenant_recent_failed_key(job["tenant_id"]), {job_id: time.time()})
                _prune_recent_metrics(client, job["tenant_id"])
                _record_audit_event(job, "ai_job.failed", detail=job["error"])
            return job

        _append_event(job, "ai_service.completed", "worker", "Dedicated AI service returned successfully")

        acknowledge_job(job_id)
        client = _require_queue_client()
        _metric_incr(client, job["tenant_id"], "processing_depth", -1)
        job["result"] = result
        job["error"] = None
        job = _transition_to_terminal(job, STATUS_COMPLETED, f"Completed in {_duration_ms(job.get('started_at'), _utcnow_iso()) or 0}ms")
        save_job(job)
        client.zadd(_tenant_recent_completed_key(job["tenant_id"]), {job_id: time.time()})
        _prune_recent_metrics(client, job["tenant_id"])
        _record_audit_event(job, "ai_job.completed")
        return job

    if tracer:
        with tracer.start_as_current_span(
            "ai_queue.process_job",
            context=context,
            attributes={
                "vidyaos.job_id": job_id,
                "vidyaos.job_type": job.get("job_type", ""),
                "vidyaos.trace_id": job.get("trace_id", ""),
                "vidyaos.tenant_id": job.get("tenant_id", ""),
            },
        ):
            return await _run()
    return await _run()


def cancel_job(job_id: str, tenant_id: str, actor_user_id: str | None = None) -> dict[str, Any]:
    client = _require_queue_client()
    job = get_job(job_id)
    if not job or job.get("tenant_id") != tenant_id:
        raise HTTPException(status_code=404, detail="AI job not found")
    if job.get("status") != STATUS_QUEUED:
        raise HTTPException(status_code=409, detail="Only queued jobs can be cancelled")

    removed = client.zrem(_tenant_queue_key(tenant_id), job_id)
    if not removed:
        raise HTTPException(status_code=409, detail="Job is no longer queued")

    _metric_incr(client, tenant_id, "pending_depth", -1)
    job["worker_id"] = None
    job["error"] = "Cancelled by admin"
    job = _transition_to_terminal(job, STATUS_CANCELLED, "Cancelled before worker pickup")
    save_job(job)
    _record_audit_event(job, "ai_job.cancelled", actor_user_id=actor_user_id)
    return _admin_job_summary(job)


def retry_job(job_id: str, tenant_id: str, actor_user_id: str | None = None) -> dict[str, Any]:
    client = _require_queue_client()
    _ensure_capacity(client, tenant_id)
    job = get_job(job_id)
    if not job or job.get("tenant_id") != tenant_id:
        raise HTTPException(status_code=404, detail="AI job not found")
    if job.get("status") not in {STATUS_FAILED, STATUS_DEAD_LETTER}:
        raise HTTPException(status_code=409, detail="Only failed or dead-letter jobs can be retried")

    if job.get("status") == STATUS_DEAD_LETTER:
        client.zrem(_tenant_dead_letter_key(tenant_id), job_id)

    job["status"] = STATUS_QUEUED
    job["worker_id"] = None
    job["result"] = None
    job["error"] = None
    job["completed_at"] = None
    job["updated_at"] = _utcnow_iso()
    _append_event(job, "job.retry_requested", "admin", "Manually requeued by admin")
    save_job(job)
    client.zadd(_tenant_queue_key(tenant_id), {job_id: _priority_score(job["job_type"])})
    _register_ready_tenant(client, tenant_id)
    _metric_incr(client, tenant_id, "pending_depth", 1)
    _metric_incr(client, tenant_id, "retry_total", 1)
    _record_audit_event(job, "ai_job.retry_requested", actor_user_id=actor_user_id)
    return _admin_job_summary(job)


def move_to_dead_letter(job_id: str, tenant_id: str, actor_user_id: str | None = None) -> dict[str, Any]:
    client = _require_queue_client()
    job = get_job(job_id)
    if not job or job.get("tenant_id") != tenant_id:
        raise HTTPException(status_code=404, detail="AI job not found")
    if job.get("status") != STATUS_FAILED:
        raise HTTPException(status_code=409, detail="Only failed jobs can be moved to dead letter")

    job = _transition_to_terminal(job, STATUS_DEAD_LETTER, "Moved to dead letter bucket")
    save_job(job)
    client.zadd(_tenant_dead_letter_key(tenant_id), {job_id: time.time()})
    _metric_incr(client, tenant_id, "dead_letter_total", 1)
    _record_audit_event(job, "ai_job.dead_lettered", actor_user_id=actor_user_id)
    return _admin_job_summary(job)
