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
from typing import Literal, Optional

try:
    from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request
except ModuleNotFoundError:  # Lightweight test environments
    class HTTPException(Exception):
        def __init__(self, status_code: int, detail: str):
            super().__init__(detail)
            self.status_code = status_code
            self.detail = detail

    class BackgroundTasks:
        def __init__(self):
            self.tasks = []

        def add_task(self, fn, *args, **kwargs):
            self.tasks.append((fn, args, kwargs))

    class Request:  # pragma: no cover - typing shim only
        headers: dict

    def Depends(_dependency):
        return None

    def Query(default=None, **_kwargs):
        return default

    class APIRouter:
        def __init__(self, *args, **kwargs):
            pass

        def get(self, *_args, **_kwargs):
            return lambda fn: fn

        def post(self, *_args, **_kwargs):
            return lambda fn: fn

        def delete(self, *_args, **_kwargs):
            return lambda fn: fn

try:
    from pydantic import BaseModel, Field
except ModuleNotFoundError:  # Lightweight test environments
    class BaseModel:
        def __init__(self, **data):
            for key, value in data.items():
                setattr(self, key, value)

        def model_dump(self, exclude_none: bool = False):
            data = self.__dict__.copy()
            if exclude_none:
                return {k: v for k, v in data.items() if v is not None}
            return data

    def Field(default=None, **_kwargs):
        return default

try:
    from starlette.responses import Response as StarletteResponse
except ModuleNotFoundError:  # Lightweight test environments
    class StarletteResponse:
        def __init__(self, content=None, media_type: str | None = None, headers: dict | None = None):
            self.body = content
            self.media_type = media_type
            self.headers = headers or {}

try:
    from sqlalchemy.orm import Session
except ModuleNotFoundError:  # Lightweight test environments
    Session = object

try:
    from auth.dependencies import get_current_user
except ModuleNotFoundError:  # Lightweight test environments
    async def get_current_user():
        raise HTTPException(status_code=503, detail="Authentication dependencies unavailable")

try:
    from database import SessionLocal, get_db
except ModuleNotFoundError:  # Lightweight test environments
    SessionLocal = None

    def get_db():
        yield None
try:
    from sqlalchemy import func as sqlfunc
except ModuleNotFoundError:  # Lightweight test environments
    class _SQLFuncShim:
        def __getattr__(self, _name):
            return lambda *args, **kwargs: None

    sqlfunc = _SQLFuncShim()

try:
    from src.domains.identity.models.user import User
except ModuleNotFoundError:  # Lightweight test environments
    class User:  # pragma: no cover - query shim for lightweight tests
        id = "id"
        role = "role"
        email = "email"
        tenant_id = "tenant_id"

try:
    from src.domains.identity.models.tenant import Tenant
except ModuleNotFoundError:  # Lightweight test environments
    class Tenant:  # pragma: no cover - query shim for lightweight tests
        id = "id"
        name = "name"

try:
    from src.domains.platform.models.whatsapp_models import PhoneUserLink, WhatsAppMessage
except ModuleNotFoundError:  # Lightweight test environments
    class PhoneUserLink:  # pragma: no cover - query shim for lightweight tests
        phone = "phone"
        user_id = "user_id"
        tenant_id = "tenant_id"
        verified = "verified"
        verified_at = "verified_at"

        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    class WhatsAppMessage:  # pragma: no cover - query shim for lightweight tests
        id = "id"
        phone = "phone"
        tenant_id = "tenant_id"
        created_at = "created_at"
        direction = "direction"
        intent = "intent"
        latency_ms = "latency_ms"

try:
    from src.domains.academic.services.report_card import generate_report_card_pdf
except ModuleNotFoundError:  # Lightweight test environments
    def generate_report_card_pdf(*_args, **_kwargs):  # pragma: no cover - runtime guard
        raise HTTPException(status_code=503, detail="Report card service unavailable")
from src.domains.platform.application.whatsapp_analytics import build_whatsapp_usage_snapshot
from src.domains.platform.services.whatsapp_gateway import (
    WHATSAPP_VERIFY_TOKEN,
    delete_session,
    generate_otp,
    get_whatsapp_metrics,
    get_session,
    log_message,
    consume_report_card_token,
    process_inbound_message,
    send_buttons,
    send_document_message,
    send_interactive_list,
    send_text_message,
    verify_otp as verify_otp_service,
    verify_webhook_signature,
)
from src.shared.ai_tools.whatsapp_tools import serialize_tool_catalog

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/whatsapp", tags=["WhatsApp"])
WHATSAPP_TEXT_CHUNK_LIMIT = 1500


def _require_admin(current_user) -> None:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")


def _build_whatsapp_usage_snapshot(current_user, db: Session, days: int) -> dict:
    return build_whatsapp_usage_snapshot(current_user, db, days)


# ─── Schemas ──────────────────────────────────────────────────

class ButtonPayload(BaseModel):
    id: str
    title: str = Field(..., min_length=1, max_length=20)


class ListRowPayload(BaseModel):
    id: str
    title: str = Field(..., min_length=1, max_length=24)
    description: Optional[str] = Field(default=None, max_length=72)


class SendMessageRequest(BaseModel):
    phone: str
    message: str
    message_type: Literal["text", "buttons", "list", "document"] = "text"
    buttons: list[ButtonPayload] = Field(default_factory=list)
    list_header: Optional[str] = Field(default=None, max_length=60)
    list_button_text: Optional[str] = Field(default=None, max_length=20)
    list_rows: list[ListRowPayload] = Field(default_factory=list)
    document_link: Optional[str] = Field(default=None, max_length=1000)
    document_filename: Optional[str] = Field(default=None, max_length=240)
    document_caption: Optional[str] = Field(default=None, max_length=1024)

    def __init__(self, **data):
        super().__init__(**data)
        if self.message_type == "buttons":
            if not self.buttons:
                raise ValueError("buttons are required when message_type='buttons'")
            if len(self.buttons) > 3:
                raise ValueError("WhatsApp supports at most 3 reply buttons")
        if self.message_type == "list":
            if not self.list_rows:
                raise ValueError("list_rows are required when message_type='list'")
            if not self.list_header:
                raise ValueError("list_header is required when message_type='list'")
            if not self.list_button_text:
                raise ValueError("list_button_text is required when message_type='list'")
            if len(self.list_rows) > 10:
                raise ValueError("WhatsApp supports at most 10 list rows per section")
        if self.message_type == "document":
            if not self.document_link:
                raise ValueError("document_link is required when message_type='document'")
            if not self.document_filename:
                raise ValueError("document_filename is required when message_type='document'")


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
        message_type = msg.get("message_type", "text")
        media_id = msg.get("media_id")
        media_filename = msg.get("media_filename")
        media_mime_type = msg.get("media_mime_type")

        if not phone or (not text and not media_id):
            continue

        # Open a fresh DB session inside the background worker instead of
        # reusing a request-scoped dependency that may be closed post-response.
        background_tasks.add_task(
            _process_and_respond,
            phone=phone,
            text=text,
            wa_message_id=wa_message_id,
            message_type=message_type,
            media_id=media_id,
            media_filename=media_filename,
            media_mime_type=media_mime_type,
        )

    return {"status": "ok"}


async def _process_and_respond(
    phone: str,
    text: str,
    wa_message_id: str | None,
    message_type: str = "text",
    media_id: str | None = None,
    media_filename: str | None = None,
    media_mime_type: str | None = None,
):
    """Background task: process message through the gateway and send response."""
    db = SessionLocal() if SessionLocal else None
    try:
        result = await process_inbound_message(
            db,
            phone,
            text,
            wa_message_id,
            message_type=message_type,
            media_id=media_id,
            media_filename=media_filename,
            media_mime_type=media_mime_type,
        )
        await _dispatch_outbound_response(phone, result)
    except Exception:
        logger.exception("Error processing WhatsApp message from %s", phone)
        await send_text_message(phone, "❌ An error occurred. Please try again later.")
    finally:
        if db is not None:
            db.close()


async def _dispatch_outbound_response(phone: str, result: dict) -> None:
    """Deliver the right outbound message type for a processed gateway response."""
    response_type = result.get("response_type", "text")
    response_text = result.get("response_text")

    if not response_text and response_type == "none":
        return

    if response_type == "buttons":
        buttons = result.get("buttons") or []
        if buttons:
            send_result = await send_buttons(phone, response_text or "Choose an option", buttons)
            if send_result.get("success"):
                return
            logger.warning("Falling back to text for button response to %s", phone)

    if response_type == "list":
        rows = result.get("rows") or []
        header = result.get("header") or "VidyaOS"
        button_text = result.get("button_text") or "View options"
        if rows:
            send_result = await send_interactive_list(phone, header, response_text or "Choose an option", button_text, rows)
            if send_result.get("success"):
                return
            logger.warning("Falling back to text for list response to %s", phone)

    if response_type == "document":
        document_link = result.get("document_link")
        document_filename = result.get("document_filename") or "document.pdf"
        document_caption = result.get("document_caption") or response_text
        if document_link:
            send_result = await send_document_message(phone, document_link, document_filename, document_caption)
            if send_result.get("success"):
                return
            logger.warning("Falling back to text for document response to %s", phone)

    if response_text:
        for chunk in _chunk_whatsapp_text(response_text):
            await send_text_message(phone, chunk)


def _chunk_whatsapp_text(text: str, chunk_size: int = WHATSAPP_TEXT_CHUNK_LIMIT) -> list[str]:
    """Split long WhatsApp text into readable chunks without mid-word truncation."""
    normalized = str(text or "").strip()
    if not normalized:
        return []
    if len(normalized) <= chunk_size:
        return [normalized]

    chunks: list[str] = []
    remaining = normalized
    while len(remaining) > chunk_size:
        split_at = remaining.rfind("\n\n", 0, chunk_size + 1)
        if split_at < max(200, chunk_size // 3):
            split_at = remaining.rfind("\n", 0, chunk_size + 1)
        if split_at < max(200, chunk_size // 3):
            split_at = remaining.rfind(" ", 0, chunk_size + 1)
        if split_at <= 0:
            split_at = chunk_size
        chunk = remaining[:split_at].strip()
        if chunk:
            chunks.append(chunk)
        remaining = remaining[split_at:].strip()

    if remaining:
        chunks.append(remaining)
    return chunks



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
                        "message_type": "text",
                    })
                elif msg.get("type") == "interactive":
                    # Handle button/list replies
                    interactive = msg.get("interactive", {})
                    reply = interactive.get("button_reply", {}) or interactive.get("list_reply", {})
                    messages.append({
                        "phone": msg.get("from", ""),
                        "text": reply.get("id") or reply.get("title", ""),
                        "wa_message_id": msg.get("id"),
                        "message_type": "interactive",
                    })
                elif msg.get("type") in {"document", "image", "video", "audio"}:
                    media_type = msg.get("type")
                    media = msg.get(media_type, {})
                    messages.append({
                        "phone": msg.get("from", ""),
                        "text": media.get("caption", ""),
                        "wa_message_id": msg.get("id"),
                        "message_type": media_type,
                        "media_id": media.get("id"),
                        "media_filename": media.get("filename"),
                        "media_mime_type": media.get("mime_type"),
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


@router.get("/report-card/{token}")
async def whatsapp_report_card_download(
    token: str,
    db: Session = Depends(get_db),
):
    """Download a WhatsApp-shared report card PDF using a short-lived token."""
    payload = consume_report_card_token(token)
    if not payload:
        raise HTTPException(status_code=404, detail="Report card link is invalid or expired")

    tenant = db.query(Tenant).filter(Tenant.id == payload["tenant_id"]).first()
    school_name = tenant.name if tenant and hasattr(tenant, "name") else "VidyaOS School"

    try:
        pdf_bytes = _generate_report_card_pdf(
            db,
            student_id=payload["child_id"],
            tenant_id=payload["tenant_id"],
            school_name=school_name,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return StarletteResponse(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=report_card.pdf"},
    )





def _generate_report_card_pdf(db, student_id: str, tenant_id: str, school_name: str) -> bytes:
    return generate_report_card_pdf(db, student_id=student_id, tenant_id=tenant_id, school_name=school_name)


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

    if data.message_type == "buttons":
        result = await send_buttons(
            data.phone,
            data.message,
            [button.model_dump() for button in data.buttons],
        )
    elif data.message_type == "list":
        result = await send_interactive_list(
            data.phone,
            data.list_header or "VidyaOS",
            data.message,
            data.list_button_text or "View options",
            [row.model_dump(exclude_none=True) for row in data.list_rows],
        )
    elif data.message_type == "document":
        result = await send_document_message(
            data.phone,
            data.document_link or "",
            data.document_filename or "document.pdf",
            data.document_caption or data.message,
        )
    else:
        result = await send_text_message(data.phone, data.message)

    if result.get("success"):
        log_message(
            db,
            data.phone,
            "outbound",
            data.message,
            message_type=data.message_type,
            user_id=current_user.id,
            tenant_id=current_user.tenant_id,
        )
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
    phone_query = db.query(
        WhatsAppMessage.phone,
        sqlfunc.max(WhatsAppMessage.created_at).label("last_activity"),
        sqlfunc.count(WhatsAppMessage.id).label("message_count"),
    ).filter(
        WhatsAppMessage.tenant_id == current_user.tenant_id,
    )
    if phone:
        phone_query = phone_query.filter(WhatsAppMessage.phone == phone)

    phones = phone_query.group_by(WhatsAppMessage.phone).all()

    sessions = []
    for p in phones:
        session = get_session(db, p.phone)
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
    db: Session = Depends(get_db),
):
    """Force-logout a WhatsApp session (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    delete_session(db, phone)
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
    _require_admin(current_user)
    return _build_whatsapp_usage_snapshot(current_user, db, days)


@router.get("/release-gate-snapshot")
async def whatsapp_release_gate_snapshot(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = Query(7, ge=1, le=90),
):
    """Return a release-gate-friendly WhatsApp staging evidence snapshot."""
    _require_admin(current_user)

    analytics = _build_whatsapp_usage_snapshot(current_user, db, days)
    tenant_id = getattr(current_user, "tenant_id", None)
    metrics = get_whatsapp_metrics(str(tenant_id) if tenant_id else None)

    routing_total = metrics.get("routing_success_total", 0) + metrics.get("routing_failure_total", 0)
    outbound_total = metrics.get("outbound_success_total", 0) + metrics.get("outbound_failure_total", 0)
    inbound_total = metrics.get("inbound_total", 0)

    def _pct(numerator: int, denominator: int) -> float:
        if denominator <= 0:
            return 0.0
        return round((numerator / denominator) * 100, 2)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "period_days": days,
        "analytics": analytics,
        "release_gate_metrics": metrics,
        "derived_rates": {
            "routing_failure_pct": _pct(metrics.get("routing_failure_total", 0), routing_total),
            "duplicate_inbound_pct": _pct(metrics.get("duplicate_inbound_total", 0), inbound_total),
            "visible_failure_pct": _pct(metrics.get("visible_failure_total", 0), inbound_total),
            "outbound_retryable_failure_pct": _pct(metrics.get("outbound_retryable_failure_total", 0), outbound_total),
        },
    }


@router.get("/tools/catalog")
async def whatsapp_tool_catalog(
    current_user=Depends(get_current_user),
    role: Optional[str] = Query(None),
):
    """Return the WhatsApp tool catalog metadata for planning/debug/admin use."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    if role is not None and role not in {"student", "teacher", "parent", "admin"}:
        raise HTTPException(status_code=400, detail="Invalid role filter")

    return {"tools": serialize_tool_catalog(role)}
