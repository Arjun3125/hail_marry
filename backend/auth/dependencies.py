"""FastAPI auth dependencies for route protection."""
import os
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from database import get_db
import uuid
from auth.jwt import decode_access_token
from src.domains.identity.models.user import User

# Demo mode check
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() in ("true", "1", "yes")

# Cache for demo user to avoid repeated DB queries
_demo_user_cache: dict = {}


async def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """Extract and validate user from JWT cookie or Authorization header.
    In DEMO_MODE, returns a demo user based on the X-Demo-Role header or defaults to student.
    """
    # ── DEMO MODE: bypass JWT validation ──
    if DEMO_MODE:
        role = request.headers.get("X-Demo-Role") or request.cookies.get("demo_role") or "student"
        cache_key = role

        if cache_key not in _demo_user_cache:
            user = db.query(User).filter(User.role == role, User.is_active == True).first()
            if not user:
                user = db.query(User).filter(User.is_active == True).first()
            if user:
                _demo_user_cache[cache_key] = user.id

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
        User.is_active == True,
        User.is_deleted == False,
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


def require_role(*roles: str):
    """Dependency factory: require user to have one of the specified roles."""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        # In DEMO_MODE, skip role enforcement
        if DEMO_MODE:
            return current_user
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.role}' not authorized. Required: {roles}",
            )
        return current_user
    return role_checker
