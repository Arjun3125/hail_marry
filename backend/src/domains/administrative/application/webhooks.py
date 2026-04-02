"""Application helpers for admin webhook lifecycle workflows."""

from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session

from src.domains.identity.models.user import User
from src.domains.platform.models.audit import AuditLog
from src.domains.platform.models.webhook import WebhookDelivery, WebhookSubscription


def build_admin_webhooks_response(
    *,
    db: Session,
    tenant_id,
) -> list[dict]:
    subscriptions = db.query(WebhookSubscription).filter(
        WebhookSubscription.tenant_id == tenant_id,
    ).order_by(desc(WebhookSubscription.created_at)).all()
    return [
        {
            "id": str(subscription.id),
            "event_type": subscription.event_type,
            "target_url": subscription.target_url,
            "is_active": subscription.is_active,
            "created_at": str(subscription.created_at),
        }
        for subscription in subscriptions
    ]


def create_admin_webhook(
    *,
    db: Session,
    tenant_id,
    actor_user_id,
    event_type: str,
    target_url: str,
    supported_webhook_events: set[str],
) -> dict:
    if event_type not in supported_webhook_events:
        raise HTTPException(status_code=400, detail="Unsupported event_type")
    if not target_url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="target_url must be an http/https URL")

    subscription = WebhookSubscription(
        tenant_id=tenant_id,
        event_type=event_type,
        target_url=target_url.strip(),
        created_by=actor_user_id,
        is_active=True,
    )
    db.add(subscription)
    if hasattr(db, "flush"):
        db.flush()
    db.add(
        AuditLog(
            tenant_id=tenant_id,
            user_id=actor_user_id,
            action="webhook.created",
            entity_type="webhook_subscription",
            entity_id=subscription.id,
            metadata_={
                "event_type": subscription.event_type,
                "target_url": subscription.target_url,
                "is_active": subscription.is_active,
            },
        )
    )
    db.commit()
    if hasattr(db, "refresh"):
        db.refresh(subscription)
    return {
        "success": True,
        "id": str(subscription.id),
        "event_type": subscription.event_type,
        "target_url": subscription.target_url,
        "secret": subscription.secret,
    }


def toggle_admin_webhook(
    *,
    db: Session,
    tenant_id,
    actor_user_id,
    webhook_id: str,
    is_active: bool,
    parse_uuid_fn,
) -> dict:
    webhook_uuid = parse_uuid_fn(webhook_id, "webhook_id")
    subscription = db.query(WebhookSubscription).filter(
        WebhookSubscription.id == webhook_uuid,
        WebhookSubscription.tenant_id == tenant_id,
    ).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Webhook not found")

    previous_state = subscription.is_active
    subscription.is_active = is_active
    db.add(
        AuditLog(
            tenant_id=tenant_id,
            user_id=actor_user_id,
            action="webhook.toggled",
            entity_type="webhook_subscription",
            entity_id=subscription.id,
            metadata_={
                "event_type": subscription.event_type,
                "old": previous_state,
                "new": subscription.is_active,
            },
        )
    )
    db.commit()
    return {"success": True, "is_active": subscription.is_active}


def delete_admin_webhook(
    *,
    db: Session,
    tenant_id,
    actor_user_id,
    webhook_id: str,
    parse_uuid_fn,
) -> dict:
    webhook_uuid = parse_uuid_fn(webhook_id, "webhook_id")
    subscription = db.query(WebhookSubscription).filter(
        WebhookSubscription.id == webhook_uuid,
        WebhookSubscription.tenant_id == tenant_id,
    ).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Webhook not found")

    db.add(
        AuditLog(
            tenant_id=tenant_id,
            user_id=actor_user_id,
            action="webhook.deleted",
            entity_type="webhook_subscription",
            entity_id=subscription.id,
            metadata_={
                "event_type": subscription.event_type,
                "target_url": subscription.target_url,
            },
        )
    )
    db.delete(subscription)
    db.commit()
    return {"success": True}


def build_admin_webhook_deliveries_response(
    *,
    db: Session,
    tenant_id,
    webhook_id: str,
    parse_uuid_fn,
) -> list[dict]:
    webhook_uuid = parse_uuid_fn(webhook_id, "webhook_id")
    subscription = db.query(WebhookSubscription).filter(
        WebhookSubscription.id == webhook_uuid,
        WebhookSubscription.tenant_id == tenant_id,
    ).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Webhook not found")

    deliveries = db.query(WebhookDelivery).filter(
        WebhookDelivery.tenant_id == tenant_id,
        WebhookDelivery.subscription_id == webhook_uuid,
    ).order_by(desc(WebhookDelivery.created_at)).limit(100).all()
    return [
        {
            "id": str(delivery.id),
            "event_type": delivery.event_type,
            "status": delivery.status,
            "status_code": delivery.status_code,
            "attempt_count": delivery.attempt_count,
            "last_attempt_at": str(delivery.last_attempt_at) if delivery.last_attempt_at else None,
            "created_at": str(delivery.created_at),
        }
        for delivery in deliveries
    ]
