"""Academic structure: Classes, Subjects, Enrollments."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Column, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base

if TYPE_CHECKING:
    from src.domains.identity.models.user import User

class Class(Base):
    __tablename__ = "classes"
    id: Column[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Column[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    name: Column[str] = Column(String(100), nullable=False)
    grade_level: Column[str] = Column(String(50), nullable=True)
    academic_year: Column[str] = Column(String(20), nullable=False, default="2025-26")
    created_at: Column[datetime] = Column(DateTime(timezone=True), server_default=func.now())
    subjects: list["Subject"] = relationship("Subject", back_populates="class_ref")
    enrollments: list["Enrollment"] = relationship("Enrollment", back_populates="class_ref")

class Subject(Base):
    __tablename__ = "subjects"
    id: Column[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Column[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    name: Column[str] = Column(String(100), nullable=False)
    class_id: Column[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("classes.id"), nullable=False)
    created_at: Column[datetime] = Column(DateTime(timezone=True), server_default=func.now())
    class_ref: "Class" = relationship("Class", back_populates="subjects")

class Enrollment(Base):
    __tablename__ = "enrollments"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "student_id",
            "class_id",
            "academic_year",
            name="uq_enrollment_tenant_student_class_year",
        ),
    )

    id: Column[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Column[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    student_id: Column[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    class_id: Column[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("classes.id"), nullable=False)
    roll_number: Column[str] = Column(String(50), nullable=True)
    academic_year: Column[str] = Column(String(20), nullable=False, default="2025-26")
    created_at: Column[datetime] = Column(DateTime(timezone=True), server_default=func.now())
    class_ref: "Class" = relationship("Class", back_populates="enrollments")
    student: User = relationship("User", foreign_keys=[student_id], lazy="select")
