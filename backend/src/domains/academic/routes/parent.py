"""Parent-facing API routes."""
from uuid import UUID
from pydantic import BaseModel

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
    build_parent_results_response as _build_parent_results_response_impl,
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
from src.domains.academic.services.parent_ai_notifications import (
    ParentAIInsightNotificationService,
)
from src.domains.academic.services.parent_notification_service import (
    ParentNotificationService,
)
from src.domains.identity.models.user import User
from src.domains.identity.models.tenant import Tenant
from src.domains.platform.models.ai import AIQuery
from src.domains.platform.models.generated_content import GeneratedContent
from src.domains.platform.models.study_session import StudySession

router = APIRouter(prefix="/api/parent", tags=["Parent"])


# ─── Pydantic Models ────────────────────────────────────────

class NotificationPreferencesRequest(BaseModel):
    """Request model for updating notification preferences."""
    whatsapp_enabled: bool | None = None
    sms_enabled: bool | None = None
    email_enabled: bool | None = None
    push_enabled: bool | None = None
    in_app_enabled: bool | None = None
    quiet_hours_start: str | None = None  # "22:00" format
    quiet_hours_end: str | None = None    # "07:00" format
    category_overrides: dict | None = None  # {"assignment_reminder": false}


class NotificationPreferencesResponse(BaseModel):
    """Response model for notification preferences."""
    whatsapp_enabled: bool
    sms_enabled: bool
    email_enabled: bool
    push_enabled: bool
    in_app_enabled: bool
    quiet_hours_start: str | None
    quiet_hours_end: str | None
    category_overrides: dict | None

    class Config:
        from_attributes = True


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
        study_session_model=StudySession,
        ai_query_model=AIQuery,
        generated_content_model=GeneratedContent,
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
    return _build_parent_results_response_impl(
        db=db,
        current_user=current_user,
        child=child,
        mark_model=Mark,
        exam_model=Exam,
        subject_model=Subject,
    )


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
        assignment_submission_model=AssignmentSubmission,
        study_session_model=StudySession,
        ai_query_model=AIQuery,
        generated_content_model=GeneratedContent,
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


# ─── AI Learning Insights for Parents ────────────────────────

@router.get("/ai-insights")
async def parent_ai_insights(
    child_id: str | None = None,
    days: int = 7,
    current_user: User = Depends(require_role("parent")),
    db: Session = Depends(get_db),
):
    """
    Get AI learning insights about child's recent AI Studio activity.
    Includes study time, engagement, mastery progress, and areas for improvement.
    """
    child = _get_child_for_parent(current_user=current_user, db=db, child_id=child_id)
    
    insights = ParentAIInsightNotificationService.generate_ai_insight_summary(
        db=db,
        child_id=child.id,
        days=days,
    )
    
    if not insights:
        return {
            "total_sessions": 0,
            "total_study_time_hours": 0.0,
            "active_subjects": [],
            "average_engagement": 0.0,
            "recent_topics": [],
            "quiz_count": 0,
            "average_quiz_score": None,
            "topics_to_review": [],
            "period_days": days,
            "message": "No AI learning sessions found in the specified period",
        }
    
    return insights


# ─── Notification Preferences ───────────────────────────────

@router.get("/notification-preferences", response_model=NotificationPreferencesResponse)
async def get_notification_preferences(
    current_user: User = Depends(require_role("parent")),
    db: Session = Depends(get_db),
):
    """
    Get parent's notification preferences (channels, quiet hours, category toggles).
    """
    tenant_id = current_user.tenant_id
    
    prefs = ParentNotificationService.get_or_create_preferences(
        db=db,
        tenant_id=tenant_id,
        parent_id=current_user.id,
    )
    
    return NotificationPreferencesResponse.model_validate(prefs)


@router.put("/notification-preferences", response_model=NotificationPreferencesResponse)
async def update_notification_preferences(
    request: NotificationPreferencesRequest,
    current_user: User = Depends(require_role("parent")),
    db: Session = Depends(get_db),
):
    """
    Update parent's notification preferences.
    
    Example:
        {
            "whatsapp_enabled": true,
            "email_enabled": false,
            "quiet_hours_start": "22:00",
            "quiet_hours_end": "07:00",
            "category_overrides": {
                "assignment_reminder": true,
                "low_attendance": true,
                "assessment_results": false
            }
        }
    """
    tenant_id = current_user.tenant_id
    
    # Filter out None values for updating only provided fields
    update_data = {k: v for k, v in request.model_dump().items() if v is not None}
    
    prefs = ParentNotificationService.update_preferences(
        db=db,
        tenant_id=tenant_id,
        parent_id=current_user.id,
        **update_data,
    )
    
    return NotificationPreferencesResponse.model_validate(prefs)

