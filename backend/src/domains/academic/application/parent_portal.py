"""Application helpers for parent-facing portal endpoints."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from typing import Any

from fastapi import HTTPException
from sqlalchemy import case, func


def get_child_for_parent(
    *,
    current_user,
    db,
    child_id: str | None,
    parent_link_model,
    user_model,
    parse_uuid_fn,
):
    links_query = db.query(parent_link_model).filter(
        parent_link_model.tenant_id == current_user.tenant_id,
        parent_link_model.parent_id == current_user.id,
    )

    if child_id:
        child_uuid = parse_uuid_fn(child_id, "child_id")
        links_query = links_query.filter(parent_link_model.child_id == child_uuid)

    link = links_query.order_by(parent_link_model.created_at.asc()).first()
    if not link:
        raise HTTPException(status_code=404, detail="No linked child found for this parent")

    child = (
        db.query(user_model)
        .filter(
            user_model.id == link.child_id,
            user_model.tenant_id == current_user.tenant_id,
            user_model.role == "student",
            user_model.is_active,
        )
        .first()
    )
    if not child:
        raise HTTPException(status_code=404, detail="Linked child not found")
    return child


def get_child_results(
    *,
    db,
    tenant_id,
    child_id,
    mark_model,
    exam_model,
    subject_model,
) -> list[dict[str, Any]]:
    marks = (
        db.query(mark_model, exam_model, subject_model.name)
        .join(exam_model, mark_model.exam_id == exam_model.id)
        .join(subject_model, exam_model.subject_id == subject_model.id)
        .filter(
            mark_model.tenant_id == tenant_id,
            mark_model.student_id == child_id,
        )
        .all()
    )

    subjects_map: dict[str, dict[str, Any]] = {}
    for mark, exam, subject_name in marks:
        subject_name = subject_name or "Unknown"
        if subject_name not in subjects_map:
            subjects_map[subject_name] = {
                "name": subject_name,
                "exams": [],
                "total": 0,
                "count": 0,
            }

        percentage = round(mark.marks_obtained / exam.max_marks * 100) if exam.max_marks else 0
        subjects_map[subject_name]["exams"].append(
            {
                "name": exam.name,
                "marks": mark.marks_obtained,
                "max": exam.max_marks,
            }
        )
        subjects_map[subject_name]["total"] += percentage
        subjects_map[subject_name]["count"] += 1

    result: list[dict[str, Any]] = []
    for item in subjects_map.values():
        item["avg"] = round(item["total"] / item["count"]) if item["count"] > 0 else 0
        del item["total"]
        del item["count"]
        result.append(item)
    return result


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


def _month_windows(now: datetime | None = None) -> list[dict[str, Any]]:
    current = _ensure_tz(now or datetime.now(UTC))
    assert current is not None
    first_of_month = current.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    windows: list[dict[str, Any]] = []
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


def _history_cutoff(now: datetime | None = None) -> datetime:
    current = _ensure_tz(now or datetime.now(UTC))
    assert current is not None
    return current - timedelta(days=183)


def _month_key(value: datetime | date | None) -> str | None:
    normalized = _ensure_tz(value)
    if normalized is None:
        return None
    return normalized.strftime("%Y-%m")


def _summarize_child_activity(
    *,
    db,
    tenant_id,
    child_id,
    assignment_submission_model,
    study_session_model,
    ai_query_model,
    generated_content_model,
) -> dict[str, Any]:
    cutoff = _history_cutoff()
    submissions = (
        db.query(assignment_submission_model)
        .filter(
            assignment_submission_model.tenant_id == tenant_id,
            assignment_submission_model.student_id == child_id,
            assignment_submission_model.submitted_at >= cutoff,
        )
        .all()
    )
    study_sessions = (
        db.query(study_session_model)
        .filter(
            study_session_model.tenant_id == tenant_id,
            study_session_model.user_id == child_id,
            study_session_model.created_at >= cutoff,
        )
        .all()
    )
    ai_queries = (
        db.query(ai_query_model)
        .filter(
            ai_query_model.tenant_id == tenant_id,
            ai_query_model.user_id == child_id,
            ai_query_model.created_at >= cutoff,
        )
        .all()
    )
    generated_items = (
        db.query(generated_content_model)
        .filter(
            generated_content_model.tenant_id == tenant_id,
            generated_content_model.user_id == child_id,
            generated_content_model.created_at >= cutoff,
        )
        .order_by(generated_content_model.created_at.desc())
        .all()
    )

    return {
        "assignments_submitted": len(submissions),
        "study_sessions": len(study_sessions),
        "ai_requests": len(ai_queries),
        "generated_tools": len(generated_items),
        "latest_milestones": {
            "last_assignment_submitted_at": str(max((item.submitted_at for item in submissions), default=None) or "") or None,
            "last_study_session_at": str(max((item.last_active_at or item.updated_at or item.created_at for item in study_sessions), default=None) or "") or None,
            "last_ai_request_at": str(max((item.created_at for item in ai_queries), default=None) or "") or None,
            "last_generated_tool_at": str(max((item.created_at for item in generated_items), default=None) or "") or None,
        },
        "recent_generated_tools": [
            {
                "id": str(item.id),
                "type": item.type,
                "title": item.title or item.type.replace("_", " ").title(),
                "created_at": str(item.created_at),
            }
            for item in generated_items[:5]
        ],
    }


def _attendance_windows(records: list[Any]) -> list[dict[str, Any]]:
    windows = _month_windows()
    buckets = {
        window["key"]: {
            "month": window["month"],
            "present": 0,
            "absent": 0,
            "late": 0,
            "attendance_pct": 0,
            "marked_days": 0,
        }
        for window in windows
    }
    for record in records:
        month_key = _month_key(record.date)
        if month_key not in buckets:
            continue
        bucket = buckets[month_key]
        status = (record.status or "").lower()
        if status == "present":
            bucket["present"] += 1
        elif status == "absent":
            bucket["absent"] += 1
        else:
            bucket["late"] += 1
        bucket["marked_days"] += 1

    result = []
    for window in windows:
        bucket = buckets[window["key"]]
        marked_days = bucket["marked_days"]
        bucket["attendance_pct"] = round((bucket["present"] / marked_days * 100) if marked_days else 0)
        result.append(bucket)
    return result


def _performance_windows(mark_rows: list[tuple[Any, Any, Any]]) -> list[dict[str, Any]]:
    windows = _month_windows()
    buckets = {
        window["key"]: {
            "month": window["month"],
            "average_pct": 0,
            "exams_recorded": 0,
            "_scores": [],
        }
        for window in windows
    }
    for mark, exam, _subject_name in mark_rows:
        month_key = _month_key(exam.exam_date or exam.created_at or mark.created_at)
        if month_key not in buckets:
            continue
        percentage = round(mark.marks_obtained / exam.max_marks * 100) if exam.max_marks else 0
        bucket = buckets[month_key]
        bucket["exams_recorded"] += 1
        bucket["_scores"].append(percentage)
    result = []
    for window in windows:
        bucket = buckets[window["key"]]
        scores = bucket.pop("_scores")
        bucket["average_pct"] = round(sum(scores) / len(scores)) if scores else 0
        result.append(bucket)
    return result


def _assignment_windows(rows: list[Any]) -> list[dict[str, Any]]:
    windows = _month_windows()
    buckets = {
        window["key"]: {
            "month": window["month"],
            "assignments_submitted": 0,
        }
        for window in windows
    }
    for row in rows:
        month_key = _month_key(row.submitted_at)
        if month_key in buckets:
            buckets[month_key]["assignments_submitted"] += 1
    return [buckets[window["key"]] for window in windows]


def get_latest_mark(
    *,
    db,
    tenant_id,
    child_id,
    mark_model,
    exam_model,
    subject_model,
) -> dict[str, Any] | None:
    mark_row = (
        db.query(mark_model, exam_model, subject_model.name)
        .join(exam_model, mark_model.exam_id == exam_model.id)
        .join(subject_model, exam_model.subject_id == subject_model.id)
        .filter(
            mark_model.tenant_id == tenant_id,
            mark_model.student_id == child_id,
        )
        .order_by(
            exam_model.exam_date.desc().nullslast(),
            exam_model.created_at.desc(),
        )
        .first()
    )
    if not mark_row:
        return None
    mark, exam, subject_name = mark_row
    percentage = round(mark.marks_obtained / exam.max_marks * 100) if exam.max_marks else 0
    return {
        "subject": subject_name or "Unknown",
        "exam": exam.name,
        "percentage": percentage,
        "marks": mark.marks_obtained,
        "max_marks": exam.max_marks,
        "date": str(exam.exam_date or exam.created_at.date() if exam.created_at else None),
    }


def get_next_class(
    *,
    db,
    tenant_id,
    class_id,
    timetable_model,
    subject_model,
) -> dict[str, Any] | None:
    now = datetime.now()
    start_day = now.weekday()
    current_time = now.time()

    for offset in range(0, 7):
        day = (start_day + offset) % 7
        query = db.query(timetable_model).filter(
            timetable_model.tenant_id == tenant_id,
            timetable_model.class_id == class_id,
            timetable_model.day_of_week == day,
        )
        if offset == 0:
            query = query.filter(timetable_model.start_time > current_time)
        slot = query.order_by(timetable_model.start_time.asc()).first()
        if slot:
            subject = (
                db.query(subject_model)
                .filter(
                    subject_model.id == slot.subject_id,
                    subject_model.tenant_id == tenant_id,
                )
                .first()
            )
            return {
                "day": slot.day_of_week,
                "start_time": slot.start_time.strftime("%H:%M"),
                "end_time": slot.end_time.strftime("%H:%M"),
                "subject": subject.name if subject else "Unknown",
            }
    return None


def build_parent_dashboard_response(
    *,
    db,
    current_user,
    child,
    enrollment_model,
    class_model,
    subject_model,
    attendance_model,
    mark_model,
    exam_model,
    assignment_model,
    assignment_submission_model,
    timetable_model,
    study_session_model,
    ai_query_model,
    generated_content_model,
) -> dict[str, Any]:
    cutoff = _history_cutoff()
    attendance_counts = (
        db.query(
            func.count(attendance_model.student_id),
            func.sum(case((attendance_model.status == "present", 1), else_=0)),
        )
        .filter(
            attendance_model.tenant_id == current_user.tenant_id,
            attendance_model.student_id == child.id,
        )
        .first()
    )
    total_att = int((attendance_counts[0] if attendance_counts else 0) or 0)
    present_att = int((attendance_counts[1] if attendance_counts else 0) or 0)
    attendance_pct = round((present_att / total_att * 100) if total_att > 0 else 0)

    avg_marks_row = (
        db.query(func.avg(mark_model.marks_obtained))
        .filter(
            mark_model.tenant_id == current_user.tenant_id,
            mark_model.student_id == child.id,
        )
        .scalar()
    )
    avg_marks = round(float(avg_marks_row)) if avg_marks_row else 0

    enrollment = (
        db.query(enrollment_model)
        .filter(
            enrollment_model.tenant_id == current_user.tenant_id,
            enrollment_model.student_id == child.id,
        )
        .first()
    )
    class_name = None
    pending_assignments = 0
    if enrollment:
        cls = (
            db.query(class_model)
            .filter(
                class_model.id == enrollment.class_id,
                class_model.tenant_id == current_user.tenant_id,
            )
            .first()
        )
        class_name = cls.name if cls else None

        subject_ids = [
            subject.id
            for subject in db.query(subject_model)
            .filter(
                subject_model.tenant_id == current_user.tenant_id,
                subject_model.class_id == enrollment.class_id,
            )
            .all()
        ]
        total_assignments = (
            db.query(assignment_model)
            .filter(
                assignment_model.tenant_id == current_user.tenant_id,
                assignment_model.subject_id.in_(subject_ids),
            )
            .count()
        )
        submitted = (
            db.query(assignment_submission_model)
            .filter(
                assignment_submission_model.tenant_id == current_user.tenant_id,
                assignment_submission_model.student_id == child.id,
            )
            .count()
        )
        pending_assignments = max(0, total_assignments - submitted)

    latest_mark = get_latest_mark(
        db=db,
        tenant_id=current_user.tenant_id,
        child_id=child.id,
        mark_model=mark_model,
        exam_model=exam_model,
        subject_model=subject_model,
    )
    next_class = (
        get_next_class(
            db=db,
            tenant_id=current_user.tenant_id,
            class_id=enrollment.class_id,
            timetable_model=timetable_model,
            subject_model=subject_model,
        )
        if enrollment
        else None
    )

    attendance_records = (
        db.query(attendance_model)
        .filter(
            attendance_model.tenant_id == current_user.tenant_id,
            attendance_model.student_id == child.id,
            attendance_model.date >= cutoff.date(),
        )
        .order_by(attendance_model.date.desc())
        .all()
    )
    recent_marks = (
        db.query(mark_model, exam_model, subject_model.name)
        .join(exam_model, mark_model.exam_id == exam_model.id)
        .join(subject_model, exam_model.subject_id == subject_model.id)
        .filter(
            mark_model.tenant_id == current_user.tenant_id,
            mark_model.student_id == child.id,
            func.coalesce(exam_model.exam_date, func.date(exam_model.created_at)) >= cutoff.date(),
        )
        .order_by(exam_model.exam_date.desc().nullslast(), exam_model.created_at.desc())
        .all()
    )
    recent_submissions = (
        db.query(assignment_submission_model)
        .filter(
            assignment_submission_model.tenant_id == current_user.tenant_id,
            assignment_submission_model.student_id == child.id,
            assignment_submission_model.submitted_at >= cutoff,
        )
        .all()
    )
    activity_summary = _summarize_child_activity(
        db=db,
        tenant_id=current_user.tenant_id,
        child_id=child.id,
        assignment_submission_model=assignment_submission_model,
        study_session_model=study_session_model,
        ai_query_model=ai_query_model,
        generated_content_model=generated_content_model,
    )

    return {
        "child": {
            "id": str(child.id),
            "name": child.full_name,
            "email": child.email,
            "class": class_name,
        },
        "attendance_pct": attendance_pct,
        "avg_marks": avg_marks,
        "pending_assignments": pending_assignments,
        "latest_mark": latest_mark,
        "next_class": next_class,
        "summary": activity_summary,
        "monthly_attendance": _attendance_windows(attendance_records),
        "monthly_performance": _performance_windows(recent_marks),
        "monthly_assignments": _assignment_windows(recent_submissions),
    }


def build_parent_attendance_response(
    *,
    db,
    current_user,
    child,
    attendance_model,
) -> dict[str, Any]:
    cutoff = _history_cutoff()
    records = (
        db.query(attendance_model)
        .filter(
            attendance_model.tenant_id == current_user.tenant_id,
            attendance_model.student_id == child.id,
            attendance_model.date >= cutoff.date(),
        )
        .order_by(attendance_model.date.desc())
        .all()
    )
    items = [
        {
            "date": str(record.date),
            "day": record.date.strftime("%a"),
            "status": record.status,
        }
        for record in records
    ]
    present = sum(1 for record in records if (record.status or "").lower() == "present")
    absent = sum(1 for record in records if (record.status or "").lower() == "absent")
    late = sum(1 for record in records if (record.status or "").lower() not in {"present", "absent"})
    return {
        "items": items[:60],
        "summary": {
            "present": present,
            "absent": absent,
            "late": late,
            "marked_days": len(records),
            "attendance_pct": round((present / len(records) * 100) if records else 0),
        },
        "monthly_activity": _attendance_windows(records),
    }


def build_parent_reports_response(
    *,
    db,
    current_user,
    child,
    attendance_model,
    mark_model,
    exam_model,
    subject_model,
    assignment_submission_model,
    study_session_model,
    ai_query_model,
    generated_content_model,
) -> dict[str, Any]:
    cutoff = _history_cutoff()
    results = get_child_results(
        db=db,
        tenant_id=current_user.tenant_id,
        child_id=child.id,
        mark_model=mark_model,
        exam_model=exam_model,
        subject_model=subject_model,
    )
    attendance = (
        db.query(attendance_model)
        .filter(
            attendance_model.tenant_id == current_user.tenant_id,
            attendance_model.student_id == child.id,
        )
        .order_by(attendance_model.date.desc())
        .limit(30)
        .all()
    )

    total_att = len(attendance)
    present_att = len([item for item in attendance if item.status == "present"])
    attendance_pct = round((present_att / total_att * 100) if total_att > 0 else 0)
    weak_subjects = [result["name"] for result in results if result.get("avg", 0) < 60]
    recent_marks = (
        db.query(mark_model, exam_model, subject_model.name)
        .join(exam_model, mark_model.exam_id == exam_model.id)
        .join(subject_model, exam_model.subject_id == subject_model.id)
        .filter(
            mark_model.tenant_id == current_user.tenant_id,
            mark_model.student_id == child.id,
            func.coalesce(exam_model.exam_date, func.date(exam_model.created_at)) >= cutoff.date(),
        )
        .order_by(exam_model.exam_date.desc().nullslast(), exam_model.created_at.desc())
        .all()
    )
    recent_submissions = (
        db.query(assignment_submission_model)
        .filter(
            assignment_submission_model.tenant_id == current_user.tenant_id,
            assignment_submission_model.student_id == child.id,
            assignment_submission_model.submitted_at >= cutoff,
        )
        .all()
    )
    activity_summary = _summarize_child_activity(
        db=db,
        tenant_id=current_user.tenant_id,
        child_id=child.id,
        assignment_submission_model=assignment_submission_model,
        study_session_model=study_session_model,
        ai_query_model=ai_query_model,
        generated_content_model=generated_content_model,
    )
    monthly_attendance = _attendance_windows(
        db.query(attendance_model)
        .filter(
            attendance_model.tenant_id == current_user.tenant_id,
            attendance_model.student_id == child.id,
            attendance_model.date >= cutoff.date(),
        )
        .order_by(attendance_model.date.desc())
        .all()
    )
    monthly_performance = _performance_windows(recent_marks)
    monthly_assignments = _assignment_windows(recent_submissions)
    average_marks_6m = round(
        sum(item["average_pct"] for item in monthly_performance if item["exams_recorded"] > 0)
        / max(1, len([item for item in monthly_performance if item["exams_recorded"] > 0]))
    ) if any(item["exams_recorded"] > 0 for item in monthly_performance) else 0

    return {
        "child": {
            "id": str(child.id),
            "name": child.full_name,
        },
        "attendance_pct_30d": attendance_pct,
        "results": results,
        "weak_subjects": weak_subjects,
        "summary": (
            "Needs attention in weak subjects."
            if weak_subjects
            else "Overall progress is stable."
        ),
        "six_month_overview": {
            "attendance_pct": round(
                sum(item["attendance_pct"] for item in monthly_attendance if item["marked_days"] > 0)
                / max(1, len([item for item in monthly_attendance if item["marked_days"] > 0]))
            ) if any(item["marked_days"] > 0 for item in monthly_attendance) else 0,
            "average_marks": average_marks_6m,
            "assignments_submitted": activity_summary["assignments_submitted"],
            "study_sessions": activity_summary["study_sessions"],
            "ai_requests": activity_summary["ai_requests"],
            "generated_tools": activity_summary["generated_tools"],
        },
        "monthly_snapshots": [
            {
                "month": attendance_bucket["month"],
                "attendance_pct": attendance_bucket["attendance_pct"],
                "average_marks": performance_bucket["average_pct"],
                "assignments_submitted": assignment_bucket["assignments_submitted"],
            }
            for attendance_bucket, performance_bucket, assignment_bucket in zip(
                monthly_attendance,
                monthly_performance,
                monthly_assignments,
            )
        ],
        "recent_generated_tools": activity_summary["recent_generated_tools"],
    }


def build_parent_results_response(
    *,
    db,
    current_user,
    child,
    mark_model,
    exam_model,
    subject_model,
) -> dict[str, Any]:
    cutoff = _history_cutoff()
    items = get_child_results(
        db=db,
        tenant_id=current_user.tenant_id,
        child_id=child.id,
        mark_model=mark_model,
        exam_model=exam_model,
        subject_model=subject_model,
    )
    recent_marks = (
        db.query(mark_model, exam_model, subject_model.name)
        .join(exam_model, mark_model.exam_id == exam_model.id)
        .join(subject_model, exam_model.subject_id == subject_model.id)
        .filter(
            mark_model.tenant_id == current_user.tenant_id,
            mark_model.student_id == child.id,
            func.coalesce(exam_model.exam_date, func.date(exam_model.created_at)) >= cutoff.date(),
        )
        .order_by(exam_model.exam_date.desc().nullslast(), exam_model.created_at.desc())
        .all()
    )
    strongest = max(items, key=lambda item: item.get("avg", 0), default=None)
    average = round(sum(item.get("avg", 0) for item in items) / len(items)) if items else 0
    recent_exams = []
    for mark, exam, subject_name in recent_marks[:6]:
        percentage = round(mark.marks_obtained / exam.max_marks * 100) if exam.max_marks else 0
        recent_exams.append(
            {
                "subject": subject_name or "Unknown",
                "exam": exam.name,
                "percentage": percentage,
                "date": str(exam.exam_date or exam.created_at.date() if exam.created_at else None),
            }
        )
    return {
        "items": items,
        "summary": {
            "subjects": len(items),
            "average": average,
            "strongest": strongest["name"] if strongest else None,
            "exams_recorded": sum(len(item.get("exams", [])) for item in items),
        },
        "monthly_trend": _performance_windows(recent_marks),
        "recent_exams": recent_exams,
    }


def build_parent_audio_report_response(
    *,
    db,
    current_user,
    child,
    attendance_model,
    mark_model,
    exam_model,
    subject_model,
) -> dict[str, Any]:
    results = get_child_results(
        db=db,
        tenant_id=current_user.tenant_id,
        child_id=child.id,
        mark_model=mark_model,
        exam_model=exam_model,
        subject_model=subject_model,
    )
    attendance_counts = (
        db.query(
            func.count(attendance_model.student_id),
            func.sum(case((attendance_model.status == "present", 1), else_=0)),
        )
        .filter(
            attendance_model.tenant_id == current_user.tenant_id,
            attendance_model.student_id == child.id,
        )
        .first()
    )
    total_att = int((attendance_counts[0] if attendance_counts else 0) or 0)
    present_att = int((attendance_counts[1] if attendance_counts else 0) or 0)
    attendance_pct = round((present_att / total_att * 100) if total_att > 0 else 0)

    parts = [f"Progress report for {child.full_name}."]
    parts.append(f"Attendance is at {attendance_pct} percent.")

    if results:
        subject_summaries = []
        weak = []
        for result in results:
            avg = result.get("avg", 0)
            name = result.get("name", "Unknown")
            subject_summaries.append(f"{name}: {avg} percent average")
            if avg < 60:
                weak.append(name)
        parts.append("Subject performance: " + ", ".join(subject_summaries) + ".")
        if weak:
            parts.append(f"Attention needed in: {', '.join(weak)}.")
        else:
            parts.append("All subjects are performing well.")
    else:
        parts.append("No exam results available yet.")

    if attendance_pct < 75:
        parts.append("Attendance is below 75 percent. Please ensure regular attendance.")

    text = " ".join(parts)

    return {
        "child_name": child.full_name,
        "text": text,
        "attendance_pct": attendance_pct,
        "subject_count": len(results),
    }


def build_parent_digest_preview_response(
    *,
    db,
    current_user,
    generate_digest_fn,
    render_digest_html_fn,
) -> dict[str, Any]:
    digest = generate_digest_fn(
        db,
        parent_id=current_user.id,
        tenant_id=current_user.tenant_id,
    )
    return {
        "digest": digest,
        "html_preview": render_digest_html_fn(digest),
    }


def build_parent_report_card_payload(
    *,
    db,
    current_user,
    parent_link_model,
    tenant_model,
    generate_report_card_pdf_fn,
) -> tuple[bytes, str]:
    link = (
        db.query(parent_link_model)
        .filter(
            parent_link_model.tenant_id == current_user.tenant_id,
            parent_link_model.parent_id == current_user.id,
        )
        .first()
    )
    if not link:
        raise HTTPException(status_code=404, detail="No linked child found")

    tenant = db.query(tenant_model).filter(tenant_model.id == current_user.tenant_id).first()
    school_name = tenant.name if tenant and hasattr(tenant, "name") else "VidyaOS School"

    try:
        pdf_bytes = generate_report_card_pdf_fn(
            db,
            student_id=str(link.child_id),
            tenant_id=str(current_user.tenant_id),
            school_name=school_name,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return pdf_bytes, "report_card.pdf"
