"""Verify all 20 models are populated for the CBSE demo."""
import sqlite3, json, sys
from pathlib import Path

DB_PATH = "vidyaos_demo.db"
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

print("=" * 60)
print("  VidyaOS CBSE Demo — Full Verification")
print("=" * 60)

# Find tenant
c.execute("SELECT id, name FROM tenants WHERE name='Modern Hustlers Academy'")
row = c.fetchone()
if not row:
    print("❌ ERROR: Tenant 'Modern Hustlers Academy' not found!")
    sys.exit(1)
tid = row[0]
print(f"\n✓ Tenant: {row[1]} ({tid})")

# Model checks
checks = [
    ("users", "Users"),
    ("classes", "Classes"),
    ("subjects", "Subjects"),
    ("enrollments", "Enrollments"),
    ("timetable", "Timetable"),
    ("attendance", "Attendance"),
    ("exams", "Exams"),
    ("marks", "Marks"),
    ("lectures", "Lectures"),
    ("assignments", "Assignments"),
    ("assignment_submissions", "Submissions"),
    ("subject_performance", "SubjectPerformance"),
    ("notebooks", "Notebooks"),
    ("documents", "Documents"),
    ("ai_folders", "AI Folders"),
    ("ai_queries", "AI Queries"),
    ("topic_mastery", "TopicMastery"),
    ("learner_profiles", "LearnerProfile"),
    ("study_path_plans", "StudyPathPlans"),
    ("review_schedules", "ReviewSchedules"),
    ("kg_concepts", "KG Concepts"),
    ("kg_relationships", "KG Relations"),
    ("generated_content", "GeneratedContent"),
    ("usage_counters", "UsageCounters"),
    ("test_series", "TestSeries"),
    ("mock_test_attempts", "MockTestAttempts"),
    ("parent_links", "ParentLinks"),
]

print(f"\n{'Table':<25} {'Count':>8}  Status")
print("-" * 50)
failures = 0
for table, label in checks:
    try:
        c.execute(f"SELECT COUNT(*) FROM {table} WHERE tenant_id=?", (tid,))
        count = c.fetchone()[0]
        status = "✓" if count > 0 else "❌ EMPTY"
        if count == 0:
            failures += 1
        print(f"  {label:<23} {count:>6}  {status}")
    except Exception as e:
        print(f"  {label:<23}     --  ⚠ {e}")
        failures += 1

# FAISS check
print(f"\n{'─' * 50}")
print("FAISS Vector Store:")
vs_dir = Path("../vector_store")
found_vs = False
if vs_dir.exists():
    for mf in vs_dir.glob("*.meta.json"):
        with open(mf) as f:
            data = json.load(f)
        print(f"  {mf.name}: {len(data)} chunks ✓")
        found_vs = True
if not found_vs:
    print("  ❌ No FAISS index files found!")
    failures += 1

# User details
print(f"\n{'─' * 50}")
print("Users:")
c.execute("SELECT full_name, email, role FROM users WHERE tenant_id=?", (tid,))
for r in c.fetchall():
    print(f"  {r[2]:8s} | {r[0]} | {r[1]}")

# AI history modes
c.execute("SELECT DISTINCT mode FROM ai_queries WHERE tenant_id=?", (tid,))
modes = [r[0] for r in c.fetchall()]
print(f"\nAI Modes Used: {modes}")

conn.close()
print(f"\n{'=' * 60}")
if failures == 0:
    print("  🎉 ALL CHECKS PASSED!")
else:
    print(f"  ⚠ {failures} check(s) failed — review above")
print("=" * 60)
sys.exit(1 if failures else 0)
