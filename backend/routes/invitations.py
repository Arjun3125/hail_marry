"""Team invitation API routes — invite, accept, revoke, list."""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from uuid import UUID

from auth.dependencies import require_role
from database import get_db
from services.team_invite import (
    accept_invitation, create_invitation, list_invitations, revoke_invitation, validate_invitation,
)

router = APIRouter(prefix="/api/invitations", tags=["Team Invitations"])


class InviteRequest(BaseModel):
    email: str
    role: str = "teacher"
    message: str = ""


@router.post("/send")
def send_invite(body: InviteRequest, user=Depends(require_role("admin")), db: Session = Depends(get_db)):
    """Send an invitation email. Admin only."""
    inv = create_invitation(user.tenant_id, body.email, body.role, user.id, body.message)
    return {"invite_url": inv["invite_url"], "token": inv["token"], "expires_at": inv["expires_at"]}


@router.get("/validate/{token}")
def validate(token: str):
    """Validate an invitation token. Public endpoint."""
    result = validate_invitation(token)
    if not result["valid"]:
        raise HTTPException(400, result["error"])
    return result


@router.post("/accept/{token}")
def accept(token: str):
    """Accept an invitation. Public endpoint."""
    result = accept_invitation(token)
    if not result.get("accepted"):
        raise HTTPException(400, result.get("error", "Invalid invitation"))
    return result


@router.delete("/revoke/{token}")
def revoke(token: str, user=Depends(require_role("admin"))):
    """Revoke a pending invitation. Admin only."""
    if not revoke_invitation(token):
        raise HTTPException(400, "Cannot revoke (already used or not found)")
    return {"revoked": True}


@router.get("/")
def list_all(status: str = Query(""), user=Depends(require_role("admin")), db: Session = Depends(get_db)):
    """List invitations. Admin only."""
    return {"invitations": list_invitations(user.tenant_id, status)}
