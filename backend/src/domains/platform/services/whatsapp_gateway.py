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
import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID, uuid4

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
from src.infrastructure.llm.cache import _get_redis

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
    "/switch": "switch_child",
    "/status": "status",
    "/reportcard": "report_card",
    "/report-card": "report_card",
}

# Tools that require async queue processing
HEAVY_TOOLS = {"generate_quiz", "generate_study_guide", "generate_audio_overview"}


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
        lines.extend(["\n/logout — Unlink this phone", "/switch — Switch child (parents)"])
        return "\n".join(lines)

    elif cmd == "logout":
        delete_session(db, session["phone"])
        return "✅ Logged out. Send any message to log in again."

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
    topic = (request.get("topic") or request.get("query") or request.get("subject_name") or "this request").strip()
    job_type = job.get("job_type", "AI task")
    labels = {
        "query": "study guide",
        "audio": "audio overview",
        "video": "video overview",
        "study_tool": "study tool",
        "teacher_assessment": "teacher assessment",
    }
    label = labels.get(job_type, job_type.replace("_", " "))
    return label, topic


def format_ai_job_status_message(job: dict) -> str:
    status = job.get("status")
    label, topic = _describe_ai_job(job)
    job_id = job.get("job_id", "unknown")

    if status == "completed":
        return (
            f"✅ Your {label} is ready for *{topic}*.\n"
            f"Job ID: `{job_id}`\n"
            "Reply with the same request if you want another version."
        )

    error = (job.get("error") or "Unknown error").strip()
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
) -> dict:
    """Main entry point: process an inbound WhatsApp message through the full pipeline.

    Returns:
        Dict with 'response_text', 'response_type', and metadata.
    """
    start_time = time.time()

    # 1. Deduplication
    if wa_message_id and is_duplicate_message(wa_message_id):
        return {"response_text": None, "response_type": "none", "duplicate": True}

    # 2. Rate limiting
    if is_rate_limited(phone):
        return {
            "response_text": "⚠️ Too many messages. Please wait a moment and try again.",
            "response_type": "text",
        }

    # 3. Resolve user
    link = resolve_phone_to_user(db, phone)

    if not link:
        # Unlinked phone — start auth flow
        return await _handle_unlinked_phone(db, phone, text)

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

    # 7. System commands
    if text_stripped in SYSTEM_COMMANDS:
        response = handle_system_command(db, text_stripped, session)
        if response == "__SWITCH_CHILD__":
            switch_result = _build_child_switch_response(db, session)
            elapsed = int((time.time() - start_time) * 1000)
            log_message(db, phone, "inbound", text, user_id=link.user_id, tenant_id=link.tenant_id,
                        wa_message_id=wa_message_id)
            log_message(db, phone, "outbound", switch_result.get("response_text", ""), user_id=link.user_id, tenant_id=link.tenant_id,
                        latency_ms=elapsed)
            return switch_result
        if response == "__REPORT_CARD__":
            report_result = _build_report_card_response(db, session)
            elapsed = int((time.time() - start_time) * 1000)
            log_message(db, phone, "inbound", text, user_id=link.user_id, tenant_id=link.tenant_id,
                        wa_message_id=wa_message_id)
            log_message(db, phone, "outbound", report_result.get("response_text", ""), user_id=link.user_id, tenant_id=link.tenant_id,
                        latency_ms=elapsed)
            return report_result
        elapsed = int((time.time() - start_time) * 1000)
        log_message(db, phone, "inbound", text, user_id=link.user_id, tenant_id=link.tenant_id,
                    wa_message_id=wa_message_id)
        log_message(db, phone, "outbound", response, user_id=link.user_id, tenant_id=link.tenant_id,
                    latency_ms=elapsed)
        return {"response_text": response, "response_type": "text"}

    # 8. Ensure parent has an active child before running parent tools
    if session.get("role") == "parent" and not session.get("active_child_id"):
        child_prompt = _build_child_switch_response(db, session)
        if child_prompt.get("response_type") == "list":
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
            conversation_history=session.get("conversation_history", [])[-10:],
        )
    except Exception:
        logger.exception("WhatsApp agent failed for phone=%s", phone)
        result = {
            "response": "❌ Sorry, I encountered an error processing your request. Please try again.",
            "response_type": "text",
            "intent": "error",
            "tool_name": None,
        }

    elapsed = int((time.time() - start_time) * 1000)

    # 8. Update session conversation history
    history = session.get("conversation_history", [])
    history.append({"role": "user", "content": text})
    history.append({"role": "assistant", "content": result.get("response", "")})
    session["conversation_history"] = history[-20:]  # Keep last 20 messages
    save_session(db, phone, session)

    # 9. Log messages
    log_message(db, phone, "inbound", text, user_id=link.user_id, tenant_id=link.tenant_id,
                wa_message_id=wa_message_id, intent=result.get("intent"))
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

    if session and session.get("pending_action") == "awaiting_otp":
        return await _handle_otp_verification(db, phone, text, session)

    if session and session.get("pending_action") == "awaiting_email":
        return await _handle_email_lookup(db, phone, text, session)

    # Start fresh auth flow
    temp_session = {
        "session_id": f"ws-{uuid4().hex[:12]}",
        "phone": phone,
        "user_id": None,
        "tenant_id": None,
        "role": None,
        "pending_action": "awaiting_email",
        "conversation_history": [],
        "last_activity": datetime.now(timezone.utc).isoformat(),
    }
    save_session(db, phone, temp_session)

    return {
        "response_text": (
            "👋 *Welcome to VidyaOS!*\n\n"
            "To get started, please enter your registered email address."
        ),
        "response_type": "text",
    }


async def _handle_email_lookup(db: Session, phone: str, text: str, session: dict) -> dict:
    """User submitted their email — look up and send OTP."""
    from src.domains.identity.models.user import User

    email = text.strip().lower()
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return {
            "response_text": "❌ No account found with that email. Please check and try again.",
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


async def _handle_otp_verification(db: Session, phone: str, text: str, session: dict) -> dict:
    """User submitted an OTP — verify and complete linking."""
    result = verify_otp(phone, text.strip())

    if not result["success"]:
        return {"response_text": f"❌ {result['error']}", "response_type": "text"}

    # Create the phone_user_link record
    user_id = UUID(session["user_id"])
    tenant_id = UUID(session["tenant_id"])
    from src.domains.platform.models.whatsapp_models import PhoneUserLink

    existing = db.query(PhoneUserLink).filter(
        PhoneUserLink.phone == phone,
        PhoneUserLink.tenant_id == tenant_id,
    ).first()

    if existing:
        existing.user_id = user_id
        existing.verified = True
        existing.verified_at = datetime.now(timezone.utc)
    else:
        link = PhoneUserLink(
            phone=phone,
            user_id=user_id,
            tenant_id=tenant_id,
            verified=True,
            verified_at=datetime.now(timezone.utc),
        )
        db.add(link)

    db.commit()

    # Upgrade session to authenticated
    session["pending_action"] = None
    save_session(db, phone, session)

    # Invalidate Redis cache for phone
    redis = _get_redis()
    if redis:
        redis.delete(f"wa:phone:{phone}")

    from src.domains.identity.models.user import User
    user = db.query(User).filter(User.id == user_id).first()
    name = user.full_name if user else "User"

    return {
        "response_text": (
            f"✅ *Verified!* You are now logged in as *{name}* ({session['role']}).\n\n"
            f"Type *help* to see what I can do for you."
        ),
        "response_type": "text",
    }
