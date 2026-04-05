"""Self-service team invitation — invite-by-email flow.

Admin can invite teachers/staff via email. Invitees receive a
tokenized signup link that pre-assigns their role and tenant.
"""
import hashlib
import os
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4


# In-memory invitation store (swap with DB in production)
_invitations: dict[str, dict] = {}

INVITE_EXPIRY_HOURS = 72
INVITE_BASE_URL = os.getenv("INVITE_BASE_URL", "http://localhost:3000/accept-invite")


def create_invitation(
    tenant_id: UUID,
    email: str,
    role: str = "teacher",
    invited_by: UUID = None,
    custom_message: str = "",
) -> dict:
    """Create an invitation token for a new team member."""
    token = hashlib.sha256(f"{email}-{uuid4().hex}".encode()).hexdigest()[:32]
    expires = datetime.now(timezone.utc) + timedelta(hours=INVITE_EXPIRY_HOURS)

    invitation = {
        "token": token,
        "tenant_id": str(tenant_id),
        "email": email,
        "role": role,
        "invited_by": str(invited_by) if invited_by else None,
        "custom_message": custom_message,
        "status": "pending",  # pending, accepted, expired, revoked
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": expires.isoformat(),
        "invite_url": f"{INVITE_BASE_URL}?token={token}",
    }
    _invitations[token] = invitation
    return invitation


def validate_invitation(token: str) -> dict:
    """Validate an invitation token."""
    inv = _invitations.get(token)
    if not inv:
        return {"valid": False, "error": "Invitation not found"}

    if inv["status"] != "pending":
        return {"valid": False, "error": f"Invitation already {inv['status']}"}

    expires = datetime.fromisoformat(inv["expires_at"])
    if datetime.now(timezone.utc) > expires:
        inv["status"] = "expired"
        return {"valid": False, "error": "Invitation has expired"}

    return {
        "valid": True,
        "email": inv["email"],
        "role": inv["role"],
        "tenant_id": inv["tenant_id"],
    }


def accept_invitation(token: str) -> dict:
    """Accept an invitation and mark it as used."""
    validation = validate_invitation(token)
    if not validation["valid"]:
        return validation

    inv = _invitations[token]
    inv["status"] = "accepted"
    inv["accepted_at"] = datetime.now(timezone.utc).isoformat()

    return {
        "accepted": True,
        "email": inv["email"],
        "role": inv["role"],
        "tenant_id": inv["tenant_id"],
    }


def revoke_invitation(token: str) -> bool:
    """Revoke a pending invitation."""
    inv = _invitations.get(token)
    if inv and inv["status"] == "pending":
        inv["status"] = "revoked"
        return True
    return False


def list_invitations(tenant_id: UUID, status_filter: str = "") -> list[dict]:
    """List all invitations for a tenant."""
    results = []
    for inv in _invitations.values():
        if inv["tenant_id"] == str(tenant_id):
            if not status_filter or inv["status"] == status_filter:
                results.append({
                    "email": inv["email"],
                    "role": inv["role"],
                    "status": inv["status"],
                    "created_at": inv["created_at"],
                    "invite_url": inv["invite_url"],
                })
    return results
