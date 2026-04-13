"""Lecture and class scheduling models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, func, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from database import Base

class Lecture(Base):
    __tablename__ = "lectures"
    id: Column[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Column[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    subject_id: Column[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False)
    class_id: Column[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("classes.id"), nullable=False)
    teacher_id: Column[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title: Column[str] = Column(String(200), nullable=False)
    description: Column[str] = Column(String(500), nullable=True)
    youtube_url: Column[str] = Column(String(500), nullable=True)
    scheduled_at: Column[datetime] = Column(DateTime(timezone=True), nullable=False)
    duration_minutes: Column[int] = Column(Integer, default=45)
    transcript_ingested: Column[bool] = Column(Boolean, default=False)
    created_at: Column[datetime] = Column(DateTime(timezone=True), server_default=func.now())
