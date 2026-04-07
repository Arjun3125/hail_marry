"""Phase 1 verification for fresh bootstrap migration + canonical demo seed."""

from __future__ import annotations

import os
import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ["DEBUG"] = "true"

import database
import db_migrate


def test_phase1_ensure_db_ready_seeds_unified_student_profile(tmp_path, monkeypatch):
    db_path = tmp_path / "phase1-fresh-seeded.sqlite3"
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
        from src.domains.academic.models.student_profile import StudentProfile
        from src.domains.identity.models.tenant import Tenant
        from src.domains.identity.models.user import User

        original_seed_demo_data = seed_cbse_demo.seed_demo_data

        def _offline_seed_demo_data(*, skip_embeddings: bool = True) -> bool:
            return original_seed_demo_data(skip_embeddings=True)

        monkeypatch.setattr(seed_cbse_demo, "seed_demo_data", _offline_seed_demo_data)

        assert db_migrate.ensure_db_ready() is True
        database.reset_database_state()

        db = SessionLocal()
        try:
            tenant = db.query(Tenant).filter(Tenant.name == seed_cbse_demo.TENANT_NAME).one()
            student = db.query(User).filter(User.email == seed_cbse_demo.DEMO_STUDENT_EMAIL).one()
            profile = db.query(StudentProfile).filter(
                StudentProfile.tenant_id == tenant.id,
                StudentProfile.user_id == student.id,
            ).one()

            assert profile.current_class_id is not None
            assert profile.primary_parent_id is not None
            assert profile.guardian_count >= 1
            assert profile.total_days > 0
            assert profile.present_days > 0
            assert profile.attendance_pct > 0
            assert profile.overall_score_pct is not None
            assert profile.strongest_subject is not None
            assert profile.weakest_subject is not None
            assert profile.subject_mastery_map
            assert profile.last_computed_at is not None
        finally:
            db.close()
    finally:
        database.reset_database_state()
