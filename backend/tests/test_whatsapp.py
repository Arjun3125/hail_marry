"""Tests for the WhatsApp notification service."""
import asyncio
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from src.domains.academic.services.whatsapp import (
    send_whatsapp_message,
    send_attendance_alert,
    send_weekly_digest,
    send_exam_result,
)


class TestSendWhatsAppMessage:
    """Test core message sending logic."""

    async def test_returns_error_when_not_configured(self):
        """When credentials are empty, message should not be sent."""
        with patch("src.domains.academic.services.whatsapp.WHATSAPP_TOKEN", ""), \
             patch("src.domains.academic.services.whatsapp.WHATSAPP_PHONE_ID", ""):
            result = await send_whatsapp_message("919876543210", "Hello!")
            assert result["success"] is False
            assert "not configured" in result["error"]

    async def test_successful_send(self):
        """When API returns 200, should return success."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"messages": [{"id": "msg123"}]}
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch("src.domains.academic.services.whatsapp.WHATSAPP_TOKEN", "test-token"), \
             patch("src.domains.academic.services.whatsapp.WHATSAPP_PHONE_ID", "phone-id"), \
             patch("src.domains.academic.services.whatsapp.httpx.AsyncClient", return_value=mock_client):
            result = await send_whatsapp_message("919876543210", "Test message")
            assert result["success"] is True
            assert "data" in result


class TestSendAttendanceAlert:
    """Test attendance alert formatting."""

    async def test_absent_alert_format(self):
        """Absent status should include '🔴 Attendance Alert' and the student's name."""
        with patch("src.domains.academic.services.whatsapp.send_whatsapp_message", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = {"success": True}
            await send_attendance_alert("919876543210", "Ravi", "2026-03-10", "absent")
            mock_send.assert_called_once()
            msg = mock_send.call_args[0][1]
            assert "🔴" in msg
            assert "Ravi" in msg
            assert "absent" in msg

    async def test_present_alert_format(self):
        """Present status should include '✅ Attendance Update'."""
        with patch("src.domains.academic.services.whatsapp.send_whatsapp_message", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = {"success": True}
            await send_attendance_alert("919876543210", "Ravi", "2026-03-10", "present")
            msg = mock_send.call_args[0][1]
            assert "✅" in msg
            assert "present" in msg


class TestSendWeeklyDigest:
    """Test weekly digest message formatting."""

    async def test_digest_includes_all_stats(self):
        with patch("src.domains.academic.services.whatsapp.send_whatsapp_message", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = {"success": True}
            await send_weekly_digest("919876543210", "Ravi", 85, 72, "Math", "English")
            msg = mock_send.call_args[0][1]
            assert "85%" in msg
            assert "72%" in msg
            assert "Math" in msg
            assert "English" in msg
            assert "📊" in msg


class TestSendExamResult:
    """Test exam result notification with emoji selection."""

    async def test_high_score_emoji(self):
        """≥80% should use attendance_emoji → 🎉."""
        with patch("src.domains.academic.services.whatsapp.send_whatsapp_message", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = {"success": True}
            await send_exam_result("919876543210", "Ravi", "Math Final", 85, 100)
            msg = mock_send.call_args[0][1]
            assert "🎉" in msg
            assert "85/100" in msg

    async def test_medium_score_emoji(self):
        """60-79% should use 👍."""
        with patch("src.domains.academic.services.whatsapp.send_whatsapp_message", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = {"success": True}
            await send_exam_result("919876543210", "Ravi", "English Mid", 65, 100)
            msg = mock_send.call_args[0][1]
            assert "👍" in msg

    async def test_low_score_emoji(self):
        """<60% should use 📖."""
        with patch("src.domains.academic.services.whatsapp.send_whatsapp_message", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = {"success": True}
            await send_exam_result("919876543210", "Ravi", "Science Quiz", 45, 100)
            msg = mock_send.call_args[0][1]
            assert "📖" in msg

    async def test_zero_max_marks_no_division_error(self):
        """max_marks=0 should not raise ZeroDivisionError."""
        with patch("src.domains.academic.services.whatsapp.send_whatsapp_message", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = {"success": True}
            await send_exam_result("919876543210", "Ravi", "Test", 0, 0)
            # Should not raise — pct defaults to 0
            msg = mock_send.call_args[0][1]
            assert "0%" in msg


for _name, _value in list(vars().items()):
    if _name.startswith("Test") and isinstance(_value, type):
        for _attr, _fn in list(vars(_value).items()):
            if _attr.startswith("test_") and asyncio.iscoroutinefunction(_fn):
                def _wrap(fn):
                    def _runner(*args, **kwargs):
                        return asyncio.run(fn(*args, **kwargs))
                    return _runner
                setattr(_value, _attr, _wrap(_fn))
