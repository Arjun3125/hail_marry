"""Observability adapters used by admin interfaces."""

from __future__ import annotations

from src.domains.platform.services.alerting import get_active_alerts
from src.domains.platform.services.metrics_registry import snapshot_ocr_metrics
from src.domains.platform.services.observability_notifier import dispatch_alerts
from src.domains.platform.services.trace_backend import get_trace_events
from src.domains.platform.services.traceability import build_traceability_summary
from src.domains.platform.services.usage_governance import build_usage_snapshot


def list_active_alerts(tenant_id: str) -> list[dict]:
    return get_active_alerts(tenant_id)


async def dispatch_active_alerts(db, tenant_id: str, alerts: list[dict]) -> dict:
    return await dispatch_alerts(db, tenant_id, alerts)


def load_trace_events(trace_id: str, tenant_id) -> list[dict]:
    return get_trace_events(trace_id, tenant_id)


def load_ocr_metrics() -> list[dict]:
    return snapshot_ocr_metrics()


def load_traceability_summary(*, tenant_id, days: int = 7) -> dict:
    return build_traceability_summary(tenant_id=tenant_id, days=days)


def load_usage_snapshot(db, *, tenant_id, days: int = 7) -> dict:
    return build_usage_snapshot(db, tenant_id=tenant_id, days=days)
