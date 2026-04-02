"""Application helpers for student quiz-result mastery ingestion."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID


@dataclass
class StudentQuizResultError(Exception):
    status_code: int
    detail: str


def process_student_quiz_result(
    *,
    db,
    tenant_id,
    student_id,
    topic: str,
    total_questions: int,
    correct_answers: int,
    subject_id: str | None,
    difficulty_breakdown: dict[str, int] | None,
    get_topic_mastery_snapshot_fn,
    record_quiz_completion_fn,
    record_mastery_outcome_fn,
) -> dict[str, Any]:
    normalized_topic = (topic or "").strip()
    if not normalized_topic:
        raise StudentQuizResultError(400, "topic is required")
    if total_questions <= 0:
        raise StudentQuizResultError(400, "total_questions must be greater than zero")
    if correct_answers < 0 or correct_answers > total_questions:
        raise StudentQuizResultError(
            400,
            "correct_answers must be between 0 and total_questions",
        )

    normalized_breakdown = difficulty_breakdown or {}
    for key, value in normalized_breakdown.items():
        if key not in {"easy", "medium", "hard"} or value < 0:
            raise StudentQuizResultError(
                400,
                "difficulty_breakdown must only contain easy, medium, hard with non-negative counts",
            )

    subject_uuid = None
    if subject_id:
        try:
            subject_uuid = UUID(str(subject_id))
        except (TypeError, ValueError):
            raise StudentQuizResultError(400, "Invalid subject_id")

    before_snapshot = get_topic_mastery_snapshot_fn(
        db,
        tenant_id=tenant_id,
        user_id=student_id,
        topic=normalized_topic,
        subject_id=subject_uuid,
    )
    record_quiz_completion_fn(
        db,
        tenant_id=tenant_id,
        user_id=student_id,
        topic=normalized_topic,
        total_questions=total_questions,
        correct_answers=correct_answers,
        subject_id=subject_uuid,
        difficulty_breakdown=normalized_breakdown,
    )
    db.commit()

    after_snapshot = get_topic_mastery_snapshot_fn(
        db,
        tenant_id=tenant_id,
        user_id=student_id,
        topic=normalized_topic,
        subject_id=subject_uuid,
    )
    record_mastery_outcome_fn(
        topic=normalized_topic,
        before_snapshot=before_snapshot,
        after_snapshot=after_snapshot,
    )

    return {
        "success": True,
        "topic": normalized_topic,
        "accuracy": round((correct_answers / total_questions) * 100.0, 1),
        "mastery": after_snapshot,
    }
