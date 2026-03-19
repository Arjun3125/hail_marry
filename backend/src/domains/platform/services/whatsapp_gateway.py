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

import httpx
from sqlalchemy.orm import Session

from src.infrastructure.llm.cache import _get_redis
from src.domains.platform.models.whatsapp_models import PhoneUserLink, WhatsAppSession, WhatsAppMessage

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

# System commands handled without AI
SYSTEM_COMMANDS = {
    "/help": "help",
    "help": "help",
    "/logout": "logout",
    "/switch": "switch_child",
    "/status": "status",
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

def resolve_phone_to_user(db: Session, phone: str) -> Optional[PhoneUserLink]:
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
            link = PhoneUserLink()
            link.id = UUID(data["id"])
            link.phone = data["phone"]
            link.user_id = UUID(data["user_id"])
            link.tenant_id = UUID(data["tenant_id"])
            link.verified = True
            return link

    # Database lookup
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

    return "Unknown command. Type *help* for options."


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

    # 6. System commands
    text_stripped = text.strip().lower()
    if text_stripped in SYSTEM_COMMANDS:
        response = handle_system_command(db, text_stripped, session)
        elapsed = int((time.time() - start_time) * 1000)
        log_message(db, phone, "inbound", text, user_id=link.user_id, tenant_id=link.tenant_id,
                    wa_message_id=wa_message_id)
        log_message(db, phone, "outbound", response, user_id=link.user_id, tenant_id=link.tenant_id,
                    latency_ms=elapsed)
        return {"response_text": response, "response_type": "text"}

    # 7. AI Agent processing
    try:
        from src.interfaces.whatsapp_bot.agent import run_whatsapp_agent
        result = await run_whatsapp_agent(
            message=text,
            user_id=str(link.user_id),
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
