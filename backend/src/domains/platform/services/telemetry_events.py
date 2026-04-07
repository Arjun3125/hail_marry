"""Business Telemetry & Event Ingestion.

Custom OpenTelemetry and Prometheus wrappers for tracking
business-level KPIs specifically critical for the Indian EdTech market.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from database import SessionLocal
from src.domains.platform.services import (
    mastery_tracking_service,
    telemetry,
)
from src.domains.platform.services.telemetry import _load_otel

logger = logging.getLogger("business_telemetry")

# Simple counters for environments without Prometheus running
_METRICS: dict[str, int | float] = {}


def _parse_uuid(value: str | UUID | None) -> UUID | None:
    try:
        return UUID(str(value)) if value else None
    except (TypeError, ValueError):
        return None


def increment_metric(name: str, amount: int | float = 1, tags: dict[str, str] | None = None) -> None:
    """Increment a business metric counter."""
    key = name
    if tags:
        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        key = f"{name}[{tag_str}]"
        
    _METRICS[key] = _METRICS.get(key, 0) + amount
    logger.debug("Metrics | %s += %s = %s", key, amount, _METRICS[key])
    
    # Also push to current trace if available
    otel = _load_otel()
    if otel:
        try:
            current_span = otel["trace"].get_current_span()
            if current_span and current_span.is_recording():
                current_span.set_attribute(f"metric.{name}", _METRICS[key])
                if tags:
                    for k, v in tags.items():
                        current_span.set_attribute(f"metric.{name}.tag.{k}", v)
        except Exception:
            pass


def record_business_event(
    event_name: str,
    user_id: str | None = None,
    tenant_id: str | None = None,
    metadata: dict[str, Any] | None = None,
    *,
    db=None,
    event_family: str | None = None,
    surface: str | None = None,
    target: str | None = None,
    channel: str | None = None,
    value: float = 1.0,
) -> None:
    """Record a structured business event for analytics (e.g. 'whatsapp_homework_query')."""
    payload = {
        "event": event_name,
        "user_id": user_id,
        "tenant_id": tenant_id,
        "event_family": event_family,
        "surface": surface,
        "target": target,
        "channel": channel,
        "value": value,
        **(metadata or {})
    }
    
    # Log for ingestion via FluentBit / DataDog
    logger.info("BUSINESS_EVENT: %s", payload)
    
    # Push to trace
    otel = _load_otel()
    if otel:
        try:
            current_span = otel["trace"].get_current_span()
            if current_span and current_span.is_recording():
                current_span.add_event(event_name, payload)
        except Exception:
            pass

    session = db
    owns_session = False
    try:
        from src.domains.platform.models.analytics_event import AnalyticsEvent

        if session is None:
            session = SessionLocal()
            owns_session = True

        event = AnalyticsEvent(
            tenant_id=_parse_uuid(tenant_id),
            user_id=_parse_uuid(user_id),
            event_name=event_name,
            event_family=event_family,
            surface=surface,
            target=target,
            channel=channel,
            value=float(value),
            event_date=datetime.now(timezone.utc).date(),
            metadata_=metadata or {},
        )
        session.add(event)
        
        # Trigger Educational/Mastery Sync
        if event_family == "educational":
            _sync_educational_mastery(session, tenant_id, user_id, event_name, metadata)

        if owns_session:
            session.commit()
        else:
            session.flush()
    except Exception:
        logger.exception("Failed to persist analytics event: %s", event_name)
        if owns_session and session is not None:
            session.rollback()
    finally:
        if owns_session and session is not None:
            session.close()


def _sync_educational_mastery(
    db: SessionLocal,
    tenant_id: str | None,
    user_id: str | None,
    event_name: str,
    metadata: dict[str, Any] | None,
) -> None:
    """Trigger mastery tracking service based on incoming telemetry."""
    if not tenant_id or not user_id or not metadata:
        return

    try:
        t_id = UUID(tenant_id)
        u_id = UUID(user_id)
        topic = metadata.get("topic", "General")
        subject_id = metadata.get("subject_id")
        s_id = UUID(str(subject_id)) if subject_id else None

        if event_name == "quiz_completed":
            mastery_tracking_service.record_quiz_completion(
                db=db,
                tenant_id=t_id,
                user_id=u_id,
                topic=topic,
                total_questions=int(metadata.get("total", 0)),
                correct_answers=int(metadata.get("score", 0)),
                subject_id=s_id,
            )
        elif event_name == "flashcard_mastered":
            mastery_tracking_service.record_review_completion(
                db=db,
                tenant_id=t_id,
                user_id=u_id,
                topic=topic,
                rating=int(metadata.get("rating", 3)),
                next_review_at=None,
                subject_id=s_id,
            )
    except Exception as exc:
        logger.error("Failed to sync mastery from telemetry: %s", exc)
