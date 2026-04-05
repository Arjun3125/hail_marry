"""Student-facing API routes — dashboard, attendance, results, timetable, assignments, lectures, complaints, upload."""
import logging
from typing import Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from config import settings
from database import SessionLocal
from auth.dependencies import require_role
from src.domains.identity.models.user import User
from src.domains.academic.application.student_study_tools import (
    generate_student_study_tool as _generate_student_study_tool_impl,
    generate_student_study_tool_job as _generate_student_study_tool_job_impl,
)
from src.domains.academic.application.student_complaints import (
    create_student_complaint as _create_student_complaint_impl,
    list_student_complaints as _list_student_complaints_impl,
)
from src.domains.academic.application.student_assignments import (
    list_student_assignments as _list_student_assignments_impl,
)
from src.domains.academic.application.student_dashboard import (
    build_student_dashboard_response as _build_student_dashboard_response_impl,
)
from src.domains.academic.application.student_learning_insights import (
    build_student_weak_topics as _build_student_weak_topics_impl,
    list_student_timetable as _list_student_timetable_impl,
    list_student_uploads as _list_student_uploads_impl,
)
from src.domains.academic.application.student_lectures import (
    list_student_lectures as _list_student_lectures_impl,
)
from src.domains.academic.application.student_reviews import (
    complete_student_review as _complete_student_review_impl,
    create_student_review as _create_student_review_impl,
    list_student_reviews as _list_student_reviews_impl,
)
from src.domains.academic.application.student_submissions import (
    StudentAssignmentSubmissionError as _StudentAssignmentSubmissionError,
    submit_student_assignment as _submit_student_assignment_impl,
)
from src.domains.academic.application.student_quiz_results import (
    StudentQuizResultError as _StudentQuizResultError,
    process_student_quiz_result as _process_student_quiz_result_impl,
)
from src.domains.academic.application.student_engagement import (
    StudentMockTestSubmissionError as _StudentMockTestSubmissionError,
    get_student_streak_overview as _get_student_streak_overview_impl,
    get_student_test_series_leaderboard as _get_student_test_series_leaderboard_impl,
    get_student_test_series_rank as _get_student_test_series_rank_impl,
    get_student_weakness_alerts as _get_student_weakness_alerts_impl,
    list_student_test_series as _list_student_test_series_impl,
    submit_student_mock_test as _submit_student_mock_test_impl,
)
from src.domains.academic.application.student_uploads import (
    StudentUploadError as _StudentUploadError,
    ingest_student_upload as _ingest_student_upload_impl,
)
from src.domains.academic.application.student_results import (
    build_student_result_trends as _build_student_result_trends_impl,
    build_student_results as _build_student_results_impl,
    list_student_attendance as _list_student_attendance_impl,
)
from src.domains.platform.schemas.ai_runtime import StudyToolGenerateRequest
from src.domains.platform.services.ai_gateway import run_study_tool
from src.domains.platform.services.ai_queue import (
    JOB_TYPE_STUDY_TOOL,
    STATUS_COMPLETED,
    _persist_job_state,
    build_public_job_response,
    enqueue_job,
)
from src.domains.platform.services.mastery_tracking_service import (
    get_topic_mastery_snapshot,
    ensure_topic_mastery_seed,
    record_quiz_completion,
    record_review_completion,
    record_study_tool_activity,
)
from src.domains.platform.services.metrics_registry import observe_personalization_event
from src.domains.platform.services.study_path_service import get_active_study_path_for_topic
from src.domains.platform.services.usage_governance import (
    evaluate_governance,
    record_usage_event,
    resolve_upload_metrics,
)
from src.shared.ai_tools.study_tools import (
    extract_json_payload as _extract_json_payload_shared,
    normalize_tool_output as _normalize_tool_output_shared,
)
from src.infrastructure.vector_store.citation_linker import make_citations_clickable
from src.infrastructure.llm.cache import invalidate_tenant_cache
from src.domains.platform.models.ai import AIQuery
from src.domains.academic.models.test_series import TestSeries, MockTestAttempt
from src.domains.academic.services.gamification import get_streak_info, record_login
from src.domains.academic.services.weakness_alerts import generate_weakness_alerts
from src.domains.academic.services.leaderboard import (
    calculate_rankings,
    get_all_series,
    get_leaderboard,
    get_student_rank,
)
from utils.upload_security import (
    UploadValidationError,
    ensure_storage_dir,
    sanitize_docx_bytes,
)
from constants import (
    STUDENT_ALLOWED_EXTENSIONS as STUDENT_ALLOWED_EXTENSIONS_CONST,
    STUDENT_MAX_FILE_SIZE,
)

router = APIRouter(prefix="/api/student", tags=["Student"])

logger = logging.getLogger(__name__)
DEMO_NOTICE = "Demo mode preview. This response is mock content and not grounded in uploaded materials."
DEMO_SOURCES = ["demo-mode"]

UPLOAD_DIR = ensure_storage_dir("uploads")
STUDENT_ALLOWED_EXTENSIONS = STUDENT_ALLOWED_EXTENSIONS_CONST
MAX_FILE_SIZE = STUDENT_MAX_FILE_SIZE
ASSIGNMENT_SUBMISSION_DIR = ensure_storage_dir("uploads", "assignment_submissions")
OCR_OUTPUT_DIR = ensure_storage_dir("uploads", "ocr_output")


class ComplaintCreate(BaseModel):
    category: str = "other"
    description: str


class QuizResultSubmitRequest(BaseModel):
    topic: str
    total_questions: int
    correct_answers: int
    subject_id: Optional[str] = None
    difficulty_breakdown: Optional[dict[str, int]] = None


def _parse_uuid(value: str, field_name: str) -> UUID:
    try:
        return UUID(str(value))
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail=f"Invalid {field_name}")

def _record_mastery_outcome_metrics(
    db: Session,
    *,
    current_user: User,
    topic: str,
    surface: str,
    target: str,
    before_snapshot: dict[str, Any],
    after_snapshot: dict[str, Any],
) -> None:
    before_mastery = float(before_snapshot.get("mastery_score") or 0.0)
    after_mastery = float(after_snapshot.get("mastery_score") or 0.0)
    if after_mastery <= before_mastery:
        return

    observe_personalization_event("mastery_improved", surface=surface, target=target)
    if before_mastery < 60 <= after_mastery:
        observe_personalization_event("mastery_recovered", surface=surface, target=target)

    active_plan = get_active_study_path_for_topic(
        db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        topic=topic,
    )
    if active_plan is None:
        return

    observe_personalization_event("guided_mastery_improved", surface=surface, target=target)
    if before_mastery < 60 <= after_mastery:
        observe_personalization_event("guided_mastery_recovered", surface=surface, target=target)


def _extract_json_payload(text: str) -> Any:
    return _extract_json_payload_shared(text)


def _normalize_tool_output(tool: str, answer: str) -> Any:
    return _normalize_tool_output_shared(tool, answer)


@router.get("/dashboard")
async def student_dashboard(
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    return _build_student_dashboard_response_impl(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
    )


@router.get("/attendance")
async def student_attendance(
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """List student's attendance records."""
    return _list_student_attendance_impl(
        db=db,
        tenant_id=current_user.tenant_id,
        student_id=current_user.id,
    )


@router.get("/results")
async def student_results(
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Get student's exam results grouped by subject."""
    return _build_student_results_impl(
        db=db,
        tenant_id=current_user.tenant_id,
        student_id=current_user.id,
    )


@router.get("/results/trends")
async def student_result_trends(
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Get chronological marks trend by subject for charting."""
    return _build_student_result_trends_impl(
        db=db,
        tenant_id=current_user.tenant_id,
        student_id=current_user.id,
    )


@router.get("/timetable")
async def student_timetable(
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Get student's weekly timetable."""
    return _list_student_timetable_impl(
        db=db,
        tenant_id=current_user.tenant_id,
        student_id=current_user.id,
    )


@router.get("/assignments")
async def student_assignments(
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Get student's assignments with submission status."""
    return _list_student_assignments_impl(
        db=db,
        tenant_id=current_user.tenant_id,
        student_id=current_user.id,
    )


@router.post("/assignments/{assignment_id}/submit")
async def submit_assignment(
    assignment_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Upload or replace student's assignment submission."""
    assignment_uuid = _parse_uuid(assignment_id, "assignment_id")
    try:
        return await _submit_student_assignment_impl(
            db=db,
            tenant_id=current_user.tenant_id,
            student_id=current_user.id,
            assignment_uuid=assignment_uuid,
            file=file,
            allowed_extensions=STUDENT_ALLOWED_EXTENSIONS,
            max_file_size=MAX_FILE_SIZE,
            assignment_submission_dir=ASSIGNMENT_SUBMISSION_DIR,
            sanitize_docx_bytes_fn=sanitize_docx_bytes,
            upload_validation_error_cls=UploadValidationError,
            logger=logger,
        )
    except _StudentAssignmentSubmissionError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail)


@router.get("/lectures")
async def student_lectures(
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """List lectures available to student."""
    return _list_student_lectures_impl(
        db=db,
        tenant_id=current_user.tenant_id,
        student_id=current_user.id,
    )


@router.get("/complaints")
async def student_complaints(
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """List student's complaints."""
    return _list_student_complaints_impl(
        db=db,
        tenant_id=current_user.tenant_id,
        student_id=current_user.id,
    )


@router.post("/complaints")
async def create_complaint(
    data: ComplaintCreate,
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Submit a new complaint."""
    return _create_student_complaint_impl(
        db=db,
        tenant_id=current_user.tenant_id,
        student_id=current_user.id,
        category=data.category,
        description=data.description,
    )


# ─── Student File Upload ────────────────────────────────────
@router.post("/tools/generate")
async def generate_study_tool(
    data: StudyToolGenerateRequest,
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Generate structured study tools from student's grounded materials."""
    topic = data.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="topic is required")
    try:
        return await _generate_student_study_tool_impl(
            db=db,
            current_user=current_user,
            data=data,
            settings_obj=settings,
            demo_notice=DEMO_NOTICE,
            demo_sources=DEMO_SOURCES,
            parse_uuid_fn=_parse_uuid,
            run_study_tool_fn=run_study_tool,
            make_citations_clickable_fn=make_citations_clickable,
            record_usage_event_fn=record_usage_event,
            record_study_tool_activity_fn=record_study_tool_activity,
        )
    except ValueError as exc:
        raise HTTPException(status_code=429, detail=str(exc))


@router.post("/tools/generate/jobs")
async def generate_study_tool_job(
    data: StudyToolGenerateRequest,
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Queue structured study tool generation for worker execution."""
    topic = data.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="topic is required")
    try:
        return await _generate_student_study_tool_job_impl(
            db=db,
            current_user=current_user,
            data=data,
            settings_obj=settings,
            demo_notice=DEMO_NOTICE,
            demo_sources=DEMO_SOURCES,
            parse_uuid_fn=_parse_uuid,
            enqueue_job_fn=enqueue_job,
            session_factory=SessionLocal,
            ai_query_model=AIQuery,
            build_public_job_response_fn=build_public_job_response,
            persist_job_state_fn=_persist_job_state,
            status_completed=STATUS_COMPLETED,
            job_type_study_tool=JOB_TYPE_STUDY_TOOL,
            record_usage_event_fn=record_usage_event,
            record_study_tool_activity_fn=record_study_tool_activity,
        )
    except ValueError as exc:
        raise HTTPException(status_code=429, detail=str(exc))


@router.post("/tools/quiz-results")
async def submit_quiz_result(
    data: QuizResultSubmitRequest,
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Persist quiz performance as mastery evidence for adaptive learning."""
    try:
        return _process_student_quiz_result_impl(
            db=db,
            tenant_id=current_user.tenant_id,
            student_id=current_user.id,
            topic=data.topic,
            total_questions=data.total_questions,
            correct_answers=data.correct_answers,
            subject_id=data.subject_id,
            difficulty_breakdown=data.difficulty_breakdown,
            get_topic_mastery_snapshot_fn=get_topic_mastery_snapshot,
            record_quiz_completion_fn=record_quiz_completion,
            record_mastery_outcome_fn=lambda *, topic, before_snapshot, after_snapshot: _record_mastery_outcome_metrics(
                db,
                current_user=current_user,
                topic=topic,
                surface="quiz_results",
                target="quiz",
                before_snapshot=before_snapshot,
                after_snapshot=after_snapshot,
            ),
        )
    except _StudentQuizResultError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail)


@router.post("/upload")
async def student_upload(
    file: UploadFile = File(...),
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """
    Student uploads study materials (PDF, DOCX, PPTX, XLSX, or OCR images).
    Uploaded files are ingested into the RAG pipeline.
    """
    try:
        return await _ingest_student_upload_impl(
            db=db,
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            file=file,
            allowed_extensions=STUDENT_ALLOWED_EXTENSIONS,
            max_file_size=MAX_FILE_SIZE,
            upload_dir=UPLOAD_DIR,
            ocr_output_dir=OCR_OUTPUT_DIR,
            sanitize_docx_bytes_fn=sanitize_docx_bytes,
            upload_validation_error_cls=UploadValidationError,
            resolve_upload_metrics_fn=resolve_upload_metrics,
            evaluate_governance_fn=evaluate_governance,
            record_usage_event_fn=record_usage_event,
            invalidate_tenant_cache_fn=invalidate_tenant_cache,
            logger=logger,
        )
    except _StudentUploadError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail)


@router.get("/uploads")
async def student_uploads(
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
    page: int = 1,
    page_size: int = 20,
):
    """List files uploaded by this student (paginated)."""
    return _list_student_uploads_impl(
        db=db,
        tenant_id=current_user.tenant_id,
        student_id=current_user.id,
        page=page,
        page_size=page_size,
    )


# ─── Weak Topics ────────────────────────────────────────────
@router.get("/weak-topics")
async def student_weak_topics(
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """
    Get the student's weak topics based on subject_performance.
    Returns subjects where average score < 60%.
    """
    return _build_student_weak_topics_impl(
        db=db,
        tenant_id=current_user.tenant_id,
        student_id=current_user.id,
    )


# ─── Spaced Repetition Reviews ─────────────────────────────

class ReviewCreateRequest(BaseModel):
    topic: str
    subject_id: Optional[str] = None


class ReviewCompleteRequest(BaseModel):
    rating: int  # 1-5 self-assessment quality


@router.get("/reviews")
async def student_reviews(
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Get student's spaced repetition review cards (due and upcoming)."""
    return _list_student_reviews_impl(
        db=db,
        tenant_id=current_user.tenant_id,
        student_id=current_user.id,
    )


@router.post("/reviews")
async def create_review(
    data: ReviewCreateRequest,
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Create a new spaced repetition review card."""
    try:
        return _create_student_review_impl(
            db=db,
            tenant_id=current_user.tenant_id,
            student_id=current_user.id,
            topic=data.topic,
            subject_id=data.subject_id,
            parse_uuid_fn=_parse_uuid,
            ensure_topic_mastery_seed_fn=ensure_topic_mastery_seed,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/reviews/{review_id}/complete")
async def complete_review(
    review_id: str,
    data: ReviewCompleteRequest,
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Mark a review as completed with quality self-rating (SM-2)."""
    try:
        return _complete_student_review_impl(
            db=db,
            tenant_id=current_user.tenant_id,
            student_id=current_user.id,
            review_id=review_id,
            rating=data.rating,
            parse_uuid_fn=_parse_uuid,
            get_topic_mastery_snapshot_fn=get_topic_mastery_snapshot,
            record_review_completion_fn=record_review_completion,
            record_mastery_outcome_fn=lambda *, topic, before_snapshot, after_snapshot: _record_mastery_outcome_metrics(
                db,
                current_user=current_user,
                topic=topic,
                surface="review_completion",
                target="review",
                before_snapshot=before_snapshot,
                after_snapshot=after_snapshot,
            ),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


# ─── Gamification: Streaks & Badges ────────────────────────

@router.get("/streaks")
async def student_streaks(
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Get student's login streak, longest streak, and earned badges."""
    return _get_student_streak_overview_impl(
        db=db,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        record_login_fn=record_login,
        get_streak_info_fn=get_streak_info,
    )


# ─── Smart Weakness Alerts ──────────────────────────────────

@router.get("/weakness-alerts")
async def student_weakness_alerts(
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Get proactive alerts for subjects where the student is below 60%."""
    return _get_student_weakness_alerts_impl(
        db=db,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        generate_weakness_alerts_fn=generate_weakness_alerts,
    )


# ─── Test Series & Leaderboard ──────────────────────────────

@router.get("/test-series")
async def list_test_series(
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """List all active test series available to the student."""
    return _list_student_test_series_impl(
        db=db,
        tenant_id=current_user.tenant_id,
        get_all_series_fn=get_all_series,
    )


@router.get("/test-series/{series_id}/leaderboard")
async def view_leaderboard(
    series_id: str,
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """View the leaderboard for a test series."""
    return _get_student_test_series_leaderboard_impl(
        db=db,
        series_id=series_id,
        tenant_id=current_user.tenant_id,
        get_leaderboard_fn=get_leaderboard,
    )


@router.get("/test-series/{series_id}/my-rank")
async def my_rank(
    series_id: str,
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Get the student's rank in a test series."""
    return _get_student_test_series_rank_impl(
        db=db,
        series_id=series_id,
        student_id=current_user.id,
        tenant_id=current_user.tenant_id,
        get_student_rank_fn=get_student_rank,
    )


class MockTestSubmission(BaseModel):
    marks_obtained: float
    time_taken_minutes: int | None = None


@router.post("/test-series/{series_id}/submit")
async def submit_mock_test(
    series_id: str,
    data: MockTestSubmission,
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Submit a mock test attempt and get updated rankings."""
    try:
        return _submit_student_mock_test_impl(
            db=db,
            series_id=series_id,
            tenant_id=current_user.tenant_id,
            student_id=current_user.id,
            marks_obtained=data.marks_obtained,
            time_taken_minutes=data.time_taken_minutes,
            test_series_model=TestSeries,
            mock_test_attempt_model=MockTestAttempt,
            calculate_rankings_fn=calculate_rankings,
        )
    except _StudentMockTestSubmissionError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail)

