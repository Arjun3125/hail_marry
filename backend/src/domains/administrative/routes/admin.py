"""Admin API routes â€” dashboard, users, AI usage, AI review, complaints, reports, security, settings."""
import logging

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import Row, desc
from datetime import datetime, time
from pydantic import BaseModel
from typing import List, Optional, Tuple
import io
from uuid import UUID

from sqlalchemy.orm.query import RowReturningQuery
from starlette.responses import StreamingResponse
from starlette.responses import Response as StarletteResponse
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session, get_db
from auth.dependencies import require_role
from src.domains.identity.models.user import User
from src.domains.identity.application.passwords import hash_password
from src.domains.administrative.application.admin_onboarding import (
    process_student_onboarding_upload as _process_student_onboarding_upload_impl,
    process_teacher_onboarding_upload as _process_teacher_onboarding_upload_impl,
)
from src.domains.administrative.application.ai_review import (
    build_ai_review_detail_response as _build_ai_review_detail_response_impl,
    build_ai_review_list_response as _build_ai_review_list_response_impl,
)
from src.domains.administrative.application.ai_jobs import (
    build_ai_job_detail_response as _build_ai_job_detail_response_impl,
    build_ai_job_list_response as _build_ai_job_list_response_impl,
)
from src.domains.administrative.application.complaints import (
    build_admin_complaints_response as _build_admin_complaints_response_impl,
    update_admin_complaint as _update_admin_complaint_impl,
)
from src.domains.administrative.application.communications import (
    build_admin_report_card_payload as _build_admin_report_card_payload_impl,
    send_admin_whatsapp_digest_bulk as _send_admin_whatsapp_digest_bulk_impl,
)
from src.domains.administrative.application.academics import (
    build_admin_classes_response as _build_admin_classes_response_impl,
    build_admin_timetable_response as _build_admin_timetable_response_impl,
    create_admin_class as _create_admin_class_impl,
    create_admin_subject as _create_admin_subject_impl,
    create_admin_timetable_slot as _create_admin_timetable_slot_impl,
    delete_admin_timetable_slot as _delete_admin_timetable_slot_impl,
    generate_admin_timetable_schedule as _generate_admin_timetable_schedule_impl,
)
from src.domains.administrative.application.dashboard import (
    build_admin_dashboard_response as _build_admin_dashboard_response_impl,
)
from src.domains.administrative.application.parent_links import (
    build_admin_parent_links_response as _build_admin_parent_links_response_impl,
    create_admin_parent_link as _create_admin_parent_link_impl,
    delete_admin_parent_link as _delete_admin_parent_link_impl,
)
from src.domains.administrative.application.reporting import (
    build_admin_ai_usage_csv_export as _build_admin_ai_usage_csv_export_impl,
    build_admin_ai_usage_report as _build_admin_ai_usage_report_impl,
    build_admin_attendance_csv_export as _build_admin_attendance_csv_export_impl,
    build_admin_attendance_report as _build_admin_attendance_report_impl,
    build_admin_billing_info as _build_admin_billing_info_impl,
    build_admin_performance_csv_export as _build_admin_performance_csv_export_impl,
    build_admin_performance_heatmap as _build_admin_performance_heatmap_impl,
    build_admin_performance_report as _build_admin_performance_report_impl,
    build_admin_security_logs as _build_admin_security_logs_impl,
)
from src.domains.administrative.application.settings import (
    build_admin_settings_response as _build_admin_settings_response_impl,
    update_admin_settings as _update_admin_settings_impl,
)
from src.domains.administrative.application.user_management import (
    build_admin_csv_template_payload as _build_admin_csv_template_payload_impl,
    build_admin_students_response as _build_admin_students_response_impl,
    build_admin_users_response as _build_admin_users_response_impl,
    change_admin_user_role as _change_admin_user_role_impl,
    generate_admin_qr_tokens as _generate_admin_qr_tokens_impl,
    toggle_admin_user_active as _toggle_admin_user_active_impl,
)
from src.domains.administrative.application.webhooks import (
    build_admin_webhook_deliveries_response as _build_admin_webhook_deliveries_response_impl,
    build_admin_webhooks_response as _build_admin_webhooks_response_impl,
    create_admin_webhook as _create_admin_webhook_impl,
    delete_admin_webhook as _delete_admin_webhook_impl,
    toggle_admin_webhook as _toggle_admin_webhook_impl,
)
from src.domains.platform.models.ai import AIQuery
from src.domains.platform.models.audit import AuditLog
from src.domains.academic.services.report_card import generate_report_card_pdf
from src.domains.academic.services.whatsapp import send_weekly_digest
from src.domains.academic.services.timetable_generator import generate_timetable
from src.infrastructure.messaging import (
    cancel_admin_job,
    dead_letter_admin_job,
    drain_admin_queue,
    emit_webhook_event,
    get_admin_job_detail,
    list_admin_jobs,
    load_queue_metrics,
    pause_admin_queue,
    resume_admin_queue,
    retry_admin_job,
)
from src.infrastructure.observability import (
    dispatch_active_alerts,
    list_active_alerts,
    load_ocr_metrics,
    load_trace_events,
    load_traceability_summary,
    load_usage_snapshot,
)
from src.domains.platform.application.mascot_release_gate import (
    build_release_gate_snapshot as _build_release_gate_snapshot_impl,
)
from src.domains.platform.application.whatsapp_analytics import (
    build_whatsapp_usage_snapshot as _build_whatsapp_usage_snapshot_impl,
)
from src.domains.platform.services.alerting import get_active_alerts
from src.domains.platform.services.metrics_registry import snapshot_stage_latency_metrics
from src.domains.platform.services.whatsapp_gateway import get_whatsapp_metrics
from src.shared.ocr_imports import (
    extract_upload_content_result,
    get_extension,
    parse_account_rows_with_diagnostics,
    parse_student_import_rows_with_diagnostics,
)

router = APIRouter(prefix="/api/admin", tags=["Admin"])
logger: logging.Logger = logging.getLogger(__name__)

ALLOWED_COMPLAINT_STATUSES: set[str] = {"open", "in_review", "resolved"}
SUPPORTED_WEBHOOK_EVENTS: set[str] = {
    "student.enrolled",
    "document.ingested",
    "ai.query.completed",
    "exam.results.published",
    "attendance.marked",
    "complaint.status.changed",
}


def _pct(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round((numerator / denominator) * 100, 2)


def _build_whatsapp_release_gate_snapshot(current_user: User, db: Session, days: int) -> dict:
    analytics = _build_whatsapp_usage_snapshot_impl(current_user, db, days)
    metrics: dict[str, int] = get_whatsapp_metrics(str(current_user.tenant_id))
    routing_total: int = metrics.get("routing_success_total", 0) + metrics.get("routing_failure_total", 0)
    outbound_total: int = metrics.get("outbound_success_total", 0) + metrics.get("outbound_failure_total", 0)
    inbound_total: int = metrics.get("inbound_total", 0)
    return {
        "generated_at": datetime.utcnow().isoformat(),
        "period_days": days,
        "analytics": analytics,
        "release_gate_metrics": metrics,
        "derived_rates": {
            "routing_failure_pct": _pct(metrics.get("routing_failure_total", 0), routing_total),
            "duplicate_inbound_pct": _pct(metrics.get("duplicate_inbound_total", 0), inbound_total),
            "visible_failure_pct": _pct(metrics.get("visible_failure_total", 0), inbound_total),
            "outbound_retryable_failure_pct": _pct(metrics.get("outbound_retryable_failure_total", 0), outbound_total),
        },
    }


def _parse_uuid(value: str, field_name: str) -> UUID:
    try:
        return UUID(str(value))
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail=f"Invalid {field_name}")


def _parse_hhmm(value: str, field_name: str) -> time:
    try:
        return datetime.strptime(value, "%H:%M").time()
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail=f"Invalid {field_name}. Expected HH:MM")


def _review_status_from_action(action: str | None) -> str:
    if not action:
        return "pending"
    if action.endswith("approved"):
        return "approved"
    if action.endswith("flagged"):
        return "flagged"
    return "pending"


def _resolve_user_names(db: Session, user_ids: list[str]) -> dict[str, str]:
    ids = []
    for user_id in user_ids:
        if not user_id:
            continue
        try:
            ids.append(UUID(str(user_id)))
        except (TypeError, ValueError):
            continue
    if not ids:
        return {}
    rows: List[Row[Tuple[UUID, str, str]]] = db.query(User.id, User.full_name, User.email).filter(User.id.in_(ids)).all()
    return {
        str(row[0]): f"{row[1]} ({row[2]})"
        for row in rows
    }


def _ai_job_audit_history(
    db: Session,
    *,
    tenant_id: UUID,
    job_id: str | None = None,
    limit: int = 50,
) -> list[dict]:
    query: RowReturningQuery[Tuple[AuditLog, str, str]] = db.query(AuditLog, User.full_name, User.email).outerjoin(User, AuditLog.user_id == User.id).filter(
        AuditLog.tenant_id == tenant_id,
        AuditLog.entity_type == "ai_job",
    )
    if job_id:
        job_uuid: UUID = _parse_uuid(job_id, "job_id")
        query: RowReturningQuery[Tuple[AuditLog, str, str]] = query.filter(AuditLog.entity_id == job_uuid)
    rows: List[Row[Tuple[AuditLog, str, str]]] = query.order_by(desc(AuditLog.created_at)).limit(max(1, min(limit, 200))).all()
    history = []
    for row, full_name, email in rows:
        metadata = row.metadata_ or {}
        history.append({
            "action": row.action,
            "actor": full_name or email,
            "created_at": str(row.created_at),
            "metadata": metadata,
            "job_id": str(row.entity_id) if row.entity_id else metadata.get("job_id"),
        })
    return history


def _load_review_history(
    db: Session,
    *,
    tenant_id: UUID,
    query_ids: list[UUID],
) -> tuple[dict[str, list[dict]], dict[str, dict]]:
    if not query_ids:
        return {}, {}
    rows: List[Row[Tuple[AuditLog, str, str]]] = db.query(AuditLog, User.full_name, User.email).outerjoin(User, AuditLog.user_id == User.id).filter(
        AuditLog.tenant_id == tenant_id,
        AuditLog.entity_type == "ai_review",
        AuditLog.entity_id.in_(query_ids),
    ).order_by(desc(AuditLog.created_at)).all()
    history_map: dict[str, list[dict]] = {str(qid): [] for qid in query_ids}
    latest_map: dict[str, dict] = {}
    for row, full_name, email in rows:
        entry = {
            "action": row.action,
            "note": (row.metadata_ or {}).get("note"),
            "reviewed_by": full_name or email,
            "created_at": str(row.created_at),
        }
        key = str(row.entity_id)
        history_map.setdefault(key, []).append(entry)
        if key not in latest_map:
            latest_map[key] = entry
    return history_map, latest_map


class RoleChange(BaseModel):
    role: str

class ComplaintAction(BaseModel):
    status: str
    resolution_note: str = ""


class AIReviewAction(BaseModel):
    action: str
    note: str | None = None


class WebhookCreate(BaseModel):
    event_type: str
    target_url: str


class WebhookUpdate(BaseModel):
    is_active: bool


class ParentLinkCreate(BaseModel):
    parent_id: str
    child_id: str


# â”€â”€â”€ Dashboard â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@router.get("/dashboard")
async def admin_dashboard(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    return _build_admin_dashboard_response_impl(
        db=db,
        tenant_id=current_user.tenant_id,
        load_queue_metrics_fn=load_queue_metrics,
        list_active_alerts_fn=list_active_alerts,
    )


@router.get("/dashboard-bootstrap")
async def admin_dashboard_bootstrap(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
    session: AsyncSession = Depends(get_async_session),
):
    whatsapp_snapshot = None
    try:
        whatsapp_snapshot = _build_whatsapp_release_gate_snapshot(current_user, db, 7)
    except Exception:
        logger.exception(
            "Failed to build WhatsApp release gate snapshot for tenant %s",
            current_user.tenant_id,
        )
        whatsapp_snapshot = None

    mascot_snapshot = None
    try:
        mascot_snapshot = await _build_release_gate_snapshot_impl(
            tenant_id=current_user.tenant_id,
            session=session,
            days=7,
            metric_rows=snapshot_stage_latency_metrics(),
            alerts=get_active_alerts(str(current_user.tenant_id)),
        )
    except Exception:
        logger.exception(
            "Failed to build mascot release gate snapshot for tenant %s",
            current_user.tenant_id,
        )
        mascot_snapshot = None

    return {
        "dashboard": _build_admin_dashboard_response_impl(
            db=db,
            tenant_id=current_user.tenant_id,
            load_queue_metrics_fn=load_queue_metrics,
            list_active_alerts_fn=list_active_alerts,
        ),
        "security": _build_admin_security_logs_impl(
            db=db,
            tenant_id=current_user.tenant_id,
        ),
        "whatsapp_snapshot": whatsapp_snapshot,
        "mascot_snapshot": mascot_snapshot,
    }


# â”€â”€â”€ User Management â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@router.get("/users")
async def list_users(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    return _build_admin_users_response_impl(
        db=db,
        tenant_id=current_user.tenant_id,
    )


@router.get("/students")
async def list_students(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    return _build_admin_students_response_impl(
        db=db,
        tenant_id=current_user.tenant_id,
    )

@router.patch("/users/{user_id}/role")
async def change_user_role(user_id: str, data: RoleChange, current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    return _change_admin_user_role_impl(
        db=db,
        tenant_id=current_user.tenant_id,
        actor_user_id=current_user.id,
        user_id=user_id,
        role=data.role,
        parse_uuid_fn=_parse_uuid,
    )

@router.patch("/users/{user_id}/deactivate")
async def deactivate_user(user_id: str, current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    return _toggle_admin_user_active_impl(
        db=db,
        tenant_id=current_user.tenant_id,
        actor_user_id=current_user.id,
        user_id=user_id,
        parse_uuid_fn=_parse_uuid,
    )


# â”€â”€â”€ User Authority & Onboarding â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@router.post("/onboard/teachers")
async def onboard_teachers(
    file: UploadFile = File(...),
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
    preview: bool = False,
):
    """
    Onboard a list of teachers using either a CSV file or an Image (JPG/PNG).
    CSV Format: name, email, password (optional)
    Image Format: handwritten or printed list of names (one per line). Emails/passwords auto-generated.
    """
    safe_filename: str = file.filename or ""
    content: bytes = await file.read()
    return _process_teacher_onboarding_upload_impl(
        db=db,
        tenant_id=current_user.tenant_id,
        safe_filename=safe_filename,
        content=content,
        preview=preview,
        get_extension_fn=get_extension,
        extract_upload_content_result_fn=extract_upload_content_result,
        parse_account_rows_with_diagnostics_fn=parse_account_rows_with_diagnostics,
        hash_password_fn=hash_password,
    )


# â”€â”€â”€ Queue Operations â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@router.post("/queue/pause")
async def pause_ai_queue(current_user: User = Depends(require_role("admin"))):
    """Pause the AI background queue. Workers will stop pulling new jobs."""
    try:
        pause_admin_queue()
        return {"success": True, "message": "Queue paused successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/queue/resume")
async def resume_ai_queue(current_user: User = Depends(require_role("admin"))):
    """Resume the AI background queue."""
    try:
        resume_admin_queue()
        return {"success": True, "message": "Queue resumed successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/queue/drain")
async def drain_ai_queue(current_user: User = Depends(require_role("admin"))):
    """Drain all pending jobs immediately to dead-letter for this tenant."""
    try:
        drained_count: int = drain_admin_queue(str(current_user.tenant_id))
        return {"success": True, "message": f"Drained {drained_count} jobs.", "drained_count": drained_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# â”€â”€ AI Job Management â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@router.get("/ai-jobs/metrics")
async def ai_job_metrics(current_user: User = Depends(require_role("admin"))):
    return load_queue_metrics(str(current_user.tenant_id))


@router.get("/ai-jobs")
async def ai_job_list(
    limit: int = 50,
    status: str | None = None,
    job_type: str | None = None,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    return _build_ai_job_list_response_impl(
        db=db,
        tenant_id=current_user.tenant_id,
        limit=limit,
        status=status,
        job_type=job_type,
        list_admin_jobs_fn=list_admin_jobs,
        resolve_user_names_fn=_resolve_user_names,
    )


@router.get("/ai-jobs/history")
async def ai_job_history(
    limit: int = 50,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    return _ai_job_audit_history(db, tenant_id=current_user.tenant_id, limit=limit)


@router.get("/ai-jobs/{job_id}")
async def ai_job_detail(
    job_id: str,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    return _build_ai_job_detail_response_impl(
        db,
        tenant_id=current_user.tenant_id,
        job_id=job_id,
        get_admin_job_detail_fn=get_admin_job_detail,
        resolve_user_names_fn=_resolve_user_names,
        ai_job_audit_history_fn=_ai_job_audit_history,
    )


@router.post("/ai-jobs/{job_id}/cancel")
async def ai_job_cancel(
    job_id: str,
    current_user: User = Depends(require_role("admin")),
):
    return cancel_admin_job(job_id, str(current_user.tenant_id), actor_user_id=str(current_user.id))


@router.post("/ai-jobs/{job_id}/retry")
async def ai_job_retry(
    job_id: str,
    current_user: User = Depends(require_role("admin")),
):
    return retry_admin_job(job_id, str(current_user.tenant_id), actor_user_id=str(current_user.id))


@router.post("/ai-jobs/{job_id}/dead-letter")
async def ai_job_dead_letter(
    job_id: str,
    current_user: User = Depends(require_role("admin")),
):
    return dead_letter_admin_job(job_id, str(current_user.tenant_id), actor_user_id=str(current_user.id))

# â”€â”€â”€ AI Usage Analytics â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@router.get("/ai-usage")
async def ai_usage_analytics(current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    return load_usage_snapshot(db, tenant_id=current_user.tenant_id, days=7)


# â”€â”€â”€ AI Quality Review â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@router.get("/ai-review")
async def ai_review(current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    return _build_ai_review_list_response_impl(
        db=db,
        tenant_id=current_user.tenant_id,
        load_review_history_fn=_load_review_history,
        review_status_from_action_fn=_review_status_from_action,
    )


@router.get("/ai-review/{review_id}")
async def ai_review_detail(
    review_id: str,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    return _build_ai_review_detail_response_impl(
        db=db,
        tenant_id=current_user.tenant_id,
        review_id=review_id,
        parse_uuid_fn=_parse_uuid,
        load_review_history_fn=_load_review_history,
        review_status_from_action_fn=_review_status_from_action,
    )


@router.patch("/ai-review/{review_id}")
async def update_ai_review(
    review_id: str,
    data: AIReviewAction,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> dict[str, bool]:
    if data.action not in {"approve", "flag"}:
        raise HTTPException(status_code=400, detail="Invalid review action")

    review_uuid: UUID = _parse_uuid(review_id, "review_id")
    query: AIQuery | None = db.query(AIQuery).filter(
        AIQuery.tenant_id == current_user.tenant_id,
        AIQuery.id == review_uuid,
    ).first()
    if not query:
        raise HTTPException(status_code=404, detail="AI review item not found")

    action: str = "ai_review.approved" if data.action == "approve" else "ai_review.flagged"
    db.add(
        AuditLog(
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            action=action,
            entity_type="ai_review",
            entity_id=query.id,
            metadata_={"note": (data.note or "").strip()},
        )
    )
    db.commit()
    return {"success": True}


# â”€â”€ Observability â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@router.get("/observability/alerts")
async def observability_alerts(current_user: User = Depends(require_role("admin"))):
    return list_active_alerts(str(current_user.tenant_id))


@router.post("/observability/alerts/dispatch")
async def dispatch_observability_alerts(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    alerts = list_active_alerts(str(current_user.tenant_id))
    result = await dispatch_active_alerts(db, str(current_user.tenant_id), alerts)
    return {"alerts": len(alerts), **result}


@router.get("/observability/traces/{trace_id}")
async def trace_detail(
    trace_id: str,
    current_user: User = Depends(require_role("admin")),
):
    events = load_trace_events(trace_id, current_user.tenant_id)
    if not events:
        raise HTTPException(status_code=404, detail="Trace not found")
    return {"trace_id": trace_id, "events": events}


@router.get("/observability/ocr-metrics")
async def ocr_metrics(current_user: User = Depends(require_role("admin"))):
    return {"metrics": load_ocr_metrics()}


@router.get("/observability/traceability")
async def traceability_summary(
    days: int = 7,
    current_user: User = Depends(require_role("admin")),
):
    return load_traceability_summary(tenant_id=current_user.tenant_id, days=days)


# â”€â”€â”€ Complaints Oversight â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@router.get("/complaints")
async def admin_complaints(current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    return _build_admin_complaints_response_impl(
        db=db,
        tenant_id=current_user.tenant_id,
    )

@router.patch("/complaints/{complaint_id}")
async def update_complaint(complaint_id: str, data: ComplaintAction, current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)) -> dict[str, bool]:
    result = _update_admin_complaint_impl(
        db=db,
        tenant_id=current_user.tenant_id,
        actor_user_id=current_user.id,
        complaint_id=complaint_id,
        status=data.status,
        resolution_note=data.resolution_note,
        parse_uuid_fn=_parse_uuid,
        allowed_statuses=ALLOWED_COMPLAINT_STATUSES,
    )
    result["complaint"]

    try:
        await emit_webhook_event(
            db=db,
            tenant_id=current_user.tenant_id,
            event_type="complaint.status.changed",
            data=result["webhook_payload"],
        )
    except Exception:
        # Primary complaint workflow should not fail if webhook delivery fails.
        pass

    return {"success": True}


# â”€â”€â”€ Class & Subject Management â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@router.get("/classes")
async def admin_classes(current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    return _build_admin_classes_response_impl(
        db=db,
        tenant_id=current_user.tenant_id,
    )

class ClassCreate(BaseModel):
    name: str
    grade_level: str
    academic_year: str = "2025-26"

class SubjectCreate(BaseModel):
    name: str
    class_id: str


class TimetableSlotCreate(BaseModel):
    class_id: str
    subject_id: str
    teacher_id: str
    day_of_week: int
    start_time: str
    end_time: str


class TimeSlotRef(BaseModel):
    day: int
    period: int


class TimeGrid(BaseModel):
    days_per_week: int
    periods_per_day: int
    day_start_time: str = "09:00"
    period_minutes: int = 45
    breaks: list[TimeSlotRef] = []


class TeacherAvailability(BaseModel):
    days: list[int] | None = None
    start_period: int | None = None
    end_period: int | None = None
    blocked_slots: list[TimeSlotRef] = []


class TeacherConstraint(BaseModel):
    id: str
    name: str | None = None
    max_periods_per_week: int = 25
    max_periods_per_day: int = 5
    availability: TeacherAvailability | None = None


class TimetableRequirement(BaseModel):
    class_id: str
    subject_id: str
    required_periods_per_week: int
    allowed_teachers: list[str] | None = None


class FixedLesson(BaseModel):
    class_id: str
    subject_id: str
    teacher_id: str
    day: int
    period: int


class TimetableRules(BaseModel):
    no_back_to_back_classes: bool = True
    no_back_to_back_teachers: bool = True


class TimetableGenerateRequest(BaseModel):
    time_grid: TimeGrid
    teachers: list[TeacherConstraint]
    requirements: list[TimetableRequirement]
    fixed_lessons: list[FixedLesson] = []
    rules: TimetableRules = TimetableRules()
    apply_to_db: bool = False
    max_nodes: int | None = None

@router.post("/classes")
async def create_class(data: ClassCreate, current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    return _create_admin_class_impl(
        db=db,
        tenant_id=current_user.tenant_id,
        actor_user_id=getattr(current_user, "id", None),
        name=data.name,
        grade_level=data.grade_level,
        academic_year=data.academic_year,
    )

@router.post("/subjects")
async def create_subject(data: SubjectCreate, current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    return _create_admin_subject_impl(
        db=db,
        tenant_id=current_user.tenant_id,
        actor_user_id=getattr(current_user, "id", None),
        name=data.name,
        class_id=data.class_id,
        parse_uuid_fn=_parse_uuid,
    )


# â”€â”€â”€ Reports â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@router.get("/timetable/{class_id}")
async def get_class_timetable(
    class_id: str,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    return _build_admin_timetable_response_impl(
        db=db,
        tenant_id=current_user.tenant_id,
        class_id=class_id,
        parse_uuid_fn=_parse_uuid,
    )


@router.post("/timetable")
async def create_timetable_slot(
    data: TimetableSlotCreate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    return _create_admin_timetable_slot_impl(
        db=db,
        tenant_id=current_user.tenant_id,
        actor_user_id=getattr(current_user, "id", None),
        class_id=data.class_id,
        subject_id=data.subject_id,
        teacher_id=data.teacher_id,
        day_of_week=data.day_of_week,
        start_time_raw=data.start_time,
        end_time_raw=data.end_time,
        parse_uuid_fn=_parse_uuid,
        parse_hhmm_fn=_parse_hhmm,
    )


@router.delete("/timetable/{slot_id}")
async def delete_timetable_slot(
    slot_id: str,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    return _delete_admin_timetable_slot_impl(
        db=db,
        tenant_id=current_user.tenant_id,
        actor_user_id=getattr(current_user, "id", None),
        slot_id=slot_id,
        parse_uuid_fn=_parse_uuid,
    )


@router.post("/timetable/generate")
async def generate_timetable_schedule(
    data: TimetableGenerateRequest,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    return _generate_admin_timetable_schedule_impl(
        db=db,
        tenant_id=current_user.tenant_id,
        actor_user_id=getattr(current_user, "id", None),
        data=data,
        parse_uuid_fn=_parse_uuid,
        parse_hhmm_fn=_parse_hhmm,
        generate_timetable_fn=generate_timetable,
    )


@router.get("/parent-links")
async def list_parent_links(current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    return _build_admin_parent_links_response_impl(
        db=db,
        tenant_id=current_user.tenant_id,
    )


@router.post("/parent-links")
async def create_parent_link(
    data: ParentLinkCreate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    return _create_admin_parent_link_impl(
        db=db,
        tenant_id=current_user.tenant_id,
        actor_user_id=getattr(current_user, "id", None),
        parent_id=data.parent_id,
        child_id=data.child_id,
        parse_uuid_fn=_parse_uuid,
    )


@router.delete("/parent-links/{link_id}")
async def delete_parent_link(
    link_id: str,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    return _delete_admin_parent_link_impl(
        db=db,
        tenant_id=current_user.tenant_id,
        actor_user_id=getattr(current_user, "id", None),
        link_id=link_id,
        parse_uuid_fn=_parse_uuid,
    )


@router.get("/reports/attendance")
async def attendance_report(current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    return _build_admin_attendance_report_impl(
        db=db,
        tenant_id=current_user.tenant_id,
    )

@router.get("/reports/performance")
async def performance_report(current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    return _build_admin_performance_report_impl(
        db=db,
        tenant_id=current_user.tenant_id,
    )

@router.get("/reports/ai-usage")
async def ai_usage_report(current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    return _build_admin_ai_usage_report_impl(
        db=db,
        tenant_id=current_user.tenant_id,
    )


# â”€â”€â”€ Security / Audit Logs â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@router.get("/security")
async def security_logs(current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    return _build_admin_security_logs_impl(
        db=db,
        tenant_id=current_user.tenant_id,
    )


# â”€â”€â”€ Billing â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@router.get("/billing")
async def billing_info(current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    return _build_admin_billing_info_impl(
        db=db,
        tenant_id=current_user.tenant_id,
    )


# â”€â”€â”€ Settings â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@router.get("/webhooks")
async def list_webhooks(current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    return _build_admin_webhooks_response_impl(
        db=db,
        tenant_id=current_user.tenant_id,
    )


@router.post("/webhooks")
async def create_webhook(
    data: WebhookCreate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    return _create_admin_webhook_impl(
        db=db,
        tenant_id=current_user.tenant_id,
        actor_user_id=getattr(current_user, "id", None),
        event_type=data.event_type,
        target_url=data.target_url,
        supported_webhook_events=SUPPORTED_WEBHOOK_EVENTS,
    )


@router.patch("/webhooks/{webhook_id}")
async def toggle_webhook(
    webhook_id: str,
    data: WebhookUpdate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    return _toggle_admin_webhook_impl(
        db=db,
        tenant_id=current_user.tenant_id,
        actor_user_id=getattr(current_user, "id", None),
        webhook_id=webhook_id,
        is_active=data.is_active,
        parse_uuid_fn=_parse_uuid,
    )


@router.get("/webhooks/{webhook_id}/deliveries")
async def list_webhook_deliveries(
    webhook_id: str,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    return _build_admin_webhook_deliveries_response_impl(
        db=db,
        tenant_id=current_user.tenant_id,
        webhook_id=webhook_id,
        parse_uuid_fn=_parse_uuid,
    )


@router.delete("/webhooks/{webhook_id}")
async def delete_webhook(
    webhook_id: str,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    return _delete_admin_webhook_impl(
        db=db,
        tenant_id=current_user.tenant_id,
        actor_user_id=getattr(current_user, "id", None),
        webhook_id=webhook_id,
        parse_uuid_fn=_parse_uuid,
    )


@router.get("/settings")
async def get_settings(current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    return _build_admin_settings_response_impl(
        db=db,
        tenant_id=current_user.tenant_id,
    )

class SettingsUpdate(BaseModel):
    ai_daily_limit: Optional[int] = None
    name: Optional[str] = None

@router.patch("/settings")
async def update_settings(data: SettingsUpdate, current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    return _update_admin_settings_impl(
        db=db,
        tenant_id=current_user.tenant_id,
        actor_user_id=getattr(current_user, "id", None),
        ai_daily_limit=data.ai_daily_limit,
        name=data.name,
    )


# â”€â”€â”€ Performance Heatmap â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@router.get("/heatmap")
async def performance_heatmap(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Performance heatmap: Subjects Ã— Classes, color-coded by avg score."""
    return _build_admin_performance_heatmap_impl(
        db=db,
        tenant_id=current_user.tenant_id,
    )


# â”€â”€â”€ CSV Export Endpoints â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@router.get("/export/attendance")
async def export_attendance_csv(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
    academic_year: str = "",
) -> StreamingResponse:
    payload = _build_admin_attendance_csv_export_impl(
        db=db,
        tenant_id=current_user.tenant_id,
    )
    return StreamingResponse(
        io.StringIO(payload["content"]),
        media_type=payload["media_type"],
        headers={"Content-Disposition": f"attachment; filename={payload['filename']}"},
    )


@router.get("/export/performance")
async def export_performance_csv(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    payload = _build_admin_performance_csv_export_impl(
        db=db,
        tenant_id=current_user.tenant_id,
    )
    return StreamingResponse(
        io.StringIO(payload["content"]),
        media_type=payload["media_type"],
        headers={"Content-Disposition": f"attachment; filename={payload['filename']}"},
    )


@router.get("/export/ai-usage")
async def export_ai_usage_csv(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    payload = _build_admin_ai_usage_csv_export_impl(
        db=db,
        tenant_id=current_user.tenant_id,
    )
    return StreamingResponse(
        io.StringIO(payload["content"]),
        media_type=payload["media_type"],
        headers={"Content-Disposition": f"attachment; filename={payload['filename']}"},
    )


# â”€â”€â”€ CSV Templates for Setup Wizard â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@router.get("/csv-template/{template_type}")
async def download_csv_template(
    template_type: str,
    current_user: User = Depends(require_role("admin")),
) -> StreamingResponse:
    """Download a pre-filled CSV template for bulk import."""
    payload = _build_admin_csv_template_payload_impl(template_type=template_type)
    return StreamingResponse(
        io.StringIO(payload["content"]),
        media_type=payload["media_type"],
        headers={"Content-Disposition": f"attachment; filename={payload['filename']}"},
    )


# â”€â”€â”€ Onboard Students via CSV â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@router.post("/onboard-students")
async def onboard_students(
    file: UploadFile = File(...),
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
    preview: bool = False,
):
    """Onboard students from CSV/TXT or OCR image. Columns: full_name, email, password, class_name"""
    safe_filename: str = file.filename or ""
    content: bytes = await file.read()
    return _process_student_onboarding_upload_impl(
        db=db,
        tenant_id=current_user.tenant_id,
        safe_filename=safe_filename,
        content=content,
        preview=preview,
        get_extension_fn=get_extension,
        extract_upload_content_result_fn=extract_upload_content_result,
        parse_student_import_rows_with_diagnostics_fn=parse_student_import_rows_with_diagnostics,
        hash_password_fn=hash_password,
    )


# â”€â”€â”€ QR Code Login Tokens â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class QrTokenBatchRequest(BaseModel):
    student_ids: list[str] | None = None
    class_id: str | None = None
    expires_in_days: int = 30
    regenerate: bool = False


@router.post("/generate-qr-tokens")
async def generate_qr_tokens(
    data: QrTokenBatchRequest | None = None,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Generate QR login tokens for students.
    Supports optional class filtering and token reuse when still valid."""
    payload: QrTokenBatchRequest = data or QrTokenBatchRequest()
    return _generate_admin_qr_tokens_impl(
        db=db,
        tenant_id=current_user.tenant_id,
        student_ids=payload.student_ids,
        class_id=payload.class_id,
        expires_in_days=payload.expires_in_days,
        regenerate=payload.regenerate,
        parse_uuid_fn=_parse_uuid,
    )


# â”€â”€â”€ Report Card PDF â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@router.get("/report-card/{student_id}")
async def download_report_card(
    student_id: str,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> StarletteResponse:
    payload = _build_admin_report_card_payload_impl(
        db=db,
        tenant_id=current_user.tenant_id,
        student_id=student_id,
        parse_uuid_fn=_parse_uuid,
        generate_report_card_pdf_fn=generate_report_card_pdf,
    )

    return StarletteResponse(
        content=payload["content"],
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={payload['filename']}"},
    )


# â”€â”€â”€ WhatsApp Bulk Digest â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class WhatsAppDigestRequest(BaseModel):
    phone_numbers: list[str] | None = None  # if None, send to all parents with phone numbers


@router.post("/whatsapp-digest")
async def send_whatsapp_digest_bulk(
    data: WhatsAppDigestRequest | None = None,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    return await _send_admin_whatsapp_digest_bulk_impl(
        db=db,
        tenant_id=current_user.tenant_id,
        phone_numbers=(data.phone_numbers if data else None),
        send_weekly_digest_fn=send_weekly_digest,
    )
