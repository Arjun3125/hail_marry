"""Razorpay billing service — order creation, signature verification, webhook handling."""
import hashlib
import hmac
import os
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from constants import BILLING_CURRENCY, BILLING_PLANS
from src.domains.administrative.models.billing import BillingPlan, PaymentRecord, TenantSubscription


# ── Razorpay credentials (from env) ──
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")
RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET", "")


def _razorpay_headers() -> dict:
    """Return auth headers for Razorpay API calls."""
    import base64

    credentials = base64.b64encode(f"{RAZORPAY_KEY_ID}:{RAZORPAY_KEY_SECRET}".encode()).decode()
    return {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json",
    }


def seed_billing_plans(db: Session) -> list[BillingPlan]:
    """Ensure default billing plans exist. Idempotent."""
    created = []
    for key, info in BILLING_PLANS.items():
        existing = db.query(BillingPlan).filter(BillingPlan.name == key).first()
        if not existing:
            plan = BillingPlan(
                name=key,
                label=info["label"],
                price_per_student_yearly=info["price_per_student_yearly"],
                features=info.get("features"),
            )
            db.add(plan)
            created.append(plan)
    if created:
        db.commit()
        for p in created:
            db.refresh(p)
    return created


def create_order(db: Session, tenant_id: UUID, amount: int, description: str = "") -> PaymentRecord:
    """Create a Razorpay order and persist a PaymentRecord.

    In production, this would call Razorpay's /v1/orders API.
    For now, it creates a local record with a placeholder order ID.
    """
    import uuid as _uuid

    # In production, call: POST https://api.razorpay.com/v1/orders
    # body = {"amount": amount * 100, "currency": BILLING_CURRENCY, "receipt": str(tenant_id)}
    # For MVP, generate a local reference:
    order_id = f"order_{_uuid.uuid4().hex[:16]}"

    record = PaymentRecord(
        tenant_id=tenant_id,
        amount=amount,
        currency=BILLING_CURRENCY,
        razorpay_order_id=order_id,
        description=description,
        status="created",
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def verify_payment_signature(
    razorpay_order_id: str,
    razorpay_payment_id: str,
    razorpay_signature: str,
) -> bool:
    """Verify Razorpay payment signature using HMAC-SHA256."""
    if not RAZORPAY_KEY_SECRET:
        # In test/demo mode, accept any signature
        return True

    message = f"{razorpay_order_id}|{razorpay_payment_id}".encode()
    expected = hmac.new(
        RAZORPAY_KEY_SECRET.encode(),
        message,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, razorpay_signature)


def capture_payment(
    db: Session,
    razorpay_order_id: str,
    razorpay_payment_id: str,
    razorpay_signature: str,
) -> PaymentRecord:
    """Verify signature and mark payment as captured."""
    record = db.query(PaymentRecord).filter(
        PaymentRecord.razorpay_order_id == razorpay_order_id
    ).first()
    if not record:
        raise ValueError(f"Order {razorpay_order_id} not found")

    if not verify_payment_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature):
        record.status = "failed"
        db.commit()
        raise ValueError("Invalid payment signature")

    record.razorpay_payment_id = razorpay_payment_id
    record.razorpay_signature = razorpay_signature
    record.status = "captured"
    db.commit()
    db.refresh(record)
    return record


def handle_webhook_event(db: Session, event_type: str, payload: dict) -> str:
    """Process Razorpay webhook events.

    Returns a status message for the webhook response.
    """
    if event_type == "payment.captured":
        entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
        order_id = entity.get("order_id")
        payment_id = entity.get("id")
        if order_id and payment_id:
            record = db.query(PaymentRecord).filter(
                PaymentRecord.razorpay_order_id == order_id
            ).first()
            if record and record.status != "captured":
                record.razorpay_payment_id = payment_id
                record.status = "captured"
                db.commit()
        return "payment.captured processed"

    if event_type == "subscription.charged":
        entity = payload.get("payload", {}).get("subscription", {}).get("entity", {})
        sub_id = entity.get("id")
        if sub_id:
            sub = db.query(TenantSubscription).filter(
                TenantSubscription.razorpay_subscription_id == sub_id
            ).first()
            if sub:
                sub.status = "active"
                db.commit()
        return "subscription.charged processed"

    return f"event {event_type} ignored"


def verify_webhook_signature(body: bytes, signature: str) -> bool:
    """Verify Razorpay webhook signature."""
    if not RAZORPAY_WEBHOOK_SECRET:
        return True
    expected = hmac.new(
        RAZORPAY_WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def get_subscription(db: Session, tenant_id: UUID) -> Optional[dict]:
    """Get current subscription details for a tenant."""
    sub = (
        db.query(TenantSubscription)
        .filter(TenantSubscription.tenant_id == tenant_id, TenantSubscription.status.in_(["active", "trialing"]))
        .first()
    )
    if not sub:
        return None

    plan = db.query(BillingPlan).filter(BillingPlan.id == sub.plan_id).first()
    return {
        "subscription_id": str(sub.id),
        "plan_name": plan.name if plan else "unknown",
        "plan_label": plan.label if plan else "Unknown",
        "status": sub.status,
        "student_count": sub.student_count,
        "current_period_start": sub.current_period_start.isoformat() if sub.current_period_start else None,
        "current_period_end": sub.current_period_end.isoformat() if sub.current_period_end else None,
    }


def get_payment_history(db: Session, tenant_id: UUID, limit: int = 20) -> list[dict]:
    """Return recent payment records for a tenant."""
    records = (
        db.query(PaymentRecord)
        .filter(PaymentRecord.tenant_id == tenant_id)
        .order_by(PaymentRecord.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": str(r.id),
            "amount": r.amount,
            "currency": r.currency,
            "status": r.status,
            "description": r.description,
            "razorpay_order_id": r.razorpay_order_id,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in records
    ]
