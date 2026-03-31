"""Topic and concept-level mastery tracking for personalized learning."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from database import Base


class TopicMastery(Base):
    __tablename__ = "topic_mastery"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "user_id",
            "topic",
            "concept",
            name="uq_topic_mastery_user_topic_concept",
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=True, index=True)
    topic = Column(String(255), nullable=False, index=True)
    concept = Column(String(255), nullable=False, index=True, default="core")
    mastery_score = Column(Float, nullable=False, default=55.0)
    confidence_score = Column(Float, nullable=False, default=0.15)
    evidence_count = Column(Integer, nullable=False, default=0)
    last_evidence_type = Column(String(50), nullable=True)
    last_evidence_score = Column(Float, nullable=True)
    last_evidence_at = Column(DateTime(timezone=True), nullable=True)
    review_due_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
