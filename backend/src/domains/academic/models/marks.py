"""Exams and marks models."""
import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Integer, Date, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from database import Base


class Exam(Base):
    __tablename__ = "exams"

    id: Column[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Column[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    name: Column[str] = Column(String(100), nullable=False)
    subject_id: Column[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False)
    max_marks: Column[int] = Column(Integer, nullable=False, default=100)
    exam_date: Column[date] = Column(Date, nullable=True)
    created_at: Column[datetime] = Column(DateTime(timezone=True), server_default=func.now())


class Mark(Base):
    __tablename__ = "marks"

    id: Column[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Column[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    student_id: Column[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    exam_id: Column[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("exams.id"), nullable=False)
    marks_obtained: Column[int] = Column(Integer, nullable=False)
    created_at: Column[datetime] = Column(DateTime(timezone=True), server_default=func.now())
