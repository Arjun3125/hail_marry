"""Analytics service for generating reports and insights on student performance, attendance, and engagement."""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple
from uuid import UUID

from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.domains.academic.models.attendance import Attendance
from src.domains.academic.models.marks import Mark, Exam
from src.domains.academic.models.core import Enrollment
from src.domains.identity.models.user import User

logger = logging.getLogger(__name__)


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
        cutoff_date = datetime.now() - timedelta(days=days)

        # Query attendance records
        records = (
            db.query(Attendance)
            .filter(
                and_(
                    Attendance.student_id == student_id,
                    Attendance.tenant_id == tenant_id,
                    Attendance.date >= cutoff_date,
                )
            )
            .all()
        )

        total = len(records)
        present = sum(1 for r in records if r.status == "present")
        absent = sum(1 for r in records if r.status == "absent")
        late = sum(1 for r in records if r.status == "late")

        percentage = (present / total * 100) if total > 0 else 0

        # Determine trend (compare first and second half)
        mid_point = len(records) // 2
        first_half_present = sum(1 for r in records[:mid_point] if r.status == "present")
        second_half_present = sum(1 for r in records[mid_point:] if r.status == "present")

        first_half_pct = (first_half_present / mid_point * 100) if mid_point > 0 else 0
        second_half_pct = (second_half_present / (len(records) - mid_point) * 100) if (len(records) - mid_point) > 0 else 0

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
        # Get all enrolled students
        enrollments = db.query(Enrollment).filter(Enrollment.class_id == class_id).all()
        student_ids = [e.student_id for e in enrollments]

        if not student_ids:
            return {"class_id": str(class_id), "total_students": 0, "average_percentage": 0, "absent_today": 0, "students": []}

        cutoff_date = datetime.now() - timedelta(days=days)
        today = datetime.now().date()

        # Query attendance for all students
        records = (
            db.query(Attendance)
            .filter(
                and_(
                    Attendance.student_id.in_(student_ids),
                    Attendance.tenant_id == tenant_id,
                    Attendance.date >= cutoff_date,
                )
            )
            .all()
        )

        # Count today's absences
        today_records = [r for r in records if r.date == today]
        absent_today = sum(1 for r in today_records if r.status == "absent")

        # Calculate per-student percentages
        student_stats = []
        for student_id in student_ids:
            student_records = [r for r in records if r.student_id == student_id]
            total = len(student_records)
            present = sum(1 for r in student_records if r.status == "present")
            percentage = (present / total * 100) if total > 0 else 0

            today_status = None
            today_record = next((r for r in today_records if r.student_id == student_id), None)
            if today_record:
                today_status = today_record.status

            student = db.query(User).filter(User.id == student_id).first()
            student_stats.append({
                "student_id": str(student_id),
                "name": student.full_name if student else "Unknown",
                "percentage": round(percentage, 2),
                "status_today": today_status,
            })

        # Calculate class average  
        total_percentage = sum(s["percentage"] for s in student_stats)
        average = total_percentage / len(student_stats) if student_stats else 0

        return {
            "class_id": str(class_id),
            "total_students": len(student_ids),
            "average_percentage": round(average, 2),
            "absent_today": absent_today,
            "students": sorted(student_stats, key=lambda x: x["percentage"], reverse=True),
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
        # Get all enrolled students
        enrollments = db.query(Enrollment).filter(Enrollment.class_id == class_id).all()
        student_ids = [e.student_id for e in enrollments]

        if not student_ids:
            return []

        # Query attendance for date range
        records = (
            db.query(Attendance)
            .filter(
                and_(
                    Attendance.student_id.in_(student_ids),
                    Attendance.tenant_id == tenant_id,
                    Attendance.date >= start_date,
                    Attendance.date <= end_date,
                )
            )
            .order_by(Attendance.date)
            .all()
        )

        # Group by date
        date_stats: Dict[str, Dict[str, int]] = {}
        for record in records:
            date_str = record.date.isoformat()
            if date_str not in date_stats:
                date_stats[date_str] = {"present": 0, "absent": 0, "late": 0}
            date_stats[date_str][record.status] += 1

        # Format response
        result = []
        for date_str in sorted(date_stats.keys()):
            stats = date_stats[date_str]
            total = stats["present"] + stats["absent"] + stats["late"]
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
        marks = (
            db.query(Mark)
            .filter(
                and_(
                    Mark.student_id == student_id,
                    Mark.tenant_id == tenant_id,
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

        scores = [m.score for m in marks]
        total_exams = len(marks)
        average = sum(scores) / total_exams if total_exams > 0 else 0
        highest = max(scores) if scores else 0
        lowest = min(scores) if scores else 0

        # Group by subject
        subject_stats: Dict[str, List[int]] = {}
        for mark in marks:
            exam = db.query(Exam).filter(Exam.id == mark.exam_id).first()
            if exam and exam.subject:
                subject_name = exam.subject.name
                if subject_name not in subject_stats:
                    subject_stats[subject_name] = []
                subject_stats[subject_name].append(mark.score)

        subjects = []
        for subject_name, scores_list in subject_stats.items():
            avg = sum(scores_list) / len(scores_list)
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
            "subjects": sorted(subjects, key=lambda x: x["average"], reverse=True),
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
        enrollments = db.query(Enrollment).filter(Enrollment.class_id == class_id).all()
        student_ids = [e.student_id for e in enrollments]

        if not student_ids:
            return {"class_id": str(class_id), "total_students": 0, "average_score": 0, "top_performers": []}

        # Get all marks for students in class
        marks = (
            db.query(Mark)
            .filter(
                and_(
                    Mark.student_id.in_(student_ids),
                    Mark.tenant_id == tenant_id,
                )
            )
            .all()
        )

        if not marks:
            return {"class_id": str(class_id), "total_students": len(student_ids), "average_score": 0, "top_performers": []}

        # Calculate per-student average
        student_scores: Dict[str, List[Tuple[int, str]]] = {}  # student_id -> [(score, name), ...]
        for mark in marks:
            if mark.student_id not in student_scores:
                student = db.query(User).filter(User.id == mark.student_id).first()
                student_scores[mark.student_id] = (student.full_name if student else "Unknown", [])
            student_scores[mark.student_id][1].append(mark.score)

        # Calculate averages and top/bottom performers
        performer_stats = []
        for student_id, (name, scores) in student_scores.items():
            avg = sum(scores) / len(scores) if scores else 0
            performer_stats.append({
                "student_id": str(student_id),
                "name": name,
                "average": round(avg, 2),
                "exams": len(scores),
            })

        performer_stats.sort(key=lambda x: x["average"], reverse=True)

        class_average = sum(p["average"] for p in performer_stats) / len(performer_stats) if performer_stats else 0

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
        exam = db.query(Exam).filter(Exam.id == exam_id).first()
        if not exam:
            return {}

        marks = db.query(Mark).filter(Mark.exam_id == exam_id).all()

        if not marks:
            return {
                "exam_id": str(exam_id),
                "exam_name": exam.name,
                "total_students": 0,
                "average_score": 0,
                "median_score": 0,
                "highest_score": 0,
                "lowest_score": 0,
                "grade_distribution": {},
            }

        scores = [m.score for m in marks]
        scores.sort()

        total = len(scores)
        average = sum(scores) / total
        median = scores[total // 2] if total > 0 else 0
        highest = max(scores)
        lowest = min(scores)

        # Grade distribution (A: 80+, B: 60-79, C: 40-59, D: 20-39, F: 0-19)
        grades = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
        for score in scores:
            if score >= 80:
                grades["A"] += 1
            elif score >= 60:
                grades["B"] += 1
            elif score >= 40:
                grades["C"] += 1
            elif score >= 20:
                grades["D"] += 1
            else:
                grades["F"] += 1

        # Performance bins for histogram
        bins = {
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
            bin_key = f"{(score // 10) * 10}-{(score // 10) * 10 + 10}"
            if bin_key in bins:
                bins[bin_key] += 1

        return {
            "exam_id": str(exam_id),
            "exam_name": exam.name,
            "total_students": total,
            "average_score": round(average, 2),
            "median_score": median,
            "highest_score": highest,
            "lowest_score": lowest,
            "grade_distribution": grades,
            "performance_distribution": [{"range": k, "count": v} for k, v in bins.items()],
        }
