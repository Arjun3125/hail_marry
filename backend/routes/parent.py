"""Parent-facing API routes."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from auth.dependencies import require_role
from database import get_db
from models.academic import Enrollment, Subject, Class
from models.assignment import Assignment, AssignmentSubmission
from models.attendance import Attendance
from models.marks import Exam, Mark
from models.parent_link import ParentLink
from models.user import User

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
    links_query = db.query(ParentLink).filter(
        ParentLink.tenant_id == current_user.tenant_id,
        ParentLink.parent_id == current_user.id,
    )

    if child_id:
        child_uuid = _parse_uuid(child_id, "child_id")
        links_query = links_query.filter(ParentLink.child_id == child_uuid)

    link = links_query.order_by(ParentLink.created_at.asc()).first()
    if not link:
        raise HTTPException(status_code=404, detail="No linked child found for this parent")

    child = db.query(User).filter(
        User.id == link.child_id,
        User.tenant_id == current_user.tenant_id,
        User.role == "student",
        User.is_active == True,
    ).first()
    if not child:
        raise HTTPException(status_code=404, detail="Linked child not found")
    return child


def _get_child_results(db: Session, tenant_id, child_id) -> list[dict]:
    marks = db.query(Mark, Exam).join(Exam, Mark.exam_id == Exam.id).filter(
        Mark.tenant_id == tenant_id,
        Mark.student_id == child_id,
    ).all()

    subjects_map: dict = {}
    for mark, exam in marks:
        subject = db.query(Subject).filter(
            Subject.id == exam.subject_id,
            Subject.tenant_id == tenant_id,
        ).first()
        subj_name = subject.name if subject else "Unknown"
        if subj_name not in subjects_map:
            subjects_map[subj_name] = {"name": subj_name, "exams": [], "total": 0, "count": 0}

        pct = round(mark.marks_obtained / exam.max_marks * 100) if exam.max_marks else 0
        subjects_map[subj_name]["exams"].append({
            "name": exam.name,
            "marks": mark.marks_obtained,
            "max": exam.max_marks,
        })
        subjects_map[subj_name]["total"] += pct
        subjects_map[subj_name]["count"] += 1

    result = []
    for item in subjects_map.values():
        item["avg"] = round(item["total"] / item["count"]) if item["count"] > 0 else 0
        del item["total"]
        del item["count"]
        result.append(item)
    return result


@router.get("/dashboard")
async def parent_dashboard(
    child_id: str | None = None,
    current_user: User = Depends(require_role("parent")),
    db: Session = Depends(get_db),
):
    child = _get_child_for_parent(current_user=current_user, db=db, child_id=child_id)

    total_att = db.query(Attendance).filter(
        Attendance.tenant_id == current_user.tenant_id,
        Attendance.student_id == child.id,
    ).count()
    present_att = db.query(Attendance).filter(
        Attendance.tenant_id == current_user.tenant_id,
        Attendance.student_id == child.id,
        Attendance.status == "present",
    ).count()
    attendance_pct = round((present_att / total_att * 100) if total_att > 0 else 0)

    avg_marks_row = db.query(func.avg(Mark.marks_obtained)).filter(
        Mark.tenant_id == current_user.tenant_id,
        Mark.student_id == child.id,
    ).scalar()
    avg_marks = round(float(avg_marks_row)) if avg_marks_row else 0

    enrollment = db.query(Enrollment).filter(
        Enrollment.tenant_id == current_user.tenant_id,
        Enrollment.student_id == child.id,
    ).first()
    class_name = None
    pending_assignments = 0
    if enrollment:
        cls = db.query(Class).filter(
            Class.id == enrollment.class_id,
            Class.tenant_id == current_user.tenant_id,
        ).first()
        class_name = cls.name if cls else None

        subject_ids = [s.id for s in db.query(Subject).filter(
            Subject.tenant_id == current_user.tenant_id,
            Subject.class_id == enrollment.class_id,
        ).all()]
        total_assignments = db.query(Assignment).filter(
            Assignment.tenant_id == current_user.tenant_id,
            Assignment.subject_id.in_(subject_ids),
        ).count()
        submitted = db.query(AssignmentSubmission).filter(
            AssignmentSubmission.tenant_id == current_user.tenant_id,
            AssignmentSubmission.student_id == child.id,
        ).count()
        pending_assignments = max(0, total_assignments - submitted)

    return {
        "child": {
            "id": str(child.id),
            "name": child.full_name,
            "email": child.email,
            "class": class_name,
        },
        "attendance_pct": attendance_pct,
        "avg_marks": avg_marks,
        "pending_assignments": pending_assignments,
    }


@router.get("/attendance")
async def parent_attendance(
    child_id: str | None = None,
    current_user: User = Depends(require_role("parent")),
    db: Session = Depends(get_db),
):
    child = _get_child_for_parent(current_user=current_user, db=db, child_id=child_id)
    records = db.query(Attendance).filter(
        Attendance.tenant_id == current_user.tenant_id,
        Attendance.student_id == child.id,
    ).order_by(Attendance.date.desc()).limit(60).all()
    return [{
        "date": str(r.date),
        "day": r.date.strftime("%a"),
        "status": r.status,
    } for r in records]


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
    results = _get_child_results(db=db, tenant_id=current_user.tenant_id, child_id=child.id)
    attendance = db.query(Attendance).filter(
        Attendance.tenant_id == current_user.tenant_id,
        Attendance.student_id == child.id,
    ).order_by(Attendance.date.desc()).limit(30).all()

    total_att = len(attendance)
    present_att = len([a for a in attendance if a.status == "present"])
    attendance_pct = round((present_att / total_att * 100) if total_att > 0 else 0)
    weak_subjects = [r["name"] for r in results if r.get("avg", 0) < 60]

    return {
        "child": {
            "id": str(child.id),
            "name": child.full_name,
        },
        "attendance_pct_30d": attendance_pct,
        "results": results,
        "weak_subjects": weak_subjects,
        "summary": "Needs attention in weak subjects." if weak_subjects else "Overall progress is stable.",
    }


@router.get("/audio-report")
async def parent_audio_report(
    child_id: str | None = None,
    current_user: User = Depends(require_role("parent")),
    db: Session = Depends(get_db),
):
    """Generate a text summary of child's progress for browser TTS playback."""
    child = _get_child_for_parent(current_user=current_user, db=db, child_id=child_id)
    results = _get_child_results(db=db, tenant_id=current_user.tenant_id, child_id=child.id)

    total_att = db.query(Attendance).filter(
        Attendance.tenant_id == current_user.tenant_id,
        Attendance.student_id == child.id,
    ).count()
    present_att = db.query(Attendance).filter(
        Attendance.tenant_id == current_user.tenant_id,
        Attendance.student_id == child.id,
        Attendance.status == "present",
    ).count()
    attendance_pct = round((present_att / total_att * 100) if total_att > 0 else 0)

    # Build natural language summary
    parts = [f"Progress report for {child.full_name}."]
    parts.append(f"Attendance is at {attendance_pct} percent.")

    if results:
        subject_summaries = []
        weak = []
        for r in results:
            avg = r.get("avg", 0)
            name = r.get("name", "Unknown")
            subject_summaries.append(f"{name}: {avg} percent average")
            if avg < 60:
                weak.append(name)
        parts.append("Subject performance: " + ", ".join(subject_summaries) + ".")
        if weak:
            parts.append(f"Attention needed in: {', '.join(weak)}.")
        else:
            parts.append("All subjects are performing well.")
    else:
        parts.append("No exam results available yet.")

    if attendance_pct < 75:
        parts.append("Attendance is below 75 percent. Please ensure regular attendance.")

    text = " ".join(parts)

    return {
        "child_name": child.full_name,
        "text": text,
        "attendance_pct": attendance_pct,
        "subject_count": len(results),
    }
