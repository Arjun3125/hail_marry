"""Authentication routes for Google OAuth, SAML SSO, token rotation, profile, and logout."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse, Response as FastAPIResponse
from passlib.context import CryptContext
from pydantic import BaseModel

from auth.dependencies import get_current_user
from auth.jwt import create_access_token, create_refresh_token, decode_refresh_token
from auth.oauth import verify_google_token
from auth.token_blacklist import blacklist_token, is_blacklisted
from config import settings
from database import get_db
from sqlalchemy.orm import Session
from models.tenant import Tenant
from models.user import User
from schemas.auth import GoogleLoginRequest, TokenResponse, UserResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter(prefix="/api/auth", tags=["Authentication"])
from services.saml_sso import (
    build_service_provider_metadata,
    create_or_update_saml_user,
    get_tenant_for_saml,
    process_saml_acs,
    saml_login_redirect,
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


def _cookie_policy() -> tuple[bool, str]:
    app_env = (settings.app.env or "").lower()
    if app_env in {"production", "prod", "staging"}:
        return True, "none"
    return (not settings.app.debug), "lax"


def _refresh_expiry(payload: dict) -> datetime | None:
    exp = payload.get("exp")
    if not exp:
        return None
    try:
        return datetime.fromtimestamp(int(exp), tz=timezone.utc)
    except (TypeError, ValueError):
        return None


def _issue_login_tokens(user: User, response: Response) -> str:
    token_data = {
        "user_id": str(user.id),
        "tenant_id": str(user.tenant_id),
        "email": user.email,
        "role": user.role,
    }
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    cookie_secure, cookie_samesite = _cookie_policy()

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
        max_age=7 * 24 * 3600,
        path="/api/auth/refresh",
    )
    return access_token


@router.post("/google", response_model=TokenResponse)
async def google_login(
    request: GoogleLoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    google_user = await verify_google_token(request.token)
    if not google_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token",
        )

    email = google_user["email"]
    domain = email.split("@")[1] if "@" in email else ""
    tenant = db.query(Tenant).filter(Tenant.domain == domain, Tenant.is_active == 1).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No active tenant found for this email domain",
        )

    user = db.query(User).filter(User.email == email, User.tenant_id == tenant.id).first()
    if not user:
        user = User(
            tenant_id=tenant.id,
            google_id=google_user["google_id"],
            email=email,
            full_name=google_user["full_name"],
            avatar_url=google_user["avatar_url"],
            role="student",
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user.last_login = datetime.now(timezone.utc)
        user.avatar_url = google_user.get("avatar_url") or user.avatar_url
        db.commit()

    token_data = {
        "user_id": str(user.id),
        "tenant_id": str(user.tenant_id),
        "email": user.email,
        "role": user.role,
    }
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    cookie_secure, cookie_samesite = _cookie_policy()

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
        max_age=7 * 24 * 3600,
        path="/api/auth/refresh",
    )
    return TokenResponse(access_token=access_token)


class LocalLoginRequest(BaseModel):
    email: str
    password: str
    tenant_domain: str | None = None


@router.post("/login", response_model=TokenResponse)
async def local_login(
    request: LocalLoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    email = request.email.lower().strip()
    
    # Try finding tenant by explicit domain or email domain
    domain = request.tenant_domain
    if not domain and "@" in email:
        domain = email.split("@")[1]
    
    if not domain:
        raise HTTPException(status_code=400, detail="Tenant domain could not be determined")

    tenant = db.query(Tenant).filter(Tenant.domain == domain, Tenant.is_active == 1).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No active tenant found for this domain",
        )

    user = db.query(User).filter(User.email == email, User.tenant_id == tenant.id).first()
    if not user or not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not pwd_context.verify(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active or user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated or deleted",
        )

    user.last_login = datetime.now(timezone.utc)
    db.commit()

    token_data = {
        "user_id": str(user.id),
        "tenant_id": str(user.tenant_id),
        "email": user.email,
        "role": user.role,
    }
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    cookie_secure, cookie_samesite = _cookie_policy()

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
        max_age=7 * 24 * 3600,
        path="/api/auth/refresh",
    )
    return TokenResponse(access_token=access_token)


class QrLoginRequest(BaseModel):
    token: str


def _consume_qr_token(db: Session, token: str) -> User:
    token_value = token.strip()
    if not token_value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="QR token required")

    user = db.query(User).filter(
        User.qr_login_token == token_value,
        User.is_active == True,
        User.is_deleted == False,
    ).first()
    if not user or user.role != "student":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid QR token")

    now = datetime.now(timezone.utc)
    if user.qr_login_expires_at and user.qr_login_expires_at <= now:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="QR token expired")

    user.qr_login_token = None
    user.qr_login_expires_at = None
    user.last_login = now
    db.commit()
    db.refresh(user)
    return user


@router.post("/qr", response_model=TokenResponse)
async def qr_login(
    request: QrLoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    user = _consume_qr_token(db, request.token)
    access_token = _issue_login_tokens(user, response)
    return TokenResponse(access_token=access_token)


@router.get("/qr-login/{token}")
async def qr_login_redirect(
    token: str,
    db: Session = Depends(get_db),
):
    user = _consume_qr_token(db, token)
    response = RedirectResponse(url="/student/overview")
    _issue_login_tokens(user, response)
    return response


class RefreshRequest(BaseModel):
    refresh_token: str | None = None


@router.post("/refresh")
async def refresh_tokens(
    request_body: RefreshRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    token = request_body.refresh_token or request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token required")

    payload = decode_refresh_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

    jti = payload.get("jti")
    if jti and is_blacklisted(db, jti):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revoked")

    user_id = payload.get("user_id")
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    if jti:
        blacklist_token(db, jti, user_id=str(user_id), expires_at=_refresh_expiry(payload))

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


@router.get("/saml/{tenant_key}/metadata")
async def saml_metadata(
    tenant_key: str,
    db: Session = Depends(get_db),
):
    tenant = get_tenant_for_saml(db, tenant_key)
    metadata = build_service_provider_metadata(tenant)
    return FastAPIResponse(content=metadata, media_type="application/samlmetadata+xml")


@router.get("/saml/{tenant_key}/login")
async def saml_login(
    tenant_key: str,
    request: Request,
    relay_state: str | None = None,
    db: Session = Depends(get_db),
):
    tenant = get_tenant_for_saml(db, tenant_key)
    redirect_url = saml_login_redirect(request, tenant, relay_state=relay_state)
    return RedirectResponse(redirect_url, status_code=302)


@router.post("/saml/{tenant_key}/acs", response_model=TokenResponse)
async def saml_acs(
    tenant_key: str,
    request: Request,
    response: Response,
    saml_response: str = Form(..., alias="SAMLResponse"),
    db: Session = Depends(get_db),
):
    tenant = get_tenant_for_saml(db, tenant_key)
    saml_identity = process_saml_acs(request, tenant, saml_response)
    user = create_or_update_saml_user(db, tenant, saml_identity)

    token_data = {
        "user_id": str(user.id),
        "tenant_id": str(user.tenant_id),
        "email": user.email,
        "role": user.role,
        "auth_provider": "saml",
    }
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    cookie_secure, cookie_samesite = _cookie_policy()
    response.set_cookie("access_token", access_token, httponly=True, secure=cookie_secure, samesite=cookie_samesite, max_age=3600)
    response.set_cookie(
        "refresh_token",
        refresh_token,
        httponly=True,
        secure=cookie_secure,
        samesite=cookie_samesite,
        max_age=7 * 24 * 3600,
        path="/api/auth/refresh",
    )
    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
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
async def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    token = request.cookies.get("refresh_token")
    if token:
        payload = decode_refresh_token(token)
        if payload and payload.get("jti"):
            blacklist_token(
                db,
                payload["jti"],
                user_id=str(payload.get("user_id") or ""),
                expires_at=_refresh_expiry(payload),
            )
    cookie_secure, cookie_samesite = _cookie_policy()
    response.delete_cookie("access_token", secure=cookie_secure, samesite=cookie_samesite)
    response.delete_cookie("refresh_token", path="/api/auth/refresh", secure=cookie_secure, samesite=cookie_samesite)
    return {"message": "Logged out", "success": True}


# ─── QR Code Auto-Login ─────────────────────────────────────

@router.get("/qr-login/{token}")
async def qr_login(
    token: str,
    response: Response,
    db: Session = Depends(get_db),
):
    """Auto-login via QR code token. Redirects to student dashboard on success."""
    if not token or len(token) < 10:
        raise HTTPException(status_code=400, detail="Invalid QR token")

    user = db.query(User).filter(
        User.qr_login_token == token,
        User.is_active == True,
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="Invalid or expired QR token")

    # Update last login
    user.last_login = datetime.now(timezone.utc)
    # Invalidate the token after first use for security
    user.qr_login_token = None
    db.commit()

    token_data = {
        "user_id": str(user.id),
        "tenant_id": str(user.tenant_id),
        "email": user.email,
        "role": user.role,
    }
    access_token = create_access_token(token_data)
    refresh_token_val = create_refresh_token(token_data)
    cookie_secure, cookie_samesite = _cookie_policy()

    response = RedirectResponse(url="/student/overview", status_code=302)
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
        value=refresh_token_val,
        httponly=True,
        secure=cookie_secure,
        samesite=cookie_samesite,
        max_age=7 * 24 * 3600,
        path="/api/auth/refresh",
    )
    return response
