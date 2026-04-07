"""WhatsApp Bridge — internal endpoint for the Node.js gateway microservice.

This route receives normalized, deduplicated WhatsApp messages from the
Node.js WhatsApp Gateway and feeds them into the existing Python processing
pipeline.  It is NOT exposed to the public internet — only the gateway
service calls it via an internal network (Docker bridge / Kubernetes service).

Security:
  · Validates the ``X-Internal-Gateway`` header.
  · No HMAC check (that already happened in the Node.js layer).
  · Rate-limiting is handled upstream by the Node gateway.
"""

import logging
from typing import Optional

try:
    from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
except ModuleNotFoundError:
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

    class Request:
        headers: dict

    class APIRouter:
        def __init__(self, *args, **kwargs):
            pass
        def post(self, *_args, **_kwargs):
            return lambda fn: fn

try:
    from pydantic import BaseModel, Field
except ModuleNotFoundError:
    class BaseModel:
        def __init__(self, **data):
            for k, v in data.items():
                setattr(self, k, v)
    def Field(default=None, **_kw):
        return default

try:
    from database import SessionLocal
except ModuleNotFoundError:
    SessionLocal = None

from src.domains.platform.services.whatsapp_gateway import (
    process_inbound_message,
    send_text_message,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/whatsapp/bridge", tags=["WhatsApp Bridge"])

INTERNAL_HEADER = "X-Internal-Gateway"
EXPECTED_HEADER_VALUE = "vidyaos-wa-gw"


class BridgeInboundPayload(BaseModel):
    phone: str
    text: str = ""
    wa_message_id: Optional[str] = None
    message_type: str = "text"
    media_id: Optional[str] = None
    media_filename: Optional[str] = None
    media_mime_type: Optional[str] = None
    timestamp: Optional[str] = None


@router.post("/inbound")
async def bridge_inbound(
    payload: BridgeInboundPayload,
    request: Request,
    background_tasks: BackgroundTasks,
):
    """Receive a normalized WhatsApp message from the Node.js gateway."""
    # Validate internal header
    gw_header = request.headers.get(INTERNAL_HEADER, "")
    if gw_header != EXPECTED_HEADER_VALUE:
        raise HTTPException(status_code=403, detail="Not authorized — internal gateway header missing")

    if not payload.phone:
        raise HTTPException(status_code=400, detail="phone is required")

    if not payload.text and not payload.media_id:
        raise HTTPException(status_code=400, detail="text or media_id is required")

    # Process in background (same pattern as the existing webhook handler)
    background_tasks.add_task(
        _bridge_process_and_respond,
        phone=payload.phone,
        text=payload.text,
        wa_message_id=payload.wa_message_id,
        message_type=payload.message_type,
        media_id=payload.media_id,
        media_filename=payload.media_filename,
        media_mime_type=payload.media_mime_type,
    )

    return {"status": "accepted", "phone": payload.phone}


async def _bridge_process_and_respond(
    phone: str,
    text: str,
    wa_message_id: str | None,
    message_type: str = "text",
    media_id: str | None = None,
    media_filename: str | None = None,
    media_mime_type: str | None = None,
):
    """Background worker: process the bridged message through the gateway."""
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
        # Dispatch response back via Meta Cloud API
        response_text = result.get("response_text", "")
        if response_text:
            await send_text_message(phone, response_text)
    except Exception:
        logger.exception("Bridge processing failed for %s", phone)
        await send_text_message(phone, "❌ An error occurred. Please try again later.")
    finally:
        if db is not None:
            db.close()
