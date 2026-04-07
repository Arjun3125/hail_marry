"""Application helpers for student timetable, uploads, and learning insights."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from src.domains.academic.models.core import Enrollment, Subject
from src.domains.academic.models.performance import SubjectPerformance
from src.domains.academic.models.student_profile import StudentProfile
from src.domains.academic.models.timetable import Timetable
from src.domains.identity.models.user import User
from src.domains.platform.models.document import Document
from src.domains.platform.models.topic_mastery import TopicMastery
from src.domains.platform.services.mastery_tracking_service import get_topic_mastery_snapshot
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


def _risk_rank(level: str | None) -> int:
    mapping = {"low": 0, "medium": 1, "high": 2}
    return mapping.get((level or "low").lower(), 0)


def _safe_datetime_iso(value) -> str | None:
    if value is None:
        return None
    if getattr(value, "tzinfo", None) is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.isoformat()


def build_student_mastery_map(
    *,
    db: Session,
    tenant_id,
    student_id,
) -> dict[str, object]:
    profile = (
        db.query(StudentProfile)
        .filter(
            StudentProfile.tenant_id == tenant_id,
            StudentProfile.user_id == student_id,
        )
        .first()
    )

    mastery_rows = (
        db.query(TopicMastery)
        .filter(
            TopicMastery.tenant_id == tenant_id,
            TopicMastery.user_id == student_id,
            TopicMastery.concept == "core",
        )
        .order_by(TopicMastery.mastery_score.asc(), TopicMastery.updated_at.desc())
        .all()
    )

    subject_ids = [row.subject_id for row in mastery_rows if row.subject_id is not None]
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

    subject_scores: dict[str, list[float]] = {}
    focus_topics: list[dict[str, object]] = []
    now = datetime.now(timezone.utc)
    due_review_count = 0
    low_mastery_count = 0

    for row in mastery_rows:
        subject_name = subject_name_by_id.get(row.subject_id, "General")
        subject_scores.setdefault(subject_name, []).append(float(row.mastery_score or 0.0))
        if float(row.mastery_score or 0.0) < 60.0:
            low_mastery_count += 1
        if row.review_due_at is not None:
            review_due_at = row.review_due_at
            if getattr(review_due_at, "tzinfo", None) is None:
                review_due_at = review_due_at.replace(tzinfo=timezone.utc)
            if review_due_at <= now:
                due_review_count += 1

        snapshot = get_topic_mastery_snapshot(
            db,
            tenant_id=tenant_id,
            user_id=student_id,
            topic=row.topic,
            subject_id=row.subject_id,
        )
        concepts = sorted(
            list(snapshot.get("concepts", [])),
            key=lambda item: (float(item.get("mastery_score") or 0.0), str(item.get("concept") or "")),
        )
        focus_topics.append(
            {
                "topic": row.topic,
                "subject": subject_name,
                "mastery_score": round(float(row.mastery_score or 0.0), 1),
                "confidence_score": round(float(row.confidence_score or 0.0), 2),
                "review_due_at": _safe_datetime_iso(row.review_due_at),
                "last_evidence_type": row.last_evidence_type,
                "last_evidence_score": row.last_evidence_score,
                "updated_at": _safe_datetime_iso(row.updated_at),
                "concepts": concepts,
            }
        )

    subject_mastery = [
        {
            "subject": subject_name,
            "score": round(sum(scores) / len(scores), 1),
            "fullMark": 100,
        }
        for subject_name, scores in sorted(subject_scores.items())
    ]
    if not subject_mastery and profile and profile.subject_mastery_map:
        subject_mastery = [
            {
                "subject": subject_name,
                "score": round(float(score or 0.0), 1),
                "fullMark": 100,
            }
            for subject_name, score in sorted((profile.subject_mastery_map or {}).items())
        ]

    risk_summary = {
        "dropout_risk": (profile.dropout_risk if profile else "low") or "low",
        "academic_risk": (profile.academic_risk if profile else "low") or "low",
        "fee_risk": (profile.fee_risk if profile else "low") or "low",
    }
    highest_risk = max(risk_summary.values(), key=_risk_rank) if risk_summary else "low"

    strongest_topic = None
    weakest_topic = None
    if focus_topics:
        strongest_topic = max(focus_topics, key=lambda item: float(item["mastery_score"]))
        weakest_topic = min(focus_topics, key=lambda item: float(item["mastery_score"]))

    summary = {
        "attendance_pct": round(float(profile.attendance_pct or 0.0), 2) if profile else 0.0,
        "absent_streak": int(profile.absent_streak or 0) if profile else 0,
        "overall_score_pct": round(float(profile.overall_score_pct or 0.0), 2) if profile and profile.overall_score_pct is not None else None,
        "exam_readiness_pct": round(float(profile.exam_readiness_pct or 0.0), 2) if profile and profile.exam_readiness_pct is not None else None,
        "current_streak_days": int(profile.current_streak_days or 0) if profile else 0,
        "total_reviews_completed": int(profile.total_reviews_completed or 0) if profile else 0,
        "last_review_at": _safe_datetime_iso(profile.last_review_at) if profile else None,
        "strongest_subject": profile.strongest_subject if profile else None,
        "weakest_subject": profile.weakest_subject if profile else None,
        "highest_risk": highest_risk,
        **risk_summary,
    }

    return {
        "summary": summary,
        "subject_mastery": subject_mastery,
        "focus_topics": focus_topics[:6],
        "insights": {
            "tracked_topics": len(focus_topics),
            "low_mastery_topics": low_mastery_count,
            "due_reviews": due_review_count,
            "strongest_topic": strongest_topic["topic"] if strongest_topic else None,
            "weakest_topic": weakest_topic["topic"] if weakest_topic else None,
        },
        "recommended_actions": [
            item["topic"]
            for item in focus_topics
            if float(item["mastery_score"]) < 60.0
        ][:3],
    }
