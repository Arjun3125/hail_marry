"""Conversation logging models for mascot interactions."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from database import Base


class MascotConversationTurn(Base):
    """Stores individual turns in mascot conversations for analysis and continuity."""

    __tablename__ = "mascot_conversation_turns"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    student_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)

    session_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    turn_number = Column(Integer, nullable=False)

    # Content
    student_message = Column(Text, nullable=True)
    mascot_response = Column(Text, nullable=True)

    # Analysis
    emotional_state = Column(String(20), nullable=True)  # positive, neutral, anxious, frustrated, disengaged
    elicitation_question_key = Column(String(100), nullable=True)  # if this turn included an elicitation

    # Performance
    response_time_ms = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))


class ConversationTurnRead(BaseModel):
    """Read model for conversation turns API responses."""

    id: UUID
    student_id: UUID
    tenant_id: UUID
    session_id: UUID
    turn_number: int
    student_message: Optional[str] = None
    mascot_response: Optional[str] = None
    emotional_state: Optional[str] = None
    elicitation_question_key: Optional[str] = None
    response_time_ms: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
