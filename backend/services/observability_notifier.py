"""Webhook-based alert delivery with deduplication."""
from __future__ import annotations

import json
import logging
import time
from hashlib import sha256
from typing import Any

from sqlalchemy.orm import Session

from config import settings
from services.webhooks import emit_webhook_event
from services.ai_queue import _get_redis_client

logger = logging.getLogger(__name__)

ALERT_DEDUPE_PREFIX = "observability:alerts:sent:"
ALERT_DEDUPE_TTL_SECONDS = 900


def _dedupe_key(tenant_id: str, alert: dict[str, Any]) -> str:
    signature = sha256(json.dumps(alert, sort_keys=True).encode("utf-8")).hexdigest()
    return f"{ALERT_DEDUPE_PREFIX}{tenant_id}:{signature}"


async def dispatch_alerts(db: Session, tenant_id: str, alerts: list[dict[str, Any]], force: bool = False) -> dict[str, int]:
    if not alerts:
        return {"alerts": 0, "delivered": 0}

    client = _get_redis_client()
    delivered = 0
    dispatched = 0
    for alert in alerts:
        key = _dedupe_key(tenant_id, alert)
        if client and not force and client.get(key):
            continue
        if client:
            client.setex(key, ALERT_DEDUPE_TTL_SECONDS, str(int(time.time())))
        
        # Webhook Pipeline
        result = await emit_webhook_event(
            db=db,
            tenant_id=tenant_id,
            event_type="observability.alert.raised",
            data={"alert": alert},
        )
        
        # Simulated Email Pipeline (for Superadmins/Operators)
        _mock_dispatch_email(tenant_id, alert)
        
        dispatched += 1
        delivered += int(result.get("delivered", 0))

    return {"alerts": dispatched, "delivered": delivered}


def _mock_dispatch_email(tenant_id: str, alert: dict[str, Any]) -> None:
    """Mock dispatcher representing an SMTP/SendGrid integration."""
    alert_name = alert.get("alertname", "Unknown Alert")
    severity = alert.get("severity", "warning")
    logger.info(
        "EMAIL DISPATCH: Sending %s alert '%s' for tenant %s to operator/admin.", 
        severity.upper(), alert_name, tenant_id
    )
