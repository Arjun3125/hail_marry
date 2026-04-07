"""Tests for the WhatsApp Bridge endpoint.

Covers:
  · Accepts valid payloads with correct internal header
  · Rejects requests without internal header
  · Rejects empty phone / text
  · Background processing is scheduled
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from src.domains.platform.routes.whatsapp_bridge import (
    BridgeInboundPayload,
    bridge_inbound,
    INTERNAL_HEADER,
    EXPECTED_HEADER_VALUE,
)


class _FakeRequest:
    """Minimal Request stub."""
    def __init__(self, headers=None):
        self.headers = headers or {}


class _FakeBackgroundTasks:
    def __init__(self):
        self.tasks = []
    def add_task(self, fn, *args, **kwargs):
        self.tasks.append((fn, args, kwargs))


class TestBridgeInboundValidation:
    """Request validation tests."""

    @pytest.mark.asyncio
    async def test_rejects_missing_gateway_header(self):
        payload = BridgeInboundPayload(phone="919999999999", text="hello")
        request = _FakeRequest(headers={})
        bg = _FakeBackgroundTasks()

        with pytest.raises(Exception) as exc_info:
            await bridge_inbound(payload, request, bg)
        assert "403" in str(exc_info.value) or "Not authorized" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_rejects_empty_phone(self):
        payload = BridgeInboundPayload(phone="", text="hello")
        request = _FakeRequest(headers={INTERNAL_HEADER: EXPECTED_HEADER_VALUE})
        bg = _FakeBackgroundTasks()

        with pytest.raises(Exception) as exc_info:
            await bridge_inbound(payload, request, bg)
        assert "400" in str(exc_info.value) or "phone" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_rejects_empty_text_and_no_media(self):
        payload = BridgeInboundPayload(phone="919999999999", text="")
        request = _FakeRequest(headers={INTERNAL_HEADER: EXPECTED_HEADER_VALUE})
        bg = _FakeBackgroundTasks()

        with pytest.raises(Exception) as exc_info:
            await bridge_inbound(payload, request, bg)
        assert "400" in str(exc_info.value) or "required" in str(exc_info.value).lower()


class TestBridgeInboundAcceptance:
    """Valid requests are accepted and background-tasked."""

    @pytest.mark.asyncio
    async def test_valid_text_message_accepted(self):
        payload = BridgeInboundPayload(phone="919999999999", text="help")
        request = _FakeRequest(headers={INTERNAL_HEADER: EXPECTED_HEADER_VALUE})
        bg = _FakeBackgroundTasks()

        result = await bridge_inbound(payload, request, bg)

        assert result["status"] == "accepted"
        assert result["phone"] == "919999999999"
        assert len(bg.tasks) == 1

    @pytest.mark.asyncio
    async def test_valid_media_message_accepted(self):
        payload = BridgeInboundPayload(
            phone="919999999999",
            text="",
            media_id="media_123",
            message_type="image",
        )
        request = _FakeRequest(headers={INTERNAL_HEADER: EXPECTED_HEADER_VALUE})
        bg = _FakeBackgroundTasks()

        result = await bridge_inbound(payload, request, bg)

        assert result["status"] == "accepted"
        assert len(bg.tasks) == 1
