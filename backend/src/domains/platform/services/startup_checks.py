"""Startup dependency checks for API and worker processes."""
from __future__ import annotations

import logging
from typing import Any

import httpx
from sqlalchemy import text

from config import settings
from database import engine

logger = logging.getLogger("startup-checks")


def _check_database() -> tuple[bool, str]:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True, "ok"
    except Exception as exc:
        return False, f"database unavailable: {exc}"


def _check_redis() -> tuple[bool, str]:
    try:
        import redis as redis_lib

        timeout = max(1, settings.startup_checks.timeout_seconds)
        client = redis_lib.from_url(
            settings.redis.url,
            decode_responses=True,
            socket_connect_timeout=timeout,
            socket_timeout=timeout,
        )
        client.ping()
        return True, "ok"
    except Exception as exc:
        return False, f"redis unavailable: {exc}"


def _check_http_health(url: str, *, timeout_seconds: int) -> tuple[bool, str]:
    try:
        with httpx.Client(timeout=timeout_seconds) as client:
            response = client.get(url)
        if 200 <= response.status_code < 300:
            return True, "ok"
        return False, f"http {response.status_code}"
    except Exception as exc:
        return False, str(exc)


def _service_checks(service_name: str) -> dict[str, tuple[bool, str]]:
    import os
    
    timeout = settings.startup_checks.timeout_seconds
    checks: dict[str, tuple[bool, str]] = {
        "database": _check_database(),
    }

    # Determine if Redis is required
    # - Worker services always require Redis
    # - AI queue services require Redis
    # - API servers in production (any non-dev environment) require Redis for distributed rate limiting
    app_env = os.getenv("APP_ENV", "production").lower()
    is_production = app_env not in ("local", "development", "test")
    redis_required = (
        service_name == "worker" 
        or settings.ai_queue.enabled
        or (service_name in ("api", "api-server") and is_production)
    )
    
    if redis_required:
        checks["redis"] = _check_redis()

    if service_name == "ai-service":
        checks["ollama"] = _check_http_health(f"{settings.llm.url.rstrip('/')}/api/tags", timeout_seconds=timeout)

    return checks


def collect_dependency_status(service_name: str) -> dict[str, Any]:
    checks = _service_checks(service_name)
    ready = all(status for status, _ in checks.values())
    return {
        "service": service_name,
        "ready": ready,
        "checks": {
            name: {"ok": ok, "detail": detail}
            for name, (ok, detail) in checks.items()
        },
    }


def enforce_startup_dependencies(service_name: str) -> dict[str, Any]:
    if not settings.startup_checks.enabled:
        return {"service": service_name, "ready": True, "checks": {}}

    status = collect_dependency_status(service_name)
    if status["ready"]:
        logger.info("Startup dependency checks passed for %s", service_name)
        return status

    if not status["ready"]:
        logger.warning("Startup dependency checks failed for %s: %s", service_name, status["checks"])
        if settings.startup_checks.strict:
            raise RuntimeError(f"Startup dependency checks failed for {service_name}: {status['checks']}")
    return status
