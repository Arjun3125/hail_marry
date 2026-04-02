"""Application helpers for mascot release-gate and staging packet APIs."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.platform.models.audit import AuditLog


def build_mascot_metric_snapshot(stage_rows: list[dict]) -> dict[str, int]:
    rows = [row for row in stage_rows if row.get("stage") == "mascot"]
    operations = ("interpretation", "execution", "confirmation", "upload")
    snapshot: dict[str, int] = {}
    for operation in operations:
        success_total = 0
        failure_total = 0
        cancelled_total = 0
        for row in rows:
            if row.get("operation") != operation:
                continue
            count = int(row.get("count", 0) or 0)
            outcome = str(row.get("outcome") or "")
            if outcome == "success":
                success_total += count
            elif outcome == "cancelled":
                cancelled_total += count
            else:
                failure_total += count
        snapshot[f"{operation}_success_total"] = success_total
        snapshot[f"{operation}_failure_total"] = failure_total
        if cancelled_total:
            snapshot[f"{operation}_cancelled_total"] = cancelled_total
    return snapshot


def _pct(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round((numerator / denominator) * 100, 2)


async def build_release_gate_snapshot(
    *,
    tenant_id,
    session: AsyncSession,
    days: int,
    metric_rows: list[dict],
    alerts: list[dict],
) -> dict:
    since = datetime.now(timezone.utc) - timedelta(days=days)

    total_actions = (
        await session.execute(
            select(func.count(AuditLog.id)).where(
                AuditLog.tenant_id == tenant_id,
                AuditLog.action.in_(["mascot.message", "mascot.upload", "mascot.confirmation"]),
                AuditLog.created_at >= since,
            )
        )
    ).scalar() or 0
    unique_users = (
        await session.execute(
            select(func.count(func.distinct(AuditLog.user_id))).where(
                AuditLog.tenant_id == tenant_id,
                AuditLog.action.in_(["mascot.message", "mascot.upload", "mascot.confirmation"]),
                AuditLog.created_at >= since,
                AuditLog.user_id.is_not(None),
            )
        )
    ).scalar() or 0

    metrics = build_mascot_metric_snapshot(metric_rows)
    interpretation_total = metrics.get("interpretation_success_total", 0) + metrics.get("interpretation_failure_total", 0)
    execution_total = metrics.get("execution_success_total", 0) + metrics.get("execution_failure_total", 0)
    upload_total = metrics.get("upload_success_total", 0) + metrics.get("upload_failure_total", 0)
    confirmation_total = (
        metrics.get("confirmation_success_total", 0)
        + metrics.get("confirmation_failure_total", 0)
        + metrics.get("confirmation_cancelled_total", 0)
    )
    overall_total = interpretation_total + execution_total + upload_total + confirmation_total
    overall_failures = (
        metrics.get("interpretation_failure_total", 0)
        + metrics.get("execution_failure_total", 0)
        + metrics.get("upload_failure_total", 0)
        + metrics.get("confirmation_failure_total", 0)
    )
    mascot_alerts = [
        alert
        for alert in alerts
        if alert.get("code") == "mascot_failure_rate_high" or alert.get("stage") == "mascot"
    ]

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "period_days": days,
        "analytics": {
            "total_actions": int(total_actions),
            "unique_users": int(unique_users),
        },
        "release_gate_metrics": metrics,
        "derived_rates": {
            "interpretation_failure_pct": _pct(metrics.get("interpretation_failure_total", 0), interpretation_total),
            "execution_failure_pct": _pct(metrics.get("execution_failure_total", 0), execution_total),
            "upload_failure_pct": _pct(metrics.get("upload_failure_total", 0), upload_total),
            "confirmation_failure_pct": _pct(metrics.get("confirmation_failure_total", 0), confirmation_total),
            "overall_failure_pct": _pct(overall_failures, overall_total),
        },
        "active_alerts": mascot_alerts,
    }


def build_release_gate_evidence_markdown(*, snapshot: dict) -> str:
    generated_at = snapshot.get("generated_at", "")
    analytics = snapshot.get("analytics", {})
    metrics = snapshot.get("release_gate_metrics", {})
    derived_rates = snapshot.get("derived_rates", {})
    active_alerts = snapshot.get("active_alerts", [])
    alert_summary = "; ".join(
        f"{alert.get('code', 'unknown')} ({alert.get('severity', 'unknown')}): {alert.get('message', '')}".strip()
        for alert in active_alerts
    ) or "none"
    return "\n".join([
        "# Mascot Release Gate Evidence",
        "",
        f"Date: {generated_at}",
        "Tester / operator: __________",
        "Environment: __________",
        "Commit / build: __________",
        "",
        "## Automated Gate",
        "",
        "| Check | Result | Notes |",
        "| --- | --- | --- |",
        "| `backend/tests/test_mascot_routes.py` | Pass / Fail | __________ |",
        "| `backend/tests/test_mascot_whatsapp_adapter.py` | Pass / Fail | __________ |",
        "| `backend/tests/test_alerting.py` | Pass / Fail | __________ |",
        "| `frontend/tests/e2e/mascot-assistant.spec.ts` | Pass / Fail | __________ |",
        "| `frontend/tests/e2e/admin-dashboard.spec.ts` | Pass / Fail | __________ |",
        "| `python -m py_compile ... mascot_orchestrator/routes/alerting/config` | Pass / Fail | __________ |",
        "| `npm run build` | Pass / Fail | __________ |",
        "",
        "## Mascot Snapshot",
        "",
        "- endpoint: `GET /api/mascot/release-gate-snapshot?days=7`",
        f"- captured at: {generated_at}",
        "- attach raw response: __________",
        "",
        "### Key values",
        "",
        f"- total mascot actions: {analytics.get('total_actions', 0)}",
        f"- unique mascot users: {analytics.get('unique_users', 0)}",
        f"- interpretation failure %: {derived_rates.get('interpretation_failure_pct', 0.0)}",
        f"- execution failure %: {derived_rates.get('execution_failure_pct', 0.0)}",
        f"- upload failure %: {derived_rates.get('upload_failure_pct', 0.0)}",
        f"- confirmation failure %: {derived_rates.get('confirmation_failure_pct', 0.0)}",
        f"- overall failure %: {derived_rates.get('overall_failure_pct', 0.0)}",
        f"- active mascot alerts: {len(active_alerts)}",
        f"- active alert summary: {alert_summary}",
        "",
        "### Raw metric totals",
        "",
        f"- interpretation success total: {metrics.get('interpretation_success_total', 0)}",
        f"- interpretation failure total: {metrics.get('interpretation_failure_total', 0)}",
        f"- execution success total: {metrics.get('execution_success_total', 0)}",
        f"- execution failure total: {metrics.get('execution_failure_total', 0)}",
        f"- upload success total: {metrics.get('upload_success_total', 0)}",
        f"- upload failure total: {metrics.get('upload_failure_total', 0)}",
        f"- confirmation success total: {metrics.get('confirmation_success_total', 0)}",
        f"- confirmation failure total: {metrics.get('confirmation_failure_total', 0)}",
        f"- confirmation cancelled total: {metrics.get('confirmation_cancelled_total', 0)}",
        "",
        "## Dashboard Verification",
        "",
        "- admin dashboard `Mascot Release Gate` card visible: Pass / Fail",
        "- admin dashboard values match API snapshot: Pass / Fail",
        "- notes: __________",
        "",
        "## WhatsApp Mascot Staging",
        "",
        "- script used: `documentation/mascot_whatsapp_staging_manual_test_script.md`",
        "- result: Pass / Fail",
        "- evidence location: __________",
        "",
        "## Sign-Off",
        "",
        "- open P0 mascot issues: Yes / No",
        "- open P1 mascot issues: Yes / No",
        "- release recommendation: Approve / Block",
        "- sign-off notes: __________",
    ])


def build_combined_staging_packet_markdown(*, whatsapp_snapshot: dict, mascot_snapshot: dict) -> str:
    whatsapp_analytics = whatsapp_snapshot.get("analytics", {})
    whatsapp_metrics = whatsapp_snapshot.get("release_gate_metrics", {})
    whatsapp_rates = whatsapp_snapshot.get("derived_rates", {})
    mascot_analytics = mascot_snapshot.get("analytics", {})
    mascot_metrics = mascot_snapshot.get("release_gate_metrics", {})
    mascot_rates = mascot_snapshot.get("derived_rates", {})
    return "\n".join([
        "# Mascot WhatsApp Staging Packet",
        "",
        f"Generated at: {datetime.now(timezone.utc).isoformat()}",
        f"WhatsApp snapshot generated at: {whatsapp_snapshot.get('generated_at', '')}",
        f"Mascot snapshot generated at: {mascot_snapshot.get('generated_at', '')}",
        "",
        "## Environment",
        "",
        "- Environment: __________",
        "- Webhook target: __________",
        "- Build / commit: __________",
        "- QA owner: __________",
        "- Engineering owner: __________",
        "- Test device phone: __________",
        "",
        "## WhatsApp Release Snapshot",
        "",
        f"- total messages: {whatsapp_analytics.get('total_messages', 0)}",
        f"- unique users: {whatsapp_analytics.get('unique_users', 0)}",
        f"- avg latency ms: {whatsapp_analytics.get('avg_latency_ms', 'N/A')}",
        f"- routing failure %: {whatsapp_rates.get('routing_failure_pct', 0.0)}",
        f"- duplicate inbound %: {whatsapp_rates.get('duplicate_inbound_pct', 0.0)}",
        f"- visible failure %: {whatsapp_rates.get('visible_failure_pct', 0.0)}",
        f"- outbound retryable failure %: {whatsapp_rates.get('outbound_retryable_failure_pct', 0.0)}",
        f"- routing failures: {whatsapp_metrics.get('routing_failure_total', 0)}",
        f"- duplicate inbound total: {whatsapp_metrics.get('duplicate_inbound_total', 0)}",
        f"- upload ingest failures: {whatsapp_metrics.get('upload_ingest_failure_total', 0)}",
        f"- link ingest failures: {whatsapp_metrics.get('link_ingest_failure_total', 0)}",
        f"- visible failures: {whatsapp_metrics.get('visible_failure_total', 0)}",
        "",
        "## Mascot Release Snapshot",
        "",
        f"- total mascot actions: {mascot_analytics.get('total_actions', 0)}",
        f"- unique mascot users: {mascot_analytics.get('unique_users', 0)}",
        f"- interpretation failure %: {mascot_rates.get('interpretation_failure_pct', 0.0)}",
        f"- execution failure %: {mascot_rates.get('execution_failure_pct', 0.0)}",
        f"- upload failure %: {mascot_rates.get('upload_failure_pct', 0.0)}",
        f"- confirmation failure %: {mascot_rates.get('confirmation_failure_pct', 0.0)}",
        f"- overall failure %: {mascot_rates.get('overall_failure_pct', 0.0)}",
        f"- execution failures: {mascot_metrics.get('execution_failure_total', 0)}",
        f"- upload failures: {mascot_metrics.get('upload_failure_total', 0)}",
        f"- confirmation cancelled: {mascot_metrics.get('confirmation_cancelled_total', 0)}",
        f"- active mascot alerts: {len(mascot_snapshot.get('active_alerts', []))}",
        "",
        "## Live Staging Checklist",
        "",
        "Use `documentation/mascot_whatsapp_staging_manual_test_script.md`.",
        "",
        "| Flow | Result | Evidence | Notes |",
        "| --- | --- | --- | --- |",
        "| Basic entry and notebook continuity | __________ | __________ | __________ |",
        "| Mixed-language command handling | __________ | __________ | __________ |",
        "| Structured output formatting | __________ | __________ | __________ |",
        "| Ingestion and follow-up continuity | __________ | __________ | __________ |",
        "| Confirmation loop safety | __________ | __________ | __________ |",
        "| Parent and role scoping | __________ | __________ | __________ |",
        "| Error and retry behavior | __________ | __________ | __________ |",
        "",
        "## Decision",
        "",
        "- Recommendation: Pass / Pass with waiver / Fail",
        "- Blocking issues: __________",
        "- Waivers approved by: __________",
        "- Follow-up actions: __________",
    ])
