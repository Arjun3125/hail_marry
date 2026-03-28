"""Context memory service for notebook-scoped conversation history."""
from typing import Optional
from uuid import UUID
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from src.domains.platform.models.ai import AIQuery


class ContextMemoryService:
    """Manages conversation context within a notebook for coherent multi-turn interactions."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_conversation_history(
        self,
        user_id: UUID,
        notebook_id: Optional[UUID] = None,
        limit: int = 10,
        hours: int = 24,
    ) -> list[dict]:
        """Get recent conversation history for context building.
        
        Args:
            user_id: User ID to filter by
            notebook_id: Optional notebook ID to scope to specific notebook
            limit: Maximum number of messages to return
            hours: Lookback period in hours
        
        Returns:
            List of conversation entries with query and response
        """
        since = datetime.now(UTC) - timedelta(hours=hours)
        
        query = self.db.query(AIQuery).filter(
            AIQuery.user_id == user_id,
            AIQuery.created_at >= since,
            AIQuery.deleted_at.is_(None),
        )
        
        if notebook_id:
            # Filter to specific notebook or global (no notebook) conversations
            query = query.filter(
                (AIQuery.notebook_id == notebook_id) | (AIQuery.notebook_id.is_(None))
            )
        else:
            # Only global conversations
            query = query.filter(AIQuery.notebook_id.is_(None))
        
        history = (
            query.order_by(desc(AIQuery.created_at))
            .limit(limit)
            .all()
        )
        
        return [
            {
                "id": str(h.id),
                "query": h.query_text,
                "response": h.response_text,
                "mode": h.mode,
                "created_at": h.created_at.isoformat() if h.created_at else None,
                "notebook_id": str(h.notebook_id) if h.notebook_id else None,
            }
            for h in reversed(history)  # Return in chronological order
        ]
    
    async def get_thread_context(
        self,
        thread_id: UUID,
        user_id: UUID,
    ) -> list[dict]:
        """Get all messages in a specific conversation thread.
        
        Args:
            thread_id: The parent conversation/thread ID
            user_id: User ID for security filtering
        
        Returns:
            List of conversation entries in the thread
        """
        history = (
            self.db.query(AIQuery)
            .filter(
                AIQuery.user_id == user_id,
                AIQuery.id == thread_id,
            )
            .order_by(AIQuery.created_at)
            .all()
        )
        
        return [
            {
                "id": str(h.id),
                "query": h.query_text,
                "response": h.response_text,
                "mode": h.mode,
                "created_at": h.created_at.isoformat() if h.created_at else None,
            }
            for h in history
        ]
    
    def format_context_for_prompt(
        self,
        history: list[dict],
        max_tokens: int = 2000,
    ) -> str:
        """Format conversation history for inclusion in AI prompt.
        
        Args:
            history: List of conversation entries
            max_tokens: Approximate token limit for context
        
        Returns:
            Formatted context string
        """
        if not history:
            return ""
        
        lines = ["Previous conversation context:"]
        total_chars = len(lines[0])
        
        # Approximate 4 chars per token
        max_chars = max_tokens * 4
        
        for entry in history:
            entry_text = f"User: {entry['query']}\nAssistant: {entry['response'][:500]}"
            if total_chars + len(entry_text) > max_chars:
                break
            lines.append(entry_text)
            total_chars += len(entry_text)
        
        return "\n\n".join(lines)
    
    async def get_notebook_stats(
        self,
        notebook_id: UUID,
        user_id: UUID,
    ) -> dict:
        """Get conversation statistics for a notebook.
        
        Args:
            notebook_id: Notebook ID to analyze
            user_id: User ID for security
        
        Returns:
            Statistics dict with counts and metrics
        """
        base_query = self.db.query(AIQuery).filter(
            AIQuery.user_id == user_id,
            AIQuery.notebook_id == notebook_id,
            AIQuery.deleted_at.is_(None),
        )
        
        total_queries = base_query.count()
        
        # Get mode distribution
        mode_counts = (
            base_query
            .with_entities(AIQuery.mode, func.count(AIQuery.id))
            .group_by(AIQuery.mode)
            .all()
        )
        
        # Get today's count
        today = datetime.now(UTC).date()
        today_count = (
            base_query
            .filter(func.date(AIQuery.created_at) == today)
            .count()
        )
        
        # Average response time
        avg_response_time = (
            base_query
            .with_entities(func.avg(AIQuery.response_time_ms))
            .scalar()
        ) or 0
        
        return {
            "total_queries": total_queries,
            "today_queries": today_count,
            "mode_distribution": {mode: count for mode, count in mode_counts},
            "average_response_time_ms": round(avg_response_time, 2),
        }


# Singleton instance factory
def get_context_memory_service(db: Session) -> ContextMemoryService:
    """Get ContextMemoryService instance."""
    return ContextMemoryService(db)
