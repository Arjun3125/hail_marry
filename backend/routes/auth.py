"""Authentication routes — Google OAuth login, token refresh, profile, logout."""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from auth.jwt import create_access_token, create_refresh_token, decode_refresh_token
from auth.oauth import verify_google_token
from auth.dependencies import get_current_user
from config import settings
from models.user import User
from models.tenant import Tenant
from schemas.auth import GoogleLoginRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


def _cookie_policy() -> tuple[bool, str]:
    """
    Choose cookie policy by environment.
    - Production/staging deployments (cross-site frontend/backend): Secure + SameSite=None
    - Local development: legacy behavior (Lax, optionally insecure)
    """
    app_env = (settings.app.env or "").lower()
    if app_env in {"production", "prod", "staging"}:
        return True, "none"
    return (not settings.app.debug), "lax"


@router.post("/google", response_model=TokenResponse)
async def google_login(
    request: GoogleLoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    """
    Authenticate via Google OAuth.
    1. Verify Google ID token
    2. Find or create user based on email
    3. Map to tenant via email domain
    4. Issue JWT access + refresh tokens
    """
    # Verify the Google token
    google_user = await verify_google_token(request.token)
    if not google_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token",
        )

    email = google_user["email"]
    domain = email.split("@")[1] if "@" in email else ""

    # Find tenant by email domain
    tenant = db.query(Tenant).filter(Tenant.domain == domain, Tenant.is_active == 1).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No active tenant found for this email domain",
        )

    # Find or create user
    user = db.query(User).filter(User.email == email, User.tenant_id == tenant.id).first()

    if not user:
        # Auto-create user on first login
        user = User(
            tenant_id=tenant.id,
            google_id=google_user["google_id"],
            email=email,
            full_name=google_user["full_name"],
            avatar_url=google_user["avatar_url"],
            role="student",  # Default role, admin can change
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Update last login
        user.last_login = datetime.now(timezone.utc)
        user.avatar_url = google_user.get("avatar_url") or user.avatar_url
        db.commit()

    # Create JWT with user info + tenant
    token_data = {
        "user_id": str(user.id),
        "tenant_id": str(user.tenant_id),
        "email": user.email,
        "role": user.role,
    }
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    cookie_secure, cookie_samesite = _cookie_policy()

    # Set HTTP-only cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=cookie_secure,
        samesite=cookie_samesite,
        max_age=3600,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=cookie_secure,
        samesite=cookie_samesite,
        max_age=7 * 24 * 3600,  # 7 days
        path="/api/auth/refresh",  # Only sent to refresh endpoint
    )

    return TokenResponse(access_token=access_token)


class RefreshRequest(BaseModel):
    refresh_token: str | None = None  # Can also be sent via cookie


@router.post("/refresh")
async def refresh_tokens(
    request_body: RefreshRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    """
    Rotate tokens: validate refresh token, issue new access + refresh pair.
    Accepts refresh token from cookie or request body.
    """
    # Try body first, then cookie
    token = request_body.refresh_token
    if not token:
        token = request.cookies.get("refresh_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token required",
        )

    payload = decode_refresh_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    user_id = payload.get("user_id")
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # Issue new token pair (rotation)
    token_data = {
        "user_id": str(user.id),
        "tenant_id": str(user.tenant_id),
        "email": user.email,
        "role": user.role,
    }
    new_access = create_access_token(token_data)
    new_refresh = create_refresh_token(token_data)
    cookie_secure, cookie_samesite = _cookie_policy()

    response.set_cookie(
        key="access_token",
        value=new_access,
        httponly=True,
        secure=cookie_secure,
        samesite=cookie_samesite,
        max_age=3600,
    )
    response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        httponly=True,
        secure=cookie_secure,
        samesite=cookie_samesite,
        max_age=7 * 24 * 3600,
        path="/api/auth/refresh",
    )

    return {"access_token": new_access, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user."""
    return current_user


class ProfileUpdate(BaseModel):
    full_name: str | None = None
    avatar_url: str | None = None


@router.patch("/profile")
async def update_profile(
    data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update the current user's profile (name, avatar)."""
    if data.full_name is not None:
        current_user.full_name = data.full_name.strip()[:100]
    if data.avatar_url is not None:
        current_user.avatar_url = data.avatar_url.strip()[:500]
    db.commit()
    return {
        "success": True,
        "full_name": current_user.full_name,
        "avatar_url": current_user.avatar_url,
    }


@router.post("/logout")
async def logout(response: Response):
    """Clear auth cookies."""
    cookie_secure, cookie_samesite = _cookie_policy()
    response.delete_cookie(
        "access_token",
        secure=cookie_secure,
        samesite=cookie_samesite,
    )
    response.delete_cookie(
        "refresh_token",
        path="/api/auth/refresh",
        secure=cookie_secure,
        samesite=cookie_samesite,
    )
    return {"message": "Logged out", "success": True}

