"""Test Series and Mock Test Attempt models for competitive exam features."""
import uuid
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Boolean, func, Text
from sqlalchemy.dialects.postgresql import UUID
from database import Base


class TestSeries(Base):
    """A test series is a collection of mock tests (e.g., 'JEE Main 2026 Series')."""
    __tablename__ = "test_series"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)  # e.g., "JEE Main 2026 Mock Series"
    description = Column(Text, nullable=True)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=True)
    class_id = Column(UUID(as_uuid=True), ForeignKey("classes.id"), nullable=True)
    total_marks = Column(Integer, default=100)
    duration_minutes = Column(Integer, default=60)
    is_active = Column(Boolean, default=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MockTestAttempt(Base):
    """A student's attempt at a mock test in a test series."""
    __tablename__ = "mock_test_attempts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    test_series_id = Column(UUID(as_uuid=True), ForeignKey("test_series.id"), nullable=False, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    marks_obtained = Column(Float, nullable=False)
    total_marks = Column(Float, nullable=False)
    time_taken_minutes = Column(Integer, nullable=True)
    percentile = Column(Float, nullable=True)  # calculated after all attempts
    rank = Column(Integer, nullable=True)       # calculated after all attempts
    created_at = Column(DateTime(timezone=True), server_default=func.now())
