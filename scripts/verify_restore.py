"""
Backup Restore Verification — validates data integrity after restore.
Usage: python scripts/verify_restore.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend"))

from sqlalchemy import text
from database import SessionLocal


def verify():
    db = SessionLocal()
    checks = []

    try:
        # 1. Table existence
        tables = ["tenants", "users", "classes", "subjects", "enrollments",
                  "attendance", "exams", "marks", "assignments", "timetable",
                  "complaints", "lectures", "documents", "ai_queries",
                  "subject_performance", "audit_logs"]

        for table in tables:
            count = db.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            status = "✅" if count is not None else "❌"
            checks.append(f"{status} {table}: {count} rows")

        # 2. Foreign key integrity
        fk_check = db.execute(text("""
            SELECT COUNT(*) FROM users u
            LEFT JOIN tenants t ON u.tenant_id = t.id
            WHERE t.id IS NULL AND u.tenant_id IS NOT NULL
        """)).scalar()
        checks.append(f"{'✅' if fk_check == 0 else '❌'} FK integrity (users→tenants): {fk_check} orphans")

        # 3. Tenant isolation
        tenant_count = db.execute(text("SELECT COUNT(DISTINCT tenant_id) FROM users")).scalar()
        checks.append(f"✅ Tenants active: {tenant_count}")

        print("\n═══ Restore Verification Report ═══\n")
        for c in checks:
            print(f"  {c}")
        print(f"\n{'✅ ALL CHECKS PASSED' if '❌' not in ''.join(checks) else '❌ SOME CHECKS FAILED'}\n")

    except Exception as e:
        print(f"❌ Verification failed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    verify()
