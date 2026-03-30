"""Legacy WhatsApp router kept for `/api/whatsapp` compatibility on Meta Cloud API."""
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from config import settings
from database import SessionLocal
from src.domains.identity.models.tenant import Tenant
from src.domains.identity.models.user import User
from src.domains.platform.services.whatsapp_gateway import send_text_message

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/whatsapp", tags=["WhatsApp"])


def get_or_create_whatsapp_user(phone: str, db: Session) -> User:
    """Get an existing linked user or auto-create a WhatsApp-first student shell."""
    user = db.query(User).filter(User.phone_number == phone, User.whatsapp_linked == True).first()
    if user:
        return user

    tenant = db.query(Tenant).first()
    if not tenant:
        raise HTTPException(status_code=500, detail="System not initialized with a tenant.")

    temp_email = f"wa_{phone.replace('+', '')}@vidyaos.whatsapp.local"
    user = User(
        tenant_id=tenant.id,
        email=temp_email,
        full_name="WhatsApp Student",
        role="student",
        phone_number=phone,
        whatsapp_linked=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _extract_inbound_messages(payload: dict) -> list[dict]:
    """Flatten Meta webhook payloads into the minimal message shape used here."""
    extracted: list[dict] = []
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            contacts = value.get("contacts", [])
            fallback_phone = contacts[0].get("wa_id", "") if contacts else ""
            for msg in value.get("messages", []):
                msg_type = msg.get("type", "")
                phone = msg.get("from", "") or fallback_phone
                body = ""
                media_id = None

                if msg_type == "text":
                    body = msg.get("text", {}).get("body", "").strip()
                elif msg_type == "interactive":
                    interactive = msg.get("interactive", {})
                    reply = interactive.get("button_reply", {}) or interactive.get("list_reply", {})
                    body = (reply.get("id") or reply.get("title") or "").strip()
                elif msg_type in {"document", "image", "audio", "video", "sticker"}:
                    media_id = msg.get(msg_type, {}).get("id")
                    caption = msg.get(msg_type, {}).get("caption")
                    body = (caption or "").strip()

                if not phone or (not body and not media_id):
                    continue

                extracted.append(
                    {
                        "phone": phone,
                        "body": body,
                        "media_id": media_id,
                    }
                )
    return extracted


async def process_whatsapp_message(phone: str, body: str, media_id: Optional[str]) -> None:
    """Process an inbound message and send the Meta Cloud API response."""
    from src.interfaces.rest_api.whatsapp.agent import handle_whatsapp_intent

    db = SessionLocal()
    try:
        user = get_or_create_whatsapp_user(phone, db)
        response_text = await handle_whatsapp_intent(user, body, media_id, db)
        send_result = await send_text_message(phone, response_text)
        if not send_result.get("success"):
            logger.warning("WhatsApp reply send failed for %s: %s", phone, send_result.get("error"))
    except Exception:
        logger.exception("WhatsApp processing error for %s", phone)
    finally:
        db.close()


@router.get("/webhook")
async def whatsapp_webhook_verify(
    hub_mode: Optional[str] = Query(None, alias="hub.mode"),
    hub_verify_token: Optional[str] = Query(None, alias="hub.verify_token"),
    hub_challenge: Optional[str] = Query(None, alias="hub.challenge"),
):
    """Meta webhook verification handshake for the legacy `/api/whatsapp` route."""
    if hub_mode == "subscribe" and hub_verify_token == settings.whatsapp.verify_token:
        return PlainTextResponse(hub_challenge or "")
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/webhook")
async def whatsapp_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
):
    """Legacy inbound webhook endpoint updated to Meta Cloud API payloads."""
    try:
        payload = await request.json()
        for message in _extract_inbound_messages(payload):
            background_tasks.add_task(
                process_whatsapp_message,
                message["phone"],
                message["body"],
                message["media_id"],
            )
        return PlainTextResponse("OK")
    except Exception:
        logger.exception("Legacy WhatsApp webhook failed")
        return PlainTextResponse("OK", status_code=200)
