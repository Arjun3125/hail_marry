"""AI session tracking routes for student learning activity."""
from uuid import UUID
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Any, Dict
import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import desc, and_
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from database import get_db
from src.domains.identity.models.user import User
from src.domains.platform.models.ai import AISessionEvent

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
    """Update session event fields (for session end)."""
    ended_at: datetime
    total_duration_seconds: Optional[int] = None
    engagement_score: Optional[float] = None
    key_concepts: Optional[str] = None
    misconceptions: Optional[str] = None
    mastery_level: Optional[str] = None
    confidence_change: Optional[float] = None
    was_quiz_attempted: Optional[bool] = None
    quiz_score_percent: Optional[float] = None
    flashcard_correct_count: Optional[int] = None
    flashcard_total_shown: Optional[int] = None


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

    # Update fields
    if update.ended_at:
        session_event.ended_at = update.ended_at  # type: ignore
    if update.total_duration_seconds is not None:
        session_event.total_duration_seconds = update.total_duration_seconds  # type: ignore
    if update.engagement_score is not None:
        session_event.engagement_score = update.engagement_score  # type: ignore
    if update.key_concepts is not None:
        session_event.key_concepts = update.key_concepts  # type: ignore
    if update.misconceptions is not None:
        session_event.misconceptions = update.misconceptions  # type: ignore
    if update.mastery_level is not None:
        session_event.mastery_level = update.mastery_level  # type: ignore
    if update.confidence_change is not None:
        session_event.confidence_change = update.confidence_change  # type: ignore
    if update.was_quiz_attempted is not None:
        session_event.was_quiz_attempted = update.was_quiz_attempted  # type: ignore
    if update.quiz_score_percent is not None:
        session_event.quiz_score_percent = update.quiz_score_percent  # type: ignore
    if update.flashcard_correct_count is not None:
        session_event.flashcard_correct_count = update.flashcard_correct_count  # type: ignore
    if update.flashcard_total_shown is not None:
        session_event.flashcard_total_shown = update.flashcard_total_shown  # type: ignore

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
        # Parse key concepts and misconceptions from JSON strings
        concepts: List[str] = []
        if session.key_concepts:  # type: ignore
            try:
                concepts = json.loads(session.key_concepts)  # type: ignore
            except (TypeError, ValueError, json.JSONDecodeError):
                concepts = []

        insights = [f"Studied: {', '.join(concepts[:3])}" if concepts else "Completed session"]
        if session.misconceptions:  # type: ignore
            try:
                misconceptions = json.loads(session.misconceptions)  # type: ignore
                insights.append(f"Topics to revisit: {', '.join(misconceptions[:2])}")
            except (TypeError, ValueError, json.JSONDecodeError):
                pass

        result.append(AISessionSummary(
            session_id=session.session_id,  # type: ignore
            tool_mode=session.tool_mode,  # type: ignore
            subject=session.subject,  # type: ignore
            topic=session.topic,  # type: ignore
            duration_seconds=session.total_duration_seconds,  # type: ignore
            engagement_score=session.engagement_score,  # type: ignore
            mastery_level=session.mastery_level,  # type: ignore
            quiz_score_percent=session.quiz_score_percent,  # type: ignore
            started_at=session.started_at,  # type: ignore
            ended_at=session.ended_at,  # type: ignore
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
        if session.key_concepts:  # type: ignore
            try:
                json.loads(session.key_concepts)  # type: ignore
            except (TypeError, ValueError, json.JSONDecodeError):
                pass

        result.append(AISessionSummary(
            session_id=session.session_id,  # type: ignore
            tool_mode=session.tool_mode,  # type: ignore
            subject=session.subject,  # type: ignore
            topic=session.topic,  # type: ignore
            duration_seconds=session.total_duration_seconds,  # type: ignore
            engagement_score=session.engagement_score,  # type: ignore
            mastery_level=session.mastery_level,  # type: ignore
            quiz_score_percent=session.quiz_score_percent,  # type: ignore
            started_at=session.started_at,  # type: ignore
            ended_at=session.ended_at,  # type: ignore
            key_insights=[f"Topic: {session.topic}" if session.topic else "Session completed"],  # type: ignore
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
    total_duration: int = sum(s.total_duration_seconds for s in sessions)  # type: ignore
    total_duration_hours: float = (total_duration / 3600.0) if total_duration else 0.0

    active_subjects_set: set[str] = set()
    for s in sessions:
        if s.subject:  # type: ignore
            active_subjects_set.add(str(s.subject))  # type: ignore
    active_subjects: list[str] = list(active_subjects_set)
    
    average_engagement: float = float(sum(s.engagement_score for s in sessions)) / len(sessions)  # type: ignore

    recent_topics: List[str] = []
    for s in sessions[-5:]:
        if s.topic:  # type: ignore
            recent_topics.append(str(s.topic))  # type: ignore

    quiz_sessions = [s for s in sessions if s.was_quiz_attempted]  # type: ignore
    quiz_attempts = len(quiz_sessions)
    average_quiz_score: Optional[float] = None
    if quiz_sessions:
        quiz_scores = [s.quiz_score_percent for s in quiz_sessions if s.quiz_score_percent]  # type: ignore
        if quiz_scores:
            average_quiz_score = float(sum(quiz_scores)) / len(quiz_scores)  # type: ignore

    # Build mastery progress by subject
    mastery_progress: Dict[str, str] = {}
    for subject_name in active_subjects:
        subject_sessions = [s for s in sessions if str(s.subject) == subject_name]  # type: ignore
        if subject_sessions:
            # Average mastery level
            levels = {"beginner": 1, "intermediate": 2, "advanced": 3}
            avg_level_value = float(sum(
                levels.get(str(s.mastery_level), 1) for s in subject_sessions  # type: ignore
            )) / len(subject_sessions)
            if avg_level_value >= 2.5:
                mastery_progress[subject_name] = "advanced"
            elif avg_level_value >= 1.5:
                mastery_progress[subject_name] = "intermediate"
            else:
                mastery_progress[subject_name] = "beginner"

    # Identify topics with misconceptions for parent guidance
    recommended_topics: List[str] = []
    for s in sessions:
        if s.misconceptions:  # type: ignore
            try:
                misconceptions = json.loads(s.misconceptions)  # type: ignore
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
