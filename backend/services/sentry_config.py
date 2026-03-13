"""Sentry initialization helper for API, AI service, and worker runtimes."""
from __future__ import annotations

import logging
from typing import Any

from config import settings

logger = logging.getLogger("sentry")


def configure_sentry(service_name: str, app: Any | None = None) -> None:
    if not settings.sentry.enabled or not settings.sentry.dsn:
        return

    try:
        import sentry_sdk
        from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.httpx import HttpxIntegration
        from sentry_sdk.integrations.redis import RedisIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    except Exception as exc:
        logger.warning("Sentry SDK unavailable: %s", exc)
        return

    sentry_sdk.init(
        dsn=settings.sentry.dsn,
        environment=settings.sentry.environment or settings.app.env,
        release=settings.app.version,
        traces_sample_rate=settings.sentry.traces_sample_rate,
        profiles_sample_rate=settings.sentry.profiles_sample_rate,
        send_default_pii=settings.sentry.send_default_pii,
        server_name=service_name,
        integrations=[
            FastApiIntegration(),
            HttpxIntegration(),
            RedisIntegration(),
            SqlalchemyIntegration(),
        ],
    )

    if app is not None:
        app.add_middleware(SentryAsgiMiddleware)
