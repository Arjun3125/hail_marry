"""Tests for WhatsApp Gateway — signature verification, OTP auth, session management,
RBAC enforcement, and webhook pipeline.
"""
import hashlib
import hmac
import json
import os
import secrets
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# ─── Set env vars before imports ──────────────────────────────
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("WHATSAPP_APP_SECRET", "test-secret-key")
os.environ.setdefault("WHATSAPP_VERIFY_TOKEN", "vidyaos-wa-verify")

from src.domains.platform.routes.whatsapp import router as wa_router
from src.domains.platform.services.whatsapp_gateway import (
    verify_webhook_signature,
    generate_otp,
    verify_otp,
    get_session,
    create_session,
    save_session,
    delete_session,
    is_rate_limited,
    is_duplicate_message,
    handle_system_command,
    SYSTEM_COMMANDS,
)
from src.domains.ai_engine.ai.whatsapp_tools import (
    authorize_tool,
    TOOL_ROLE_MAP,
    get_tools_for_role,
)
from src.domains.ai_engine.ai.whatsapp_agent import (
    _classify_intent_heuristic,
    WhatsAppAgentState,
    build_whatsapp_agent_graph,
)


# ─── Fixtures ─────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def reset_app_secret():
    """Reset WHATSAPP_APP_SECRET between tests to prevent ordering issues."""
    from src.domains.platform.services import whatsapp_gateway
    original = whatsapp_gateway.WHATSAPP_APP_SECRET
    yield
    whatsapp_gateway.WHATSAPP_APP_SECRET = original

@pytest.fixture
def app():
    """Create a test FastAPI app with WhatsApp routes."""
    test_app = FastAPI()
    test_app.include_router(wa_router)
    return test_app


@pytest.fixture
def client(app):
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def mock_redis():
    """Mock Redis with an in-memory dict."""
    storage = {}

    class FakeRedis:
        def get(self, key):
            item = storage.get(key)
            if item and isinstance(item, dict) and "ttl" in item:
                return item["value"]
            return item

        def setex(self, key, ttl, value):
            storage[key] = {"value": value, "ttl": ttl}

        def delete(self, key):
            storage.pop(key, None)

        def incr(self, key):
            if key not in storage:
                storage[key] = {"value": "0", "ttl": 60}
            val = int(storage[key]["value"]) + 1
            storage[key]["value"] = str(val)
            return val

        def expire(self, key, ttl):
            if key in storage:
                storage[key]["ttl"] = ttl

        def pipeline(self):
            return FakePipeline(self)

    class FakePipeline:
        def __init__(self, redis):
            self._redis = redis
            self._ops = []

        def incr(self, key):
            self._ops.append(("incr", key))
            return self

        def expire(self, key, ttl):
            self._ops.append(("expire", key, ttl))
            return self

        def execute(self):
            for op in self._ops:
                if op[0] == "incr":
                    self._redis.incr(op[1])
                elif op[0] == "expire":
                    self._redis.expire(op[1], op[2])

    fake = FakeRedis()
    with patch("src.domains.platform.services.whatsapp_gateway._get_redis", return_value=fake):
        yield fake, storage


# ─── Signature Verification Tests ─────────────────────────────

class TestSignatureVerification:
    def test_valid_signature(self):
        """Verify that a correctly signed payload passes."""
        payload = b'{"test": "data"}'
        secret = "test-secret-key"
        expected_sig = "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()

        with patch.dict(os.environ, {"WHATSAPP_APP_SECRET": secret}):
            # Re-import to pick up env var
            from src.domains.platform.services import whatsapp_gateway
            whatsapp_gateway.WHATSAPP_APP_SECRET = secret
            assert verify_webhook_signature(payload, expected_sig) is True

    def test_invalid_signature(self):
        """Verify that an incorrectly signed payload fails."""
        payload = b'{"test": "data"}'
        from src.domains.platform.services import whatsapp_gateway
        whatsapp_gateway.WHATSAPP_APP_SECRET = "test-secret-key"
        assert verify_webhook_signature(payload, "sha256=invalid") is False

    def test_missing_secret_allows_in_dev(self):
        """When APP_SECRET is empty, verification should pass (dev mode)."""
        from src.domains.platform.services import whatsapp_gateway
        whatsapp_gateway.WHATSAPP_APP_SECRET = ""
        assert verify_webhook_signature(b"anything", "sha256=whatever") is True


# ─── OTP Tests ────────────────────────────────────────────────

class TestOTPFlow:
    def test_generate_and_verify_otp(self, mock_redis):
        """Generate an OTP and verify it successfully."""
        fake_redis, storage = mock_redis
        otp = generate_otp("919876543210", "student@test.com")
        assert len(otp) == 6
        assert otp.isdigit()

        result = verify_otp("919876543210", otp)
        assert result["success"] is True
        assert result["email"] == "student@test.com"

    def test_wrong_otp(self, mock_redis):
        """Wrong OTP should fail with remaining attempts."""
        fake_redis, storage = mock_redis
        generate_otp("919876543210", "student@test.com")

        result = verify_otp("919876543210", "000000")
        assert result["success"] is False
        assert "Invalid OTP" in result["error"]

    def test_expired_otp(self, mock_redis):
        """Non-existent OTP should report expired."""
        fake_redis, storage = mock_redis
        result = verify_otp("919876543210", "123456")
        assert result["success"] is False
        assert "expired" in result["error"].lower() or "not found" in result["error"].lower()

    def test_max_attempts_lockout(self, mock_redis):
        """After max attempts, OTP should be deleted."""
        fake_redis, storage = mock_redis
        generate_otp("919876543210", "student@test.com")

        for i in range(3):
            verify_otp("919876543210", "000000")

        result = verify_otp("919876543210", "000000")
        assert result["success"] is False
        assert "too many" in result["error"].lower()


# ─── Session Management Tests ─────────────────────────────────

class TestSessionManagement:
    def test_create_and_load_session(self, mock_redis):
        """Create a session and load it back."""
        fake_redis, storage = mock_redis
        session = create_session("919876543210", "user-123", "tenant-456", "student")
        assert session["phone"] == "919876543210"
        assert session["role"] == "student"

        loaded = get_session("919876543210")
        assert loaded is not None
        assert loaded["user_id"] == "user-123"

    def test_delete_session(self, mock_redis):
        """Delete a session."""
        fake_redis, storage = mock_redis
        create_session("919876543210", "user-123", "tenant-456", "student")
        delete_session("919876543210")
        assert get_session("919876543210") is None

    def test_session_not_found(self, mock_redis):
        """Loading a non-existent session returns None."""
        fake_redis, storage = mock_redis
        assert get_session("919999999999") is None


# ─── Rate Limiting Tests ─────────────────────────────────────

class TestRateLimiting:
    def test_under_limit(self, mock_redis):
        """Should not be rate limited under threshold."""
        fake_redis, storage = mock_redis
        assert is_rate_limited("919876543210") is False

    def test_over_limit(self, mock_redis):
        """Should be rate limited after exceeding threshold."""
        fake_redis, storage = mock_redis
        # Simulate hitting the limit
        for _ in range(10):
            is_rate_limited("919876543210")
        assert is_rate_limited("919876543210") is True


# ─── Deduplication Tests ──────────────────────────────────────

class TestDeduplication:
    def test_first_message_not_duplicate(self, mock_redis):
        """First time seeing a message ID should not be duplicate."""
        fake_redis, storage = mock_redis
        assert is_duplicate_message("msg-001") is False

    def test_second_message_is_duplicate(self, mock_redis):
        """Second time seeing the same message ID should be duplicate."""
        fake_redis, storage = mock_redis
        is_duplicate_message("msg-002")
        assert is_duplicate_message("msg-002") is True


# ─── System Command Tests ─────────────────────────────────────

class TestSystemCommands:
    def test_help_command_student(self):
        """Help command should return student-specific options."""
        session = {"role": "student", "phone": "919876543210"}
        response = handle_system_command("help", session)
        assert "timetable" in response.lower()
        assert "attendance" in response.lower()

    def test_help_command_teacher(self):
        """Help command should return teacher-specific options."""
        session = {"role": "teacher", "phone": "919876543210"}
        response = handle_system_command("help", session)
        assert "classes" in response.lower()
        assert "absent" in response.lower()

    def test_help_command_parent(self):
        """Help command should return parent-specific options."""
        session = {"role": "parent", "phone": "919876543210"}
        response = handle_system_command("help", session)
        assert "child" in response.lower()

    def test_help_command_admin(self):
        """Help command should return admin-specific options."""
        session = {"role": "admin", "phone": "919876543210"}
        response = handle_system_command("help", session)
        assert "fee" in response.lower()
        assert "attendance" in response.lower()

    def test_logout_command(self, mock_redis):
        """Logout should delete the session."""
        fake_redis, storage = mock_redis
        create_session("919876543210", "user-123", "tenant-456", "student")
        session = {"role": "student", "phone": "919876543210"}
        response = handle_system_command("/logout", session)
        assert "logged out" in response.lower()

    def test_status_command(self):
        """Status should return session info."""
        session = {"role": "student", "phone": "919876543210", "session_id": "ws-abc123", "last_activity": "2026-03-18T10:00:00"}
        response = handle_system_command("/status", session)
        assert "student" in response.lower()
        assert "ws-abc123" in response

    def test_switch_child_non_parent(self):
        """Switch child should only work for parents."""
        session = {"role": "student", "phone": "919876543210"}
        response = handle_system_command("/switch", session)
        assert "parent" in response.lower()


# ─── RBAC Tests ───────────────────────────────────────────────

class TestRBAC:
    def test_student_authorized_for_timetable(self):
        assert authorize_tool("get_student_timetable", "student") is True

    def test_student_not_authorized_for_fees(self):
        assert authorize_tool("get_fee_pending_report", "student") is False

    def test_teacher_authorized_for_schedule(self):
        assert authorize_tool("get_teacher_schedule", "teacher") is True

    def test_parent_authorized_for_child_attendance(self):
        assert authorize_tool("get_child_attendance", "parent") is True

    def test_parent_not_authorized_for_admin_tools(self):
        assert authorize_tool("get_school_attendance_summary", "parent") is False

    def test_admin_authorized_for_fees(self):
        assert authorize_tool("get_fee_pending_report", "admin") is True

    def test_admin_not_authorized_for_student_tools(self):
        assert authorize_tool("get_student_timetable", "admin") is False

    def test_library_shared_across_roles(self):
        assert authorize_tool("check_library_catalog", "student") is True
        assert authorize_tool("check_library_catalog", "teacher") is True
        assert authorize_tool("check_library_catalog", "admin") is True
        assert authorize_tool("check_library_catalog", "parent") is False

    def test_get_tools_for_student(self):
        tools = get_tools_for_role("student")
        tool_names = [t.name for t in tools]
        assert "get_student_timetable" in tool_names
        assert "get_fee_pending_report" not in tool_names

    def test_get_tools_for_admin(self):
        tools = get_tools_for_role("admin")
        tool_names = [t.name for t in tools]
        assert "get_fee_pending_report" in tool_names
        assert "get_student_timetable" not in tool_names


# ─── Intent Classification Tests ──────────────────────────────

class TestIntentClassification:
    def test_student_timetable_intent(self):
        result = _classify_intent_heuristic("What is my timetable today?", "student")
        assert result == "get_student_timetable"

    def test_student_test_intent(self):
        result = _classify_intent_heuristic("Do I have any test today?", "student")
        assert result == "get_student_tests"

    def test_student_attendance_intent(self):
        result = _classify_intent_heuristic("Show my attendance", "student")
        assert result == "get_student_attendance"

    def test_student_results_intent(self):
        result = _classify_intent_heuristic("Show my marks", "student")
        assert result == "get_student_results"

    def test_teacher_schedule_override(self):
        """Teacher asking for timetable should get teacher schedule, not student."""
        result = _classify_intent_heuristic("Show my timetable", "teacher")
        assert result == "get_teacher_schedule"

    def test_teacher_absent_intent(self):
        result = _classify_intent_heuristic("Which students are absent?", "teacher")
        assert result == "get_teacher_absent_students"

    def test_parent_attendance_override(self):
        """Parent asking for attendance should get child's attendance."""
        result = _classify_intent_heuristic("Show attendance", "parent")
        assert result == "get_child_attendance"

    def test_parent_homework_intent(self):
        result = _classify_intent_heuristic("Any homework today?", "parent")
        assert result == "get_child_homework"

    def test_admin_fee_intent(self):
        result = _classify_intent_heuristic("Fee pending report", "admin")
        assert result == "get_fee_pending_report"

    def test_admin_attendance_override(self):
        result = _classify_intent_heuristic("Show attendance summary", "admin")
        assert result == "get_school_attendance_summary"

    def test_unknown_intent_returns_none(self):
        result = _classify_intent_heuristic("Hello there how are you doing?", "student")
        assert result is None

    def test_library_intent(self):
        result = _classify_intent_heuristic("Any books on physics?", "admin")
        assert result == "check_library_catalog"


# ─── Webhook Endpoint Tests ──────────────────────────────────

class TestWebhookEndpoints:
    def test_webhook_verification_success(self, client):
        """Meta verification handshake should succeed with correct token."""
        response = client.get(
            "/whatsapp/webhook",
            params={
                "hub.mode": "subscribe",
                "hub.verify_token": "vidyaos-wa-verify",
                "hub.challenge": "12345",
            },
        )
        assert response.status_code == 200
        assert response.json() == 12345

    def test_webhook_verification_failure(self, client):
        """Meta verification should fail with wrong token."""
        response = client.get(
            "/whatsapp/webhook",
            params={
                "hub.mode": "subscribe",
                "hub.verify_token": "wrong-token",
                "hub.challenge": "12345",
            },
        )
        assert response.status_code == 403

    def test_webhook_inbound_invalid_signature(self, client):
        """Inbound webhook should reject invalid signatures."""
        from src.domains.platform.services import whatsapp_gateway
        whatsapp_gateway.WHATSAPP_APP_SECRET = "real-secret"

        response = client.post(
            "/whatsapp/webhook",
            json={"entry": []},
            headers={"X-Hub-Signature-256": "sha256=invalid"},
        )
        assert response.status_code == 403

        # Reset
        whatsapp_gateway.WHATSAPP_APP_SECRET = ""


# ─── Agent Graph Structure Test ───────────────────────────────

class TestAgentGraph:
    def test_graph_compiles(self):
        """The WhatsApp agent graph should compile without errors."""
        graph = build_whatsapp_agent_graph()
        compiled = graph.compile()
        assert compiled is not None

    def test_graph_has_expected_nodes(self):
        """The graph should contain all 4 expected nodes."""
        graph = build_whatsapp_agent_graph()
        node_names = set(graph.nodes.keys())
        assert "classify_intent" in node_names
        assert "execute_tool" in node_names
        assert "generate_response" in node_names
        assert "format_for_whatsapp" in node_names


# ─── Model Import Test ───────────────────────────────────────

class TestModels:
    def test_phone_user_link_import(self):
        from src.domains.platform.models.whatsapp_models import PhoneUserLink
        assert PhoneUserLink.__tablename__ == "phone_user_link"

    def test_whatsapp_session_import(self):
        from src.domains.platform.models.whatsapp_models import WhatsAppSession
        assert WhatsAppSession.__tablename__ == "whatsapp_sessions"

    def test_whatsapp_message_import(self):
        from src.domains.platform.models.whatsapp_models import WhatsAppMessage
        assert WhatsAppMessage.__tablename__ == "whatsapp_messages"
