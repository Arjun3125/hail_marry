"""Mascot assistant API routes."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from database import SessionLocal, get_async_session, get_db
from src.domains.identity.models.user import User
from src.domains.platform.models.audit import AuditLog
from src.domains.platform.routes.whatsapp import _build_whatsapp_usage_snapshot
from src.domains.platform.services.alerting import get_active_alerts
from src.domains.platform.services.learner_profile_service import get_learner_profile_dict
from src.domains.platform.services.metrics_registry import snapshot_stage_latency_metrics
from src.domains.platform.services.whatsapp_gateway import get_whatsapp_metrics
from src.domains.platform.services.mascot_orchestrator import (
    clear_mascot_session,
    execute_pending_confirmation,
    get_mascot_session,
    get_mascot_suggestions,
    handle_mascot_upload,
    handle_mascot_message,
)
from src.domains.platform.services.mascot_schemas import MascotConfirmRequest, MascotMessageRequest, MascotUIContext
from src.domains.platform.services.mastery_tracking_service import build_profile_aware_recommendations

router = APIRouter(prefix="/api/mascot", tags=["mascot"])


def _require_admin(current_user: User) -> None:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")


def _build_mascot_metric_snapshot() -> dict[str, int]:
    rows = [row for row in snapshot_stage_latency_metrics() if row.get("stage") == "mascot"]
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


async def _build_release_gate_snapshot(
    *,
    current_user: User,
    session: AsyncSession,
    days: int,
) -> dict:
    since = datetime.now(timezone.utc) - timedelta(days=days)
    tenant_id = current_user.tenant_id

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

    metrics = _build_mascot_metric_snapshot()

    def _pct(numerator: int, denominator: int) -> float:
        if denominator <= 0:
            return 0.0
        return round((numerator / denominator) * 100, 2)

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
    alerts = [
        alert
        for alert in get_active_alerts(str(tenant_id))
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
        "active_alerts": alerts,
    }


def _build_release_gate_evidence_markdown(*, snapshot: dict) -> str:
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


def _build_combined_staging_packet_markdown(*, whatsapp_snapshot: dict, mascot_snapshot: dict) -> str:
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


@router.post("/message")
async def mascot_message(
    request: MascotMessageRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    request.role = current_user.role
    request.tenant_id = str(current_user.tenant_id)
    request.user_id = str(current_user.id)
    if request.ui_context and request.ui_context.selected_notebook_id and not request.notebook_id:
        request.notebook_id = request.ui_context.selected_notebook_id
    return await handle_mascot_message(request, session)


@router.post("/upload")
async def mascot_upload(
    file: UploadFile = File(...),
    message: str = Form(default=""),
    notebook_id: str | None = Form(default=None),
    session_id: str | None = Form(default=None),
    current_route: str | None = Form(default=None),
    current_page_entity: str | None = Form(default=None),
    current_page_entity_id: str | None = Form(default=None),
    context_metadata: str | None = Form(default=None),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    metadata: dict = {}
    if context_metadata:
        try:
            parsed = json.loads(context_metadata)
            if isinstance(parsed, dict):
                metadata = parsed
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid context metadata") from None
    request = MascotMessageRequest(
        message=message,
        channel="web",
        role=current_user.role,
        tenant_id=str(current_user.tenant_id),
        user_id=str(current_user.id),
        notebook_id=notebook_id,
        session_id=session_id,
        ui_context=MascotUIContext(
            current_route=current_route,
            selected_notebook_id=notebook_id,
            current_page_entity=current_page_entity,
            current_page_entity_id=current_page_entity_id,
            metadata=metadata,
        ),
    )
    try:
        return await handle_mascot_upload(
            request=request,
            session=session,
            filename=file.filename or "",
            content=await file.read(),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/confirm")
async def mascot_confirm(
    request: MascotConfirmRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    return await execute_pending_confirmation(
        confirmation_id=request.confirmation_id,
        approved=request.approved,
        channel=request.channel,
        session_id=request.session_id,
        tenant_id=str(current_user.tenant_id),
        user_id=str(current_user.id),
        role=current_user.role,
        session=session,
    )


@router.get("/suggestions")
async def mascot_suggestions(
    current_route: str | None = Query(default=None),
    notebook_id: str | None = Query(default=None),
    current_page_entity: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role == "student":
        notebook_uuid = None
        if notebook_id:
            try:
                notebook_uuid = UUID(str(notebook_id))
            except ValueError as exc:
                raise HTTPException(status_code=400, detail="Invalid notebook_id") from exc

        route = (current_route or "").lower()
        if "ai-studio" in route:
            current_surface = "ai_studio"
        elif "overview" in route:
            current_surface = "overview"
        elif "assistant" in route:
            current_surface = "assistant"
        elif "upload" in route:
            current_surface = "upload"
        else:
            current_surface = None

        learner_profile = get_learner_profile_dict(
            db,
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
        )
        items = build_profile_aware_recommendations(
            db,
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            notebook_id=notebook_uuid,
            current_surface=current_surface,
            learner_profile=learner_profile,
        )
        db.commit()
        if items:
            return {"suggestions": [str(item.get("label") or item.get("prompt") or "") for item in items[:4] if item.get("label") or item.get("prompt")]}

    return {
        "suggestions": get_mascot_suggestions(
            role=current_user.role,
            current_route=current_route,
            notebook_id=notebook_id,
            current_page_entity=current_page_entity,
        )
    }


@router.get("/session")
async def mascot_session(
    channel: str = Query(default="web"),
    session_id: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
):
    return get_mascot_session(channel=channel, user_id=str(current_user.id), session_id=session_id)


@router.delete("/session")
async def mascot_session_clear(
    channel: str = Query(default="web"),
    session_id: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
):
    clear_mascot_session(channel=channel, user_id=str(current_user.id), session_id=session_id)
    return {"cleared": True}


@router.get("/release-gate-snapshot")
async def mascot_release_gate_snapshot(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
    days: int = Query(7, ge=1, le=90),
):
    _require_admin(current_user)
    return await _build_release_gate_snapshot(current_user=current_user, session=session, days=days)


@router.get("/release-gate-evidence")
async def mascot_release_gate_evidence(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
    days: int = Query(7, ge=1, le=90),
):
    _require_admin(current_user)
    snapshot = await _build_release_gate_snapshot(current_user=current_user, session=session, days=days)
    generated_at = snapshot["generated_at"]
    safe_stamp = generated_at.replace(":", "-")
    return {
        "generated_at": generated_at,
        "filename": f"mascot_release_gate_evidence_{safe_stamp}.md",
        "markdown": _build_release_gate_evidence_markdown(snapshot=snapshot),
        "snapshot": snapshot,
    }


@router.get("/staging-packet")
async def mascot_staging_packet(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
    days: int = Query(7, ge=1, le=90),
):
    _require_admin(current_user)
    mascot_snapshot = await _build_release_gate_snapshot(current_user=current_user, session=session, days=days)

    sync_db = SessionLocal()
    try:
        whatsapp_analytics = _build_whatsapp_usage_snapshot(current_user, sync_db, days)
    finally:
        sync_db.close()

    whatsapp_metrics = get_whatsapp_metrics(str(current_user.tenant_id))

    def _pct(numerator: int, denominator: int) -> float:
        if denominator <= 0:
            return 0.0
        return round((numerator / denominator) * 100, 2)

    routing_total = whatsapp_metrics.get("routing_success_total", 0) + whatsapp_metrics.get("routing_failure_total", 0)
    outbound_total = whatsapp_metrics.get("outbound_success_total", 0) + whatsapp_metrics.get("outbound_failure_total", 0)
    inbound_total = whatsapp_metrics.get("inbound_total", 0)
    whatsapp_snapshot = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "period_days": days,
        "analytics": whatsapp_analytics,
        "release_gate_metrics": whatsapp_metrics,
        "derived_rates": {
            "routing_failure_pct": _pct(whatsapp_metrics.get("routing_failure_total", 0), routing_total),
            "duplicate_inbound_pct": _pct(whatsapp_metrics.get("duplicate_inbound_total", 0), inbound_total),
            "visible_failure_pct": _pct(whatsapp_metrics.get("visible_failure_total", 0), inbound_total),
            "outbound_retryable_failure_pct": _pct(whatsapp_metrics.get("outbound_retryable_failure_total", 0), outbound_total),
        },
    }
    generated_at = datetime.now(timezone.utc).isoformat()
    safe_stamp = generated_at.replace(":", "-")
    return {
        "generated_at": generated_at,
        "filename": f"mascot_whatsapp_staging_packet_{safe_stamp}.md",
        "markdown": _build_combined_staging_packet_markdown(
            whatsapp_snapshot=whatsapp_snapshot,
            mascot_snapshot=mascot_snapshot,
        ),
        "whatsapp_snapshot": whatsapp_snapshot,
        "mascot_snapshot": mascot_snapshot,
    }
