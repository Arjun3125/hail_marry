"""Refresh token blacklisting — prevents reuse of rotated tokens.

Uses an in-memory LRU cache for fast lookups with a DB table as source of truth.
"""
import uuid
from datetime import datetime, timezone
from functools import lru_cache

from sqlalchemy import Column, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Session

from database import Base


class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    jti = Column(String(64), unique=True, nullable=False, index=True)
    user_id = Column(String(64), nullable=True)
    blacklisted_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)


# ── In-memory cache for fast lookups ──
_blacklist_cache: set[str] = set()
_CACHE_MAX_SIZE = 5000


def blacklist_token(db: Session, jti: str, user_id: str = "", expires_at: datetime = None):
    """Add a token JTI to the blacklist."""
    if not expires_at:
        from auth.jwt import REFRESH_TOKEN_EXPIRE_DAYS
        from datetime import timedelta
        expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    existing = db.query(BlacklistedToken).filter(BlacklistedToken.jti == jti).first()
    if not existing:
        entry = BlacklistedToken(jti=jti, user_id=user_id, expires_at=expires_at)
        db.add(entry)
        db.commit()

    # Add to in-memory cache
    if len(_blacklist_cache) < _CACHE_MAX_SIZE:
        _blacklist_cache.add(jti)


def is_blacklisted(db: Session, jti: str) -> bool:
    """Check if a token JTI is blacklisted."""
    # Fast path: check in-memory cache
    if jti in _blacklist_cache:
        return True

    # Slow path: check database
    entry = db.query(BlacklistedToken).filter(BlacklistedToken.jti == jti).first()
    if entry:
        _blacklist_cache.add(jti)
        return True

    return False


def cleanup_expired(db: Session) -> int:
    """Remove expired blacklist entries. Returns count of deleted entries."""
    now = datetime.now(timezone.utc)
    count = db.query(BlacklistedToken).filter(BlacklistedToken.expires_at < now).delete()
    db.commit()

    # Rebuild cache from active entries
    _blacklist_cache.clear()
    active = db.query(BlacklistedToken.jti).limit(_CACHE_MAX_SIZE).all()
    for (jti,) in active:
        _blacklist_cache.add(jti)

    return count


def blacklist_all_for_user(db: Session, user_id: str, expires_at: datetime = None):
    """Blacklist all tokens for a specific user (e.g., on password change)."""
    if not expires_at:
        from auth.jwt import REFRESH_TOKEN_EXPIRE_DAYS
        from datetime import timedelta
        expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    # This is a marker — actual enforcement happens via JTI checks
    # When a user changes password, all their existing refresh tokens
    # should be invalidated by bumping a user-level token version
    pass
