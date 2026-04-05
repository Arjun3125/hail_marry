"""
Subject Performance Cron Job
Computes average scores per student per subject and updates the subject_performance table.
Run via: python -m scripts.compute_performance
Or schedule via cron: 0 2 * * * cd /app && python -m scripts.compute_performance
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import func
from sqlalchemy.orm import Session
from database import SessionLocal
from src.domains.academic.models.marks import Mark, Exam
from src.domains.academic.models.core import Subject, Enrollment
from src.domains.academic.models.performance import SubjectPerformance
from src.domains.identity.models.user import User
from datetime import datetime, timezone


def compute_all_performance():
    """Recompute subject performance for all active students across all tenants."""
    db: Session = SessionLocal()
    try:
        # Get all active students
        students = db.query(User).filter(
            User.role == "student", User.is_active, not User.is_deleted
        ).all()

        updated = 0
        for student in students:
            # Get student's enrollment
            enrollment = db.query(Enrollment).filter(
                Enrollment.student_id == student.id,
                Enrollment.tenant_id == student.tenant_id,
            ).first()
            if not enrollment:
                continue

            # Get subjects for that class
            subjects = db.query(Subject).filter(
                Subject.tenant_id == student.tenant_id,
                Subject.class_id == enrollment.class_id,
            ).all()

            for subject in subjects:
                # Calculate average across all exams for this subject
                result = db.query(
                    func.avg(Mark.marks_obtained * 100.0 / Exam.max_marks).label("avg_pct"),
                    func.count(Mark.id).label("exam_count"),
                ).join(Exam, Mark.exam_id == Exam.id).filter(
                    Mark.student_id == student.id,
                    Mark.tenant_id == student.tenant_id,
                    Exam.subject_id == subject.id,
                ).first()

                avg_score = round(float(result.avg_pct), 1) if result.avg_pct else 0.0
                exam_count = result.exam_count or 0

                if exam_count == 0:
                    continue

                # Upsert into subject_performance
                perf = db.query(SubjectPerformance).filter(
                    SubjectPerformance.student_id == student.id,
                    SubjectPerformance.subject_id == subject.id,
                    SubjectPerformance.tenant_id == student.tenant_id,
                ).first()

                if perf:
                    perf.average_score = avg_score
                    perf.exam_count = exam_count
                    perf.last_updated = datetime.now(timezone.utc)
                else:
                    perf = SubjectPerformance(
                        tenant_id=student.tenant_id,
                        student_id=student.id,
                        subject_id=subject.id,
                        average_score=avg_score,
                        exam_count=exam_count,
                    )
                    db.add(perf)

                updated += 1

        db.commit()
        print(f"✅ Updated {updated} subject performance records for {len(students)} students")

    except Exception as e:
        db.rollback()
        print(f"❌ Error computing performance: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    compute_all_performance()
