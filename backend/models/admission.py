"""Admission application model for student enrollment pipeline."""
import uuid
from sqlalchemy import Column, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from database import Base


class AdmissionApplication(Base):
    __tablename__ = "admission_applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)

    student_name = Column(String(255), nullable=False)
    parent_email = Column(String(255), nullable=False)
    parent_phone = Column(String(20), nullable=True)
    applied_class_id = Column(UUID(as_uuid=True), ForeignKey("classes.id"), nullable=True)
    applied_class_name = Column(String(100), nullable=True)  # denormalized for convenience

    status = Column(String(20), nullable=False, default="pending")
    # Valid statuses: pending, under_review, accepted, rejected, enrolled

    documents = Column(JSONB, nullable=True)  # [{"name": "birth_cert.pdf", "url": "..."}]
    notes = Column(Text, nullable=True)

    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)

    applied_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
