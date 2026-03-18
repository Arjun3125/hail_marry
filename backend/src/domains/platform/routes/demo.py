"""Demo login route — bypasses Google OAuth for development and demos."""
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from database import get_db
from auth.jwt import create_access_token
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
    if not settings.app.debug:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    role = data.get("role", "student")

    # Find a user with this role
    user = db.query(User).filter(User.role == role, User.is_active == True).first()

    if not user:
        # Fallback: find any active user
        user = db.query(User).filter(User.is_active == True).first()

    if not user:
        return {"error": "No users found. Run seed.py first."}

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
