"""Student subject-wise performance tracking model."""
import uuid
from datetime import datetime
from sqlalchemy import Column, ForeignKey, Float, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from database import Base

class SubjectPerformance(Base):
    __tablename__ = "subject_performance"
    id: Column[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Column[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    student_id: Column[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    subject_id: Column[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False)
    average_score = Column(Float, default=0.0)
    attendance_rate = Column(Float, default=0.0)
    last_updated: Column[datetime] = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
