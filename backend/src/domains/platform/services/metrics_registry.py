"""In-process metrics registry with Prometheus text export."""
from __future__ import annotations

import threading
from collections import defaultdict
from typing import Any

from src.domains.platform.services.ai_queue import GLOBAL_METRICS_KEY, READY_TENANTS_ACTIVE_KEY, get_queue_metrics, _get_redis_client

_lock = threading.Lock()
_http_metrics: dict[tuple[str, str, str, str], dict[str, float]] = defaultdict(lambda: {"count": 0.0, "duration_ms_sum": 0.0})


def _sanitize_label(value: str) -> str:
    return value.replace("\\", "_").replace('"', "_")


def observe_http_request(service: str, method: str, path: str, status_code: int, duration_ms: float) -> None:
    key = (service, method, path, str(status_code))
    with _lock:
        bucket = _http_metrics[key]
        bucket["count"] += 1
        bucket["duration_ms_sum"] += duration_ms


def snapshot_http_metrics() -> list[dict[str, Any]]:
    with _lock:
        return [
            {
                "service": service,
                "method": method,
                "path": path,
                "status_code": status_code,
                "count": values["count"],
                "duration_ms_sum": values["duration_ms_sum"],
            }
            for (service, method, path, status_code), values in _http_metrics.items()
        ]


def _get_global_queue_metrics() -> dict[str, int]:
    client = _get_redis_client()
    if not client:
        return {
            "pending_depth": 0,
            "processing_depth": 0,
            "tracked_jobs_total": 0,
            "retry_total": 0,
            "dead_letter_total": 0,
            "ready_tenants": 0,
        }

    return {
        "pending_depth": int(client.hget(GLOBAL_METRICS_KEY, "pending_depth") or 0),
        "processing_depth": int(client.hget(GLOBAL_METRICS_KEY, "processing_depth") or 0),
        "tracked_jobs_total": int(client.hget(GLOBAL_METRICS_KEY, "tracked_jobs_total") or 0),
        "retry_total": int(client.hget(GLOBAL_METRICS_KEY, "retry_total") or 0),
        "dead_letter_total": int(client.hget(GLOBAL_METRICS_KEY, "dead_letter_total") or 0),
        "ready_tenants": int(client.scard(READY_TENANTS_ACTIVE_KEY) or 0),
    }


def export_prometheus_text(alerts: list[dict[str, Any]] | None = None) -> str:
    lines = [
        "# HELP vidyaos_http_requests_total Total HTTP requests observed by the process",
        "# TYPE vidyaos_http_requests_total counter",
    ]
    for row in snapshot_http_metrics():
        lines.append(
            f'vidyaos_http_requests_total{{service="{_sanitize_label(row["service"])}",method="{_sanitize_label(row["method"])}",path="{_sanitize_label(row["path"])}",status_code="{row["status_code"]}"}} {row["count"]}'
        )

    lines.extend([
        "# HELP vidyaos_http_request_duration_ms_sum Sum of HTTP request durations in milliseconds",
        "# TYPE vidyaos_http_request_duration_ms_sum counter",
    ])
    for row in snapshot_http_metrics():
        lines.append(
            f'vidyaos_http_request_duration_ms_sum{{service="{_sanitize_label(row["service"])}",method="{_sanitize_label(row["method"])}",path="{_sanitize_label(row["path"])}",status_code="{row["status_code"]}"}} {row["duration_ms_sum"]}'
        )

    queue = _get_global_queue_metrics()
    lines.extend([
        "# HELP vidyaos_queue_pending_depth Current pending AI jobs across all tenants",
        "# TYPE vidyaos_queue_pending_depth gauge",
        f"vidyaos_queue_pending_depth {queue['pending_depth']}",
        "# HELP vidyaos_queue_processing_depth Current processing AI jobs across all tenants",
        "# TYPE vidyaos_queue_processing_depth gauge",
        f"vidyaos_queue_processing_depth {queue['processing_depth']}",
        "# HELP vidyaos_queue_ready_tenants Number of tenants with runnable jobs",
        "# TYPE vidyaos_queue_ready_tenants gauge",
        f"vidyaos_queue_ready_tenants {queue['ready_tenants']}",
        "# HELP vidyaos_queue_retries_total Total AI job retries",
        "# TYPE vidyaos_queue_retries_total counter",
        f"vidyaos_queue_retries_total {queue['retry_total']}",
        "# HELP vidyaos_queue_dead_letter_total Total dead-lettered AI jobs",
        "# TYPE vidyaos_queue_dead_letter_total counter",
        f"vidyaos_queue_dead_letter_total {queue['dead_letter_total']}",
    ])

    if alerts is not None:
        lines.extend([
            "# HELP vidyaos_alerts_active Current active observability alerts",
            "# TYPE vidyaos_alerts_active gauge",
            f"vidyaos_alerts_active {len(alerts)}",
        ])

    return "\n".join(lines) + "\n"
