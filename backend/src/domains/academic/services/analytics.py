"""Analytics service for generating reports and insights on student performance, attendance, and engagement."""
import logging
from datetime import date, datetime, timedelta
from typing import Any, cast, Dict, List, Optional
from uuid import UUID

from sqlalchemy import and_
from sqlalchemy.orm import Session

from constants import GRADE_A_THRESHOLD, GRADE_B_THRESHOLD, GRADE_C_THRESHOLD, GRADE_D_THRESHOLD
from src.domains.academic.models.attendance import Attendance
from src.domains.academic.models.marks import Mark, Exam
from src.domains.academic.models.core import Enrollment
from src.domains.identity.models.user import User

logger: logging.Logger = logging.getLogger(__name__)


class AttendanceAnalytics:
    """Analyze attendance patterns and generate attendance insights."""

    @staticmethod
    def get_student_attendance_summary(
        db: Session, tenant_id: UUID, student_id: UUID, days: int = 30
    ) -> Dict[str, Any]:
        """Get attendance summary for a student over N days.

        Returns:
            {
                "student_id": "<uuid>",
                "total_days": 20,
                "present": 18,
                "absent": 2,
                "late": 0,
                "percentage": 90.0,
                "trend": "improving"  # or "stable" or "declining"
            }
        """
        cutoff_date: datetime = datetime.now() - timedelta(days=days)

        records: List[Any] = (
            db.query(Attendance)
            .filter(
                and_(
                    cast(Any, Attendance.student_id) == student_id,
                    cast(Any, Attendance.tenant_id) == tenant_id,
                    getattr(Attendance, "date") >= cutoff_date,
                )
            )
            .all()
        )

        total: int = len(records)
        present: int = sum(1 for r in records if cast(str, r.status) == "present")
        absent: int = sum(1 for r in records if cast(str, r.status) == "absent")
        late: int = sum(1 for r in records if cast(str, r.status) == "late")

        percentage: float | int = (present / total * 100) if total > 0 else 0

        mid_point: int = total // 2
        first_half_present: int = sum(1 for r in records[:mid_point] if cast(str, r.status) == "present")
        second_half_present: int = sum(1 for r in records[mid_point:] if cast(str, r.status) == "present")

        first_half_pct: float | int = (first_half_present / mid_point * 100) if mid_point > 0 else 0
        second_half_pct: float | int = (second_half_present / (total - mid_point) * 100) if (total - mid_point) > 0 else 0

        if second_half_pct > first_half_pct + 5:
            trend = "improving"
        elif second_half_pct < first_half_pct - 5:
            trend = "declining"
        else:
            trend = "stable"

        return {
            "student_id": str(student_id),
            "total_days": total,
            "present": present,
            "absent": absent,
            "late": late,
            "percentage": round(percentage, 2),
            "trend": trend,
        }

    @staticmethod
    def get_class_attendance_summary(
        db: Session, tenant_id: UUID, class_id: UUID, days: int = 30
    ) -> Dict[str, Any]:
        """Get attendance summary for entire class.

        Returns:
            {
                "class_id": "<uuid>",
                "total_students": 45,
                "average_percentage": 88.5,
                "absent_today": 3,
                "students": [
                    {"student_id": "...", "name": "...", "percentage": 90.0, "status": "present"},
                    ...
                ]
            }
        """
        enrollments: List[Any] = db.query(Enrollment).filter(Enrollment.class_id == class_id).all()
        student_ids: List[UUID] = [cast(UUID, e.student_id) for e in enrollments]

        if not student_ids:
            return {"class_id": str(class_id), "total_students": 0, "average_percentage": 0, "absent_today": 0, "students": []}

        cutoff_date: datetime = datetime.now() - timedelta(days=days)
        today: date = datetime.now().date()

        records: List[Any] = (
            db.query(Attendance)
            .filter(
                and_(
                    cast(Any, Attendance.student_id).in_(student_ids),
                    cast(Any, Attendance.tenant_id) == tenant_id,
                    getattr(Attendance, "date") >= cutoff_date,
                )
            )
            .all()
        )

        today_records: List[Any] = [r for r in records if cast(date, r.date) == today]
        absent_today: int = sum(1 for r in today_records if cast(str, r.status) == "absent")

        students: List[Any] = db.query(User).filter(cast(Any, User.id).in_(student_ids)).all()
        students_by_id: Dict[UUID, User] = {cast(UUID, s.id): s for s in students}

        student_stats: List[Dict[str, Any]] = []
        for student_id in student_ids:
            student_records: List[Any] = [r for r in records if cast(UUID, r.student_id) == student_id]
            total_student: int = len(student_records)
            present_student: int = sum(1 for r in student_records if cast(str, r.status) == "present")
            percentage: float | int = (present_student / total_student * 100) if total_student > 0 else 0

            today_status: Optional[str] = None
            today_record: Optional[Any] = next((r for r in today_records if cast(UUID, r.student_id) == student_id), None)
            if today_record:
                today_status = cast(str, today_record.status)

            student: Optional[User] = students_by_id.get(student_id)
            student_stats.append({
                "student_id": str(student_id),
                "name": student.full_name if student else "Unknown",
                "percentage": round(percentage, 2),
                "status_today": today_status,
            })

        total_percentage: float = sum(item["percentage"] for item in student_stats)
        average: float | int = total_percentage / len(student_stats) if student_stats else 0

        return {
            "class_id": str(class_id),
            "total_students": len(student_ids),
            "average_percentage": round(average, 2),
            "absent_today": absent_today,
            "students": sorted(student_stats, key=lambda item: item["percentage"], reverse=True),
        }

    @staticmethod
    def get_attendance_by_date_range(
        db: Session, tenant_id: UUID, class_id: UUID, start_date: datetime, end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Get daily attendance stats for a class over a date range.

        Returns:
            [
                {"date": "2026-04-11", "total": 45, "present": 43, "absent": 2, "late": 0},
                ...
            ]
        """
        enrollments: List[Any] = db.query(Enrollment).filter(Enrollment.class_id == class_id).all()
        student_ids: List[UUID] = [cast(UUID, e.student_id) for e in enrollments]

        if not student_ids:
            return []

        records: List[Any] = (
            db.query(Attendance)
            .filter(
                and_(
                    cast(Any, Attendance.student_id).in_(student_ids),
                    cast(Any, Attendance.tenant_id) == tenant_id,
                    getattr(Attendance, "date") >= start_date,
                    getattr(Attendance, "date") <= end_date,
                )
            )
            .order_by(getattr(Attendance, "date"))
            .all()
        )

        date_stats: Dict[str, Dict[str, int]] = {}
        for record in records:
            date_str = cast(date, record.date).isoformat()
            if date_str not in date_stats:
                date_stats[date_str] = {"present": 0, "absent": 0, "late": 0}
            date_stats[date_str][cast(str, record.status)] += 1

        result: List[Dict[str, Any]] = []
        for date_str in sorted(date_stats.keys()):
            stats: Dict[str, int] = date_stats[date_str]
            total: int = stats["present"] + stats["absent"] + stats["late"]
            result.append({
                "date": date_str,
                "total": total,
                "present": stats["present"],
                "absent": stats["absent"],
                "late": stats["late"],
            })

        return result


class AcademicAnalytics:
    """Analyze academic performance, marks, and exam results."""

    @staticmethod
    def get_student_performance_summary(
        db: Session, tenant_id: UUID, student_id: UUID
    ) -> Dict[str, Any]:
        """Get academic performance summary for a student.

        Returns:
            {
                "student_id": "<uuid>",
                "total_exams": 5,
                "average_score": 78.5,
                "highest_score": 92,
                "lowest_score": 65,
                "subjects": [
                    {"subject": "Math", "average": 82.0, "exams": 3},
                    ...
                ]
            }
        """
        marks: List[Any] = (
            db.query(Mark)
            .filter(
                and_(
                    cast(Any, Mark.student_id) == student_id,
                    cast(Any, Mark.tenant_id) == tenant_id,
                )
            )
            .all()
        )

        if not marks:
            return {
                "student_id": str(student_id),
                "total_exams": 0,
                "average_score": 0,
                "highest_score": 0,
                "lowest_score": 0,
                "subjects": [],
            }

        scores: List[int] = [cast(int, m.score) for m in marks]
        total_exams: int = len(marks)
        average: float | int = sum(scores) / total_exams if total_exams > 0 else 0
        highest: int = max(scores) if scores else 0
        lowest: int = min(scores) if scores else 0

        subject_stats: Dict[str, List[int]] = {}
        for mark in marks:
            exam = getattr(mark, "exam", None)
            if exam and getattr(exam, "subject", None):
                subject_name = cast(str, exam.subject.name)
                subject_stats.setdefault(subject_name, []).append(cast(int, mark.score))

        subjects: List[Dict[str, Any]] = []
        for subject_name, scores_list in subject_stats.items():
            avg: float = sum(scores_list) / len(scores_list)
            subjects.append({
                "subject": subject_name,
                "average": round(avg, 2),
                "exams": len(scores_list),
            })

        return {
            "student_id": str(student_id),
            "total_exams": total_exams,
            "average_score": round(average, 2),
            "highest_score": highest,
            "lowest_score": lowest,
            "subjects": sorted(subjects, key=lambda item: item["average"], reverse=True),
        }

    @staticmethod
    def get_class_performance_summary(
        db: Session, tenant_id: UUID, class_id: UUID
    ) -> Dict[str, Any]:
        """Get academic performance summary for entire class.

        Returns:
            {
                "class_id": "<uuid>",
                "total_students": 45,
                "average_score": 76.5,
                "top_performers": [...],
                "bottom_performers": [...],
                "by_subject": [...]
            }
        """
        enrollments: List[Any] = db.query(Enrollment).filter(Enrollment.class_id == class_id).all()
        student_ids: List[UUID] = [cast(UUID, e.student_id) for e in enrollments]

        if not student_ids:
            return {"class_id": str(class_id), "total_students": 0, "average_score": 0, "top_performers": []}

        marks: List[Any] = (
            db.query(Mark)
            .filter(
                and_(
                    cast(Any, Mark.student_id).in_(student_ids),
                    cast(Any, Mark.tenant_id) == tenant_id,
                )
            )
            .all()
        )

        if not marks:
            return {"class_id": str(class_id), "total_students": len(student_ids), "average_score": 0, "top_performers": []}

        students: List[Any] = db.query(User).filter(cast(Any, User.id).in_(student_ids)).all()
        students_by_id: Dict[UUID, User] = {cast(UUID, s.id): s for s in students}

        student_scores: Dict[UUID, List[int]] = {}
        student_names: Dict[UUID, str] = {}
        for mark in marks:
            student_id = cast(UUID, mark.student_id)
            student_scores.setdefault(student_id, []).append(cast(int, mark.score))
            if student_id not in student_names:
                student: Optional[User] = students_by_id.get(student_id)
                student_names[student_id] = student.full_name if student else "Unknown"

        performer_stats: List[Dict[str, Any]] = []
        for student_id, scores in student_scores.items():
            avg: float = sum(scores) / len(scores) if scores else 0
            performer_stats.append({
                "student_id": str(student_id),
                "name": student_names.get(student_id, "Unknown"),
                "average": round(avg, 2),
                "exams": len(scores),
            })

        performer_stats.sort(key=lambda item: item["average"], reverse=True)

        class_average: float | int = sum(p["average"] for p in performer_stats) / len(performer_stats) if performer_stats else 0

        return {
            "class_id": str(class_id),
            "total_students": len(student_ids),
            "average_score": round(class_average, 2),
            "top_performers": performer_stats[:5],
            "bottom_performers": performer_stats[-5:] if len(performer_stats) > 5 else performer_stats,
        }

    @staticmethod
    def get_exam_analysis(
        db: Session, tenant_id: UUID, exam_id: UUID
    ) -> Dict[str, Any]:
        """Get detailed analysis of exam results.

        Returns:
            {
                "exam_id": "<uuid>",
                "exam_name": "Math Final",
                "total_students": 45,
                "average_score": 78.5,
                "median_score": 79,
                "highest_score": 98,
                "lowest_score": 45,
                "grade_distribution": {"A": 10, "B": 20, "C": 10, "D": 4, "F": 1},
                "performance_distribution": [...]
            }
        """
        exam: Optional[Exam] = db.query(Exam).filter(Exam.id == exam_id).first()
        if not exam:
            return {}

        marks: List[Any] = db.query(Mark).filter(cast(Any, Mark.exam_id) == exam_id).all()

        if not marks:
            return {
                "exam_id": str(exam_id),
                "exam_name": cast(str, exam.name),
                "total_students": 0,
                "average_score": 0,
                "median_score": 0,
                "highest_score": 0,
                "lowest_score": 0,
                "grade_distribution": {},
            }

        scores: List[int] = [cast(int, m.score) for m in marks]
        scores.sort()

        total: int = len(scores)
        average: float = sum(scores) / total
        median: int = scores[total // 2] if total > 0 else 0
        highest: int = max(scores)
        lowest: int = min(scores)

        grades: Dict[str, int] = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
        for score in scores:
            if score >= GRADE_A_THRESHOLD:
                grades["A"] += 1
            elif score >= GRADE_B_THRESHOLD:
                grades["B"] += 1
            elif score >= GRADE_C_THRESHOLD:
                grades["C"] += 1
            elif score >= GRADE_D_THRESHOLD:
                grades["D"] += 1
            else:
                grades["F"] += 1

        bins: Dict[str, int] = {
            "0-10": 0,
            "10-20": 0,
            "20-30": 0,
            "30-40": 0,
            "40-50": 0,
            "50-60": 0,
            "60-70": 0,
            "70-80": 0,
            "80-90": 0,
            "90-100": 0,
        }
        for score in scores:
            bin_start = (score // 10) * 10
            bin_key: str = f"{bin_start}-{bin_start + 10}"
            if bin_key in bins:
                bins[bin_key] += 1

        return {
            "exam_id": str(exam_id),
            "exam_name": cast(str, exam.name),
            "total_students": total,
            "average_score": round(average, 2),
            "median_score": median,
            "highest_score": highest,
            "lowest_score": lowest,
            "grade_distribution": grades,
            "performance_distribution": [{"range": k, "count": v} for k, v in bins.items()],
        }
