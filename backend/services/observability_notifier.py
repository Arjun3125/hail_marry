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


def _dispatch_alert_email(tenant_id: str, alert: dict[str, Any]) -> int:
    recipients = [email for email in settings.observability.alert_email_recipients if email]
    if not recipients:
        return 0

    from services.emailer import send_email

    alert_name = alert.get("alertname", "Unknown Alert")
    severity = alert.get("severity", "warning")
    subject = f"[VidyaOS] {alert_name} ({severity})"
    text_body = (
        f"Alert: {alert_name}\n"
        f"Severity: {severity}\n"
        f"Tenant: {tenant_id}\n"
        f"Message: {alert.get('message', '-')}\n"
        f"Trace ID: {alert.get('trace_id', '-')}\n"
    )
    html_body = (
        f"<h3>{alert_name}</h3>"
        f"<p><strong>Severity:</strong> {severity}</p>"
        f"<p><strong>Tenant:</strong> {tenant_id}</p>"
        f"<p><strong>Message:</strong> {alert.get('message', '-')}</p>"
        f"<p><strong>Trace ID:</strong> {alert.get('trace_id', '-')}</p>"
    )

    delivered = 0
    for recipient in recipients:
        try:
            send_email(
                to_address=recipient,
                subject=subject,
                html_body=html_body,
                text_body=text_body,
            )
            delivered += 1
        except Exception:
            logger.exception("Alert email dispatch failed to %s", recipient)
    return delivered


def _dispatch_alert_sms(tenant_id: str, alert: dict[str, Any]) -> int:
    recipients = [number for number in settings.observability.alert_sms_recipients if number]
    if not recipients:
        return 0

    from services.sms import send_sms

    alert_name = alert.get("alertname", "Alert")
    severity = alert.get("severity", "warning")
    message = alert.get("message", "") or ""
    sms_body = f"[VidyaOS {severity.upper()}] {alert_name}: {message}".strip()
    delivered = 0
    for number in recipients:
        result = send_sms(to_number=number, message=sms_body)
        if result.get("sent"):
            delivered += 1
    return delivered


async def dispatch_alerts(db: Session, tenant_id: str, alerts: list[dict[str, Any]], force: bool = False) -> dict[str, int]:
    if not alerts:
        return {"alerts": 0, "delivered": 0, "email_delivered": 0, "sms_delivered": 0}

    client = _get_redis_client()
    delivered = 0
    dispatched = 0
    email_delivered = 0
    sms_delivered = 0
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
        
        email_delivered += _dispatch_alert_email(tenant_id, alert)
        sms_delivered += _dispatch_alert_sms(tenant_id, alert)

        dispatched += 1
        delivered += int(result.get("delivered", 0))

    return {
        "alerts": dispatched,
        "delivered": delivered,
        "email_delivered": email_delivered,
        "sms_delivered": sms_delivered,
    }


def _mock_dispatch_email(tenant_id: str, alert: dict[str, Any]) -> None:
    """Mock dispatcher representing an SMTP/SendGrid integration."""
    alert_name = alert.get("alertname", "Unknown Alert")
    severity = alert.get("severity", "warning")
    logger.info(
        "EMAIL DISPATCH: Sending %s alert '%s' for tenant %s to operator/admin.", 
        severity.upper(), alert_name, tenant_id
    )
