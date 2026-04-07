"""Verification for six-month synthetic demo history across all core personas."""

from __future__ import annotations

import os
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ["DEBUG"] = "true"

import database
import db_migrate


def test_demo_seed_populates_six_month_persona_history(tmp_path, monkeypatch):
    db_path = tmp_path / "demo-persona-history.sqlite3"
    db_url = f"sqlite:///{db_path.as_posix()}"

    monkeypatch.chdir(BACKEND_DIR)
    monkeypatch.setenv("DATABASE_URL", db_url)
    monkeypatch.delenv("TEST_DATABASE_URL", raising=False)
    monkeypatch.setenv("TESTING", "false")
    monkeypatch.setenv("DEMO_MODE", "false")

    try:
        database._setup_compilers()
        database.reset_database_state()

        import seed_cbse_demo
        from database import SessionLocal
        from src.domains.academic.models.attendance import Attendance
        from src.domains.identity.models.tenant import Tenant
        from src.domains.identity.models.user import User
        from src.domains.platform.models.ai import AIQuery
        from src.domains.platform.models.audit import AuditLog
        from src.domains.platform.models.notification import Notification
        from src.domains.platform.models.study_session import StudySession
        from src.domains.platform.models.usage_counter import UsageCounter

        original_seed_demo_data = seed_cbse_demo.seed_demo_data

        def _offline_seed_demo_data(*, skip_embeddings: bool = True) -> bool:
            return original_seed_demo_data(skip_embeddings=True)

        monkeypatch.setattr(seed_cbse_demo, "seed_demo_data", _offline_seed_demo_data)

        assert db_migrate.ensure_db_ready() is True
        database.reset_database_state()

        now = datetime.now(UTC)
        db = SessionLocal()
        try:
            tenant = db.query(Tenant).filter(Tenant.name == seed_cbse_demo.TENANT_NAME).one()
            users = {
                user.email: user
                for user in db.query(User).filter(User.tenant_id == tenant.id).all()
            }

            student = users[seed_cbse_demo.DEMO_STUDENT_EMAIL]
            teacher = users[seed_cbse_demo.DEMO_TEACHER_EMAIL]
            admin = users[seed_cbse_demo.DEMO_ADMIN_EMAIL]
            parent = users[seed_cbse_demo.DEMO_PARENT_EMAIL]

            attendance_rows = db.query(Attendance).filter(
                Attendance.tenant_id == tenant.id,
                Attendance.student_id == student.id,
            ).all()
            assert len(attendance_rows) >= 140
            assert min(row.date for row in attendance_rows) <= (now.date() - timedelta(days=150))

            ai_counts = {
                "student": db.query(AIQuery).filter(AIQuery.tenant_id == tenant.id, AIQuery.user_id == student.id).count(),
                "teacher": db.query(AIQuery).filter(AIQuery.tenant_id == tenant.id, AIQuery.user_id == teacher.id).count(),
                "parent": db.query(AIQuery).filter(AIQuery.tenant_id == tenant.id, AIQuery.user_id == parent.id).count(),
                "admin": db.query(AIQuery).filter(AIQuery.tenant_id == tenant.id, AIQuery.user_id == admin.id).count(),
            }
            assert ai_counts["student"] >= 40
            assert ai_counts["teacher"] >= 6
            assert ai_counts["parent"] >= 6
            assert ai_counts["admin"] >= 6

            notification_counts = {
                "student": db.query(Notification).filter(Notification.tenant_id == tenant.id, Notification.user_id == student.id).count(),
                "teacher": db.query(Notification).filter(Notification.tenant_id == tenant.id, Notification.user_id == teacher.id).count(),
                "parent": db.query(Notification).filter(Notification.tenant_id == tenant.id, Notification.user_id == parent.id).count(),
                "admin": db.query(Notification).filter(Notification.tenant_id == tenant.id, Notification.user_id == admin.id).count(),
            }
            assert all(count >= 5 for count in notification_counts.values())

            audit_counts = {
                "student": db.query(AuditLog).filter(AuditLog.tenant_id == tenant.id, AuditLog.user_id == student.id).count(),
                "teacher": db.query(AuditLog).filter(AuditLog.tenant_id == tenant.id, AuditLog.user_id == teacher.id).count(),
                "parent": db.query(AuditLog).filter(AuditLog.tenant_id == tenant.id, AuditLog.user_id == parent.id).count(),
                "admin": db.query(AuditLog).filter(AuditLog.tenant_id == tenant.id, AuditLog.user_id == admin.id).count(),
            }
            assert all(count >= 5 for count in audit_counts.values())

            study_session_count = db.query(StudySession).filter(
                StudySession.tenant_id == tenant.id,
                StudySession.user_id == student.id,
            ).count()
            assert study_session_count >= 20

            user_counter_count = db.query(UsageCounter).filter(
                UsageCounter.tenant_id == tenant.id,
                UsageCounter.user_id.in_([student.id, teacher.id, parent.id, admin.id]),
                UsageCounter.bucket_type == "day",
            ).count()
            tenant_counter_count = db.query(UsageCounter).filter(
                UsageCounter.tenant_id == tenant.id,
                UsageCounter.user_id.is_(None),
                UsageCounter.scope == "tenant",
            ).count()
            assert user_counter_count >= 120
            assert tenant_counter_count >= 30
        finally:
            db.close()
    finally:
        database.reset_database_state()
