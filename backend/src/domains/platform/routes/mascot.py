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
from src.domains.platform.application.mascot_release_gate import (
    build_combined_staging_packet_markdown as _build_combined_staging_packet_markdown_impl,
    build_mascot_metric_snapshot as _build_mascot_metric_snapshot_impl,
    build_release_gate_evidence_markdown as _build_release_gate_evidence_markdown_impl,
    build_release_gate_snapshot as _build_release_gate_snapshot_impl,
)
from src.domains.platform.application.mascot_suggestions import (
    build_student_mascot_suggestions as _build_student_mascot_suggestions_impl,
)
from src.domains.platform.application.whatsapp_analytics import build_whatsapp_usage_snapshot
from src.domains.platform.services.alerting import get_active_alerts
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

router = APIRouter(prefix="/api/mascot", tags=["mascot"])
_build_whatsapp_usage_snapshot = build_whatsapp_usage_snapshot


def _require_admin(current_user: User) -> None:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")


def _build_mascot_metric_snapshot() -> dict[str, int]:
    return _build_mascot_metric_snapshot_impl(snapshot_stage_latency_metrics())


async def _build_release_gate_snapshot(
    *,
    current_user: User,
    session: AsyncSession,
    days: int,
) -> dict:
    return await _build_release_gate_snapshot_impl(
        tenant_id=current_user.tenant_id,
        session=session,
        days=days,
        metric_rows=snapshot_stage_latency_metrics(),
        alerts=get_active_alerts(str(current_user.tenant_id)),
    )


def _build_release_gate_evidence_markdown(*, snapshot: dict) -> str:
    return _build_release_gate_evidence_markdown_impl(snapshot=snapshot)


def _build_combined_staging_packet_markdown(*, whatsapp_snapshot: dict, mascot_snapshot: dict) -> str:
    return _build_combined_staging_packet_markdown_impl(
        whatsapp_snapshot=whatsapp_snapshot,
        mascot_snapshot=mascot_snapshot,
    )


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
        suggestions = _build_student_mascot_suggestions_impl(
            db=db,
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            current_route=current_route,
            notebook_id=notebook_id,
        )
        if suggestions:
            return {"suggestions": suggestions}

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
