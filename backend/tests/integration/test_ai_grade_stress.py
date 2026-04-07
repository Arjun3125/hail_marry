from uuid import uuid4
from unittest.mock import patch


def _create_user(db_session, tenant_id, *, email: str, role: str, password: str = "pass123!"):
    from src.domains.identity.models.user import User
    from src.domains.identity.routes.auth import pwd_context

    user = User(
        id=uuid4(),
        tenant_id=tenant_id,
        email=email,
        full_name=f"{role.title()} User",
        role=role,
        hashed_password=pwd_context.hash(password),
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    return user


def _login(client, email: str, password: str = "pass123!") -> str:
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json().get("access_token")


def _setup_teacher_environment(db_session, active_tenant):
    from src.domains.academic.models import Class, Subject, Exam, Timetable
    import datetime

    teacher = _create_user(db_session, active_tenant.id, email="teacher-aigrade@testschool.edu", role="teacher")
    
    cls = Class(id=uuid4(), tenant_id=active_tenant.id, name="Class 10A")
    subject = Subject(id=uuid4(), tenant_id=active_tenant.id, name="Science", class_id=cls.id)
    exam = Exam(id=uuid4(), tenant_id=active_tenant.id, name="Midterm", subject_id=subject.id, max_marks=100)
    timetable = Timetable(id=uuid4(), tenant_id=active_tenant.id, class_id=cls.id, subject_id=subject.id, teacher_id=teacher.id, day_of_week=0, start_time=datetime.time(9, 0), end_time=datetime.time(10, 0))

    db_session.add_all([cls, subject, exam, timetable])
    db_session.commit()
    db_session.refresh(exam)
    return teacher, exam


@patch("src.domains.academic.routes.teacher.enqueue_job")
def test_ai_grade_endpoint_valid_request(mock_enqueue, client, db_session, active_tenant):
    teacher, exam = _setup_teacher_environment(db_session, active_tenant)
    token = _login(client, teacher.email)
    
    mock_enqueue.return_value = "mock-job-id"
    
    files = {"file": ("answers.png", b"fake image bytes", "image/png")}
    data = {"exam_id": str(exam.id), "student_name": "John Doe", "rubric": "Grade strictly"}

    response = client.post(
        "/api/teacher/ai-grade",
        headers={"Authorization": f"Bearer {token}"},
        data=data,
        files=files
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["job_id"] == "mock-job-id"
    mock_enqueue.assert_called_once()
    args, kwargs = mock_enqueue.call_args
    assert kwargs.get("job_type") == "ai_grade"


def test_ai_grade_endpoint_missing_file(client, db_session, active_tenant):
    teacher, exam = _setup_teacher_environment(db_session, active_tenant)
    token = _login(client, teacher.email)
    
    data = {"exam_id": str(exam.id)}
    
    response = client.post(
        "/api/teacher/ai-grade",
        headers={"Authorization": f"Bearer {token}"},
        data=data,
    )
    # File is required
    assert response.status_code == 422


@patch("src.domains.academic.routes.teacher.enqueue_job")
def test_ai_grade_endpoint_invalid_exam_id(mock_enqueue, client, db_session, active_tenant):
    teacher, exam = _setup_teacher_environment(db_session, active_tenant)
    token = _login(client, teacher.email)
    
    files = {"file": ("answers.png", b"fake image bytes", "image/png")}
    data = {"exam_id": str(uuid4())} # exam doesn't exist

    response = client.post(
        "/api/teacher/ai-grade",
        headers={"Authorization": f"Bearer {token}"},
        data=data,
        files=files
    )

    assert response.status_code == 404
    assert mock_enqueue.call_count == 0
