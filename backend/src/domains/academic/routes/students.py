"""Student-facing API routes — dashboard, attendance, results, timetable, assignments, lectures, complaints, upload."""
import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from auth.dependencies import require_role
from src.domains.identity.models.user import User
from src.domains.academic.models.attendance import Attendance
from src.domains.academic.models.marks import Exam, Mark
from src.domains.academic.models.assignment import Assignment, AssignmentSubmission
from src.domains.academic.models.timetable import Timetable
from src.domains.academic.models.lecture import Lecture
from src.domains.administrative.models.complaint import Complaint
from src.domains.academic.models.core import Enrollment, Subject
from src.domains.platform.models.ai import AIQuery
from src.domains.platform.models.document import Document
from src.domains.identity.models.tenant import Tenant
from src.domains.platform.schemas.ai_runtime import InternalStudyToolGenerateRequest, StudyToolGenerateRequest
from src.domains.platform.services.ai_gateway import run_study_tool
from src.domains.platform.services.ai_queue import JOB_TYPE_STUDY_TOOL, enqueue_job
from src.infrastructure.vector_store.citation_linker import make_citations_clickable
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

UPLOAD_DIR = ensure_storage_dir("uploads")
STUDENT_ALLOWED_EXTENSIONS = STUDENT_ALLOWED_EXTENSIONS_CONST
MAX_FILE_SIZE = STUDENT_MAX_FILE_SIZE
ASSIGNMENT_SUBMISSION_DIR = ensure_storage_dir("uploads", "assignment_submissions")
OCR_OUTPUT_DIR = ensure_storage_dir("uploads", "ocr_output")


class ComplaintCreate(BaseModel):
    category: str = "other"
    description: str


def _parse_uuid(value: str, field_name: str) -> UUID:
    try:
        return UUID(str(value))
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail=f"Invalid {field_name}")


def _extract_json_payload(text: str) -> Any:
    raw = (text or "").strip()
    if not raw:
        return None

    try:
        return json.loads(raw)
    except Exception:
        pass

    fenced = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw)
    if fenced:
        candidate = fenced.group(1).strip()
        try:
            return json.loads(candidate)
        except Exception:
            pass

    for start_char, end_char in (("[", "]"), ("{", "}")):
        start_idx = raw.find(start_char)
        end_idx = raw.rfind(end_char)
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            candidate = raw[start_idx : end_idx + 1]
            try:
                return json.loads(candidate)
            except Exception:
                continue

    return None


def _normalize_tool_output(tool: str, answer: str) -> Any:
    if tool == "flowchart":
        cleaned = answer.split("\n\nSources:")[0].strip()
        if not cleaned:
            raise HTTPException(status_code=422, detail="Tool output is empty")
        return cleaned

    parsed = _extract_json_payload(answer)
    if parsed is None:
        raise HTTPException(status_code=422, detail="Failed to parse tool output as JSON")

    if tool == "quiz":
        if not isinstance(parsed, list):
            raise HTTPException(status_code=422, detail="Quiz output must be a JSON array")
        normalized: list[dict[str, Any]] = []
        for idx, item in enumerate(parsed):
            if not isinstance(item, dict):
                continue
            question = str(item.get("question", "")).strip()
            options_raw = item.get("options", [])
            if isinstance(options_raw, list):
                options = [str(option).strip() for option in options_raw if str(option).strip()]
            else:
                options = []
            correct_raw = str(item.get("correct", "")).strip().upper()
            match = re.search(r"[A-D]", correct_raw)
            correct = match.group(0) if match else "A"
            if not question or len(options) < 2:
                continue
            normalized.append(
                {
                    "question": question,
                    "options": options,
                    "correct": correct,
                    "citation": str(item.get("citation", "")).strip() or None,
                    "index": idx + 1,
                }
            )
        if not normalized:
            raise HTTPException(status_code=422, detail="Quiz output did not contain valid questions")
        return normalized

    if tool == "flashcards":
        if not isinstance(parsed, list):
            raise HTTPException(status_code=422, detail="Flashcards output must be a JSON array")
        cards = []
        for item in parsed:
            if not isinstance(item, dict):
                continue
            front = str(item.get("front", "")).strip()
            back = str(item.get("back", "")).strip()
            if front and back:
                cards.append({"front": front, "back": back})
        if not cards:
            raise HTTPException(status_code=422, detail="Flashcards output was empty")
        return cards

    if tool == "mindmap":
        if not isinstance(parsed, dict) or not str(parsed.get("label", "")).strip():
            raise HTTPException(status_code=422, detail="Mind map output must include a root label")
        return parsed

    if tool == "concept_map":
        if not isinstance(parsed, dict):
            raise HTTPException(status_code=422, detail="Concept map output must be a JSON object")
        nodes = parsed.get("nodes", [])
        edges = parsed.get("edges", [])
        if not isinstance(nodes, list) or not isinstance(edges, list):
            raise HTTPException(status_code=422, detail="Concept map nodes/edges are invalid")
        normalized_nodes = []
        for node in nodes:
            if not isinstance(node, dict):
                continue
            node_id = str(node.get("id", "")).strip()
            label = str(node.get("label", "")).strip()
            if node_id and label:
                normalized_nodes.append({"id": node_id, "label": label})
        normalized_edges = []
        for edge in edges:
            if not isinstance(edge, dict):
                continue
            edge_from = str(edge.get("from", "")).strip()
            edge_to = str(edge.get("to", "")).strip()
            edge_label = str(edge.get("label", "")).strip()
            if edge_from and edge_to:
                normalized_edges.append({"from": edge_from, "to": edge_to, "label": edge_label})
        if not normalized_nodes:
            raise HTTPException(status_code=422, detail="Concept map output had no valid nodes")
        return {"nodes": normalized_nodes, "edges": normalized_edges}

    raise HTTPException(status_code=400, detail="Unsupported tool")


@router.get("/dashboard")
async def student_dashboard(
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Student dashboard: KPI stats + upcoming classes + AI insight."""
    tenant_id = current_user.tenant_id
    user_id = current_user.id

    # Attendance %
    total_att = db.query(Attendance).filter(
        Attendance.tenant_id == tenant_id, Attendance.student_id == user_id
    ).count()
    present_att = db.query(Attendance).filter(
        Attendance.tenant_id == tenant_id, Attendance.student_id == user_id,
        Attendance.status == "present"
    ).count()
    attendance_pct = round((present_att / total_att * 100) if total_att > 0 else 0)

    # Average marks
    avg_marks_row = db.query(func.avg(Mark.marks_obtained)).filter(
        Mark.tenant_id == tenant_id, Mark.student_id == user_id
    ).scalar()
    avg_marks = round(float(avg_marks_row)) if avg_marks_row else 0

    # Pending assignments
    enrollment = db.query(Enrollment).filter(
        Enrollment.tenant_id == tenant_id, Enrollment.student_id == user_id
    ).first()
    pending_assignments = 0
    if enrollment:
        subject_ids = [s.id for s in db.query(Subject).filter(
            Subject.tenant_id == tenant_id, Subject.class_id == enrollment.class_id
        ).all()]
        total_assignments = db.query(Assignment).filter(
            Assignment.tenant_id == tenant_id, Assignment.subject_id.in_(subject_ids)
        ).count()
        submitted = db.query(AssignmentSubmission).filter(
            AssignmentSubmission.tenant_id == tenant_id,
            AssignmentSubmission.student_id == user_id
        ).count()
        pending_assignments = max(0, total_assignments - submitted)

    # AI queries today
    from datetime import date
    ai_today = db.query(AIQuery).filter(
        AIQuery.tenant_id == tenant_id, AIQuery.user_id == user_id,
        func.date(AIQuery.created_at) == date.today()
    ).count()
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    ai_limit = tenant.ai_daily_limit if tenant else 50

    # Upcoming classes (timetable for today)
    from datetime import datetime
    today_dow = datetime.now().weekday()
    upcoming = []
    if enrollment:
        slots = db.query(Timetable).filter(
            Timetable.tenant_id == tenant_id,
            Timetable.class_id == enrollment.class_id,
            Timetable.day_of_week == today_dow,
        ).order_by(Timetable.start_time).all()
        for slot in slots:
            subject = db.query(Subject).filter(
                Subject.id == slot.subject_id,
                Subject.tenant_id == tenant_id,
            ).first()
            upcoming.append({
                "subject": subject.name if subject else "Unknown",
                "time": slot.start_time.strftime("%I:%M %p"),
            })

    # Uploaded docs count
    my_docs = db.query(Document).filter(
        Document.tenant_id == tenant_id, Document.uploaded_by == user_id
    ).count()

    return {
        "attendance_pct": attendance_pct,
        "avg_marks": avg_marks,
        "pending_assignments": pending_assignments,
        "ai_queries_today": ai_today,
        "ai_queries_limit": ai_limit,
        "upcoming_classes": upcoming,
        "my_uploads": my_docs,
        "ai_insight": f"Your average is {avg_marks}%. Focus on weak areas to improve." if avg_marks < 80 else None,
    }


@router.get("/attendance")
async def student_attendance(
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """List student's attendance records."""
    records = db.query(Attendance).filter(
        Attendance.tenant_id == current_user.tenant_id,
        Attendance.student_id == current_user.id,
    ).order_by(Attendance.date.desc()).limit(30).all()

    return [
        {
            "date": str(r.date),
            "day": r.date.strftime("%a"),
            "status": r.status,
        }
        for r in records
    ]


@router.get("/results")
async def student_results(
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Get student's exam results grouped by subject."""
    marks = db.query(Mark, Exam).join(Exam, Mark.exam_id == Exam.id).filter(
        Mark.tenant_id == current_user.tenant_id,
        Mark.student_id == current_user.id,
    ).all()

    subjects_map: dict = {}
    for mark, exam in marks:
        subject = db.query(Subject).filter(
            Subject.id == exam.subject_id,
            Subject.tenant_id == current_user.tenant_id,
        ).first()
        subj_name = subject.name if subject else "Unknown"
        if subj_name not in subjects_map:
            subjects_map[subj_name] = {"name": subj_name, "exams": [], "total": 0, "count": 0}
        pct = round(mark.marks_obtained / exam.max_marks * 100)
        subjects_map[subj_name]["exams"].append({
            "name": exam.name,
            "marks": mark.marks_obtained,
            "max": exam.max_marks,
        })
        subjects_map[subj_name]["total"] += pct
        subjects_map[subj_name]["count"] += 1

    result = []
    for s in subjects_map.values():
        s["avg"] = round(s["total"] / s["count"]) if s["count"] > 0 else 0
        del s["total"]
        del s["count"]
        result.append(s)

    return result


@router.get("/results/trends")
async def student_result_trends(
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Get chronological marks trend by subject for charting."""
    marks = db.query(Mark, Exam).join(Exam, Mark.exam_id == Exam.id).filter(
        Mark.tenant_id == current_user.tenant_id,
        Mark.student_id == current_user.id,
    ).all()

    subject_ids = list({exam.subject_id for _, exam in marks})
    subject_name_by_id: dict[UUID, str] = {}
    if subject_ids:
        subjects = db.query(Subject).filter(
            Subject.tenant_id == current_user.tenant_id,
            Subject.id.in_(subject_ids),
        ).all()
        subject_name_by_id = {subject.id: subject.name for subject in subjects}

    trends_by_subject: dict[str, list[dict[str, Any]]] = {}
    for mark, exam in marks:
        subject_name = subject_name_by_id.get(exam.subject_id, "Unknown")
        date_value = exam.exam_date or (exam.created_at.date() if exam.created_at else None)
        percentage = round(mark.marks_obtained / exam.max_marks * 100) if exam.max_marks > 0 else 0
        trends_by_subject.setdefault(subject_name, []).append(
            {
                "exam": exam.name,
                "date": str(date_value) if date_value else None,
                "marks": mark.marks_obtained,
                "max": exam.max_marks,
                "percentage": percentage,
            }
        )

    response = []
    for subject_name, points in trends_by_subject.items():
        points.sort(key=lambda point: (point.get("date") or "9999-99-99", point.get("exam") or ""))
        average = round(sum(point["percentage"] for point in points) / len(points)) if points else 0
        response.append({"subject": subject_name, "average": average, "points": points})

    response.sort(key=lambda item: item["subject"])
    return response


@router.get("/timetable")
async def student_timetable(
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Get student's weekly timetable."""
    enrollment = db.query(Enrollment).filter(
        Enrollment.tenant_id == current_user.tenant_id,
        Enrollment.student_id == current_user.id,
    ).first()

    if not enrollment:
        return []

    slots = db.query(Timetable).filter(
        Timetable.tenant_id == current_user.tenant_id,
        Timetable.class_id == enrollment.class_id,
    ).order_by(Timetable.day_of_week, Timetable.start_time).all()

    result = []
    for slot in slots:
        subject = db.query(Subject).filter(
            Subject.id == slot.subject_id,
            Subject.tenant_id == current_user.tenant_id,
        ).first()
        teacher = db.query(User).filter(
            User.id == slot.teacher_id,
            User.tenant_id == current_user.tenant_id,
        ).first()
        result.append({
            "day": slot.day_of_week,
            "start": slot.start_time.strftime("%H:%M"),
            "end": slot.end_time.strftime("%H:%M"),
            "subject": subject.name if subject else "Unknown",
            "teacher": teacher.full_name if teacher else "Unknown",
        })

    return result


@router.get("/assignments")
async def student_assignments(
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Get student's assignments with submission status."""
    enrollment = db.query(Enrollment).filter(
        Enrollment.tenant_id == current_user.tenant_id,
        Enrollment.student_id == current_user.id,
    ).first()

    if not enrollment:
        return []

    subject_ids = [s.id for s in db.query(Subject).filter(
        Subject.tenant_id == current_user.tenant_id,
        Subject.class_id == enrollment.class_id,
    ).all()]

    assignments = db.query(Assignment).filter(
        Assignment.tenant_id == current_user.tenant_id,
        Assignment.subject_id.in_(subject_ids),
    ).order_by(Assignment.due_date.desc()).all()

    result = []
    for a in assignments:
        submission = db.query(AssignmentSubmission).filter(
            AssignmentSubmission.assignment_id == a.id,
            AssignmentSubmission.student_id == current_user.id,
        ).first()
        subject = db.query(Subject).filter(
            Subject.id == a.subject_id,
            Subject.tenant_id == current_user.tenant_id,
        ).first()

        status = "pending"
        grade = None
        if submission:
            if submission.grade is not None:
                status = "graded"
                grade = submission.grade
            else:
                status = "submitted"

        result.append({
            "id": str(a.id),
            "title": a.title,
            "subject": subject.name if subject else "Unknown",
            "due": str(a.due_date.date()) if a.due_date else None,
            "status": status,
            "grade": grade,
            "has_submission": submission is not None,
            "submitted_at": str(submission.submitted_at) if submission and submission.submitted_at else None,
        })

    return result


@router.post("/assignments/{assignment_id}/submit")
async def submit_assignment(
    assignment_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Upload or replace student's assignment submission."""
    assignment_uuid = _parse_uuid(assignment_id, "assignment_id")

    enrollment = db.query(Enrollment).filter(
        Enrollment.tenant_id == current_user.tenant_id,
        Enrollment.student_id == current_user.id,
    ).first()
    if not enrollment:
        raise HTTPException(status_code=403, detail="Student is not enrolled in any class")

    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_uuid,
        Assignment.tenant_id == current_user.tenant_id,
    ).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    subject = db.query(Subject).filter(
        Subject.id == assignment.subject_id,
        Subject.tenant_id == current_user.tenant_id,
    ).first()
    if not subject or subject.class_id != enrollment.class_id:
        raise HTTPException(status_code=403, detail="Not authorized to submit this assignment")

    existing_submission = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.tenant_id == current_user.tenant_id,
        AssignmentSubmission.assignment_id == assignment_uuid,
        AssignmentSubmission.student_id == current_user.id,
    ).first()
    if existing_submission and existing_submission.grade is not None:
        raise HTTPException(status_code=409, detail="Assignment already graded. Resubmission is locked.")

    safe_filename = Path(file.filename or "").name
    if not safe_filename:
        raise HTTPException(status_code=400, detail="Filename is required.")

    ext = safe_filename.split(".")[-1].lower() if "." in safe_filename else ""
    if ext not in STUDENT_ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Only {', '.join(sorted(STUDENT_ALLOWED_EXTENSIONS))} files allowed.",
        )

    content = await file.read()
    if ext == "docx":
        try:
            content, _ = sanitize_docx_bytes(content)
        except UploadValidationError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File exceeds 25MB limit.")

    # OCR: convert image to PDF
    if ext in ("jpg", "jpeg", "png"):
        from src.infrastructure.vector_store.ocr_service import image_to_pdf, validate_image_size
        try:
            validate_image_size(content)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        # Save temp image, run OCR, produce PDF
        temp_img = ASSIGNMENT_SUBMISSION_DIR / f"_tmp_{uuid4().hex}.{ext}"
        with open(temp_img, "wb") as f:
            f.write(content)
        pdf_name = f"{current_user.tenant_id}_{current_user.id}_{assignment_uuid}_{uuid4().hex}_ocr.pdf"
        pdf_path = ASSIGNMENT_SUBMISSION_DIR / pdf_name
        try:
            image_to_pdf(str(temp_img), str(pdf_path), title=safe_filename)
        except Exception as exc:
            logger.exception("OCR processing failed")
            raise HTTPException(status_code=500, detail="OCR processing failed.")
        finally:
            temp_img.unlink(missing_ok=True)
        file_path = pdf_path
        safe_filename = pdf_name
    else:
        stored_name = f"{current_user.tenant_id}_{current_user.id}_{assignment_uuid}_{uuid4().hex}_{safe_filename}"
        file_path = ASSIGNMENT_SUBMISSION_DIR / stored_name
        with open(file_path, "wb") as f:
            f.write(content)

    now = datetime.now(timezone.utc)
    if existing_submission:
        existing_submission.submission_url = str(file_path)
        existing_submission.submitted_at = now
    else:
        existing_submission = AssignmentSubmission(
            tenant_id=current_user.tenant_id,
            assignment_id=assignment_uuid,
            student_id=current_user.id,
            submission_url=str(file_path),
            submitted_at=now,
        )
        db.add(existing_submission)

    db.commit()
    db.refresh(existing_submission)

    return {
        "success": True,
        "submission_id": str(existing_submission.id),
        "assignment_id": str(assignment_uuid),
        "file_name": safe_filename,
        "submitted_at": str(existing_submission.submitted_at),
        "status": "submitted",
    }


@router.get("/lectures")
async def student_lectures(
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """List lectures available to student."""
    enrollment = db.query(Enrollment).filter(
        Enrollment.tenant_id == current_user.tenant_id,
        Enrollment.student_id == current_user.id,
    ).first()

    if not enrollment:
        return []

    subject_ids = [s.id for s in db.query(Subject).filter(
        Subject.tenant_id == current_user.tenant_id,
        Subject.class_id == enrollment.class_id,
    ).all()]

    lectures = db.query(Lecture).filter(
        Lecture.tenant_id == current_user.tenant_id,
        Lecture.subject_id.in_(subject_ids),
    ).all()

    result = []
    for lecture in lectures:
        subject = db.query(Subject).filter(
            Subject.id == lecture.subject_id,
            Subject.tenant_id == current_user.tenant_id,
        ).first()
        result.append({
            "title": lecture.title,
            "subject": subject.name if subject else "Unknown",
            "youtube_url": lecture.youtube_url,
            "has_transcript": lecture.transcript_ingested,
        })
    return result


@router.get("/complaints")
async def student_complaints(
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """List student's complaints."""
    complaints = db.query(Complaint).filter(
        Complaint.tenant_id == current_user.tenant_id,
        Complaint.student_id == current_user.id,
    ).order_by(Complaint.created_at.desc()).all()

    return [
        {
            "id": str(c.id),
            "category": c.category,
            "description": c.description,
            "status": c.status,
            "date": str(c.created_at.date()),
        }
        for c in complaints
    ]


@router.post("/complaints")
async def create_complaint(
    data: ComplaintCreate,
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Submit a new complaint."""
    complaint = Complaint(
        tenant_id=current_user.tenant_id,
        student_id=current_user.id,
        category=data.category,
        description=data.description.strip(),
    )
    db.add(complaint)
    db.commit()
    return {"success": True, "message": "Complaint submitted"}


# ─── Student File Upload ────────────────────────────────────
@router.post("/tools/generate")
async def generate_study_tool(
    data: StudyToolGenerateRequest,
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Generate structured study tools from student's grounded materials."""
    _ = db
    topic = data.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="topic is required")

    from config import settings
    if settings.app.demo_mode:
        # Return pre-seeded demo data for each tool type
        demo_tools = {
            "quiz": {
                "data": [
                    {"question": f"What is {topic}?", "options": [f"A branch of science", f"A type of art", f"A form of literature", f"None of the above"], "correct": f"A branch of science", "citation": "Demo Materials p.1"},
                    {"question": f"Which concept is central to {topic}?", "options": ["Equilibrium", "Entropy", "Evolution", "Elasticity"], "correct": "Equilibrium", "citation": "Demo Materials p.3"},
                    {"question": f"Who is a notable contributor to {topic}?", "options": ["Albert Einstein", "Isaac Newton", "Marie Curie", "Charles Darwin"], "correct": "Isaac Newton", "citation": "Demo Materials p.5"},
                ],
                "citations": [{"source": "Demo Study Materials", "page": "1-5"}],
            },
            "flashcards": {
                "data": [
                    {"front": f"Define {topic}", "back": f"{topic} is a fundamental area of study that explores key principles and theories."},
                    {"front": f"Key principle of {topic}", "back": "The principle of conservation states that certain properties remain constant."},
                    {"front": f"Application of {topic}", "back": f"{topic} is applied in engineering, medicine, and technology."},
                ],
                "citations": [{"source": "Demo Study Materials", "page": "1-3"}],
            },
            "mindmap": {
                "data": {
                    "label": topic,
                    "children": [
                        {"label": "Fundamentals", "children": [{"label": "Core Concepts"}, {"label": "Key Theories"}]},
                        {"label": "Applications", "children": [{"label": "Engineering"}, {"label": "Medicine"}]},
                        {"label": "History", "children": [{"label": "Key Discoveries"}, {"label": "Notable Scientists"}]},
                    ]
                },
                "citations": [{"source": "Demo Study Materials", "page": "1-10"}],
            },
            "flowchart": {
                "data": f"graph TD\n    A[Start: {topic}] --> B[Learn Fundamentals]\n    B --> C[Study Core Concepts]\n    C --> D[Practice Problems]\n    D --> E{{Understand?}}\n    E -->|Yes| F[Advanced Topics]\n    E -->|No| C\n    F --> G[Apply Knowledge]\n    G --> H[End: Mastery]",
                "citations": [{"source": "Demo Study Materials", "page": "1-8"}],
            },
            "concept_map": {
                "data": {
                    "nodes": [
                        {"id": "1", "label": topic},
                        {"id": "2", "label": "Theory"},
                        {"id": "3", "label": "Practice"},
                        {"id": "4", "label": "Application"},
                        {"id": "5", "label": "Research"},
                    ],
                    "edges": [
                        {"from": "1", "to": "2", "label": "requires"},
                        {"from": "1", "to": "3", "label": "involves"},
                        {"from": "2", "to": "4", "label": "leads to"},
                        {"from": "3", "to": "4", "label": "supports"},
                        {"from": "4", "to": "5", "label": "drives"},
                    ]
                },
                "citations": [{"source": "Demo Study Materials", "page": "1-6"}],
            },
        }
        return demo_tools.get(data.tool, {"data": f"Demo content for {data.tool}: {topic}", "citations": []})

    result = await run_study_tool(
        InternalStudyToolGenerateRequest(
            tool=data.tool,
            topic=topic,
            subject_id=data.subject_id,
            tenant_id=str(current_user.tenant_id),
        )
    )
    return make_citations_clickable(result, current_user.tenant_id, db)


@router.post("/tools/generate/jobs")
async def generate_study_tool_job(
    data: StudyToolGenerateRequest,
    current_user: User = Depends(require_role("student")),
):
    """Queue structured study tool generation for worker execution."""
    topic = data.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="topic is required")

    payload = InternalStudyToolGenerateRequest(
        tool=data.tool,
        topic=topic,
        subject_id=data.subject_id,
        tenant_id=str(current_user.tenant_id),
    )
    
    from config import settings
    if settings.app.demo_mode:
        import uuid
        import time
        from database import SessionLocal
        from src.domains.platform.models.ai import AIQuery
        from src.domains.platform.services.ai_queue import STATUS_COMPLETED, _persist_job_state, build_public_job_response, JOB_TYPE_STUDY_TOOL
        
        db = SessionLocal()
        try:
            demo_log = db.query(AIQuery).filter(
                AIQuery.tenant_id == current_user.tenant_id,
                AIQuery.mode == data.tool
            ).first()
            
            response_data = None
            if demo_log and demo_log.response_text:
                import json
                try:
                    response_data = json.loads(demo_log.response_text)
                except Exception:
                    response_data = {"output": demo_log.response_text}
            
            if not response_data:
                response_data = {"message": f"This is a mocked response for the '{data.tool}' tool generated in Demo Mode."}
        finally:
            db.close()
            
        now_str = time.strftime("%Y-%m-%dT%H:%M:%S.%fZ", time.gmtime())
        mock_job = {
            "job_id": str(uuid.uuid4()),
            "job_type": JOB_TYPE_STUDY_TOOL,
            "priority": 30,
            "trace_id": str(uuid.uuid4())[:8],
            "status": STATUS_COMPLETED,
            "tenant_id": str(current_user.tenant_id),
            "user_id": str(current_user.id),
            "worker_id": "demo-worker",
            "request": payload.model_dump(),
            "result": response_data,
            "error": None,
            "attempts": 1,
            "max_retries": 3,
            "created_at": now_str,
            "updated_at": now_str,
            "started_at": now_str,
            "completed_at": now_str,
            "events": []
        }
        _persist_job_state(mock_job)
        return build_public_job_response(mock_job)

    return enqueue_job(
        JOB_TYPE_STUDY_TOOL,
        payload.model_dump(),
        tenant_id=str(current_user.tenant_id),
        user_id=str(current_user.id),
    )


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
    safe_filename = Path(file.filename or "").name
    if not safe_filename:
        raise HTTPException(status_code=400, detail="Filename is required.")

    ext = safe_filename.split(".")[-1].lower() if "." in safe_filename else ""
    if ext not in STUDENT_ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Only {', '.join(sorted(STUDENT_ALLOWED_EXTENSIONS))} files allowed.")

    content = await file.read()
    macros_removed = False
    ocr_processed = False
    if ext == "docx":
        try:
            content, macros_removed = sanitize_docx_bytes(content)
        except UploadValidationError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File exceeds 25MB limit.")

    # OCR: convert image to PDF for RAG ingestion
    if ext in ("jpg", "jpeg", "png"):
        from src.infrastructure.vector_store.ocr_service import image_to_pdf, validate_image_size
        try:
            validate_image_size(content)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        temp_img = OCR_OUTPUT_DIR / f"_tmp_{uuid4().hex}.{ext}"
        with open(temp_img, "wb") as f:
            f.write(content)
        pdf_name = f"{current_user.tenant_id}_{current_user.id}_{uuid4().hex}_ocr.pdf"
        file_path = OCR_OUTPUT_DIR / pdf_name
        try:
            image_to_pdf(str(temp_img), str(file_path), title=safe_filename)
        except Exception:
            logger.exception("OCR processing failed for student upload")
            raise HTTPException(status_code=500, detail="OCR processing failed.")
        finally:
            temp_img.unlink(missing_ok=True)
        safe_filename = pdf_name
        ext = "pdf"
        ocr_processed = True
    else:
        # Save file normally
        safe_name = f"{current_user.tenant_id}_{current_user.id}_{uuid4().hex}_{safe_filename}"
        file_path = UPLOAD_DIR / safe_name
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

    # RAG ingestion
    chunks_count = 0
    try:
        from src.infrastructure.vector_store.ingestion import ingest_document
        from src.infrastructure.llm.providers import get_embedding_provider, get_vector_store_provider

        chunks = ingest_document(
            file_path=str(file_path),
            document_id=str(doc.id),
            tenant_id=str(current_user.tenant_id),
        )

        if chunks:
            texts = [c.text for c in chunks]
            embeddings = await get_embedding_provider().embed_batch(texts)
            store = get_vector_store_provider(str(current_user.tenant_id))
            chunk_dicts = [{
                "text": c.text,
                "document_id": c.document_id,
                "page_number": c.page_number,
                "section_title": c.section_title or "",
                "subject_id": c.subject_id or "",
                "source_file": c.source_file or "",
            } for c in chunks]
            store.add_chunks(chunk_dicts, embeddings)
            chunks_count = len(chunks)

        doc.ingestion_status = "completed"
        db.commit()
    except Exception:
        logger.exception("Student document ingestion failed", extra={"document_id": str(doc.id)})
        doc.ingestion_status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail="Document ingestion failed.")

    return {
        "success": True,
        "document_id": str(doc.id),
        "file_name": safe_filename,
        "file_type": ext,
        "chunks": chunks_count,
        "macros_removed": macros_removed,
        "ocr_processed": ocr_processed,
        "status": doc.ingestion_status,
    }


@router.get("/uploads")
async def student_uploads(
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
    page: int = 1,
    page_size: int = 20,
):
    """List files uploaded by this student (paginated)."""
    query = db.query(Document).filter(
        Document.tenant_id == current_user.tenant_id,
        Document.uploaded_by == current_user.id,
    ).order_by(Document.created_at.desc())

    from utils.pagination import paginate
    result = paginate(query, page, page_size)

    return {
        "items": [{
            "id": str(d.id),
            "file_name": d.file_name,
            "file_type": d.file_type,
            "status": d.ingestion_status,
            "uploaded_at": str(d.created_at),
        } for d in result["items"]],
        "total": result["total"],
        "page": result["page"],
        "total_pages": result["total_pages"],
    }


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
    from src.domains.academic.models.performance import SubjectPerformance

    performances = db.query(SubjectPerformance).filter(
        SubjectPerformance.tenant_id == current_user.tenant_id,
        SubjectPerformance.student_id == current_user.id,
    ).all()

    weak = []
    strong = []
    for p in performances:
        subject = db.query(Subject).filter(
            Subject.id == p.subject_id,
            Subject.tenant_id == current_user.tenant_id,
        ).first()
        entry = {
            "subject": subject.name if subject else "Unknown",
            "average_score": p.average_score,
            "exam_count": 0,
            "is_weak": p.average_score < 60,
        }
        if p.average_score < 60:
            weak.append(entry)
        else:
            strong.append(entry)

    return {
        "weak_topics": sorted(weak, key=lambda x: x["average_score"]),
        "strong_topics": sorted(strong, key=lambda x: -x["average_score"]),
        "total_subjects": len(performances),
        "weak_count": len(weak),
    }


# ─── Spaced Repetition Reviews ─────────────────────────────

class ReviewCreateRequest(BaseModel):
    topic: str
    subject_id: Optional[str] = None


class ReviewCompleteRequest(BaseModel):
    rating: int  # 1-5 self-assessment quality


def _sm2_update(interval: int, ease_factor: float, rating: int) -> tuple[int, float]:
    """SM-2 spaced repetition algorithm.
    Returns (new_interval_days, new_ease_factor).
    Rating: 1=Again, 2=Hard, 3=Good, 4=Easy, 5=Perfect
    """
    if rating < 3:
        return 1, max(1.3, ease_factor - 0.2)
    else:
        new_ef = ease_factor + (0.1 - (5 - rating) * (0.08 + (5 - rating) * 0.02))
        new_ef = max(1.3, new_ef)
        if interval == 0:
            new_interval = 1
        elif interval == 1:
            new_interval = 6
        else:
            new_interval = round(interval * new_ef)
        return new_interval, new_ef


@router.get("/reviews")
async def student_reviews(
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Get student's spaced repetition review cards (due and upcoming)."""
    from src.domains.platform.models.spaced_repetition import ReviewSchedule

    reviews = db.query(ReviewSchedule).filter(
        ReviewSchedule.tenant_id == current_user.tenant_id,
        ReviewSchedule.student_id == current_user.id,
    ).order_by(ReviewSchedule.next_review_at).all()

    now = datetime.now(timezone.utc)
    due = []
    upcoming = []
    for r in reviews:
        # SQLite returns naive datetimes; make them aware for comparison
        review_at = r.next_review_at
        if review_at and review_at.tzinfo is None:
            review_at = review_at.replace(tzinfo=timezone.utc)
        is_due = review_at <= now if review_at else False
        entry = {
            "id": str(r.id),
            "topic": r.topic,
            "subject_id": str(r.subject_id) if r.subject_id else None,
            "next_review_at": str(r.next_review_at),
            "interval_days": r.interval_days,
            "ease_factor": round(r.ease_factor, 2),
            "review_count": r.review_count,
            "is_due": is_due,
        }
        if is_due:
            due.append(entry)
        else:
            upcoming.append(entry)

    return {"due": due, "upcoming": upcoming, "total": len(reviews)}


@router.post("/reviews")
async def create_review(
    data: ReviewCreateRequest,
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Create a new spaced repetition review card."""
    from src.domains.platform.models.spaced_repetition import ReviewSchedule
    from datetime import timedelta

    topic = data.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="topic is required")

    subject_uuid = None
    if data.subject_id:
        subject_uuid = _parse_uuid(data.subject_id, "subject_id")

    now = datetime.now(timezone.utc)
    review = ReviewSchedule(
        tenant_id=current_user.tenant_id,
        student_id=current_user.id,
        subject_id=subject_uuid,
        topic=topic,
        next_review_at=now + timedelta(days=1),
        interval_days=1,
        ease_factor=2.5,
        review_count=0,
    )
    db.add(review)
    db.commit()
    db.refresh(review)

    return {
        "success": True,
        "review_id": str(review.id),
        "topic": review.topic,
        "next_review_at": str(review.next_review_at),
    }


@router.post("/reviews/{review_id}/complete")
async def complete_review(
    review_id: str,
    data: ReviewCompleteRequest,
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Mark a review as completed with quality self-rating (SM-2)."""
    from src.domains.platform.models.spaced_repetition import ReviewSchedule
    from datetime import timedelta

    review_uuid = _parse_uuid(review_id, "review_id")
    if data.rating < 1 or data.rating > 5:
        raise HTTPException(status_code=400, detail="rating must be between 1 and 5")

    review = db.query(ReviewSchedule).filter(
        ReviewSchedule.id == review_uuid,
        ReviewSchedule.tenant_id == current_user.tenant_id,
        ReviewSchedule.student_id == current_user.id,
    ).first()

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    new_interval, new_ef = _sm2_update(review.interval_days, review.ease_factor, data.rating)

    review.interval_days = new_interval
    review.ease_factor = new_ef
    review.review_count += 1
    review.next_review_at = datetime.now(timezone.utc) + timedelta(days=new_interval)
    review.updated_at = datetime.now(timezone.utc)
    db.commit()

    return {
        "success": True,
        "review_id": str(review.id),
        "new_interval_days": new_interval,
        "new_ease_factor": round(new_ef, 2),
        "next_review_at": str(review.next_review_at),
        "review_count": review.review_count,
    }


# ─── Gamification: Streaks & Badges ────────────────────────

@router.get("/streaks")
async def student_streaks(
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Get student's login streak, longest streak, and earned badges."""
    from src.domains.academic.services.gamification import get_streak_info, record_login
    # Record this login
    record_login(db, current_user.id, current_user.tenant_id)
    return get_streak_info(db, current_user.id, current_user.tenant_id)


# ─── Smart Weakness Alerts ──────────────────────────────────

@router.get("/weakness-alerts")
async def student_weakness_alerts(
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Get proactive alerts for subjects where the student is below 60%."""
    from src.domains.academic.services.weakness_alerts import generate_weakness_alerts
    return generate_weakness_alerts(
        db,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
    )


# ─── Test Series & Leaderboard ──────────────────────────────

@router.get("/test-series")
async def list_test_series(
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """List all active test series available to the student."""
    from src.domains.academic.services.leaderboard import get_all_series
    return get_all_series(db, tenant_id=str(current_user.tenant_id))


@router.get("/test-series/{series_id}/leaderboard")
async def view_leaderboard(
    series_id: str,
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """View the leaderboard for a test series."""
    from src.domains.academic.services.leaderboard import get_leaderboard
    return get_leaderboard(db, test_series_id=series_id, tenant_id=str(current_user.tenant_id))


@router.get("/test-series/{series_id}/my-rank")
async def my_rank(
    series_id: str,
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Get the student's rank in a test series."""
    from src.domains.academic.services.leaderboard import get_student_rank
    return get_student_rank(
        db,
        test_series_id=series_id,
        student_id=str(current_user.id),
        tenant_id=str(current_user.tenant_id),
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
    from src.domains.academic.models.test_series import TestSeries, MockTestAttempt
    from src.domains.academic.services.leaderboard import calculate_rankings

    series = db.query(TestSeries).filter(
        TestSeries.id == series_id,
        TestSeries.tenant_id == current_user.tenant_id,
        TestSeries.is_active == True,
    ).first()
    if not series:
        raise HTTPException(status_code=404, detail="Test series not found")

    # Check if already attempted
    existing = db.query(MockTestAttempt).filter(
        MockTestAttempt.test_series_id == series_id,
        MockTestAttempt.student_id == current_user.id,
        MockTestAttempt.tenant_id == current_user.tenant_id,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="You have already attempted this test")

    attempt = MockTestAttempt(
        tenant_id=current_user.tenant_id,
        test_series_id=series.id,
        student_id=current_user.id,
        marks_obtained=data.marks_obtained,
        total_marks=series.total_marks,
        time_taken_minutes=data.time_taken_minutes,
    )
    db.add(attempt)
    db.commit()

    # Recalculate rankings
    rankings = calculate_rankings(db, test_series_id=series_id, tenant_id=str(current_user.tenant_id))

    # Find this student's rank
    my_rank = next((r for r in rankings if r["student_id"] == str(current_user.id)), None)

    return {
        "success": True,
        "attempt_id": str(attempt.id),
        "rank": my_rank["rank"] if my_rank else None,
        "percentile": my_rank["percentile"] if my_rank else None,
        "total_students": len(rankings),
    }
