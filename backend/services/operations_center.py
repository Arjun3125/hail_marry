"""Operations Center summary service for single-pane admin visibility."""
from __future__ import annotations

import os
from typing import Any

import httpx

from config import settings
from constants import OLLAMA_BASE_URL
from services.ai_queue import get_queue_metrics
from services.alerting import get_active_alerts


RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


def _resolve_ollama_urls() -> list[str]:
    configured_urls = os.getenv("OLLAMA_BASE_URLS", "")
    parsed_urls = [part.strip() for part in configured_urls.split(",") if part.strip()]
    if parsed_urls:
        return parsed_urls
    legacy_url = os.getenv("OLLAMA_BASE_URL", OLLAMA_BASE_URL)
    return [legacy_url] if legacy_url else []


async def _probe_http(url: str, *, timeout_seconds: int = 3) -> dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            response = await client.get(url)
        return {
            "url": url,
            "healthy": response.status_code < 400,
            "status_code": response.status_code,
            "retryable_error": response.status_code in RETRYABLE_STATUS_CODES,
        }
    except httpx.HTTPError as exc:
        return {
            "url": url,
            "healthy": False,
            "status_code": None,
            "retryable_error": True,
            "error": str(exc),
        }


async def build_operations_summary(tenant_id: str) -> dict[str, Any]:
    queue_metrics = get_queue_metrics(tenant_id)
    alerts = get_active_alerts(tenant_id)

    ai_service_urls = settings.ai_service.resolved_urls()
    ai_service_nodes = [
        await _probe_http(f"{base_url.rstrip('/')}/health", timeout_seconds=min(settings.ai_service.timeout_seconds, 5))
        for base_url in ai_service_urls
    ]

    ollama_nodes = [
        await _probe_http(f"{base_url.rstrip('/')}/api/tags")
        for base_url in _resolve_ollama_urls()
    ]

    ai_healthy = sum(1 for node in ai_service_nodes if node.get("healthy"))
    ollama_healthy = sum(1 for node in ollama_nodes if node.get("healthy"))

    recommended_actions: list[str] = []
    if ai_service_nodes and ai_healthy == 0:
        recommended_actions.append("Dedicated AI service is down on all configured nodes; fail over or restart AI service pods.")
    if ollama_nodes and ollama_healthy == 0:
        recommended_actions.append("All Ollama endpoints are unavailable; switch provider or restore centralized Ollama capacity.")
    if queue_metrics.get("pending_depth", 0) > 100:
        recommended_actions.append("Queue depth is elevated; scale worker replicas and throttle non-critical AI workloads.")
    if queue_metrics.get("stuck_jobs", 0) > 0:
        recommended_actions.append("Stuck jobs detected; inspect dead-letter and retry failed jobs from queue operations.")

    return {
        "tenant_id": tenant_id,
        "summary": {
            "queue": {
                "pending_depth": queue_metrics.get("pending_depth", 0),
                "processing_depth": queue_metrics.get("processing_depth", 0),
                "stuck_jobs": queue_metrics.get("stuck_jobs", 0),
                "failure_rate_pct": queue_metrics.get("failure_rate_pct", 0),
            },
            "alerts": {
                "count": len(alerts),
                "items": alerts,
            },
            "ai_service": {
                "configured_nodes": len(ai_service_nodes),
                "healthy_nodes": ai_healthy,
                "nodes": ai_service_nodes,
            },
            "ollama": {
                "configured_nodes": len(ollama_nodes),
                "healthy_nodes": ollama_healthy,
                "nodes": ollama_nodes,
            },
        },
        "recommended_actions": recommended_actions,
    }
