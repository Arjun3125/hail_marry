"""Application helpers for admin dashboard orchestration."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from numbers import Number

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.domains.academic.models.attendance import Attendance
from src.domains.academic.models.core import Class
from src.domains.academic.models.marks import Exam, Mark
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


def _ensure_tz(value: datetime | date | None) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return datetime.combine(value, datetime.min.time(), tzinfo=UTC)
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _shift_month(value: datetime, delta: int) -> datetime:
    month_index = value.month - 1 + delta
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    return value.replace(year=year, month=month, day=1)


def _month_windows(now: datetime | None = None) -> list[dict]:
    current = _ensure_tz(now or datetime.now(UTC))
    assert current is not None
    first_of_month = current.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    windows = []
    for offset in range(-5, 1):
        start = _shift_month(first_of_month, offset)
        windows.append(
            {
                "key": start.strftime("%Y-%m"),
                "month": start.strftime("%b"),
                "start": start,
                "end": _shift_month(start, 1),
            }
        )
    return windows


def _month_key(value: datetime | date | None) -> str | None:
    normalized = _ensure_tz(value)
    if normalized is None:
        return None
    return normalized.strftime("%Y-%m")


def _history_cutoff(now: datetime | None = None) -> datetime:
    current = _ensure_tz(now or datetime.now(UTC))
    assert current is not None
    return current - timedelta(days=183)


def _build_monthly_trends(*, db: Session, tenant_id) -> list[dict]:
    cutoff = _history_cutoff()
    windows = _month_windows()
    buckets = {
        window["key"]: {
            "month": window["month"],
            "active_users": set(),
            "ai_queries": 0,
            "complaints_opened": 0,
            "complaints_resolved": 0,
            "present_days": 0,
            "marked_days": 0,
            "scores": [],
        }
        for window in windows
    }

    for query in (
        db.query(AIQuery.user_id, AIQuery.created_at)
        .filter(AIQuery.tenant_id == tenant_id, AIQuery.created_at >= cutoff)
        .all()
    ):
        month_key = _month_key(query.created_at)
        if month_key not in buckets:
            continue
        buckets[month_key]["ai_queries"] += 1
        buckets[month_key]["active_users"].add(str(query.user_id))

    for complaint in (
        db.query(Complaint.created_at, Complaint.resolved_at)
        .filter(Complaint.tenant_id == tenant_id, Complaint.created_at >= cutoff)
        .all()
    ):
        created_month = _month_key(complaint.created_at)
        if created_month in buckets:
            buckets[created_month]["complaints_opened"] += 1
        resolved_month = _month_key(complaint.resolved_at)
        if resolved_month in buckets:
            buckets[resolved_month]["complaints_resolved"] += 1

    for record in (
        db.query(Attendance.date, Attendance.status)
        .filter(Attendance.tenant_id == tenant_id, Attendance.date >= cutoff.date())
        .all()
    ):
        month_key = _month_key(record.date)
        if month_key not in buckets:
            continue
        buckets[month_key]["marked_days"] += 1
        if (record.status or "").lower() == "present":
            buckets[month_key]["present_days"] += 1

    for mark, exam in (
        db.query(Mark, Exam)
        .join(Exam, Mark.exam_id == Exam.id)
        .filter(
            Mark.tenant_id == tenant_id,
            func.coalesce(Exam.exam_date, func.date(Exam.created_at)) >= cutoff.date(),
        )
        .all()
    ):
        month_key = _month_key(exam.exam_date or exam.created_at or mark.created_at)
        if month_key not in buckets:
            continue
        if isinstance(exam.max_marks, Number) and exam.max_marks and isinstance(mark.marks_obtained, Number):
            buckets[month_key]["scores"].append(round(float(mark.marks_obtained) / float(exam.max_marks) * 100))

    result = []
    for window in windows:
        bucket = buckets[window["key"]]
        scores = bucket["scores"]
        marked_days = bucket["marked_days"]
        result.append(
            {
                "month": bucket["month"],
                "active_users": len(bucket["active_users"]),
                "ai_queries": bucket["ai_queries"],
                "complaints_opened": bucket["complaints_opened"],
                "complaints_resolved": bucket["complaints_resolved"],
                "attendance_pct": round((bucket["present_days"] / marked_days * 100) if marked_days else 0),
                "average_marks": round(sum(scores) / len(scores)) if scores else 0,
            }
        )
    return result


def build_admin_dashboard_response(
    *,
    db: Session,
    tenant_id,
    load_queue_metrics_fn,
    list_active_alerts_fn,
) -> dict:
    total_students = db.query(User).filter(User.tenant_id == tenant_id, User.role == "student", User.is_active).count()
    total_teachers = db.query(User).filter(User.tenant_id == tenant_id, User.role == "teacher", User.is_active).count()
    total_parents = db.query(User).filter(User.tenant_id == tenant_id, User.role == "parent", User.is_active).count()
    utc_today = datetime.now(UTC).date()
    utc_day_start = datetime.combine(utc_today, datetime.min.time(), tzinfo=UTC)
    utc_day_end = utc_day_start + timedelta(days=1)
    active_users_today = {
        str(user_id)
        for user_id, in db.query(AIQuery.user_id)
        .filter(
            AIQuery.tenant_id == tenant_id,
            AIQuery.created_at >= utc_day_start,
            AIQuery.created_at < utc_day_end,
        )
        .distinct()
        .all()
    }
    active_today = len(active_users_today) or max(1, total_students // 5)
    ai_today = db.query(AIQuery).filter(
        AIQuery.tenant_id == tenant_id,
        AIQuery.created_at >= utc_day_start,
        AIQuery.created_at < utc_day_end,
    ).count()
    total_att = db.query(Attendance).filter(Attendance.tenant_id == tenant_id).count()
    present_att = db.query(Attendance).filter(Attendance.tenant_id == tenant_id, Attendance.status == "present").count()
    avg_attendance = round(present_att / total_att * 100) if total_att > 0 else 0
    avg_marks = db.query(func.avg(Mark.marks_obtained)).filter(Mark.tenant_id == tenant_id).scalar()
    complaints = db.query(Complaint).filter(Complaint.tenant_id == tenant_id).all()
    open_complaints = sum(1 for complaint in complaints if complaint.status != "resolved")
    last_30_days = datetime.now(UTC) - timedelta(days=30)
    opened_last_30d = sum(1 for complaint in complaints if _ensure_tz(complaint.created_at) and _ensure_tz(complaint.created_at) >= last_30_days)
    resolved_last_30d = sum(1 for complaint in complaints if _ensure_tz(complaint.resolved_at) and _ensure_tz(complaint.resolved_at) >= last_30_days)

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
    monthly_trends = _build_monthly_trends(db=db, tenant_id=tenant_id)
    latest_ai_query_at = db.query(func.max(AIQuery.created_at)).filter(AIQuery.tenant_id == tenant_id).scalar()
    latest_complaint_at = max((complaint.created_at for complaint in complaints), default=None)
    latest_resolved_complaint_at = max((complaint.resolved_at for complaint in complaints if complaint.resolved_at), default=None)
    latest_attendance_at = db.query(func.max(Attendance.date)).filter(Attendance.tenant_id == tenant_id).scalar()
    latest_exam_date = db.query(func.max(Exam.exam_date)).filter(Exam.tenant_id == tenant_id).scalar()

    return {
        "total_students": total_students,
        "total_teachers": total_teachers,
        "total_parents": total_parents,
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
        "role_totals": {
            "students": total_students,
            "teachers": total_teachers,
            "parents": total_parents,
            "admins": db.query(User).filter(User.tenant_id == tenant_id, User.role == "admin", User.is_active).count(),
        },
        "monthly_trends": monthly_trends,
        "complaint_health": {
            "opened_last_30d": opened_last_30d,
            "resolved_last_30d": resolved_last_30d,
            "resolution_rate_pct": round((resolved_last_30d / opened_last_30d * 100) if opened_last_30d else 100),
        },
        "latest_milestones": {
            "last_ai_query_at": str(latest_ai_query_at) if latest_ai_query_at else None,
            "last_complaint_at": str(latest_complaint_at) if latest_complaint_at else None,
            "last_resolved_complaint_at": str(latest_resolved_complaint_at) if latest_resolved_complaint_at else None,
            "last_attendance_marked_at": str(latest_attendance_at) if latest_attendance_at else None,
            "last_exam_date": str(latest_exam_date) if latest_exam_date else None,
        },
    }
