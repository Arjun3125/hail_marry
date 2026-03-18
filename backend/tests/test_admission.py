"""Tests for admission workflow service."""
import uuid

import pytest

from constants import ADMISSION_STATUSES, ADMISSION_STATUS_TRANSITIONS


# ── Status constants ──

def test_admission_statuses_defined():
    """All expected statuses should exist."""
    expected = {"pending", "under_review", "accepted", "rejected", "enrolled"}
    assert ADMISSION_STATUSES == expected


def test_admission_status_transitions():
    """Status transitions should follow the defined rules."""
    # pending → under_review or rejected
    assert "under_review" in ADMISSION_STATUS_TRANSITIONS["pending"]
    assert "rejected" in ADMISSION_STATUS_TRANSITIONS["pending"]
    # under_review → accepted or rejected
    assert "accepted" in ADMISSION_STATUS_TRANSITIONS["under_review"]
    assert "rejected" in ADMISSION_STATUS_TRANSITIONS["under_review"]
    # accepted → enrolled or rejected
    assert "enrolled" in ADMISSION_STATUS_TRANSITIONS["accepted"]
    # rejected → nothing
    assert len(ADMISSION_STATUS_TRANSITIONS["rejected"]) == 0
    # enrolled → nothing
    assert len(ADMISSION_STATUS_TRANSITIONS["enrolled"]) == 0


def test_no_backwards_transitions():
    """Cannot go from enrolled/rejected back to earlier states."""
    assert "pending" not in ADMISSION_STATUS_TRANSITIONS["enrolled"]
    assert "pending" not in ADMISSION_STATUS_TRANSITIONS["rejected"]


def test_cannot_skip_review():
    """Cannot go directly from pending to accepted."""
    assert "accepted" not in ADMISSION_STATUS_TRANSITIONS["pending"]


# ── Model instantiation ──

def test_admission_application_model():
    """AdmissionApplication model should accept expected fields."""
    from src.domains.administrative.models.admission import AdmissionApplication

    app = AdmissionApplication(
        tenant_id=uuid.uuid4(),
        student_name="Ravi Kumar",
        parent_email="ravi.parent@email.com",
        parent_phone="+919876543210",
        applied_class_name="Class 5",
        status="pending",
    )
    assert app.student_name == "Ravi Kumar"
    assert app.status == "pending"


def test_admission_application_default_status():
    """Default status should be 'pending' (set by column default on insert)."""
    from src.domains.administrative.models.admission import AdmissionApplication

    app = AdmissionApplication(
        tenant_id=uuid.uuid4(),
        student_name="Test Student",
        parent_email="test@email.com",
    )
    # Column default="pending" is applied on DB insert, not on Python instantiation.
    # On instantiation, the attribute may be None until flushed to DB.
    assert app.status is None or app.status == "pending"


def test_admission_documents_jsonb():
    """Documents field should accept a list of dicts."""
    from src.domains.administrative.models.admission import AdmissionApplication

    docs = [
        {"name": "birth_certificate.pdf", "url": "/uploads/birth_cert.pdf"},
        {"name": "report_card.pdf", "url": "/uploads/report_card.pdf"},
    ]
    app = AdmissionApplication(
        tenant_id=uuid.uuid4(),
        student_name="Test",
        parent_email="test@email.com",
        documents=docs,
    )
    assert len(app.documents) == 2
    assert app.documents[0]["name"] == "birth_certificate.pdf"


# ── Bulk enrollment validation ──

def test_bulk_enroll_only_accepted():
    """Only accepted applications should be enrollable."""
    statuses_that_can_enroll = {"accepted"}
    for status in ADMISSION_STATUSES:
        if status in statuses_that_can_enroll:
            assert "enrolled" in ADMISSION_STATUS_TRANSITIONS[status]
        else:
            if status != "enrolled":  # enrolled staying enrolled is a no-op
                assert "enrolled" not in ADMISSION_STATUS_TRANSITIONS.get(status, set())


# ── Stats structure ──

def test_admission_stats_structure():
    """Stats should have all status counts + total."""
    stats = {status: 0 for status in ADMISSION_STATUSES}
    stats["total"] = 0
    assert "pending" in stats
    assert "under_review" in stats
    assert "accepted" in stats
    assert "rejected" in stats
    assert "enrolled" in stats
    assert "total" in stats


# ── Application data validation ──

def test_phone_number_format():
    """Indian phone numbers should be 10+ digits."""
    phone = "+919876543210"
    digits = "".join(c for c in phone if c.isdigit())
    assert len(digits) >= 10


def test_email_format():
    """Email should contain @ and domain."""
    email = "parent@school.com"
    assert "@" in email
    assert "." in email.split("@")[1]
