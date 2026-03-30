"""WhatsApp Gateway Service — central coordinator for inbound/outbound WhatsApp messaging.

Handles:
- HMAC-SHA256 webhook signature verification
- Phone → ERP user resolution (Redis cache + DB fallback)
- OTP generation/verification for phone linking
- Redis-backed conversation session management
- Message routing pipeline (auth → AI agent → response)
- Meta Cloud API outbound message sending
- Audit logging to whatsapp_messages
"""
import hashlib
import hmac
import json
import logging
import os
import re
import secrets
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional
from uuid import UUID, uuid4
from urllib.parse import urlparse

from types import SimpleNamespace

try:
    import httpx
except ModuleNotFoundError:  # Lightweight test environments
    class _HTTPStatusError(Exception):
        def __init__(self, *args, response=None, **kwargs):
            super().__init__(*args)
            self.response = response

    class _HTTPXStub:
        AsyncClient = None
        HTTPStatusError = _HTTPStatusError

    httpx = _HTTPXStub()

try:
    from sqlalchemy.orm import Session
except ModuleNotFoundError:  # Type-only fallback for test environments
    Session = object

from config import settings
from constants import STUDENT_ALLOWED_EXTENSIONS, STUDENT_MAX_FILE_SIZE
from src.infrastructure.llm.cache import _get_redis, invalidate_tenant_cache
from utils.upload_security import UploadValidationError, ensure_storage_dir, sanitize_docx_bytes

logger = logging.getLogger(__name__)

# ─── Configuration ────────────────────────────────────────────
WHATSAPP_API_URL = "https://graph.facebook.com/v18.0"
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
WHATSAPP_APP_SECRET = os.getenv("WHATSAPP_APP_SECRET", "")
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "vidyaos-wa-verify")

WA_SESSION_TTL_DAYS = int(os.getenv("WA_SESSION_TTL_DAYS", "30"))
WA_RATE_LIMIT_PER_MINUTE = int(os.getenv("WA_RATE_LIMIT_PER_MINUTE", "10"))
WA_OTP_TTL_SECONDS = int(os.getenv("WA_OTP_TTL_SECONDS", "300"))
WA_OTP_MAX_ATTEMPTS = int(os.getenv("WA_OTP_MAX_ATTEMPTS", "3"))
WA_REPORT_CARD_TTL_SECONDS = int(os.getenv("WA_REPORT_CARD_TTL_SECONDS", "3600"))

# System commands handled without AI
SYSTEM_COMMANDS = {
    "/help": "help",
    "help": "help",
    "/logout": "logout",
    "/relink": "relink",
    "relink": "relink",
    "/unlink": "relink",
    "/switch": "switch_child",
    "/status": "status",
    "/reportcard": "report_card",
    "/report-card": "report_card",
}
SIGNUP_COMMANDS = {"signup", "sign up", "register", "create account", "new account"}

# Tools that require async queue processing
HEAVY_TOOLS = {"generate_quiz", "generate_study_guide", "generate_audio_overview"}
WHATSAPP_UPLOAD_DIR = ensure_storage_dir("uploads", "whatsapp")
WHATSAPP_OCR_DIR = ensure_storage_dir("uploads", "whatsapp_ocr")
WHATSAPP_MEDIA_EXTENSIONS = {"mp3", "wav", "m4a", "ogg", "mp4", "mov", "webm"}
WHATSAPP_ALLOWED_EXTENSIONS = STUDENT_ALLOWED_EXTENSIONS | {"txt", "csv"} | WHATSAPP_MEDIA_EXTENSIONS
URL_PATTERN = r"https?://[^\s]+"
WA_RETRYABLE_STATUS_CODES = {408, 429, 500, 502, 503, 504}
TEXT_NOTE_PREFIXES = (
    "note:",
    "notes:",
    "study note:",
    "study notes:",
    "save note:",
    "upload note:",
)
TEXT_NOTE_FOLLOW_UP_PREFIXES = ("question:", "ask:", "prompt:", "query:")
WHATSAPP_METRICS_TTL_SECONDS = 60 * 60 * 24 * 30
WHATSAPP_METRIC_FIELDS = (
    "inbound_total",
    "duplicate_inbound_total",
    "rate_limited_total",
    "unlinked_inbound_total",
    "routing_success_total",
    "routing_failure_total",
    "upload_ingest_success_total",
    "upload_ingest_failure_total",
    "link_ingest_success_total",
    "link_ingest_failure_total",
    "outbound_success_total",
    "outbound_failure_total",
    "outbound_retryable_failure_total",
    "outbound_non_retryable_failure_total",
    "visible_failure_total",
)


def _whatsapp_metric_key(field: str, tenant_id: str | None = None) -> str:
    if tenant_id:
        return f"wa:metrics:tenant:{tenant_id}:{field}"
    return f"wa:metrics:global:{field}"


def _increment_whatsapp_metric(field: str, tenant_id: str | None = None) -> None:
    if field not in WHATSAPP_METRIC_FIELDS:
        return
    try:
        redis = _get_redis()
        if not redis:
            return
        key = _whatsapp_metric_key(field, tenant_id)
        pipe = redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, WHATSAPP_METRICS_TTL_SECONDS)
        pipe.execute()
    except Exception as exc:
        logger.debug("WhatsApp metric increment failed field=%s tenant=%s error=%s", field, tenant_id, exc)


def get_whatsapp_metrics(tenant_id: str | None = None) -> dict[str, int]:
    metrics: dict[str, int] = {}
    try:
        redis = _get_redis()
        if not redis:
            return {field: 0 for field in WHATSAPP_METRIC_FIELDS}
        for field in WHATSAPP_METRIC_FIELDS:
            raw_value = redis.get(_whatsapp_metric_key(field, tenant_id))
            metrics[field] = int(raw_value or 0)
    except Exception as exc:
        logger.debug("WhatsApp metrics read failed tenant=%s error=%s", tenant_id, exc)
        return {field: 0 for field in WHATSAPP_METRIC_FIELDS}
    return metrics


def _log_whatsapp_event(event: str, **fields) -> None:
    safe_fields = {key: value for key, value in fields.items() if value is not None}
    logger.info("whatsapp_event=%s %s", event, json.dumps(safe_fields, default=str, sort_keys=True))


# ─── Signature Verification ──────────────────────────────────

def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """Verify Meta webhook payload using HMAC-SHA256.

    Args:
        payload: Raw request body bytes.
        signature: Value of X-Hub-Signature-256 header.

    Returns:
        True if signature is valid.
    """
    if not WHATSAPP_APP_SECRET:
        logger.warning("WHATSAPP_APP_SECRET not configured — skipping signature verification")
        return True  # Allow in dev mode

    expected = "sha256=" + hmac.new(
        WHATSAPP_APP_SECRET.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


# ─── Phone → User Resolution ─────────────────────────────────

def resolve_phone_to_user(db: Session, phone: str):
    """Look up a verified phone link. Checks Redis cache first, falls back to DB.

    Args:
        db: SQLAlchemy session.
        phone: E.164 phone number (e.g. "919876543210").

    Returns:
        PhoneUserLink if found and verified, else None.
    """
    redis = _get_redis()
    cache_key = f"wa:phone:{phone}"

    # Redis cache hit
    if redis:
        cached = redis.get(cache_key)
        if cached:
            data = json.loads(cached)
            link = SimpleNamespace(
                id=UUID(data["id"]),
                phone=data["phone"],
                user_id=UUID(data["user_id"]),
                tenant_id=UUID(data["tenant_id"]),
                verified=True,
            )
            return link

    # Database lookup
    from src.domains.platform.models.whatsapp_models import PhoneUserLink
    link = db.query(PhoneUserLink).filter(
        PhoneUserLink.phone == phone,
        PhoneUserLink.verified == True,
    ).first()

    if link and redis:
        redis.setex(cache_key, 86400, json.dumps({
            "id": str(link.id),
            "phone": link.phone,
            "user_id": str(link.user_id),
            "tenant_id": str(link.tenant_id),
        }))

    return link


# ─── OTP Authentication ──────────────────────────────────────

def generate_otp(phone: str, email: str) -> str:
    """Generate a 6-digit OTP and store in Redis.

    Args:
        phone: WhatsApp phone number.
        email: ERP email address used for lookup.

    Returns:
        The generated OTP string.
    """
    otp = str(secrets.randbelow(900000) + 100000)
    redis = _get_redis()
    if redis:
        otp_data = json.dumps({"otp": otp, "email": email, "attempts": 0})
        redis.setex(f"wa:otp:{phone}", WA_OTP_TTL_SECONDS, otp_data)
    else:
        logger.error("Redis unavailable — cannot store OTP")
    return otp


def verify_otp(phone: str, submitted_otp: str) -> dict:
    """Verify a submitted OTP against the stored value.

    Args:
        phone: WhatsApp phone number.
        submitted_otp: OTP entered by the user.

    Returns:
        Dict with 'success', 'email', and optionally 'error'.
    """
    redis = _get_redis()
    if not redis:
        return {"success": False, "error": "Redis unavailable"}

    key = f"wa:otp:{phone}"
    raw = redis.get(key)
    if not raw:
        return {"success": False, "error": "OTP expired or not found"}

    data = json.loads(raw)
    attempts = data.get("attempts", 0)

    if attempts >= WA_OTP_MAX_ATTEMPTS:
        redis.delete(key)
        return {"success": False, "error": "Too many failed attempts. Please request a new OTP."}

    if data["otp"] != submitted_otp:
        data["attempts"] = attempts + 1
        redis.setex(key, WA_OTP_TTL_SECONDS, json.dumps(data))
        remaining = WA_OTP_MAX_ATTEMPTS - data["attempts"]
        return {"success": False, "error": f"Invalid OTP. {remaining} attempts remaining."}

    # Success — delete OTP
    redis.delete(key)
    return {"success": True, "email": data["email"]}


# ─── Session Management ──────────────────────────────────────

def get_session(db: Session, phone: str) -> Optional[dict]:
    """Load a WhatsApp session from Redis. Gracefully fall back to Postgres if Redis fails or misses."""
    # 1. Try Redis Hot Cache
    try:
        redis = _get_redis()
        if redis:
            raw = redis.get(f"wa:session:{phone}")
            if raw:
                return json.loads(raw)
    except Exception as e:
        logger.error("Redis unreachable for get_session: %s. Falling back to Postgres", e)
        
    # 2. Try Postgres DB Backup
    try:
        from src.domains.platform.models.whatsapp_models import WhatsAppSession
        db_session = db.query(WhatsAppSession).filter(WhatsAppSession.phone == phone).first()
        if db_session and db_session.expires_at > datetime.now(timezone.utc):
            return db_session.session_data
    except Exception as e:
        logger.error("Postgres get_session failed: %s", e)
    return None


def create_session(db: Session, phone: str, user_id: str, tenant_id: str, role: str) -> dict:
    """Create a new WhatsApp conversation session in Redis and Postgres."""
    session = {
        "session_id": f"ws-{uuid4().hex[:12]}",
        "phone": phone,
        "user_id": user_id,
        "tenant_id": tenant_id,
        "role": role,
        "active_child_id": None,
        "active_notebook_id": None,
        "pending_action": None,
        "conversation_history": [],
        "last_activity": datetime.now(timezone.utc).isoformat(),
    }
    save_session(db, phone, session)
    return session


def save_session(db: Session, phone: str, session: dict) -> None:
    """Persist session to Redis and Upsert to PostgreSQL."""
    session["last_activity"] = datetime.now(timezone.utc).isoformat()
    session_json = json.dumps(session)
    
    # Push to Redis
    try:
        redis = _get_redis()
        if redis:
            redis.setex(f"wa:session:{phone}", WA_SESSION_TTL_DAYS * 86400, session_json)
    except Exception as e:
        logger.warning("Redis unreachable for save_session: %s", e)
        
    # Push to Postgres
    try:
        from src.domains.platform.models.whatsapp_models import WhatsAppSession
        from uuid import UUID
        
        expires_at = datetime.now(timezone.utc) + timedelta(days=WA_SESSION_TTL_DAYS)
        
        db_session = db.query(WhatsAppSession).filter(WhatsAppSession.phone == phone).first()
        if db_session:
            db_session.session_data = session
            db_session.expires_at = expires_at
        else:
            if session.get("user_id") and session.get("tenant_id"):
                new_session = WhatsAppSession(
                    phone=phone,
                    user_id=UUID(session["user_id"]),
                    tenant_id=UUID(session["tenant_id"]),
                    role=session.get("role", "unknown"),
                    session_data=session,
                    expires_at=expires_at
                )
                db.add(new_session)
        db.commit()
    except Exception as e:
        logger.warning("Postgres unreachable for save_session: %s", e)
        db.rollback()


def delete_session(db: Session, phone: str) -> None:
    """Delete a WhatsApp session from Redis and Postgres."""
    try:
        redis = _get_redis()
        if redis:
            redis.delete(f"wa:session:{phone}")
    except Exception:
        pass
        
    try:
        from src.domains.platform.models.whatsapp_models import WhatsAppSession
        db.query(WhatsAppSession).filter(WhatsAppSession.phone == phone).delete()
        db.commit()
    except Exception:
        db.rollback()


def _clear_phone_link_cache(phone: str) -> None:
    try:
        redis = _get_redis()
        if redis:
            redis.delete(f"wa:phone:{phone}")
    except Exception:
        pass


def unlink_phone(db: Session, phone: str) -> None:
    """Remove both the active WhatsApp session and the verified phone link."""
    delete_session(db, phone)
    try:
        from src.domains.platform.models.whatsapp_models import PhoneUserLink

        db.query(PhoneUserLink).filter(PhoneUserLink.phone == phone).delete()
        db.commit()
    except Exception:
        db.rollback()
    _clear_phone_link_cache(phone)


def _looks_like_email(text: str) -> bool:
    candidate = (text or "").strip()
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", candidate))


def _derive_name_from_email(email: str) -> str:
    local = (email.split("@", 1)[0] if "@" in email else email).strip()
    cleaned = re.sub(r"[._-]+", " ", local).strip()
    return cleaned.title()[:255] or "WhatsApp Student"


def _upsert_phone_link(db: Session, *, phone: str, user_id: UUID, tenant_id: UUID) -> None:
    from src.domains.platform.models.whatsapp_models import PhoneUserLink

    existing = db.query(PhoneUserLink).filter(
        PhoneUserLink.phone == phone,
        PhoneUserLink.tenant_id == tenant_id,
    ).first()
    if existing:
        existing.user_id = user_id
        existing.verified = True
        existing.verified_at = datetime.now(timezone.utc)
        return

    db.add(PhoneUserLink(
        phone=phone,
        user_id=user_id,
        tenant_id=tenant_id,
        verified=True,
        verified_at=datetime.now(timezone.utc),
    ))


def _create_whatsapp_signup_user(db: Session, *, phone: str, email: str):
    from src.domains.identity.models.tenant import Tenant
    from src.domains.identity.models.user import User

    domain = email.split("@", 1)[1].lower()
    tenant = db.query(Tenant).filter(Tenant.domain == domain, Tenant.is_active == 1).first()
    if not tenant:
        return None, "I couldn't match that email domain to an active school. Try your school email address."

    existing_user = db.query(User).filter(User.email == email, User.tenant_id == tenant.id).first()
    if existing_user:
        return None, "An account with that email already exists. Send the same email again in login mode to link this phone."

    existing_phone_user = db.query(User).filter(User.phone_number == phone).first()
    if existing_phone_user:
        user = existing_phone_user
        user.email = user.email or email
        user.full_name = user.full_name or _derive_name_from_email(email)
        user.tenant_id = tenant.id
        user.role = user.role or "student"
        user.is_active = True
        user.phone_number = phone
        user.whatsapp_linked = True
    else:
        user = User(
            tenant_id=tenant.id,
            email=email,
            full_name=_derive_name_from_email(email),
            role="student",
            is_active=True,
            phone_number=phone,
            whatsapp_linked=True,
        )
        db.add(user)

    db.flush()
    _upsert_phone_link(db, phone=phone, user_id=user.id, tenant_id=tenant.id)
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    _clear_phone_link_cache(phone)
    return user, None


def _complete_authenticated_session(db: Session, *, phone: str, session: dict, user, is_signup: bool = False) -> dict:
    session["user_id"] = str(user.id)
    session["tenant_id"] = str(user.tenant_id)
    session["role"] = user.role
    session["pending_action"] = None
    session["active_child_id"] = None
    session["active_notebook_id"] = None
    save_session(db, phone, session)
    _clear_phone_link_cache(phone)

    action = "created and linked" if is_signup else "logged in"
    return {
        "response_text": (
            f"✅ *Verified!* You are now {action} as *{(user.full_name or 'User').strip()}* ({user.role}).\n\n"
            "Type *help* to see what I can do for you."
        ),
        "response_type": "text",
    }


# ─── Rate Limiting ────────────────────────────────────────────

def is_rate_limited(phone: str) -> bool:
    """Check if a phone number has exceeded the message rate limit.

    Uses a sliding-window counter in Redis. Fails open dynamically if Redis crashes.
    """
    try:
        redis = _get_redis()
        if not redis:
            return False

        key = f"wa:ratelimit:{phone}"
        count = redis.get(key)
        if count and int(count) >= WA_RATE_LIMIT_PER_MINUTE:
            return True

        pipe = redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, 60)
        pipe.execute()
        return False
    except Exception as e:
        logger.error("Redis unreachable for is_rate_limited: %s. Failing open.", e)
        return False


# ─── Message Deduplication ────────────────────────────────────

def is_duplicate_message(wa_message_id: str) -> bool:
    """Check if this Meta message ID has already been processed."""
    try:
        redis = _get_redis()
        if not redis or not wa_message_id:
            return False

        key = f"wa:dedup:{wa_message_id}"
        if redis.get(key):
            return True

        redis.setex(key, 3600, "1")  # 1-hour dedup window
        return False
    except Exception as e:
        logger.error("Redis unreachable for is_duplicate_message: %s. Failing open.", e)
        return False


# ─── Outbound Messaging ──────────────────────────────────────

def _classify_outbound_exception(exc: Exception) -> dict:
    """Classify outbound delivery failures for retry-aware handling."""
    if isinstance(exc, getattr(httpx, "HTTPStatusError", ())):
        response = getattr(exc, "response", None)
        status_code = getattr(response, "status_code", None)
        retryable = status_code in WA_RETRYABLE_STATUS_CODES if status_code is not None else False
        return {
            "success": False,
            "error": str(exc),
            "error_type": "http_retryable" if retryable else "http_non_retryable",
            "retryable": retryable,
            "status_code": status_code,
        }

    timeout_types = tuple(
        error_type
        for error_type in (
            getattr(httpx, "TimeoutException", None),
            getattr(httpx, "ConnectError", None),
        )
        if isinstance(error_type, type)
    )
    if timeout_types and isinstance(exc, timeout_types):
        return {
            "success": False,
            "error": str(exc),
            "error_type": "network_retryable",
            "retryable": True,
            "status_code": None,
        }

    return {
        "success": False,
        "error": str(exc),
        "error_type": "unknown_non_retryable",
        "retryable": False,
        "status_code": None,
    }


async def _send_whatsapp_payload(phone: str, payload: dict, *, transport: str) -> dict:
    if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_ID:
        logger.warning("WhatsApp credentials not configured. Message not sent.")
        _increment_whatsapp_metric("outbound_failure_total")
        _increment_whatsapp_metric("outbound_non_retryable_failure_total")
        _log_whatsapp_event("outbound_failure", phone=phone, transport=transport, error_type="configuration")
        return {
            "success": False,
            "error": "WhatsApp not configured",
            "error_type": "configuration",
            "retryable": False,
            "status_code": None,
        }

    url = f"{WHATSAPP_API_URL}/{WHATSAPP_PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            _increment_whatsapp_metric("outbound_success_total")
            _log_whatsapp_event("outbound_success", phone=phone, transport=transport)
            return {"success": True, "data": resp.json()}
    except Exception as exc:
        failure = _classify_outbound_exception(exc)
        _increment_whatsapp_metric("outbound_failure_total")
        _increment_whatsapp_metric(
            "outbound_retryable_failure_total" if failure.get("retryable") else "outbound_non_retryable_failure_total"
        )
        _log_whatsapp_event(
            "outbound_failure",
            phone=phone,
            transport=transport,
            error_type=failure.get("error_type"),
            retryable=failure.get("retryable"),
            status_code=failure.get("status_code"),
        )
        logger.error(
            "WhatsApp %s send failed phone=%s type=%s retryable=%s status=%s error=%s",
            transport,
            phone,
            failure.get("error_type"),
            failure.get("retryable"),
            failure.get("status_code"),
            failure.get("error"),
        )
        return failure


async def send_text_message(phone: str, text: str) -> dict:
    """Send a plain-text WhatsApp message via Meta Cloud API."""
    if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_ID:
        logger.warning("WhatsApp credentials not configured. Message not sent.")
        return {"success": False, "error": "WhatsApp not configured"}

    url = f"{WHATSAPP_API_URL}/{WHATSAPP_PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": {"body": text[:4096]},  # WhatsApp text limit
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            return {"success": True, "data": resp.json()}
    except httpx.HTTPStatusError as e:
        logger.error("WhatsApp API error: %s — %s", e.response.status_code, e.response.text)
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error("WhatsApp send failed: %s", str(e))
        return {"success": False, "error": str(e)}


async def send_interactive_list(phone: str, header: str, body: str, button_text: str, rows: list[dict]) -> dict:
    """Send an interactive list message for multi-option selection.

    Args:
        phone: Recipient phone.
        header: Header text.
        body: Body text.
        button_text: CTA button label.
        rows: List of dicts with 'id', 'title', and optional 'description'.
    """
    if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_ID:
        return {"success": False, "error": "WhatsApp not configured"}

    url = f"{WHATSAPP_API_URL}/{WHATSAPP_PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {"type": "text", "text": header},
            "body": {"text": body},
            "action": {
                "button": button_text,
                "sections": [{"title": "Options", "rows": rows[:10]}],
            },
        },
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            return {"success": True, "data": resp.json()}
    except Exception as e:
        logger.error("WhatsApp list send failed: %s", str(e))
        return {"success": False, "error": str(e)}


async def send_buttons(phone: str, body: str, buttons: list[dict]) -> dict:
    """Send a quick-reply button message.

    Args:
        phone: Recipient phone.
        body: Message body text.
        buttons: List of dicts with 'id' and 'title' (max 3).
    """
    if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_ID:
        return {"success": False, "error": "WhatsApp not configured"}

    url = f"{WHATSAPP_API_URL}/{WHATSAPP_PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }

    btn_list = [
        {"type": "reply", "reply": {"id": b["id"], "title": b["title"][:20]}}
        for b in buttons[:3]
    ]

    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body},
            "action": {"buttons": btn_list},
        },
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            return {"success": True, "data": resp.json()}
    except Exception as e:
        logger.error("WhatsApp buttons send failed: %s", str(e))
        return {"success": False, "error": str(e)}


async def send_document_message(phone: str, link: str, filename: str, caption: str | None = None) -> dict:
    """Send a WhatsApp document message via Meta Cloud API."""
    if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_ID:
        return {"success": False, "error": "WhatsApp not configured"}

    url = f"{WHATSAPP_API_URL}/{WHATSAPP_PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "document",
        "document": {
            "link": link,
            "filename": filename[:240],
        },
    }
    if caption:
        payload["document"]["caption"] = caption[:1024]

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            return {"success": True, "data": resp.json()}
    except Exception as e:
        logger.error("WhatsApp document send failed: %s", str(e))
        return {"success": False, "error": str(e)}


# ─── Message Logging ─────────────────────────────────────────

def log_message(
    db: Session,
    phone: str,
    direction: str,
    content: str,
    message_type: str = "text",
    user_id: Optional[UUID] = None,
    tenant_id: Optional[UUID] = None,
    wa_message_id: Optional[str] = None,
    intent: Optional[str] = None,
    tool_called: Optional[str] = None,
    latency_ms: Optional[int] = None,
) -> None:
    """Persist a message record to the whatsapp_messages audit table."""
    try:
        from src.domains.platform.models.whatsapp_models import WhatsAppMessage
        msg = WhatsAppMessage(
            phone=phone,
            direction=direction,
            content=content[:2000],  # Truncate very long messages
            message_type=message_type,
            user_id=user_id,
            tenant_id=tenant_id,
            wa_message_id=wa_message_id,
            intent=intent,
            tool_called=tool_called,
            latency_ms=latency_ms,
        )
        db.add(msg)
        db.commit()
    except Exception:
        logger.exception("Failed to log WhatsApp message")
        db.rollback()


async def _download_whatsapp_media(media_id: str) -> tuple[bytes, str]:
    token = settings.whatsapp.token or WHATSAPP_TOKEN
    if not token:
        raise ValueError("WHATSAPP_TOKEN is required to download inbound media.")

    api_url = (settings.whatsapp.api_url or WHATSAPP_API_URL).rstrip("/")
    headers = {"Authorization": f"Bearer {token}"}
    media_meta_url = f"{api_url}/{media_id}"

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        meta_response = await client.get(media_meta_url, headers=headers)
        meta_response.raise_for_status()
        media_url = meta_response.json().get("url")
        if not media_url:
            raise ValueError("WhatsApp media lookup did not return a download URL.")

        media_response = await client.get(media_url, headers=headers)
        media_response.raise_for_status()
        return media_response.content, media_response.headers.get("Content-Type", "")


def _infer_whatsapp_extension(
    *,
    filename: str | None,
    mime_type: str | None,
    message_type: str | None,
) -> str:
    candidate = Path(filename or "").suffix.lower().lstrip(".")
    if candidate:
        return candidate

    normalized = (mime_type or "").lower()
    if "pdf" in normalized:
        return "pdf"
    if "wordprocessingml.document" in normalized:
        return "docx"
    if "presentationml.presentation" in normalized:
        return "pptx"
    if "spreadsheetml.sheet" in normalized:
        return "xlsx"
    if "text/plain" in normalized:
        return "txt"
    if "text/csv" in normalized:
        return "csv"
    if "jpeg" in normalized or "jpg" in normalized:
        return "jpg"
    if "png" in normalized:
        return "png"
    if "audio/mpeg" in normalized:
        return "mp3"
    if "audio/wav" in normalized or "audio/x-wav" in normalized:
        return "wav"
    if "audio/ogg" in normalized:
        return "ogg"
    if "audio/mp4" in normalized or "audio/m4a" in normalized:
        return "m4a"
    if "video/mp4" in normalized:
        return "mp4"
    if "video/quicktime" in normalized:
        return "mov"
    if "video/webm" in normalized:
        return "webm"
    if message_type == "image":
        return "jpg"
    if message_type == "audio":
        return "mp3"
    if message_type == "video":
        return "mp4"
    return "bin"


def _build_inbound_media_log_text(
    *,
    message_type: str,
    text: str,
    media_filename: str | None,
) -> str:
    caption = (text or "").strip()
    if caption:
        return caption
    if media_filename:
        return media_filename
    return f"[{message_type} upload]"


def _parse_text_note_message(text: str) -> tuple[str | None, str | None]:
    normalized = (text or "").strip()
    lowered = normalized.lower()
    prefix = next((candidate for candidate in TEXT_NOTE_PREFIXES if lowered.startswith(candidate)), None)
    if not prefix:
        return None, None

    body = normalized[len(prefix):].strip()
    if not body:
        return "", None

    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", body) if part.strip()]
    follow_up = None
    if paragraphs:
        lowered_last = paragraphs[-1].lower()
        marker = next((item for item in TEXT_NOTE_FOLLOW_UP_PREFIXES if lowered_last.startswith(item)), None)
        if marker:
            follow_up = paragraphs[-1][len(marker):].strip() or None
            paragraphs = paragraphs[:-1]

    note_text = "\n\n".join(paragraphs).strip()
    return note_text, follow_up


def _format_upload_ingest_error(message_type: str, exc: Exception) -> str:
    detail = str(exc).strip()
    if message_type in {"video", "audio"}:
        if "ffmpeg" in detail.lower():
            return "Sorry, media transcription is not available because ffmpeg is missing on the server."
        if "transformers" in detail.lower():
            return "Sorry, media transcription is not available on this server yet."
        if "decode" in detail.lower() or "transcript" in detail.lower():
            return (
                "Sorry, I couldn't transcribe that media file. "
                "Please try a clearer audio/video file or share a YouTube link instead."
            )
        return (
            "Sorry, I couldn't ingest that media file. "
            "Try a smaller clip, convert it to notes/PDF, or share a YouTube link instead."
        )
    if "Unsupported WhatsApp upload type" in detail:
        return (
            "Sorry, that file type is not supported in WhatsApp yet. "
            "Send a PDF, image, DOCX, PPTX, XLSX, audio/video clip, or share a YouTube/web link instead."
        )
    if "25MB" in detail or "exceeds" in detail.lower():
        return "Sorry, that file is too large for WhatsApp ingestion. Please keep it under 25MB."
    return f"Sorry, I couldn't ingest that upload. {detail}"


def _format_link_ingest_error(exc: Exception) -> str:
    detail = str(exc).strip()
    if "private or unsupported destination" in detail.lower():
        return "Sorry, that link isn't supported. Send a public web page or YouTube link."
    if "not enough readable text" in detail.lower() or "no study content" in detail.lower():
        return "Sorry, I couldn't find enough readable study content at that link. Try another page or send notes directly."
    return f"Sorry, I couldn't ingest that link. {detail}"


def _build_whatsapp_media_queue_message(display_name: str, *, has_follow_up_prompt: bool) -> str:
    follow_up_text = (
        " I'll message you here once the transcript is ready so you can continue from the same upload."
        if has_follow_up_prompt
        else " I'll message you here once it is ready for questions."
    )
    return f"Received *{display_name}* and queued transcript extraction.{follow_up_text}"


def _extract_first_url(text: str) -> str | None:
    match = re.search(URL_PATTERN, text or "", flags=re.IGNORECASE)
    if not match:
        return None
    return match.group(0).rstrip(".,);]")


def _strip_url_from_text(text: str, url: str | None) -> str:
    if not text or not url:
        return (text or "").strip()
    return re.sub(re.escape(url), " ", text, count=1, flags=re.IGNORECASE).strip()


def _should_trigger_post_ingest_follow_up(text: str) -> bool:
    normalized = (text or "").strip().lower()
    if not normalized:
        return False
    if "?" in normalized:
        return True

    markers = (
        "explain",
        "summarize",
        "summary",
        "what is",
        "why",
        "how",
        "ask",
        "quiz",
        "flashcard",
        "mind map",
        "mindmap",
        "flowchart",
        "concept map",
        "study guide",
        "audio overview",
        "audio summary",
        "podcast",
        "teach me",
        "debate",
        "essay review",
        "review",
        "samjha",
        "samjhao",
        "bata",
        "batao",
        "kaise",
    )
    return any(marker in normalized for marker in markers)


def _build_whatsapp_notebook_name(source_name: str, *, prefix: str) -> str:
    stem = Path(source_name or "").stem.strip()
    cleaned = re.sub(r"\s+", " ", stem).strip(" -_")
    if not cleaned:
        cleaned = "study material"
    label = f"{prefix}: {cleaned}"
    return label[:255]


def _create_whatsapp_notebook(
    db: Session,
    *,
    tenant_id: str,
    user_id: str,
    name: str,
    description: str | None = None,
):
    from src.domains.platform.models.notebook import Notebook

    notebook = Notebook(
        tenant_id=UUID(str(tenant_id)),
        user_id=UUID(str(user_id)),
        name=name[:255],
        description=(description or "")[:1000] or None,
        subject="WhatsApp",
        color="#25D366",
        icon="MessageSquare",
    )
    db.add(notebook)
    db.commit()
    db.refresh(notebook)
    return notebook


async def _ingest_whatsapp_media_upload(
    db: Session,
    *,
    user_id: str,
    tenant_id: str,
    media_id: str,
    message_type: str,
    text: str = "",
    media_filename: str | None = None,
    media_mime_type: str | None = None,
    role: str | None = None,
    follow_up_user_id: str | None = None,
    conversation_history: list | None = None,
) -> dict:
    from src.domains.platform.models.document import Document
    from src.infrastructure.llm.providers import get_embedding_provider, get_vector_store_provider
    from src.infrastructure.vector_store.ingestion import ingest_document
    from src.domains.platform.schemas.ai_runtime import InternalWhatsAppMediaIngestRequest
    from src.domains.platform.services.ai_queue import JOB_TYPE_WHATSAPP_MEDIA_INGEST, enqueue_job

    content, downloaded_content_type = await _download_whatsapp_media(media_id)
    content_type = downloaded_content_type or (media_mime_type or "")
    extension = _infer_whatsapp_extension(
        filename=media_filename,
        mime_type=content_type,
        message_type=message_type,
    )

    if extension not in WHATSAPP_ALLOWED_EXTENSIONS:
        supported = ", ".join(sorted(WHATSAPP_ALLOWED_EXTENSIONS))
        raise ValueError(f"Unsupported WhatsApp upload type '{extension}'. Supported types: {supported}.")

    if len(content) > STUDENT_MAX_FILE_SIZE:
        raise ValueError("File exceeds 25MB limit.")

    display_name = Path(media_filename or f"whatsapp_upload.{extension}").name
    safe_prefix = f"{tenant_id}_{user_id}_{uuid4().hex}"
    file_path: Path
    final_type = extension
    macros_removed = False
    ocr_processed = False
    ocr_review_required = False
    ocr_warning = None
    ocr_languages: list[str] = []
    ocr_preprocessing: list[str] = []
    ocr_confidence: float | None = None

    is_media = message_type in {"video", "audio"} or extension in WHATSAPP_MEDIA_EXTENSIONS

    if extension == "docx":
        try:
            content, macros_removed = sanitize_docx_bytes(content)
        except UploadValidationError as exc:
            raise ValueError(str(exc)) from exc

    if extension in {"jpg", "jpeg", "png"}:
        from src.infrastructure.vector_store.ocr_service import image_bytes_to_pdf, validate_image_size

        try:
            validate_image_size(content)
        except ValueError as exc:
            raise ValueError(str(exc)) from exc

        pdf_name = f"{safe_prefix}_ocr.pdf"
        file_path = WHATSAPP_OCR_DIR / pdf_name
        try:
            ocr_result = image_bytes_to_pdf(
                content,
                str(file_path),
                suffix=f".{extension}",
                title=display_name,
                source_name=display_name,
            )
        except Exception as exc:
            raise ValueError(
                "OCR processing failed for this image upload. Please send a clearer, higher-contrast photo."
            ) from exc

        display_name = pdf_name
        final_type = "pdf"
        ocr_processed = True
        ocr_review_required = ocr_result.review_required
        ocr_warning = ocr_result.warning
        ocr_languages = ocr_result.languages
        ocr_preprocessing = ocr_result.preprocessing_applied
        ocr_confidence = getattr(ocr_result, "confidence", None)
    else:
        file_path = WHATSAPP_UPLOAD_DIR / f"{safe_prefix}_{display_name}"
        with open(file_path, "wb") as handle:
            handle.write(content)

    notebook = _create_whatsapp_notebook(
        db,
        tenant_id=str(tenant_id),
        user_id=str(user_id),
        name=_build_whatsapp_notebook_name(display_name, prefix="WhatsApp upload"),
        description=f"Ingested from WhatsApp {message_type} upload.",
    )

    document = Document(
        tenant_id=UUID(str(tenant_id)),
        uploaded_by=UUID(str(user_id)),
        notebook_id=notebook.id,
        file_name=display_name,
        file_type=final_type,
        storage_path=str(file_path),
        ingestion_status="processing",
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    try:
        if is_media:
            final_type = "audio" if message_type == "audio" else "video"
            document.file_type = final_type
            payload = InternalWhatsAppMediaIngestRequest(
                document_id=str(document.id),
                file_path=str(file_path),
                display_name=display_name,
                media_kind=final_type,
                follow_up_message=text.strip() if _should_trigger_post_ingest_follow_up(text) else None,
                follow_up_user_id=str(follow_up_user_id or user_id),
                role=role or "student",
                conversation_history=(conversation_history or [])[-10:],
                tenant_id=str(tenant_id),
            )
            job = enqueue_job(
                JOB_TYPE_WHATSAPP_MEDIA_INGEST,
                payload.model_dump(mode="json"),
                tenant_id=str(tenant_id),
                user_id=str(user_id),
                source="whatsapp",
            )
            db.commit()
            return {
                "response_text": _build_whatsapp_media_queue_message(
                    display_name,
                    has_follow_up_prompt=_should_trigger_post_ingest_follow_up(text),
                ),
                "response_type": "text",
                "intent": "media_upload",
                "tool_name": "ingest_whatsapp_media",
                "document_id": str(document.id),
                "notebook_id": str(document.notebook_id) if document.notebook_id else None,
                "job_id": job.get("job_id"),
                "status": "queued",
                "ingestion_mode": "async",
                "ocr_processed": ocr_processed,
                "ocr_review_required": ocr_review_required,
                "ocr_warning": ocr_warning,
                "ocr_languages": ocr_languages,
                "ocr_preprocessing": ocr_preprocessing,
                "ocr_confidence": ocr_confidence,
            }
        else:
            chunks = ingest_document(
                file_path=str(file_path),
                document_id=str(document.id),
                tenant_id=str(tenant_id),
                notebook_id=str(document.notebook_id) if document.notebook_id else None,
            )
        chunk_count = 0
        if chunks:
            texts = [chunk.text for chunk in chunks]
            embeddings = await get_embedding_provider().embed_batch(texts)
            store = get_vector_store_provider(str(tenant_id))
            store.add_chunks(
                [
                    {
                        "text": chunk.text,
                        "document_id": chunk.document_id,
                        "page_number": chunk.page_number,
                        "section_title": chunk.section_title or "",
                        "subject_id": chunk.subject_id or "",
                        "notebook_id": chunk.notebook_id or "",
                        "source_file": chunk.source_file or "",
                    }
                    for chunk in chunks
                ],
                embeddings,
            )
            chunk_count = len(chunks)

        invalidate_tenant_cache(str(tenant_id))

        document.ingestion_status = "completed"
        document.chunk_count = chunk_count
        db.commit()

        details = []
        if ocr_processed:
            details.append("OCR applied")
        if is_media:
            details.append("transcript extracted")
        if ocr_review_required:
            details.append("review recommended")
        if macros_removed:
            details.append("DOCX macros removed")
        details_text = f" ({', '.join(details)})" if details else ""
        warning_text = f" {ocr_warning}" if ocr_warning else ""
        return {
            "response_text": (
                f"Received *{display_name}* and added it to your knowledge base."
                f"{details_text}{warning_text} You can now ask questions about it in WhatsApp."
            ),
            "response_type": "text",
            "intent": "media_upload",
            "tool_name": "ingest_whatsapp_media",
            "document_id": str(document.id),
            "notebook_id": str(document.notebook_id) if document.notebook_id else None,
            "chunks": chunk_count,
            "ocr_processed": ocr_processed,
            "ocr_review_required": ocr_review_required,
            "ocr_warning": ocr_warning,
            "ocr_languages": ocr_languages,
            "ocr_preprocessing": ocr_preprocessing,
            "ocr_confidence": ocr_confidence,
        }
    except Exception:
        document.ingestion_status = "failed"
        db.commit()
        raise


async def _ingest_whatsapp_text_note(
    db: Session,
    *,
    user_id: str,
    tenant_id: str,
    note_text: str,
) -> dict:
    from src.domains.platform.models.document import Document
    from src.infrastructure.llm.providers import get_embedding_provider, get_vector_store_provider
    from src.infrastructure.vector_store.ingestion import ingest_document

    cleaned_note = (note_text or "").strip()
    if len(cleaned_note.split()) < 10:
        raise ValueError("Please send a longer study note so I can add useful context to your knowledge base.")

    note_name = f"whatsapp_note_{uuid4().hex[:8]}.txt"
    file_path = WHATSAPP_UPLOAD_DIR / note_name
    file_path.write_text(cleaned_note, encoding="utf-8")

    notebook = _create_whatsapp_notebook(
        db,
        tenant_id=str(tenant_id),
        user_id=str(user_id),
        name=_build_whatsapp_notebook_name("WhatsApp note", prefix="WhatsApp note"),
        description="Ingested from a WhatsApp text note.",
    )

    document = Document(
        tenant_id=UUID(str(tenant_id)),
        uploaded_by=UUID(str(user_id)),
        notebook_id=notebook.id,
        file_name=note_name,
        file_type="txt",
        storage_path=str(file_path),
        ingestion_status="processing",
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    try:
        chunks = ingest_document(
            file_path=str(file_path),
            document_id=str(document.id),
            tenant_id=str(tenant_id),
            notebook_id=str(document.notebook_id) if document.notebook_id else None,
        )
        texts = [chunk.text for chunk in chunks]
        embeddings = await get_embedding_provider().embed_batch(texts)
        store = get_vector_store_provider(str(tenant_id))
        store.add_chunks(
            [
                {
                    "text": chunk.text,
                    "document_id": chunk.document_id,
                    "page_number": chunk.page_number,
                    "section_title": chunk.section_title or "",
                    "subject_id": chunk.subject_id or "",
                    "notebook_id": chunk.notebook_id or "",
                    "source_file": chunk.source_file or "",
                }
                for chunk in chunks
            ],
            embeddings,
        )

        invalidate_tenant_cache(str(tenant_id))
        document.ingestion_status = "completed"
        document.chunk_count = len(chunks)
        db.commit()
        return {
            "response_text": "Saved your text note to the knowledge base. You can now ask questions about it in WhatsApp.",
            "response_type": "text",
            "intent": "text_note_upload",
            "tool_name": "ingest_whatsapp_text_note",
            "document_id": str(document.id),
            "notebook_id": str(document.notebook_id) if document.notebook_id else None,
            "chunks": len(chunks),
        }
    except Exception:
        document.ingestion_status = "failed"
        db.commit()
        raise


async def _ingest_whatsapp_url(
    db: Session,
    *,
    user_id: str,
    tenant_id: str,
    url: str,
    text: str = "",
) -> dict:
    from src.domains.platform.models.document import Document
    from src.infrastructure.llm.providers import get_embedding_provider, get_vector_store_provider
    from src.infrastructure.vector_store.ingestion import hierarchical_chunk, ingest_youtube
    from src.interfaces.rest_api.ai.discovery_workflows import is_safe_url, strip_html

    if not is_safe_url(url):
        raise ValueError("That link points to a private or unsupported destination.")

    parsed = urlparse(url)
    host = (parsed.netloc or "link").lower()
    title_hint = (text or "").strip() or host
    notebook = _create_whatsapp_notebook(
        db,
        tenant_id=str(tenant_id),
        user_id=str(user_id),
        name=_build_whatsapp_notebook_name(title_hint or host, prefix="WhatsApp link"),
        description=f"Ingested from WhatsApp link: {url}",
    )

    file_type = "youtube" if ("youtube.com" in host or "youtu.be" in host) else "html"
    display_name = f"{host[:120] or 'web-source'}"
    document = Document(
        tenant_id=UUID(str(tenant_id)),
        uploaded_by=UUID(str(user_id)),
        notebook_id=notebook.id,
        file_name=display_name,
        file_type=file_type,
        storage_path=url,
        ingestion_status="processing",
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    try:
        if file_type == "youtube":
            chunks = ingest_youtube(
                url=url,
                document_id=str(document.id),
                tenant_id=str(tenant_id),
                notebook_id=str(notebook.id),
            )
            source_label = "YouTube link"
        else:
            async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
                response = await client.get(
                    url,
                    headers={"User-Agent": "Mozilla/5.0 (educational content ingestion)"},
                )
                response.raise_for_status()
            page_text = strip_html(response.text)[:50000]
            if len(page_text) < 50:
                raise ValueError("Not enough readable text was found at that link.")
            chunks = hierarchical_chunk(
                pages=[{"text": page_text, "page_number": 1}],
                document_id=str(document.id),
                tenant_id=str(tenant_id),
                source_file=url,
                notebook_id=str(notebook.id),
            )
            source_label = "link"

        if not chunks:
            raise ValueError("No study content could be extracted from that link.")

        texts = [chunk.text for chunk in chunks]
        embeddings = await get_embedding_provider().embed_batch(texts)
        store = get_vector_store_provider(str(tenant_id))
        store.add_chunks(
            [
                {
                    "text": chunk.text,
                    "document_id": chunk.document_id,
                    "page_number": chunk.page_number,
                    "section_title": chunk.section_title or "",
                    "subject_id": chunk.subject_id or "",
                    "notebook_id": chunk.notebook_id or "",
                    "source_file": chunk.source_file or "",
                }
                for chunk in chunks
            ],
            embeddings,
        )

        invalidate_tenant_cache(str(tenant_id))

        document.ingestion_status = "completed"
        document.chunk_count = len(chunks)
        db.commit()
        return {
            "response_text": (
                f"Added this {source_label} to your knowledge base."
                " You can now ask questions about it in WhatsApp."
            ),
            "response_type": "text",
            "intent": "url_upload",
            "tool_name": "ingest_whatsapp_url",
            "document_id": str(document.id),
            "notebook_id": str(notebook.id),
            "chunks": len(chunks),
            "url": url,
        }
    except Exception:
        document.ingestion_status = "failed"
        db.commit()
        raise


async def _run_post_ingest_follow_up(
    *,
    message: str,
    user_id: str,
    tenant_id: str,
    role: str,
    notebook_id: str,
    conversation_history: list,
) -> dict:
    from src.interfaces.whatsapp_bot.agent import run_whatsapp_agent

    return await run_whatsapp_agent(
        message=message,
        user_id=user_id,
        tenant_id=tenant_id,
        role=role,
        notebook_id=notebook_id,
        conversation_history=conversation_history[-10:],
        session_id=None,
        pending_confirmation_id=None,
    )


# ─── System Command Handler ──────────────────────────────────

def handle_system_command(db: Session, command: str, session: dict) -> str:
    """Handle deterministic system commands (no AI needed).

    Returns:
        Response text.
    """
    cmd = SYSTEM_COMMANDS.get(command.lower().strip(), "")

    if cmd == "help":
        role = session.get("role", "student")
        lines = [
            "🤖 *VidyaOS WhatsApp Assistant*\n",
            "Just type naturally! Here are some things you can ask:\n",
        ]
        if role == "student":
            lines.extend([
                "📅 _What's my timetable today?_",
                "📝 _Do I have any tests today?_",
                "📋 _Pending assignments?_",
                "📊 _Show my attendance_",
                "📈 _Show my marks_",
                "💡 _Explain photosynthesis_",
            ])
        elif role == "teacher":
            lines.extend([
                "📅 _Show today's classes_",
                "❌ _Which students are absent?_",
                "📝 _Generate quiz for class 8 science_",
            ])
        elif role == "parent":
            lines.extend([
                "📊 _Show my child's performance_",
                "📅 _Attendance report for this week_",
                "📋 _Any homework today?_",
                "📄 _/reportcard_",
            ])
        elif role == "admin":
            lines.extend([
                "📊 _School attendance summary_",
                "💰 _Fee pending report_",
                "🤖 _AI usage stats_",
                "📚 _Any books on physics?_",
            ])
        lines.extend(["\n/logout — End this session", "/relink — Unlink and relink this phone", "/switch — Switch child (parents)"])
        return "\n".join(lines)

    elif cmd == "logout":
        delete_session(db, session["phone"])
        return "✅ Logged out. Send any message to start a fresh session."

    elif cmd == "relink":
        unlink_phone(db, session["phone"])
        return "✅ This phone has been unlinked. Send your registered email to link it again."

    elif cmd == "switch_child":
        if session.get("role") != "parent":
            return "⚠️ Child switching is only available for parent accounts."
        return "__SWITCH_CHILD__"  # Handled by the route layer

    elif cmd == "status":
        return (
            f"📱 *Session Info*\n"
            f"Role: {session.get('role', 'unknown')}\n"
            f"Session: {session.get('session_id', 'N/A')}\n"
            f"Last Activity: {session.get('last_activity', 'N/A')}"
        )

    elif cmd == "report_card":
        if session.get("role") != "parent":
            return "⚠️ Report card delivery is currently available for parent accounts."
        return "__REPORT_CARD__"

    return "Unknown command. Type *help* for options."


# ─── Async Job Notifications ───────────────────────────────────

def _coerce_uuid(value: str | None):
    if not value:
        return None
    try:
        return UUID(str(value))
    except (ValueError, TypeError, AttributeError):
        return value


def _describe_ai_job(job: dict) -> str:
    request = job.get("request") or {}
    topic = (
        request.get("topic")
        or request.get("query")
        or request.get("display_name")
        or request.get("subject_name")
        or "this request"
    ).strip()
    job_type = job.get("job_type", "AI task")
    labels = {
        "query": "study guide",
        "audio": "audio overview",
        "video": "video overview",
        "study_tool": "study tool",
        "teacher_assessment": "teacher assessment",
        "whatsapp_media_ingest": "media upload",
    }
    label = labels.get(job_type, job_type.replace("_", " "))
    return label, topic


def format_ai_job_status_message(job: dict) -> str:
    status = job.get("status")
    if status == "completed":
        result = job.get("result") or {}
        response_text = (result.get("response_text") or "").strip() if isinstance(result, dict) else ""
        if response_text:
            return response_text

    label, topic = _describe_ai_job(job)
    job_id = job.get("job_id", "unknown")

    if status == "completed":
        return (
            f"✅ Your {label} is ready for *{topic}*.\n"
            f"Job ID: `{job_id}`\n"
            "Reply with the same request if you want another version."
        )

    error = (job.get("error") or "Unknown error").strip()
    if job.get("job_type") == "whatsapp_media_ingest":
        return (
            f"⚠️ I couldn't finish indexing *{topic}*.\n"
            f"Job ID: `{job_id}`\n"
            f"Reason: {error[:200]}"
        )
    return (
        f"⚠️ Your {label} request for *{topic}* failed.\n"
        f"Job ID: `{job_id}`\n"
        f"Reason: {error[:200]}"
    )


async def send_ai_job_status_notification(job: dict) -> bool:
    """Best-effort WhatsApp notification when an async AI job finishes."""
    try:
        from database import SessionLocal
        from src.domains.platform.models.whatsapp_models import PhoneUserLink
    except ModuleNotFoundError:
        logger.warning("WhatsApp job notification dependencies unavailable")
        return False

    db = SessionLocal() if SessionLocal else None
    if db is None:
        return False

    try:
        user_id = _coerce_uuid(job.get("user_id"))
        tenant_id = _coerce_uuid(job.get("tenant_id"))
        if not user_id or not tenant_id:
            return False

        link = db.query(PhoneUserLink).filter(
            PhoneUserLink.user_id == user_id,
            PhoneUserLink.tenant_id == tenant_id,
            PhoneUserLink.verified == True,
        ).order_by(PhoneUserLink.verified_at.desc()).first()
        if not link:
            return False

        message = format_ai_job_status_message(job)
        result = await send_text_message(link.phone, message)
        if not result.get("success"):
            return False

        log_message(
            db,
            link.phone,
            "outbound",
            message,
            message_type="text",
            user_id=user_id if isinstance(user_id, UUID) else None,
            tenant_id=tenant_id if isinstance(tenant_id, UUID) else None,
            tool_called="ai_job_status",
        )
        return True
    except Exception:
        logger.exception("Failed to send WhatsApp AI job notification for job=%s", job.get("job_id"))
        return False
    finally:
        db.close()




def _get_parent_children(db: Session, session: dict) -> list[dict]:
    try:
        from models.parent_link import ParentLink
        from src.domains.identity.models.user import User

        parent_id = UUID(session["user_id"])
        tenant_id = UUID(session["tenant_id"])
        rows = db.query(ParentLink, User).join(
            User, ParentLink.child_id == User.id
        ).filter(
            ParentLink.tenant_id == tenant_id,
            ParentLink.parent_id == parent_id,
        ).all()
        return [
            {
                "child_id": str(link.child_id),
                "name": (child.full_name or "Child").strip(),
            }
            for link, child in rows
        ]
    except Exception:
        logger.exception("Failed to load parent children for WhatsApp session=%s", session.get("session_id"))
        return []


def _build_child_switch_response(db: Session, session: dict) -> dict:
    children = _get_parent_children(db, session)
    if not children:
        return {
            "response_text": "⚠️ No linked children were found for this parent account.",
            "response_type": "text",
        }

    if len(children) == 1:
        only_child = children[0]
        session["active_child_id"] = only_child["child_id"]
        save_session(db, session["phone"], session)
        return {
            "response_text": f"✅ Using *{only_child['name']}* for parent updates.",
            "response_type": "text",
        }

    active_child_id = session.get("active_child_id")
    rows = []
    for child in children[:10]:
        description = "Currently selected" if child["child_id"] == active_child_id else "Tap to switch"
        rows.append({
            "id": f"child:{child['child_id']}",
            "title": child["name"][:24],
            "description": description[:72],
        })

    return {
        "response_text": "👨‍👩‍👧 Select which child you want to use for WhatsApp updates.",
        "response_type": "list",
        "header": "Choose child",
        "button_text": "Select",
        "rows": rows,
    }


def _handle_child_switch_selection(db: Session, session: dict, text: str) -> dict | None:
    lowered = (text or "").strip().lower()
    if not lowered.startswith("child:"):
        return None

    selected_child_id = lowered.split(":", 1)[1].strip()
    children = _get_parent_children(db, session)
    selected = next((child for child in children if child["child_id"].lower() == selected_child_id), None)
    if not selected:
        return {
            "response_text": "⚠️ I couldn't find that child selection. Please use /switch again.",
            "response_type": "text",
        }

    session["active_child_id"] = selected["child_id"]
    session["active_notebook_id"] = None
    save_session(db, session["phone"], session)
    return {
        "response_text": f"✅ Switched to *{selected['name']}*. Ask me about attendance, homework, or performance.",
        "response_type": "text",
    }




def _create_report_card_token(session: dict, child_id: str) -> str | None:
    redis = _get_redis()
    if not redis:
        return None

    token = secrets.token_urlsafe(24)
    payload = {
        "tenant_id": session.get("tenant_id"),
        "child_id": child_id,
        "parent_id": session.get("user_id"),
    }
    redis.setex(f"wa:report_card:{token}", WA_REPORT_CARD_TTL_SECONDS, json.dumps(payload))
    return token


def consume_report_card_token(token: str) -> dict | None:
    redis = _get_redis()
    if not redis:
        return None
    raw = redis.get(f"wa:report_card:{token}")
    if not raw:
        return None
    return json.loads(raw)


def _build_report_card_response(db: Session, session: dict) -> dict:
    active_child_id = session.get("active_child_id")
    if not active_child_id:
        return _build_child_switch_response(db, session)

    token = _create_report_card_token(session, active_child_id)
    if not token:
        return {
            "response_text": "⚠️ I couldn't prepare the report card link right now. Please try again later.",
            "response_type": "text",
        }

    try:
        from src.domains.identity.models.user import User
        child = db.query(User).filter(User.id == UUID(active_child_id)).first()
        child_name = (child.full_name if child else "child").strip()
    except Exception:
        child_name = "child"

    safe_name = "_".join(child_name.lower().split()) or "report_card"
    base_url = settings.auth.saml_sp_base_url.rstrip("/")
    document_link = f"{base_url}/api/v1/whatsapp/report-card/{token}"
    return {
        "response_text": f"📄 *{child_name}*'s report card is ready.",
        "response_type": "document",
        "document_link": document_link,
        "document_filename": f"report_card_{safe_name}.pdf",
        "document_caption": f"📄 {child_name} — Report Card",
    }


# ─── Main Processing Pipeline ─────────────────────────────────

async def process_inbound_message(
    db: Session,
    phone: str,
    text: str,
    wa_message_id: Optional[str] = None,
    message_type: str = "text",
    media_id: Optional[str] = None,
    media_filename: Optional[str] = None,
    media_mime_type: Optional[str] = None,
) -> dict:
    """Main entry point: process an inbound WhatsApp message through the full pipeline.

    Returns:
        Dict with 'response_text', 'response_type', and metadata.
    """
    start_time = time.time()

    # 1. Deduplication
    if wa_message_id and is_duplicate_message(wa_message_id):
        _increment_whatsapp_metric("duplicate_inbound_total")
        _log_whatsapp_event(
            "inbound_duplicate",
            phone=phone,
            wa_message_id=wa_message_id,
            message_type=message_type,
        )
        return {"response_text": None, "response_type": "none", "duplicate": True}

    # 2. Rate limiting
    if is_rate_limited(phone):
        _increment_whatsapp_metric("rate_limited_total")
        _log_whatsapp_event("rate_limited", phone=phone, message_type=message_type)
        return {
            "response_text": "⚠️ Too many messages. Please wait a moment and try again.",
            "response_type": "text",
        }

    # 3. Resolve user
    link = resolve_phone_to_user(db, phone)

    if not link:
        # Unlinked phone — start auth flow
        _increment_whatsapp_metric("unlinked_inbound_total")
        _log_whatsapp_event("unlinked_inbound", phone=phone, message_type=message_type)
        return await _handle_unlinked_phone(db, phone, text)

    tenant_scope = str(link.tenant_id)
    _increment_whatsapp_metric("inbound_total", tenant_scope)
    _log_whatsapp_event(
        "inbound_received",
        phone=phone,
        tenant_id=tenant_scope,
        wa_message_id=wa_message_id,
        message_type=message_type,
    )

    # 4. Load or create session
    session = get_session(db, phone)
    if not session:
        from src.domains.identity.models.user import User
        user = db.query(User).filter(User.id == link.user_id).first()
        role = user.role if user else "student"
        session = create_session(db, phone, str(link.user_id), str(link.tenant_id), role)

    # 5. Check pending auth actions
    if session.get("pending_action") == "awaiting_otp":
        return await _handle_otp_verification(db, phone, text, session)

    if session.get("pending_action") == "awaiting_email":
        return await _handle_email_lookup(db, phone, text, session)

    # 6. Parent child selection shortcuts
    text_stripped = text.strip().lower()
    if session.get("role") == "parent":
        selection_result = _handle_child_switch_selection(db, session, text_stripped)
        if selection_result:
            elapsed = int((time.time() - start_time) * 1000)
            log_message(db, phone, "inbound", text, user_id=link.user_id, tenant_id=link.tenant_id,
                        wa_message_id=wa_message_id)
            log_message(db, phone, "outbound", selection_result.get("response_text", ""), user_id=link.user_id, tenant_id=link.tenant_id,
                        latency_ms=elapsed)
            return selection_result

    inbound_log_text = _build_inbound_media_log_text(
        message_type=message_type,
        text=text,
        media_filename=media_filename,
    )

    # 7. Media upload ingestion
    if media_id:
        try:
            media_result = await _ingest_whatsapp_media_upload(
                db,
                user_id=str(session.get("user_id") or link.user_id),
                tenant_id=str(link.tenant_id),
                media_id=media_id,
                message_type=message_type,
                text=text,
                media_filename=media_filename,
                media_mime_type=media_mime_type,
                role=session.get("role"),
                follow_up_user_id=str(session.get("active_child_id") or link.user_id),
                conversation_history=list(session.get("conversation_history", [])),
            )
        except Exception as exc:
            logger.exception("WhatsApp media ingestion failed for phone=%s", phone)
            media_result = {
                "response_text": _format_upload_ingest_error(message_type, exc),
                "response_type": "text",
                "intent": "media_upload_error",
                "tool_name": "ingest_whatsapp_media",
            }
        media_success = media_result.get("intent") != "media_upload_error"
        _increment_whatsapp_metric(
            "upload_ingest_success_total" if media_success else "upload_ingest_failure_total",
            tenant_scope,
        )
        if not media_success:
            _increment_whatsapp_metric("visible_failure_total", tenant_scope)
        _log_whatsapp_event(
            "media_ingest_result",
            phone=phone,
            tenant_id=tenant_scope,
            success=media_success,
            notebook_id=media_result.get("notebook_id"),
            tool_name=media_result.get("tool_name"),
        )

        elapsed = int((time.time() - start_time) * 1000)
        if media_result.get("notebook_id"):
            session["active_notebook_id"] = str(media_result["notebook_id"])
            if media_result.get("ingestion_mode") != "async" and _should_trigger_post_ingest_follow_up(text):
                try:
                    follow_up = await _run_post_ingest_follow_up(
                        message=text,
                        user_id=str(session.get("active_child_id") or link.user_id),
                        tenant_id=str(link.tenant_id),
                        role=session["role"],
                        notebook_id=str(media_result["notebook_id"]),
                        conversation_history=session.get("conversation_history", []),
                    )
                    follow_up_text = str(follow_up.get("response") or "").strip()
                    if follow_up_text:
                        media_result["response_text"] = (
                            f"{media_result.get('response_text', '').strip()}\n\n"
                            f"{follow_up_text}"
                        ).strip()
                        media_result["intent"] = follow_up.get("intent") or media_result.get("intent")
                        media_result["tool_name"] = follow_up.get("tool_name") or media_result.get("tool_name")
                except Exception:
                    logger.exception("WhatsApp post-upload follow-up failed for phone=%s", phone)
        history = session.get("conversation_history", [])
        history.append({"role": "user", "content": inbound_log_text})
        history.append({"role": "assistant", "content": media_result.get("response_text", "")})
        session["conversation_history"] = history[-20:]
        save_session(db, phone, session)
        log_message(
            db,
            phone,
            "inbound",
            inbound_log_text,
            user_id=link.user_id,
            tenant_id=link.tenant_id,
            wa_message_id=wa_message_id,
            intent=media_result.get("intent"),
            message_type=message_type,
        )
        log_message(
            db,
            phone,
            "outbound",
            media_result.get("response_text", ""),
            user_id=link.user_id,
            tenant_id=link.tenant_id,
            tool_called=media_result.get("tool_name"),
            latency_ms=elapsed,
        )
        media_result["latency_ms"] = elapsed
        return media_result

    note_text, note_follow_up = _parse_text_note_message(text)
    if note_text is not None:
        try:
            note_result = await _ingest_whatsapp_text_note(
                db,
                user_id=str(session.get("user_id") or link.user_id),
                tenant_id=str(link.tenant_id),
                note_text=note_text,
            )
        except Exception as exc:
            logger.exception("WhatsApp text note ingestion failed for phone=%s", phone)
            note_result = {
                "response_text": f"Sorry, I couldn't save that note. {str(exc).strip()}",
                "response_type": "text",
                "intent": "text_note_upload_error",
                "tool_name": "ingest_whatsapp_text_note",
            }

        elapsed = int((time.time() - start_time) * 1000)
        if note_result.get("notebook_id"):
            session["active_notebook_id"] = str(note_result["notebook_id"])
            if _should_trigger_post_ingest_follow_up(note_follow_up or ""):
                try:
                    follow_up = await _run_post_ingest_follow_up(
                        message=note_follow_up,
                        user_id=str(session.get("active_child_id") or link.user_id),
                        tenant_id=str(link.tenant_id),
                        role=session["role"],
                        notebook_id=str(note_result["notebook_id"]),
                        conversation_history=session.get("conversation_history", []),
                    )
                    follow_up_text = str(follow_up.get("response") or "").strip()
                    if follow_up_text:
                        note_result["response_text"] = (
                            f"{note_result.get('response_text', '').strip()}\n\n{follow_up_text}"
                        ).strip()
                        note_result["intent"] = follow_up.get("intent") or note_result.get("intent")
                        note_result["tool_name"] = follow_up.get("tool_name") or note_result.get("tool_name")
                except Exception:
                    logger.exception("WhatsApp text note follow-up failed for phone=%s", phone)

        history = session.get("conversation_history", [])
        history.append({"role": "user", "content": inbound_log_text})
        history.append({"role": "assistant", "content": note_result.get("response_text", "")})
        session["conversation_history"] = history[-20:]
        save_session(db, phone, session)
        log_message(
            db,
            phone,
            "inbound",
            inbound_log_text,
            user_id=link.user_id,
            tenant_id=link.tenant_id,
            wa_message_id=wa_message_id,
            intent=note_result.get("intent"),
            message_type=message_type,
        )
        log_message(
            db,
            phone,
            "outbound",
            note_result.get("response_text", ""),
            user_id=link.user_id,
            tenant_id=link.tenant_id,
            tool_called=note_result.get("tool_name"),
            latency_ms=elapsed,
        )
        note_result["latency_ms"] = elapsed
        return note_result

    detected_url = _extract_first_url(text)
    if detected_url:
        try:
            url_result = await _ingest_whatsapp_url(
                db,
                user_id=str(session.get("user_id") or link.user_id),
                tenant_id=str(link.tenant_id),
                url=detected_url,
                text=text,
            )
        except Exception as exc:
            logger.exception("WhatsApp URL ingestion failed for phone=%s", phone)
            url_result = {
                "response_text": _format_link_ingest_error(exc),
                "response_type": "text",
                "intent": "url_upload_error",
                "tool_name": "ingest_whatsapp_url",
            }
        url_success = url_result.get("intent") != "url_upload_error"
        _increment_whatsapp_metric(
            "link_ingest_success_total" if url_success else "link_ingest_failure_total",
            tenant_scope,
        )
        if not url_success:
            _increment_whatsapp_metric("visible_failure_total", tenant_scope)
        _log_whatsapp_event(
            "link_ingest_result",
            phone=phone,
            tenant_id=tenant_scope,
            success=url_success,
            notebook_id=url_result.get("notebook_id"),
            tool_name=url_result.get("tool_name"),
        )

        elapsed = int((time.time() - start_time) * 1000)
        if url_result.get("notebook_id"):
            session["active_notebook_id"] = str(url_result["notebook_id"])
            follow_up_prompt = _strip_url_from_text(text, detected_url)
            if _should_trigger_post_ingest_follow_up(follow_up_prompt):
                try:
                    follow_up = await _run_post_ingest_follow_up(
                        message=follow_up_prompt,
                        user_id=str(session.get("active_child_id") or link.user_id),
                        tenant_id=str(link.tenant_id),
                        role=session["role"],
                        notebook_id=str(url_result["notebook_id"]),
                        conversation_history=session.get("conversation_history", []),
                    )
                    follow_up_text = str(follow_up.get("response") or "").strip()
                    if follow_up_text:
                        url_result["response_text"] = (
                            f"{url_result.get('response_text', '').strip()}\n\n"
                            f"{follow_up_text}"
                        ).strip()
                        url_result["intent"] = follow_up.get("intent") or url_result.get("intent")
                        url_result["tool_name"] = follow_up.get("tool_name") or url_result.get("tool_name")
                except Exception:
                    logger.exception("WhatsApp post-link follow-up failed for phone=%s", phone)

        history = session.get("conversation_history", [])
        history.append({"role": "user", "content": inbound_log_text})
        history.append({"role": "assistant", "content": url_result.get("response_text", "")})
        session["conversation_history"] = history[-20:]
        save_session(db, phone, session)
        log_message(
            db,
            phone,
            "inbound",
            inbound_log_text,
            user_id=link.user_id,
            tenant_id=link.tenant_id,
            wa_message_id=wa_message_id,
            intent=url_result.get("intent"),
            message_type=message_type,
        )
        log_message(
            db,
            phone,
            "outbound",
            url_result.get("response_text", ""),
            user_id=link.user_id,
            tenant_id=link.tenant_id,
            tool_called=url_result.get("tool_name"),
            latency_ms=elapsed,
        )
        url_result["latency_ms"] = elapsed
        return url_result

    # 8. System commands
    if text_stripped in SYSTEM_COMMANDS:
        response = handle_system_command(db, text_stripped, session)
        if response == "__SWITCH_CHILD__":
            _increment_whatsapp_metric("routing_success_total", tenant_scope)
            switch_result = _build_child_switch_response(db, session)
            elapsed = int((time.time() - start_time) * 1000)
            log_message(db, phone, "inbound", inbound_log_text, user_id=link.user_id, tenant_id=link.tenant_id,
                        wa_message_id=wa_message_id)
            log_message(db, phone, "outbound", switch_result.get("response_text", ""), user_id=link.user_id, tenant_id=link.tenant_id,
                        latency_ms=elapsed)
            return switch_result
        if response == "__REPORT_CARD__":
            _increment_whatsapp_metric("routing_success_total", tenant_scope)
            report_result = _build_report_card_response(db, session)
            elapsed = int((time.time() - start_time) * 1000)
            log_message(db, phone, "inbound", inbound_log_text, user_id=link.user_id, tenant_id=link.tenant_id,
                        wa_message_id=wa_message_id)
            log_message(db, phone, "outbound", report_result.get("response_text", ""), user_id=link.user_id, tenant_id=link.tenant_id,
                        latency_ms=elapsed)
            return report_result
        elapsed = int((time.time() - start_time) * 1000)
        _increment_whatsapp_metric("routing_success_total", tenant_scope)
        log_message(db, phone, "inbound", inbound_log_text, user_id=link.user_id, tenant_id=link.tenant_id,
                    wa_message_id=wa_message_id)
        log_message(db, phone, "outbound", response, user_id=link.user_id, tenant_id=link.tenant_id,
                    latency_ms=elapsed)
        return {"response_text": response, "response_type": "text"}

    # 8. Ensure parent has an active child before running parent tools
    if session.get("role") == "parent" and not session.get("active_child_id"):
        child_prompt = _build_child_switch_response(db, session)
        if child_prompt.get("response_type") == "list":
            _increment_whatsapp_metric("routing_success_total", tenant_scope)
            elapsed = int((time.time() - start_time) * 1000)
            log_message(db, phone, "inbound", text, user_id=link.user_id, tenant_id=link.tenant_id,
                        wa_message_id=wa_message_id)
            log_message(db, phone, "outbound", child_prompt.get("response_text", ""), user_id=link.user_id, tenant_id=link.tenant_id,
                        latency_ms=elapsed)
            return child_prompt

    # 9. AI Agent processing
    try:
        from src.interfaces.whatsapp_bot.agent import run_whatsapp_agent
        result = await run_whatsapp_agent(
            message=text,
            user_id=str(session.get("active_child_id") or link.user_id),
            tenant_id=str(link.tenant_id),
            role=session["role"],
            notebook_id=str(session.get("active_notebook_id") or "") or None,
            conversation_history=session.get("conversation_history", [])[-10:],
            session_id=session.get("session_id"),
            pending_confirmation_id=session.get("pending_mascot_confirmation_id"),
        )
    except Exception:
        logger.exception("WhatsApp agent failed for phone=%s", phone)
        result = {
            "response": "❌ Sorry, I encountered an error processing your request. Please try again.",
            "response_type": "text",
            "intent": "error",
            "tool_name": None,
        }

    if result.get("intent") == "error":
        _increment_whatsapp_metric("routing_failure_total", tenant_scope)
        _increment_whatsapp_metric("visible_failure_total", tenant_scope)
    else:
        _increment_whatsapp_metric("routing_success_total", tenant_scope)
    _log_whatsapp_event(
        "agent_result",
        phone=phone,
        tenant_id=tenant_scope,
        intent=result.get("intent"),
        tool_name=result.get("tool_name"),
        notebook_id=session.get("active_notebook_id"),
    )

    elapsed = int((time.time() - start_time) * 1000)

    if result.get("notebook_id"):
        session["active_notebook_id"] = str(result["notebook_id"])
    if result.get("requires_confirmation") and result.get("confirmation_id"):
        session["pending_mascot_confirmation_id"] = result["confirmation_id"]
    elif result.get("confirmation_cleared") or result.get("intent") == "confirm":
        session.pop("pending_mascot_confirmation_id", None)

    # 8. Update session conversation history
    history = session.get("conversation_history", [])
    history.append({"role": "user", "content": inbound_log_text})
    history.append({"role": "assistant", "content": result.get("response", "")})
    session["conversation_history"] = history[-20:]  # Keep last 20 messages
    save_session(db, phone, session)

    # 9. Log messages
    log_message(db, phone, "inbound", inbound_log_text, user_id=link.user_id, tenant_id=link.tenant_id,
                wa_message_id=wa_message_id, intent=result.get("intent"), message_type=message_type)
    log_message(db, phone, "outbound", result.get("response", ""), user_id=link.user_id,
                tenant_id=link.tenant_id, tool_called=result.get("tool_name"), latency_ms=elapsed)

    return {
        "response_text": result.get("response", ""),
        "response_type": result.get("response_type", "text"),
        "intent": result.get("intent"),
        "tool_name": result.get("tool_name"),
        "latency_ms": elapsed,
    }


# ─── Auth Flow Helpers ────────────────────────────────────────

async def _handle_unlinked_phone(db: Session, phone: str, text: str) -> dict:
    """Handle messages from phones not yet linked to an ERP account."""
    # Check if there's a pending OTP
    session = get_session(db, phone)
    normalized = (text or "").strip()
    lowered = normalized.lower()

    if session and session.get("pending_action") == "awaiting_otp":
        return await _handle_otp_verification(db, phone, text, session)

    if session and session.get("pending_action") == "awaiting_email":
        if lowered in SIGNUP_COMMANDS:
            session["pending_action"] = "awaiting_signup_email"
            save_session(db, phone, session)
            return {
                "response_text": "Send the email address you want to use for your new student account.",
                "response_type": "text",
            }
        return await _handle_email_lookup(db, phone, text, session)

    if session and session.get("pending_action") == "awaiting_signup_email":
        return await _handle_signup_email(db, phone, text, session)

    if lowered in SIGNUP_COMMANDS:
        temp_session = {
            "session_id": f"ws-{uuid4().hex[:12]}",
            "phone": phone,
            "user_id": None,
            "tenant_id": None,
            "role": None,
            "active_notebook_id": None,
            "pending_action": "awaiting_signup_email",
            "conversation_history": [],
            "last_activity": datetime.now(timezone.utc).isoformat(),
        }
        save_session(db, phone, temp_session)
        return {
            "response_text": (
                "👋 *Welcome to VidyaOS!*\n\n"
                "Send the email address you want to use for your new student account."
            ),
            "response_type": "text",
        }

    if _looks_like_email(normalized):
        temp_session = {
            "session_id": f"ws-{uuid4().hex[:12]}",
            "phone": phone,
            "user_id": None,
            "tenant_id": None,
            "role": None,
            "active_notebook_id": None,
            "pending_action": "awaiting_email",
            "conversation_history": [],
            "last_activity": datetime.now(timezone.utc).isoformat(),
        }
        save_session(db, phone, temp_session)
        return await _handle_email_lookup(db, phone, normalized, temp_session)

    # Start fresh auth flow
    temp_session = {
        "session_id": f"ws-{uuid4().hex[:12]}",
        "phone": phone,
        "user_id": None,
        "tenant_id": None,
        "role": None,
        "active_notebook_id": None,
        "pending_action": "awaiting_email",
        "conversation_history": [],
        "last_activity": datetime.now(timezone.utc).isoformat(),
    }
    save_session(db, phone, temp_session)

    return {
        "response_text": (
            "👋 *Welcome to VidyaOS!*\n\n"
            "To get started, send your registered email address.\n"
            "If you're new here, reply *signup* to create a student account."
        ),
        "response_type": "text",
    }


async def _handle_email_lookup(db: Session, phone: str, text: str, session: dict) -> dict:
    """User submitted their email — look up and send OTP."""
    from src.domains.identity.models.user import User

    email = text.strip().lower()
    if not _looks_like_email(email):
        return {
            "response_text": "❌ Please send a valid email address.",
            "response_type": "text",
        }
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return {
            "response_text": "❌ No account found with that email. Check it and try again, or reply *signup* to create a new student account.",
            "response_type": "text",
        }

    # Generate OTP
    otp = generate_otp(phone, email)

    session["pending_action"] = "awaiting_otp"
    session["user_id"] = str(user.id)
    session["tenant_id"] = str(user.tenant_id)
    session["role"] = user.role
    save_session(db, phone, session)

    return {
        "response_text": f"📩 Your verification code is: *{otp}*\n\nPlease enter the 6-digit code to verify.",
        "response_type": "text",
    }


async def _handle_signup_email(db: Session, phone: str, text: str, session: dict) -> dict:
    email = text.strip().lower()
    if not _looks_like_email(email):
        return {
            "response_text": "❌ Please send a valid school email address to create your account.",
            "response_type": "text",
        }

    user, error = _create_whatsapp_signup_user(db, phone=phone, email=email)
    if error:
        return {"response_text": f"❌ {error}", "response_type": "text"}

    return _complete_authenticated_session(db, phone=phone, session=session, user=user, is_signup=True)


async def _handle_otp_verification(db: Session, phone: str, text: str, session: dict) -> dict:
    """User submitted an OTP — verify and complete linking."""
    result = verify_otp(phone, text.strip())

    if not result["success"]:
        return {"response_text": f"❌ {result['error']}", "response_type": "text"}

    user_id = UUID(session["user_id"])
    tenant_id = UUID(session["tenant_id"])
    _upsert_phone_link(db, phone=phone, user_id=user_id, tenant_id=tenant_id)
    db.commit()

    from src.domains.identity.models.user import User
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.phone_number = phone
        user.whatsapp_linked = True
        user.last_login = datetime.now(timezone.utc)
        db.commit()
        db.refresh(user)

    return _complete_authenticated_session(db, phone=phone, session=session, user=user or SimpleNamespace(
        id=user_id,
        tenant_id=tenant_id,
        full_name="User",
        role=session.get("role", "student"),
    ))
def _classify_outbound_exception(exc: Exception) -> dict:
    """Classify outbound delivery failures for retry-aware handling."""
    if isinstance(exc, getattr(httpx, "HTTPStatusError", ())):
        response = getattr(exc, "response", None)
        status_code = getattr(response, "status_code", None)
        retryable = status_code in WA_RETRYABLE_STATUS_CODES if status_code is not None else False
        return {
            "success": False,
            "error": str(exc),
            "error_type": "http_retryable" if retryable else "http_non_retryable",
            "retryable": retryable,
            "status_code": status_code,
        }

    timeout_types = tuple(
        error_type
        for error_type in (
            getattr(httpx, "TimeoutException", None),
            getattr(httpx, "ConnectError", None),
        )
        if isinstance(error_type, type)
    )
    if timeout_types and isinstance(exc, timeout_types):
        return {
            "success": False,
            "error": str(exc),
            "error_type": "network_retryable",
            "retryable": True,
            "status_code": None,
        }

    return {
        "success": False,
        "error": str(exc),
        "error_type": "unknown_non_retryable",
        "retryable": False,
        "status_code": None,
    }


async def _send_whatsapp_payload(phone: str, payload: dict, *, transport: str) -> dict:
    if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_ID:
        logger.warning("WhatsApp credentials not configured. Message not sent.")
        _increment_whatsapp_metric("outbound_failure_total")
        _increment_whatsapp_metric("outbound_non_retryable_failure_total")
        _log_whatsapp_event("outbound_failure", phone=phone, transport=transport, error_type="configuration")
        return {
            "success": False,
            "error": "WhatsApp not configured",
            "error_type": "configuration",
            "retryable": False,
            "status_code": None,
        }

    url = f"{WHATSAPP_API_URL}/{WHATSAPP_PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            _increment_whatsapp_metric("outbound_success_total")
            _log_whatsapp_event("outbound_success", phone=phone, transport=transport)
            return {"success": True, "data": resp.json()}
    except Exception as exc:
        failure = _classify_outbound_exception(exc)
        _increment_whatsapp_metric("outbound_failure_total")
        _increment_whatsapp_metric(
            "outbound_retryable_failure_total" if failure.get("retryable") else "outbound_non_retryable_failure_total"
        )
        _log_whatsapp_event(
            "outbound_failure",
            phone=phone,
            transport=transport,
            error_type=failure.get("error_type"),
            retryable=failure.get("retryable"),
            status_code=failure.get("status_code"),
        )
        logger.error(
            "WhatsApp %s send failed phone=%s type=%s retryable=%s status=%s error=%s",
            transport,
            phone,
            failure.get("error_type"),
            failure.get("retryable"),
            failure.get("status_code"),
            failure.get("error"),
        )
        return failure


async def send_text_message(phone: str, text: str) -> dict:
    """Send a plain-text WhatsApp message via Meta Cloud API."""
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": {"body": text[:4096]},
    }
    return await _send_whatsapp_payload(phone, payload, transport="text")


async def send_interactive_list(phone: str, header: str, body: str, button_text: str, rows: list[dict]) -> dict:
    """Send an interactive list message for multi-option selection."""
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {"type": "text", "text": header},
            "body": {"text": body},
            "action": {
                "button": button_text,
                "sections": [{"title": "Options", "rows": rows[:10]}],
            },
        },
    }
    return await _send_whatsapp_payload(phone, payload, transport="interactive_list")


async def send_buttons(phone: str, body: str, buttons: list[dict]) -> dict:
    """Send a quick-reply button message."""
    btn_list = [
        {"type": "reply", "reply": {"id": button["id"], "title": button["title"][:20]}}
        for button in buttons[:3]
    ]
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body},
            "action": {"buttons": btn_list},
        },
    }
    return await _send_whatsapp_payload(phone, payload, transport="interactive_buttons")


async def send_document_message(phone: str, link: str, filename: str, caption: str | None = None) -> dict:
    """Send a WhatsApp document message via Meta Cloud API."""
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "document",
        "document": {
            "link": link,
            "filename": filename[:240],
        },
    }
    if caption:
        payload["document"]["caption"] = caption[:1024]
    return await _send_whatsapp_payload(phone, payload, transport="document")
