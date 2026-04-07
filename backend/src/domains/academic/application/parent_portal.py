"""Application helpers for parent-facing portal endpoints."""

from __future__ import annotations

from datetime import datetime
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
) -> dict[str, Any]:
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
    }


def build_parent_attendance_response(
    *,
    db,
    current_user,
    child,
    attendance_model,
) -> list[dict[str, Any]]:
    records = (
        db.query(attendance_model)
        .filter(
            attendance_model.tenant_id == current_user.tenant_id,
            attendance_model.student_id == child.id,
        )
        .order_by(attendance_model.date.desc())
        .limit(60)
        .all()
    )
    return [
        {
            "date": str(record.date),
            "day": record.date.strftime("%a"),
            "status": record.status,
        }
        for record in records
    ]


def build_parent_reports_response(
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
