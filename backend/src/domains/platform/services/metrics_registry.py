"""In-process metrics registry with Prometheus text export."""
from __future__ import annotations

import threading
from collections import defaultdict
from typing import Any

_lock = threading.Lock()
_http_metrics: dict[tuple[str, str, str, str], dict[str, float]] = defaultdict(lambda: {"count": 0.0, "duration_ms_sum": 0.0})
_ocr_metrics: dict[tuple[str, str], float] = defaultdict(float)
_stage_latency_metrics: dict[tuple[str, str, str], dict[str, float]] = defaultdict(
    lambda: {"count": 0.0, "duration_ms_sum": 0.0, "duration_ms_max": 0.0}
)
_personalization_metrics: dict[tuple[str, str, str], float] = defaultdict(float)
_traceability_error_metrics: dict[tuple[str, str, str], float] = defaultdict(float)


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


def increment_ocr_metric(outcome: str, engine: str = "easyocr", count: float = 1.0) -> None:
    with _lock:
        _ocr_metrics[(outcome, engine)] += count


def snapshot_ocr_metrics() -> list[dict[str, Any]]:
    with _lock:
        return [
            {
                "outcome": outcome,
                "engine": engine,
                "count": value,
            }
            for (outcome, engine), value in _ocr_metrics.items()
        ]


def observe_stage_latency(stage: str, operation: str, duration_ms: float, outcome: str = "success") -> None:
    key = (stage, operation, outcome)
    with _lock:
        bucket = _stage_latency_metrics[key]
        bucket["count"] += 1
        bucket["duration_ms_sum"] += duration_ms
        bucket["duration_ms_max"] = max(bucket["duration_ms_max"], duration_ms)


def snapshot_stage_latency_metrics() -> list[dict[str, Any]]:
    with _lock:
        return [
            {
                "stage": stage,
                "operation": operation,
                "outcome": outcome,
                "count": values["count"],
                "duration_ms_sum": values["duration_ms_sum"],
                "duration_ms_max": values["duration_ms_max"],
            }
            for (stage, operation, outcome), values in _stage_latency_metrics.items()
        ]


def observe_personalization_event(
    metric: str,
    *,
    surface: str = "unknown",
    target: str = "unknown",
    count: float = 1.0,
    db=None,
    tenant_id: str | None = None,
    user_id: str | None = None,
    channel: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    key = (metric, surface, target)
    with _lock:
        _personalization_metrics[key] += count
    if tenant_id or user_id:
        from src.domains.platform.services.telemetry_events import record_business_event

        record_business_event(
            metric,
            db=db,
            tenant_id=str(tenant_id) if tenant_id is not None else None,
            user_id=str(user_id) if user_id is not None else None,
            event_family="personalization",
            surface=surface,
            target=target,
            channel=channel,
            value=count,
            metadata=metadata or {},
        )


def snapshot_personalization_metrics() -> list[dict[str, Any]]:
    with _lock:
        return [
            {
                "metric": metric,
                "surface": surface,
                "target": target,
                "count": value,
            }
            for (metric, surface, target), value in _personalization_metrics.items()
        ]


def observe_traceability_error(error_code: str, *, subsystem: str = "unknown", severity: str = "error", count: float = 1.0) -> None:
    key = (error_code, subsystem, severity)
    with _lock:
        _traceability_error_metrics[key] += count


def snapshot_traceability_error_metrics() -> list[dict[str, Any]]:
    with _lock:
        return [
            {
                "error_code": error_code,
                "subsystem": subsystem,
                "severity": severity,
                "count": value,
            }
            for (error_code, subsystem, severity), value in _traceability_error_metrics.items()
        ]


def reset_metrics_registry() -> None:
    with _lock:
        _http_metrics.clear()
        _ocr_metrics.clear()
        _stage_latency_metrics.clear()
        _personalization_metrics.clear()
        _traceability_error_metrics.clear()


def _get_global_queue_metrics() -> dict[str, int]:
    from src.domains.platform.services.ai_queue import (
        GLOBAL_METRICS_KEY,
        READY_TENANTS_ACTIVE_KEY,
        _get_redis_client,
    )

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
    # Cache snapshots to avoid redundant lock acquisitions and list copies
    http_snapshot = snapshot_http_metrics()
    ocr_snapshot = snapshot_ocr_metrics()
    stage_snapshot = snapshot_stage_latency_metrics()
    personalization_snapshot = snapshot_personalization_metrics()
    traceability_snapshot = snapshot_traceability_error_metrics()

    lines = [
        "# HELP vidyaos_http_requests_total Total HTTP requests observed by the process",
        "# TYPE vidyaos_http_requests_total counter",
    ]
    for row in http_snapshot:
        lines.append(
            f'vidyaos_http_requests_total{{service="{_sanitize_label(row["service"])}",method="{_sanitize_label(row["method"])}",path="{_sanitize_label(row["path"])}",status_code="{row["status_code"]}"}} {row["count"]}'
        )

    lines.extend([
        "# HELP vidyaos_http_request_duration_ms_sum Sum of HTTP request durations in milliseconds",
        "# TYPE vidyaos_http_request_duration_ms_sum counter",
    ])
    for row in http_snapshot:
        lines.append(
            f'vidyaos_http_request_duration_ms_sum{{service="{_sanitize_label(row["service"])}",method="{_sanitize_label(row["method"])}",path="{_sanitize_label(row["path"])}",status_code="{row["status_code"]}"}} {row["duration_ms_sum"]}'
        )

    lines.extend([
        "# HELP vidyaos_ocr_events_total OCR events by outcome and engine",
        "# TYPE vidyaos_ocr_events_total counter",
    ])
    for row in ocr_snapshot:
        lines.append(
            f'vidyaos_ocr_events_total{{outcome="{_sanitize_label(row["outcome"])}",engine="{_sanitize_label(row["engine"])}"}} {row["count"]}'
        )

    lines.extend([
        "# HELP vidyaos_stage_latency_total Total observed stage latency events by stage, operation, and outcome",
        "# TYPE vidyaos_stage_latency_total counter",
    ])
    for row in stage_snapshot:
        lines.append(
            f'vidyaos_stage_latency_total{{stage="{_sanitize_label(row["stage"])}",operation="{_sanitize_label(row["operation"])}",outcome="{_sanitize_label(row["outcome"])}"}} {row["count"]}'
        )

    lines.extend([
        "# HELP vidyaos_stage_latency_duration_ms_sum Sum of observed stage latencies in milliseconds",
        "# TYPE vidyaos_stage_latency_duration_ms_sum counter",
    ])
    for row in stage_snapshot:
        lines.append(
            f'vidyaos_stage_latency_duration_ms_sum{{stage="{_sanitize_label(row["stage"])}",operation="{_sanitize_label(row["operation"])}",outcome="{_sanitize_label(row["outcome"])}"}} {row["duration_ms_sum"]}'
        )

    lines.extend([
        "# HELP vidyaos_stage_latency_duration_ms_max Maximum observed stage latency in milliseconds",
        "# TYPE vidyaos_stage_latency_duration_ms_max gauge",
    ])
    for row in stage_snapshot:
        lines.append(
            f'vidyaos_stage_latency_duration_ms_max{{stage="{_sanitize_label(row["stage"])}",operation="{_sanitize_label(row["operation"])}",outcome="{_sanitize_label(row["outcome"])}"}} {row["duration_ms_max"]}'
        )

    lines.extend([
        "# HELP vidyaos_personalization_events_total Personalization events by metric, surface, and target",
        "# TYPE vidyaos_personalization_events_total counter",
    ])
    for row in personalization_snapshot:
        lines.append(
            f'vidyaos_personalization_events_total{{metric="{_sanitize_label(row["metric"])}",surface="{_sanitize_label(row["surface"])}",target="{_sanitize_label(row["target"])}"}} {row["count"]}'
        )

    lines.extend([
        "# HELP vidyaos_traceability_errors_total Traceability errors by code, subsystem, and severity",
        "# TYPE vidyaos_traceability_errors_total counter",
    ])
    for row in traceability_snapshot:
        lines.append(
            f'vidyaos_traceability_errors_total{{error_code="{_sanitize_label(row["error_code"])}",subsystem="{_sanitize_label(row["subsystem"])}",severity="{_sanitize_label(row["severity"])}"}} {row["count"]}'
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
