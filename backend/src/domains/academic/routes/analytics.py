"""Analytics API endpoints for reports, dashboard data, and exports."""
import logging
from datetime import datetime, timedelta
from typing import Any, cast, Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth.dependencies import require_role
from database import get_db
from src.domains.identity.models.user import User
from src.domains.academic.services.analytics import AttendanceAnalytics, AcademicAnalytics
from src.domains.academic.services.pdf_reporter import PDFReportGenerator
from starlette.responses import StreamingResponse

logger: logging.Logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


def _get_tenant_id(user: User) -> UUID:
    return cast(UUID, user.tenant_id)


# ─── Attendance Analytics ──────────────────────────────────
@router.get("/attendance/student/{student_id}")
async def get_student_attendance(
    student_id: UUID,
    days: int = 30,
    current_user: User = Depends(require_role("teacher", "admin", "parent")),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Get attendance analytics for a student."""
    tenant_id: UUID = _get_tenant_id(current_user)
    data: Dict[str, Any] = AttendanceAnalytics.get_student_attendance_summary(
        db=db,
        tenant_id=tenant_id,
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
) -> Dict[str, Any]:
    """Get attendance analytics for entire class."""
    tenant_id: UUID = _get_tenant_id(current_user)
    data: Dict[str, Any] = AttendanceAnalytics.get_class_attendance_summary(
        db=db,
        tenant_id=tenant_id,
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
) -> Dict[str, Any]:
    """Get daily attendance trend for a class (max 365 days to prevent DOS)."""
    try:
        start: datetime = datetime.fromisoformat(start_date)
        end: datetime = datetime.fromisoformat(end_date) + timedelta(days=1) - timedelta(microseconds=1)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use ISO format: YYYY-MM-DD")

    # Prevent DOS: limit date range to 365 days
    if (end.date() - start.date()).days > 365:
        raise HTTPException(
            status_code=400,
            detail="Date range cannot exceed 365 days. Please select a smaller range.",
        )

    if start > end:
        raise HTTPException(status_code=400, detail="start_date must be before or equal to end_date")

    tenant_id: UUID = _get_tenant_id(current_user)
    data: List[Dict[str, Any]] = AttendanceAnalytics.get_attendance_by_date_range(
        db=db,
        tenant_id=tenant_id,
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
) -> Dict[str, Any]:
    """Get academic performance analytics for a student."""
    tenant_id: UUID = _get_tenant_id(current_user)
    data: Dict[str, Any] = AcademicAnalytics.get_student_performance_summary(
        db=db,
        tenant_id=tenant_id,
        student_id=student_id,
    )
    return {"success": True, "data": data}


@router.get("/academic/class/{class_id}")
async def get_class_performance(
    class_id: UUID,
    current_user: User = Depends(require_role("teacher", "admin")),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Get academic performance analytics for entire class."""
    tenant_id: UUID = _get_tenant_id(current_user)
    data: Dict[str, Any] = AcademicAnalytics.get_class_performance_summary(
        db=db,
        tenant_id=tenant_id,
        class_id=class_id,
    )
    return {"success": True, "data": data}


@router.get("/academic/exam/{exam_id}")
async def get_exam_analysis(
    exam_id: UUID,
    current_user: User = Depends(require_role("teacher", "admin")),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Get detailed analysis for a specific exam."""
    tenant_id: UUID = _get_tenant_id(current_user)
    data: Dict[str, Any] = AcademicAnalytics.get_exam_analysis(
        db=db,
        tenant_id=tenant_id,
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
) -> StreamingResponse:
    """Export student report as PDF."""
    try:
        tenant_id: UUID = _get_tenant_id(current_user)
        generator = PDFReportGenerator()
        pdf_bytes: bytes = generator.generate_student_report(
            db=db,
            tenant_id=tenant_id,
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
) -> StreamingResponse:
    """Export class report as PDF."""
    try:
        tenant_id: UUID = _get_tenant_id(current_user)
        generator = PDFReportGenerator()
        pdf_bytes: bytes = generator.generate_class_report(
            db=db,
            tenant_id=tenant_id,
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
