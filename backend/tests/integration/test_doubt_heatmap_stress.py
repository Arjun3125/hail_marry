from uuid import uuid4
import pytest


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


def _setup_heatmap_environment(db_session, active_tenant):
    from src.domains.academic.models import Class, Subject, Enrollment, Timetable
    from src.domains.platform.models import AIQuery
    import datetime

    teacher = _create_user(db_session, active_tenant.id, email="teacher-heatmap@testschool.edu", role="teacher")
    student1 = _create_user(db_session, active_tenant.id, email="student1@testschool.edu", role="student")
    student2 = _create_user(db_session, active_tenant.id, email="student2@testschool.edu", role="student")

    cls = Class(id=uuid4(), tenant_id=active_tenant.id, name="Class 10A")
    subject1 = Subject(id=uuid4(), tenant_id=active_tenant.id, name="Science", class_id=cls.id)
    timetable = Timetable(id=uuid4(), tenant_id=active_tenant.id, class_id=cls.id, subject_id=subject1.id, teacher_id=teacher.id, day_of_week=0, start_time=datetime.time(9, 0), end_time=datetime.time(10, 0))

    enroll1 = Enrollment(id=uuid4(), tenant_id=active_tenant.id, student_id=student1.id, class_id=cls.id)
    enroll2 = Enrollment(id=uuid4(), tenant_id=active_tenant.id, student_id=student2.id, class_id=cls.id)

    db_session.add_all([cls, subject1, timetable, enroll1, enroll2])
    db_session.commit()
    
    queries = [
        AIQuery(
            id=uuid4(), tenant_id=active_tenant.id, user_id=student1.id, 
            query_text="how does photosynthesis work? (science)", 
            mode="doubt"
        ),
        AIQuery(
            id=uuid4(), tenant_id=active_tenant.id, user_id=student2.id, 
            query_text="explain cell division for science class", 
            mode="doubt"
        ),
        AIQuery(
            id=uuid4(), tenant_id=active_tenant.id, user_id=student1.id, 
            query_text="newtons third law", 
            mode="doubt"
        )
    ]
    db_session.add_all(queries)
    db_session.commit()

    return teacher, subject1


def test_doubt_heatmap_aggregation(client, db_session, active_tenant):
    teacher, subject = _setup_heatmap_environment(db_session, active_tenant)
    token = _login(client, teacher.email)
    
    response = client.get(
        "/api/teacher/doubt-heatmap",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "heatmap" in data
    assert "top_topics" in data
    
    heatmap = {t["label"]: t["query_count"] for t in data["heatmap"]}
    assert heatmap.get("Class 10A - Science") == 2
    assert data["total_queries"] == 3


def test_doubt_heatmap_unauthorized(client, db_session, active_tenant):
    response = client.get("/api/teacher/doubt-heatmap")
    assert response.status_code == 401
