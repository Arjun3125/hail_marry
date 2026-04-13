"""Mascot memory models for storing conversation state and preferences."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID

from database import Base


class StudentMascotMemory(Base):
    """Stores persistent memory for each student's mascot interactions."""

    __tablename__ = "student_mascot_memory"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    student_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)

    # Interaction tracking
    total_interactions = Column(Integer, nullable=False, default=0)
    last_interaction_at = Column(DateTime(timezone=True), nullable=True)
    last_summary = Column(Text, nullable=True)
    last_emotional_state = Column(String(20), nullable=True)

    # Preferences
    preferred_explanation_style = Column(String(50), nullable=True)
    mascot_tone_setting = Column(String(50), nullable=False, default="encouraging")

    # Context snapshot (pre-assembled for fast responses)
    context_snapshot = Column(JSONB, nullable=True)

    # Timestamps
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))


class MascotMemoryUpdate(BaseModel):
    """Update model for modifying mascot memory fields."""

    last_summary: Optional[str] = None
    last_emotional_state: Optional[str] = None
    preferred_explanation_style: Optional[str] = None
    mascot_tone_setting: Optional[str] = None
    context_snapshot: Optional[dict] = None


class MascotMemoryRead(BaseModel):
    """Read model for mascot memory API responses."""

    id: UUID
    student_id: UUID
    tenant_id: UUID
    total_interactions: int
    last_interaction_at: Optional[datetime] = None
    last_summary: Optional[str] = None
    last_emotional_state: Optional[str] = None
    preferred_explanation_style: Optional[str] = None
    mascot_tone_setting: str
    updated_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True
