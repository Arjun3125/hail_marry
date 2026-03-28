"""Tests for AI Studio session tracking and smart suggestions endpoints."""
import uuid
import pytest
from fastapi.testclient import TestClient

from main import app
from auth.dependencies import get_current_user
from src.domains.identity.models.user import User
from src.domains.identity.models.tenant import Tenant
from src.domains.platform.models.study_session import StudySession

@pytest.fixture
def test_tenant(db_session):
    tenant = Tenant(id=uuid.uuid4(), name="Test School", domain="testschool.edu")
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant

@pytest.fixture
def test_user(db_session, test_tenant):
    user = User(
        id=uuid.uuid4(),
        tenant_id=test_tenant.id,
        email="student@testschool.edu",
        role="student",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def auth_client(client, test_user):
    app.dependency_overrides[get_current_user] = lambda: test_user
    yield client
    app.dependency_overrides.pop(get_current_user, None)

def test_start_session(auth_client, db_session, test_user):
    response = auth_client.post(
        "/api/ai-studio/sessions",
        json={"topic": "Biology Notes"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "session_id" in data
    
    session_id = data["session_id"]
    # Verify in DB
    session = db_session.query(StudySession).filter(StudySession.id == uuid.UUID(session_id)).first()
    assert session is not None
    assert session.user_id == test_user.id
    assert session.topic == "Biology Notes"

def test_heartbeat_session(auth_client, db_session, test_user):
    # First start a session
    start_resp = auth_client.post("/api/ai-studio/sessions", json={"topic": "Biology Notes"})
    session_id = start_resp.json()["session_id"]
    
    # Send heartbeat
    hb_resp = auth_client.put(
        f"/api/ai-studio/sessions/{session_id}",
        json={"duration_increment_seconds": 60, "questions_answered_increment": 2}
    )
    assert hb_resp.status_code == 200, hb_resp.text
    assert hb_resp.json() == {"status": "ok"}
    
    # Check DB update
    session = db_session.query(StudySession).filter(StudySession.id == uuid.UUID(session_id)).first()
    assert session.duration_seconds == 60
    assert session.questions_answered == 2

def test_get_suggestions(auth_client, db_session, test_user):
    response = auth_client.get("/api/ai-studio/suggestions")
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    # Should get deep_dive as default if no data
    assert data[0]["type"] == "deep_dive"
