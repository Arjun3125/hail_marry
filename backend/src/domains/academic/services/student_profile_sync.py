"""Helpers for keeping the unified student profile aligned with core records."""

from __future__ import annotations
from typing import List

from sqlalchemy.orm import Session

from src.domains.academic.models.attendance import Attendance
from src.domains.academic.models.batch import BatchEnrollment
from src.domains.academic.models.core import Enrollment, Subject
from src.domains.academic.models.parent_link import ParentLink
from src.domains.academic.models.performance import SubjectPerformance
from src.domains.academic.models.student_profile import StudentProfile


def _sync_attendance_aggregates(*, db: Session, tenant_id, student_id, profile: StudentProfile) -> None:
    attendance_rows: List[Attendance] = (
        db.query(Attendance)
        .filter(
            Attendance.tenant_id == tenant_id,
            Attendance.student_id == student_id,
        )
        .order_by(Attendance.date.desc(), Attendance.created_at.desc())
        .all()
    )

    total_days: int = len(attendance_rows)
    present_days: int = sum(1 for row in attendance_rows if row.status == "present")
    absent_streak = 0
    for row in attendance_rows:
        if row.status != "absent":
            break
        absent_streak += 1

    profile.total_days = total_days
    profile.present_days = present_days
    profile.attendance_pct = round((present_days / total_days * 100), 2) if total_days > 0 else 0.0
    profile.absent_streak = absent_streak


def _sync_performance_aggregates(*, db: Session, tenant_id, student_id, profile: StudentProfile) -> None:
    performance_rows: List[SubjectPerformance] = (
        db.query(SubjectPerformance)
        .filter(
            SubjectPerformance.tenant_id == tenant_id,
            SubjectPerformance.student_id == student_id,
        )
        .all()
    )
    if not performance_rows:
        profile.overall_score_pct = None
        profile.strongest_subject = None
        profile.weakest_subject = None
        profile.subject_mastery_map = None
        return

    subject_ids = [row.subject_id for row in performance_rows if row.subject_id is not None]
    subjects: List[Subject] = (
        db.query(Subject)
        .filter(
            Subject.tenant_id == tenant_id,
            Subject.id.in_(subject_ids),
        )
        .all()
        if subject_ids
        else []
    )
    subject_name_by_id = {subject.id: subject.name for subject in subjects}

    named_scores: list[tuple[str, float]] = []
    for row in performance_rows:
        subject_name = subject_name_by_id.get(row.subject_id, "Unknown")
        named_scores.append((subject_name, float(row.average_score or 0.0)))

    named_scores.sort(key=lambda item: item[0])
    strongest_subject, _strongest_score = max(named_scores, key=lambda item: item[1])
    weakest_subject, _weakest_score = min(named_scores, key=lambda item: item[1])

    profile.overall_score_pct = round(
        sum(score for _, score in named_scores) / len(named_scores),
        2,
    )
    profile.strongest_subject = strongest_subject
    profile.weakest_subject = weakest_subject
    profile.subject_mastery_map = {
        subject_name: round(score, 2)
        for subject_name, score in named_scores
    }


def sync_student_profile_context(*, db: Session, tenant_id, student_id) -> StudentProfile:
    """Upsert the learner-profile context fields from live enrollment/link records.

    This keeps the shared learner profile usable before the heavier analytics
    layer is introduced. The function is intentionally transaction-friendly:
    it mutates the current session but does not commit.
    """

    profile: StudentProfile | None = db.query(StudentProfile).filter(
        StudentProfile.tenant_id == tenant_id,
        StudentProfile.user_id == student_id,
    ).first()
    if profile is None:
        profile = StudentProfile(
            tenant_id=tenant_id,
            user_id=student_id,
        )
        db.add(profile)

    enrollment: Enrollment | None = db.query(Enrollment).filter(
        Enrollment.tenant_id == tenant_id,
        Enrollment.student_id == student_id,
    ).order_by(Enrollment.created_at.desc()).first()

    batch_enrollment: BatchEnrollment | None = db.query(BatchEnrollment).filter(
        BatchEnrollment.tenant_id == tenant_id,
        BatchEnrollment.student_id == student_id,
        BatchEnrollment.status.in_(("active", "trial")),
    ).order_by(BatchEnrollment.enrolled_at.desc()).first()

    guardian_links: List[ParentLink] = db.query(ParentLink).filter(
        ParentLink.tenant_id == tenant_id,
        ParentLink.child_id == student_id,
    ).order_by(ParentLink.created_at.asc()).all()

    profile.current_class_id = enrollment.class_id if enrollment else None
    profile.current_batch_id = batch_enrollment.batch_id if batch_enrollment else None
    profile.primary_parent_id = guardian_links[0].parent_id if guardian_links else None
    profile.guardian_count = len(guardian_links)
    _sync_attendance_aggregates(
        db=db,
        tenant_id=tenant_id,
        student_id=student_id,
        profile=profile,
    )
    _sync_performance_aggregates(
        db=db,
        tenant_id=tenant_id,
        student_id=student_id,
        profile=profile,
    )

    if hasattr(db, "flush"):
        db.flush()

    return profile
