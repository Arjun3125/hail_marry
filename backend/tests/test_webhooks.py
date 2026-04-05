"""Tests for the webhooks service."""
import pytest
from unittest.mock import MagicMock
from uuid import uuid4


class TestEmitWebhookEvent:
    """Test webhook event emission."""

    @pytest.mark.asyncio
    async def test_no_subscriptions_returns_zero(self):
        """When no subscriptions exist, should return 0."""
        from src.domains.platform.services.webhooks import emit_webhook_event

        db = MagicMock()
        db.query.return_value.filter.return_value.all.return_value = []

        result = await emit_webhook_event(
            db=db,
            tenant_id=uuid4(),
            event_type="attendance.marked",
            data={"student_id": str(uuid4()), "status": "present"},
        )
        assert result["subscriptions"] == 0

    @pytest.mark.asyncio
    async def test_subscription_creates_delivery(self):
        """When a subscription exists, a delivery should be created."""
        from src.domains.platform.services.webhooks import emit_webhook_event

        db = MagicMock()
        sub = MagicMock()
        sub.id = uuid4()
        sub.target_url = "https://example.com/webhook"
        sub.secret = "webhook-secret"
        sub.event_type = "attendance.marked"
        sub.is_active = True
        db.query.return_value.filter.return_value.all.return_value = [sub]

        result = await emit_webhook_event(
            db=db,
            tenant_id=uuid4(),
            event_type="attendance.marked",
            data={"student_id": str(uuid4())},
        )
        assert result["subscriptions"] >= 1
        assert db.add.called
