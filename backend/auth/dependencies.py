"""FastAPI auth dependencies for route protection."""
import os
import uuid
import threading
import logging
from typing import Optional, Dict
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from auth.jwt import decode_access_token
from config import settings
from database import get_db
from src.domains.identity.models.user import User

logger = logging.getLogger(__name__)

_NON_PRODUCTION_ENVS = {"local", "development", "dev", "test"}


def is_demo_mode() -> bool:
    """Resolve demo mode dynamically so tests/runtime env changes are honored."""
    app_env = os.getenv("APP_ENV", settings.app.env or "production").strip().lower()
    if app_env == "production":
        return False
    env_demo_mode = os.getenv("DEMO_MODE")
    if env_demo_mode is None:
        configured_demo_mode = settings.app.demo_mode
    else:
        configured_demo_mode = env_demo_mode.strip().lower() in ("true", "1", "yes")
    return configured_demo_mode and app_env in _NON_PRODUCTION_ENVS


# Thread-safe cache for demo user to avoid repeated DB queries
class DemoUserCache:
    """Thread-safe singleton cache for demo users."""
    
    _instance: Optional["DemoUserCache"] = None
    _lock: threading.Lock = threading.Lock()
    
    def __init__(self):
        self._cache: Dict[str, UUID] = {}
        self._cache_lock: threading.Lock = threading.Lock()
    
    @classmethod
    def get_instance(cls) -> "DemoUserCache":
        """Get or create singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    def get(self, key: str) -> Optional[UUID]:
        """Thread-safe get from cache."""
        with self._cache_lock:
            return self._cache.get(key)
    
    def set(self, key: str, value: UUID) -> None:
        """Thread-safe set to cache."""
        with self._cache_lock:
            self._cache[key] = value
    
    def has_key(self, key: str) -> bool:
        """Check if key exists in cache."""
        with self._cache_lock:
            return key in self._cache
    
    def clear(self) -> None:
        """Clear all cache (useful for testing)."""
        with self._cache_lock:
            self._cache.clear()


_demo_user_cache = DemoUserCache.get_instance()


async def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """Extract and validate user from JWT cookie or Authorization header.
    In demo mode (is_demo_mode() returns True), first tries JWT if present, then falls back to role-based lookup.
    """
    # ── DEMO MODE ──
    if is_demo_mode():
        # 0. Check for E2E test token first
        token = request.cookies.get("access_token")
        if not token:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ", 1)[1]

        if token == "test-token":
            # E2E test token - use demo_role cookie to determine user role
            role = request.cookies.get("demo_role") or "admin"  # Default to admin for tests
            cache_key = f"test-{role}"

            if not _demo_user_cache.has_key(cache_key):
                user = None
                # Use environment variable for demo user email (not hardcoded)
                demo_user_email = os.getenv("DEMO_USER_EMAIL", "demo_cbse11@modernhustlers.com")
                if role == "student":
                    user = db.query(User).filter(User.email == demo_user_email, User.is_active).first()
                if not user:
                    user = db.query(User).filter(User.role == role, User.is_active).first()
                if not user:
                    user = db.query(User).filter(User.is_active).first()
                if user:
                    _demo_user_cache.set(cache_key, user.id)

            user_id = _demo_user_cache.get(cache_key)
            if user_id:
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    request.state.tenant_id = str(user.tenant_id)
                    request.state.user_role = user.role
                    request.state.user_id = str(user.id)
                    return user

        # 1. Try JWT token first (from demo-login or regular login)
        token = request.cookies.get("access_token")
        if not token:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ", 1)[1]

        if token and token != "test-token":
            payload = decode_access_token(token)
            if payload and payload.get("user_id"):
                try:
                    user_uuid = uuid.UUID(payload["user_id"])
                    user = db.query(User).filter(User.id == user_uuid, User.is_active).first()
                    if user:
                        request.state.tenant_id = str(user.tenant_id)
                        request.state.user_role = user.role
                        request.state.user_id = str(user.id)
                        return user
                except (ValueError, Exception):
                    pass  # fall through to role-based lookup

        # 2. Fallback: role-based lookup via demo cookie only.
        # The role cookie is set by demo-management surfaces in local/dev demo mode.
        role = request.cookies.get("demo_role") or "student"
        cache_key = role

        if not _demo_user_cache.has_key(cache_key):
            user = None
            # Use environment variable for demo user email (not hardcoded)
            demo_user_email = os.getenv("DEMO_USER_EMAIL", "demo_cbse11@modernhustlers.com")
            if role == "student":
                user = db.query(User).filter(User.email == demo_user_email, User.is_active).first()
            if not user:
                user = db.query(User).filter(User.role == role, User.is_active).first()
            if not user:
                user = db.query(User).filter(User.is_active).first()
            if user:
                _demo_user_cache.set(cache_key, user.id)

        user_id = _demo_user_cache.get(cache_key)
        if user_id:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                request.state.tenant_id = str(user.tenant_id)
                request.state.user_role = user.role
                request.state.user_id = str(user.id)
                return user


        raise HTTPException(status_code=503, detail="Demo data not seeded. Run: python seed.py")

    # ── PRODUCTION: standard JWT auth ──
    token = None

    # Try cookie first
    token = request.cookies.get("access_token")

    # Fallback to Authorization header
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id_str = payload.get("user_id")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    try:
        user_uuid = uuid.UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed user ID in token",
        )

    user = db.query(User).filter(
        User.id == user_uuid,
        User.is_active,
        User.is_deleted.is_(False),
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    # Attach tenant_id to request state for downstream use
    request.state.tenant_id = str(user.tenant_id)
    request.state.user_role = user.role
    request.state.user_id = str(user.id)

    return user


def _resolve_optional_user(request: Request, db: Session) -> User | None:
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]

    if not token:
        return None

    payload = decode_access_token(token)
    user_id_str = payload.get("user_id") if payload else None
    if not user_id_str:
        return None

    try:
        user_uuid = uuid.UUID(user_id_str)
    except ValueError:
        return None

    user = db.query(User).filter(
        User.id == user_uuid,
        User.is_active,
        User.is_deleted.is_(False),
    ).first()
    if not user:
        return None

    request.state.tenant_id = str(user.tenant_id)
    request.state.user_role = user.role
    request.state.user_id = str(user.id)
    return user


async def get_current_user_optional(
    request: Request,
    db: Session = Depends(get_db),
) -> uuid.UUID | None:
    user = _resolve_optional_user(request, db)
    return user.id if user else None


async def get_tenant_id_optional(
    request: Request,
    db: Session = Depends(get_db),
) -> uuid.UUID | None:
    user = _resolve_optional_user(request, db)
    return user.tenant_id if user else None


def require_role(*roles: str):
    """Dependency factory: require user to have one of the specified roles."""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.role}' not authorized. Required: {roles}",
            )
        return current_user
    return role_checker
