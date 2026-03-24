"""Lecture and class scheduling models."""
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, func, Integer
from sqlalchemy.dialects.postgresql import UUID
from database import Base

class Lecture(Base):
    __tablename__ = "lectures"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False)
    class_id = Column(UUID(as_uuid=True), ForeignKey("classes.id"), nullable=False)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, default=45)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
