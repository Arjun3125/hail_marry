"""Platform Telemetry Endpoints."""
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user_optional, get_tenant_id_optional
from database import get_db
from src.domains.platform.services.telemetry_events import record_business_event

router = APIRouter(prefix="/telemetry", tags=["telemetry"])


@router.post("/event")
async def track_event(
    request: Request,
    event_payload: dict[str, Any],
    db: Session = Depends(get_db),
    user_id: UUID | None = Depends(get_current_user_optional),
    tenant_id: UUID | None = Depends(get_tenant_id_optional),
):
    """Record a business/product event from the frontend."""
    event_name: Any | None = event_payload.get("eventName")
    if not event_name:
        return {"status": "ignored", "reason": "missing_event_name"}

    # Extract metadata and surface info
    metadata = event_payload.get("metadata", {})
    event_family: Any | None = event_payload.get("eventFamily")
    surface: Any | None = event_payload.get("surface")
    target: Any | None = event_payload.get("target")
    channel: Any | None = event_payload.get("channel")
    value = float(event_payload.get("value", 1.0))

    # Persist the event
    record_business_event(
        db=db,
        event_name=event_name,
        user_id=str(user_id) if user_id else None,
        tenant_id=str(tenant_id) if tenant_id else None,
        event_family=event_family,
        surface=surface,
        target=target,
        channel=channel,
        value=value,
        metadata=metadata,
    )

    return {"status": "recorded", "event": event_name}
