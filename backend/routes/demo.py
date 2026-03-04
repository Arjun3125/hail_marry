"""Demo login route — bypasses Google OAuth for development and demos."""
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from database import get_db
from auth.jwt import create_access_token
from config import settings
from models.user import User
from schemas.auth import TokenResponse

router = APIRouter(prefix="/api/auth", tags=["Demo Auth"])


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

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=not settings.app.debug,
        samesite="lax",
        max_age=3600,
    )

    return TokenResponse(access_token=access_token)
