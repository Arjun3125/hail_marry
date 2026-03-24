"""Billing API routes — Razorpay order creation, payment verification, webhooks, subscription status."""
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth.dependencies import require_role
from database import get_db
from src.domains.administrative.services.billing import (
    capture_payment,
    create_order,
    get_payment_history,
    get_subscription,
    handle_webhook_event,
    verify_webhook_signature,
)

router = APIRouter(prefix="/api/billing", tags=["Billing"])


# ── Request / Response schemas ──

class CreateOrderRequest(BaseModel):
    amount: int                     # total amount in INR
    description: str = ""


class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


# ── Endpoints ──

@router.post("/create-order")
async def create_billing_order(
    body: CreateOrderRequest,
    user=Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Create a Razorpay payment order. Admin only."""
    if body.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    record = await create_order(db, user.tenant_id, body.amount, body.description)
    return {
        "order_id": record.razorpay_order_id,
        "amount": record.amount,
        "currency": record.currency,
        "status": record.status,
    }


@router.post("/verify-payment")
def verify_payment(
    body: VerifyPaymentRequest,
    user=Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Verify a completed Razorpay payment. Admin only."""
    try:
        record = capture_payment(
            db,
            body.razorpay_order_id,
            body.razorpay_payment_id,
            body.razorpay_signature,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"status": record.status, "payment_id": record.razorpay_payment_id}


@router.post("/webhook")
async def razorpay_webhook(request: Request, db: Session = Depends(get_db)):
    """Razorpay webhook receiver. No auth — verified via HMAC signature."""
    body = await request.body()
    signature = request.headers.get("X-Razorpay-Signature", "")
    if not verify_webhook_signature(body, signature):
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    import json

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    event_type = payload.get("event", "")
    result = handle_webhook_event(db, event_type, payload)
    return {"status": "ok", "message": result}


@router.get("/subscription")
def get_billing_subscription(
    user=Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Get current subscription status for the tenant."""
    sub = get_subscription(db, user.tenant_id)
    if not sub:
        return {"subscription": None, "message": "No active subscription"}
    return {"subscription": sub}


@router.get("/history")
def get_billing_history(
    user=Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Get payment history for the tenant."""
    history = get_payment_history(db, user.tenant_id)
    return {"payments": history, "count": len(history)}
