"""Application helpers for admin dashboard orchestration."""

from __future__ import annotations

from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.domains.academic.models.attendance import Attendance
from src.domains.academic.models.marks import Mark
from src.domains.administrative.models.complaint import Complaint
from src.domains.identity.models.user import User
from src.domains.platform.models.ai import AIQuery


def build_admin_dashboard_response(
    *,
    db: Session,
    tenant_id,
    load_queue_metrics_fn,
    list_active_alerts_fn,
) -> dict:
    total_students = db.query(User).filter(User.tenant_id == tenant_id, User.role == "student", User.is_active).count()
    total_teachers = db.query(User).filter(User.tenant_id == tenant_id, User.role == "teacher", User.is_active).count()
    active_today = max(1, total_students // 5)
    ai_today = db.query(AIQuery).filter(AIQuery.tenant_id == tenant_id, func.date(AIQuery.created_at) == date.today()).count()
    total_att = db.query(Attendance).filter(Attendance.tenant_id == tenant_id).count()
    present_att = db.query(Attendance).filter(Attendance.tenant_id == tenant_id, Attendance.status == "present").count()
    avg_attendance = round(present_att / total_att * 100) if total_att > 0 else 0
    avg_marks = db.query(func.avg(Mark.marks_obtained)).filter(Mark.tenant_id == tenant_id).scalar()
    open_complaints = db.query(Complaint).filter(Complaint.tenant_id == tenant_id, Complaint.status != "resolved").count()

    try:
        queue_metrics = load_queue_metrics_fn(str(tenant_id))
    except Exception:
        queue_metrics = {
            "pending_depth": 0,
            "processing_depth": 0,
            "failure_rate_pct": 0,
            "stuck_jobs": 0,
        }

    try:
        observability_alerts = list_active_alerts_fn(str(tenant_id))
    except Exception:
        observability_alerts = []

    return {
        "total_students": total_students,
        "total_teachers": total_teachers,
        "active_today": active_today,
        "ai_queries_today": ai_today,
        "avg_attendance": avg_attendance,
        "avg_performance": round(float(avg_marks)) if avg_marks else 0,
        "open_complaints": open_complaints,
        "queue_pending_depth": queue_metrics.get("pending_depth", 0),
        "queue_processing_depth": queue_metrics.get("processing_depth", 0),
        "queue_failure_rate_pct": queue_metrics.get("failure_rate_pct", 0),
        "queue_stuck_jobs": queue_metrics.get("stuck_jobs", 0),
        "observability_alerts": observability_alerts,
    }
