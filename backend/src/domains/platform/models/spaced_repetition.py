"""Spaced Repetition Review Schedule model (SM-2 algorithm)."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Float, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from database import Base

class ReviewSchedule(Base):
    __tablename__ = "review_schedules"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    subject_id = Column(UUID(as_uuid=True), nullable=True)
    topic = Column(String, nullable=False)
    next_review_at = Column(DateTime(timezone=True), nullable=False)
    interval_days = Column(Integer, default=1)
    ease_factor = Column(Float, default=2.5)
    review_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
