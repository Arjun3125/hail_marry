"""Attendance tracking model."""
import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Date, DateTime, ForeignKey, func, Index
from sqlalchemy.dialects.postgresql import UUID
from database import Base


class Attendance(Base):
    __tablename__ = "attendance"

    id: Column[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Column[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    student_id: Column[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    class_id: Column[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("classes.id"), nullable=False, index=True)
    date: Column[date] = Column(Date, nullable=False, index=True)
    status: Column[str] = Column(String(20), nullable=False, default="present")  # present, absent, late
    created_at: Column[datetime] = Column(DateTime(timezone=True), server_default=func.now())
    
    # Composite indexes for common query patterns
    __table_args__ = (
        Index("ix_attendance_tenant_student_date", "tenant_id", "student_id", "date"),
        Index("ix_attendance_tenant_class_date", "tenant_id", "class_id", "date"),
        Index("ix_attendance_student_date", "student_id", "date"),
    )
