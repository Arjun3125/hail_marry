"""AI query log with trace support."""
import uuid
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, func, Boolean, Float
from sqlalchemy.dialects.postgresql import UUID
from database import Base

class AIQuery(Base):
    __tablename__ = "ai_queries"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    notebook_id = Column(UUID(as_uuid=True), ForeignKey("notebooks.id"), nullable=True, index=True)
    query_text = Column(Text, nullable=False)
    mode = Column(String(50), nullable=False, default="qa")
    response_text = Column(Text, nullable=True)
    token_usage = Column(Integer, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    trace_id = Column(String(64), nullable=True)
    citation_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # History management fields
    title = Column(String(200), nullable=True)
    is_pinned = Column(Boolean, default=False)
    folder_id = Column(UUID(as_uuid=True), ForeignKey("ai_folders.id"), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)


class AISessionEvent(Base):
    """Track AI Studio session activity: tool usage, topic focus, learning outcomes."""
    __tablename__ = "ai_session_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Session metadata
    session_id = Column(String(64), nullable=False, index=True)  # Browser session ID
    tool_mode = Column(String(50), nullable=False)  # qa, quiz, flashcards, mindmap, etc.
    subject = Column(String(100), nullable=True, index=True)  # e.g., "Physics", "Mathematics"
    topic = Column(String(255), nullable=True)  # e.g., "Thermodynamics", "Quadratic Equations"
    
    # Activity tracking
    queries_count = Column(Integer, default=0)  # Number of questions asked in session
    total_duration_seconds = Column(Integer, default=0)  # Session length
    engagement_score = Column(Float, default=0.0)  # 0-100: measurement of student focus
    
    # Learning outcomes (extracted from session)
    key_concepts = Column(Text, nullable=True)  # JSON list: ["concept1", "concept2", ...]
    misconceptions = Column(Text, nullable=True)  # JSON list of identified gaps
    mastery_level = Column(String(20), default="beginner")  # beginner, intermediate, advanced
    confidence_change = Column(Float, default=0.0)  # -100 to +100: improvement in confidence
    
    # Retention markers
    was_quiz_attempted = Column(Boolean, default=False)
    quiz_score_percent = Column(Float, nullable=True)  # 0-100 if quiz taken
    flashcard_correct_count = Column(Integer, default=0)  # For spaced repetition tracking
    flashcard_total_shown = Column(Integer, default=0)
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    ended_at = Column(DateTime(timezone=True), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AIFolder(Base):
    __tablename__ = "ai_folders"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    color = Column(String(20), default="blue")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
