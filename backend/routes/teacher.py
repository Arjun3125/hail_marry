"""Teacher-facing API routes — dashboard, attendance, marks, assignments, upload, insights."""
import logging
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import List, Optional
import csv
import io
import re
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


# ─── Onboarding ──────────────────────────────────────────────
@router.post("/onboard/students")
async def onboard_students(
    file: UploadFile = File(...),
    current_user: User = Depends(require_role("teacher", "admin")),
    db: Session = Depends(get_db),
):
    """
    Teacher can onboard a list of students via CSV or Image.
    Format is same as admin teacher onboarding: name (email/password generated).
    """
    safe_filename = file.filename or ""
    ext = safe_filename.split(".")[-1].lower() if "." in safe_filename else ""
    import tempfile
    import shutil
    import os

    with tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    students_to_create = []

    if ext in ("csv", "txt"):
        try:
            with open(tmp_path, "r", encoding="utf-8") as f:
                text = f.read()
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="Invalid encoding. Use UTF-8.")
        
        reader = csv.reader(io.StringIO(text))
        for row in reader:
            if not row or not any(row):
                continue
            name = row[0].strip()
            email = row[1].strip() if len(row) > 1 else f"{re.sub(r'[^a-zA-Z0-9]', '.', name.lower())}@example.com"
            password = row[2].strip() if len(row) > 2 else "Student123!"
            students_to_create.append({"name": name, "email": email, "password": password})
            
    elif ext in ("jpg", "jpeg", "png"):
        from ai.ocr_service import extract_text_from_image, validate_image_size
        try:
            with open(tmp_path, "rb") as f:
                validate_image_size(f.read())
        except ValueError as exc:
            os.unlink(tmp_path)
            raise HTTPException(status_code=400, detail=str(exc))
        
        try:
            extracted_text = extract_text_from_image(tmp_path)
            for line in extracted_text.splitlines():
                name = line.strip()
                if len(name) > 2:
                    email = f"{re.sub(r'[^a-zA-Z0-9]', '.', name.lower())}@example.com"
                    students_to_create.append({"name": name, "email": email, "password": "Student123!"})
        except Exception:
            os.unlink(tmp_path)
            raise HTTPException(status_code=500, detail="OCR processing failed")
    else:
        os.unlink(tmp_path)
        raise HTTPException(status_code=400, detail="Only CSV, TXT, JPG, JPEG, PNG allowed")
        
    # Cleanup temp file
    if os.path.exists(tmp_path):
        os.unlink(tmp_path)
        raise HTTPException(status_code=400, detail="Only CSV, TXT, JPG, JPEG, PNG allowed")

    if not students_to_create:
        raise HTTPException(status_code=400, detail="No readable names found in the file")

    try:
        from auth.auth import pwd_context
    except ImportError:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    created_count = 0
    from models.tenant import Tenant
    tenant_domain = db.query(Tenant.domain).filter(Tenant.id == current_user.tenant_id).scalar()

    for s in students_to_create:
        email = s["email"]
        if "@example.com" in email and tenant_domain:
            email = email.replace("@example.com", f"@{tenant_domain}")

        existing = db.query(User).filter(User.email == email).first()
        if existing:
            continue
            
        hashed_pw = pwd_context.hash(s["password"])
        new_student = User(
            tenant_id=current_user.tenant_id,
            email=email,
            full_name=s["name"],
            role="student",
            hashed_password=hashed_pw,
            is_active=True
        )
        db.add(new_student)
        created_count += 1
        
    db.commit()
    
    return {
        "success": True, 
        "message": f"Successfully onboarded {created_count} students.",
        "created_count": created_count
    }


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

    from routes.ai import ai_query, AIQueryRequest
    n = max(1, min(data.num_questions, 15))
    prompt_query = (
        f"Generate exactly {n} multiple-choice questions about: {data.topic}. "
        f"Subject: {subject.name}. Format as JSON array."
    )
    ai_request = AIQueryRequest(
        query=prompt_query,
        mode="quiz",
        subject_id=str(subject.id),
    )
    ai_result = await ai_query(ai_request, current_user, db)
    return {
        "success": True,
        "subject": subject.name,
        "topic": data.topic,
        "assessment": ai_result.get("answer", ""),
        "citations": ai_result.get("citations", []),
        "trace_id": ai_result.get("trace_id", ""),
    }


# ─── Doubt Heatmap ──────────────────────────────────────────

@router.get("/doubt-heatmap")
async def teacher_doubt_heatmap(
    current_user: User = Depends(require_role("teacher", "admin")),
    teacher_class_ids: list = Depends(get_teacher_class_ids),
    db: Session = Depends(get_db),
):
    """Aggregate student AI queries by subject to identify doubt hotspots."""
    from models.ai_query import AIQuery
    from collections import Counter

    allowed_class_ids = list(teacher_class_ids)
    if not allowed_class_ids:
        return {"heatmap": []}

    # Get student IDs in teacher's classes
    student_ids = []
    for cid in allowed_class_ids:
        enrollments = db.query(Enrollment).filter(
            Enrollment.tenant_id == current_user.tenant_id,
            Enrollment.class_id == cid,
        ).all()
        student_ids.extend([e.student_id for e in enrollments])

    if not student_ids:
        return {"heatmap": []}

    student_ids = list(set(student_ids))

    # Get recent AI queries from these students
    queries = db.query(AIQuery).filter(
        AIQuery.tenant_id == current_user.tenant_id,
        AIQuery.user_id.in_(student_ids),
    ).order_by(AIQuery.created_at.desc()).limit(500).all()

    # Build subject mapping for context
    subject_map = {}
    for cid in allowed_class_ids:
        cls = db.query(Class).filter(
            Class.id == cid,
            Class.tenant_id == current_user.tenant_id,
        ).first()
        subjects = db.query(Subject).filter(
            Subject.tenant_id == current_user.tenant_id,
            Subject.class_id == cid,
        ).all()
        for subj in subjects:
            subject_map[str(subj.id)] = {
                "subject": subj.name,
                "class": cls.name if cls else "Unknown",
            }

    # Count queries per topic keyword (use query text as topic proxy)
    topic_counter: Counter = Counter()
    subject_counter: Counter = Counter()
    queries_by_subject: dict = {}

    for q in queries:
        # Extract short topic from query text (first 60 chars)
        topic = q.query_text[:60].strip() if q.query_text else "Unknown"
        topic_counter[topic] += 1

        # Count by mode
        mode_key = q.mode or "qa"

        # Try to associate with a subject if subject queries exist
        for subj_id, info in subject_map.items():
            subj_name = info["subject"]
            cls_name = info["class"]
            key = f"{cls_name} — {subj_name}"
            if subj_name.lower() in (q.query_text or "").lower():
                subject_counter[key] += 1
                if key not in queries_by_subject:
                    queries_by_subject[key] = []
                queries_by_subject[key].append(topic)
                break

    # Build heatmap data
    heatmap = []
    for key, count in subject_counter.most_common(20):
        sample_topics = list(set(queries_by_subject.get(key, [])))[:5]
        heatmap.append({
            "label": key,
            "query_count": count,
            "intensity": min(1.0, count / max(1, len(queries)) * 10),
            "sample_topics": sample_topics,
        })

    # Top doubt topics overall
    top_topics = [
        {"topic": t, "count": c}
        for t, c in topic_counter.most_common(15)
    ]

    return {
        "heatmap": heatmap,
        "top_topics": top_topics,
        "total_queries": len(queries),
        "student_count": len(student_ids),
    }
