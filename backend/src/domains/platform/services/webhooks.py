"""Webhook event dispatch service."""
import hashlib
import hmac
import json
import uuid
from datetime import datetime, timezone
from typing import Any

import httpx
from sqlalchemy.orm import Session

from src.domains.platform.models.webhook import WebhookDelivery, WebhookSubscription


def _sign_payload(secret: str, body: str) -> str:
    digest = hmac.new(secret.encode("utf-8"), body.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"sha256={digest}"


async def emit_webhook_event(
    db: Session,
    tenant_id: Any,
    event_type: str,
    data: dict,
) -> dict:
    """Dispatch a webhook event to active subscribers and log delivery status."""
    subscriptions = db.query(WebhookSubscription).filter(
        WebhookSubscription.tenant_id == tenant_id,
        WebhookSubscription.event_type == event_type,
        WebhookSubscription.is_active,
    ).all()

    if not subscriptions:
        return {"subscriptions": 0, "delivered": 0}

    envelope = {
        "id": str(uuid.uuid4()),
        "event_type": event_type,
        "tenant_id": str(tenant_id),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "data": data,
    }
    body = json.dumps(envelope, separators=(",", ":"), sort_keys=True)

    deliveries: list[WebhookDelivery] = []
    for sub in subscriptions:
        delivery = WebhookDelivery(
            tenant_id=tenant_id,
            subscription_id=sub.id,
            event_type=event_type,
            payload=envelope,
            status="pending",
            attempt_count=0,
        )
        db.add(delivery)
        deliveries.append(delivery)
    db.commit()

    delivered_count = 0
    for delivery, sub in zip(deliveries, subscriptions):
        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Event": event_type,
            "X-Webhook-Delivery": str(delivery.id),
            "X-Webhook-Signature": _sign_payload(sub.secret, body),
        }

        delivery.attempt_count = (delivery.attempt_count or 0) + 1
        delivery.last_attempt_at = datetime.now(timezone.utc)

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(sub.target_url, content=body, headers=headers)
            delivery.status_code = response.status_code
            delivery.response_body = response.text[:2000]
            if 200 <= response.status_code < 300:
                delivery.status = "delivered"
                delivered_count += 1
            else:
                delivery.status = "failed"
        except Exception as exc:
            delivery.status = "failed"
            delivery.response_body = str(exc)[:2000]

    db.commit()
    return {"subscriptions": len(subscriptions), "delivered": delivered_count}
