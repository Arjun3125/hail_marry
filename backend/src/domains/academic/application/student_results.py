"""Application helpers for student attendance and result workflows."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from src.domains.academic.models.attendance import Attendance
from src.domains.academic.models.core import Subject
from src.domains.academic.models.marks import Exam, Mark


def list_student_attendance(
    *,
    db: Session,
    tenant_id,
    student_id,
    limit: int = 30,
) -> list[dict[str, str]]:
    records = (
        db.query(Attendance)
        .filter(
            Attendance.tenant_id == tenant_id,
            Attendance.student_id == student_id,
        )
        .order_by(Attendance.date.desc())
        .limit(limit)
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


def build_student_results(
    *,
    db: Session,
    tenant_id,
    student_id,
) -> list[dict[str, Any]]:
    marks = (
        db.query(Mark, Exam)
        .join(Exam, Mark.exam_id == Exam.id)
        .filter(
            Mark.tenant_id == tenant_id,
            Mark.student_id == student_id,
        )
        .all()
    )

    subject_ids = list({exam.subject_id for _, exam in marks})
    subject_name_by_id: dict[UUID, str] = {}
    if subject_ids:
        subjects = (
            db.query(Subject)
            .filter(
                Subject.tenant_id == tenant_id,
                Subject.id.in_(subject_ids),
            )
            .all()
        )
        subject_name_by_id = {subject.id: subject.name for subject in subjects}

    subjects_map: dict[str, dict[str, Any]] = {}
    for mark, exam in marks:
        subject_name = subject_name_by_id.get(exam.subject_id, "Unknown")
        subject_entry = subjects_map.setdefault(
            subject_name,
            {"name": subject_name, "exams": [], "total": 0, "count": 0},
        )
        percentage = round(mark.marks_obtained / exam.max_marks * 100) if exam.max_marks > 0 else 0
        subject_entry["exams"].append(
            {
                "name": exam.name,
                "marks": mark.marks_obtained,
                "max": exam.max_marks,
            }
        )
        subject_entry["total"] += percentage
        subject_entry["count"] += 1

    results: list[dict[str, Any]] = []
    for subject_entry in subjects_map.values():
        subject_entry["avg"] = round(subject_entry["total"] / subject_entry["count"]) if subject_entry["count"] > 0 else 0
        del subject_entry["total"]
        del subject_entry["count"]
        results.append(subject_entry)

    return results


def build_student_result_trends(
    *,
    db: Session,
    tenant_id,
    student_id,
) -> list[dict[str, Any]]:
    marks = (
        db.query(Mark, Exam)
        .join(Exam, Mark.exam_id == Exam.id)
        .filter(
            Mark.tenant_id == tenant_id,
            Mark.student_id == student_id,
        )
        .all()
    )

    subject_ids = list({exam.subject_id for _, exam in marks})
    subject_name_by_id: dict[UUID, str] = {}
    if subject_ids:
        subjects = (
            db.query(Subject)
            .filter(
                Subject.tenant_id == tenant_id,
                Subject.id.in_(subject_ids),
            )
            .all()
        )
        subject_name_by_id = {subject.id: subject.name for subject in subjects}

    trends_by_subject: dict[str, list[dict[str, Any]]] = {}
    for mark, exam in marks:
        subject_name = subject_name_by_id.get(exam.subject_id, "Unknown")
        date_value = exam.exam_date or (exam.created_at.date() if exam.created_at else None)
        percentage = round(mark.marks_obtained / exam.max_marks * 100) if exam.max_marks > 0 else 0
        trends_by_subject.setdefault(subject_name, []).append(
            {
                "exam": exam.name,
                "date": str(date_value) if date_value else None,
                "marks": mark.marks_obtained,
                "max": exam.max_marks,
                "percentage": percentage,
            }
        )

    response: list[dict[str, Any]] = []
    for subject_name, points in trends_by_subject.items():
        points.sort(key=lambda point: (point.get("date") or "9999-99-99", point.get("exam") or ""))
        average = round(sum(point["percentage"] for point in points) / len(points)) if points else 0
        response.append({"subject": subject_name, "average": average, "points": points})

    response.sort(key=lambda item: item["subject"])
    return response
