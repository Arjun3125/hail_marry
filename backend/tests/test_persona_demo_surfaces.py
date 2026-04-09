from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta, time

from src.domains.identity.routes.auth import pwd_context


def _login(client, email: str) -> str:
    response = client.post("/api/auth/login", json={"email": email, "password": "pass123!"})
    token = response.json().get("access_token")
    assert token, response.text
    return token


def test_student_history_routes_return_enriched_demo_payloads(client, db_session, active_tenant):
    from src.domains.academic.models.assignment import Assignment, AssignmentSubmission
    from src.domains.academic.models.attendance import Attendance
    from src.domains.academic.models.core import Class, Enrollment, Subject
    from src.domains.identity.models.user import User
    from src.domains.platform.models.ai import AIQuery
    from src.domains.platform.models.document import Document
    from src.domains.platform.models.generated_content import GeneratedContent
    from src.domains.platform.models.notebook import Notebook
    from src.domains.platform.models.spaced_repetition import ReviewSchedule
    from src.domains.platform.models.study_session import StudySession

    now = datetime.now(UTC)
    student = User(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        email="student-demo@testschool.edu",
        full_name="Student Demo",
        role="student",
        hashed_password=pwd_context.hash("pass123!"),
        is_active=True,
    )
    teacher = User(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        email="teacher-demo@testschool.edu",
        full_name="Teacher Demo",
        role="teacher",
        hashed_password=pwd_context.hash("pass123!"),
        is_active=True,
    )
    db_session.add_all([student, teacher])
    db_session.flush()

    cls = Class(id=uuid.uuid4(), tenant_id=active_tenant.id, name="Class 11 A", grade_level="11", academic_year="2026-27")
    subject = Subject(id=uuid.uuid4(), tenant_id=active_tenant.id, class_id=cls.id, name="Physics")
    notebook = Notebook(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        user_id=student.id,
        name="Physics Notebook",
        subject="Physics",
        color="#2563eb",
        icon="Book",
        created_at=now - timedelta(days=150),
        updated_at=now - timedelta(days=30),
    )
    db_session.add_all([cls, subject, notebook])
    db_session.flush()

    db_session.add(Enrollment(tenant_id=active_tenant.id, student_id=student.id, class_id=cls.id, roll_number="11", academic_year="2026-27"))
    db_session.add_all([
        Document(
            id=uuid.uuid4(),
            tenant_id=active_tenant.id,
            subject_id=subject.id,
            notebook_id=notebook.id,
            uploaded_by=student.id,
            file_name="Projectile Motion Notes.pdf",
            file_type="pdf",
            ingestion_status="completed",
            chunk_count=8,
            created_at=now - timedelta(days=160),
        ),
        Document(
            id=uuid.uuid4(),
            tenant_id=active_tenant.id,
            subject_id=subject.id,
            notebook_id=notebook.id,
            uploaded_by=student.id,
            file_name="Lab Scan.jpg",
            file_type="jpg",
            ingestion_status="processing",
            chunk_count=0,
            created_at=now - timedelta(days=14),
        ),
    ])

    assignment = Assignment(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        subject_id=subject.id,
        title="Kinematics Worksheet",
        description="Solve all numericals",
        created_by=teacher.id,
        due_date=now - timedelta(days=6),
        created_at=now - timedelta(days=10),
    )
    db_session.add(assignment)
    db_session.flush()
    db_session.add(AssignmentSubmission(
        tenant_id=active_tenant.id,
        assignment_id=assignment.id,
        student_id=student.id,
        submitted_at=now - timedelta(days=7),
        grade=84,
        feedback="Solid work",
    ))
    db_session.add_all([
        Attendance(tenant_id=active_tenant.id, student_id=student.id, class_id=cls.id, date=(now - timedelta(days=5)).date(), status="present"),
        Attendance(tenant_id=active_tenant.id, student_id=student.id, class_id=cls.id, date=(now - timedelta(days=4)).date(), status="late"),
        Attendance(tenant_id=active_tenant.id, student_id=student.id, class_id=cls.id, date=(now - timedelta(days=3)).date(), status="present"),
        StudySession(
            tenant_id=active_tenant.id,
            user_id=student.id,
            topic="Projectile Motion",
            duration_seconds=1800,
            questions_answered=12,
            created_at=now - timedelta(days=12),
            updated_at=now - timedelta(days=12),
            last_active_at=now - timedelta(days=12),
        ),
        AIQuery(
            tenant_id=active_tenant.id,
            user_id=student.id,
            notebook_id=notebook.id,
            query_text="Explain projectile motion",
            mode="qa",
            response_text="response",
            token_usage=420,
            created_at=now - timedelta(days=9),
        ),
        ReviewSchedule(
            tenant_id=active_tenant.id,
            student_id=student.id,
            subject_id=subject.id,
            topic="Kinematics",
            next_review_at=now + timedelta(days=2),
            interval_days=7,
            ease_factor=2.5,
            review_count=3,
            created_at=now - timedelta(days=90),
            updated_at=now - timedelta(days=2),
        ),
        GeneratedContent(
            id=uuid.uuid4(),
            tenant_id=active_tenant.id,
            notebook_id=notebook.id,
            user_id=student.id,
            type="audio_overview",
            title="Kinematics Audio Overview",
            content={
                "title": "Kinematics Audio Overview",
                "duration_estimate": "5 min",
                "dialogue": [{"speaker": "Anika", "text": "Start with distance versus displacement."}],
            },
            source_query="Generate audio overview for kinematics",
            created_at=now - timedelta(days=20),
            updated_at=now - timedelta(days=20),
        ),
    ])
    db_session.commit()

    token = _login(client, student.email)
    headers = {"Authorization": f"Bearer {token}"}

    uploads_response = client.get("/api/student/uploads", headers=headers)
    assert uploads_response.status_code == 200
    uploads_payload = uploads_response.json()
    assert uploads_payload["summary"]["total_uploads"] == 2
    assert uploads_payload["summary"]["completed_ingestions"] == 1
    assert len(uploads_payload["monthly_activity"]) == 6
    assert any(item["type"] == "pdf" for item in uploads_payload["file_types"])

    profile_response = client.get("/api/student/profile-summary", headers=headers)
    assert profile_response.status_code == 200
    profile_payload = profile_response.json()
    assert profile_payload["uploads"] == 2
    assert profile_payload["assignments_submitted"] == 1
    assert profile_payload["study_sessions"] == 1
    assert profile_payload["ai_requests"] == 1
    assert profile_payload["attendance_average"] > 0
    assert profile_payload["latest_milestones"]["last_generated_artifact_at"] is not None

    history_response = client.get("/api/student/study-tools/history?tool=audio_overview", headers=headers)
    assert history_response.status_code == 200
    history_payload = history_response.json()
    assert history_payload["count"] == 1
    assert history_payload["items"][0]["content"]["dialogue"][0]["speaker"] == "Anika"


def test_teacher_history_routes_return_seed_ready_payloads(client, db_session, active_tenant):
    from src.domains.academic.models.assignment import Assignment
    from src.domains.academic.models.core import Class, Enrollment, Subject
    from src.domains.academic.models.lecture import Lecture
    from src.domains.academic.models.timetable import Timetable
    from src.domains.identity.models.user import User
    from src.domains.platform.models.ai import AIQuery
    from src.domains.platform.models.document import Document

    now = datetime.now(UTC)
    teacher = User(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        email="teacher-history@testschool.edu",
        full_name="Teacher History",
        role="teacher",
        hashed_password=pwd_context.hash("pass123!"),
        is_active=True,
    )
    student_one = User(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        email="student-one@testschool.edu",
        full_name="Student One",
        role="student",
        hashed_password=pwd_context.hash("pass123!"),
        is_active=True,
    )
    student_two = User(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        email="student-two@testschool.edu",
        full_name="Student Two",
        role="student",
        hashed_password=pwd_context.hash("pass123!"),
        is_active=True,
    )
    db_session.add_all([teacher, student_one, student_two])
    db_session.flush()

    cls = Class(id=uuid.uuid4(), tenant_id=active_tenant.id, name="Class 11 B", grade_level="11", academic_year="2026-27")
    subject = Subject(id=uuid.uuid4(), tenant_id=active_tenant.id, class_id=cls.id, name="Chemistry")
    db_session.add_all([cls, subject])
    db_session.flush()

    db_session.add_all([
        Enrollment(tenant_id=active_tenant.id, student_id=student_one.id, class_id=cls.id, roll_number="21", academic_year="2026-27"),
        Enrollment(tenant_id=active_tenant.id, student_id=student_two.id, class_id=cls.id, roll_number="22", academic_year="2026-27"),
        Timetable(
            tenant_id=active_tenant.id,
            class_id=cls.id,
            subject_id=subject.id,
            teacher_id=teacher.id,
            day_of_week=1,
            start_time=time(9, 0),
            end_time=time(9, 45),
            room_number="Lab 1",
        ),
        Document(
            id=uuid.uuid4(),
            tenant_id=active_tenant.id,
            subject_id=subject.id,
            uploaded_by=teacher.id,
            file_name="Organic Naming Slides.pptx",
            file_type="pptx",
            ingestion_status="completed",
            chunk_count=6,
            created_at=now - timedelta(days=30),
        ),
        Lecture(
            id=uuid.uuid4(),
            tenant_id=active_tenant.id,
            subject_id=subject.id,
            class_id=cls.id,
            teacher_id=teacher.id,
            title="Organic Chemistry Walkthrough",
            scheduled_at=now - timedelta(days=18),
            duration_minutes=45,
            transcript_ingested=True,
            created_at=now - timedelta(days=18),
        ),
        Assignment(
            id=uuid.uuid4(),
            tenant_id=active_tenant.id,
            subject_id=subject.id,
            title="Functional Group Worksheet",
            description="Practice set",
            created_by=teacher.id,
            due_date=now - timedelta(days=8),
            created_at=now - timedelta(days=14),
        ),
        AIQuery(
            tenant_id=active_tenant.id,
            user_id=teacher.id,
            query_text="Summarize common organic chemistry errors",
            mode="qa",
            response_text="response",
            token_usage=510,
            created_at=now - timedelta(days=11),
        ),
    ])
    db_session.commit()

    token = _login(client, teacher.email)
    headers = {"Authorization": f"Bearer {token}"}

    history_response = client.get("/api/teacher/resource-history", headers=headers)
    assert history_response.status_code == 200
    history_payload = history_response.json()
    assert history_payload["summary"]["documents"] == 1
    assert history_payload["summary"]["lectures"] == 1
    assert history_payload["summary"]["indexed_chunks"] == 6
    assert len(history_payload["recent_activity"]) == 2

    profile_response = client.get("/api/teacher/profile-summary", headers=headers)
    assert profile_response.status_code == 200
    profile_payload = profile_response.json()
    assert profile_payload["classes_in_scope"] == 1
    assert profile_payload["students_supported"] == 2
    assert profile_payload["documents_uploaded"] == 1
    assert profile_payload["lectures_indexed"] == 1
    assert profile_payload["assignments_created"] == 1
    assert profile_payload["ai_requests"] == 1


def test_parent_routes_return_enriched_family_history(client, db_session, active_tenant):
    from src.domains.academic.models.assignment import Assignment, AssignmentSubmission
    from src.domains.academic.models.attendance import Attendance
    from src.domains.academic.models.core import Class, Enrollment, Subject
    from src.domains.academic.models.marks import Exam, Mark
    from src.domains.academic.models.parent_link import ParentLink
    from src.domains.identity.models.user import User
    from src.domains.platform.models.ai import AIQuery
    from src.domains.platform.models.generated_content import GeneratedContent
    from src.domains.platform.models.notebook import Notebook
    from src.domains.platform.models.study_session import StudySession

    now = datetime.now(UTC)
    parent = User(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        email="parent-demo@testschool.edu",
        full_name="Parent Demo",
        role="parent",
        hashed_password=pwd_context.hash("pass123!"),
        is_active=True,
    )
    student = User(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        email="student-family@testschool.edu",
        full_name="Student Family",
        role="student",
        hashed_password=pwd_context.hash("pass123!"),
        is_active=True,
    )
    teacher = User(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        email="teacher-family@testschool.edu",
        full_name="Teacher Family",
        role="teacher",
        hashed_password=pwd_context.hash("pass123!"),
        is_active=True,
    )
    db_session.add_all([parent, student, teacher])
    db_session.flush()

    school_class = Class(id=uuid.uuid4(), tenant_id=active_tenant.id, name="Class 9 A", grade_level="9", academic_year="2026-27")
    subject = Subject(id=uuid.uuid4(), tenant_id=active_tenant.id, class_id=school_class.id, name="Mathematics")
    notebook = Notebook(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        user_id=student.id,
        name="Math Notebook",
        subject="Mathematics",
        color="#14b8a6",
        icon="BookOpen",
        created_at=now - timedelta(days=160),
        updated_at=now - timedelta(days=10),
    )
    db_session.add_all([school_class, subject, notebook])
    db_session.flush()

    exam = Exam(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        name="Monthly Test",
        subject_id=subject.id,
        max_marks=100,
        exam_date=(now - timedelta(days=21)).date(),
        created_at=now - timedelta(days=21),
    )
    assignment = Assignment(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        subject_id=subject.id,
        title="Algebra Worksheet",
        description="Solve equations",
        created_by=teacher.id,
        due_date=now - timedelta(days=15),
        created_at=now - timedelta(days=20),
    )
    db_session.add_all([
        ParentLink(tenant_id=active_tenant.id, parent_id=parent.id, child_id=student.id),
        Enrollment(tenant_id=active_tenant.id, student_id=student.id, class_id=school_class.id, roll_number="8", academic_year="2026-27"),
        exam,
        assignment,
    ])
    db_session.flush()
    db_session.add_all([
        Mark(tenant_id=active_tenant.id, student_id=student.id, exam_id=exam.id, marks_obtained=88, created_at=now - timedelta(days=20)),
        AssignmentSubmission(
            tenant_id=active_tenant.id,
            assignment_id=assignment.id,
            student_id=student.id,
            submitted_at=now - timedelta(days=14),
            grade=86,
            feedback="Well done",
        ),
        Attendance(tenant_id=active_tenant.id, student_id=student.id, class_id=school_class.id, date=(now - timedelta(days=25)).date(), status="present"),
        Attendance(tenant_id=active_tenant.id, student_id=student.id, class_id=school_class.id, date=(now - timedelta(days=24)).date(), status="absent"),
        Attendance(tenant_id=active_tenant.id, student_id=student.id, class_id=school_class.id, date=(now - timedelta(days=23)).date(), status="present"),
        StudySession(
            tenant_id=active_tenant.id,
            user_id=student.id,
            topic="Linear Equations",
            duration_seconds=1500,
            questions_answered=9,
            created_at=now - timedelta(days=18),
            updated_at=now - timedelta(days=18),
            last_active_at=now - timedelta(days=18),
        ),
        AIQuery(
            tenant_id=active_tenant.id,
            user_id=student.id,
            notebook_id=notebook.id,
            query_text="Explain factorization",
            mode="qa",
            response_text="response",
            token_usage=380,
            created_at=now - timedelta(days=17),
        ),
        GeneratedContent(
            id=uuid.uuid4(),
            tenant_id=active_tenant.id,
            notebook_id=notebook.id,
            user_id=student.id,
            type="mind_map",
            title="Factorization Map",
            content={"label": "Factorization", "children": []},
            source_query="Build a factorization map",
            created_at=now - timedelta(days=16),
            updated_at=now - timedelta(days=16),
        ),
    ])
    db_session.commit()

    token = _login(client, parent.email)
    headers = {"Authorization": f"Bearer {token}"}

    dashboard_response = client.get("/api/parent/dashboard", headers=headers)
    assert dashboard_response.status_code == 200
    dashboard_payload = dashboard_response.json()
    assert dashboard_payload["summary"]["assignments_submitted"] == 1
    assert dashboard_payload["summary"]["ai_requests"] == 1
    assert len(dashboard_payload["monthly_attendance"]) == 6
    assert dashboard_payload["summary"]["recent_generated_tools"][0]["type"] == "mind_map"

    results_response = client.get("/api/parent/results", headers=headers)
    assert results_response.status_code == 200
    results_payload = results_response.json()
    assert results_payload["summary"]["subjects"] == 1
    assert len(results_payload["monthly_trend"]) == 6
    assert results_payload["recent_exams"][0]["subject"] == "Mathematics"

    reports_response = client.get("/api/parent/reports", headers=headers)
    assert reports_response.status_code == 200
    reports_payload = reports_response.json()
    assert reports_payload["six_month_overview"]["assignments_submitted"] == 1
    assert reports_payload["six_month_overview"]["generated_tools"] == 1
    assert len(reports_payload["monthly_snapshots"]) == 6


def test_admin_routes_return_enriched_demo_history(client, db_session, active_tenant):
    from src.domains.academic.models.attendance import Attendance
    from src.domains.academic.models.core import Class, Subject
    from src.domains.academic.models.marks import Exam, Mark
    from src.domains.administrative.models.complaint import Complaint
    from src.domains.identity.models.user import User
    from src.domains.platform.models.ai import AIQuery

    now = datetime.now(UTC)
    admin = User(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        email="admin-demo@testschool.edu",
        full_name="Admin Demo",
        role="admin",
        hashed_password=pwd_context.hash("pass123!"),
        is_active=True,
    )
    parent = User(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        email="parent-demo-admin@testschool.edu",
        full_name="Parent Admin Demo",
        role="parent",
        hashed_password=pwd_context.hash("pass123!"),
        is_active=True,
    )
    student = User(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        email="student-demo-admin@testschool.edu",
        full_name="Student Admin Demo",
        role="student",
        hashed_password=pwd_context.hash("pass123!"),
        is_active=True,
    )
    school_class = Class(id=uuid.uuid4(), tenant_id=active_tenant.id, name="Class 8 B", grade_level="8", academic_year="2026-27")
    subject = Subject(id=uuid.uuid4(), tenant_id=active_tenant.id, class_id=school_class.id, name="Science")
    db_session.add_all([admin, parent, student, school_class, subject])
    db_session.flush()

    exam = Exam(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        name="Mid Term",
        subject_id=subject.id,
        max_marks=100,
        exam_date=(now - timedelta(days=32)).date(),
        created_at=now - timedelta(days=32),
    )
    db_session.add(exam)
    db_session.flush()
    db_session.add_all([
        Attendance(tenant_id=active_tenant.id, student_id=student.id, class_id=school_class.id, date=(now - timedelta(days=30)).date(), status="present"),
        Attendance(tenant_id=active_tenant.id, student_id=student.id, class_id=school_class.id, date=(now - timedelta(days=29)).date(), status="present"),
        Mark(tenant_id=active_tenant.id, student_id=student.id, exam_id=exam.id, marks_obtained=81, created_at=now - timedelta(days=31)),
        AIQuery(
            tenant_id=active_tenant.id,
            user_id=student.id,
            query_text="Explain photosynthesis",
            mode="qa",
            response_text="response",
            token_usage=250,
            created_at=now - timedelta(days=9),
        ),
        Complaint(
            id=uuid.uuid4(),
            tenant_id=active_tenant.id,
            student_id=student.id,
            category="Transport",
            description="Bus route timing changed without notice.",
            status="open",
            created_at=now - timedelta(days=11),
        ),
        Complaint(
            id=uuid.uuid4(),
            tenant_id=active_tenant.id,
            student_id=student.id,
            category="Academic",
            description="Need answer sheet review.",
            status="resolved",
            resolution_note="Teacher review shared.",
            created_at=now - timedelta(days=27),
            resolved_at=now - timedelta(days=25),
        ),
    ])
    db_session.commit()

    token = _login(client, admin.email)
    headers = {"Authorization": f"Bearer {token}"}

    dashboard_response = client.get("/api/admin/dashboard", headers=headers)
    assert dashboard_response.status_code == 200
    dashboard_payload = dashboard_response.json()
    assert dashboard_payload["total_parents"] == 1
    assert len(dashboard_payload["monthly_trends"]) == 6
    assert dashboard_payload["complaint_health"]["resolution_rate_pct"] >= 50
    assert dashboard_payload["latest_milestones"]["last_complaint_at"] is not None

    complaints_response = client.get("/api/admin/complaints", headers=headers)
    assert complaints_response.status_code == 200
    complaints_payload = complaints_response.json()
    assert complaints_payload["summary"]["total"] == 2
    assert len(complaints_payload["monthly_activity"]) == 6
    assert complaints_payload["categories"][0]["count"] >= 1
