"""Elicitation question scheduling service."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from ..models.signals import ElicitationLog
from ..models.personality_profile import StudentPersonalityProfile


ELICITATION_QUESTIONS = [
    {
        "key": "learning_style_pref",
        "target_field": "learning_style_stated",
        "text": "Quick question — when you're studying, do you prefer: (a) reading notes, (b) watching/seeing diagrams, (c) doing practice problems, or (d) listening/discussing?",
        "min_interactions_before": 3,
    },
    {
        "key": "study_environment",
        "target_field": "peak_study_hour",
        "text": "When do you usually study? Morning, afternoon, evening, or late night?",
        "min_interactions_before": 2,
    },
    {
        "key": "career_aspiration",
        "target_field": "career_aspiration_text",
        "text": "One big question — where do you see yourself in 10 years? Just the first thing that comes to mind.",
        "min_interactions_before": 5,
    },
    {
        "key": "motivation_trigger",
        "target_field": "primary_motivation_driver",
        "text": "What makes you actually want to study — is it: (a) wanting to top the class, (b) genuine curiosity, (c) fear of failing, (d) rewards/goals, or (e) not wanting to disappoint family?",
        "min_interactions_before": 4,
    },
    {
        "key": "help_seeking",
        "target_field": "help_seeking_style",
        "text": "When you're stuck on a problem, what do you prefer — a small hint to figure it out yourself, the full solution explained, or a discussion-style walkthrough?",
        "min_interactions_before": 6,
    },
    {
        "key": "interest_tags",
        "target_field": "interest_tags",
        "text": "Totally off-topic — what are you actually into outside of studying? Sports, gaming, music, art? Pick your top 2.",
        "min_interactions_before": 3,
    },
    {
        "key": "social_orientation",
        "target_field": "social_orientation",
        "text": "Do you prefer studying solo, competing with classmates, or learning together with friends?",
        "min_interactions_before": 7,
    },
]


def get_next_elicitation(db: Session, student_id: UUID, tenant_id: UUID,
                          total_interactions: int,
                          profile: StudentPersonalityProfile) -> Optional[dict]:
    """
    Returns the next elicitation question to ask, or None if:
    - no question is due (min_interactions_before not met)
    - all questions have already been answered
    - a question was already asked this session

    Logic:
    1. Get all question keys already answered from elicitation_log for this student
    2. For each ELICITATION_QUESTIONS entry in order:
       - Skip if key already answered
       - Skip if total_interactions < min_interactions_before
       - Skip if target_field is already non-null in profile
       - Return the first eligible one
    3. Return None if none found
    """
    # Get answered questions
    answered_keys = set()
    logs = db.query(ElicitationLog.question_key).filter(
        ElicitationLog.student_id == student_id,
        ElicitationLog.tenant_id == tenant_id,
        ElicitationLog.answered_at.isnot(None)
    ).all()
    answered_keys = {log.question_key for log in logs}

    for question in ELICITATION_QUESTIONS:
        # Skip if already answered
        if question["key"] in answered_keys:
            continue

        # Skip if not enough interactions
        if total_interactions < question["min_interactions_before"]:
            continue

        # Skip if target field already filled
        target_field = question["target_field"]
        if getattr(profile, target_field) is not None:
            continue

        return question

    return None


def record_elicitation_asked(db: Session, student_id: UUID,
                              tenant_id: UUID, question: dict) -> ElicitationLog:
    """
    Create an ElicitationLog record for this question being asked.
    If record already exists (upsert on student_id + question_key),
    increment skipped_count instead.
    """
    existing = db.query(ElicitationLog).filter(
        ElicitationLog.student_id == student_id,
        ElicitationLog.tenant_id == tenant_id,
        ElicitationLog.question_key == question["key"]
    ).first()

    if existing:
        existing.skipped_count += 1
        db.commit()
        db.refresh(existing)
        return existing
    else:
        log = ElicitationLog(
            student_id=student_id,
            tenant_id=tenant_id,
            question_key=question["key"]
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log


def record_elicitation_answered(db: Session, student_id: UUID,
                                  question_key: str, response_text: str,
                                  response_time_ms: Optional[int] = None) -> None:
    """
    Update the ElicitationLog record to mark it answered.
    Set response_text, response_time_ms, answered_at=now.
    """
    from datetime import datetime, timezone

    db.query(ElicitationLog).filter(
        ElicitationLog.student_id == student_id,
        ElicitationLog.question_key == question_key
    ).update({
        "response_text": response_text,
        "response_time_ms": response_time_ms,
        "answered_at": datetime.now(timezone.utc)
    })
    db.commit()