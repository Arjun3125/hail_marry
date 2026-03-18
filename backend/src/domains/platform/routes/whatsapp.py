"""WhatsApp webhook and management routes.

Endpoints:
- GET  /whatsapp/webhook — Meta verification handshake
- POST /whatsapp/webhook — Inbound message handler
- POST /whatsapp/send    — Admin manual send
- POST /whatsapp/link    — Initiate phone linking
- POST /whatsapp/verify  — Complete OTP verification
- GET  /whatsapp/sessions — Admin session list
- DELETE /whatsapp/sessions/{session_id} — Force logout
- GET  /whatsapp/analytics — Usage metrics
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func as sqlfunc

from database import get_db
from auth.dependencies import get_current_user
from src.domains.platform.models.whatsapp_models import PhoneUserLink, WhatsAppSession, WhatsAppMessage
from src.domains.platform.services.whatsapp_gateway import (
    WHATSAPP_VERIFY_TOKEN,
    verify_webhook_signature,
    process_inbound_message,
    send_text_message,
    generate_otp,
    verify_otp as verify_otp_service,
    get_session,
    delete_session,
    resolve_phone_to_user,
    log_message,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])


# ─── Schemas ──────────────────────────────────────────────────

class SendMessageRequest(BaseModel):
    phone: str
    message: str
    message_type: str = "text"


class PhoneLinkRequest(BaseModel):
    phone: str
    email: str


class OTPVerifyRequest(BaseModel):
    phone: str
    otp: str


# ─── Webhook Endpoints ───────────────────────────────────────

@router.get("/webhook")
async def whatsapp_webhook_verify(
    request: Request,
    hub_mode: Optional[str] = Query(None, alias="hub.mode"),
    hub_verify_token: Optional[str] = Query(None, alias="hub.verify_token"),
    hub_challenge: Optional[str] = Query(None, alias="hub.challenge"),
):
    """Meta webhook verification handshake.

    Meta sends a GET request with hub.mode, hub.verify_token, and hub.challenge.
    We must respond with the challenge value if the verify_token matches.
    """
    if hub_mode == "subscribe" and hub_verify_token == WHATSAPP_VERIFY_TOKEN:
        logger.info("WhatsApp webhook verified successfully")
        return int(hub_challenge) if hub_challenge else ""
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/webhook")
async def whatsapp_webhook_inbound(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Process inbound WhatsApp messages from Meta Cloud API.

    Must respond with 200 OK within 5 seconds. Heavy processing is done
    in the background; response is sent back via outbound Meta API call.
    """
    body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")

    if not verify_webhook_signature(body, signature):
        raise HTTPException(status_code=403, detail="Invalid signature")

    payload = await request.json()

    # Extract messages from Meta's webhook format
    messages = _extract_messages(payload)

    for msg in messages:
        phone = msg.get("phone", "")
        text = msg.get("text", "")
        wa_message_id = msg.get("wa_message_id")

        if not phone or not text:
            continue

        # Process asynchronously to meet the 5-second requirement
        background_tasks.add_task(
            _process_and_respond,
            db=db,
            phone=phone,
            text=text,
            wa_message_id=wa_message_id,
        )

    return {"status": "ok"}


async def _process_and_respond(db: Session, phone: str, text: str, wa_message_id: str | None):
    """Background task: process message through the gateway and send response."""
    try:
        result = await process_inbound_message(db, phone, text, wa_message_id)
        response_text = result.get("response_text")
        if response_text:
            await send_text_message(phone, response_text)
    except Exception:
        logger.exception("Error processing WhatsApp message from %s", phone)
        await send_text_message(phone, "❌ An error occurred. Please try again later.")


def _extract_messages(payload: dict) -> list[dict]:
    """Extract message data from Meta's webhook payload format.

    Meta sends messages in:
    entry[].changes[].value.messages[]

    Each message has: from (phone), id, text.body, type, timestamp
    """
    messages = []
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            for msg in value.get("messages", []):
                if msg.get("type") == "text":
                    messages.append({
                        "phone": msg.get("from", ""),
                        "text": msg.get("text", {}).get("body", ""),
                        "wa_message_id": msg.get("id"),
                    })
                elif msg.get("type") == "interactive":
                    # Handle button/list replies
                    interactive = msg.get("interactive", {})
                    reply = interactive.get("button_reply", {}) or interactive.get("list_reply", {})
                    messages.append({
                        "phone": msg.get("from", ""),
                        "text": reply.get("title", reply.get("id", "")),
                        "wa_message_id": msg.get("id"),
                    })
    return messages


# ─── Phone Linking (OTP Auth) ────────────────────────────────

@router.post("/link")
async def initiate_phone_linking(
    data: PhoneLinkRequest,
    db: Session = Depends(get_db),
):
    """Initiate phone-to-ERP account linking by sending an OTP.

    Can be called from the web UI settings page or via WhatsApp.
    """
    from src.domains.identity.models.user import User
    user = db.query(User).filter(User.email == data.email.lower()).first()
    if not user:
        raise HTTPException(status_code=404, detail="No account found with that email")

    # Check if already linked
    existing = db.query(PhoneUserLink).filter(
        PhoneUserLink.phone == data.phone,
        PhoneUserLink.tenant_id == user.tenant_id,
        PhoneUserLink.verified == True,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="This phone is already linked to an account")

    otp = generate_otp(data.phone, data.email.lower())
    await send_text_message(data.phone, f"🔐 Your VidyaOS verification code is: *{otp}*\nExpires in 5 minutes.")

    return {"message": "OTP sent to WhatsApp", "phone": data.phone}


@router.post("/verify")
async def complete_phone_verification(
    data: OTPVerifyRequest,
    db: Session = Depends(get_db),
):
    """Complete phone linking by verifying the OTP."""
    result = verify_otp_service(data.phone, data.otp)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])

    from src.domains.identity.models.user import User
    user = db.query(User).filter(User.email == result["email"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Create or update phone link
    existing = db.query(PhoneUserLink).filter(
        PhoneUserLink.phone == data.phone,
        PhoneUserLink.tenant_id == user.tenant_id,
    ).first()

    if existing:
        existing.user_id = user.id
        existing.verified = True
        existing.verified_at = datetime.now(timezone.utc)
    else:
        link = PhoneUserLink(
            phone=data.phone,
            user_id=user.id,
            tenant_id=user.tenant_id,
            verified=True,
            verified_at=datetime.now(timezone.utc),
        )
        db.add(link)

    db.commit()
    return {"message": "Phone linked successfully", "role": user.role}


# ─── Admin: Manual Send ──────────────────────────────────────

@router.post("/send")
async def admin_send_message(
    data: SendMessageRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Admin endpoint to manually send a WhatsApp message."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    result = await send_text_message(data.phone, data.message)
    if result.get("success"):
        log_message(db, data.phone, "outbound", data.message, user_id=current_user.id,
                    tenant_id=current_user.tenant_id)
    return result


# ─── Admin: Session Management ───────────────────────────────

@router.get("/sessions")
async def list_sessions(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
    phone: Optional[str] = None,
):
    """List active WhatsApp sessions (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    query = db.query(WhatsAppMessage).filter(
        WhatsAppMessage.tenant_id == current_user.tenant_id,
    )
    if phone:
        query = query.filter(WhatsAppMessage.phone == phone)

    # Get unique phones with last activity
    phones = db.query(
        WhatsAppMessage.phone,
        sqlfunc.max(WhatsAppMessage.created_at).label("last_activity"),
        sqlfunc.count(WhatsAppMessage.id).label("message_count"),
    ).filter(
        WhatsAppMessage.tenant_id == current_user.tenant_id,
    ).group_by(WhatsAppMessage.phone).all()

    sessions = []
    for p in phones:
        session = get_session(p.phone)
        sessions.append({
            "phone": p.phone,
            "last_activity": p.last_activity.isoformat() if p.last_activity else None,
            "message_count": p.message_count,
            "session_active": session is not None,
            "role": session.get("role") if session else None,
        })

    return {"sessions": sessions}


@router.delete("/sessions/{phone}")
async def force_logout_session(
    phone: str,
    current_user=Depends(get_current_user),
):
    """Force-logout a WhatsApp session (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    delete_session(phone)
    await send_text_message(phone, "🔒 Your session has been ended by an administrator. Send any message to log in again.")
    return {"message": f"Session for {phone} terminated"}


# ─── Admin: Analytics ─────────────────────────────────────────

@router.get("/analytics")
async def whatsapp_analytics(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = Query(7, ge=1, le=90),
):
    """Get WhatsApp usage analytics (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    since = datetime.now(timezone.utc) - timedelta(days=days)

    base_query = db.query(WhatsAppMessage).filter(
        WhatsAppMessage.tenant_id == current_user.tenant_id,
        WhatsAppMessage.created_at >= since,
    )

    total_messages = base_query.count()
    inbound = base_query.filter(WhatsAppMessage.direction == "inbound").count()
    outbound = base_query.filter(WhatsAppMessage.direction == "outbound").count()

    unique_users = db.query(sqlfunc.count(sqlfunc.distinct(WhatsAppMessage.phone))).filter(
        WhatsAppMessage.tenant_id == current_user.tenant_id,
        WhatsAppMessage.created_at >= since,
    ).scalar()

    # Top intents
    top_intents = db.query(
        WhatsAppMessage.intent,
        sqlfunc.count(WhatsAppMessage.id).label("count"),
    ).filter(
        WhatsAppMessage.tenant_id == current_user.tenant_id,
        WhatsAppMessage.created_at >= since,
        WhatsAppMessage.intent.isnot(None),
    ).group_by(WhatsAppMessage.intent).order_by(
        sqlfunc.count(WhatsAppMessage.id).desc()
    ).limit(10).all()

    # Average latency
    avg_latency = db.query(sqlfunc.avg(WhatsAppMessage.latency_ms)).filter(
        WhatsAppMessage.tenant_id == current_user.tenant_id,
        WhatsAppMessage.created_at >= since,
        WhatsAppMessage.latency_ms.isnot(None),
    ).scalar()

    return {
        "period_days": days,
        "total_messages": total_messages,
        "inbound": inbound,
        "outbound": outbound,
        "unique_users": unique_users or 0,
        "avg_latency_ms": round(avg_latency) if avg_latency else None,
        "top_intents": [{"intent": i[0], "count": i[1]} for i in top_intents],
    }
