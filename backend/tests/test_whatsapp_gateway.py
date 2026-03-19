"""Tests for WhatsApp Gateway — signature verification, OTP auth, session management,
RBAC enforcement, and webhook pipeline.
"""
import asyncio
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

# ─── Set env vars before imports ──────────────────────────────
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("WHATSAPP_APP_SECRET", "test-secret-key")
os.environ.setdefault("WHATSAPP_VERIFY_TOKEN", "vidyaos-wa-verify")

from src.domains.platform.routes.whatsapp import (
    whatsapp_webhook_verify,
    whatsapp_webhook_inbound,
    whatsapp_tool_catalog,
    _extract_messages,
    SendMessageRequest,
    _dispatch_outbound_response,
    whatsapp_report_card_download,
)
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
    format_ai_job_status_message,
    process_inbound_message,
    _build_child_switch_response,
    _handle_child_switch_selection,
    _build_report_card_response,
    SYSTEM_COMMANDS,
)
from src.shared.ai_tools.whatsapp_tools import (
    authorize_tool,
    TOOL_ROLE_MAP,
    get_tools_for_role,
    get_tool_spec,
    get_tool_specs_for_role,
    serialize_tool_catalog,
)
from src.interfaces.whatsapp_bot.agent import (
    _classify_intent_heuristic,
    _extract_topic_from_message,
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

    def test_session_not_found(self, mock_redis):
        """Loading a non-existent session returns None."""
        fake_redis, storage = mock_redis
        assert get_session(MagicMock(), "919999999999") is None


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
            if _attr.startswith("test_") and asyncio.iscoroutinefunction(_fn):
                def _wrap(fn):
                    def _runner(*args, **kwargs):
                        return asyncio.run(fn(*args, **kwargs))
                    return _runner
                setattr(_value, _attr, _wrap(_fn))
