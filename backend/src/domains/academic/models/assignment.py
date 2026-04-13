"""Assignment and submission models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from database import Base


class Assignment(Base):
    __tablename__ = "assignments"

    id: Column[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Column[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    subject_id: Column[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False)
    title: Column[str] = Column(String(255), nullable=False)
    description: Column[str] = Column(Text, nullable=True)
    due_date: Column[datetime] = Column(DateTime(timezone=True), nullable=True)
    created_by: Column[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at: Column[datetime] = Column(DateTime(timezone=True), server_default=func.now())


class AssignmentSubmission(Base):
    __tablename__ = "assignment_submissions"
    __table_args__ = (
        UniqueConstraint("tenant_id", "assignment_id", "student_id", name="uq_assignment_submissions_student"),
    )

    id: Column[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Column[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    assignment_id: Column[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("assignments.id"), nullable=False)
    student_id: Column[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    submission_url: Column[str] = Column(Text, nullable=True)
    submitted_at: Column[datetime] = Column(DateTime(timezone=True), server_default=func.now())
    grade: Column[int] = Column(Integer, nullable=True)
    feedback: Column[str] = Column(Text, nullable=True)
