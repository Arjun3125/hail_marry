"""Subject Performance — precomputed performance aggregation for AI personalization."""
import uuid
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from database import Base


class SubjectPerformance(Base):
    __tablename__ = "subject_performance"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False)
    average_score = Column(Float, default=0.0)
    exam_count = Column(Integer, default=0)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
