"""Analytics API endpoints for reports, dashboard data, and exports."""
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth.dependencies import require_role
from database import get_db
from src.domains.identity.models.user import User
from src.domains.academic.services.analytics import AttendanceAnalytics, AcademicAnalytics
from src.domains.academic.services.pdf_reporter import PDFReportGenerator
from starlette.responses import StreamingResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


# ─── Attendance Analytics ──────────────────────────────────
@router.get("/attendance/student/{student_id}")
async def get_student_attendance(
    student_id: UUID,
    days: int = 30,
    current_user: User = Depends(require_role("teacher", "admin", "parent")),
    db: Session = Depends(get_db),
):
    """Get attendance analytics for a student."""
    data = AttendanceAnalytics.get_student_attendance_summary(
        db=db,
        tenant_id=current_user.tenant_id,
        student_id=student_id,
        days=days,
    )
    return {"success": True, "data": data}


@router.get("/attendance/class/{class_id}")
async def get_class_attendance(
    class_id: UUID,
    days: int = 30,
    current_user: User = Depends(require_role("teacher", "admin")),
    db: Session = Depends(get_db),
):
    """Get attendance analytics for entire class."""
    data = AttendanceAnalytics.get_class_attendance_summary(
        db=db,
        tenant_id=current_user.tenant_id,
        class_id=class_id,
        days=days,
    )
    return {"success": True, "data": data}


@router.get("/attendance/trend/{class_id}")
async def get_class_attendance_trend(
    class_id: UUID,
    start_date: str,  # ISO format: 2026-04-01
    end_date: str,    # ISO format: 2026-04-30
    current_user: User = Depends(require_role("teacher", "admin")),
    db: Session = Depends(get_db),
):
    """Get daily attendance trend for a class."""
    from datetime import datetime
    
    try:
        start = datetime.fromisoformat(start_date).date()
        end = datetime.fromisoformat(end_date).date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use ISO format: YYYY-MM-DD")

    data = AttendanceAnalytics.get_attendance_by_date_range(
        db=db,
        tenant_id=current_user.tenant_id,
        class_id=class_id,
        start_date=start,
        end_date=end,
    )
    return {"success": True, "data": data}


# ─── Academic Analytics ───────────────────────────────────
@router.get("/academic/student/{student_id}")
async def get_student_performance(
    student_id: UUID,
    current_user: User = Depends(require_role("teacher", "admin", "parent")),
    db: Session = Depends(get_db),
):
    """Get academic performance analytics for a student."""
    data = AcademicAnalytics.get_student_performance_summary(
        db=db,
        tenant_id=current_user.tenant_id,
        student_id=student_id,
    )
    return {"success": True, "data": data}


@router.get("/academic/class/{class_id}")
async def get_class_performance(
    class_id: UUID,
    current_user: User = Depends(require_role("teacher", "admin")),
    db: Session = Depends(get_db),
):
    """Get academic performance analytics for entire class."""
    data = AcademicAnalytics.get_class_performance_summary(
        db=db,
        tenant_id=current_user.tenant_id,
        class_id=class_id,
    )
    return {"success": True, "data": data}


@router.get("/academic/exam/{exam_id}")
async def get_exam_analysis(
    exam_id: UUID,
    current_user: User = Depends(require_role("teacher", "admin")),
    db: Session = Depends(get_db),
):
    """Get detailed analysis for a specific exam."""
    data = AcademicAnalytics.get_exam_analysis(
        db=db,
        tenant_id=current_user.tenant_id,
        exam_id=exam_id,
    )
    if not data:
        raise HTTPException(status_code=404, detail="Exam not found")
    return {"success": True, "data": data}


# ─── PDF Reports ──────────────────────────────────────────
@router.get("/report/student/{student_id}/pdf")
async def export_student_report_pdf(
    student_id: UUID,
    include_attendance: bool = True,
    include_academics: bool = True,
    current_user: User = Depends(require_role("admin", "parent")),
    db: Session = Depends(get_db),
):
    """Export student report as PDF."""
    try:
        generator = PDFReportGenerator()
        pdf_bytes = generator.generate_student_report(
            db=db,
            tenant_id=current_user.tenant_id,
            student_id=student_id,
            include_attendance=include_attendance,
            include_academics=include_academics,
        )

        if not pdf_bytes:
            raise HTTPException(status_code=404, detail="Student not found or no data available")

        return StreamingResponse(
            iter([pdf_bytes]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=student_report_{student_id}.pdf"},
        )
    except Exception as e:
        logger.error(f"Failed to generate student PDF: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF report")


@router.get("/report/class/{class_id}/pdf")
async def export_class_report_pdf(
    class_id: UUID,
    include_attendance: bool = True,
    include_academics: bool = True,
    current_user: User = Depends(require_role("admin", "teacher")),
    db: Session = Depends(get_db),
):
    """Export class report as PDF."""
    try:
        generator = PDFReportGenerator()
        pdf_bytes = generator.generate_class_report(
            db=db,
            tenant_id=current_user.tenant_id,
            class_id=class_id,
            include_attendance=include_attendance,
            include_academics=include_academics,
        )

        if not pdf_bytes:
            raise HTTPException(status_code=404, detail="Class not found or no data available")

        return StreamingResponse(
            iter([pdf_bytes]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=class_report_{class_id}.pdf"},
        )
    except Exception as e:
        logger.error(f"Failed to generate class PDF: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF report")
