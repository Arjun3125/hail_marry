"""Signal extraction and logging models for personality profiling."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from database import Base


class ProfileSignal(Base):
    """Stores individual signals extracted from student interactions."""

    __tablename__ = "profile_signals"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    student_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)

    signal_type = Column(String(100), nullable=False, index=True)  # e.g., "learning_style_hint"
    signal_value = Column(Text, nullable=False)                    # e.g., "visual"
    confidence_score = Column(Float, nullable=False)               # 0.0 to 1.0
    extraction_method = Column(String(50), nullable=False)         # "rule_based", "llm", etc.
    extraction_channel = Column(String(50), nullable=False)        # "whatsapp", "web", etc.

    promoted_to_profile = Column(Boolean, nullable=False, default=False, index=True)

    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))


class ElicitationLog(Base):
    """Tracks elicitation questions asked to students."""

    __tablename__ = "elicitation_log"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    student_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)

    question_key = Column(String(100), nullable=False, index=True)  # e.g., "learning_style_pref"
    asked_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    response_text = Column(Text, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    answered_at = Column(DateTime(timezone=True), nullable=True)
    skipped_count = Column(Integer, nullable=False, default=0)


class ExtractedSignal(BaseModel):
    """Represents a signal extracted from text analysis."""

    signal_type: str
    signal_value: str
    confidence_score: float
    extraction_method: str = "rule_based"


class ProfileSignalRead(BaseModel):
    """Read model for profile signals API responses."""

    id: UUID
    student_id: UUID
    tenant_id: UUID
    signal_type: str
    signal_value: str
    confidence_score: float
    extraction_method: str
    extraction_channel: str
    promoted_to_profile: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ElicitationLogRead(BaseModel):
    """Read model for elicitation log API responses."""

    id: UUID
    student_id: UUID
    tenant_id: UUID
    question_key: str
    asked_at: datetime
    response_text: Optional[str] = None
    response_time_ms: Optional[int] = None
    answered_at: Optional[datetime] = None
    skipped_count: int

    class Config:
        from_attributes = True
