"""Notebook model for subject-based organization."""
import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import UUID

from database import Base


class Notebook(Base):
    """A notebook represents a subject-based workspace for study materials."""

    __tablename__ = "notebooks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    subject = Column(String(100), nullable=True)
    color = Column(String(7), nullable=False, default="#6366f1")
    icon = Column(String(50), nullable=False, default="Book")
    created_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    is_active = Column(Boolean, nullable=False, default=True, index=True)
