"""Persistent trace event recording and lookup."""
from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from database import SessionLocal
from models.ai_query import AIQuery
from models.audit_log import AuditLog


def _maybe_uuid(value: str | None) -> UUID | None:
    if not value:
        return None
    try:
        return UUID(str(value))
    except (TypeError, ValueError):
        return None


def record_trace_event(
    *,
    trace_id: str | None,
    tenant_id: str | None,
    source: str,
    stage: str,
    detail: str | None = None,
    user_id: str | None = None,
    status: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    if not trace_id or not tenant_id:
        return

    tenant_uuid = _maybe_uuid(tenant_id)
    if not tenant_uuid:
        return

    db = SessionLocal()
    try:
        payload = {
            "trace_id": trace_id,
            "source": source,
            "stage": stage,
            "detail": detail,
            "status": status,
            **(metadata or {}),
        }
        db.add(
            AuditLog(
                tenant_id=tenant_uuid,
                user_id=_maybe_uuid(user_id),
                action="trace.event",
                entity_type="trace_event",
                entity_id=None,
                metadata_=payload,
            )
        )
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


def get_trace_events(trace_id: str, tenant_id: UUID, limit: int = 200) -> list[dict[str, Any]]:
    db = SessionLocal()
    try:
        rows = db.query(AuditLog).filter(
            AuditLog.tenant_id == tenant_id,
            AuditLog.entity_type.in_(["trace_event", "ai_job"]),
        ).order_by(AuditLog.created_at.desc()).limit(max(limit * 3, 200)).all()

        events: list[dict[str, Any]] = []
        for row in rows:
            metadata = row.metadata_ or {}
            if metadata.get("trace_id") != trace_id:
                continue
            events.append({
                "created_at": str(row.created_at),
                "action": row.action,
                "entity_type": row.entity_type,
                "metadata": metadata,
            })
            if len(events) >= limit:
                break

        query = db.query(AIQuery).filter(
            AIQuery.tenant_id == tenant_id,
            AIQuery.trace_id == trace_id,
        ).order_by(AIQuery.created_at.desc()).first()
        if query:
            events.append({
                "created_at": str(query.created_at),
                "action": "ai.query.recorded",
                "entity_type": "ai_query",
                "metadata": {
                    "trace_id": trace_id,
                    "mode": query.mode,
                    "token_usage": query.token_usage,
                    "response_time_ms": query.response_time_ms,
                    "citation_count": query.citation_count,
                },
            })

        events.sort(key=lambda item: item["created_at"])
        return events[:limit]
    finally:
        db.close()
