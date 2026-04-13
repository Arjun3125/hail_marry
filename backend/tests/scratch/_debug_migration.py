"""Debug migration test failure."""
import os
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.DEBUG)

BACKEND_DIR = str(Path(__file__).resolve().parents[2])
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
os.chdir(BACKEND_DIR)

os.environ["TESTING"] = "false"

import database
import db_migrate

tmp = Path(__file__).parent / "_test_phase1.sqlite3"
db_url = f"sqlite:///{tmp.as_posix()}"
os.environ["DATABASE_URL"] = db_url

database._setup_compilers()
database.reset_database_state()

from database import Base, get_engine

engine = get_engine()
Base.metadata.create_all(bind=engine)

with engine.begin() as conn:
    conn.exec_driver_sql("DROP TABLE student_profiles")
    for col in ("assessment_kind", "grading_mode", "status", "opens_at", "closes_at", "published_at"):
        conn.exec_driver_sql(f"ALTER TABLE test_series DROP COLUMN {col}")
    conn.exec_driver_sql("CREATE TABLE IF NOT EXISTS alembic_version (version_num VARCHAR(32) NOT NULL)")
    conn.exec_driver_sql("DELETE FROM alembic_version")
    conn.exec_driver_sql("INSERT INTO alembic_version (version_num) VALUES ('20260331_0014')")

print("Fresh?", db_migrate._is_fresh_database())
try:
    from alembic import command
    alembic_cfg = db_migrate._get_alembic_config()
    command.upgrade(alembic_cfg, "head")
    print("UPGRADE SUCCEEDED")
except Exception as e:
    import traceback
    traceback.print_exc()
    print("UPGRADE FAILED:", e)

database.reset_database_state()
tmp.unlink(missing_ok=True)
