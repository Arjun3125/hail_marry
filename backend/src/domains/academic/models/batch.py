"""Batch management models — essential for Indian tuition/coaching centers.

Indian tuition centers operate in "batches" (e.g., Batch A - Class 10 Maths,
Evening Batch - JEE Physics). This model supports:
- Multiple batches per class/subject
- Teacher assignment per batch
- Trial class tracking (coaching centers often offer free trial classes)
- Capacity management for physical classroom constraints
"""
import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base


class Batch(Base):
    """A teaching group — maps to the Indian tuition concept of 'batch'.

    Examples: "Batch A - Class 10 Maths", "Evening JEE Physics", "NEET Bio Weekend"
    """
    __tablename__ = "batches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    name = Column(String(150), nullable=False)                    # "Batch A - Class 10 Maths"
    class_id = Column(UUID(as_uuid=True), ForeignKey("classes.id"), nullable=True)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=True)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    max_capacity = Column(Integer, nullable=True)                 # Physical room limit
    schedule_description = Column(String(300), nullable=True)     # "Mon/Wed/Fri 5-7 PM"
    academic_year = Column(String(20), nullable=False, default="2025-26")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    enrollments = relationship("BatchEnrollment", back_populates="batch", lazy="dynamic")


class BatchEnrollment(Base):
    """Student enrollment in a specific batch."""
    __tablename__ = "batch_enrollments"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "batch_id",
            "student_id",
            name="uq_batch_enrollment_tenant_batch_student",
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    batch_id = Column(UUID(as_uuid=True), ForeignKey("batches.id"), nullable=False, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    is_trial = Column(Boolean, default=False)                     # Trial class tracking
    trial_expires_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), nullable=False, default="active") # active, dropped, completed, trial
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    batch = relationship("Batch", back_populates="enrollments")
