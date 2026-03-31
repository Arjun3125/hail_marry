"""Persistent learner profile for personalization."""
import uuid

from sqlalchemy import Column, DateTime, Float, ForeignKey, String, text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID

from database import Base


class LearnerProfile(Base):
    """Stores inferred learner preferences and engagement signals."""

    __tablename__ = "learner_profiles"
    __table_args__ = (
        UniqueConstraint("tenant_id", "user_id", name="uq_learner_profiles_tenant_user"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    preferred_language = Column(String(32), nullable=False, default="english", server_default="english")
    inferred_expertise_level = Column(String(32), nullable=False, default="standard", server_default="standard")
    preferred_response_length = Column(String(32), nullable=False, default="default", server_default="default")
    primary_subjects = Column(JSONB, nullable=False, default=list, server_default="[]")
    engagement_score = Column(Float, nullable=False, default=0.0, server_default="0")
    consistency_score = Column(Float, nullable=False, default=0.0, server_default="0")
    signal_summary = Column(JSONB, nullable=False, default=dict, server_default="{}")
    last_recomputed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
