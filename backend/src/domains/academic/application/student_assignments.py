"""Application helpers for student assignment workflows."""

from __future__ import annotations

from sqlalchemy.orm import Session

from src.domains.academic.models.assignment import Assignment, AssignmentSubmission
from src.domains.academic.models.core import Enrollment, Subject


def list_student_assignments(
    *,
    db: Session,
    tenant_id,
    student_id,
) -> list[dict[str, object]]:
    enrollment = (
        db.query(Enrollment)
        .filter(
            Enrollment.tenant_id == tenant_id,
            Enrollment.student_id == student_id,
        )
        .first()
    )
    if not enrollment:
        return []

    subjects = (
        db.query(Subject)
        .filter(
            Subject.tenant_id == tenant_id,
            Subject.class_id == enrollment.class_id,
        )
        .all()
    )
    subject_ids = [subject.id for subject in subjects]
    subject_name_by_id = {subject.id: subject.name for subject in subjects}
    if not subject_ids:
        return []

    assignments = (
        db.query(Assignment)
        .filter(
            Assignment.tenant_id == tenant_id,
            Assignment.subject_id.in_(subject_ids),
        )
        .order_by(Assignment.due_date.desc())
        .all()
    )

    result: list[dict[str, object]] = []
    for assignment in assignments:
        submission = (
            db.query(AssignmentSubmission)
            .filter(
                AssignmentSubmission.assignment_id == assignment.id,
                AssignmentSubmission.student_id == student_id,
            )
            .first()
        )

        status = "pending"
        grade = None
        if submission:
            if submission.grade is not None:
                status = "graded"
                grade = submission.grade
            else:
                status = "submitted"

        result.append(
            {
                "id": str(assignment.id),
                "title": assignment.title,
                "subject": subject_name_by_id.get(assignment.subject_id, "Unknown"),
                "due": str(assignment.due_date.date()) if assignment.due_date else None,
                "status": status,
                "grade": grade,
                "has_submission": submission is not None,
                "submitted_at": str(submission.submitted_at) if submission and submission.submitted_at else None,
            }
        )

    return result
