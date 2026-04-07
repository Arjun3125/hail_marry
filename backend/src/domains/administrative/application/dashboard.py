"""Application helpers for admin dashboard orchestration."""

from __future__ import annotations

from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.domains.academic.models.attendance import Attendance
from src.domains.academic.models.core import Class
from src.domains.academic.models.marks import Mark
from src.domains.academic.models.student_profile import StudentProfile
from src.domains.administrative.models.complaint import Complaint
from src.domains.identity.models.user import User
from src.domains.platform.models.ai import AIQuery


def _risk_level_value(level: str | None) -> int:
    return {"low": 0, "medium": 1, "high": 2}.get((level or "low").lower(), 0)


def _build_student_risk_payload(*, db: Session, tenant_id) -> tuple[dict, list[dict]]:
    rows = (
        db.query(StudentProfile, User.full_name, User.email, Class.name)
        .outerjoin(User, User.id == StudentProfile.user_id)
        .outerjoin(Class, Class.id == StudentProfile.current_class_id)
        .filter(StudentProfile.tenant_id == tenant_id)
        .all()
    )

    summary = {
        "high_risk_students": 0,
        "medium_risk_students": 0,
        "academic_high_risk": 0,
        "fee_high_risk": 0,
        "dropout_high_risk": 0,
    }
    alerts: list[dict] = []

    for profile, full_name, email, class_name in rows:
        risk_values = {
            "dropout_risk": profile.dropout_risk or "low",
            "academic_risk": profile.academic_risk or "low",
            "fee_risk": profile.fee_risk or "low",
        }
        max_risk = max(_risk_level_value(value) for value in risk_values.values())
        if max_risk >= 2:
            summary["high_risk_students"] += 1
        elif max_risk == 1:
            summary["medium_risk_students"] += 1

        if risk_values["academic_risk"] == "high":
            summary["academic_high_risk"] += 1
        if risk_values["fee_risk"] == "high":
            summary["fee_high_risk"] += 1
        if risk_values["dropout_risk"] == "high":
            summary["dropout_high_risk"] += 1

        if max_risk == 0:
            continue

        alerts.append(
            {
                "student_id": str(profile.user_id),
                "student_name": full_name or email or "Unknown student",
                "class_name": class_name or "Unassigned",
                "dropout_risk": risk_values["dropout_risk"],
                "academic_risk": risk_values["academic_risk"],
                "fee_risk": risk_values["fee_risk"],
                "attendance_pct": round(float(profile.attendance_pct or 0.0), 2),
                "overall_score_pct": round(float(profile.overall_score_pct), 2) if profile.overall_score_pct is not None else None,
            }
        )

    alerts.sort(
        key=lambda row: (
            -max(
                _risk_level_value(row["dropout_risk"]),
                _risk_level_value(row["academic_risk"]),
                _risk_level_value(row["fee_risk"]),
            ),
            -sum(
                1
                for key in ("dropout_risk", "academic_risk", "fee_risk")
                if _risk_level_value(row[key]) == 2
            ),
            row["attendance_pct"],
            row["overall_score_pct"] if row["overall_score_pct"] is not None else 101.0,
            row["student_name"],
        )
    )
    return summary, alerts[:5]


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
    student_risk_summary, student_risk_alerts = _build_student_risk_payload(
        db=db,
        tenant_id=tenant_id,
    )

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
        "student_risk_summary": student_risk_summary,
        "student_risk_alerts": student_risk_alerts,
    }
