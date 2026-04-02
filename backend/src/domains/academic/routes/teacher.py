"""Teacher-facing API routes — dashboard, attendance, marks, assignments, upload, insights."""
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import io
from uuid import UUID
from starlette.responses import StreamingResponse

from database import get_db
from auth.dependencies import require_role
from auth.scoping import get_teacher_class_ids
from src.domains.academic.application.assessment_generation import generate_subject_assessment
from src.domains.academic.application.teacher_analytics import (
    build_teacher_classes_response as _build_teacher_classes_response_impl,
    build_teacher_dashboard_response as _build_teacher_dashboard_response_impl,
    build_teacher_doubt_heatmap_response as _build_teacher_doubt_heatmap_response_impl,
    build_teacher_insights_response as _build_teacher_insights_response_impl,
)
from src.domains.academic.application.teacher_bulk_updates import (
    apply_bulk_attendance_entries,
    apply_bulk_marks_entries,
    apply_structured_attendance_import_rows,
    apply_structured_marks_import_rows,
)
from src.domains.academic.application.teacher_coursework import (
    build_class_attendance_response as _build_class_attendance_response_impl,
    build_created_assignment_response as _build_created_assignment_response_impl,
    build_created_exam_response as _build_created_exam_response_impl,
    build_teacher_assignments_response as _build_teacher_assignments_response_impl,
)
from src.domains.academic.application.teacher_ingestion import (
    TeacherIngestionError as _TeacherIngestionError,
    ingest_teacher_youtube_video as _ingest_teacher_youtube_video_impl,
    upload_teacher_document as _upload_teacher_document_impl,
)
from src.domains.academic.application.teacher_onboarding import (
    TeacherOnboardingError as _TeacherOnboardingError,
    onboard_students_from_upload as _onboard_students_from_upload_impl,
)
from src.domains.academic.application.teacher_reporting import (
    build_attendance_csv_payload as _build_attendance_csv_payload_impl,
    build_created_test_series_response as _build_created_test_series_response_impl,
    build_marks_csv_payload as _build_marks_csv_payload_impl,
    build_teacher_test_series_leaderboard_response as _build_teacher_test_series_leaderboard_response_impl,
    list_teacher_test_series_response as _list_teacher_test_series_response_impl,
    queue_teacher_ai_grade_job as _queue_teacher_ai_grade_job_impl,
)
from src.domains.platform.services.webhooks import emit_webhook_event
from src.infrastructure.llm.cache import invalidate_tenant_cache
from src.domains.identity.application.passwords import hash_password
from src.domains.identity.models.tenant import Tenant
from src.domains.identity.models.user import User
from src.domains.academic.models.core import Class, Subject, Enrollment
from src.domains.academic.models.attendance import Attendance
from src.domains.academic.models.marks import Exam, Mark
from src.domains.academic.models.assignment import Assignment, AssignmentSubmission
from src.domains.academic.models.test_series import TestSeries
from src.domains.platform.models.document import Document
from src.domains.platform.models.ai import AIQuery
from src.domains.academic.models.lecture import Lecture
from src.domains.academic.models.timetable import Timetable
from src.domains.academic.services.leaderboard import get_all_series, get_leaderboard
from src.domains.platform.services.ai_queue import enqueue_job
from src.shared.ocr_imports import (
    StructuredImportParseResult,
    extract_upload_content_result,
    get_extension,
    parse_account_rows_with_diagnostics,
    parse_attendance_rows_with_diagnostics,
    parse_marks_rows_with_diagnostics,
)
from utils.upload_security import (
    UploadValidationError,
    ensure_storage_dir,
    sanitize_docx_bytes,
)
from constants import TEACHER_ALLOWED_EXTENSIONS, TEACHER_MAX_FILE_SIZE
from src.domains.platform.services.usage_governance import (
    evaluate_governance,
    record_usage_event,
    resolve_upload_metrics,
)

router = APIRouter(prefix="/api/teacher", tags=["Teacher"])

logger = logging.getLogger(__name__)

UPLOAD_DIR = ensure_storage_dir("uploads")
ALLOWED_EXTENSIONS = TEACHER_ALLOWED_EXTENSIONS
ALLOWED_ATTENDANCE_STATUSES = {"present", "absent", "late"}
MAX_FILE_SIZE = TEACHER_MAX_FILE_SIZE


# ─── Pydantic Schemas ────────────────────────────────────────
class AttendanceEntry(BaseModel):
    student_id: str
    status: str  # present, absent, late

class AttendanceBulk(BaseModel):
    class_id: str
    date: str  # YYYY-MM-DD
    entries: List[AttendanceEntry]

class MarkEntry(BaseModel):
    student_id: str
    marks_obtained: int

class MarksBulk(BaseModel):
    exam_id: str
    entries: List[MarkEntry]

class ExamCreate(BaseModel):
    name: str
    subject_id: str
    max_marks: int
    exam_date: Optional[str] = None

class AssignmentCreate(BaseModel):
    title: str
    description: str = ""
    subject_id: str
    due_date: Optional[str] = None

class YouTubeIngest(BaseModel):
    url: str
    title: str
    subject_id: Optional[str] = None


def _parse_uuid(value: str, field_name: str) -> UUID:
    try:
        return UUID(str(value))
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail=f"Invalid {field_name}")


def _ensure_class_access(current_user: User, class_id: UUID, allowed_class_ids: set[UUID]) -> None:
    if current_user.role == "admin":
        return
    if class_id not in allowed_class_ids:
        raise HTTPException(status_code=403, detail="Not authorized for this class")


def _get_subject_in_scope(
    db: Session,
    current_user: User,
    subject_id: str,
    allowed_class_ids: set[UUID],
) -> Subject:
    subject_uuid = _parse_uuid(subject_id, "subject_id")
    subject = db.query(Subject).filter(
        Subject.id == subject_uuid,
        Subject.tenant_id == current_user.tenant_id,
    ).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    _ensure_class_access(current_user, subject.class_id, allowed_class_ids)
    return subject


def _get_exam_with_subject_in_scope(
    db: Session,
    current_user: User,
    exam_id: str,
    allowed_class_ids: set[UUID],
) -> tuple[Exam, Subject]:
    exam_uuid = _parse_uuid(exam_id, "exam_id")
    exam = db.query(Exam).filter(
        Exam.id == exam_uuid,
        Exam.tenant_id == current_user.tenant_id,
    ).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    subject = db.query(Subject).filter(
        Subject.id == exam.subject_id,
        Subject.tenant_id == current_user.tenant_id,
    ).first()
    if not subject:
        raise HTTPException(status_code=400, detail="Exam has invalid subject mapping")

    _ensure_class_access(current_user, subject.class_id, allowed_class_ids)
    return exam, subject


def _validate_student_in_class(
    db: Session,
    current_user: User,
    student_id: str,
    class_id: UUID,
) -> UUID:
    student_uuid = _parse_uuid(student_id, "student_id")
    enrollment = db.query(Enrollment).filter(
        Enrollment.tenant_id == current_user.tenant_id,
        Enrollment.student_id == student_uuid,
        Enrollment.class_id == class_id,
    ).first()
    if not enrollment:
        raise HTTPException(status_code=400, detail=f"Student {student_id} is not enrolled in class")
    return student_uuid


def _resolve_student_identifier_in_class(
    db: Session,
    current_user: User,
    identifier: str,
    class_id: UUID,
) -> UUID:
    """Allow OCR imports to refer to students by UUID, email, or full name."""
    cleaned = identifier.strip()
    if not cleaned:
        raise HTTPException(status_code=400, detail="Missing student identifier")

    try:
        return _validate_student_in_class(db, current_user, cleaned, class_id)
    except HTTPException:
        pass

    match_value = cleaned.casefold()
    enrollments = db.query(Enrollment).filter(
        Enrollment.tenant_id == current_user.tenant_id,
        Enrollment.class_id == class_id,
    ).all()
    for enrollment in enrollments:
        student = db.query(User).filter(
            User.id == enrollment.student_id,
            User.tenant_id == current_user.tenant_id,
        ).first()
        if not student:
            continue
        if student.email and student.email.casefold() == match_value:
            return student.id
        if student.full_name and student.full_name.casefold() == match_value:
            return student.id

    raise HTTPException(status_code=400, detail=f"Student '{identifier}' is not enrolled in class")


def _load_structured_import_rows(
    filename: str,
    content: bytes,
    *,
    parser,
    empty_detail: str,
) -> tuple[list[tuple[str, int | str]], dict]:
    ext = get_extension(filename)
    if ext not in {"csv", "txt", "jpg", "jpeg", "png"}:
        raise HTTPException(status_code=400, detail="Only CSV, TXT, JPG, JPEG, PNG files allowed.")
    try:
        extraction = extract_upload_content_result(filename, content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    parsed: StructuredImportParseResult = parser(extraction.text)
    if not parsed.rows:
        raise HTTPException(status_code=400, detail=empty_detail)
    review_required = extraction.review_required or parsed.review_required
    warning = parsed.warning or extraction.warning
    if extraction.used_ocr and not warning and parsed.unmatched_lines:
        warning = f"OCR parsed {len(parsed.rows)} rows but some lines need manual review."
    metadata = {
        "ocr_processed": extraction.used_ocr,
        "ocr_review_required": review_required,
        "ocr_warning": warning,
        "ocr_languages": extraction.languages,
        "ocr_preprocessing": extraction.preprocessing_applied,
        "ocr_confidence": getattr(extraction, "confidence", None),
        "ocr_unmatched_lines": len(parsed.unmatched_lines),
    }
    return parsed.rows, metadata


# ─── Dashboard ───────────────────────────────────────────────
@router.get("/dashboard")
async def teacher_dashboard(
    current_user: User = Depends(require_role("teacher", "admin")),
    teacher_class_ids: list = Depends(get_teacher_class_ids),
    db: Session = Depends(get_db),
):
    """Teacher dashboard: classes overview with stats."""
    return _build_teacher_dashboard_response_impl(
        db=db,
        current_user=current_user,
        class_ids=list(teacher_class_ids),
        class_model=Class,
        enrollment_model=Enrollment,
        attendance_model=Attendance,
        subject_model=Subject,
        exam_model=Exam,
        mark_model=Mark,
        timetable_model=Timetable,
        assignment_model=Assignment,
        assignment_submission_model=AssignmentSubmission,
    )


# ─── Attendance Entry ────────────────────────────────────────
@router.post("/attendance")
async def submit_attendance(
    data: AttendanceBulk,
    current_user: User = Depends(require_role("teacher", "admin")),
    teacher_class_ids: list = Depends(get_teacher_class_ids),
    db: Session = Depends(get_db),
):
    """Bulk attendance entry for a class."""
    allowed_class_ids = set(teacher_class_ids)
    class_uuid = _parse_uuid(data.class_id, "class_id")
    _ensure_class_access(current_user, class_uuid, allowed_class_ids)

    try:
        att_date = datetime.strptime(data.date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date. Expected YYYY-MM-DD.")

    try:
        count = apply_bulk_attendance_entries(
            db=db,
            current_user=current_user,
            entries=data.entries,
            class_uuid=class_uuid,
            att_date=att_date,
            allowed_statuses=ALLOWED_ATTENDANCE_STATUSES,
            validate_student_in_class_fn=_validate_student_in_class,
            attendance_model=Attendance,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    try:
        await emit_webhook_event(
            db=db,
            tenant_id=current_user.tenant_id,
            event_type="attendance.marked",
            data={
                "class_id": str(class_uuid),
                "date": str(att_date),
                "submitted_count": count,
                "marked_by": str(current_user.id),
            },
        )
    except Exception:
        # Attendance submission should not fail if webhook delivery fails.
        pass

    return {"success": True, "count": count}

@router.get("/attendance/{class_id}")
async def get_class_attendance(
    class_id: str,
    current_user: User = Depends(require_role("teacher", "admin")),
    teacher_class_ids: list = Depends(get_teacher_class_ids),
    db: Session = Depends(get_db),
):
    """Get attendance records for a class."""
    allowed_class_ids = set(teacher_class_ids)
    class_uuid = _parse_uuid(class_id, "class_id")
    _ensure_class_access(current_user, class_uuid, allowed_class_ids)
    return _build_class_attendance_response_impl(
        db=db,
        current_user=current_user,
        class_uuid=class_uuid,
        attendance_model=Attendance,
        user_model=User,
    )


# ─── Marks Entry ─────────────────────────────────────────────
@router.post("/exams")
async def create_exam(
    data: ExamCreate,
    current_user: User = Depends(require_role("teacher", "admin")),
    teacher_class_ids: list = Depends(get_teacher_class_ids),
    db: Session = Depends(get_db),
):
    """Create a new exam."""
    allowed_class_ids = set(teacher_class_ids)
    subject = _get_subject_in_scope(
        db=db,
        current_user=current_user,
        subject_id=data.subject_id,
        allowed_class_ids=allowed_class_ids,
    )
    try:
        return _build_created_exam_response_impl(
            db=db,
            current_user=current_user,
            name=data.name,
            subject_id=subject.id,
            max_marks=data.max_marks,
            exam_date_raw=data.exam_date,
            exam_model=Exam,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.post("/marks")
async def submit_marks(
    data: MarksBulk,
    current_user: User = Depends(require_role("teacher", "admin")),
    teacher_class_ids: list = Depends(get_teacher_class_ids),
    db: Session = Depends(get_db),
):
    """Bulk marks entry for an exam."""
    allowed_class_ids = set(teacher_class_ids)
    exam, subject = _get_exam_with_subject_in_scope(
        db=db,
        current_user=current_user,
        exam_id=data.exam_id,
        allowed_class_ids=allowed_class_ids,
    )

    try:
        count = apply_bulk_marks_entries(
            db=db,
            current_user=current_user,
            entries=data.entries,
            exam=exam,
            subject=subject,
            validate_student_in_class_fn=_validate_student_in_class,
            mark_model=Mark,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    try:
        await emit_webhook_event(
            db=db,
            tenant_id=current_user.tenant_id,
            event_type="exam.results.published",
            data={
                "exam_id": str(exam.id),
                "subject_id": str(subject.id),
                "class_id": str(subject.class_id),
                "submitted_count": count,
                "published_by": str(current_user.id),
            },
        )
    except Exception:
        # Marks submission should not fail if webhook delivery fails.
        pass

    return {"success": True, "count": count}


# ─── Assignments CRUD ────────────────────────────────────────
@router.get("/assignments")
async def list_assignments(
    current_user: User = Depends(require_role("teacher", "admin")),
    db: Session = Depends(get_db),
):
    """List all assignments created by this teacher."""
    return _build_teacher_assignments_response_impl(
        db=db,
        current_user=current_user,
        assignment_model=Assignment,
        subject_model=Subject,
        assignment_submission_model=AssignmentSubmission,
    )

@router.post("/assignments")
async def create_assignment(
    data: AssignmentCreate,
    current_user: User = Depends(require_role("teacher", "admin")),
    teacher_class_ids: list = Depends(get_teacher_class_ids),
    db: Session = Depends(get_db),
):
    """Create a new assignment."""
    allowed_class_ids = set(teacher_class_ids)
    subject = _get_subject_in_scope(
        db=db,
        current_user=current_user,
        subject_id=data.subject_id,
        allowed_class_ids=allowed_class_ids,
    )
    try:
        return _build_created_assignment_response_impl(
            db=db,
            current_user=current_user,
            subject_id=subject.id,
            title=data.title,
            description=data.description,
            due_date_raw=data.due_date,
            assignment_model=Assignment,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


# ─── Upload + Ingestion ─────────────────────────────────────
@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(require_role("teacher", "admin")),
    db: Session = Depends(get_db),
):
    """Upload a document or OCR image for AI ingestion with the RAG pipeline."""
    try:
        return await _upload_teacher_document_impl(
            db=db,
            current_user=current_user,
            file=file,
            allowed_extensions=ALLOWED_EXTENSIONS,
            max_file_size=MAX_FILE_SIZE,
            upload_dir=UPLOAD_DIR,
            sanitize_docx_bytes_fn=sanitize_docx_bytes,
            upload_validation_error_cls=UploadValidationError,
            resolve_upload_metrics_fn=resolve_upload_metrics,
            evaluate_governance_fn=evaluate_governance,
            record_usage_event_fn=record_usage_event,
            invalidate_tenant_cache_fn=invalidate_tenant_cache,
            emit_webhook_event_fn=emit_webhook_event,
            document_model=Document,
            logger=logger,
        )
    except _TeacherIngestionError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail)


@router.post("/youtube")
async def ingest_youtube_video(
    data: YouTubeIngest,
    current_user: User = Depends(require_role("teacher", "admin")),
    teacher_class_ids: list = Depends(get_teacher_class_ids),
    db: Session = Depends(get_db),
):
    """Ingest a YouTube transcript for AI."""
    try:
        return await _ingest_teacher_youtube_video_impl(
            db=db,
            current_user=current_user,
            title=data.title,
            url=data.url,
            subject_id=data.subject_id,
            allowed_class_ids=set(teacher_class_ids),
            get_subject_in_scope_fn=_get_subject_in_scope,
            evaluate_governance_fn=evaluate_governance,
            record_usage_event_fn=record_usage_event,
            invalidate_tenant_cache_fn=invalidate_tenant_cache,
            lecture_model=Lecture,
        )
    except _TeacherIngestionError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail)


# ─── Onboarding ──────────────────────────────────────────────
@router.post("/onboard/students")
async def onboard_students(
    file: UploadFile = File(...),
    preview: bool = False,
    current_user: User = Depends(require_role("teacher", "admin")),
    db: Session = Depends(get_db),
):
    """
    Teacher can onboard a list of students via CSV or Image.
    Format is same as admin teacher onboarding: name (email/password generated).
    """
    try:
        return await _onboard_students_from_upload_impl(
            file=file,
            preview=preview,
            current_user=current_user,
            db=db,
            get_extension_fn=get_extension,
            extract_upload_content_result_fn=extract_upload_content_result,
            parse_account_rows_with_diagnostics_fn=parse_account_rows_with_diagnostics,
            user_model=User,
            tenant_model=Tenant,
            hash_password_fn=hash_password,
        )
    except _TeacherOnboardingError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail)


# ─── Classes ─────────────────────────────────────────────────
@router.get("/classes")
async def teacher_classes(
    current_user: User = Depends(require_role("teacher", "admin")),
    teacher_class_ids: list = Depends(get_teacher_class_ids),
    db: Session = Depends(get_db),
):
    """List classes with students."""
    return _build_teacher_classes_response_impl(
        db=db,
        current_user=current_user,
        allowed_class_ids=list(teacher_class_ids),
        class_model=Class,
        enrollment_model=Enrollment,
        user_model=User,
        subject_model=Subject,
    )


# ─── Insights ────────────────────────────────────────────────
@router.get("/insights")
async def teacher_insights(
    current_user: User = Depends(require_role("teacher", "admin")),
    teacher_class_ids: list = Depends(get_teacher_class_ids),
    db: Session = Depends(get_db),
):
    """AI-powered class analytics and weak topic insights."""
    return _build_teacher_insights_response_impl(
        db=db,
        current_user=current_user,
        allowed_class_ids=list(teacher_class_ids),
        class_model=Class,
        subject_model=Subject,
        exam_model=Exam,
        mark_model=Mark,
    )


# ─── Assessment Generator ────────────────────────────────────

class AssessmentGenerateRequest(BaseModel):
    subject_id: str
    topic: str
    num_questions: int = 5


@router.post("/generate-assessment")
async def generate_assessment(
    data: AssessmentGenerateRequest,
    current_user: User = Depends(require_role("teacher", "admin")),
    teacher_class_ids: list = Depends(get_teacher_class_ids),
    db: Session = Depends(get_db),
):
    """Generate an NCERT-aligned formative assessment using RAG + LLM."""
    allowed_class_ids = set(teacher_class_ids)
    subject = _get_subject_in_scope(
        db=db, current_user=current_user,
        subject_id=data.subject_id, allowed_class_ids=allowed_class_ids,
    )
    ai_result = await generate_subject_assessment(
        tenant_id=str(current_user.tenant_id),
        user_id=str(current_user.id),
        subject_id=str(subject.id),
        subject_name=subject.name,
        topic=data.topic,
        num_questions=data.num_questions,
    )
    return {
        "success": True,
        **ai_result,
    }


# ─── Doubt Heatmap ──────────────────────────────────────────

@router.get("/doubt-heatmap")
async def teacher_doubt_heatmap(
    current_user: User = Depends(require_role("teacher", "admin")),
    teacher_class_ids: list = Depends(get_teacher_class_ids),
    db: Session = Depends(get_db),
):
    """Aggregate student AI queries by subject to identify doubt hotspots."""
    return _build_teacher_doubt_heatmap_response_impl(
        db=db,
        current_user=current_user,
        allowed_class_ids=list(teacher_class_ids),
        class_model=Class,
        subject_model=Subject,
        enrollment_model=Enrollment,
        ai_query_model=AIQuery,
    )



# ─── Bulk CSV Import / Export ────────────────────────────────

class CSVAttendanceImport(BaseModel):
    class_id: str
    date: str  # YYYY-MM-DD

class CSVMarksImport(BaseModel):
    exam_id: str


@router.post("/attendance/csv-import")
async def import_attendance_csv(
    file: UploadFile = File(...),
    class_id: str = "",
    date: str = "",
    current_user: User = Depends(require_role("teacher", "admin")),
    teacher_class_ids: list = Depends(get_teacher_class_ids),
    db: Session = Depends(get_db),
):
    """Import attendance from CSV/TXT or OCR image. Rows may use student ID, email, or full name."""
    if not class_id or not date:
        raise HTTPException(status_code=400, detail="class_id and date are required query params")

    allowed_class_ids = set(teacher_class_ids)
    class_uuid = _parse_uuid(class_id, "class_id")
    _ensure_class_access(current_user, class_uuid, allowed_class_ids)

    try:
        att_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date. Expected YYYY-MM-DD.")

    content = await file.read()
    rows, ocr_meta = _load_structured_import_rows(
        file.filename or "",
        content,
        parser=parse_attendance_rows_with_diagnostics,
        empty_detail="No readable attendance rows found in the file.",
    )
    count, errors = apply_structured_attendance_import_rows(
        db=db,
        current_user=current_user,
        rows=rows,
        class_uuid=class_uuid,
        att_date=att_date,
        allowed_statuses=ALLOWED_ATTENDANCE_STATUSES,
        resolve_student_identifier_in_class_fn=_resolve_student_identifier_in_class,
        attendance_model=Attendance,
    )
    if errors and ocr_meta["ocr_processed"] and not ocr_meta["ocr_warning"]:
        ocr_meta["ocr_warning"] = f"OCR parsed {count} attendance rows but {len(errors)} rows need manual review."
    return {"success": True, "imported": count, "errors": errors, **ocr_meta}


@router.get("/attendance/csv-export/{class_id}")
async def export_attendance_csv(
    class_id: str,
    current_user: User = Depends(require_role("teacher", "admin")),
    teacher_class_ids: list = Depends(get_teacher_class_ids),
    db: Session = Depends(get_db),
):
    """Export class attendance as CSV."""
    allowed_class_ids = set(teacher_class_ids)
    class_uuid = _parse_uuid(class_id, "class_id")
    _ensure_class_access(current_user, class_uuid, allowed_class_ids)
    payload = _build_attendance_csv_payload_impl(
        db=db,
        current_user=current_user,
        class_uuid=class_uuid,
        requested_class_id=class_id,
        attendance_model=Attendance,
        user_model=User,
    )
    return StreamingResponse(
        io.StringIO(payload["content"]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={payload['filename']}"},
    )


@router.post("/marks/csv-import")
async def import_marks_csv(
    file: UploadFile = File(...),
    exam_id: str = "",
    current_user: User = Depends(require_role("teacher", "admin")),
    teacher_class_ids: list = Depends(get_teacher_class_ids),
    db: Session = Depends(get_db),
):
    """Import marks from CSV/TXT or OCR image. Rows may use student ID, email, or full name."""
    if not exam_id:
        raise HTTPException(status_code=400, detail="exam_id is required")

    allowed_class_ids = set(teacher_class_ids)
    exam, subject = _get_exam_with_subject_in_scope(db, current_user, exam_id, allowed_class_ids)

    content = await file.read()
    rows, ocr_meta = _load_structured_import_rows(
        file.filename or "",
        content,
        parser=parse_marks_rows_with_diagnostics,
        empty_detail="No readable marks rows found in the file.",
    )
    count, errors = apply_structured_marks_import_rows(
        db=db,
        current_user=current_user,
        rows=rows,
        exam=exam,
        subject=subject,
        resolve_student_identifier_in_class_fn=_resolve_student_identifier_in_class,
        mark_model=Mark,
    )
    if errors and ocr_meta["ocr_processed"] and not ocr_meta["ocr_warning"]:
        ocr_meta["ocr_warning"] = f"OCR parsed {count} marks rows but {len(errors)} rows need manual review."
    return {"success": True, "imported": count, "errors": errors, **ocr_meta}


@router.get("/marks/csv-export/{exam_id}")
async def export_marks_csv(
    exam_id: str,
    current_user: User = Depends(require_role("teacher", "admin")),
    teacher_class_ids: list = Depends(get_teacher_class_ids),
    db: Session = Depends(get_db),
):
    """Export exam marks as CSV."""
    allowed_class_ids = set(teacher_class_ids)
    exam, subject = _get_exam_with_subject_in_scope(db, current_user, exam_id, allowed_class_ids)
    payload = _build_marks_csv_payload_impl(
        db=db,
        current_user=current_user,
        exam=exam,
        requested_exam_id=exam_id,
        mark_model=Mark,
        user_model=User,
    )
    return StreamingResponse(
        io.StringIO(payload["content"]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={payload['filename']}"},
    )


# ─── AI Grading Co-Pilot ────────────────────────────────────

@router.post("/ai-grade")
async def ai_grade_answer_sheet(
    file: UploadFile = File(...),
    current_user: User = Depends(require_role("teacher", "admin")),
    db: Session = Depends(get_db),
):
    """Upload a student answer sheet image for AI-assisted grading.
    Returns a job ID that can be polled for results.
    """
    content = await file.read()
    try:
        return _queue_teacher_ai_grade_job_impl(
            file_name=file.filename or "",
            content=content,
            current_user=current_user,
            max_file_size=MAX_FILE_SIZE,
            upload_dir=UPLOAD_DIR,
            enqueue_job_fn=enqueue_job,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


# ─── Test Series Management ─────────────────────────────────

class TestSeriesCreate(BaseModel):
    name: str
    description: str = ""
    total_marks: int = 100
    duration_minutes: int = 60
    class_id: str | None = None
    subject_id: str | None = None


@router.post("/test-series")
async def create_test_series(
    data: TestSeriesCreate,
    current_user: User = Depends(require_role("teacher", "admin")),
    db: Session = Depends(get_db),
):
    """Create a new test series / mock test."""
    return _build_created_test_series_response_impl(
        db=db,
        current_user=current_user,
        name=data.name,
        description=data.description,
        total_marks=data.total_marks,
        duration_minutes=data.duration_minutes,
        class_id=data.class_id,
        subject_id=data.subject_id,
        test_series_model=TestSeries,
    )


@router.get("/test-series")
async def list_teacher_test_series(
    current_user: User = Depends(require_role("teacher", "admin")),
    db: Session = Depends(get_db),
):
    """List all test series created by this teacher."""
    return _list_teacher_test_series_response_impl(
        db=db,
        current_user=current_user,
        get_all_series_fn=get_all_series,
    )


@router.get("/test-series/{series_id}/leaderboard")
async def teacher_leaderboard(
    series_id: str,
    current_user: User = Depends(require_role("teacher", "admin")),
    db: Session = Depends(get_db),
):
    """View the leaderboard for a test series (teacher view)."""
    return _build_teacher_test_series_leaderboard_response_impl(
        db=db,
        current_user=current_user,
        series_id=series_id,
        get_leaderboard_fn=get_leaderboard,
    )

