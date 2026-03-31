"""Simple alert evaluation for queue and AI runtime health."""
from __future__ import annotations

from typing import Any

from config import settings
from src.domains.platform.services.ai_queue import get_queue_metrics
from src.domains.platform.services.metrics_registry import (
    snapshot_ocr_metrics,
    snapshot_stage_latency_metrics,
    snapshot_traceability_error_metrics,
)


def _build_stage_latency_alerts() -> list[dict[str, Any]]:
    thresholds = {
        ("ai_query", "retrieval"): settings.observability.retrieval_latency_warn_ms,
        ("ai_query", "generation"): settings.observability.generation_latency_warn_ms,
        ("whatsapp_media_ingest", "transcription"): settings.observability.transcription_latency_warn_ms,
        ("whatsapp_media_ingest", "embedding"): settings.observability.embedding_latency_warn_ms,
        ("whatsapp_media_ingest", "follow_up_generation"): settings.observability.generation_latency_warn_ms,
    }
    alerts: list[dict[str, Any]] = []
    for row in snapshot_stage_latency_metrics():
        threshold = thresholds.get((row.get("stage"), row.get("operation")))
        if not threshold or row.get("outcome") != "success":
            continue
        count = row.get("count", 0) or 0
        if count < settings.observability.stage_latency_min_events_for_alert:
            continue
        avg_latency_ms = row.get("duration_ms_sum", 0.0) / max(count, 1)
        if avg_latency_ms < threshold and row.get("duration_ms_max", 0.0) < threshold:
            continue
        alerts.append({
            "code": "stage_latency_high",
            "severity": "warning",
            "message": (
                f"{row.get('stage')}:{row.get('operation')} latency is elevated "
                f"(avg {avg_latency_ms:.0f}ms, max {row.get('duration_ms_max', 0.0):.0f}ms; "
                f"budget {threshold}ms over {int(count)} events)."
            ),
            "stage": row.get("stage"),
            "operation": row.get("operation"),
            "avg_latency_ms": round(avg_latency_ms, 1),
            "max_latency_ms": round(row.get("duration_ms_max", 0.0), 1),
            "budget_ms": threshold,
            "event_count": int(count),
        })
    return alerts


def _build_mascot_failure_alerts() -> list[dict[str, Any]]:
    rows = [row for row in snapshot_stage_latency_metrics() if row.get("stage") == "mascot"]
    by_operation: dict[str, dict[str, float]] = {}
    for row in rows:
        operation = str(row.get("operation") or "")
        outcome = str(row.get("outcome") or "")
        count = float(row.get("count", 0.0) or 0.0)
        bucket = by_operation.setdefault(operation, {"total": 0.0, "failed": 0.0})
        bucket["total"] += count
        if outcome not in {"success", "cancelled"}:
            bucket["failed"] += count

    alerts: list[dict[str, Any]] = []
    for operation, values in by_operation.items():
        total = values["total"]
        failed = values["failed"]
        if total < settings.observability.mascot_min_events_for_alert or failed <= 0:
            continue
        failure_pct = (failed / max(total, 1.0)) * 100.0
        if failure_pct < settings.observability.mascot_failure_warn_pct:
            continue
        alerts.append({
            "code": "mascot_failure_rate_high",
            "severity": "critical" if operation in {"execution", "upload"} else "warning",
            "message": (
                f"Mascot {operation} failure rate reached {failure_pct:.1f}% "
                f"over {int(total)} events."
            ),
            "stage": "mascot",
            "operation": operation,
            "failure_rate_pct": round(failure_pct, 1),
            "event_count": int(total),
            "failed_count": int(failed),
        })
    return alerts


def _build_traceability_error_alerts() -> list[dict[str, Any]]:
    alerts: list[dict[str, Any]] = []
    for row in snapshot_traceability_error_metrics():
        count = int(row.get("count", 0) or 0)
        severity = str(row.get("severity") or "error")
        threshold = (
            settings.observability.traceability_min_events_for_alert
            if severity == "critical"
            else settings.observability.traceability_warning_events_for_alert
        )
        if count < threshold:
            continue
        alerts.append({
            "code": "traceability_error_spike",
            "severity": "critical" if severity == "critical" else "warning",
            "message": (
                f"Traceability error {row.get('error_code')} in subsystem "
                f"{row.get('subsystem')} occurred {count} time(s)."
            ),
            "error_code": row.get("error_code"),
            "subsystem": row.get("subsystem"),
            "event_count": count,
        })
    return alerts


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

    ocr_rows = snapshot_ocr_metrics()
    if ocr_rows:
        totals = {row["outcome"]: row["count"] for row in ocr_rows}
        processed = totals.get("processed", 0.0)
        failed = totals.get("failed", 0.0)
        review_required = totals.get("review_required", 0.0)
        total_events = processed + failed
        if total_events >= settings.observability.ocr_min_events_for_alert:
            failure_pct = (failed / max(total_events, 1)) * 100
            if failure_pct >= settings.observability.ocr_failure_warn_pct:
                alerts.append({
                    "code": "ocr_failure_rate_high",
                    "severity": "critical",
                    "message": f"OCR failure rate reached {failure_pct:.1f}% over {int(total_events)} events.",
                })
            review_pct = (review_required / max(processed, 1)) * 100
            if review_pct >= settings.observability.ocr_review_warn_pct:
                alerts.append({
                    "code": "ocr_review_rate_high",
                    "severity": "warning",
                    "message": f"OCR review-required rate is {review_pct:.1f}% over {int(processed)} processed images.",
                })

    alerts.extend(_build_stage_latency_alerts())
    alerts.extend(_build_mascot_failure_alerts())
    alerts.extend(_build_traceability_error_alerts())
    return alerts
