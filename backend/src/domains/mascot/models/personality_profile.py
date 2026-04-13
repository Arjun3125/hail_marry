"""Personality profile models for storing student traits and preferences."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlalchemy import ARRAY, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from database import Base


class StudentPersonalityProfile(Base):
    """Stores aggregated personality traits and learning preferences for each student."""

    __tablename__ = "student_personality_profiles"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    student_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)

    # Learning preferences
    learning_style_detected = Column(String(50), nullable=True)  # visual, auditory, kinesthetic, etc.
    learning_style_stated = Column(String(50), nullable=True)   # explicitly stated by student
    reasoning_type = Column(String(50), nullable=True)          # analytical, intuitive, etc.
    primary_motivation_driver = Column(String(50), nullable=True)  # achievement, curiosity, fear, reward, belonging

    # Emotional and psychological
    stress_threshold = Column(Float, nullable=True)             # 0.0 to 1.0
    self_esteem_score = Column(Float, nullable=True)            # 0.0 to 1.0
    resilience_score = Column(Float, nullable=True)             # 0.0 to 1.0
    humor_index = Column(Float, nullable=True)                  # 0.0 to 1.0

    # Social and behavioral
    social_orientation = Column(String(50), nullable=True)      # competitive, collaborative, independent
    locus_of_control = Column(String(50), nullable=True)        # internal, external
    mindset_orientation = Column(String(50), nullable=True)     # growth, fixed

    # Temporal preferences
    peak_study_hour = Column(Integer, nullable=True)            # 0-23

    # Help-seeking behavior
    help_seeking_style = Column(String(50), nullable=True)      # independent, collaborative, guided

    # Aspirations and interests
    career_aspiration_text = Column(Text, nullable=True)
    interest_tags = Column(ARRAY(String(100)), nullable=True)   # ["sports", "music", "science"]

    # External pressures
    parental_pressure_level = Column(String(20), nullable=True)  # "low", "medium", "high"

    # Metadata
    profile_completeness_score = Column(Float, nullable=False, default=0.0)  # 0.0 to 1.0
    profile_version = Column(Integer, nullable=False, default=1)

    # Timestamps
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))


class PersonalityProfileRead(BaseModel):
    """Read model for personality profile API responses (admin view)."""

    id: UUID
    student_id: UUID
    tenant_id: UUID
    learning_style_detected: Optional[str] = None
    learning_style_stated: Optional[str] = None
    reasoning_type: Optional[str] = None
    primary_motivation_driver: Optional[str] = None
    stress_threshold: Optional[float] = None
    self_esteem_score: Optional[float] = None
    resilience_score: Optional[float] = None
    humor_index: Optional[float] = None
    social_orientation: Optional[str] = None
    locus_of_control: Optional[str] = None
    mindset_orientation: Optional[str] = None
    peak_study_hour: Optional[int] = None
    help_seeking_style: Optional[str] = None
    career_aspiration_text: Optional[str] = None
    interest_tags: Optional[List[str]] = None
    parental_pressure_level: Optional[str] = None
    profile_completeness_score: float
    profile_version: int
    updated_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class PersonalityProfilePublic(BaseModel):
    """Public read model for personality profile (student view - excludes sensitive fields)."""

    learning_style_detected: Optional[str] = None
    primary_motivation_driver: Optional[str] = None
    resilience_score: Optional[float] = None
    social_orientation: Optional[str] = None
    career_aspiration_text: Optional[str] = None
    interest_tags: Optional[List[str]] = None
    profile_completeness_score: float
    profile_version: int

    class Config:
        from_attributes = True
