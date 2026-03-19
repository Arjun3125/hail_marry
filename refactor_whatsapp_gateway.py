import pathlib
import re

gateway_path = pathlib.Path('backend/src/domains/platform/services/whatsapp_gateway.py')
code = gateway_path.read_text(encoding='utf-8')

# 1. Update Session Management Functions
session_management_replacement = '''# ─── Session Management ──────────────────────────────────────

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
        from datetime import datetime, timezone
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
        from datetime import datetime, timedelta, timezone
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
        db.rollback()'''

code = re.sub(r'# ─── Session Management ──────────────────────────────────────.*?def delete_session\(phone: str\) -> None:.*?redis\.delete\(f"wa:session:{phone}"\)', session_management_replacement, code, flags=re.DOTALL)

# 2. Update all callers of session functions:
# get_session(phone) -> get_session(db, phone)
code = re.sub(r'(?<!def )get_session\(phone\)', 'get_session(db, phone)', code)

# create_session(phone, ...) -> create_session(db, phone, ...)
code = re.sub(r'(?<!def )create_session\(phone,', 'create_session(db, phone,', code)

# save_session(phone, session) -> save_session(db, phone, session)
code = re.sub(r'(?<!def )save_session\(phone, temp_session\)', 'save_session(db, phone, temp_session)', code)
code = re.sub(r'(?<!def )save_session\(phone, session\)', 'save_session(db, phone, session)', code)

# delete_session(session["phone"]) -> delete_session(db, session["phone"])
code = re.sub(r'(?<!def )delete_session\(session\["phone"\]\)', 'delete_session(db, session["phone"])', code)

# Fix handle_system_command to accept db:
code = code.replace('def handle_system_command(command: str, session: dict) -> str:', 'def handle_system_command(db: Session, command: str, session: dict) -> str:')
code = code.replace('response = handle_system_command(text_stripped, session)', 'response = handle_system_command(db, text_stripped, session)')

gateway_path.write_text(code, encoding='utf-8')
print("Updated session fallbacks successfully in whatsapp_gateway.py")
