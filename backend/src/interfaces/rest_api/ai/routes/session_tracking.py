"""AI session tracking routes for student learning activity."""
from uuid import UUID
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Any, Dict, cast
import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy import desc, and_
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from constants import JSON_ARRAY_MAX_ITEMS, SECONDS_PER_HOUR
from database import get_db
from src.domains.identity.models.user import User
from src.domains.platform.models.ai import AISessionEvent

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ai/sessions", tags=["AI Sessions"])


# ============================================================================
# Pydantic Schemas
# ============================================================================

class AISessionEventCreate(BaseModel):
    """Create a new AI session event."""
    session_id: str
    tool_mode: str
    subject: Optional[str] = None
    topic: Optional[str] = None
    queries_count: int = 0
    total_duration_seconds: int = 0
    engagement_score: float = 0.0
    key_concepts: Optional[str] = None
    misconceptions: Optional[str] = None
    mastery_level: str = "beginner"
    confidence_change: float = 0.0
    was_quiz_attempted: bool = False
    quiz_score_percent: Optional[float] = None
    flashcard_correct_count: int = 0
    flashcard_total_shown: int = 0

    class Config:
        schema_extra: Dict[str, Any] = {
            "example": {
                "session_id": "sess_abc123def456",
                "tool_mode": "quiz",
                "subject": "Physics",
                "topic": "Thermodynamics - Laws of Motion",
                "queries_count": 5,
                "total_duration_seconds": 1800,
                "engagement_score": 82.5,
                "key_concepts": '["Newton\'s First Law", "Friction", "Acceleration"]',
                "misconceptions": '["Force equals mass only", "Gravity acts downward only"]',
                "mastery_level": "intermediate",
                "confidence_change": 15.0,
                "was_quiz_attempted": True,
                "quiz_score_percent": 78.5,
            }
        }


class AISessionEventUpdate(BaseModel):
    """Update session event fields (for session end) with proper type validation."""
    ended_at: datetime
    total_duration_seconds: Optional[int] = None
    engagement_score: Optional[float] = None
    key_concepts: Optional[str] = None  # JSON string or None
    misconceptions: Optional[str] = None  # JSON string or None
    mastery_level: Optional[str] = None
    confidence_change: Optional[float] = None
    was_quiz_attempted: Optional[bool] = None
    quiz_score_percent: Optional[float] = None
    flashcard_correct_count: Optional[int] = None
    flashcard_total_shown: Optional[int] = None

    # ─── Generic range validators (eliminate duplication) ───
    def _validate_range(self, value: Optional[float], min_val: float, max_val: float, field_name: str) -> Optional[float]:
        """Reusable validator for numeric ranges."""
        if value is not None:
            if not min_val <= value <= max_val:
                raise ValueError(f"{field_name} must be between {min_val} and {max_val}")
            return float(value)
        return None

    def _validate_non_negative_int(self, value: Optional[int], field_name: str) -> Optional[int]:
        """Reusable validator for non-negative integers."""
        if value is not None:
            if value < 0:
                raise ValueError(f"{field_name} must be non-negative")
        return value

    @field_validator("total_duration_seconds")
    @classmethod
    def validate_duration(cls, v: Optional[int]) -> Optional[int]:
        """Ensure duration is non-negative."""
        if v is not None and v < 0:
            raise ValueError("total_duration_seconds must be non-negative")
        return v

    @field_validator("engagement_score")
    @classmethod
    def validate_engagement_score(cls, v: Optional[float]) -> Optional[float]:
        """Ensure engagement score is between 0-100."""
        if v is not None:
            if not 0 <= v <= 100:
                raise ValueError("engagement_score must be between 0 and 100")
            return float(v)
        return None

    @field_validator("confidence_change")
    @classmethod
    def validate_confidence_change(cls, v: Optional[float]) -> Optional[float]:
        """Ensure confidence change is between -100 and +100."""
        if v is not None:
            if not -100 <= v <= 100:
                raise ValueError("confidence_change must be between -100 and +100")
            return float(v)
        return None

    @field_validator("quiz_score_percent")
    @classmethod
    def validate_quiz_score(cls, v: Optional[float]) -> Optional[float]:
        """Ensure quiz score is between 0-100."""
        if v is not None:
            if not 0 <= v <= 100:
                raise ValueError("quiz_score_percent must be between 0 and 100")
            return float(v)
        return None

    @field_validator("flashcard_correct_count", "flashcard_total_shown")
    @classmethod
    def validate_flashcard_counts(cls, v: Optional[int]) -> Optional[int]:
        """Ensure flashcard counts are non-negative integers."""
        if v is not None:
            if v < 0:
                raise ValueError("Flashcard counts must be non-negative")
        return v

    @field_validator("key_concepts", "misconceptions")
    @classmethod
    def validate_json_fields(cls, v: Optional[str]) -> Optional[str]:
        """Validate that JSON fields are valid JSON strings."""
        if v is not None:
            try:
                # Verify it's valid JSON
                parsed = json.loads(v)
                # Ensure it's a list (as database stores JSON arrays)
                if not isinstance(parsed, list):
                    raise ValueError("JSON field must represent an array")
                # Prevent extremely large arrays (enforced constraint)
                parsed_list = cast(List[Any], parsed)
                if len(parsed_list) > JSON_ARRAY_MAX_ITEMS:
                    raise ValueError(f"JSON array cannot have more than {JSON_ARRAY_MAX_ITEMS} items")
                # Prevent duplicates in concepts/misconceptions
                if len(parsed_list) != len(set(parsed_list)):
                    raise ValueError("JSON array contains duplicate items")
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON: {str(e)}")
        return v


class AISessionEventResponse(BaseModel):
    """Response schema for session event."""
    id: UUID
    session_id: str
    tool_mode: str
    subject: Optional[str]
    topic: Optional[str]
    queries_count: int
    total_duration_seconds: int
    engagement_score: float
    mastery_level: str
    confidence_change: float
    was_quiz_attempted: bool
    quiz_score_percent: Optional[float]
    started_at: datetime
    ended_at: Optional[datetime]

    class Config:
        from_attributes = True


class AISessionSummary(BaseModel):
    """Summary of session activity for dashboard display."""
    session_id: str
    tool_mode: str
    subject: Optional[str]
    topic: Optional[str]
    duration_seconds: int
    engagement_score: float
    mastery_level: str
    quiz_score_percent: Optional[float]
    started_at: datetime
    ended_at: Optional[datetime]
    key_insights: List[str]  # Derived from key_concepts + misconceptions


class ParentInsightsSummary(BaseModel):
    """Parent-facing summary of child's AI learning activity."""
    total_sessions: int
    total_study_time_hours: float
    active_subjects: List[str]
    average_engagement: float
    recent_topics: List[str]
    quiz_attempts: int
    average_quiz_score: Optional[float]
    mastery_progress: Dict[str, str]  # {subject: mastery_level}
    recommended_topics: List[str]  # Topics showing misconceptions


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/", response_model=AISessionEventResponse)
async def create_session_event(
    event: AISessionEventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new AI session event.
    Called when student starts an AI Studio session.
    """
    session_event = AISessionEvent(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        session_id=event.session_id,
        tool_mode=event.tool_mode,
        subject=event.subject,
        topic=event.topic,
        queries_count=event.queries_count,
        total_duration_seconds=event.total_duration_seconds,
        engagement_score=event.engagement_score,
        key_concepts=event.key_concepts,
        misconceptions=event.misconceptions,
        mastery_level=event.mastery_level,
        confidence_change=event.confidence_change,
        was_quiz_attempted=event.was_quiz_attempted,
        quiz_score_percent=event.quiz_score_percent,
        flashcard_correct_count=event.flashcard_correct_count,
        flashcard_total_shown=event.flashcard_total_shown,
    )
    db.add(session_event)
    db.commit()
    db.refresh(session_event)
    return session_event


@router.patch("/{session_event_id}", response_model=AISessionEventResponse)
async def update_session_event(
    session_event_id: UUID,
    update: AISessionEventUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update a session event (typically called when session ends).
    Captures final engagement score, quiz results, mastery changes.
    """
    session_event = db.query(AISessionEvent).filter(
        and_(
            AISessionEvent.id == session_event_id,
            AISessionEvent.user_id == current_user.id,
        )
    ).first()

    if not session_event:
        raise HTTPException(status_code=404, detail="Session event not found")

    # Update fields (all validated by AISessionEventUpdate schema validators)
    session_event_any = cast(Any, session_event)
    if update.ended_at:
        session_event_any.ended_at = update.ended_at
    if update.total_duration_seconds is not None:
        session_event_any.total_duration_seconds = update.total_duration_seconds
    if update.engagement_score is not None:
        session_event_any.engagement_score = update.engagement_score
    if update.key_concepts is not None:
        session_event_any.key_concepts = update.key_concepts
    if update.misconceptions is not None:
        session_event_any.misconceptions = update.misconceptions
    if update.mastery_level is not None:
        session_event_any.mastery_level = update.mastery_level
    if update.confidence_change is not None:
        session_event_any.confidence_change = update.confidence_change
    if update.was_quiz_attempted is not None:
        session_event_any.was_quiz_attempted = update.was_quiz_attempted
    if update.quiz_score_percent is not None:
        session_event_any.quiz_score_percent = update.quiz_score_percent
    if update.flashcard_correct_count is not None:
        session_event_any.flashcard_correct_count = update.flashcard_correct_count
    if update.flashcard_total_shown is not None:
        session_event_any.flashcard_total_shown = update.flashcard_total_shown

    db.commit()
    db.refresh(session_event)
    return session_event


@router.get("/recent", response_model=List[AISessionSummary])
async def get_recent_sessions(
    days: int = 7,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[AISessionSummary]:
    """
    Get recent AI session summaries for the student.
    Used in student dashboard to show recent study activity.
    """
    since = datetime.now(timezone.utc) - timedelta(days=days)

    sessions = db.query(AISessionEvent).filter(
        and_(
            AISessionEvent.user_id == current_user.id,
            AISessionEvent.started_at >= since,
        )
    ).order_by(desc(AISessionEvent.started_at)).limit(limit).all()

    result: List[AISessionSummary] = []
    for session in sessions:
        session_any = cast(Any, session)
        # Parse key concepts and misconceptions from JSON strings
        concepts: List[str] = []
        if session_any.key_concepts is not None:
            try:
                concepts = json.loads(str(session_any.key_concepts))
            except (TypeError, ValueError, json.JSONDecodeError):
                concepts = []

        insights = [f"Studied: {', '.join(concepts[:3])}" if concepts else "Completed session"]
        if session_any.misconceptions is not None:
            try:
                misconceptions = json.loads(str(session_any.misconceptions))
                insights.append(f"Topics to revisit: {', '.join(misconceptions[:2])}")
            except (TypeError, ValueError, json.JSONDecodeError) as e:
                logger.warning(f"Failed to parse misconceptions JSON for session {session_any.session_id}: {type(e).__name__}: {e}")

        result.append(AISessionSummary(
            session_id=cast(str, session_any.session_id),
            tool_mode=cast(str, session_any.tool_mode),
            subject=cast(Optional[str], session_any.subject),
            topic=cast(Optional[str], session_any.topic),
            duration_seconds=int(cast(int, session_any.total_duration_seconds or 0)),
            engagement_score=float(cast(float, session_any.engagement_score or 0.0)),
            mastery_level=cast(str, session_any.mastery_level),
            quiz_score_percent=cast(Optional[float], session_any.quiz_score_percent),
            started_at=cast(datetime, session_any.started_at),
            ended_at=cast(Optional[datetime], session_any.ended_at),
            key_insights=insights,
        ))

    return result


@router.get("/by-subject/{subject}", response_model=List[AISessionSummary])
async def get_sessions_by_subject(
    subject: str,
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[AISessionSummary]:
    """
    Get all sessions for a specific subject in the past N days.
    Used for subject-specific learning insights.
    """
    since = datetime.now(timezone.utc) - timedelta(days=days)

    sessions = db.query(AISessionEvent).filter(
        and_(
            AISessionEvent.user_id == current_user.id,
            AISessionEvent.subject == subject,
            AISessionEvent.started_at >= since,
        )
    ).order_by(desc(AISessionEvent.started_at)).all()

    result: List[AISessionSummary] = []
    for session in sessions:
        session_any = cast(Any, session)
        result.append(AISessionSummary(
            session_id=cast(str, session_any.session_id),
            tool_mode=cast(str, session_any.tool_mode),
            subject=cast(Optional[str], session_any.subject),
            topic=cast(Optional[str], session_any.topic),
            duration_seconds=int(cast(int, session_any.total_duration_seconds or 0)),
            engagement_score=float(cast(float, session_any.engagement_score or 0.0)),
            mastery_level=cast(str, session_any.mastery_level),
            quiz_score_percent=cast(Optional[float], session_any.quiz_score_percent),
            started_at=cast(datetime, session_any.started_at),
            ended_at=cast(Optional[datetime], session_any.ended_at),
            key_insights=[f"Topic: {cast(str, session_any.topic)}" if session_any.topic else "Session completed"],
        ))

    return result


@router.get("/parent-insights", response_model=ParentInsightsSummary)
async def get_parent_insights(
    child_id: Optional[UUID] = None,
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ParentInsightsSummary:
    """
    Get parent-friendly summaries of child's AI learning activity.
    Aggregates session data for parent dashboard.
    """
    # For now, assume current_user is the student or has child context
    target_user_id = child_id or current_user.id
    since = datetime.now(timezone.utc) - timedelta(days=days)

    sessions = db.query(AISessionEvent).filter(
        and_(
            AISessionEvent.user_id == target_user_id,
            AISessionEvent.started_at >= since,
        )
    ).all()

    if not sessions:
        return ParentInsightsSummary(
            total_sessions=0,
            total_study_time_hours=0.0,
            active_subjects=[],
            average_engagement=0.0,
            recent_topics=[],
            quiz_attempts=0,
            average_quiz_score=None,
            mastery_progress={},
            recommended_topics=[],
        )

    # Calculate aggregates
    sessions_any = [cast(Any, s) for s in sessions]
    total_duration: int = sum(int(cast(int, s.total_duration_seconds or 0)) for s in sessions_any)
    total_duration_hours: float = (total_duration / SECONDS_PER_HOUR) if total_duration else 0.0

    active_subjects_set: set[str] = set()
    for s in sessions_any:
        if s.subject:
            active_subjects_set.add(str(s.subject))
    active_subjects: list[str] = list(active_subjects_set)
    
    average_engagement: float = float(sum(float(cast(float, s.engagement_score or 0.0)) for s in sessions_any)) / len(sessions_any)

    recent_topics: List[str] = []
    for s in sessions_any[-5:]:
        if s.topic:
            recent_topics.append(str(s.topic))

    quiz_sessions = [s for s in sessions_any if cast(bool, s.was_quiz_attempted)]
    quiz_attempts = len(quiz_sessions)
    average_quiz_score: Optional[float] = None
    if quiz_sessions:
        quiz_scores = [float(cast(float, s.quiz_score_percent)) for s in quiz_sessions if s.quiz_score_percent is not None]
        if quiz_scores:
            average_quiz_score = float(sum(quiz_scores)) / len(quiz_scores)

    # Build mastery progress by subject
    mastery_progress: Dict[str, str] = {}
    for subject_name in active_subjects:
        subject_sessions = [s for s in sessions if str(s.subject) == subject_name]
        if subject_sessions:
            # Average mastery level
            levels = {"beginner": 1, "intermediate": 2, "advanced": 3}
            avg_level_value = float(sum(
                levels.get(str(s.mastery_level), 1) for s in subject_sessions
            )) / len(subject_sessions)
            if avg_level_value >= 2.5:
                mastery_progress[subject_name] = "advanced"
            elif avg_level_value >= 1.5:
                mastery_progress[subject_name] = "intermediate"
            else:
                mastery_progress[subject_name] = "beginner"

    # Identify topics with misconceptions for parent guidance
    recommended_topics: List[str] = []
    for s in sessions_any:
        if s.misconceptions:
            try:
                misconceptions = json.loads(str(s.misconceptions))
                for topic in misconceptions:
                    if topic not in recommended_topics:
                        recommended_topics.append(topic)
            except (TypeError, ValueError, json.JSONDecodeError):
                pass

    return ParentInsightsSummary(
        total_sessions=len(sessions),
        total_study_time_hours=total_duration_hours,
        active_subjects=active_subjects,
        average_engagement=average_engagement,
        recent_topics=recent_topics[:5],
        quiz_attempts=quiz_attempts,
        average_quiz_score=average_quiz_score,
        mastery_progress=mastery_progress,
        recommended_topics=recommended_topics[:5],
    )
