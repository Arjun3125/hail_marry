import sqlite3

DB_PATH = 'vidyaos_demo.db'
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

c.execute("SELECT id FROM tenants WHERE name='Modern Hustlers Academy'")
tid = c.fetchone()[0]

checks = [
    'users', 'classes', 'subjects', 'enrollments', 'timetable', 
    'attendance', 'exams', 'marks', 'lectures', 'assignments', 
    'assignment_submissions', 'subject_performance', 'notebooks', 
    'documents', 'ai_folders', 'ai_queries', 'topic_mastery', 
    'learner_profiles', 'study_path_plans', 'review_schedules', 
    'kg_concepts', 'kg_relationships', 'generated_content', 
    'usage_counters', 'test_series', 'mock_test_attempts', 'parent_links'
]

with open('test_output.log', 'w', encoding='utf-8') as f:
    for table in checks:
        try:
            c.execute(f"SELECT COUNT(*) FROM {table} WHERE tenant_id=?", (tid,))
            count = c.fetchone()[0]
            f.write(f"{table}: {count}\n")
        except Exception as e:
            f.write(f"{table}: ERROR {e}\n")
