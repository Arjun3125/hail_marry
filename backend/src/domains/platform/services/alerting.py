"""Simple alert evaluation for queue and AI runtime health."""
from __future__ import annotations

from typing import Any

from config import settings
from src.domains.platform.services.ai_queue import get_queue_metrics


def get_active_alerts(tenant_id: str) -> list[dict[str, Any]]:
    if not settings.observability.alerting_enabled:
        return []

    queue = get_queue_metrics(tenant_id)
    alerts: list[dict[str, Any]] = []
    tenant_cap = max(queue.get("max_pending_jobs_per_tenant", 1), 1)
    queue_depth_pct = (queue.get("pending_depth", 0) / tenant_cap) * 100

    if queue_depth_pct >= settings.observability.queue_depth_warn_threshold_pct:
        alerts.append({
            "code": "queue_depth_high",
            "severity": "warning",
            "message": f"Queue depth is {queue.get('pending_depth', 0)} / {tenant_cap} for this tenant.",
        })

    if queue.get("failure_rate_pct", 0) >= settings.observability.queue_failure_warn_pct and queue.get("failed_last_window", 0) > 0:
        alerts.append({
            "code": "queue_failure_rate_high",
            "severity": "critical",
            "message": f"Failure rate reached {queue.get('failure_rate_pct', 0)}% in the current window.",
        })

    if queue.get("stuck_jobs", 0) > 0:
        alerts.append({
            "code": "queue_jobs_stuck",
            "severity": "critical",
            "message": f"{queue.get('stuck_jobs', 0)} job(s) exceed the stuck threshold.",
        })

    if queue.get("pending_depth", 0) > 0 and queue.get("processing_depth", 0) == 0:
        alerts.append({
            "code": "queue_worker_idle",
            "severity": "warning",
            "message": "Queued jobs are waiting but no worker is currently processing jobs.",
        })

    if queue.get("dead_letter_count", 0) > 0:
        alerts.append({
            "code": "queue_dead_letter_present",
            "severity": "warning",
            "message": f"{queue.get('dead_letter_count', 0)} job(s) are in the dead-letter bucket.",
        })

    return alerts
