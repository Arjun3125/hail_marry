"""Test Series and Mock Test Attempt models for competitive exam features."""
import uuid
from datetime import datetime
from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from database import Base


class TestSeries(Base):
    """A test series is a collection of mock tests (e.g., 'JEE Main 2026 Series')."""
    __tablename__ = "test_series"
    __table_args__ = (
        CheckConstraint("total_marks > 0", name="ck_test_series_total_marks_positive"),
        CheckConstraint("duration_minutes > 0", name="ck_test_series_duration_minutes_positive"),
    )

    id: Column[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Column[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    name: Column[str] = Column(String(255), nullable=False)  # e.g., "JEE Main 2026 Mock Series"
    description: Column[str] = Column(Text, nullable=True)
    subject_id: Column[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=True)
    class_id: Column[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("classes.id"), nullable=True)
    total_marks: Column[int] = Column(Integer, default=100)
    duration_minutes: Column[int] = Column(Integer, default=60)
    assessment_kind: Column[str] = Column(String(30), nullable=False, default="mock_test")
    grading_mode: Column[str] = Column(String(30), nullable=False, default="manual_review")
    status: Column[str] = Column(String(20), nullable=False, default="draft")
    opens_at: Column[datetime] = Column(DateTime(timezone=True), nullable=True)
    closes_at: Column[datetime] = Column(DateTime(timezone=True), nullable=True)
    published_at: Column[datetime] = Column(DateTime(timezone=True), nullable=True)
    is_active: Column[bool] = Column(Boolean, default=True)
    created_by: Column[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at: Column[datetime] = Column(DateTime(timezone=True), server_default=func.now())


class MockTestAttempt(Base):
    """A student's attempt at a mock test in a test series."""
    __tablename__ = "mock_test_attempts"

    id: Column[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Column[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    test_series_id: Column[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("test_series.id"), nullable=False, index=True)
    student_id: Column[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    marks_obtained = Column(Float, nullable=False)
    total_marks = Column(Float, nullable=False)
    time_taken_minutes: Column[int] = Column(Integer, nullable=True)
    percentile = Column(Float, nullable=True)  # calculated after all attempts
    rank: Column[int] = Column(Integer, nullable=True)       # calculated after all attempts
    created_at: Column[datetime] = Column(DateTime(timezone=True), server_default=func.now())
