"""Parent-facing API routes."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import Response as StarletteResponse

from auth.dependencies import require_role
from database import get_db
from src.domains.academic.application.parent_portal import (
    build_parent_attendance_response as _build_parent_attendance_response_impl,
    build_parent_audio_report_response as _build_parent_audio_report_response_impl,
    build_parent_dashboard_response as _build_parent_dashboard_response_impl,
    build_parent_digest_preview_response as _build_parent_digest_preview_response_impl,
    build_parent_report_card_payload as _build_parent_report_card_payload_impl,
    build_parent_reports_response as _build_parent_reports_response_impl,
    get_child_for_parent as _get_child_for_parent_impl,
    get_child_results as _get_child_results_impl,
)
from src.domains.academic.models.core import Enrollment, Subject, Class
from src.domains.academic.models.assignment import Assignment, AssignmentSubmission
from src.domains.academic.models.attendance import Attendance
from src.domains.academic.models.marks import Exam, Mark
from src.domains.academic.models.parent_link import ParentLink
from src.domains.academic.models.timetable import Timetable
from src.domains.academic.services.digest_email import (
    generate_digest,
    render_digest_html,
)
from src.domains.academic.services.report_card import generate_report_card_pdf
from src.domains.identity.models.user import User
from src.domains.identity.models.tenant import Tenant

router = APIRouter(prefix="/api/parent", tags=["Parent"])


def _parse_uuid(value: str, field_name: str) -> UUID:
    try:
        return UUID(str(value))
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail=f"Invalid {field_name}")


def _get_child_for_parent(
    current_user: User,
    db: Session,
    child_id: str | None = None,
) -> User:
    return _get_child_for_parent_impl(
        current_user=current_user,
        db=db,
        child_id=child_id,
        parent_link_model=ParentLink,
        user_model=User,
        parse_uuid_fn=_parse_uuid,
    )


def _get_child_results(db: Session, tenant_id, child_id) -> list[dict]:
    return _get_child_results_impl(
        db=db,
        tenant_id=tenant_id,
        child_id=child_id,
        mark_model=Mark,
        exam_model=Exam,
        subject_model=Subject,
    )


@router.get("/dashboard")
async def parent_dashboard(
    child_id: str | None = None,
    current_user: User = Depends(require_role("parent")),
    db: Session = Depends(get_db),
):
    child = _get_child_for_parent(current_user=current_user, db=db, child_id=child_id)
    return _build_parent_dashboard_response_impl(
        db=db,
        current_user=current_user,
        child=child,
        enrollment_model=Enrollment,
        class_model=Class,
        subject_model=Subject,
        attendance_model=Attendance,
        mark_model=Mark,
        exam_model=Exam,
        assignment_model=Assignment,
        assignment_submission_model=AssignmentSubmission,
        timetable_model=Timetable,
    )


@router.get("/attendance")
async def parent_attendance(
    child_id: str | None = None,
    current_user: User = Depends(require_role("parent")),
    db: Session = Depends(get_db),
):
    child = _get_child_for_parent(current_user=current_user, db=db, child_id=child_id)
    return _build_parent_attendance_response_impl(
        db=db,
        current_user=current_user,
        child=child,
        attendance_model=Attendance,
    )


@router.get("/results")
async def parent_results(
    child_id: str | None = None,
    current_user: User = Depends(require_role("parent")),
    db: Session = Depends(get_db),
):
    child = _get_child_for_parent(current_user=current_user, db=db, child_id=child_id)
    return _get_child_results(db=db, tenant_id=current_user.tenant_id, child_id=child.id)


@router.get("/reports")
async def parent_reports(
    child_id: str | None = None,
    current_user: User = Depends(require_role("parent")),
    db: Session = Depends(get_db),
):
    child = _get_child_for_parent(current_user=current_user, db=db, child_id=child_id)
    return _build_parent_reports_response_impl(
        db=db,
        current_user=current_user,
        child=child,
        attendance_model=Attendance,
        mark_model=Mark,
        exam_model=Exam,
        subject_model=Subject,
    )


@router.get("/audio-report")
async def parent_audio_report(
    child_id: str | None = None,
    current_user: User = Depends(require_role("parent")),
    db: Session = Depends(get_db),
):
    """Generate a text summary of child's progress for browser TTS playback."""
    child = _get_child_for_parent(current_user=current_user, db=db, child_id=child_id)
    return _build_parent_audio_report_response_impl(
        db=db,
        current_user=current_user,
        child=child,
        attendance_model=Attendance,
        mark_model=Mark,
        exam_model=Exam,
        subject_model=Subject,
    )


# ─── Weekly Digest Preview ──────────────────────────────────

@router.get("/digest-preview")
async def parent_digest_preview(
    current_user: User = Depends(require_role("parent")),
    db: Session = Depends(get_db),
):
    """Preview the weekly digest email that would be sent to this parent."""
    return _build_parent_digest_preview_response_impl(
        db=db,
        current_user=current_user,
        generate_digest_fn=generate_digest,
        render_digest_html_fn=render_digest_html,
    )


# ─── Report Card PDF ────────────────────────────────────────

@router.get("/report-card")
async def parent_report_card(
    current_user: User = Depends(require_role("parent")),
    db: Session = Depends(get_db),
):
    """Download the report card PDF for the parent's linked child."""
    pdf_bytes, filename = _build_parent_report_card_payload_impl(
        db=db,
        current_user=current_user,
        parent_link_model=ParentLink,
        tenant_model=Tenant,
        generate_report_card_pdf_fn=generate_report_card_pdf,
    )

    return StarletteResponse(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
