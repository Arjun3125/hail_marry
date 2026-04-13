"""Parent notification service for AI learning insights."""
from datetime import datetime, timedelta, timezone
from typing import cast, List, Optional, Dict, Any
import json

from sqlalchemy.orm import Session
from sqlalchemy import and_
from uuid import UUID

from constants import (
    SECONDS_PER_HOUR,
    ENGAGEMENT_EXCELLENT_PCT,
    ENGAGEMENT_GOOD_PCT,
    ENGAGEMENT_FAIR_PCT,
)
from src.domains.platform.models.ai import AISessionEvent


class ParentAIInsightNotificationService:
    """Service to generate and send parent notifications about child's AI learning."""

    @staticmethod
    def generate_ai_insight_summary(
        db: Session,
        child_id: UUID,
        days: int = 7,
    ) -> Optional[Dict[str, Any]]:
        """Generate AI insight summary for a child's recent sessions.
        
        Args:
            db: Database session
            child_id: Child's user ID
            days: Number of days to look back
            
        Returns:
            Dictionary with insight summary or None if no sessions found
        """
        since: datetime = datetime.now(timezone.utc) - timedelta(days=days)
        
        sessions: List[AISessionEvent] = db.query(AISessionEvent).filter(
            and_(
                AISessionEvent.user_id == child_id,
                AISessionEvent.started_at >= since,
            )
        ).all()
        
        if not sessions:
            return None
        
        # Calculate stats
        total_sessions: int = len(sessions)
        total_duration: int = sum(
            int(cast(Optional[int], getattr(s, "total_duration_seconds", None)) or 0)
            for s in sessions
        )
        total_duration_hours: float = float(total_duration) / SECONDS_PER_HOUR if total_duration else 0.0
        
        # Get active subjects
        active_subjects: list[str] = list(
            {
                str(cast(str, getattr(s, "subject", None)))
                for s in sessions
                if cast(Optional[str], getattr(s, "subject", None)) is not None
            }
        )
        
        # Calculate average engagement
        engagement_total: float = 0.0
        for s in sessions:
            engagement_score = cast(Optional[float], getattr(s, "engagement_score", None))
            engagement_total += float(engagement_score) if engagement_score is not None else 0.0

        avg_engagement: float = engagement_total / len(sessions)
        
        # Get quiz stats
        quiz_sessions: list[AISessionEvent] = [
            s
            for s in sessions
            if cast(Optional[bool], getattr(s, "was_quiz_attempted", None)) is True
        ]
        avg_quiz_score: Optional[float] = None
        if quiz_sessions:
            quiz_scores: list[float] = []
            for s in quiz_sessions:
                quiz_score = cast(Optional[float], getattr(s, "quiz_score_percent", None))
                if quiz_score is not None:
                    quiz_scores.append(float(quiz_score))
            if quiz_scores:
                avg_quiz_score = float(sum(quiz_scores)) / len(quiz_scores)
        
        # Get recent topics
        recent_topics: list[str] = []
        for s in sessions[-5:]:
            topic = cast(Optional[str], getattr(s, "topic", None))
            if topic:
                recent_topics.append(str(topic))
        
        # Find topics with misconceptions
        misconception_topics: list[str] = []
        for s in sessions:
            misconceptions_raw = cast(Optional[str], getattr(s, "misconceptions", None))
            if misconceptions_raw:
                try:
                    misconceptions = json.loads(misconceptions_raw)
                    for topic in misconceptions:
                        if topic not in misconception_topics:
                            misconception_topics.append(topic)
                except (TypeError, ValueError, json.JSONDecodeError):
                    pass
        
        return {
            "total_sessions": total_sessions,
            "total_study_time_hours": round(total_duration_hours, 1),
            "active_subjects": active_subjects,
            "average_engagement": round(float(avg_engagement), 1),
            "recent_topics": recent_topics[:3],
            "quiz_count": len(quiz_sessions),
            "average_quiz_score": round(float(avg_quiz_score), 1) if avg_quiz_score else None,
            "topics_to_review": misconception_topics[:3],
            "period_days": days,
        }

    @staticmethod
    def should_send_notification(
        db: Session,
        child_id: UUID,
        parent_id: UUID,
        days: int = 7,
    ) -> bool:
        """Determine if a parent notification should be sent.
        
        Conditions:
        - Child has at least 3 sessions in the past N days
        - Parent hasn't received notification in the last 24 hours
        """
        since: datetime = datetime.now(timezone.utc) - timedelta(days=days)
        session_count: int = db.query(AISessionEvent).filter(
            and_(
                AISessionEvent.user_id == child_id,
                AISessionEvent.started_at >= since,
            )
        ).count()
        
        return session_count >= 3

    @staticmethod
    def create_notification_message(
        child_name: str,
        insights: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create a structured notification message.
        
        Args:
            child_name: Name of the child
            insights: Insight summary from generate_ai_insight_summary
            
        Returns:
            Notification message dictionary
        """
        subjects_str: str = ", ".join(insights["active_subjects"][:2])
        if len(insights["active_subjects"]) > 2:
            subjects_str += f", and {len(insights['active_subjects']) - 2} more"
        
        # Engagement level classification
        engagement = float(insights["average_engagement"])
        if engagement >= ENGAGEMENT_EXCELLENT_PCT:
            engagement_level = "Excellent"
        elif engagement >= ENGAGEMENT_GOOD_PCT:
            engagement_level = "Good"
        elif engagement >= ENGAGEMENT_FAIR_PCT:
            engagement_level = "Fair"
        else:
            engagement_level = "Needs Attention"
        
        title: str = f"📚 {child_name}'s AI Learning Update"
        
        body_parts: list[str] = [
            f"Study time: {insights['total_study_time_hours']}h across {insights['total_sessions']} sessions",
            f"Engagement: {engagement_level} ({insights['average_engagement']}%)",
        ]
        
        if subjects_str:
            body_parts.append(f"Active subjects: {subjects_str}")
        
        if insights["average_quiz_score"] is not None:
            body_parts.append(f"Average quiz score: {insights['average_quiz_score']}%")
        
        if insights.get("topics_to_review"):
            topics_str: str = ", ".join(insights["topics_to_review"])
            body_parts.append(f"Topics to review: {topics_str}")
        
        body: str = "\n".join([f"• {part}" for part in body_parts])
        
        return {
            "title": title,
            "body": body,
            "type": "ai_learning_insights",
            "priority": "medium",
            "data": {
                "insights": insights,
                "action_url": "/parent/reports",
            },
        }
