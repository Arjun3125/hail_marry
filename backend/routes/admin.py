"""Admin API routes — dashboard, users, AI usage, AI review, complaints, reports, security, settings."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import date, timedelta, datetime
from pydantic import BaseModel
from typing import Optional
import csv
import io
from uuid import UUID

from database import get_db
from auth.dependencies import require_role
from models.user import User
from models.attendance import Attendance
from models.marks import Mark, Exam
from models.complaint import Complaint
from models.ai_query import AIQuery
from models.academic import Enrollment, Class, Subject
from models.timetable import Timetable
from models.document import Document
from models.audit_log import AuditLog
from models.tenant import Tenant
from models.webhook import WebhookSubscription, WebhookDelivery
from models.parent_link import ParentLink
from services.webhooks import emit_webhook_event

router = APIRouter(prefix="/api/admin", tags=["Admin"])

ALLOWED_COMPLAINT_STATUSES = {"open", "in_review", "resolved"}
SUPPORTED_WEBHOOK_EVENTS = {
    "student.enrolled",
    "document.ingested",
    "ai.query.completed",
    "exam.results.published",
    "attendance.marked",
    "complaint.status.changed",
}


def _parse_uuid(value: str, field_name: str) -> UUID:
    try:
        return UUID(str(value))
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail=f"Invalid {field_name}")


def _parse_hhmm(value: str, field_name: str):
    try:
        return datetime.strptime(value, "%H:%M").time()
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail=f"Invalid {field_name}. Expected HH:MM")


class RoleChange(BaseModel):
    role: str

class ComplaintAction(BaseModel):
    status: str
    resolution_note: str = ""


class WebhookCreate(BaseModel):
    event_type: str
    target_url: str


class WebhookUpdate(BaseModel):
    is_active: bool


class ParentLinkCreate(BaseModel):
    parent_id: str
    child_id: str


# ─── Dashboard ───────────────────────────────────────────────
@router.get("/dashboard")
async def admin_dashboard(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    tid = current_user.tenant_id
    total_students = db.query(User).filter(User.tenant_id == tid, User.role == "student", User.is_active == True).count()
    total_teachers = db.query(User).filter(User.tenant_id == tid, User.role == "teacher", User.is_active == True).count()
    active_today = max(1, total_students // 5)
    ai_today = db.query(AIQuery).filter(AIQuery.tenant_id == tid, func.date(AIQuery.created_at) == date.today()).count()
    total_att = db.query(Attendance).filter(Attendance.tenant_id == tid).count()
    present_att = db.query(Attendance).filter(Attendance.tenant_id == tid, Attendance.status == "present").count()
    avg_attendance = round(present_att / total_att * 100) if total_att > 0 else 0
    avg_marks = db.query(func.avg(Mark.marks_obtained)).filter(Mark.tenant_id == tid).scalar()
    open_complaints = db.query(Complaint).filter(Complaint.tenant_id == tid, Complaint.status != "resolved").count()
    return {
        "total_students": total_students, "total_teachers": total_teachers,
        "active_today": active_today, "ai_queries_today": ai_today,
        "avg_attendance": avg_attendance, "avg_performance": round(float(avg_marks)) if avg_marks else 0,
        "open_complaints": open_complaints,
    }


# ─── User Management ────────────────────────────────────────
@router.get("/users")
async def list_users(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    users = db.query(User).filter(User.tenant_id == current_user.tenant_id, User.is_deleted == False).order_by(User.created_at.desc()).all()
    return [{
        "id": str(u.id), "name": u.full_name, "email": u.email, "role": u.role,
        "is_active": u.is_active, "last_login": str(u.last_login) if u.last_login else None,
        "ai_queries_30d": db.query(AIQuery).filter(
            AIQuery.tenant_id == current_user.tenant_id,
            AIQuery.user_id == u.id,
        ).count(),
    } for u in users]

@router.patch("/users/{user_id}/role")
async def change_user_role(user_id: str, data: RoleChange, current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    user_uuid = _parse_uuid(user_id, "user_id")
    user = db.query(User).filter(User.id == user_uuid, User.tenant_id == current_user.tenant_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if data.role not in ("student", "teacher", "admin", "parent"):
        raise HTTPException(status_code=400, detail="Invalid role")
    old_role = user.role
    user.role = data.role
    db.add(AuditLog(tenant_id=current_user.tenant_id, user_id=current_user.id, action="role.changed", entity_type="user", entity_id=user.id, metadata_={"old": old_role, "new": data.role}))
    db.commit()
    return {"success": True}

@router.patch("/users/{user_id}/deactivate")
async def deactivate_user(user_id: str, current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    user_uuid = _parse_uuid(user_id, "user_id")
    user = db.query(User).filter(User.id == user_uuid, User.tenant_id == current_user.tenant_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = not user.is_active
    db.add(AuditLog(tenant_id=current_user.tenant_id, user_id=current_user.id, action="user.toggled", entity_type="user", entity_id=user.id, metadata_={"is_active": user.is_active}))
    db.commit()
    return {"success": True, "is_active": user.is_active}


# ─── AI Usage Analytics ─────────────────────────────────────
@router.get("/ai-usage")
async def ai_usage_analytics(current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    tid = current_user.tenant_id
    week_ago = date.today() - timedelta(days=7)
    total_week = db.query(AIQuery).filter(AIQuery.tenant_id == tid, func.date(AIQuery.created_at) >= week_ago).count()
    student_q = db.query(AIQuery).join(User, AIQuery.user_id == User.id).filter(AIQuery.tenant_id == tid, User.role == "student").count()
    teacher_q = db.query(AIQuery).join(User, AIQuery.user_id == User.id).filter(AIQuery.tenant_id == tid, User.role == "teacher").count()
    admin_q = db.query(AIQuery).join(User, AIQuery.user_id == User.id).filter(AIQuery.tenant_id == tid, User.role == "admin").count()
    total_all = max(student_q + teacher_q + admin_q, 1)
    heavy = db.query(User.full_name, func.count(AIQuery.id).label("cnt")).join(AIQuery, AIQuery.user_id == User.id).filter(AIQuery.tenant_id == tid).group_by(User.full_name).order_by(desc("cnt")).limit(5).all()
    return {
        "total_week": total_week,
        "by_role": {"students": round(student_q / total_all * 100), "teachers": round(teacher_q / total_all * 100), "admin": round(admin_q / total_all * 100)},
        "heavy_users": [{"name": n, "queries": c} for n, c in heavy],
    }


# ─── AI Quality Review ──────────────────────────────────────
@router.get("/ai-review")
async def ai_review(current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    """Random sample of recent AI responses for quality review."""
    recent = db.query(AIQuery, User.full_name).join(User, AIQuery.user_id == User.id).filter(
        AIQuery.tenant_id == current_user.tenant_id,
    ).order_by(desc(AIQuery.created_at)).limit(20).all()
    return [{
        "id": str(q.id), "user": name, "query": q.query_text,
        "response": q.response_text[:500], "mode": q.mode,
        "citations": q.citation_count, "response_time_ms": q.response_time_ms,
        "trace_id": q.trace_id, "created_at": str(q.created_at),
    } for q, name in recent]


# ─── Complaints Oversight ───────────────────────────────────
@router.get("/complaints")
async def admin_complaints(current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    complaints = db.query(Complaint, User.full_name).join(User, Complaint.student_id == User.id).filter(
        Complaint.tenant_id == current_user.tenant_id,
    ).order_by(desc(Complaint.created_at)).all()
    return [{
        "id": str(c.id), "student": name, "category": c.category,
        "description": c.description, "status": c.status,
        "resolution_note": c.resolution_note, "date": str(c.created_at.date()),
    } for c, name in complaints]

@router.patch("/complaints/{complaint_id}")
async def update_complaint(complaint_id: str, data: ComplaintAction, current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    complaint_uuid = _parse_uuid(complaint_id, "complaint_id")
    complaint = db.query(Complaint).filter(Complaint.id == complaint_uuid, Complaint.tenant_id == current_user.tenant_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    if data.status not in ALLOWED_COMPLAINT_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid complaint status")
    complaint.status = data.status
    complaint.resolution_note = data.resolution_note
    if data.status == "resolved":
        from datetime import datetime
        complaint.resolved_by = current_user.id
        complaint.resolved_at = datetime.utcnow()
    db.commit()

    try:
        await emit_webhook_event(
            db=db,
            tenant_id=current_user.tenant_id,
            event_type="complaint.status.changed",
            data={
                "complaint_id": str(complaint.id),
                "status": complaint.status,
                "resolved_by": str(complaint.resolved_by) if complaint.resolved_by else None,
            },
        )
    except Exception:
        # Primary complaint workflow should not fail if webhook delivery fails.
        pass

    return {"success": True}


# ─── Class & Subject Management ──────────────────────────────
@router.get("/classes")
async def admin_classes(current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    classes = db.query(Class).filter(Class.tenant_id == current_user.tenant_id).all()
    return [{
        "id": str(c.id), "name": c.name, "grade": c.grade_level,
        "students": db.query(Enrollment).filter(
            Enrollment.tenant_id == current_user.tenant_id,
            Enrollment.class_id == c.id,
        ).count(),
        "subjects": [{"id": str(s.id), "name": s.name} for s in db.query(Subject).filter(
            Subject.tenant_id == current_user.tenant_id,
            Subject.class_id == c.id,
        ).all()],
    } for c in classes]

class ClassCreate(BaseModel):
    name: str
    grade_level: str
    academic_year: str = "2025-26"

class SubjectCreate(BaseModel):
    name: str
    class_id: str


class TimetableSlotCreate(BaseModel):
    class_id: str
    subject_id: str
    teacher_id: str
    day_of_week: int
    start_time: str
    end_time: str

@router.post("/classes")
async def create_class(data: ClassCreate, current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    cls = Class(tenant_id=current_user.tenant_id, name=data.name, grade_level=data.grade_level, academic_year=data.academic_year)
    db.add(cls)
    db.flush()
    db.add(AuditLog(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        action="class.created",
        entity_type="class",
        entity_id=cls.id,
        metadata_={"name": cls.name, "grade_level": cls.grade_level, "academic_year": cls.academic_year},
    ))
    db.commit()
    db.refresh(cls)
    return {"success": True, "class_id": str(cls.id)}

@router.post("/subjects")
async def create_subject(data: SubjectCreate, current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    class_uuid = _parse_uuid(data.class_id, "class_id")
    cls = db.query(Class).filter(
        Class.id == class_uuid,
        Class.tenant_id == current_user.tenant_id,
    ).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")

    subj = Subject(tenant_id=current_user.tenant_id, name=data.name, class_id=class_uuid)
    db.add(subj)
    db.flush()
    db.add(AuditLog(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        action="subject.created",
        entity_type="subject",
        entity_id=subj.id,
        metadata_={"name": subj.name, "class_id": str(class_uuid)},
    ))
    db.commit()
    return {"success": True, "subject_id": str(subj.id)}


# ─── Reports ────────────────────────────────────────────────
@router.get("/timetable/{class_id}")
async def get_class_timetable(
    class_id: str,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    class_uuid = _parse_uuid(class_id, "class_id")
    cls = db.query(Class).filter(
        Class.id == class_uuid,
        Class.tenant_id == current_user.tenant_id,
    ).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")

    slots = db.query(Timetable).filter(
        Timetable.tenant_id == current_user.tenant_id,
        Timetable.class_id == class_uuid,
    ).order_by(Timetable.day_of_week, Timetable.start_time).all()

    subject_ids = list({slot.subject_id for slot in slots})
    teacher_ids = list({slot.teacher_id for slot in slots})
    subjects = []
    teachers = []
    if subject_ids:
        subjects = db.query(Subject).filter(
            Subject.tenant_id == current_user.tenant_id,
            Subject.id.in_(subject_ids),
        ).all()
    if teacher_ids:
        teachers = db.query(User).filter(
            User.tenant_id == current_user.tenant_id,
            User.id.in_(teacher_ids),
        ).all()
    subject_name_by_id = {s.id: s.name for s in subjects}
    teacher_name_by_id = {t.id: (t.full_name or t.email) for t in teachers}

    return [{
        "id": str(slot.id),
        "class_id": str(slot.class_id),
        "subject_id": str(slot.subject_id),
        "subject": subject_name_by_id.get(slot.subject_id, "Unknown"),
        "teacher_id": str(slot.teacher_id),
        "teacher": teacher_name_by_id.get(slot.teacher_id, "Unknown"),
        "day_of_week": slot.day_of_week,
        "start_time": slot.start_time.strftime("%H:%M"),
        "end_time": slot.end_time.strftime("%H:%M"),
    } for slot in slots]


@router.post("/timetable")
async def create_timetable_slot(
    data: TimetableSlotCreate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    class_uuid = _parse_uuid(data.class_id, "class_id")
    subject_uuid = _parse_uuid(data.subject_id, "subject_id")
    teacher_uuid = _parse_uuid(data.teacher_id, "teacher_id")

    if data.day_of_week < 0 or data.day_of_week > 6:
        raise HTTPException(status_code=400, detail="day_of_week must be between 0 and 6")

    start_time = _parse_hhmm(data.start_time, "start_time")
    end_time = _parse_hhmm(data.end_time, "end_time")
    if start_time >= end_time:
        raise HTTPException(status_code=400, detail="start_time must be before end_time")

    cls = db.query(Class).filter(
        Class.id == class_uuid,
        Class.tenant_id == current_user.tenant_id,
    ).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")

    subject = db.query(Subject).filter(
        Subject.id == subject_uuid,
        Subject.tenant_id == current_user.tenant_id,
    ).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    if subject.class_id != class_uuid:
        raise HTTPException(status_code=400, detail="Subject does not belong to class")

    teacher = db.query(User).filter(
        User.id == teacher_uuid,
        User.tenant_id == current_user.tenant_id,
        User.role.in_(["teacher", "admin"]),
    ).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    conflict = db.query(Timetable).filter(
        Timetable.tenant_id == current_user.tenant_id,
        Timetable.class_id == class_uuid,
        Timetable.day_of_week == data.day_of_week,
        Timetable.start_time < end_time,
        Timetable.end_time > start_time,
    ).first()
    if conflict:
        raise HTTPException(status_code=409, detail="Time slot overlaps with an existing timetable entry")

    slot = Timetable(
        tenant_id=current_user.tenant_id,
        class_id=class_uuid,
        subject_id=subject_uuid,
        teacher_id=teacher_uuid,
        day_of_week=data.day_of_week,
        start_time=start_time,
        end_time=end_time,
    )
    db.add(slot)
    db.flush()
    db.add(AuditLog(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        action="timetable.slot.created",
        entity_type="timetable",
        entity_id=slot.id,
        metadata_={
            "class_id": str(class_uuid),
            "day_of_week": data.day_of_week,
            "start_time": data.start_time,
            "end_time": data.end_time,
            "subject_id": str(subject_uuid),
            "teacher_id": str(teacher_uuid),
        },
    ))
    db.commit()
    db.refresh(slot)
    return {
        "success": True,
        "id": str(slot.id),
        "class_id": str(slot.class_id),
        "subject_id": str(slot.subject_id),
        "teacher_id": str(slot.teacher_id),
        "day_of_week": slot.day_of_week,
        "start_time": slot.start_time.strftime("%H:%M"),
        "end_time": slot.end_time.strftime("%H:%M"),
    }


@router.delete("/timetable/{slot_id}")
async def delete_timetable_slot(
    slot_id: str,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    slot_uuid = _parse_uuid(slot_id, "slot_id")
    slot = db.query(Timetable).filter(
        Timetable.id == slot_uuid,
        Timetable.tenant_id == current_user.tenant_id,
    ).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Timetable slot not found")

    db.delete(slot)
    db.add(AuditLog(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        action="timetable.slot.deleted",
        entity_type="timetable",
        entity_id=slot_uuid,
        metadata_={
            "class_id": str(slot.class_id),
            "day_of_week": slot.day_of_week,
            "start_time": slot.start_time.strftime("%H:%M"),
            "end_time": slot.end_time.strftime("%H:%M"),
        },
    ))
    db.commit()
    return {"success": True}


@router.get("/parent-links")
async def list_parent_links(current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    links = db.query(ParentLink).filter(
        ParentLink.tenant_id == current_user.tenant_id,
    ).order_by(desc(ParentLink.created_at)).all()

    parent_ids = list({l.parent_id for l in links})
    child_ids = list({l.child_id for l in links})
    users = []
    if parent_ids or child_ids:
        users = db.query(User).filter(
            User.tenant_id == current_user.tenant_id,
            User.id.in_(parent_ids + child_ids),
        ).all()
    name_by_id = {u.id: u.full_name or u.email for u in users}

    return [{
        "id": str(l.id),
        "parent_id": str(l.parent_id),
        "parent_name": name_by_id.get(l.parent_id, "Unknown"),
        "child_id": str(l.child_id),
        "child_name": name_by_id.get(l.child_id, "Unknown"),
        "created_at": str(l.created_at),
    } for l in links]


@router.post("/parent-links")
async def create_parent_link(
    data: ParentLinkCreate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    parent_uuid = _parse_uuid(data.parent_id, "parent_id")
    child_uuid = _parse_uuid(data.child_id, "child_id")

    parent = db.query(User).filter(
        User.id == parent_uuid,
        User.tenant_id == current_user.tenant_id,
        User.role == "parent",
    ).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent user not found")

    child = db.query(User).filter(
        User.id == child_uuid,
        User.tenant_id == current_user.tenant_id,
        User.role == "student",
    ).first()
    if not child:
        raise HTTPException(status_code=404, detail="Student user not found")

    existing = db.query(ParentLink).filter(
        ParentLink.tenant_id == current_user.tenant_id,
        ParentLink.parent_id == parent_uuid,
        ParentLink.child_id == child_uuid,
    ).first()
    if existing:
        return {"success": True, "id": str(existing.id), "already_exists": True}

    link = ParentLink(
        tenant_id=current_user.tenant_id,
        parent_id=parent_uuid,
        child_id=child_uuid,
    )
    db.add(link)
    db.flush()
    db.add(AuditLog(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        action="parent.linked",
        entity_type="parent_link",
        entity_id=link.id,
        metadata_={"parent_id": str(parent_uuid), "child_id": str(child_uuid)},
    ))
    db.commit()
    db.refresh(link)
    return {"success": True, "id": str(link.id)}


@router.delete("/parent-links/{link_id}")
async def delete_parent_link(
    link_id: str,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    link_uuid = _parse_uuid(link_id, "link_id")
    link = db.query(ParentLink).filter(
        ParentLink.id == link_uuid,
        ParentLink.tenant_id == current_user.tenant_id,
    ).first()
    if not link:
        raise HTTPException(status_code=404, detail="Parent link not found")

    db.delete(link)
    db.add(AuditLog(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        action="parent.unlinked",
        entity_type="parent_link",
        entity_id=link_uuid,
    ))
    db.commit()
    return {"success": True}


@router.get("/reports/attendance")
async def attendance_report(current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    """Generate attendance summary grouped by class."""
    classes = db.query(Class).filter(Class.tenant_id == current_user.tenant_id).all()
    report = []
    for cls in classes:
        total = db.query(Attendance).filter(Attendance.tenant_id == current_user.tenant_id, Attendance.class_id == cls.id).count()
        present = db.query(Attendance).filter(Attendance.tenant_id == current_user.tenant_id, Attendance.class_id == cls.id, Attendance.status == "present").count()
        report.append({"class": cls.name, "total_records": total, "present": present, "pct": round(present / total * 100) if total > 0 else 0})
    return report

@router.get("/reports/performance")
async def performance_report(current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    """Generate performance summary grouped by subject."""
    subjects = db.query(Subject).filter(Subject.tenant_id == current_user.tenant_id).all()
    report = []
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
        report.append({"subject": subj.name, "avg_marks": round(float(avg)) if avg else 0, "max_marks": max_m, "pct": round(float(avg) / max_m * 100) if avg and max_m else 0})
    return report

@router.get("/reports/ai-usage")
async def ai_usage_report(current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    """AI usage report."""
    queries = db.query(AIQuery, User.full_name).join(User, AIQuery.user_id == User.id).filter(AIQuery.tenant_id == current_user.tenant_id).order_by(desc(AIQuery.created_at)).limit(200).all()
    return [{"user": name, "query": q.query_text[:100], "mode": q.mode, "tokens": q.token_usage, "time_ms": q.response_time_ms, "date": str(q.created_at)} for q, name in queries]


# ─── Security / Audit Logs ──────────────────────────────────
@router.get("/security")
async def security_logs(current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    logs = db.query(AuditLog, User.full_name).join(User, AuditLog.user_id == User.id).filter(
        AuditLog.tenant_id == current_user.tenant_id,
    ).order_by(desc(AuditLog.created_at)).limit(50).all()
    return [{
        "id": str(log.id), "user": name, "action": log.action,
        "entity_type": log.entity_type, "metadata": log.metadata_,
        "date": str(log.created_at),
    } for log, name in logs]


# ─── Billing ────────────────────────────────────────────────
@router.get("/billing")
async def billing_info(current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    total_queries = db.query(AIQuery).filter(AIQuery.tenant_id == current_user.tenant_id).count()
    total_tokens = db.query(func.sum(AIQuery.token_usage)).filter(AIQuery.tenant_id == current_user.tenant_id).scalar()
    total_docs = db.query(Document).filter(Document.tenant_id == current_user.tenant_id).count()
    return {
        "plan": tenant.plan_tier if tenant else "basic",
        "max_students": tenant.max_students if tenant else 50,
        "ai_daily_limit": tenant.ai_daily_limit if tenant else 50,
        "total_queries": total_queries,
        "total_tokens": total_tokens or 0,
        "total_documents": total_docs,
        "estimated_cost": "Pilot — Free tier",
    }


# ─── Settings ───────────────────────────────────────────────
@router.get("/webhooks")
async def list_webhooks(current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    subs = db.query(WebhookSubscription).filter(
        WebhookSubscription.tenant_id == current_user.tenant_id,
    ).order_by(desc(WebhookSubscription.created_at)).all()
    return [{
        "id": str(s.id),
        "event_type": s.event_type,
        "target_url": s.target_url,
        "is_active": s.is_active,
        "created_at": str(s.created_at),
    } for s in subs]


@router.post("/webhooks")
async def create_webhook(
    data: WebhookCreate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    if data.event_type not in SUPPORTED_WEBHOOK_EVENTS:
        raise HTTPException(status_code=400, detail="Unsupported event_type")
    if not data.target_url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="target_url must be an http/https URL")

    sub = WebhookSubscription(
        tenant_id=current_user.tenant_id,
        event_type=data.event_type,
        target_url=data.target_url.strip(),
        created_by=current_user.id,
        is_active=True,
    )
    db.add(sub)
    db.flush()
    db.add(AuditLog(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        action="webhook.created",
        entity_type="webhook_subscription",
        entity_id=sub.id,
        metadata_={"event_type": sub.event_type, "target_url": sub.target_url, "is_active": sub.is_active},
    ))
    db.commit()
    db.refresh(sub)
    return {
        "success": True,
        "id": str(sub.id),
        "event_type": sub.event_type,
        "target_url": sub.target_url,
        "secret": sub.secret,
    }


@router.patch("/webhooks/{webhook_id}")
async def toggle_webhook(
    webhook_id: str,
    data: WebhookUpdate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    webhook_uuid = _parse_uuid(webhook_id, "webhook_id")
    sub = db.query(WebhookSubscription).filter(
        WebhookSubscription.id == webhook_uuid,
        WebhookSubscription.tenant_id == current_user.tenant_id,
    ).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Webhook not found")
    previous_state = sub.is_active
    sub.is_active = data.is_active
    db.add(AuditLog(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        action="webhook.toggled",
        entity_type="webhook_subscription",
        entity_id=sub.id,
        metadata_={"event_type": sub.event_type, "old": previous_state, "new": sub.is_active},
    ))
    db.commit()
    return {"success": True, "is_active": sub.is_active}


@router.get("/webhooks/{webhook_id}/deliveries")
async def list_webhook_deliveries(
    webhook_id: str,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    webhook_uuid = _parse_uuid(webhook_id, "webhook_id")
    sub = db.query(WebhookSubscription).filter(
        WebhookSubscription.id == webhook_uuid,
        WebhookSubscription.tenant_id == current_user.tenant_id,
    ).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Webhook not found")

    deliveries = db.query(WebhookDelivery).filter(
        WebhookDelivery.tenant_id == current_user.tenant_id,
        WebhookDelivery.subscription_id == webhook_uuid,
    ).order_by(desc(WebhookDelivery.created_at)).limit(100).all()

    return [{
        "id": str(d.id),
        "event_type": d.event_type,
        "status": d.status,
        "status_code": d.status_code,
        "attempt_count": d.attempt_count,
        "last_attempt_at": str(d.last_attempt_at) if d.last_attempt_at else None,
        "created_at": str(d.created_at),
    } for d in deliveries]


@router.delete("/webhooks/{webhook_id}")
async def delete_webhook(
    webhook_id: str,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    webhook_uuid = _parse_uuid(webhook_id, "webhook_id")
    sub = db.query(WebhookSubscription).filter(
        WebhookSubscription.id == webhook_uuid,
        WebhookSubscription.tenant_id == current_user.tenant_id,
    ).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Webhook not found")
    db.add(AuditLog(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        action="webhook.deleted",
        entity_type="webhook_subscription",
        entity_id=sub.id,
        metadata_={"event_type": sub.event_type, "target_url": sub.target_url},
    ))
    db.delete(sub)
    db.commit()
    return {"success": True}


@router.get("/settings")
async def get_settings(current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    return {
        "name": tenant.name if tenant else "",
        "plan_tier": tenant.plan_tier if tenant else "basic",
        "max_students": tenant.max_students if tenant else 50,
        "ai_daily_limit": tenant.ai_daily_limit if tenant else 50,
        "domain": tenant.domain if tenant else "",
    }

class SettingsUpdate(BaseModel):
    ai_daily_limit: Optional[int] = None
    name: Optional[str] = None

@router.patch("/settings")
async def update_settings(data: SettingsUpdate, current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    if data.ai_daily_limit is not None:
        tenant.ai_daily_limit = data.ai_daily_limit
    if data.name:
        tenant.name = data.name
    db.add(AuditLog(tenant_id=current_user.tenant_id, user_id=current_user.id, action="settings.updated", entity_type="tenant", entity_id=tenant.id))
    db.commit()
    return {"success": True}


# ─── Performance Heatmap ────────────────────────────────────
@router.get("/heatmap")
async def performance_heatmap(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Performance heatmap: Subjects × Classes, color-coded by avg score."""
    tid = current_user.tenant_id
    classes = db.query(Class).filter(Class.tenant_id == tid).all()
    subjects = db.query(Subject).filter(Subject.tenant_id == tid).all()

    heatmap = []
    for cls in classes:
        row = {"class": cls.name, "class_id": str(cls.id), "subjects": []}
        for subj in subjects:
            if str(subj.class_id) != str(cls.id):
                continue
            exams = db.query(Exam).filter(
                Exam.tenant_id == tid,
                Exam.subject_id == subj.id,
            ).all()
            if not exams:
                row["subjects"].append({"subject": subj.name, "avg": 0, "color": "gray"})
                continue
            exam_ids = [e.id for e in exams]
            max_marks_val = max(e.max_marks for e in exams)
            avg = db.query(func.avg(Mark.marks_obtained * 100.0 / max_marks_val)).filter(
                Mark.exam_id.in_(exam_ids), Mark.tenant_id == tid
            ).scalar()
            avg_pct = round(float(avg)) if avg else 0
            color = "green" if avg_pct >= 80 else ("yellow" if avg_pct >= 60 else "red")
            row["subjects"].append({"subject": subj.name, "avg": avg_pct, "color": color})
        heatmap.append(row)

    return {"heatmap": heatmap, "classes": len(classes), "subjects": len(subjects)}


# ─── CSV Export Endpoints ───────────────────────────────────
@router.get("/export/attendance")
async def export_attendance_csv(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
    academic_year: str = "",
):
    """Export attendance data as CSV."""
    from starlette.responses import StreamingResponse

    query = db.query(Attendance, User.full_name, Class.name.label("class_name")).join(
        User, Attendance.student_id == User.id
    ).join(
        Class, Attendance.class_id == Class.id
    ).filter(Attendance.tenant_id == current_user.tenant_id)

    records = query.order_by(Attendance.date.desc()).limit(5000).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Student", "Class", "Date", "Status"])
    for att, name, cls_name in records:
        writer.writerow([name, cls_name, str(att.date), att.status])

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=attendance_export.csv"},
    )


@router.get("/export/performance")
async def export_performance_csv(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Export student performance as CSV."""
    from starlette.responses import StreamingResponse

    marks = db.query(Mark, User.full_name, Exam.name.label("exam_name"), Subject.name.label("subject_name")).join(
        User, Mark.student_id == User.id
    ).join(
        Exam, Mark.exam_id == Exam.id
    ).join(
        Subject, Exam.subject_id == Subject.id
    ).filter(Mark.tenant_id == current_user.tenant_id).order_by(User.full_name).limit(5000).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Student", "Subject", "Exam", "Marks Obtained", "Max Marks"])
    for m, name, exam_name, subj_name in marks:
        exam_obj = db.query(Exam).filter(
            Exam.id == m.exam_id,
            Exam.tenant_id == current_user.tenant_id,
        ).first()
        writer.writerow([name, subj_name, exam_name, m.marks_obtained, exam_obj.max_marks if exam_obj else ""])

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=performance_export.csv"},
    )


@router.get("/export/ai-usage")
async def export_ai_usage_csv(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Export AI usage data as CSV."""
    from starlette.responses import StreamingResponse

    queries = db.query(AIQuery, User.full_name).join(
        User, AIQuery.user_id == User.id
    ).filter(AIQuery.tenant_id == current_user.tenant_id).order_by(desc(AIQuery.created_at)).limit(5000).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["User", "Query", "Mode", "Tokens", "Response Time (ms)", "Date"])
    for q, name in queries:
        writer.writerow([name, q.query_text[:200], q.mode, q.token_usage, q.response_time_ms, str(q.created_at)])

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=ai_usage_export.csv"},
    )

