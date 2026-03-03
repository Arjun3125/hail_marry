"""Teacher-facing API routes — dashboard, attendance, marks, assignments, upload, insights."""
import logging
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
from uuid import UUID, uuid4

from database import get_db
from auth.dependencies import require_role
from auth.scoping import get_teacher_class_ids
from services.webhooks import emit_webhook_event
from models.user import User
from models.academic import Class, Subject, Enrollment
from models.attendance import Attendance
from models.marks import Exam, Mark
from models.assignment import Assignment, AssignmentSubmission
from models.document import Document
from models.lecture import Lecture
from utils.upload_security import (
    UploadValidationError,
    ensure_storage_dir,
    sanitize_docx_bytes,
)

router = APIRouter(prefix="/api/teacher", tags=["Teacher"])

logger = logging.getLogger(__name__)

UPLOAD_DIR = ensure_storage_dir("uploads")
ALLOWED_EXTENSIONS = {"pdf", "docx"}
ALLOWED_ATTENDANCE_STATUSES = {"present", "absent", "late"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


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


# ─── Dashboard ───────────────────────────────────────────────
@router.get("/dashboard")
async def teacher_dashboard(
    current_user: User = Depends(require_role("teacher", "admin")),
    teacher_class_ids: list = Depends(get_teacher_class_ids),
    db: Session = Depends(get_db),
):
    """Teacher dashboard: classes overview with stats."""
    class_ids = list(teacher_class_ids)

    classes = []
    for cid in class_ids:
        cls = db.query(Class).filter(
            Class.id == cid,
            Class.tenant_id == current_user.tenant_id,
        ).first()
        if not cls:
            continue
        student_count = db.query(Enrollment).filter(
            Enrollment.tenant_id == current_user.tenant_id,
            Enrollment.class_id == cid,
        ).count()
        total_att = db.query(Attendance).filter(Attendance.tenant_id == current_user.tenant_id, Attendance.class_id == cid).count()
        present_att = db.query(Attendance).filter(Attendance.tenant_id == current_user.tenant_id, Attendance.class_id == cid, Attendance.status == "present").count()
        avg_att = round(present_att / total_att * 100) if total_att > 0 else 0
        subject_ids = [s.id for s in db.query(Subject).filter(Subject.tenant_id == current_user.tenant_id, Subject.class_id == cid).all()]
        exam_ids = [e.id for e in db.query(Exam).filter(
            Exam.tenant_id == current_user.tenant_id,
            Exam.subject_id.in_(subject_ids),
        ).all()] if subject_ids else []
        avg_m = db.query(func.avg(Mark.marks_obtained)).filter(
            Mark.tenant_id == current_user.tenant_id,
            Mark.exam_id.in_(exam_ids),
        ).scalar() if exam_ids else None
        classes.append({"id": str(cls.id), "name": cls.name, "students": student_count, "avg_attendance": avg_att, "avg_marks": round(float(avg_m)) if avg_m else 0})

    return {"classes": classes}


# ─── Attendance Entry ────────────────────────────────────────
@router.post("/attendance")
async def submit_attendance(
    data: AttendanceBulk,
    current_user: User = Depends(require_role("teacher", "admin")),
    teacher_class_ids: list = Depends(get_teacher_class_ids),
    db: Session = Depends(get_db),
):
    """Bulk attendance entry for a class."""
    from datetime import datetime

    allowed_class_ids = set(teacher_class_ids)
    class_uuid = _parse_uuid(data.class_id, "class_id")
    _ensure_class_access(current_user, class_uuid, allowed_class_ids)

    try:
        att_date = datetime.strptime(data.date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date. Expected YYYY-MM-DD.")

    for entry in data.entries:
        if entry.status not in ALLOWED_ATTENDANCE_STATUSES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid attendance status for student {entry.student_id}",
            )
        student_uuid = _validate_student_in_class(db, current_user, entry.student_id, class_uuid)
        existing = db.query(Attendance).filter(
            Attendance.tenant_id == current_user.tenant_id,
            Attendance.student_id == student_uuid,
            Attendance.class_id == class_uuid,
            Attendance.date == att_date,
        ).first()
        if existing:
            existing.status = entry.status
        else:
            db.add(Attendance(
                tenant_id=current_user.tenant_id,
                student_id=student_uuid,
                class_id=class_uuid,
                date=att_date,
                status=entry.status,
            ))
    db.commit()

    try:
        await emit_webhook_event(
            db=db,
            tenant_id=current_user.tenant_id,
            event_type="attendance.marked",
            data={
                "class_id": str(class_uuid),
                "date": str(att_date),
                "submitted_count": len(data.entries),
                "marked_by": str(current_user.id),
            },
        )
    except Exception:
        # Attendance submission should not fail if webhook delivery fails.
        pass

    return {"success": True, "count": len(data.entries)}

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

    records = db.query(Attendance).filter(
        Attendance.tenant_id == current_user.tenant_id,
        Attendance.class_id == class_uuid,
    ).order_by(Attendance.date.desc()).limit(100).all()

    student_ids = list({r.student_id for r in records})
    users = []
    if student_ids:
        users = db.query(User).filter(
            User.tenant_id == current_user.tenant_id,
            User.id.in_(student_ids),
        ).all()
    student_name_by_id = {u.id: u.full_name for u in users}

    return [{
        "student_id": str(r.student_id),
        "student_name": student_name_by_id.get(r.student_id, "Unknown"),
        "date": str(r.date),
        "status": r.status,
    } for r in records]


# ─── Marks Entry ─────────────────────────────────────────────
@router.post("/exams")
async def create_exam(
    data: ExamCreate,
    current_user: User = Depends(require_role("teacher", "admin")),
    teacher_class_ids: list = Depends(get_teacher_class_ids),
    db: Session = Depends(get_db),
):
    """Create a new exam."""
    from datetime import datetime

    allowed_class_ids = set(teacher_class_ids)
    if data.max_marks <= 0:
        raise HTTPException(status_code=400, detail="max_marks must be greater than 0")

    subject = _get_subject_in_scope(
        db=db,
        current_user=current_user,
        subject_id=data.subject_id,
        allowed_class_ids=allowed_class_ids,
    )

    exam_date = None
    if data.exam_date:
        try:
            exam_date = datetime.strptime(data.exam_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid exam_date. Expected YYYY-MM-DD.")

    exam = Exam(
        tenant_id=current_user.tenant_id,
        name=data.name,
        subject_id=subject.id,
        max_marks=data.max_marks,
        exam_date=exam_date,
    )
    db.add(exam)
    db.commit()
    db.refresh(exam)
    return {"success": True, "exam_id": str(exam.id), "name": exam.name}

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

    for entry in data.entries:
        if entry.marks_obtained < 0 or entry.marks_obtained > exam.max_marks:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid marks for student {entry.student_id}. Must be between 0 and {exam.max_marks}.",
            )

        student_uuid = _validate_student_in_class(
            db=db,
            current_user=current_user,
            student_id=entry.student_id,
            class_id=subject.class_id,
        )

        existing = db.query(Mark).filter(
            Mark.tenant_id == current_user.tenant_id,
            Mark.exam_id == exam.id,
            Mark.student_id == student_uuid,
        ).first()
        if existing:
            existing.marks_obtained = entry.marks_obtained
        else:
            db.add(Mark(
                tenant_id=current_user.tenant_id,
                student_id=student_uuid,
                exam_id=exam.id,
                marks_obtained=entry.marks_obtained,
            ))
    db.commit()

    try:
        await emit_webhook_event(
            db=db,
            tenant_id=current_user.tenant_id,
            event_type="exam.results.published",
            data={
                "exam_id": str(exam.id),
                "subject_id": str(subject.id),
                "class_id": str(subject.class_id),
                "submitted_count": len(data.entries),
                "published_by": str(current_user.id),
            },
        )
    except Exception:
        # Marks submission should not fail if webhook delivery fails.
        pass

    return {"success": True, "count": len(data.entries)}


# ─── Assignments CRUD ────────────────────────────────────────
@router.get("/assignments")
async def list_assignments(
    current_user: User = Depends(require_role("teacher", "admin")),
    db: Session = Depends(get_db),
):
    """List all assignments created by this teacher."""
    assignments = db.query(Assignment).filter(
        Assignment.tenant_id == current_user.tenant_id,
        Assignment.created_by == current_user.id,
    ).order_by(Assignment.created_at.desc()).all()
    subject_ids = list({a.subject_id for a in assignments})
    subjects = []
    if subject_ids:
        subjects = db.query(Subject).filter(
            Subject.tenant_id == current_user.tenant_id,
            Subject.id.in_(subject_ids),
        ).all()
    subject_name_by_id = {s.id: s.name for s in subjects}

    return [{
        "id": str(a.id),
        "title": a.title,
        "subject": subject_name_by_id.get(a.subject_id, "Unknown"),
        "due_date": str(a.due_date.date()) if a.due_date else None,
        "submissions": db.query(AssignmentSubmission).filter(
            AssignmentSubmission.tenant_id == current_user.tenant_id,
            AssignmentSubmission.assignment_id == a.id,
        ).count(),
    } for a in assignments]

@router.post("/assignments")
async def create_assignment(
    data: AssignmentCreate,
    current_user: User = Depends(require_role("teacher", "admin")),
    teacher_class_ids: list = Depends(get_teacher_class_ids),
    db: Session = Depends(get_db),
):
    """Create a new assignment."""
    from datetime import datetime

    allowed_class_ids = set(teacher_class_ids)
    subject = _get_subject_in_scope(
        db=db,
        current_user=current_user,
        subject_id=data.subject_id,
        allowed_class_ids=allowed_class_ids,
    )

    due_date = None
    if data.due_date:
        try:
            due_date = datetime.strptime(data.due_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid due_date. Expected YYYY-MM-DD.")

    assignment = Assignment(
        tenant_id=current_user.tenant_id,
        subject_id=subject.id,
        title=data.title,
        description=data.description,
        due_date=due_date,
        created_by=current_user.id,
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return {"success": True, "assignment_id": str(assignment.id)}


# ─── Upload + Ingestion ─────────────────────────────────────
@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(require_role("teacher", "admin")),
    db: Session = Depends(get_db),
):
    """Upload a PDF/DOCX for AI ingestion with RAG pipeline."""
    safe_filename = Path(file.filename or "").name
    if not safe_filename:
        raise HTTPException(status_code=400, detail="Filename is required.")

    # Validate file type
    ext = safe_filename.split(".")[-1].lower() if "." in safe_filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Only {', '.join(sorted(ALLOWED_EXTENSIONS))} files allowed.")

    # Save file
    file_path = UPLOAD_DIR / f"{current_user.tenant_id}_{current_user.id}_{uuid4().hex}_{safe_filename}"
    content = await file.read()
    macros_removed = False
    if ext == "docx":
        try:
            content, macros_removed = sanitize_docx_bytes(content)
        except UploadValidationError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File exceeds 50MB limit.")
    with open(file_path, "wb") as f:
        f.write(content)

    # Track in DB
    doc = Document(
        tenant_id=current_user.tenant_id,
        uploaded_by=current_user.id,
        file_name=safe_filename,
        file_type=ext,
        storage_path=str(file_path),
        ingestion_status="processing",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Trigger RAG ingestion
    try:
        from ai.ingestion import ingest_document
        from ai.embeddings import generate_embeddings_batch
        from ai.vector_store import get_vector_store

        chunks = ingest_document(
            file_path=str(file_path),
            document_id=str(doc.id),
            tenant_id=str(current_user.tenant_id),
        )

        if chunks:
            texts = [c.text for c in chunks]
            embeddings = await generate_embeddings_batch(texts)
            store = get_vector_store(str(current_user.tenant_id))
            chunk_dicts = [{
                "text": c.text,
                "document_id": c.document_id,
                "page_number": c.page_number,
                "section_title": c.section_title or "",
                "subject_id": c.subject_id or "",
                "source_file": c.source_file or "",
            } for c in chunks]
            store.add_chunks(chunk_dicts, embeddings)

        doc.ingestion_status = "completed"
        doc.chunk_count = len(chunks) if chunks else 0
        db.commit()

        try:
            await emit_webhook_event(
                db=db,
                tenant_id=current_user.tenant_id,
                event_type="document.ingested",
                data={
                    "document_id": str(doc.id),
                    "file_name": doc.file_name,
                    "uploaded_by": str(current_user.id),
                    "chunks": doc.chunk_count,
                },
            )
        except Exception:
            # Upload should not fail if webhook delivery fails.
            pass

        return {
            "success": True,
            "document_id": str(doc.id),
            "chunks": len(chunks),
            "status": "completed",
            "macros_removed": macros_removed,
        }
    except Exception:
        logger.exception("Teacher document ingestion failed", extra={"document_id": str(doc.id)})
        doc.ingestion_status = "failed"
        db.commit()
        return {
            "success": False,
            "document_id": str(doc.id),
            "error": "Document ingestion failed.",
            "status": "failed",
        }


@router.post("/youtube")
async def ingest_youtube_video(
    data: YouTubeIngest,
    current_user: User = Depends(require_role("teacher", "admin")),
    teacher_class_ids: list = Depends(get_teacher_class_ids),
    db: Session = Depends(get_db),
):
    """Ingest a YouTube transcript for AI."""
    if not data.subject_id:
        raise HTTPException(status_code=400, detail="subject_id is required")

    allowed_class_ids = set(teacher_class_ids)
    subject = _get_subject_in_scope(
        db=db,
        current_user=current_user,
        subject_id=data.subject_id,
        allowed_class_ids=allowed_class_ids,
    )
    subject_uuid = subject.id

    lecture = Lecture(
        tenant_id=current_user.tenant_id,
        title=data.title,
        youtube_url=data.url,
        subject_id=subject_uuid,
        transcript_ingested=False,
    )
    db.add(lecture)
    db.commit()
    db.refresh(lecture)

    try:
        from ai.ingestion import ingest_youtube
        from ai.embeddings import generate_embeddings_batch
        from ai.vector_store import get_vector_store

        chunks = ingest_youtube(
            url=data.url,
            document_id=str(lecture.id),
            tenant_id=str(current_user.tenant_id),
            subject_id=str(subject_uuid),
        )
        if chunks:
            texts = [c.text for c in chunks]
            embeddings = await generate_embeddings_batch(texts)
            store = get_vector_store(str(current_user.tenant_id))
            chunk_dicts = [{"text": c.text, "document_id": c.document_id, "page_number": c.page_number, "section_title": c.section_title or "", "subject_id": c.subject_id or "", "source_file": c.source_file or ""} for c in chunks]
            store.add_chunks(chunk_dicts, embeddings)

        lecture.transcript_ingested = True
        db.commit()
        return {"success": True, "lecture_id": str(lecture.id), "chunks": len(chunks)}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ─── Classes ─────────────────────────────────────────────────
@router.get("/classes")
async def teacher_classes(
    current_user: User = Depends(require_role("teacher", "admin")),
    teacher_class_ids: list = Depends(get_teacher_class_ids),
    db: Session = Depends(get_db),
):
    """List classes with students."""
    allowed_class_ids = list(teacher_class_ids)
    if not allowed_class_ids:
        return []

    classes = db.query(Class).filter(
        Class.tenant_id == current_user.tenant_id,
        Class.id.in_(allowed_class_ids),
    ).all()
    result = []
    for cls in classes:
        enrollments = db.query(Enrollment).filter(Enrollment.tenant_id == current_user.tenant_id, Enrollment.class_id == cls.id).all()
        students = []
        for e in enrollments:
            student = db.query(User).filter(
                User.id == e.student_id,
                User.tenant_id == current_user.tenant_id,
            ).first()
            if student:
                students.append({"id": str(student.id), "name": student.full_name, "email": student.email, "roll_number": e.roll_number})
        subjects = db.query(Subject).filter(Subject.tenant_id == current_user.tenant_id, Subject.class_id == cls.id).all()
        result.append({
            "id": str(cls.id), "name": cls.name, "grade": cls.grade_level,
            "students": students,
            "subjects": [{"id": str(s.id), "name": s.name} for s in subjects],
        })
    return result


# ─── Insights ────────────────────────────────────────────────
@router.get("/insights")
async def teacher_insights(
    current_user: User = Depends(require_role("teacher", "admin")),
    teacher_class_ids: list = Depends(get_teacher_class_ids),
    db: Session = Depends(get_db),
):
    """AI-powered class analytics and weak topic insights."""
    allowed_class_ids = list(teacher_class_ids)
    if not allowed_class_ids:
        return {"insights": []}

    classes = db.query(Class).filter(
        Class.tenant_id == current_user.tenant_id,
        Class.id.in_(allowed_class_ids),
    ).all()
    insights = []
    for cls in classes:
        subjects = db.query(Subject).filter(
            Subject.tenant_id == current_user.tenant_id,
            Subject.class_id == cls.id,
        ).all()
        subject_stats = []
        for subj in subjects:
            exams = db.query(Exam).filter(
                Exam.tenant_id == current_user.tenant_id,
                Exam.subject_id == subj.id,
            ).all()
            if not exams:
                continue
            exam_ids = [e.id for e in exams]
            avg = db.query(func.avg(Mark.marks_obtained)).filter(
                Mark.tenant_id == current_user.tenant_id,
                Mark.exam_id.in_(exam_ids),
            ).scalar()
            max_m = max(e.max_marks for e in exams)
            pct = round(float(avg) / max_m * 100) if avg and max_m else 0
            subject_stats.append({"subject": subj.name, "avg_pct": pct, "is_weak": pct < 60})
        weak_topics = [s["subject"] for s in subject_stats if s.get("is_weak")]
        insights.append({
            "class": cls.name,
            "subjects": subject_stats,
            "weak_topics": weak_topics,
            "recommendation": f"Focus on: {', '.join(weak_topics)}" if weak_topics else "All subjects performing well",
        })
    return {"insights": insights}
