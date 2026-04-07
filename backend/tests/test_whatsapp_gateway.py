"""Tests for WhatsApp Gateway — signature verification, OTP auth, session management,
RBAC enforcement, and webhook pipeline.
"""
import asyncio
import functools
import inspect
import hashlib
import hmac
import httpx
import json
import os
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, mock_open, patch
from uuid import uuid4

import pytest

# ─── Set env vars before imports ──────────────────────────────
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("WHATSAPP_APP_SECRET", "test-secret-key")
os.environ.setdefault("WHATSAPP_VERIFY_TOKEN", "vidyaos-wa-verify")

from src.domains.platform.routes.whatsapp import (
    whatsapp_webhook_verify,
    whatsapp_webhook_inbound,
    whatsapp_tool_catalog,
    whatsapp_release_gate_snapshot,
    admin_send_message,
    _extract_messages,
    _chunk_whatsapp_text,
    SendMessageRequest,
    _dispatch_outbound_response,
    whatsapp_report_card_download,
)
from src.domains.platform.services.whatsapp_gateway import (
    verify_webhook_signature,
    generate_otp,
    verify_otp,
    get_whatsapp_metrics,
    get_session,
    create_session,
    delete_session,
    unlink_phone,
    is_rate_limited,
    is_duplicate_message,
    send_text_message,
    handle_system_command,
    format_ai_job_status_message,
    process_inbound_message,
    _handle_unlinked_phone,
    _handle_signup_email,
    _ingest_whatsapp_url,
    _build_child_switch_response,
    _handle_child_switch_selection,
    _build_report_card_response,
)
from src.shared.ai_tools.whatsapp_tools import (
    authorize_tool,
    _format_study_tool_payload,
    get_tools_for_role,
    get_tool_spec,
    get_tool_specs_for_role,
    serialize_tool_catalog,
    serialize_tier_4_5_feature_matrix,
)
from src.interfaces.whatsapp_bot.agent import (
    classify_intent,
    execute_tool,
    generate_response,
    _classify_intent_heuristic,
    _extract_topic_from_message,
    format_for_whatsapp,
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

@pytest.fixture(autouse=True)
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

    def test_missing_signature_header_fails(self):
        """Webhook requests without the Meta signature header must be rejected."""
        payload = b'{"test": "data"}'
        from src.domains.platform.services import whatsapp_gateway
        whatsapp_gateway.WHATSAPP_APP_SECRET = "test-secret-key"
        assert verify_webhook_signature(payload, "") is False

    def test_missing_secret_rejects_signature(self):
        """When APP_SECRET is empty, webhook verification must fail closed."""
        from src.domains.platform.services import whatsapp_gateway
        whatsapp_gateway.WHATSAPP_APP_SECRET = ""
        assert verify_webhook_signature(b"anything", "sha256=whatever") is False


@pytest.mark.asyncio
async def test_whatsapp_release_gate_snapshot_includes_metrics_and_rates():
    current_user = SimpleNamespace(role="admin", tenant_id=uuid4())
    db = MagicMock()
    metrics = {
        "inbound_total": 20,
        "duplicate_inbound_total": 2,
        "rate_limited_total": 1,
        "unlinked_inbound_total": 3,
        "routing_success_total": 15,
        "routing_failure_total": 5,
        "upload_ingest_success_total": 4,
        "upload_ingest_failure_total": 1,
        "link_ingest_success_total": 3,
        "link_ingest_failure_total": 1,
        "outbound_success_total": 12,
        "outbound_failure_total": 3,
        "outbound_retryable_failure_total": 2,
        "outbound_non_retryable_failure_total": 1,
        "visible_failure_total": 4,
    }
    analytics = {
        "period_days": 7,
        "total_messages": 40,
        "inbound": 20,
        "outbound": 20,
        "unique_users": 6,
        "avg_latency_ms": 850,
        "top_intents": [{"intent": "quiz", "count": 5}],
    }

    with patch("src.domains.platform.routes.whatsapp._build_whatsapp_usage_snapshot", return_value=analytics), \
         patch("src.domains.platform.routes.whatsapp.get_whatsapp_metrics", return_value=metrics):
        result = await whatsapp_release_gate_snapshot(current_user=current_user, db=db, days=7)

    assert result["analytics"] == analytics
    assert result["release_gate_metrics"] == metrics
    assert result["derived_rates"]["routing_failure_pct"] == 25.0
    assert result["derived_rates"]["duplicate_inbound_pct"] == 10.0
    assert result["derived_rates"]["visible_failure_pct"] == 20.0
    assert result["derived_rates"]["outbound_retryable_failure_pct"] == round((2 / 15) * 100, 2)


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

class TestUnlinkedPhoneAuth:
    async def test_unlinked_phone_welcome_mentions_signup(self):
        db = MagicMock()
        with patch("src.domains.platform.services.whatsapp_gateway.get_session", return_value=None), \
             patch("src.domains.platform.services.whatsapp_gateway.save_session"):
            result = await _handle_unlinked_phone(db, "919876543210", "hello")

        assert "registered email address" in result["response_text"].lower()
        assert "signup" in result["response_text"].lower()

    async def test_unlinked_phone_accepts_direct_email_on_first_message(self):
        db = MagicMock()
        with patch("src.domains.platform.services.whatsapp_gateway.get_session", return_value=None), \
             patch("src.domains.platform.services.whatsapp_gateway.save_session") as save_mock, \
             patch("src.domains.platform.services.whatsapp_gateway._handle_email_lookup", new=AsyncMock(return_value={
                 "response_text": "OTP sent",
                 "response_type": "text",
             })) as email_lookup:
            result = await _handle_unlinked_phone(db, "919876543210", "student@school.edu")

        assert result["response_text"] == "OTP sent"
        save_mock.assert_called_once()
        email_lookup.assert_awaited_once()

    async def test_unlinked_phone_signup_command_enters_signup_state(self):
        db = MagicMock()
        with patch("src.domains.platform.services.whatsapp_gateway.get_session", return_value=None), \
             patch("src.domains.platform.services.whatsapp_gateway.save_session") as save_mock:
            result = await _handle_unlinked_phone(db, "919876543210", "signup")

        assert "new student account" in result["response_text"].lower()
        saved_session = save_mock.call_args.args[2]
        assert saved_session["pending_action"] == "awaiting_signup_email"

    async def test_handle_signup_email_creates_authenticated_session(self):
        db = MagicMock()
        session = {
            "session_id": "ws-123",
            "phone": "919876543210",
            "user_id": None,
            "tenant_id": None,
            "role": None,
            "active_notebook_id": None,
            "pending_action": "awaiting_signup_email",
            "conversation_history": [],
            "last_activity": datetime.now(timezone.utc).isoformat(),
        }
        fake_user = SimpleNamespace(
            id=uuid4(),
            tenant_id=uuid4(),
            full_name="New Student",
            role="student",
        )

        with patch("src.domains.platform.services.whatsapp_gateway._create_whatsapp_signup_user", return_value=(fake_user, None)), \
             patch("src.domains.platform.services.whatsapp_gateway.save_session") as save_mock:
            result = await _handle_signup_email(db, "919876543210", "new@school.edu", session)

        assert "created and linked" in result["response_text"].lower()
        assert session["pending_action"] is None
        assert session["user_id"] == str(fake_user.id)
        save_mock.assert_called_once()


class TestSessionManagement:
    def test_create_and_load_session(self, mock_redis):
        """Create a session and load it back."""
        fake_redis, storage = mock_redis
        session = create_session(MagicMock(), "919876543210", "user-123", "tenant-456", "student")
        assert session["phone"] == "919876543210"
        assert session["role"] == "student"

        loaded = get_session(MagicMock(), "919876543210")
        assert loaded is not None
        assert loaded["user_id"] == "user-123"

    def test_delete_session(self, mock_redis):
        """Delete a session."""
        fake_redis, storage = mock_redis
        create_session(MagicMock(), "919876543210", "user-123", "tenant-456", "student")
        delete_session(MagicMock(), "919876543210")
        assert get_session(MagicMock(), "919876543210") is None

    def test_unlink_phone_clears_session_and_phone_cache(self, mock_redis):
        fake_redis, storage = mock_redis
        create_session(MagicMock(), "919876543210", "user-123", "tenant-456", "student")
        storage["wa:phone:919876543210"] = json.dumps({
            "id": str(uuid4()),
            "phone": "919876543210",
            "user_id": str(uuid4()),
            "tenant_id": str(uuid4()),
        })
        db = MagicMock()

        unlink_phone(db, "919876543210")

        assert get_session(MagicMock(), "919876543210") is None
        assert "wa:phone:919876543210" not in storage
        assert db.query.return_value.filter.return_value.delete.call_count >= 1
        db.commit.assert_called()

    def test_session_not_found(self, mock_redis):
        """Loading a non-existent session returns None."""
        fake_redis, storage = mock_redis
        assert get_session(MagicMock(), "919999999999") is None


# ─── Rate Limiting Tests ─────────────────────────────────────

class TestReturningUserReEntry:
    async def test_process_inbound_message_recreates_session_for_linked_user_without_active_session(self):
        link = SimpleNamespace(user_id=uuid4(), tenant_id=uuid4())
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = SimpleNamespace(role="student")
        recreated_session = {
            "phone": "919876543210",
            "user_id": str(link.user_id),
            "tenant_id": str(link.tenant_id),
            "role": "student",
            "active_child_id": None,
            "active_notebook_id": None,
            "conversation_history": [],
        }

        with patch("src.domains.platform.services.whatsapp_gateway.resolve_phone_to_user", return_value=link), \
             patch("src.domains.platform.services.whatsapp_gateway.get_session", return_value=None), \
             patch("src.domains.platform.services.whatsapp_gateway.create_session", return_value=recreated_session) as create_session_mock, \
             patch("src.interfaces.whatsapp_bot.agent.run_whatsapp_agent", new=AsyncMock(return_value={
                 "response": "Welcome back",
                 "response_type": "text",
                 "intent": "ask_ai_question",
                 "tool_name": "ask_ai_question",
             })) as agent_mock, \
             patch("src.domains.platform.services.whatsapp_gateway.save_session"), \
             patch("src.domains.platform.services.whatsapp_gateway.log_message"):
            result = await process_inbound_message(db, "919876543210", "Explain photosynthesis")

        assert result["response_text"] == "Welcome back"
        create_session_mock.assert_called_once_with(
            db,
            "919876543210",
            str(link.user_id),
            str(link.tenant_id),
            "student",
        )
        agent_mock.assert_awaited_once()


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

    async def test_process_inbound_message_short_circuits_duplicate_events(self, mock_redis):
        fake_redis, storage = mock_redis
        db = MagicMock()
        with patch("src.domains.platform.services.whatsapp_gateway.is_duplicate_message", return_value=True), \
             patch("src.domains.platform.services.whatsapp_gateway.resolve_phone_to_user") as resolve_mock:
            result = await process_inbound_message(
                db,
                "919876543210",
                "Explain photosynthesis",
                wa_message_id="wamid-dup-1",
            )

        assert result == {"response_text": None, "response_type": "none", "duplicate": True}
        resolve_mock.assert_not_called()
        metrics = get_whatsapp_metrics()
        assert metrics["duplicate_inbound_total"] == 1


# ─── Parent Child Switching Tests ─────────────────────────────

class TestParentChildSwitching:
    def test_build_child_switch_response_returns_list_for_multiple_children(self):
        session = {"phone": "919876543210", "active_child_id": None}
        db = MagicMock()
        with patch("src.domains.platform.services.whatsapp_gateway._get_parent_children", return_value=[
            {"child_id": "child-1", "name": "Aarav"},
            {"child_id": "child-2", "name": "Diya"},
        ]):
            response = _build_child_switch_response(db, session)

        assert response["response_type"] == "list"
        assert response["rows"][0]["id"] == "child:child-1"
        assert response["rows"][1]["title"] == "Diya"

    def test_handle_child_switch_selection_updates_session(self):
        session = {"phone": "919876543210", "active_child_id": None}
        db = MagicMock()
        with patch("src.domains.platform.services.whatsapp_gateway._get_parent_children", return_value=[
            {"child_id": "child-1", "name": "Aarav"},
        ]), patch("src.domains.platform.services.whatsapp_gateway.save_session") as save_mock:
            response = _handle_child_switch_selection(db, session, "child:child-1")

        assert session["active_child_id"] == "child-1"
        assert response["response_type"] == "text"
        save_mock.assert_called_once()

    async def test_parent_without_active_child_gets_selection_list(self):
        link = SimpleNamespace(user_id=uuid4(), tenant_id=uuid4())
        session = {
            "phone": "919876543210",
            "user_id": str(link.user_id),
            "tenant_id": str(link.tenant_id),
            "role": "parent",
            "active_child_id": None,
            "conversation_history": [],
        }
        db = MagicMock()
        with patch("src.domains.platform.services.whatsapp_gateway.resolve_phone_to_user", return_value=link), \
             patch("src.domains.platform.services.whatsapp_gateway.get_session", return_value=session), \
             patch("src.domains.platform.services.whatsapp_gateway._build_child_switch_response", return_value={
                 "response_text": "Choose a child",
                 "response_type": "list",
                 "rows": [{"id": "child:1", "title": "Aarav"}],
                 "header": "Choose child",
                 "button_text": "Select",
             }), \
             patch("src.domains.platform.services.whatsapp_gateway.log_message"), \
             patch("src.domains.platform.services.whatsapp_gateway.save_session"):
            result = await process_inbound_message(db, "919876543210", "Show attendance")

        assert result["response_type"] == "list"
        assert result["rows"][0]["id"] == "child:1"


# ─── System Command Tests ─────────────────────────────────────

class TestSystemCommands:
    def test_help_command_student(self):
        """Help command should return student-specific options."""
        session = {"role": "student", "phone": "919876543210"}
        response = handle_system_command(MagicMock(), "help", session)
        assert "timetable" in response.lower()
        assert "attendance" in response.lower()

    def test_help_command_teacher(self):
        """Help command should return teacher-specific options."""
        session = {"role": "teacher", "phone": "919876543210"}
        response = handle_system_command(MagicMock(), "help", session)
        assert "classes" in response.lower()
        assert "absent" in response.lower()

    def test_help_command_parent(self):
        """Help command should return parent-specific options."""
        session = {"role": "parent", "phone": "919876543210"}
        response = handle_system_command(MagicMock(), "help", session)
        assert "child" in response.lower()
        assert "/reportcard" in response.lower()

    def test_help_command_admin(self):
        """Help command should return admin-specific options."""
        session = {"role": "admin", "phone": "919876543210"}
        response = handle_system_command(MagicMock(), "help", session)
        assert "fee" in response.lower()
        assert "attendance" in response.lower()

    def test_logout_command(self, mock_redis):
        """Logout should delete the session."""
        fake_redis, storage = mock_redis
        create_session(MagicMock(), "919876543210", "user-123", "tenant-456", "student")
        session = {"role": "student", "phone": "919876543210"}
        response = handle_system_command(MagicMock(), "/logout", session)
        assert "logged out" in response.lower()
        assert "wa:session:919876543210" not in storage

    def test_help_command_mentions_relink(self):
        session = {"role": "student", "phone": "919876543210"}
        response = handle_system_command(MagicMock(), "help", session)
        assert "/relink" in response

    def test_relink_command_unlinks_phone(self):
        session = {"role": "student", "phone": "919876543210"}
        with patch("src.domains.platform.services.whatsapp_gateway.unlink_phone") as unlink_mock:
            response = handle_system_command(MagicMock(), "/relink", session)

        unlink_mock.assert_called_once()
        assert "unlinked" in response.lower()
        assert "registered email" in response.lower()

    def test_status_command(self):
        """Status should return session info."""
        session = {"role": "student", "phone": "919876543210", "session_id": "ws-abc123", "last_activity": "2026-03-18T10:00:00"}
        response = handle_system_command(MagicMock(), "/status", session)
        assert "student" in response.lower()
        assert "ws-abc123" in response

    def test_switch_child_non_parent(self):
        """Switch child should only work for parents."""
        session = {"role": "student", "phone": "919876543210"}
        response = handle_system_command(MagicMock(), "/switch", session)
        assert "parent" in response.lower()

    def test_report_card_non_parent(self):
        session = {"role": "student", "phone": "919876543210"}
        response = handle_system_command(MagicMock(), "/reportcard", session)
        assert "parent" in response.lower()


# ─── RBAC Tests ───────────────────────────────────────────────

class TestRBAC:
    def test_student_authorized_for_timetable(self):
        assert authorize_tool("get_student_timetable", "student") is True

    def test_student_not_authorized_for_fees(self):
        assert authorize_tool("get_fee_pending_report", "student") is False

    def test_teacher_authorized_for_schedule(self):
        assert authorize_tool("get_teacher_schedule", "teacher") is True

    def test_teacher_authorized_for_generate_quiz(self):
        assert authorize_tool("generate_quiz", "teacher") is True

    def test_student_authorized_for_generate_study_guide(self):
        assert authorize_tool("generate_study_guide", "student") is True

    def test_student_authorized_for_generate_audio_overview(self):
        assert authorize_tool("generate_audio_overview", "student") is True

    def test_teacher_authorized_for_generate_study_guide(self):
        assert authorize_tool("generate_study_guide", "teacher") is True

    def test_parent_authorized_for_generate_study_guide(self):
        assert authorize_tool("generate_study_guide", "parent") is True

    def test_admin_authorized_for_generate_audio_overview(self):
        assert authorize_tool("generate_audio_overview", "admin") is True

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

    def test_tool_spec_metadata_for_parent_tool(self):
        spec = get_tool_spec("get_child_attendance")
        assert spec is not None
        assert spec.required_params == ("child_id", "tenant_id")
        assert spec.feature_category == "erp_read"
        assert "parent" in spec.roles

    def test_tool_specs_for_role_are_filtered(self):
        specs = get_tool_specs_for_role("teacher")
        names = [spec.name for spec in specs]
        assert "get_teacher_schedule" in names
        assert "generate_quiz" in names
        assert "get_student_timetable" not in names

    def test_serialized_catalog_includes_execution_metadata(self):
        catalog = serialize_tool_catalog("admin")
        fee_tool = next(item for item in catalog if item["name"] == "get_fee_pending_report")
        assert fee_tool["execution_mode"] == "sync"
        assert fee_tool["channel_suitability"] == "direct"

    def test_serialized_catalog_marks_generate_quiz_async(self):
        catalog = serialize_tool_catalog("teacher")
        quiz_tool = next(item for item in catalog if item["name"] == "generate_quiz")
        assert quiz_tool["execution_mode"] == "async"
        assert quiz_tool["feature_category"] == "ai_async"

    def test_serialized_catalog_marks_generate_study_guide_async(self):
        catalog = serialize_tool_catalog("student")
        guide_tool = next(item for item in catalog if item["name"] == "generate_study_guide")
        assert guide_tool["execution_mode"] == "async"
        assert guide_tool["feature_category"] == "ai_async"

    def test_serialized_catalog_marks_generate_audio_overview_async(self):
        catalog = serialize_tool_catalog("student")
        audio_tool = next(item for item in catalog if item["name"] == "generate_audio_overview")
        assert audio_tool["execution_mode"] == "async"
        assert audio_tool["feature_category"] == "ai_async"

    def test_serialized_catalog_marks_diagram_tools_summary_plus_link(self):
        catalog = serialize_tool_catalog("student")
        flowchart_tool = next(item for item in catalog if item["name"] == "generate_flowchart")
        mindmap_tool = next(item for item in catalog if item["name"] == "generate_mindmap")
        concept_map_tool = next(item for item in catalog if item["name"] == "generate_concept_map")
        assert flowchart_tool["channel_suitability"] == "summary_plus_link"
        assert mindmap_tool["channel_suitability"] == "summary_plus_link"
        assert concept_map_tool["channel_suitability"] == "summary_plus_link"

    def test_tier_4_5_feature_matrix_is_complete(self):
        matrix = serialize_tier_4_5_feature_matrix()
        incomplete = [item for item in matrix if item["status"] != "complete"]
        assert incomplete == []

    def test_tier_4_5_feature_matrix_covers_ai_assistant_roles_for_study_guide(self):
        matrix = serialize_tier_4_5_feature_matrix()
        study_guide = next(item for item in matrix if item["feature_key"] == "study_guide")
        assert study_guide["required_roles"] == ["admin", "parent", "student", "teacher"]
        assert study_guide["tools"][0]["missing_roles"] == []


# ─── Intent Classification Tests ──────────────────────────────

class TestAsyncJobNotifications:
    def test_format_completed_ai_job_status_message(self):
        message = format_ai_job_status_message({
            "status": "completed",
            "job_id": "job-123",
            "job_type": "query",
            "request": {"query": "photosynthesis"},
        })
        assert "ready" in message.lower()
        assert "photosynthesis" in message
        assert "job-123" in message

    def test_format_failed_ai_job_status_message(self):
        message = format_ai_job_status_message({
            "status": "failed",
            "job_id": "job-456",
            "job_type": "audio",
            "request": {"topic": "atoms"},
            "error": "worker timeout",
        })
        assert "failed" in message.lower()
        assert "atoms" in message
        assert "worker timeout" in message

    def test_format_completed_media_ingest_job_status_message_uses_result_text(self):
        message = format_ai_job_status_message({
            "status": "completed",
            "job_id": "job-789",
            "job_type": "whatsapp_media_ingest",
            "request": {"display_name": "lesson.mp4"},
            "result": {"response_text": "Received *lesson.mp4* and added it to your knowledge base."},
        })
        assert message == "Received *lesson.mp4* and added it to your knowledge base."


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

    def test_teacher_generate_quiz_intent(self):
        result = _classify_intent_heuristic("Generate quiz for class 8 science", "teacher")
        assert result == "generate_quiz"

    def test_student_generate_study_guide_intent(self):
        result = _classify_intent_heuristic("Generate study guide for photosynthesis", "student")
        assert result == "generate_study_guide"

    def test_student_generate_audio_overview_intent(self):
        result = _classify_intent_heuristic("Create audio overview for photosynthesis", "student")
        assert result == "generate_audio_overview"

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

    def test_extract_topic_from_generate_quiz_message(self):
        topic = _extract_topic_from_message("Generate quiz for class 8 science")
        assert topic == "class 8 science"

    def test_extract_topic_from_generate_study_guide_message(self):
        topic = _extract_topic_from_message("Generate study guide for photosynthesis")
        assert topic == "photosynthesis"

    def test_extract_topic_from_generate_audio_overview_message(self):
        topic = _extract_topic_from_message("Create audio overview for photosynthesis")
        assert topic == "photosynthesis"


class TestLlmIntentInterpretation:
    def test_classify_intent_uses_llm_translation_for_mixed_language_flashcards(self):
        fake_provider = SimpleNamespace(
            generate_structured=AsyncMock(
                return_value={
                    "response": {
                        "normalized_message": "mala flashcards pahije photosynthesis var",
                        "translated_message": "Create flashcards for photosynthesis",
                        "tool_name": "generate_flashcards",
                        "question": "Create flashcards for photosynthesis",
                        "topic": "photosynthesis",
                        "is_general_chat": False,
                    }
                }
            )
        )
        state: WhatsAppAgentState = {
            "message": "mala flashcards pahije photosynthesis var",
            "user_id": str(uuid4()),
            "tenant_id": str(uuid4()),
            "role": "student",
            "conversation_history": [],
            "intent": None,
            "tool_name": None,
            "tool_args": None,
            "tool_result": None,
            "response": None,
            "response_type": "text",
        }

        with patch("src.infrastructure.llm.providers.get_llm_provider", return_value=fake_provider):
            result = classify_intent(state)

        assert result["tool_name"] == "generate_flashcards"
        assert result["tool_args"]["topic"] == "photosynthesis"
        assert result["tool_args"]["translated_message"] == "Create flashcards for photosynthesis"
        fake_provider.generate_structured.assert_awaited_once()

    def test_classify_intent_requests_clarification_for_missing_topic(self):
        state: WhatsAppAgentState = {
            "message": "quiz bana",
            "user_id": str(uuid4()),
            "tenant_id": str(uuid4()),
            "notebook_id": None,
            "role": "student",
            "conversation_history": [],
            "intent": None,
            "tool_name": None,
            "tool_args": None,
            "tool_result": None,
            "response": None,
            "response_type": "text",
        }

        result = classify_intent(state)

        assert result["intent"] == "clarify_request"
        assert result["tool_name"] is None
        assert result["tool_args"]["clarification_reason"] == "missing_topic"
        assert "topic" in result["tool_args"]["clarification_prompt"].lower()

    def test_classify_intent_requests_clarification_for_conflicting_study_tools(self):
        state: WhatsAppAgentState = {
            "message": "quiz or flashcards bana photosynthesis par",
            "user_id": str(uuid4()),
            "tenant_id": str(uuid4()),
            "notebook_id": None,
            "role": "student",
            "conversation_history": [],
            "intent": None,
            "tool_name": None,
            "tool_args": None,
            "tool_result": None,
            "response": None,
            "response_type": "text",
        }

        result = classify_intent(state)

        assert result["intent"] == "clarify_request"
        assert result["tool_args"]["clarification_reason"] == "multiple_study_tools"
        assert "choose one format" in result["tool_args"]["clarification_prompt"].lower()

    def test_generate_response_returns_clarification_prompt_directly(self):
        state: WhatsAppAgentState = {
            "message": "quiz bana",
            "user_id": str(uuid4()),
            "tenant_id": str(uuid4()),
            "notebook_id": None,
            "role": "student",
            "conversation_history": [],
            "intent": "clarify_request",
            "tool_name": None,
            "tool_args": {
                "clarification_prompt": "Tell me the topic too. Example: *quiz on photosynthesis*.",
                "clarification_reason": "missing_topic",
            },
            "tool_result": None,
            "response": None,
            "response_type": "text",
        }

        result = generate_response(state)
        assert result["response"].startswith("Tell me the topic too.")

    def test_execute_tool_maps_generate_quiz_alias_to_direct_whatsapp_tool(self):
        fake_tool = SimpleNamespace(
            name="generate_quiz_now",
            invoke=MagicMock(return_value="Quiz ready"),
        )
        state: WhatsAppAgentState = {
            "message": "Generate quiz for photosynthesis",
            "user_id": str(uuid4()),
            "tenant_id": str(uuid4()),
            "notebook_id": str(uuid4()),
            "role": "student",
            "conversation_history": [],
            "intent": "generate_quiz",
            "tool_name": "generate_quiz",
            "tool_args": {"topic": "photosynthesis"},
            "tool_result": None,
            "response": None,
            "response_type": "text",
        }

        with patch("src.shared.ai_tools.whatsapp_tools.authorize_tool", return_value=True), patch(
            "src.shared.ai_tools.whatsapp_tools.ALL_WHATSAPP_TOOLS",
            [fake_tool],
        ):
            result = execute_tool(state)

        assert result["tool_result"] == "Quiz ready"
        fake_tool.invoke.assert_called_once_with(
            {
                "user_id": state["user_id"],
                "tenant_id": state["tenant_id"],
                "topic": "photosynthesis",
                "notebook_id": state["notebook_id"],
            }
        )

    def test_execute_tool_passes_notebook_id_to_audio_overview(self):
        fake_tool = SimpleNamespace(
            name="generate_audio_overview",
            invoke=MagicMock(return_value="Audio queued"),
        )
        state: WhatsAppAgentState = {
            "message": "Create audio overview for photosynthesis",
            "user_id": str(uuid4()),
            "tenant_id": str(uuid4()),
            "notebook_id": str(uuid4()),
            "role": "student",
            "conversation_history": [],
            "intent": "generate_audio_overview",
            "tool_name": "generate_audio_overview",
            "tool_args": {"topic": "photosynthesis"},
            "tool_result": None,
            "response": None,
            "response_type": "text",
        }

        with patch("src.shared.ai_tools.whatsapp_tools.authorize_tool", return_value=True), patch(
            "src.shared.ai_tools.whatsapp_tools.ALL_WHATSAPP_TOOLS",
            [fake_tool],
        ):
            result = execute_tool(state)

        assert result["tool_result"] == "Audio queued"
        fake_tool.invoke.assert_called_once_with(
            {
                "user_id": state["user_id"],
                "tenant_id": state["tenant_id"],
                "topic": "photosynthesis",
                "notebook_id": state["notebook_id"],
            }
        )


class TestWhatsAppFormatting:
    def test_flowchart_whatsapp_payload_hides_raw_mermaid(self):
        result = _format_study_tool_payload(
            "flowchart",
            "Photosynthesis",
            {
                "data": {
                    "mermaid": "flowchart TD\nA[Light] --> B[Glucose]",
                    "steps": [
                        {"label": "Capture light", "detail": "Leaves absorb sunlight.", "citation": "Biology p.10"},
                        {"label": "Make glucose", "detail": "Plants produce glucose.", "citation": "Biology p.11"},
                    ],
                },
                "citations": [{"source": "Biology Textbook"}],
            },
        )

        assert "flowchart TD" not in result
        assert "Capture light" in result
        assert "Open the web app for the full visual diagram." in result

    def test_format_for_whatsapp_keeps_long_text_for_router_chunking(self):
        long_text = "A" * 5000
        state: WhatsAppAgentState = {
            "message": "Explain this",
            "user_id": str(uuid4()),
            "tenant_id": str(uuid4()),
            "notebook_id": None,
            "role": "student",
            "conversation_history": [],
            "intent": None,
            "tool_name": None,
            "tool_args": None,
            "tool_result": None,
            "response": long_text,
            "response_type": "text",
        }

        result = format_for_whatsapp(state)
        assert result["response"] == long_text


class TestInteractiveReplyExtraction:
    def test_extract_messages_prefers_interactive_reply_id(self):
        payload = {
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "type": "interactive",
                            "from": "919876543210",
                            "id": "wamid-1",
                            "interactive": {
                                "list_reply": {
                                    "id": "child:abc123",
                                    "title": "Aarav",
                                }
                            },
                        }]
                    }
                }]
            }]
        }

        messages = _extract_messages(payload)
        assert messages[0]["text"] == "child:abc123"

    def test_extract_messages_includes_document_media_metadata(self):
        payload = {
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "type": "document",
                            "from": "919876543210",
                            "id": "wamid-doc",
                            "document": {
                                "id": "media-123",
                                "filename": "biology_notes.pdf",
                                "mime_type": "application/pdf",
                                "caption": "biology notes",
                            },
                        }]
                    }
                }]
            }]
        }

        messages = _extract_messages(payload)
        assert messages[0]["message_type"] == "document"
        assert messages[0]["media_id"] == "media-123"
        assert messages[0]["media_filename"] == "biology_notes.pdf"
        assert messages[0]["text"] == "biology notes"


class TestReportCardDelivery:
    def test_build_report_card_response_returns_document_payload(self):
        child_id = str(uuid4())
        session = {
            "phone": "919876543210",
            "user_id": str(uuid4()),
            "tenant_id": str(uuid4()),
            "role": "parent",
            "active_child_id": child_id,
        }
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = SimpleNamespace(full_name="Aarav Sharma")
        with patch("src.domains.platform.services.whatsapp_gateway._create_report_card_token", return_value="token-123"), \
             patch("src.domains.platform.services.whatsapp_gateway.settings.auth.saml_sp_base_url", "https://vidyaos.app"):
            response = _build_report_card_response(db, session)

        assert response["response_type"] == "document"
        assert response["document_link"].endswith("/api/v1/whatsapp/report-card/token-123")
        assert response["document_filename"].endswith(".pdf")

    async def test_whatsapp_report_card_download_uses_token_payload(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = SimpleNamespace(name="VidyaOS School")
        with patch("src.domains.platform.routes.whatsapp.consume_report_card_token", return_value={
            "tenant_id": str(uuid4()),
            "child_id": str(uuid4()),
        }), patch("src.domains.platform.routes.whatsapp._generate_report_card_pdf", return_value=b"%PDF-1.4"):
            response = await whatsapp_report_card_download("token-123", db=db)

        assert response.media_type == "application/pdf"


class TestDocumentMessages:
    def test_send_message_request_requires_document_fields(self):
        with pytest.raises(ValueError):
            SendMessageRequest(phone="919876543210", message="Report card", message_type="document")

    def test_send_message_request_accepts_document_fields(self):
        request = SendMessageRequest(
            phone="919876543210",
            message="Report card ready",
            message_type="document",
            document_link="https://example.com/report.pdf",
            document_filename="report_card.pdf",
        )
        assert request.document_filename == "report_card.pdf"

    async def test_dispatch_outbound_document_response(self):
        with patch("src.domains.platform.routes.whatsapp.send_document_message", new_callable=AsyncMock) as send_document:
            send_document.return_value = {"success": True}
            await _dispatch_outbound_response("919876543210", {
                "response_type": "document",
                "response_text": "📄 Your report is ready",
                "document_link": "https://example.com/report.pdf",
                "document_filename": "report_card.pdf",
                "document_caption": "📄 Report card",
            })

        send_document.assert_awaited_once()

    async def test_dispatch_outbound_text_response_chunks_long_messages(self):
        long_text = ("Photosynthesis summary paragraph.\n\n" * 120).strip()
        with patch("src.domains.platform.routes.whatsapp.send_text_message", new_callable=AsyncMock) as send_text:
            send_text.return_value = {"success": True}
            await _dispatch_outbound_response("919876543210", {
                "response_type": "text",
                "response_text": long_text,
            })

        assert send_text.await_count >= 2
        for call in send_text.await_args_list:
            assert len(call.args[1]) <= 1500

    def test_chunk_whatsapp_text_splits_paragraphs_without_empty_chunks(self):
        long_text = ("Cell respiration explanation.\n\n" * 100).strip()
        chunks = _chunk_whatsapp_text(long_text, chunk_size=500)
        assert len(chunks) >= 2
        assert all(chunk.strip() for chunk in chunks)
        assert all(len(chunk) <= 500 for chunk in chunks)

    async def test_send_text_message_marks_429_as_retryable(self, mock_redis):
        fake_redis, storage = mock_redis
        request = httpx.Request("POST", "https://graph.facebook.com/v18.0/messages")
        response = httpx.Response(429, request=request, text="rate limited")
        error = httpx.HTTPStatusError("429 Too Many Requests", request=request, response=response)

        class FakeClient:
            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc, tb):
                return False

            async def post(self, *args, **kwargs):
                raise error

        with patch("src.domains.platform.services.whatsapp_gateway.WHATSAPP_TOKEN", "token"), \
             patch("src.domains.platform.services.whatsapp_gateway.WHATSAPP_PHONE_ID", "phone-id"), \
             patch("src.domains.platform.services.whatsapp_gateway.httpx.AsyncClient", return_value=FakeClient()):
            result = await send_text_message("919876543210", "Hello")

        assert result["success"] is False
        assert result["retryable"] is True
        assert result["error_type"] == "http_retryable"
        assert result["status_code"] == 429
        metrics = get_whatsapp_metrics()
        assert metrics["outbound_failure_total"] == 1
        assert metrics["outbound_retryable_failure_total"] == 1

    async def test_send_text_message_marks_400_as_non_retryable(self, mock_redis):
        fake_redis, storage = mock_redis
        request = httpx.Request("POST", "https://graph.facebook.com/v18.0/messages")
        response = httpx.Response(400, request=request, text="bad request")
        error = httpx.HTTPStatusError("400 Bad Request", request=request, response=response)

        class FakeClient:
            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc, tb):
                return False

            async def post(self, *args, **kwargs):
                raise error

        with patch("src.domains.platform.services.whatsapp_gateway.WHATSAPP_TOKEN", "token"), \
             patch("src.domains.platform.services.whatsapp_gateway.WHATSAPP_PHONE_ID", "phone-id"), \
             patch("src.domains.platform.services.whatsapp_gateway.httpx.AsyncClient", return_value=FakeClient()):
            result = await send_text_message("919876543210", "Hello")

        assert result["success"] is False
        assert result["retryable"] is False
        assert result["error_type"] == "http_non_retryable"
        assert result["status_code"] == 400
        metrics = get_whatsapp_metrics()
        assert metrics["outbound_failure_total"] == 1
        assert metrics["outbound_non_retryable_failure_total"] == 1

    async def test_send_text_message_records_success_metric(self, mock_redis):
        fake_redis, storage = mock_redis

        class FakeClient:
            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc, tb):
                return False

            async def post(self, *args, **kwargs):
                return SimpleNamespace(
                    raise_for_status=lambda: None,
                    json=lambda: {"messages": [{"id": "wamid-out-1"}]},
                )

        with patch("src.domains.platform.services.whatsapp_gateway.WHATSAPP_TOKEN", "token"), \
             patch("src.domains.platform.services.whatsapp_gateway.WHATSAPP_PHONE_ID", "phone-id"), \
             patch("src.domains.platform.services.whatsapp_gateway.httpx.AsyncClient", return_value=FakeClient()):
            result = await send_text_message("919876543210", "Hello")

        assert result["success"] is True
        metrics = get_whatsapp_metrics()
        assert metrics["outbound_success_total"] == 1


# ─── Webhook Endpoint Tests ──────────────────────────────────

class TestWebhookEndpoints:
    async def test_webhook_verification_success(self):
        """Meta verification handshake should succeed with correct token."""
        response = await whatsapp_webhook_verify(
            request=SimpleNamespace(),
            hub_mode="subscribe",
            hub_verify_token="vidyaos-wa-verify",
            hub_challenge="12345",
        )
        assert response == 12345

    async def test_webhook_verification_failure(self):
        """Meta verification should fail with wrong token."""
        with pytest.raises(Exception) as exc:
            await whatsapp_webhook_verify(
                request=SimpleNamespace(),
                hub_mode="subscribe",
                hub_verify_token="wrong-token",
                hub_challenge="12345",
            )
        assert getattr(exc.value, "status_code", None) == 403

    async def test_webhook_inbound_invalid_signature(self):
        """Inbound webhook should reject invalid signatures."""
        from src.domains.platform.services import whatsapp_gateway
        whatsapp_gateway.WHATSAPP_APP_SECRET = "real-secret"

        class FakeRequest:
            headers = {"X-Hub-Signature-256": "sha256=invalid"}

            async def body(self):
                return b'{"entry": []}'

            async def json(self):
                return {"entry": []}

        with pytest.raises(Exception) as exc:
            await whatsapp_webhook_inbound(
                request=FakeRequest(),
                background_tasks=SimpleNamespace(add_task=lambda *args, **kwargs: None),
            )
        assert getattr(exc.value, "status_code", None) == 403

        # Reset
        whatsapp_gateway.WHATSAPP_APP_SECRET = ""

    async def test_webhook_inbound_schedules_document_message_without_caption(self):
        payload = {
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "type": "document",
                            "from": "919876543210",
                            "id": "wamid-doc",
                            "document": {
                                "id": "media-123",
                                "filename": "biology_notes.pdf",
                                "mime_type": "application/pdf",
                            },
                        }]
                    }
                }]
            }]
        }
        scheduled = []

        class FakeRequest:
            headers = {"X-Hub-Signature-256": ""}

            async def body(self):
                return json.dumps(payload).encode("utf-8")

            async def json(self):
                return payload

        background_tasks = SimpleNamespace(add_task=lambda fn, **kwargs: scheduled.append((fn, kwargs)))
        with patch("src.domains.platform.routes.whatsapp.verify_webhook_signature", return_value=True):
            result = await whatsapp_webhook_inbound(request=FakeRequest(), background_tasks=background_tasks)

        assert result == {"status": "ok"}
        assert len(scheduled) == 1
        assert scheduled[0][1]["message_type"] == "document"
        assert scheduled[0][1]["media_id"] == "media-123"
        assert scheduled[0][1]["media_filename"] == "biology_notes.pdf"


class TestToolCatalogEndpoint:
    def test_admin_can_get_full_tool_catalog(self):
        current_user = SimpleNamespace(role="admin")
        result = asyncio.run(whatsapp_tool_catalog(current_user=current_user, role=None))
        assert "tools" in result
        assert any(tool["name"] == "get_student_timetable" for tool in result["tools"])

    def test_admin_can_filter_tool_catalog_by_role(self):
        current_user = SimpleNamespace(role="admin")
        result = asyncio.run(whatsapp_tool_catalog(current_user=current_user, role="parent"))
        tool_names = [tool["name"] for tool in result["tools"]]
        assert "get_child_attendance" in tool_names
        assert "get_student_timetable" not in tool_names

    def test_non_admin_cannot_get_tool_catalog(self):
        current_user = SimpleNamespace(role="teacher")
        with pytest.raises(Exception) as exc:
            asyncio.run(whatsapp_tool_catalog(current_user=current_user, role=None))
        assert getattr(exc.value, "status_code", None) == 403


class TestAdminManualSend:
    def test_admin_text_send_uses_notification_dispatch_for_linked_phone(self):
        current_user = SimpleNamespace(id=uuid4(), tenant_id=uuid4(), role="admin")
        linked_user = SimpleNamespace(user_id=uuid4())
        fake_query = MagicMock()
        fake_query.filter.return_value.first.return_value = linked_user
        db = MagicMock()
        db.query.return_value = fake_query

        with patch("src.domains.platform.routes.whatsapp.dispatch_notification", new=AsyncMock(return_value=[
            {"channel": "whatsapp", "status": "delivered"},
            {"channel": "in_app", "status": "sent"},
        ])) as dispatch_mock, patch("src.domains.platform.routes.whatsapp.log_message") as log_mock:
            result = asyncio.run(
                admin_send_message(
                    SendMessageRequest(phone="919876543210", message="School closed tomorrow", message_type="text"),
                    current_user=current_user,
                    db=db,
                )
            )

        assert result["success"] is True
        assert result["routed_via"] == "notification_dispatch"
        dispatch_mock.assert_awaited_once()
        log_mock.assert_called_once()


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


class TestMediaIngestion:
    async def test_ingest_whatsapp_media_upload_queues_video_transcription_job(self):
        from src.domains.platform.services import whatsapp_gateway as whatsapp_mod

        tenant_id = str(uuid4())
        user_id = str(uuid4())
        notebook = SimpleNamespace(id=uuid4())

        class _DBStub:
            def add(self, obj):
                if getattr(obj, "id", None) is None:
                    obj.id = uuid4()

            def commit(self):
                return None

            def refresh(self, obj):
                if getattr(obj, "id", None) is None:
                    obj.id = uuid4()

        db = _DBStub()

        with patch.object(whatsapp_mod, "_download_whatsapp_media", new=AsyncMock(return_value=(b"video-bytes", "video/mp4"))), \
             patch.object(whatsapp_mod, "_create_whatsapp_notebook", return_value=notebook), \
             patch("builtins.open", mock_open()), \
             patch("src.domains.platform.services.ai_queue.enqueue_job", return_value={"job_id": "job-123"}) as enqueue_mock:
            payload = await whatsapp_mod._ingest_whatsapp_media_upload(
                db,
                user_id=user_id,
                tenant_id=tenant_id,
                media_id="media-video-123",
                message_type="video",
                text="Explain the key ideas",
                media_filename="lesson.mp4",
                media_mime_type="video/mp4",
            )

        assert payload["status"] == "queued"
        assert payload["ingestion_mode"] == "async"
        assert payload["job_id"] == "job-123"
        assert "queued transcript extraction" in payload["response_text"].lower()
        enqueue_mock.assert_called_once()
        queued_payload = enqueue_mock.call_args.args[1]
        assert queued_payload["follow_up_message"] == "Explain the key ideas"
        assert queued_payload["follow_up_user_id"] == user_id

    async def test_execute_whatsapp_media_ingestion_runs_deferred_follow_up(self):
        from src.domains.platform.schemas.ai_runtime import InternalWhatsAppMediaIngestRequest
        from src.interfaces.rest_api.ai import ingestion_workflows

        document = SimpleNamespace(
            id=uuid4(),
            tenant_id=uuid4(),
            notebook_id=uuid4(),
            ingestion_status="processing",
            chunk_count=0,
        )
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = document
        embedding_provider = SimpleNamespace(embed_batch=AsyncMock(return_value=[[0.1, 0.2]]))
        vector_store = SimpleNamespace(add_chunks=MagicMock())
        fake_chunk = SimpleNamespace(
            text="Transcript chunk",
            document_id="doc-1",
            page_number=1,
            section_title="Transcript",
            subject_id="",
            notebook_id=str(document.notebook_id),
            source_file="lesson.mp4",
        )

        request = InternalWhatsAppMediaIngestRequest(
            document_id=str(document.id),
            file_path="C:/tmp/lesson.mp4",
            display_name="lesson.mp4",
            media_kind="video",
            follow_up_message="Explain the key ideas",
            follow_up_user_id="11111111-1111-1111-1111-111111111111",
            role="student",
            conversation_history=[{"role": "user", "content": "earlier context"}],
            tenant_id=str(document.tenant_id),
        )

        with patch.object(ingestion_workflows, "SessionLocal", return_value=db), \
             patch("src.infrastructure.vector_store.ingestion.ingest_media_transcript", return_value=[fake_chunk]), \
             patch("src.infrastructure.llm.providers.get_embedding_provider", return_value=embedding_provider), \
             patch("src.infrastructure.llm.providers.get_vector_store_provider", return_value=vector_store), \
             patch.object(ingestion_workflows, "invalidate_tenant_cache"), \
             patch("src.interfaces.whatsapp_bot.agent.run_whatsapp_agent", new=AsyncMock(return_value={
                 "response": "Here is a grounded answer from the transcript.",
                 "intent": "ask_ai_question",
                 "tool_name": "ask_ai_question",
             })) as agent_mock:
            payload = await ingestion_workflows.execute_whatsapp_media_ingestion(request)

        assert payload["status"] == "completed"
        assert "grounded answer from the transcript" in payload["response_text"].lower()
        agent_mock.assert_awaited_once_with(
            message="Explain the key ideas",
            user_id="11111111-1111-1111-1111-111111111111",
            tenant_id=str(document.tenant_id),
            role="student",
            notebook_id=str(document.notebook_id),
            conversation_history=[{"role": "user", "content": "earlier context"}],
            session_id=None,
            pending_confirmation_id=None,
        )

    async def test_process_inbound_message_routes_media_uploads_to_ingestion_pipeline(self):
        link = SimpleNamespace(user_id=uuid4(), tenant_id=uuid4())
        session = {
            "phone": "919876543210",
            "user_id": str(link.user_id),
            "tenant_id": str(link.tenant_id),
            "role": "student",
            "active_child_id": None,
            "active_notebook_id": None,
            "conversation_history": [],
        }
        db = MagicMock()
        media_result = {
            "response_text": "Received *biology_notes.pdf* and added it to your knowledge base.",
            "response_type": "text",
            "intent": "media_upload",
            "tool_name": "ingest_whatsapp_media",
            "notebook_id": str(uuid4()),
        }

        with patch("src.domains.platform.services.whatsapp_gateway.resolve_phone_to_user", return_value=link), \
             patch("src.domains.platform.services.whatsapp_gateway.get_session", return_value=session), \
             patch("src.domains.platform.services.whatsapp_gateway._ingest_whatsapp_media_upload", new=AsyncMock(return_value=media_result)) as ingest_mock, \
             patch("src.domains.platform.services.whatsapp_gateway.save_session") as save_mock, \
             patch("src.domains.platform.services.whatsapp_gateway.log_message") as log_mock:
            result = await process_inbound_message(
                db,
                "919876543210",
                "biology notes",
                wa_message_id="wamid-doc",
                message_type="document",
                media_id="media-123",
                media_filename="biology_notes.pdf",
                media_mime_type="application/pdf",
            )

        assert result["response_text"] == media_result["response_text"]
        ingest_mock.assert_awaited_once_with(
            db,
            user_id=str(link.user_id),
            tenant_id=str(link.tenant_id),
            media_id="media-123",
            message_type="document",
            text="biology notes",
            media_filename="biology_notes.pdf",
            media_mime_type="application/pdf",
            role="student",
            follow_up_user_id=str(link.user_id),
            conversation_history=[],
        )
        save_mock.assert_called_once()
        assert session["active_notebook_id"] == media_result["notebook_id"]
        assert any(call.kwargs.get("message_type") == "document" for call in log_mock.call_args_list)

    async def test_process_inbound_message_passes_active_notebook_id_to_agent(self, mock_redis):
        fake_redis, storage = mock_redis
        link = SimpleNamespace(user_id=uuid4(), tenant_id=uuid4())
        session = {
            "phone": "919876543210",
            "session_id": "ws-scope-123",
            "user_id": str(link.user_id),
            "tenant_id": str(link.tenant_id),
            "role": "student",
            "active_child_id": None,
            "active_notebook_id": str(uuid4()),
            "conversation_history": [],
        }
        db = MagicMock()

        with patch("src.domains.platform.services.whatsapp_gateway.resolve_phone_to_user", return_value=link), \
             patch("src.domains.platform.services.whatsapp_gateway.get_session", return_value=session), \
             patch("src.interfaces.whatsapp_bot.agent.run_whatsapp_agent", new=AsyncMock(return_value={
                 "response": "Scoped answer",
                 "response_type": "text",
                 "intent": "ask_ai_question",
                 "tool_name": "ask_ai_question",
             })) as agent_mock, \
             patch("src.domains.platform.services.whatsapp_gateway.save_session"), \
             patch("src.domains.platform.services.whatsapp_gateway.log_message"):
            result = await process_inbound_message(db, "919876543210", "Explain my uploaded notes")

        assert result["response_text"] == "Scoped answer"
        agent_mock.assert_awaited_once_with(
            message="Explain my uploaded notes",
            user_id=str(link.user_id),
            tenant_id=str(link.tenant_id),
            role="student",
            notebook_id=session["active_notebook_id"],
            conversation_history=[],
            session_id=session["session_id"],
            pending_confirmation_id=session.get("pending_mascot_confirmation_id"),
        )
        metrics = get_whatsapp_metrics(str(link.tenant_id))
        assert metrics["inbound_total"] == 1
        assert metrics["routing_success_total"] == 1

    async def test_process_inbound_message_stores_pending_mascot_confirmation(self, mock_redis):
        fake_redis, storage = mock_redis
        link = SimpleNamespace(user_id=uuid4(), tenant_id=uuid4())
        session = {
            "phone": "919876543210",
            "session_id": "ws-confirm-123",
            "user_id": str(link.user_id),
            "tenant_id": str(link.tenant_id),
            "role": "student",
            "active_child_id": None,
            "active_notebook_id": None,
            "conversation_history": [],
        }
        db = MagicMock()

        with patch("src.domains.platform.services.whatsapp_gateway.resolve_phone_to_user", return_value=link), \
             patch("src.domains.platform.services.whatsapp_gateway.get_session", return_value=session), \
             patch("src.interfaces.whatsapp_bot.agent.run_whatsapp_agent", new=AsyncMock(return_value={
                 "response": "Please confirm before I archive that notebook.\n\nReply *CONFIRM* to continue or *CANCEL* to stop.",
                 "response_type": "text",
                 "intent": "notebook_update",
                 "tool_name": "notebook_update",
                 "requires_confirmation": True,
                 "confirmation_id": "mascot-confirm-123",
                 "confirmation_cleared": False,
                 "notebook_id": None,
             })), \
             patch("src.domains.platform.services.whatsapp_gateway.save_session") as save_mock, \
             patch("src.domains.platform.services.whatsapp_gateway.log_message"):
            result = await process_inbound_message(db, "919876543210", "Delete Biology notebook")

        assert result["response_text"].startswith("Please confirm")
        saved_session = save_mock.call_args.args[2]
        assert saved_session["pending_mascot_confirmation_id"] == "mascot-confirm-123"

    async def test_process_inbound_message_clears_pending_mascot_confirmation_after_confirm(self, mock_redis):
        fake_redis, storage = mock_redis
        link = SimpleNamespace(user_id=uuid4(), tenant_id=uuid4())
        session = {
            "phone": "919876543210",
            "session_id": "ws-confirm-456",
            "user_id": str(link.user_id),
            "tenant_id": str(link.tenant_id),
            "role": "student",
            "active_child_id": None,
            "active_notebook_id": None,
            "pending_mascot_confirmation_id": "mascot-confirm-456",
            "conversation_history": [],
        }
        db = MagicMock()

        with patch("src.domains.platform.services.whatsapp_gateway.resolve_phone_to_user", return_value=link), \
             patch("src.domains.platform.services.whatsapp_gateway.get_session", return_value=session), \
             patch("src.interfaces.whatsapp_bot.agent.run_whatsapp_agent", new=AsyncMock(return_value={
                 "response": "Archived notebook 'Biology'.",
                 "response_type": "text",
                 "intent": "confirm",
                 "tool_name": "confirm",
                 "requires_confirmation": False,
                 "confirmation_id": None,
                 "confirmation_cleared": True,
                 "notebook_id": None,
             })), \
             patch("src.domains.platform.services.whatsapp_gateway.save_session") as save_mock, \
             patch("src.domains.platform.services.whatsapp_gateway.log_message"):
            result = await process_inbound_message(db, "919876543210", "confirm")

        assert result["response_text"] == "Archived notebook 'Biology'."
        saved_session = save_mock.call_args.args[2]
        assert "pending_mascot_confirmation_id" not in saved_session

    async def test_process_inbound_message_updates_active_notebook_from_mascot_result(self, mock_redis):
        fake_redis, storage = mock_redis
        link = SimpleNamespace(user_id=uuid4(), tenant_id=uuid4())
        notebook_id = str(uuid4())
        session = {
            "phone": "919876543210",
            "session_id": "ws-notebook-123",
            "user_id": str(link.user_id),
            "tenant_id": str(link.tenant_id),
            "role": "student",
            "active_child_id": None,
            "active_notebook_id": None,
            "conversation_history": [],
        }
        db = MagicMock()

        with patch("src.domains.platform.services.whatsapp_gateway.resolve_phone_to_user", return_value=link), \
             patch("src.domains.platform.services.whatsapp_gateway.get_session", return_value=session), \
             patch("src.interfaces.whatsapp_bot.agent.run_whatsapp_agent", new=AsyncMock(return_value={
                 "response": "Created notebook 'Biology Chapter 10'.",
                 "response_type": "text",
                 "intent": "notebook_create",
                 "tool_name": "notebook_create",
                 "requires_confirmation": False,
                 "confirmation_id": None,
                 "confirmation_cleared": False,
                 "notebook_id": notebook_id,
             })), \
             patch("src.domains.platform.services.whatsapp_gateway.save_session") as save_mock, \
             patch("src.domains.platform.services.whatsapp_gateway.log_message"):
            result = await process_inbound_message(db, "919876543210", "Create notebook for Biology Chapter 10")

        assert result["response_text"] == "Created notebook 'Biology Chapter 10'."
        saved_session = save_mock.call_args.args[2]
        assert saved_session["active_notebook_id"] == notebook_id

    async def test_process_inbound_message_reuses_mascot_created_notebook_on_next_turn(self, mock_redis):
        fake_redis, storage = mock_redis
        link = SimpleNamespace(user_id=uuid4(), tenant_id=uuid4())
        notebook_id = str(uuid4())
        session = {
            "phone": "919876543210",
            "session_id": "ws-notebook-chain",
            "user_id": str(link.user_id),
            "tenant_id": str(link.tenant_id),
            "role": "student",
            "active_child_id": None,
            "active_notebook_id": None,
            "conversation_history": [],
        }
        db = MagicMock()
        agent_mock = AsyncMock(
            side_effect=[
                {
                    "response": "Created notebook 'Biology Chapter 10'.",
                    "response_type": "text",
                    "intent": "notebook_create",
                    "tool_name": "notebook_create",
                    "requires_confirmation": False,
                    "confirmation_id": None,
                    "confirmation_cleared": False,
                    "notebook_id": notebook_id,
                },
                {
                    "response": "Scoped answer",
                    "response_type": "text",
                    "intent": "ask_ai_question",
                    "tool_name": "ask_ai_question",
                    "requires_confirmation": False,
                    "confirmation_id": None,
                    "confirmation_cleared": False,
                    "notebook_id": notebook_id,
                },
            ]
        )

        with patch("src.domains.platform.services.whatsapp_gateway.resolve_phone_to_user", return_value=link), \
             patch("src.domains.platform.services.whatsapp_gateway.get_session", return_value=session), \
             patch("src.interfaces.whatsapp_bot.agent.run_whatsapp_agent", new=agent_mock), \
             patch("src.domains.platform.services.whatsapp_gateway.save_session"), \
             patch("src.domains.platform.services.whatsapp_gateway.log_message"):
            first = await process_inbound_message(db, "919876543210", "Create notebook for Biology Chapter 10")
            second = await process_inbound_message(db, "919876543210", "Explain photosynthesis")

        assert first["response_text"] == "Created notebook 'Biology Chapter 10'."
        assert second["response_text"] == "Scoped answer"
        assert session["active_notebook_id"] == notebook_id
        second_call = agent_mock.await_args_list[1]
        assert second_call.kwargs["notebook_id"] == notebook_id

    async def test_process_inbound_message_answers_follow_up_from_media_caption(self):
        link = SimpleNamespace(user_id=uuid4(), tenant_id=uuid4())
        notebook_id = str(uuid4())
        session = {
            "phone": "919876543210",
            "user_id": str(link.user_id),
            "tenant_id": str(link.tenant_id),
            "role": "student",
            "active_child_id": None,
            "active_notebook_id": None,
            "conversation_history": [],
        }
        db = MagicMock()
        media_result = {
            "response_text": "Received *biology_notes.pdf* and added it to your knowledge base.",
            "response_type": "text",
            "intent": "media_upload",
            "tool_name": "ingest_whatsapp_media",
            "notebook_id": notebook_id,
        }

        with patch("src.domains.platform.services.whatsapp_gateway.resolve_phone_to_user", return_value=link), \
             patch("src.domains.platform.services.whatsapp_gateway.get_session", return_value=session), \
             patch("src.domains.platform.services.whatsapp_gateway._ingest_whatsapp_media_upload", new=AsyncMock(return_value=media_result)), \
             patch("src.domains.platform.services.whatsapp_gateway._run_post_ingest_follow_up", new=AsyncMock(return_value={
                 "response": "Here is a grounded summary from your uploaded notes.",
                 "intent": "ask_ai_question",
                 "tool_name": "ask_ai_question",
             })) as follow_up_mock, \
             patch("src.domains.platform.services.whatsapp_gateway.save_session"), \
             patch("src.domains.platform.services.whatsapp_gateway.log_message"):
            result = await process_inbound_message(
                db,
                "919876543210",
                "Explain this chapter briefly",
                wa_message_id="wamid-doc-followup",
                message_type="document",
                media_id="media-123",
                media_filename="biology_notes.pdf",
                media_mime_type="application/pdf",
            )

        assert "Received *biology_notes.pdf*" in result["response_text"]
        assert "Here is a grounded summary" in result["response_text"]
        assert session["active_notebook_id"] == notebook_id
        follow_up_mock.assert_awaited_once()
        kwargs = follow_up_mock.await_args.kwargs
        assert kwargs["message"] == "Explain this chapter briefly"
        assert kwargs["user_id"] == str(link.user_id)
        assert kwargs["tenant_id"] == str(link.tenant_id)
        assert kwargs["role"] == "student"
        assert kwargs["notebook_id"] == notebook_id
        assert isinstance(kwargs["conversation_history"], list)

    async def test_process_inbound_message_ingests_link_and_runs_follow_up(self):
        link = SimpleNamespace(user_id=uuid4(), tenant_id=uuid4())
        notebook_id = str(uuid4())
        session = {
            "phone": "919876543210",
            "user_id": str(link.user_id),
            "tenant_id": str(link.tenant_id),
            "role": "student",
            "active_child_id": None,
            "active_notebook_id": None,
            "conversation_history": [],
        }
        db = MagicMock()
        url_result = {
            "response_text": "Added this link to your knowledge base. You can now ask questions about it in WhatsApp.",
            "response_type": "text",
            "intent": "url_upload",
            "tool_name": "ingest_whatsapp_url",
            "notebook_id": notebook_id,
        }

        with patch("src.domains.platform.services.whatsapp_gateway.resolve_phone_to_user", return_value=link), \
             patch("src.domains.platform.services.whatsapp_gateway.get_session", return_value=session), \
             patch("src.domains.platform.services.whatsapp_gateway._ingest_whatsapp_url", new=AsyncMock(return_value=url_result)) as ingest_mock, \
             patch("src.domains.platform.services.whatsapp_gateway._run_post_ingest_follow_up", new=AsyncMock(return_value={
                 "response": "This link explains the lesson in a grounded way.",
                 "intent": "ask_ai_question",
                 "tool_name": "ask_ai_question",
             })) as follow_up_mock, \
             patch("src.domains.platform.services.whatsapp_gateway.save_session"), \
             patch("src.domains.platform.services.whatsapp_gateway.log_message"):
            result = await process_inbound_message(
                db,
                "919876543210",
                "Summarize this https://example.com/lesson",
                wa_message_id="wamid-link-1",
            )

        assert "Added this link to your knowledge base." in result["response_text"]
        assert "This link explains the lesson" in result["response_text"]
        assert session["active_notebook_id"] == notebook_id
        ingest_mock.assert_awaited_once_with(
            db,
            user_id=str(link.user_id),
            tenant_id=str(link.tenant_id),
            url="https://example.com/lesson",
            text="Summarize this https://example.com/lesson",
        )
        follow_up_mock.assert_awaited_once()
        kwargs = follow_up_mock.await_args.kwargs
        assert kwargs["message"] == "Summarize this"
        assert kwargs["user_id"] == str(link.user_id)
        assert kwargs["tenant_id"] == str(link.tenant_id)
        assert kwargs["role"] == "student"
        assert kwargs["notebook_id"] == notebook_id
        assert isinstance(kwargs["conversation_history"], list)

    async def test_process_inbound_message_ingests_text_note_and_runs_follow_up(self):
        link = SimpleNamespace(user_id=uuid4(), tenant_id=uuid4())
        notebook_id = str(uuid4())
        session = {
            "phone": "919876543210",
            "user_id": str(link.user_id),
            "tenant_id": str(link.tenant_id),
            "role": "student",
            "active_child_id": None,
            "active_notebook_id": None,
            "conversation_history": [],
        }
        db = MagicMock()
        note_result = {
            "response_text": "Saved your text note to the knowledge base. You can now ask questions about it in WhatsApp.",
            "response_type": "text",
            "intent": "text_note_upload",
            "tool_name": "ingest_whatsapp_text_note",
            "notebook_id": notebook_id,
        }

        with patch("src.domains.platform.services.whatsapp_gateway.resolve_phone_to_user", return_value=link), \
             patch("src.domains.platform.services.whatsapp_gateway.get_session", return_value=session), \
             patch("src.domains.platform.services.whatsapp_gateway._ingest_whatsapp_text_note", new=AsyncMock(return_value=note_result)) as ingest_mock, \
             patch("src.domains.platform.services.whatsapp_gateway._run_post_ingest_follow_up", new=AsyncMock(return_value={
                 "response": "Here is a grounded answer from your saved note.",
                 "intent": "ask_ai_question",
                 "tool_name": "ask_ai_question",
             })) as follow_up_mock, \
             patch("src.domains.platform.services.whatsapp_gateway.save_session"), \
             patch("src.domains.platform.services.whatsapp_gateway.log_message"):
            result = await process_inbound_message(
                db,
                "919876543210",
                "note: Photosynthesis uses sunlight to make food.\n\nquestion: summarize this note",
                wa_message_id="wamid-note-1",
            )

        assert "Saved your text note" in result["response_text"]
        assert "grounded answer from your saved note" in result["response_text"]
        assert session["active_notebook_id"] == notebook_id
        ingest_mock.assert_awaited_once()
        assert ingest_mock.await_args.kwargs["note_text"] == "Photosynthesis uses sunlight to make food."
        follow_up_mock.assert_awaited_once()
        assert follow_up_mock.await_args.kwargs["message"] == "summarize this note"
        assert follow_up_mock.await_args.kwargs["notebook_id"] == notebook_id

    async def test_process_inbound_message_queues_video_upload_without_inline_follow_up(self):
        link = SimpleNamespace(user_id=uuid4(), tenant_id=uuid4())
        notebook_id = str(uuid4())
        session = {
            "phone": "919876543210",
            "user_id": str(link.user_id),
            "tenant_id": str(link.tenant_id),
            "role": "student",
            "active_child_id": None,
            "active_notebook_id": None,
            "conversation_history": [],
        }
        db = MagicMock()
        media_result = {
            "response_text": "Received *lesson.mp4* and queued transcript extraction. I'll message you here once the transcript is ready so you can continue from the same upload.",
            "response_type": "text",
            "intent": "media_upload",
            "tool_name": "ingest_whatsapp_media",
            "notebook_id": notebook_id,
            "status": "queued",
            "ingestion_mode": "async",
            "job_id": "job-123",
        }

        with patch("src.domains.platform.services.whatsapp_gateway.resolve_phone_to_user", return_value=link), \
             patch("src.domains.platform.services.whatsapp_gateway.get_session", return_value=session), \
             patch("src.domains.platform.services.whatsapp_gateway._ingest_whatsapp_media_upload", new=AsyncMock(return_value=media_result)), \
             patch("src.domains.platform.services.whatsapp_gateway._run_post_ingest_follow_up", new=AsyncMock(return_value={
                 "response": "This should not run yet.",
                 "intent": "ask_ai_question",
                 "tool_name": "ask_ai_question",
             })) as follow_up_mock, \
             patch("src.domains.platform.services.whatsapp_gateway.save_session"), \
             patch("src.domains.platform.services.whatsapp_gateway.log_message"):
            result = await process_inbound_message(
                db,
                "919876543210",
                "Explain the key ideas",
                wa_message_id="wamid-video-1",
                message_type="video",
                media_id="media-video-123",
                media_filename="lesson.mp4",
                media_mime_type="video/mp4",
            )

        assert "queued transcript extraction" in result["response_text"].lower()
        assert session["active_notebook_id"] == notebook_id
        follow_up_mock.assert_not_awaited()

    async def test_process_inbound_message_returns_actionable_bad_link_error(self):
        link = SimpleNamespace(user_id=uuid4(), tenant_id=uuid4())
        session = {
            "phone": "919876543210",
            "user_id": str(link.user_id),
            "tenant_id": str(link.tenant_id),
            "role": "student",
            "active_child_id": None,
            "active_notebook_id": None,
            "conversation_history": [],
        }
        db = MagicMock()

        with patch("src.domains.platform.services.whatsapp_gateway.resolve_phone_to_user", return_value=link), \
             patch("src.domains.platform.services.whatsapp_gateway.get_session", return_value=session), \
             patch("src.domains.platform.services.whatsapp_gateway._ingest_whatsapp_url", new=AsyncMock(side_effect=ValueError(
                 "That link points to a private or unsupported destination."
             ))), \
             patch("src.domains.platform.services.whatsapp_gateway.save_session"), \
             patch("src.domains.platform.services.whatsapp_gateway.log_message"):
            result = await process_inbound_message(
                db,
                "919876543210",
                "Summarize this https://internal.example.local",
                wa_message_id="wamid-link-bad",
            )

        assert "public web page" in result["response_text"].lower()
        assert "youtube link" in result["response_text"].lower()

    async def test_ingest_whatsapp_url_uses_youtube_pipeline(self):
        tenant_id = str(uuid4())
        user_id = str(uuid4())
        notebook = SimpleNamespace(id=uuid4())
        db = MagicMock()
        fake_chunks = [
            SimpleNamespace(
                text="Photosynthesis transcript chunk",
                document_id="doc-1",
                page_number=1,
                section_title="Segment 1",
                subject_id=None,
                notebook_id=str(notebook.id),
                source_file="https://youtu.be/abc123xyz09",
            )
        ]
        embedding_provider = SimpleNamespace(embed_batch=AsyncMock(return_value=[[0.1, 0.2]]))
        vector_store = SimpleNamespace(add_chunks=MagicMock())

        with patch("src.domains.platform.services.whatsapp_gateway._create_whatsapp_notebook", return_value=notebook), \
             patch("src.infrastructure.vector_store.ingestion.ingest_youtube", return_value=fake_chunks) as ingest_youtube_mock, \
             patch("src.infrastructure.llm.providers.get_embedding_provider", return_value=embedding_provider), \
             patch("src.infrastructure.llm.providers.get_vector_store_provider", return_value=vector_store), \
             patch("src.domains.platform.services.whatsapp_gateway.invalidate_tenant_cache"):
            result = await _ingest_whatsapp_url(
                db,
                user_id=user_id,
                tenant_id=tenant_id,
                url="https://youtu.be/abc123xyz09",
                text="Summarize this YouTube lesson",
            )

        assert "youtube link" in result["response_text"].lower()
        assert result["notebook_id"] == str(notebook.id)
        ingest_youtube_mock.assert_called_once()
        assert ingest_youtube_mock.call_args.kwargs["url"] == "https://youtu.be/abc123xyz09"
        assert ingest_youtube_mock.call_args.kwargs["tenant_id"] == tenant_id
        assert ingest_youtube_mock.call_args.kwargs["notebook_id"] == str(notebook.id)
        vector_store.add_chunks.assert_called_once()


# ─── Model Import Test ───────────────────────────────────────

class TestModels:
    def test_phone_user_link_import(self):
        pytest.importorskip("sqlalchemy")
        from src.domains.platform.models.whatsapp_models import PhoneUserLink
        assert PhoneUserLink.__tablename__ == "phone_user_link"

    def test_whatsapp_session_import(self):
        pytest.importorskip("sqlalchemy")
        from src.domains.platform.models.whatsapp_models import WhatsAppSession
        assert WhatsAppSession.__tablename__ == "whatsapp_sessions"

    def test_whatsapp_message_import(self):
        pytest.importorskip("sqlalchemy")
        from src.domains.platform.models.whatsapp_models import WhatsAppMessage
        assert WhatsAppMessage.__tablename__ == "whatsapp_messages"


for _name, _value in list(vars().items()):
    if _name.startswith("Test") and isinstance(_value, type):
        for _attr, _fn in list(vars(_value).items()):
            if _attr.startswith("test_") and inspect.iscoroutinefunction(_fn):
                def _wrap(fn):
                    @functools.wraps(fn)
                    def _runner(*args, **kwargs):
                        return asyncio.run(fn(*args, **kwargs))
                    return _runner
                setattr(_value, _attr, _wrap(_fn))
