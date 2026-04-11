"""PDF report generation for student reports, attendance summaries, and analytics exports."""
import io
import logging
from datetime import datetime
from uuid import UUID

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    PageBreak,
)
from sqlalchemy.orm import Session

from src.domains.academic.services.analytics import AttendanceAnalytics, AcademicAnalytics
from src.domains.identity.models.user import User
from src.domains.academic.models.core import Class

logger = logging.getLogger(__name__)


class PDFReportGenerator:
    """Generate PDF reports for student performance, attendance, and analytics."""

    def __init__(self, page_size=A4, margin_top=0.5 * inch, margin_bottom=0.5 * inch):
        self.page_size = page_size
        self.margin_top = margin_top
        self.margin_bottom = margin_bottom
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles for reports."""
        self.styles.add(ParagraphStyle(
            name="Title",
            parent=self.styles["Heading1"],
            fontSize=20,
            textColor=colors.HexColor("#1F2937"),
            spaceAfter=12,
            alignment=1,  # Center
        ))

        self.styles.add(ParagraphStyle(
            name="SectionHeader",
            parent=self.styles["Heading2"],
            fontSize=14,
            textColor=colors.HexColor("#374151"),
            spaceAfter=6,
            spaceBefore=6,
        ))

        self.styles.add(ParagraphStyle(
            name="Normal",
            fontSize=10,
            textColor=colors.HexColor("#4B5563"),
        ))

    def generate_student_report(
        self,
        db: Session,
        tenant_id: UUID,
        student_id: UUID,
        include_attendance: bool = True,
        include_academics: bool = True,
    ) -> bytes:
        """Generate comprehensive PDF report for a student.

        Returns:
            PDF bytes ready to save or download
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=self.page_size,
            topMargin=self.margin_top,
            bottomMargin=self.margin_bottom,
        )

        story = []

        # Get student info
        student = db.query(User).filter(User.id == student_id).first()
        if not student:
            logger.error(f"Student {student_id} not found")
            return b""

        # Title
        title = Paragraph("Student Report", self.styles["Title"])
        story.append(title)

        # Student info section
        student_info = [
            ["Name:", student.full_name],
            ["Email:", student.email or "N/A"],
            ["Student ID:", str(student.id)],
            ["Generated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        ]

        info_table = Table(student_info, colWidths=[2 * inch, 4 * inch])
        info_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F3F4F6")),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#1F2937")),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#D1D5DB")),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.3 * inch))

        # Attendance section
        if include_attendance:
            attendance_data = AttendanceAnalytics.get_student_attendance_summary(
                db, tenant_id, student_id, days=30
            )

            story.append(Paragraph("Attendance Summary (Last 30 Days)", self.styles["SectionHeader"]))

            att_content = [
                ["Metric", "Value"],
                ["Total Days", str(attendance_data["total_days"])],
                ["Present", str(attendance_data["present"])],
                ["Absent", str(attendance_data["absent"])],
                ["Late", str(attendance_data["late"])],
                ["Attendance %", f"{attendance_data['percentage']:.1f}%"],
                ["Trend", attendance_data["trend"].capitalize()],
            ]

            att_table = Table(att_content, colWidths=[3 * inch, 3 * inch])
            att_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DBEAFE")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1E40AF")),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
                ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#E5E7EB")),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]))
            story.append(att_table)
            story.append(Spacer(1, 0.3 * inch))

        # Academic performance section
        if include_academics:
            perf_data = AcademicAnalytics.get_student_performance_summary(db, tenant_id, student_id)

            story.append(Paragraph("Academic Performance", self.styles["SectionHeader"]))

            perf_content = [
                ["Metric", "Value"],
                ["Total Exams", str(perf_data.get("total_exams", 0))],
                ["Average Score", f"{perf_data.get('average_score', 0):.1f}"],
                ["Highest Score", str(perf_data.get("highest_score", 0))],
                ["Lowest Score", str(perf_data.get("lowest_score", 0))],
            ]

            perf_table = Table(perf_content, colWidths=[3 * inch, 3 * inch])
            perf_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DCFCE7")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#166534")),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
                ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#E5E7EB")),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]))
            story.append(perf_table)

            # Subject breakdown
            if perf_data.get("subjects"):
                story.append(Spacer(1, 0.2 * inch))
                story.append(Paragraph("Performance by Subject", self.styles["SectionHeader"]))

                subject_content = [["Subject", "Average", "Exams"]]
                for subject in perf_data["subjects"]:
                    subject_content.append([
                        subject["subject"],
                        f"{subject['average']:.1f}",
                        str(subject["exams"]),
                    ])

                subject_table = Table(subject_content, colWidths=[3 * inch, 1.5 * inch, 1.5 * inch])
                subject_table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E0E7FF")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#3730A3")),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
                    ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#E5E7EB")),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ]))
                story.append(subject_table)

        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def generate_class_report(
        self,
        db: Session,
        tenant_id: UUID,
        class_id: UUID,
        include_attendance: bool = True,
        include_academics: bool = True,
    ) -> bytes:
        """Generate comprehensive PDF report for a class.

        Returns:
            PDF bytes ready to save or download
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=self.page_size,
            topMargin=self.margin_top,
            bottomMargin=self.margin_bottom,
        )

        story = []

        # Get class info
        class_obj = db.query(Class).filter(Class.id == class_id).first()
        if not class_obj:
            logger.error(f"Class {class_id} not found")
            return b""

        # Title
        title = Paragraph("Class Report", self.styles["Title"])
        story.append(title)

        # Class info section
        class_info = [
            ["Class:", class_obj.name or "N/A"],
            ["Total Students:", "TBD"],  # Will be added by analytics
            ["Generated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        ]

        info_table = Table(class_info, colWidths=[2 * inch, 4 * inch])
        info_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F3F4F6")),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#1F2937")),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#D1D5DB")),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.3 * inch))

        # Attendance section
        if include_attendance:
            attendance_data = AttendanceAnalytics.get_class_attendance_summary(
                db, tenant_id, class_id, days=30
            )

            story.append(Paragraph("Attendance Summary (Last 30 Days)", self.styles["SectionHeader"]))

            att_content = [
                ["Metric", "Value"],
                ["Total Students", str(attendance_data["total_students"])],
                ["Average Attendance %", f"{attendance_data['average_percentage']:.1f}%"],
                ["Absent Today", str(attendance_data["absent_today"])],
            ]

            att_table = Table(att_content, colWidths=[3 * inch, 3 * inch])
            att_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DBEAFE")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1E40AF")),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
                ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#E5E7EB")),
            ]))
            story.append(att_table)
            story.append(Spacer(1, 0.2 * inch))

            # Top students by attendance
            if attendance_data.get("students"):
                story.append(Paragraph("Student Attendance (Top 10)", self.styles["SectionHeader"]))

                student_content = [["Student Name", "Attendance %", "Status"]]
                for student in attendance_data["students"][:10]:
                    status = student.get("status_today", "N/A")
                    student_content.append([
                        student["name"],
                        f"{student['percentage']:.1f}%",
                        status.capitalize() if status else "N/A",
                    ])

                student_table = Table(student_content, colWidths=[3 * inch, 2 * inch, 1 * inch])
                student_table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F0FDF4")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#15803D")),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
                    ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#E5E7EB")),
                ]))
                story.append(student_table)

        # Academic performance section
        if include_academics:
            perf_data = AcademicAnalytics.get_class_performance_summary(db, tenant_id, class_id)

            story.append(PageBreak())
            story.append(Paragraph("Academic Performance", self.styles["SectionHeader"]))

            perf_content = [
                ["Metric", "Value"],
                ["Average Class Score", f"{perf_data.get('average_score', 0):.1f}"],
                ["Total Students", str(perf_data.get("total_students", 0))],
            ]

            perf_table = Table(perf_content, colWidths=[3 * inch, 3 * inch])
            perf_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DCFCE7")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#166534")),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
                ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#E5E7EB")),
            ]))
            story.append(perf_table)

            # Top performers
            if perf_data.get("top_performers"):
                story.append(Spacer(1, 0.2 * inch))
                story.append(Paragraph("Top Performers", self.styles["SectionHeader"]))

                top_content = [["Rank", "Name", "Average", "Exams"]]
                for i, student in enumerate(perf_data["top_performers"], 1):
                    top_content.append([
                        str(i),
                        student["name"],
                        f"{student['average']:.1f}",
                        str(student["exams"]),
                    ])

                top_table = Table(top_content, colWidths=[0.8 * inch, 3 * inch, 1.2 * inch, 1 * inch])
                top_table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#FEF3C7")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#92400E")),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("ALIGN", (0, 0), (0, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
                    ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#E5E7EB")),
                ]))
                story.append(top_table)

        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
