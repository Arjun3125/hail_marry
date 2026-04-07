"""Phase 1 migration rollout verification against an existing database."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from sqlalchemy import inspect


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ["DEBUG"] = "true"

import database
import db_migrate


def test_phase1_run_migrations_upgrades_existing_schema(tmp_path, monkeypatch):
    db_path = tmp_path / "phase1-existing.sqlite3"
    db_url = f"sqlite:///{db_path.as_posix()}"

    monkeypatch.chdir(BACKEND_DIR)
    monkeypatch.setenv("DATABASE_URL", db_url)
    monkeypatch.delenv("TEST_DATABASE_URL", raising=False)
    monkeypatch.setenv("TESTING", "false")

    try:
        database._setup_compilers()
        database.reset_database_state()

        import models  # noqa: F401
        from database import Base, get_engine

        engine = get_engine()
        Base.metadata.create_all(bind=engine)
        with engine.begin() as conn:
            conn.exec_driver_sql("DROP TABLE student_profiles")
            for column_name in (
                "assessment_kind",
                "grading_mode",
                "status",
                "opens_at",
                "closes_at",
                "published_at",
            ):
                conn.exec_driver_sql(f"ALTER TABLE test_series DROP COLUMN {column_name}")
            conn.exec_driver_sql(
                "CREATE TABLE IF NOT EXISTS alembic_version (version_num VARCHAR(32) NOT NULL)"
            )
            conn.exec_driver_sql("DELETE FROM alembic_version")
            conn.exec_driver_sql(
                "INSERT INTO alembic_version (version_num) VALUES ('20260331_0014')"
            )

        inspector = inspect(engine)
        assert "student_profiles" not in inspector.get_table_names()
        test_series_columns_before = {column["name"] for column in inspector.get_columns("test_series")}
        assert "assessment_kind" not in test_series_columns_before
        assert db_migrate._is_fresh_database() is False

        assert db_migrate.run_migrations() is True
        database.reset_database_state()

        upgraded_engine = database.get_engine()
        inspector = inspect(upgraded_engine)
        assert "student_profiles" in inspector.get_table_names()

        student_profile_columns = {column["name"] for column in inspector.get_columns("student_profiles")}
        assert {
            "tenant_id",
            "user_id",
            "current_class_id",
            "current_batch_id",
            "primary_parent_id",
            "guardian_count",
            "total_days",
            "present_days",
            "attendance_pct",
            "absent_streak",
            "overall_score_pct",
            "strongest_subject",
            "weakest_subject",
            "subject_mastery_map",
        }.issubset(student_profile_columns)

        test_series_columns_after = {column["name"] for column in inspector.get_columns("test_series")}
        assert {
            "assessment_kind",
            "grading_mode",
            "status",
            "opens_at",
            "closes_at",
            "published_at",
        }.issubset(test_series_columns_after)
    finally:
        database.reset_database_state()
