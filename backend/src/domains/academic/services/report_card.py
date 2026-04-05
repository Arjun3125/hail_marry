"""Auto-generate PDF report cards for students.

Uses ReportLab for PDF generation with school branding,
attendance summary, subject-wise marks, and teacher comments.
"""
import io
from datetime import date
from sqlalchemy.orm import Session

from constants import (
    compute_grade,
    PDF_PRIMARY_COLOR, PDF_MUTED_COLOR,
)
from src.domains.identity.models.user import User
from src.domains.academic.models.attendance import Attendance
from src.domains.academic.models.marks import Mark, Exam
from src.domains.academic.models.core import Enrollment, Class, Subject


def generate_report_card_pdf(
    db: Session,
    student_id: str,
    tenant_id: str,
    school_name: str = "VidyaOS School",
    academic_year: str = "2025-26",
) -> bytes:
    """Generate a PDF report card for a student.

    Returns raw PDF bytes that can be streamed as a response.
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER

    # ── Fetch student data ──
    student = db.query(User).filter(User.id == student_id, User.tenant_id == tenant_id).first()
    if not student:
        raise ValueError("Student not found")

    # Get enrollment & class
    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == student.id,
        Enrollment.tenant_id == tenant_id,
    ).first()

    class_name = "N/A"
    if enrollment:
        cls = db.query(Class).filter(Class.id == enrollment.class_id).first()
        if cls:
            class_name = cls.name

    # Attendance stats
    total_att = db.query(Attendance).filter(
        Attendance.tenant_id == tenant_id,
        Attendance.student_id == student.id,
    ).count()
    present_att = db.query(Attendance).filter(
        Attendance.tenant_id == tenant_id,
        Attendance.student_id == student.id,
        Attendance.status == "present",
    ).count()
    att_pct = round(present_att / total_att * 100) if total_att > 0 else 0

    # Subject-wise marks
    marks_data = []
    exams = db.query(Exam).filter(Exam.tenant_id == tenant_id).all()
    subject_scores: dict[str, list] = {}
    for exam in exams:
        mark = db.query(Mark).filter(
            Mark.tenant_id == tenant_id,
            Mark.exam_id == exam.id,
            Mark.student_id == student.id,
        ).first()
        if mark:
            subj = db.query(Subject).filter(Subject.id == exam.subject_id).first()
            subj_name = subj.name if subj else "Unknown"
            if subj_name not in subject_scores:
                subject_scores[subj_name] = []
            subject_scores[subj_name].append({
                "exam": exam.name,
                "obtained": mark.marks_obtained,
                "max": exam.max_marks,
            })

    for subj_name, scores in subject_scores.items():
        total_obtained = sum(s["obtained"] for s in scores)
        total_max = sum(s["max"] for s in scores)
        pct = round(total_obtained / total_max * 100) if total_max > 0 else 0
        grade = compute_grade(pct)
        marks_data.append({
            "subject": subj_name,
            "obtained": total_obtained,
            "max": total_max,
            "pct": pct,
            "grade": grade,
        })

    # ── Build PDF ──
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20 * mm, bottomMargin=20 * mm)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle", parent=styles["Title"],
        fontSize=18, alignment=TA_CENTER, spaceAfter=6,
        textColor=colors.HexColor(PDF_PRIMARY_COLOR),
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle", parent=styles["Normal"],
        fontSize=10, alignment=TA_CENTER, spaceAfter=12,
        textColor=colors.HexColor(PDF_MUTED_COLOR),
    )
    heading_style = ParagraphStyle(
        "SectionHeading", parent=styles["Heading2"],
        fontSize=13, spaceAfter=6, spaceBefore=14,
        textColor=colors.HexColor(PDF_PRIMARY_COLOR),
    )
    normal_style = ParagraphStyle(
        "ReportNormal", parent=styles["Normal"],
        fontSize=10, spaceAfter=4,
    )

    elements = []

    # Header
    elements.append(Paragraph(school_name, title_style))
    elements.append(Paragraph(f"Academic Year: {academic_year} | Report Card", subtitle_style))
    elements.append(Spacer(1, 8 * mm))

    # Student info table
    info_data = [
        ["Student Name", student.full_name or student.email],
        ["Class", class_name],
        ["Email", student.email],
        ["Date Generated", date.today().strftime("%d %B %Y")],
    ]
    info_table = Table(info_data, colWidths=[120, 350])
    info_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#374151")),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 6 * mm))

    # Attendance
    elements.append(Paragraph("Attendance Summary", heading_style))
    att_data = [
        ["Total Days", "Present", "Absent", "Percentage"],
        [str(total_att), str(present_att), str(total_att - present_att), f"{att_pct}%"],
    ]
    att_table = Table(att_data, colWidths=[120, 120, 120, 120])
    att_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a5f")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(att_table)
    elements.append(Spacer(1, 6 * mm))

    # Marks table
    if marks_data:
        elements.append(Paragraph("Subject-wise Performance", heading_style))
        marks_header = ["Subject", "Marks Obtained", "Max Marks", "Percentage", "Grade"]
        marks_rows = [marks_header]
        for m in marks_data:
            marks_rows.append([
                m["subject"], str(m["obtained"]), str(m["max"]),
                f"{m['pct']}%", m["grade"],
            ])

        # Overall row
        total_obt = sum(m["obtained"] for m in marks_data)
        total_max = sum(m["max"] for m in marks_data)
        overall_pct = round(total_obt / total_max * 100) if total_max > 0 else 0
        overall_grade = compute_grade(overall_pct)
        marks_rows.append(["OVERALL", str(total_obt), str(total_max), f"{overall_pct}%", overall_grade])

        marks_table = Table(marks_rows, colWidths=[140, 90, 90, 80, 80])
        marks_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a5f")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#f0f9ff")),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
        ]))
        elements.append(marks_table)
    else:
        elements.append(Paragraph("No exam results available yet.", normal_style))

    elements.append(Spacer(1, 12 * mm))

    # Footer
    elements.append(Paragraph(
        "This is a computer-generated report card from VidyaOS.",
        ParagraphStyle("Footer", parent=styles["Normal"], fontSize=8, alignment=TA_CENTER, textColor=colors.grey),
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer.read()
