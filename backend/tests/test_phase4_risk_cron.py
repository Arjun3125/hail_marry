from __future__ import annotations

from datetime import datetime, timedelta, timezone
import uuid

import src.domains.academic.services.risk_cron as risk_cron
from src.domains.academic.models.student_profile import StudentProfile
from src.domains.academic.services.risk_cron import compute_student_risks
from src.domains.administrative.models.fee import FeeInvoice, FeeStructure
from src.domains.identity.models.tenant import Tenant
from src.domains.identity.models.user import User
from src.domains.identity.routes.auth import pwd_context
from src.domains.platform.models.analytics_event import AnalyticsEvent


def _student(*, tenant_id, email: str) -> User:
    return User(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        email=email,
        full_name="Risk Student",
        role="student",
        hashed_password=pwd_context.hash("pass123!"),
        is_active=True,
    )


class _SessionProxy:
    def __init__(self, session):
        self._session = session

    def __getattr__(self, name):
        return getattr(self._session, name)

    def close(self):
        return None


def test_compute_student_risks_updates_profile_and_persists_analytics_event(db_session, active_tenant, monkeypatch):
    monkeypatch.setattr(risk_cron, "SessionLocal", lambda: _SessionProxy(db_session))
    student = _student(tenant_id=active_tenant.id, email="risk-student@testschool.edu")
    fee_structure = FeeStructure(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        fee_type="tuition",
        amount=5000.0,
        frequency="monthly",
    )
    profile = StudentProfile(
        tenant_id=active_tenant.id,
        user_id=student.id,
        attendance_pct=52.0,
        absent_streak=5,
        overall_score_pct=38.0,
        current_streak_days=0,
        total_reviews_completed=0,
        last_review_at=datetime.now(timezone.utc) - timedelta(days=30),
    )
    db_session.add_all([student, fee_structure, profile])
    db_session.flush()
    db_session.add_all(
        [
            FeeInvoice(
                tenant_id=active_tenant.id,
                student_id=student.id,
                fee_structure_id=fee_structure.id,
                amount_due=5000.0,
                amount_paid=0.0,
                status="pending",
                due_date=datetime.now(timezone.utc) - timedelta(days=15),
            ),
            FeeInvoice(
                tenant_id=active_tenant.id,
                student_id=student.id,
                fee_structure_id=fee_structure.id,
                amount_due=6000.0,
                amount_paid=1000.0,
                status="partial",
                due_date=datetime.now(timezone.utc) - timedelta(days=8),
            ),
        ]
    )
    db_session.commit()

    updated = compute_student_risks(tenant_id=active_tenant.id)

    assert updated == 1
    db_session.refresh(profile)
    assert profile.dropout_risk == "high"
    assert profile.academic_risk == "high"
    assert profile.fee_risk == "high"
    assert profile.last_computed_at is not None

    events = (
        db_session.query(AnalyticsEvent)
        .filter(
            AnalyticsEvent.tenant_id == active_tenant.id,
            AnalyticsEvent.user_id == student.id,
            AnalyticsEvent.event_name == "student_risk_recomputed",
        )
        .all()
    )
    assert len(events) == 1
    payload = events[0].metadata_ or {}
    assert events[0].event_family == "risk"
    assert events[0].surface == "risk_cron"
    assert events[0].channel == "system"
    assert payload["changed"] is True
    assert payload["dropout_risk"] == "high"
    assert payload["academic_risk"] == "high"
    assert payload["fee_risk"] == "high"
    assert payload["overdue_invoice_count"] == 2
    assert payload["overdue_amount"] == 10000.0


def test_compute_student_risks_respects_tenant_filter(db_session, active_tenant, monkeypatch):
    monkeypatch.setattr(risk_cron, "SessionLocal", lambda: _SessionProxy(db_session))
    other_tenant = Tenant(id=uuid.uuid4(), name="Other School", domain="other-risk.edu")
    student = _student(tenant_id=active_tenant.id, email="tenant-a-risk@testschool.edu")
    other_student = _student(tenant_id=other_tenant.id, email="tenant-b-risk@testschool.edu")
    scoped_profile = StudentProfile(
        tenant_id=active_tenant.id,
        user_id=student.id,
        attendance_pct=74.0,
        absent_streak=3,
        overall_score_pct=58.0,
        current_streak_days=0,
        total_reviews_completed=0,
        last_review_at=datetime.now(timezone.utc) - timedelta(days=10),
    )
    unscoped_profile = StudentProfile(
        tenant_id=other_tenant.id,
        user_id=other_student.id,
        attendance_pct=40.0,
        absent_streak=7,
        overall_score_pct=32.0,
    )
    db_session.add_all([other_tenant, student, other_student, scoped_profile, unscoped_profile])
    db_session.commit()

    updated = compute_student_risks(tenant_id=active_tenant.id)

    assert updated == 1
    db_session.refresh(scoped_profile)
    db_session.refresh(unscoped_profile)
    assert scoped_profile.dropout_risk == "medium"
    assert scoped_profile.academic_risk == "medium"
    assert unscoped_profile.dropout_risk == "low"
    assert unscoped_profile.academic_risk == "low"
    assert unscoped_profile.last_computed_at is None

    scoped_events = (
        db_session.query(AnalyticsEvent)
        .filter(AnalyticsEvent.event_name == "student_risk_recomputed")
        .all()
    )
    assert len(scoped_events) == 1
    assert scoped_events[0].tenant_id == active_tenant.id
