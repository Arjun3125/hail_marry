"""Application helpers for teacher coursework and classroom operations."""

from __future__ import annotations

from datetime import datetime
from typing import Any


def build_class_attendance_response(
    *,
    db,
    current_user,
    class_uuid,
    attendance_model,
    user_model,
) -> list[dict[str, Any]]:
    records = (
        db.query(attendance_model)
        .filter(
            attendance_model.tenant_id == current_user.tenant_id,
            attendance_model.class_id == class_uuid,
        )
        .order_by(attendance_model.date.desc())
        .limit(100)
        .all()
    )

    student_ids = list({record.student_id for record in records})
    users = []
    if student_ids:
        users = (
            db.query(user_model)
            .filter(
                user_model.tenant_id == current_user.tenant_id,
                user_model.id.in_(student_ids),
            )
            .all()
        )
    student_name_by_id = {user.id: user.full_name for user in users}

    return [
        {
            "student_id": str(record.student_id),
            "student_name": student_name_by_id.get(record.student_id, "Unknown"),
            "date": str(record.date),
            "status": record.status,
        }
        for record in records
    ]


def build_created_exam_response(
    *,
    db,
    current_user,
    name: str,
    subject_id,
    max_marks: int,
    exam_date_raw: str | None,
    exam_model,
) -> dict[str, Any]:
    if max_marks <= 0:
        raise ValueError("max_marks must be greater than 0")

    exam_date = None
    if exam_date_raw:
        try:
            exam_date = datetime.strptime(exam_date_raw, "%Y-%m-%d").date()
        except ValueError as exc:
            raise ValueError("Invalid exam_date. Expected YYYY-MM-DD.") from exc

    exam = exam_model(
        tenant_id=current_user.tenant_id,
        name=name,
        subject_id=subject_id,
        max_marks=max_marks,
        exam_date=exam_date,
    )
    db.add(exam)
    db.commit()
    db.refresh(exam)
    return {"success": True, "exam_id": str(exam.id), "name": exam.name}


def build_teacher_assignments_response(
    *,
    db,
    current_user,
    assignment_model,
    subject_model,
    assignment_submission_model,
) -> list[dict[str, Any]]:
    assignments = (
        db.query(assignment_model)
        .filter(
            assignment_model.tenant_id == current_user.tenant_id,
            assignment_model.created_by == current_user.id,
        )
        .order_by(assignment_model.created_at.desc())
        .all()
    )
    subject_ids = list({assignment.subject_id for assignment in assignments})
    subjects = []
    if subject_ids:
        subjects = (
            db.query(subject_model)
            .filter(
                subject_model.tenant_id == current_user.tenant_id,
                subject_model.id.in_(subject_ids),
            )
            .all()
        )
    subject_name_by_id = {subject.id: subject.name for subject in subjects}

    return [
        {
            "id": str(assignment.id),
            "title": assignment.title,
            "subject": subject_name_by_id.get(assignment.subject_id, "Unknown"),
            "due_date": str(assignment.due_date.date()) if assignment.due_date else None,
            "submissions": (
                db.query(assignment_submission_model)
                .filter(
                    assignment_submission_model.tenant_id == current_user.tenant_id,
                    assignment_submission_model.assignment_id == assignment.id,
                )
                .count()
            ),
        }
        for assignment in assignments
    ]


def build_created_assignment_response(
    *,
    db,
    current_user,
    subject_id,
    title: str,
    description: str,
    due_date_raw: str | None,
    assignment_model,
) -> dict[str, Any]:
    due_date = None
    if due_date_raw:
        try:
            due_date = datetime.strptime(due_date_raw, "%Y-%m-%d")
        except ValueError as exc:
            raise ValueError("Invalid due_date. Expected YYYY-MM-DD.") from exc

    assignment = assignment_model(
        tenant_id=current_user.tenant_id,
        subject_id=subject_id,
        title=title,
        description=description,
        due_date=due_date,
        created_by=current_user.id,
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return {"success": True, "assignment_id": str(assignment.id)}
