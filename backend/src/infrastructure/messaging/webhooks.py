"""Messaging adapter for webhook delivery."""

from __future__ import annotations

from src.domains.platform.services.webhooks import emit_webhook_event as _emit_webhook_event


async def emit_webhook_event(*args, **kwargs):
    return await _emit_webhook_event(*args, **kwargs)
