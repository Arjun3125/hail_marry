"""Demo login route — bypasses Google OAuth for development and demos."""
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from database import get_db
from auth.jwt import create_access_token
from auth.dependencies import is_demo_mode
from config import settings
from src.domains.identity.models.user import User
from src.domains.identity.schemas.auth import TokenResponse

router = APIRouter(prefix="/api/auth", tags=["Demo Auth"])


def _cookie_policy() -> tuple[bool, str]:
    app_env = (settings.app.env or "").lower()
    if app_env in {"production", "prod", "staging"}:
        return True, "none"
    return (not settings.app.debug), "lax"


@router.post("/demo-login", response_model=TokenResponse)
async def demo_login(
    data: dict,
    response: Response,
    db: Session = Depends(get_db),
):
    """
    Demo login: pick a role and login as a demo user.
    For development/demo only — disabled in production.
    """
    if not (settings.app.debug or is_demo_mode()):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    role = data.get("role", "student")
    email = data.get("email", "")

    # Prefer specific demo email if provided
    if email:
        user = db.query(User).filter(User.email == email, User.is_active).first()
    else:
        user = None

    # Prefer CBSE demo users (modernhustlers.com) for ALL roles
    cbse_demo_emails = {
        "student": "demo_cbse11@modernhustlers.com",
        "teacher": "teacher@modernhustlers.com",
        "admin": "admin@modernhustlers.com",
        "parent": "parent@modernhustlers.com",
    }
    if not user and role in cbse_demo_emails:
        user = db.query(User).filter(
            User.email == cbse_demo_emails[role], User.is_active
        ).first()

    # Fallback: any user with matching role
    if not user:
        user = db.query(User).filter(User.role == role, User.is_active).first()

    if not user:
        # Fallback: find any active user
        user = db.query(User).filter(User.is_active).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No users found in the database. Please run the seed script."
        )

    token_data = {
        "user_id": str(user.id),
        "tenant_id": str(user.tenant_id),
        "email": user.email,
        "role": user.role,
    }
    access_token = create_access_token(token_data)
    cookie_secure, cookie_samesite = _cookie_policy()

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=cookie_secure,
        samesite=cookie_samesite,
        max_age=3600,
    )

    return TokenResponse(access_token=access_token)
