"""Unified Student Learning Profile — the "one student record" that powers everything.

This model aggregates a student's academic identity into a single queryable
record. It links attendance patterns, subject mastery, learning streaks,
and risk indicators so that teachers, parents, and admins can see a
holistic view of each student without joining across 10+ tables.

Designed for Indian K-12 and tuition center deployments where:
- Parents want a single "Is my child okay?" answer
- Teachers need at-a-glance class readiness
- Admins need risk flags (dropout, fee default, academic decline)
"""
import uuid
from datetime import datetime
from typing import Any
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from database import Base


class StudentProfile(Base):
    """Aggregated learning profile for a student — the "school brain" record.

    Updated by background jobs that scan attendance, marks, reviews, and fees
    to produce a single, queryable snapshot per student.
    """
    __tablename__ = "student_profiles"

    id: Column[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Column[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    user_id: Column[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True, index=True)
    current_class_id: Column[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("classes.id"), nullable=True, index=True)
    current_batch_id: Column[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("batches.id"), nullable=True, index=True)
    primary_parent_id: Column[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    guardian_count: Column[int] = Column(Integer, default=0)

    # ── Attendance aggregates ────────────────────────────────────────
    total_days: Column[int] = Column(Integer, default=0)
    present_days: Column[int] = Column(Integer, default=0)
    attendance_pct = Column(Float, default=0.0)      # Computed: present_days / total_days * 100
    absent_streak: Column[int] = Column(Integer, default=0)        # Consecutive absent days (risk flag)

    # ── Academic aggregates ──────────────────────────────────────────
    overall_score_pct = Column(Float, nullable=True)  # Weighted average across subjects
    strongest_subject: Column[str] = Column(String(100), nullable=True)
    weakest_subject: Column[str] = Column(String(100), nullable=True)
    # Per-subject mastery stored as JSON: {"Maths": 78.5, "Science": 92.0}
    subject_mastery_map: Column[Any] = Column(JSONB, nullable=True)

    # ── Spaced Repetition / Learning streaks ─────────────────────────
    current_streak_days: Column[int] = Column(Integer, default=0)  # Daily learning streak
    longest_streak_days: Column[int] = Column(Integer, default=0)
    total_reviews_completed: Column[int] = Column(Integer, default=0)
    last_review_at: Column[datetime] = Column(DateTime(timezone=True), nullable=True)

    # ── Risk indicators (computed by background jobs) ────────────────
    dropout_risk: Column[str] = Column(String(20), default="low")   # low, medium, high
    academic_risk: Column[str] = Column(String(20), default="low")  # low, medium, high
    fee_risk: Column[str] = Column(String(20), default="low")       # low, medium, high (from fee module)

    # ── Exam readiness ───────────────────────────────────────────────
    exam_readiness_pct = Column(Float, nullable=True)  # AI-computed exam preparedness score
    predicted_score = Column(Float, nullable=True)      # AI-predicted exam score

    # ── Metadata ─────────────────────────────────────────────────────
    last_computed_at: Column[datetime] = Column(DateTime(timezone=True), nullable=True)
    created_at: Column[datetime] = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: Column[datetime] = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
