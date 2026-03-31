"""Persisted remediation and study-path plans for personalized learning."""
import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from database import Base


class StudyPathPlan(Base):
    __tablename__ = "study_path_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    notebook_id = Column(UUID(as_uuid=True), ForeignKey("notebooks.id"), nullable=True, index=True)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=True, index=True)
    plan_type = Column(String(32), nullable=False, default="remediation", server_default="remediation")
    focus_topic = Column(String(255), nullable=False, index=True)
    status = Column(String(32), nullable=False, default="active", server_default="active")
    current_step_index = Column(Integer, nullable=False, default=0, server_default="0")
    items = Column(JSONB, nullable=False, default=list, server_default="[]")
    source_context = Column(JSONB, nullable=False, default=dict, server_default="{}")
    is_active = Column(Boolean, nullable=False, default=True, server_default=text("true"))
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
