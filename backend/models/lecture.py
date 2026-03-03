"""Lecture library model."""
import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from database import Base


class Lecture(Base):
    __tablename__ = "lectures"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False)
    title = Column(String(255), nullable=False)
    youtube_url = Column(String(512), nullable=True)
    transcript_ingested = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
