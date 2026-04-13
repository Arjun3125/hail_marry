"""Context assembler service for building mascot conversation context."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from dataclasses import dataclass
from sqlalchemy.orm import Session

from src.domains.academic.models.student_profile import StudentProfile
from src.domains.platform.models.engagement import LoginStreak
from src.domains.platform.models.spaced_repetition import ReviewSchedule

from ..models.mascot_memory import StudentMascotMemory
from ..services.memory_manager import get_days_since_last_interaction
from ..services.profile_manager import get_or_create_profile

logger = logging.getLogger(__name__)


@dataclass
class MascotContext:
    """Complete context snapshot for mascot conversations."""

    student_name: str
    student_id: str
    tenant_id: str

    # Academic snapshot
    overall_score_pct: Optional[float] = None
    strongest_subject: Optional[str] = None
    weakest_subject: Optional[str] = None
    subject_mastery_map: Optional[dict] = None
    current_streak_days: int = 0
    dropout_risk: str = "unknown"
    academic_risk: str = "unknown"
    exam_readiness_pct: Optional[float] = None

    # Mascot memory
    last_summary: Optional[str] = None
    total_interactions: int = 0
    preferred_explanation_style: Optional[str] = None
    mascot_tone_setting: str = "encouraging"
    last_emotional_state: Optional[str] = None
    days_since_last_interaction: Optional[int] = None

    # Personality
    learning_style_detected: Optional[str] = None
    primary_motivation_driver: Optional[str] = None
    self_esteem_score: Optional[float] = None
    resilience_score: Optional[float] = None
    career_aspiration_text: Optional[str] = None
    interest_tags: Optional[list] = None
    social_orientation: Optional[str] = None
    profile_completeness_score: float = 0.0

    # Upcoming reviews
    topics_due_for_review: list = None

    def to_prompt_context(self) -> str:
        """
        Render this context as a compact string for injection into
        the mascot system prompt. Max ~400 tokens.
        Use this format:

        STUDENT: {student_name} | Streak: {current_streak_days} days
        ACADEMIC: Overall {overall_score_pct}% | Weakest: {weakest_subject} | Strongest: {strongest_subject}
        RISK: Academic={academic_risk} | Dropout={dropout_risk}
        PERSONALITY: Style={learning_style_detected} | Motivation={primary_motivation_driver} | Tone={mascot_tone_setting}
        LAST SESSION: {last_summary or 'First session'}
        DAYS SINCE LAST: {days_since_last_interaction or 'Never'}
        ASPIRATION: {career_aspiration_text or 'Not mentioned yet'}
        INTERESTS: {', '.join(interest_tags) if interest_tags else 'Not known yet'}
        DUE FOR REVIEW: {', '.join(topics_due_for_review[:3]) if topics_due_for_review else 'None'}
        """
        if self.topics_due_for_review is None:
            self.topics_due_for_review = []

        return "\n".join([
            f"STUDENT: {self.student_name} | Streak: {self.current_streak_days} days",
            f"ACADEMIC: Overall {self.overall_score_pct or 'Unknown'}% | Weakest: {self.weakest_subject or 'Unknown'} | Strongest: {self.strongest_subject or 'Unknown'}",
            f"RISK: Academic={self.academic_risk} | Dropout={self.dropout_risk}",
            f"PERSONALITY: Style={self.learning_style_detected or 'Unknown'} | Motivation={self.primary_motivation_driver or 'Unknown'} | Tone={self.mascot_tone_setting}",
            f"LAST SESSION: {self.last_summary or 'First session'}",
            f"DAYS SINCE LAST: {self.days_since_last_interaction or 'Never'}",
            f"ASPIRATION: {self.career_aspiration_text or 'Not mentioned yet'}",
            f"INTERESTS: {', '.join(self.interest_tags) if self.interest_tags else 'Not known yet'}",
            f"DUE FOR REVIEW: {', '.join(self.topics_due_for_review[:3]) if self.topics_due_for_review else 'None'}"
        ])


def assemble_context(db: Session, student_id: UUID,
                     tenant_id: UUID, student_name: str) -> MascotContext:
    """
    Query all relevant tables and build a MascotContext.
    If any table lookup fails, use safe defaults (never raise).
    Use try/except per query so one failure doesn't block the whole assembly.
    """
    context = MascotContext(
        student_name=student_name,
        student_id=str(student_id),
        tenant_id=str(tenant_id)
    )

    # Academic snapshot
    try:
        student_profile = db.query(StudentProfile).filter(
            StudentProfile.user_id == student_id,
            StudentProfile.tenant_id == tenant_id
        ).first()
        if student_profile:
            context.overall_score_pct = student_profile.overall_score_pct
            context.strongest_subject = student_profile.strongest_subject
            context.weakest_subject = student_profile.weakest_subject
            context.dropout_risk = student_profile.dropout_risk or "unknown"
            context.academic_risk = student_profile.academic_risk or "unknown"
            context.exam_readiness_pct = student_profile.exam_readiness_pct
            # subject_mastery_map would need additional processing
    except Exception as e:
        logger.warning(f"Failed to load academic profile for student {student_id}: {e}")

    # Current streak
    try:
        streak = db.query(LoginStreak).filter(
            LoginStreak.user_id == student_id,
            LoginStreak.tenant_id == tenant_id
        ).first()
        if streak:
            context.current_streak_days = streak.current_streak_days
    except Exception as e:
        logger.warning(f"Failed to load streak for student {student_id}: {e}")

    # Upcoming reviews
    try:
        # Get topics due for review (simplified - would need actual spaced repetition logic)
        due_reviews = db.query(ReviewSchedule).filter(
            ReviewSchedule.user_id == student_id,
            ReviewSchedule.tenant_id == tenant_id,
            ReviewSchedule.next_review_date <= datetime.now(timezone.utc)
        ).limit(5).all()
        context.topics_due_for_review = [r.topic_name for r in due_reviews if r.topic_name]
    except Exception as e:
        logger.warning(f"Failed to load review schedule for student {student_id}: {e}")

    # Mascot memory
    try:
        memory = db.query(StudentMascotMemory).filter(
            StudentMascotMemory.student_id == student_id,
            StudentMascotMemory.tenant_id == tenant_id
        ).first()
        if memory:
            context.last_summary = memory.last_summary
            context.total_interactions = memory.total_interactions
            context.preferred_explanation_style = memory.preferred_explanation_style
            context.mascot_tone_setting = memory.mascot_tone_setting or "encouraging"
            context.last_emotional_state = memory.last_emotional_state
            context.days_since_last_interaction = get_days_since_last_interaction(db, student_id, tenant_id)
    except Exception as e:
        logger.warning(f"Failed to load mascot memory for student {student_id}: {e}")

    # Personality profile
    try:
        profile = get_or_create_profile(db, student_id, tenant_id)
        context.learning_style_detected = profile.learning_style_detected
        context.primary_motivation_driver = profile.primary_motivation_driver
        context.self_esteem_score = profile.self_esteem_score
        context.resilience_score = profile.resilience_score
        context.career_aspiration_text = profile.career_aspiration_text
        context.interest_tags = profile.interest_tags
        context.social_orientation = profile.social_orientation
        context.profile_completeness_score = profile.profile_completeness_score
    except Exception as e:
        logger.warning(f"Failed to load personality profile for student {student_id}: {e}")

    return context
