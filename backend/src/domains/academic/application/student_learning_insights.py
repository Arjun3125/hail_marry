"""Application helpers for student timetable, uploads, and weak-topic insights."""

from __future__ import annotations

from sqlalchemy.orm import Session

from src.domains.academic.models.core import Enrollment, Subject
from src.domains.academic.models.performance import SubjectPerformance
from src.domains.academic.models.timetable import Timetable
from src.domains.identity.models.user import User
from src.domains.platform.models.document import Document
from src.domains.platform.models.topic_mastery import TopicMastery
from utils.pagination import paginate


def list_student_timetable(
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

    slots = (
        db.query(Timetable)
        .filter(
            Timetable.tenant_id == tenant_id,
            Timetable.class_id == enrollment.class_id,
        )
        .order_by(Timetable.day_of_week, Timetable.start_time)
        .all()
    )

    subject_ids = [slot.subject_id for slot in slots if slot.subject_id is not None]
    teacher_ids = [slot.teacher_id for slot in slots if slot.teacher_id is not None]
    subjects = (
        db.query(Subject)
        .filter(
            Subject.tenant_id == tenant_id,
            Subject.id.in_(subject_ids),
        )
        .all()
        if subject_ids
        else []
    )
    teachers = (
        db.query(User)
        .filter(
            User.tenant_id == tenant_id,
            User.id.in_(teacher_ids),
        )
        .all()
        if teacher_ids
        else []
    )
    subject_name_by_id = {subject.id: subject.name for subject in subjects}
    teacher_name_by_id = {teacher.id: teacher.full_name for teacher in teachers}

    return [
        {
            "day": slot.day_of_week,
            "start": slot.start_time.strftime("%H:%M"),
            "end": slot.end_time.strftime("%H:%M"),
            "subject": subject_name_by_id.get(slot.subject_id, "Unknown"),
            "teacher": teacher_name_by_id.get(slot.teacher_id, "Unknown"),
        }
        for slot in slots
    ]


def list_student_uploads(
    *,
    db: Session,
    tenant_id,
    student_id,
    page: int,
    page_size: int,
) -> dict[str, object]:
    query = (
        db.query(Document)
        .filter(
            Document.tenant_id == tenant_id,
            Document.uploaded_by == student_id,
        )
        .order_by(Document.created_at.desc())
    )
    result = paginate(query, page, page_size)

    return {
        "items": [
            {
                "id": str(document.id),
                "file_name": document.file_name,
                "file_type": document.file_type,
                "status": document.ingestion_status,
                "uploaded_at": str(document.created_at),
            }
            for document in result["items"]
        ],
        "total": result["total"],
        "page": result["page"],
        "total_pages": result["total_pages"],
    }


def build_student_weak_topics(
    *,
    db: Session,
    tenant_id,
    student_id,
) -> dict[str, object]:
    performances = (
        db.query(SubjectPerformance)
        .filter(
            SubjectPerformance.tenant_id == tenant_id,
            SubjectPerformance.student_id == student_id,
        )
        .all()
    )

    subject_ids = [performance.subject_id for performance in performances if performance.subject_id is not None]
    subjects = (
        db.query(Subject)
        .filter(
            Subject.tenant_id == tenant_id,
            Subject.id.in_(subject_ids),
        )
        .all()
        if subject_ids
        else []
    )
    subject_name_by_id = {subject.id: subject.name for subject in subjects}

    weak: list[dict[str, object]] = []
    strong: list[dict[str, object]] = []
    for performance in performances:
        entry = {
            "subject": subject_name_by_id.get(performance.subject_id, "Unknown"),
            "average_score": performance.average_score,
            "exam_count": 0,
            "is_weak": performance.average_score < 60,
        }
        if performance.average_score < 60:
            weak.append(entry)
        else:
            strong.append(entry)

    mastery_rows = (
        db.query(TopicMastery)
        .filter(
            TopicMastery.tenant_id == tenant_id,
            TopicMastery.user_id == student_id,
            TopicMastery.concept == "core",
            TopicMastery.mastery_score < 60,
        )
        .order_by(TopicMastery.mastery_score.asc(), TopicMastery.updated_at.desc())
        .limit(5)
        .all()
    )

    mastery_subject_ids = [row.subject_id for row in mastery_rows if row.subject_id is not None]
    mastery_subjects = (
        db.query(Subject)
        .filter(
            Subject.tenant_id == tenant_id,
            Subject.id.in_(mastery_subject_ids),
        )
        .all()
        if mastery_subject_ids
        else []
    )
    mastery_subject_name_by_id = {subject.id: subject.name for subject in mastery_subjects}

    mastery_topics = [
        {
            "topic": row.topic,
            "subject": mastery_subject_name_by_id.get(row.subject_id),
            "mastery_score": round(float(row.mastery_score), 1),
            "confidence_score": round(float(row.confidence_score), 2),
            "review_due_at": str(row.review_due_at) if row.review_due_at else None,
            "last_evidence_type": row.last_evidence_type,
        }
        for row in mastery_rows
    ]

    return {
        "weak_topics": sorted(weak, key=lambda item: item["average_score"]),
        "strong_topics": sorted(strong, key=lambda item: -item["average_score"]),
        "mastery_topics": mastery_topics,
        "recommended_focus_topics": [item["topic"] for item in mastery_topics[:3]],
        "total_subjects": len(performances),
        "weak_count": len(weak),
    }
