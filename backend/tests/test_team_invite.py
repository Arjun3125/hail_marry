"""Tests for self-service team invitation."""
import uuid
import pytest
from services.team_invite import (
    INVITE_EXPIRY_HOURS, accept_invitation, create_invitation,
    list_invitations, revoke_invitation, validate_invitation,
)


def test_invite_expiry():
    assert INVITE_EXPIRY_HOURS == 72


def test_create_invitation():
    tid = uuid.uuid4()
    inv = create_invitation(tid, "teacher@school.com", "teacher")
    assert inv["email"] == "teacher@school.com"
    assert inv["role"] == "teacher"
    assert inv["status"] == "pending"
    assert "token" in inv


def test_validate_invitation():
    tid = uuid.uuid4()
    inv = create_invitation(tid, "test@school.com")
    result = validate_invitation(inv["token"])
    assert result["valid"] is True
    assert result["email"] == "test@school.com"


def test_validate_nonexistent():
    result = validate_invitation("fake-token")
    assert result["valid"] is False


def test_accept_invitation():
    tid = uuid.uuid4()
    inv = create_invitation(tid, "accept@school.com")
    result = accept_invitation(inv["token"])
    assert result["accepted"] is True


def test_accept_already_used():
    tid = uuid.uuid4()
    inv = create_invitation(tid, "double@school.com")
    accept_invitation(inv["token"])
    result = accept_invitation(inv["token"])
    assert result.get("valid") is False


def test_revoke_invitation():
    tid = uuid.uuid4()
    inv = create_invitation(tid, "revoke@school.com")
    assert revoke_invitation(inv["token"]) is True


def test_revoke_already_accepted():
    tid = uuid.uuid4()
    inv = create_invitation(tid, "used@school.com")
    accept_invitation(inv["token"])
    assert revoke_invitation(inv["token"]) is False


def test_list_invitations():
    tid = uuid.uuid4()
    create_invitation(tid, "a@school.com")
    create_invitation(tid, "b@school.com")
    invs = list_invitations(tid)
    assert len(invs) >= 2
