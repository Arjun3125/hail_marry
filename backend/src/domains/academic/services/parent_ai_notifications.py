"""Parent notification service for AI learning insights."""
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import json

from sqlalchemy.orm import Session
from sqlalchemy import and_
from uuid import UUID

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
        since = datetime.now(timezone.utc) - timedelta(days=days)
        
        sessions = db.query(AISessionEvent).filter(
            and_(
                AISessionEvent.user_id == child_id,
                AISessionEvent.started_at >= since,
            )
        ).all()
        
        if not sessions:
            return None
        
        # Calculate stats
        total_sessions = len(sessions)
        total_duration: int = sum(s.total_duration_seconds for s in sessions)  # type: ignore
        total_duration_hours = float(total_duration) / 3600.0 if total_duration else 0.0
        
        # Get active subjects
        active_subjects = list(set([str(s.subject) for s in sessions if s.subject]))  # type: ignore
        
        # Calculate average engagement
        avg_engagement = float(sum(s.engagement_score for s in sessions)) / len(sessions)  # type: ignore
        
        # Get quiz stats
        quiz_sessions = [s for s in sessions if s.was_quiz_attempted]  # type: ignore
        avg_quiz_score = None
        if quiz_sessions:
            quiz_scores = [s.quiz_score_percent for s in quiz_sessions if s.quiz_score_percent]  # type: ignore
            if quiz_scores:
                avg_quiz_score = float(sum(quiz_scores)) / len(quiz_scores)  # type: ignore
        
        # Get recent topics
        recent_topics: list[str] = []
        for s in sessions[-5:]:
            if s.topic:  # type: ignore
                recent_topics.append(str(s.topic))  # type: ignore
        
        # Find topics with misconceptions
        misconception_topics: list[str] = []
        for s in sessions:
            if s.misconceptions:  # type: ignore
                try:
                    misconceptions = json.loads(s.misconceptions)  # type: ignore
                    for topic in misconceptions:
                        if topic not in misconception_topics:
                            misconception_topics.append(topic)
                except (TypeError, ValueError, json.JSONDecodeError):
                    pass
        
        return {
            "total_sessions": total_sessions,
            "total_study_time_hours": round(total_duration_hours, 1),  # type: ignore
            "active_subjects": active_subjects,
            "average_engagement": round(float(avg_engagement), 1),  # type: ignore
            "recent_topics": recent_topics[:3],
            "quiz_count": len(quiz_sessions),
            "average_quiz_score": round(float(avg_quiz_score), 1) if avg_quiz_score else None,  # type: ignore
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
        since = datetime.now(timezone.utc) - timedelta(days=days)
        session_count = db.query(AISessionEvent).filter(
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
        subjects_str = ", ".join(insights["active_subjects"][:2])  # type: ignore
        if len(insights["active_subjects"]) > 2:  # type: ignore
            subjects_str += f", and {len(insights['active_subjects']) - 2} more"  # type: ignore
        
        # Engagement level classification
        engagement = float(insights["average_engagement"])  # type: ignore
        if engagement >= 80:
            engagement_level = "Excellent"
        elif engagement >= 60:
            engagement_level = "Good"
        elif engagement >= 40:
            engagement_level = "Fair"
        else:
            engagement_level = "Needs Attention"
        
        title = f"📚 {child_name}'s AI Learning Update"
        
        body_parts = [
            f"Study time: {insights['total_study_time_hours']}h across {insights['total_sessions']} sessions",
            f"Engagement: {engagement_level} ({insights['average_engagement']}%)",
        ]
        
        if subjects_str:
            body_parts.append(f"Active subjects: {subjects_str}")
        
        if insights["average_quiz_score"] is not None:  # type: ignore
            body_parts.append(f"Average quiz score: {insights['average_quiz_score']}%")  # type: ignore
        
        if insights.get("topics_to_review"):  # type: ignore
            topics_str = ", ".join(insights["topics_to_review"])  # type: ignore
            body_parts.append(f"Topics to review: {topics_str}")
        
        body = "\n".join([f"• {part}" for part in body_parts])
        
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
