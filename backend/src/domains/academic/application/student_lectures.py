"""Application helpers for student lecture workflows."""

from __future__ import annotations

from sqlalchemy.orm import Session

from src.domains.academic.models.core import Enrollment, Subject
from src.domains.academic.models.lecture import Lecture


def list_student_lectures(
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

    lectures = (
        db.query(Lecture)
        .filter(
            Lecture.tenant_id == tenant_id,
            Lecture.subject_id.in_(subject_ids),
        )
        .all()
    )

    return [
        {
            "title": lecture.title,
            "subject": subject_name_by_id.get(lecture.subject_id, "Unknown"),
            "youtube_url": lecture.youtube_url,
            "has_transcript": lecture.transcript_ingested,
        }
        for lecture in lectures
    ]
