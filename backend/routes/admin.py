"""Admin API routes — dashboard, users, AI usage, AI review, complaints, reports, security, settings."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import date, timedelta, datetime
from pydantic import BaseModel
from typing import Optional
import csv
import io
import re
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File

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
from services.ai_queue import (
    cancel_job,
    drain_queue,
    get_job_detail_for_tenant,
    get_queue_metrics,
    list_jobs_for_tenant,
    move_to_dead_letter,
    pause_queue,
    resume_queue,
    retry_job,
)
from services.alerting import get_active_alerts
from services.observability_notifier import dispatch_alerts
from services.trace_backend import get_trace_events
from services.timetable_generator import generate_timetable
from constants import performance_color

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


def _review_status_from_action(action: str | None) -> str:
    if not action:
        return "pending"
    if action.endswith("approved"):
        return "approved"
    if action.endswith("flagged"):
        return "flagged"
    return "pending"


def _resolve_user_names(db: Session, user_ids: list[str]) -> dict[str, str]:
    ids = []
    for user_id in user_ids:
        if not user_id:
            continue
        try:
            ids.append(UUID(str(user_id)))
        except (TypeError, ValueError):
            continue
    if not ids:
        return {}
    rows = db.query(User.id, User.full_name, User.email).filter(User.id.in_(ids)).all()
    return {
        str(row.id): (row.full_name or row.email or "Unknown")
        for row in rows
    }


def _ai_job_audit_history(
    db: Session,
    *,
    tenant_id: UUID,
    job_id: str | None = None,
    limit: int = 50,
) -> list[dict]:
    query = db.query(AuditLog, User.full_name, User.email).outerjoin(User, AuditLog.user_id == User.id).filter(
        AuditLog.tenant_id == tenant_id,
        AuditLog.entity_type == "ai_job",
    )
    if job_id:
        job_uuid = _parse_uuid(job_id, "job_id")
        query = query.filter(AuditLog.entity_id == job_uuid)
    rows = query.order_by(desc(AuditLog.created_at)).limit(max(1, min(limit, 200))).all()
    history = []
    for row, full_name, email in rows:
        metadata = row.metadata_ or {}
        history.append({
            "action": row.action,
            "actor": full_name or email,
            "created_at": str(row.created_at),
            "metadata": metadata,
            "job_id": str(row.entity_id) if row.entity_id else metadata.get("job_id"),
        })
    return history


def _load_review_history(
    db: Session,
    *,
    tenant_id: UUID,
    query_ids: list[UUID],
) -> tuple[dict[str, list[dict]], dict[str, dict]]:
    if not query_ids:
        return {}, {}
    rows = db.query(AuditLog, User.full_name, User.email).outerjoin(User, AuditLog.user_id == User.id).filter(
        AuditLog.tenant_id == tenant_id,
        AuditLog.entity_type == "ai_review",
        AuditLog.entity_id.in_(query_ids),
    ).order_by(desc(AuditLog.created_at)).all()
    history_map: dict[str, list[dict]] = {str(qid): [] for qid in query_ids}
    latest_map: dict[str, dict] = {}
    for row, full_name, email in rows:
        entry = {
            "action": row.action,
            "note": (row.metadata_ or {}).get("note"),
            "reviewed_by": full_name or email,
            "created_at": str(row.created_at),
        }
        key = str(row.entity_id)
        history_map.setdefault(key, []).append(entry)
        if key not in latest_map:
            latest_map[key] = entry
    return history_map, latest_map


class RoleChange(BaseModel):
    role: str

class ComplaintAction(BaseModel):
    status: str
    resolution_note: str = ""


class AIReviewAction(BaseModel):
    action: str
    note: str | None = None


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
    queue_metrics = {}
    try:
        queue_metrics = get_queue_metrics(str(current_user.tenant_id))
    except Exception:
        queue_metrics = {
            "pending_depth": 0,
            "processing_depth": 0,
            "failure_rate_pct": 0,
            "stuck_jobs": 0,
        }

    observability_alerts = []
    try:
        observability_alerts = get_active_alerts(str(current_user.tenant_id))
    except Exception:
        observability_alerts = []

    return {
        "total_students": total_students, "total_teachers": total_teachers,
        "active_today": active_today, "ai_queries_today": ai_today,
        "avg_attendance": avg_attendance, "avg_performance": round(float(avg_marks)) if avg_marks else 0,
        "open_complaints": open_complaints,
        "queue_pending_depth": queue_metrics.get("pending_depth", 0),
        "queue_processing_depth": queue_metrics.get("processing_depth", 0),
        "queue_failure_rate_pct": queue_metrics.get("failure_rate_pct", 0),
        "queue_stuck_jobs": queue_metrics.get("stuck_jobs", 0),
        "observability_alerts": observability_alerts,
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


@router.get("/students")
async def list_students(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    students = db.query(User).filter(
        User.tenant_id == current_user.tenant_id,
        User.role == "student",
        User.is_deleted == False,
    ).order_by(User.full_name.asc()).all()

    class_by_student: dict[UUID, tuple[UUID | None, str | None]] = {}
    if students:
        ids = [s.id for s in students]
        enrollment_rows = db.query(Enrollment, Class).join(
            Class, Enrollment.class_id == Class.id
        ).filter(
            Enrollment.tenant_id == current_user.tenant_id,
            Enrollment.student_id.in_(ids),
        ).all()
        class_by_student = {
            row[0].student_id: (row[0].class_id, row[1].name)
            for row in enrollment_rows
        }

    return [{
        "id": str(student.id),
        "name": student.full_name or student.email,
        "email": student.email,
        "is_active": student.is_active,
        "class_id": str(class_by_student.get(student.id, (None, None))[0]) if student.id in class_by_student else None,
        "class_name": class_by_student.get(student.id, (None, None))[1],
    } for student in students]

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


# ─── User Authority & Onboarding ────────────────────────────
@router.post("/onboard/teachers")
async def onboard_teachers(
    file: UploadFile = File(...),
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """
    Onboard a list of teachers using either a CSV file or an Image (JPG/PNG).
    CSV Format: name, email, password (optional)
    Image Format: handwritten or printed list of names (one per line). Emails/passwords auto-generated.
    """
    safe_filename = file.filename or ""
    ext = safe_filename.split(".")[-1].lower() if "." in safe_filename else ""
    import tempfile
    import shutil
    import os

    with tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    teachers_to_create = []

    if ext in ("csv", "txt"):
        try:
            with open(tmp_path, "r", encoding="utf-8") as f:
                text = f.read()
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="Invalid text encoding. Please use UTF-8.")
        
        reader = csv.reader(io.StringIO(text))
        for row in reader:
            if not row or not any(row):
                continue
            name = row[0].strip()
            email = row[1].strip() if len(row) > 1 else f"{re.sub(r'[^a-zA-Z0-9]', '.', name.lower())}@example.com"
            password = row[2].strip() if len(row) > 2 else "Teacher123!"
            teachers_to_create.append({"name": name, "email": email, "password": password})
            
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
                    teachers_to_create.append({"name": name, "email": email, "password": "Teacher123!"})
        except Exception:
            os.unlink(tmp_path)
            raise HTTPException(status_code=500, detail="OCR processing failed")
    else:
        os.unlink(tmp_path)
        raise HTTPException(status_code=400, detail="Only CSV, TXT, JPG, JPEG, PNG allowed")
        
    # Cleanup temp file if it wasn't already handled inside the specific blocks
    if os.path.exists(tmp_path):
        os.unlink(tmp_path)

    if not teachers_to_create:
        raise HTTPException(status_code=400, detail="No readable names found in the file")

    try:
        from auth.auth import pwd_context
    except ImportError:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    created_count = 0
    tenant_domain = db.query(Tenant.domain).filter(Tenant.id == current_user.tenant_id).scalar()

    for t in teachers_to_create:
        email = t["email"]
        if "@example.com" in email and tenant_domain:
            email = email.replace("@example.com", f"@{tenant_domain}")

        existing = db.query(User).filter(User.email == email).first()
        if existing:
            continue
            
        hashed_pw = pwd_context.hash(t["password"])
        new_teacher = User(
            tenant_id=current_user.tenant_id,
            email=email,
            full_name=t["name"],
            role="teacher",
            hashed_password=hashed_pw,
            is_active=True
        )
        db.add(new_teacher)
        created_count += 1
        
    db.commit()
    
    return {
        "success": True, 
        "message": f"Successfully onboarded {created_count} teachers.",
        "created_count": created_count
    }


# ─── Queue Operations ─────────────────────────────────────────

@router.post("/queue/pause")
async def pause_ai_queue(current_user: User = Depends(require_role("admin"))):
    """Pause the AI background queue. Workers will stop pulling new jobs."""
    try:
        pause_queue()
        return {"success": True, "message": "Queue paused successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/queue/resume")
async def resume_ai_queue(current_user: User = Depends(require_role("admin"))):
    """Resume the AI background queue."""
    try:
        resume_queue()
        return {"success": True, "message": "Queue resumed successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/queue/drain")
async def drain_ai_queue(current_user: User = Depends(require_role("admin"))):
    """Drain all pending jobs immediately to dead-letter for this tenant."""
    try:
        drained_count = drain_queue(str(current_user.tenant_id))
        return {"success": True, "message": f"Drained {drained_count} jobs.", "drained_count": drained_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── AI Job Management ─────────────────────────────────────────────────────────

@router.get("/ai-jobs/metrics")
async def ai_job_metrics(current_user: User = Depends(require_role("admin"))):
    return get_queue_metrics(str(current_user.tenant_id))


@router.get("/ai-jobs")
async def ai_job_list(
    limit: int = 50,
    status: str | None = None,
    job_type: str | None = None,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    jobs = list_jobs_for_tenant(
        tenant_id=str(current_user.tenant_id),
        limit=limit,
        status=status,
        job_type=job_type,
    )
    user_map = _resolve_user_names(db, [job.get("user_id") for job in jobs])
    for job in jobs:
        job["user_name"] = user_map.get(job.get("user_id"), "Unknown") if job.get("user_id") else None
    return jobs


@router.get("/ai-jobs/history")
async def ai_job_history(
    limit: int = 50,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    return _ai_job_audit_history(db, tenant_id=current_user.tenant_id, limit=limit)


@router.get("/ai-jobs/{job_id}")
async def ai_job_detail(
    job_id: str,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    job = get_job_detail_for_tenant(job_id, str(current_user.tenant_id))
    if not job:
        raise HTTPException(status_code=404, detail="AI job not found")
    user_map = _resolve_user_names(db, [job.get("user_id")])
    job["user_name"] = user_map.get(job.get("user_id"), "Unknown") if job.get("user_id") else None
    job["audit_history"] = _ai_job_audit_history(
        db,
        tenant_id=current_user.tenant_id,
        job_id=job_id,
        limit=100,
    )
    return job


@router.post("/ai-jobs/{job_id}/cancel")
async def ai_job_cancel(
    job_id: str,
    current_user: User = Depends(require_role("admin")),
):
    return cancel_job(job_id, str(current_user.tenant_id), actor_user_id=str(current_user.id))


@router.post("/ai-jobs/{job_id}/retry")
async def ai_job_retry(
    job_id: str,
    current_user: User = Depends(require_role("admin")),
):
    return retry_job(job_id, str(current_user.tenant_id), actor_user_id=str(current_user.id))


@router.post("/ai-jobs/{job_id}/dead-letter")
async def ai_job_dead_letter(
    job_id: str,
    current_user: User = Depends(require_role("admin")),
):
    return move_to_dead_letter(job_id, str(current_user.tenant_id), actor_user_id=str(current_user.id))

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
    query_ids = [q.id for q, _ in recent]
    _, latest_map = _load_review_history(
        db,
        tenant_id=current_user.tenant_id,
        query_ids=query_ids,
    )
    return [{
        **({
            "review_status": _review_status_from_action(latest_map.get(str(q.id), {}).get("action")),
            "review_note": latest_map.get(str(q.id), {}).get("note"),
            "reviewed_at": latest_map.get(str(q.id), {}).get("created_at"),
            "reviewed_by": latest_map.get(str(q.id), {}).get("reviewed_by"),
        }),
        "id": str(q.id), "user": name, "query": q.query_text,
        "response": q.response_text[:500], "mode": q.mode,
        "citations": q.citation_count, "response_time_ms": q.response_time_ms,
        "trace_id": q.trace_id, "created_at": str(q.created_at),
    } for q, name in recent]


@router.get("/ai-review/{review_id}")
async def ai_review_detail(
    review_id: str,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    review_uuid = _parse_uuid(review_id, "review_id")
    row = db.query(AIQuery, User.full_name).join(User, AIQuery.user_id == User.id).filter(
        AIQuery.tenant_id == current_user.tenant_id,
        AIQuery.id == review_uuid,
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="AI review item not found")
    query, name = row
    history_map, latest_map = _load_review_history(
        db,
        tenant_id=current_user.tenant_id,
        query_ids=[query.id],
    )
    latest = latest_map.get(str(query.id), {})
    return {
        "id": str(query.id),
        "user": name,
        "query": query.query_text,
        "response": query.response_text,
        "mode": query.mode,
        "citations": query.citation_count,
        "response_time_ms": query.response_time_ms,
        "trace_id": query.trace_id,
        "created_at": str(query.created_at),
        "token_usage": query.token_usage,
        "review_status": _review_status_from_action(latest.get("action")),
        "review_note": latest.get("note"),
        "reviewed_at": latest.get("created_at"),
        "reviewed_by": latest.get("reviewed_by"),
        "review_history": history_map.get(str(query.id), []),
    }


@router.patch("/ai-review/{review_id}")
async def update_ai_review(
    review_id: str,
    data: AIReviewAction,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    if data.action not in {"approve", "flag"}:
        raise HTTPException(status_code=400, detail="Invalid review action")

    review_uuid = _parse_uuid(review_id, "review_id")
    query = db.query(AIQuery).filter(
        AIQuery.tenant_id == current_user.tenant_id,
        AIQuery.id == review_uuid,
    ).first()
    if not query:
        raise HTTPException(status_code=404, detail="AI review item not found")

    action = "ai_review.approved" if data.action == "approve" else "ai_review.flagged"
    db.add(
        AuditLog(
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            action=action,
            entity_type="ai_review",
            entity_id=query.id,
            metadata_={"note": (data.note or "").strip()},
        )
    )
    db.commit()
    return {"success": True}


# ── Observability ────────────────────────────────────────────────────────────

@router.get("/observability/alerts")
async def observability_alerts(current_user: User = Depends(require_role("admin"))):
    return get_active_alerts(str(current_user.tenant_id))


@router.post("/observability/alerts/dispatch")
async def dispatch_observability_alerts(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    alerts = get_active_alerts(str(current_user.tenant_id))
    result = await dispatch_alerts(db, str(current_user.tenant_id), alerts)
    return {"alerts": len(alerts), **result}


@router.get("/observability/traces/{trace_id}")
async def trace_detail(
    trace_id: str,
    current_user: User = Depends(require_role("admin")),
):
    events = get_trace_events(trace_id, current_user.tenant_id)
    if not events:
        raise HTTPException(status_code=404, detail="Trace not found")
    return {"trace_id": trace_id, "events": events}


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


class TimeSlotRef(BaseModel):
    day: int
    period: int


class TimeGrid(BaseModel):
    days_per_week: int
    periods_per_day: int
    day_start_time: str = "09:00"
    period_minutes: int = 45
    breaks: list[TimeSlotRef] = []


class TeacherAvailability(BaseModel):
    days: list[int] | None = None
    start_period: int | None = None
    end_period: int | None = None
    blocked_slots: list[TimeSlotRef] = []


class TeacherConstraint(BaseModel):
    id: str
    name: str | None = None
    max_periods_per_week: int = 25
    max_periods_per_day: int = 5
    availability: TeacherAvailability | None = None


class TimetableRequirement(BaseModel):
    class_id: str
    subject_id: str
    required_periods_per_week: int
    allowed_teachers: list[str] | None = None


class FixedLesson(BaseModel):
    class_id: str
    subject_id: str
    teacher_id: str
    day: int
    period: int


class TimetableRules(BaseModel):
    no_back_to_back_classes: bool = True
    no_back_to_back_teachers: bool = True


class TimetableGenerateRequest(BaseModel):
    time_grid: TimeGrid
    teachers: list[TeacherConstraint]
    requirements: list[TimetableRequirement]
    fixed_lessons: list[FixedLesson] = []
    rules: TimetableRules = TimetableRules()
    apply_to_db: bool = False
    max_nodes: int | None = None

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


@router.post("/timetable/generate")
async def generate_timetable_schedule(
    data: TimetableGenerateRequest,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Generate a timetable based on constraints and optionally apply it."""
    teacher_ids = {t.id for t in data.teachers}
    if not teacher_ids:
        raise HTTPException(status_code=400, detail="At least one teacher is required")

    class_ids = {r.class_id for r in data.requirements} | {f.class_id for f in data.fixed_lessons}
    subject_ids = {r.subject_id for r in data.requirements} | {f.subject_id for f in data.fixed_lessons}
    fixed_teacher_ids = {f.teacher_id for f in data.fixed_lessons}
    allowed_teacher_ids = set().union(*(r.allowed_teachers or [] for r in data.requirements))
    if not allowed_teacher_ids:
        allowed_teacher_ids = set(teacher_ids)
    missing_in_payload = (allowed_teacher_ids | fixed_teacher_ids) - teacher_ids
    if missing_in_payload:
        raise HTTPException(status_code=400, detail="All allowed/fixed teachers must be included in teachers list")
    all_teacher_ids = teacher_ids | fixed_teacher_ids | allowed_teacher_ids

    if not class_ids or not subject_ids:
        raise HTTPException(status_code=400, detail="Requirements must include class and subject IDs")

    classes = db.query(Class).filter(
        Class.tenant_id == current_user.tenant_id,
        Class.id.in_([_parse_uuid(cid, "class_id") for cid in class_ids]),
    ).all()
    if len(classes) != len(class_ids):
        raise HTTPException(status_code=404, detail="One or more classes not found")

    subjects = db.query(Subject).filter(
        Subject.tenant_id == current_user.tenant_id,
        Subject.id.in_([_parse_uuid(sid, "subject_id") for sid in subject_ids]),
    ).all()
    if len(subjects) != len(subject_ids):
        raise HTTPException(status_code=404, detail="One or more subjects not found")

    teachers = db.query(User).filter(
        User.tenant_id == current_user.tenant_id,
        User.id.in_([_parse_uuid(tid, "teacher_id") for tid in all_teacher_ids]),
        User.role.in_(["teacher", "admin"]),
    ).all()
    if len(teachers) != len(all_teacher_ids):
        raise HTTPException(status_code=404, detail="One or more teachers not found")

    subject_by_id = {str(s.id): s for s in subjects}
    for req in data.requirements:
        subject = subject_by_id.get(req.subject_id)
        if subject and str(subject.class_id) != req.class_id:
            raise HTTPException(status_code=400, detail="Subject does not belong to class")
        if not req.allowed_teachers:
            req.allowed_teachers = list(teacher_ids)

    for fixed in data.fixed_lessons:
        subject = subject_by_id.get(fixed.subject_id)
        if subject and str(subject.class_id) != fixed.class_id:
            raise HTTPException(status_code=400, detail="Fixed lesson subject does not belong to class")

    payload = data.model_dump()
    if data.max_nodes is not None:
        payload["max_nodes"] = data.max_nodes

    result = generate_timetable(payload)
    if result.get("status") != "success":
        return {"success": False, **result}

    assignments = result.get("assignments", [])
    if data.apply_to_db:
        class_uuid_ids = [_parse_uuid(cid, "class_id") for cid in class_ids]
        db.query(Timetable).filter(
            Timetable.tenant_id == current_user.tenant_id,
            Timetable.class_id.in_(class_uuid_ids),
        ).delete(synchronize_session=False)

        for assignment in assignments:
            start_time = _parse_hhmm(assignment["start_time"], "start_time")
            end_time = _parse_hhmm(assignment["end_time"], "end_time")
            db.add(Timetable(
                tenant_id=current_user.tenant_id,
                class_id=_parse_uuid(assignment["class_id"], "class_id"),
                subject_id=_parse_uuid(assignment["subject_id"], "subject_id"),
                teacher_id=_parse_uuid(assignment["teacher_id"], "teacher_id"),
                day_of_week=int(assignment["day"]),
                start_time=start_time,
                end_time=end_time,
            ))

        db.add(AuditLog(
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            action="timetable.generated",
            entity_type="timetable",
            entity_id=None,
            metadata_={
                "classes": [str(cid) for cid in class_ids],
                "slots_created": len(assignments),
            },
        ))
        db.commit()
        return {"success": True, "applied": True, "created": len(assignments), **result}

    return {"success": True, "applied": False, **result}


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
            color = performance_color(avg_pct)
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


# ─── CSV Templates for Setup Wizard ─────────────────────────

CSV_TEMPLATES = {
    "teachers": {
        "filename": "teachers_template.csv",
        "headers": ["full_name", "email", "password"],
        "sample_rows": [
            ["Priya Sharma", "priya@yourschool.com", "Welcome@123"],
            ["Raj Patel", "raj@yourschool.com", "Welcome@123"],
        ],
    },
    "students": {
        "filename": "students_template.csv",
        "headers": ["full_name", "email", "password", "class_name"],
        "sample_rows": [
            ["Ananya Kumari", "ananya@yourschool.com", "Student@123", "Class 9A"],
            ["Vikram Singh", "vikram@yourschool.com", "Student@123", "Class 9B"],
        ],
    },
    "attendance": {
        "filename": "attendance_template.csv",
        "headers": ["student_id", "status"],
        "sample_rows": [
            ["<paste-student-uuid-here>", "present"],
            ["<paste-student-uuid-here>", "absent"],
        ],
    },
    "marks": {
        "filename": "marks_template.csv",
        "headers": ["student_id", "marks_obtained"],
        "sample_rows": [
            ["<paste-student-uuid-here>", "85"],
            ["<paste-student-uuid-here>", "72"],
        ],
    },
}


@router.get("/csv-template/{template_type}")
async def download_csv_template(
    template_type: str,
    current_user: User = Depends(require_role("admin")),
):
    """Download a pre-filled CSV template for bulk import."""
    from starlette.responses import StreamingResponse

    tpl = CSV_TEMPLATES.get(template_type)
    if not tpl:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown template type. Available: {', '.join(CSV_TEMPLATES.keys())}",
        )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(tpl["headers"])
    for row in tpl["sample_rows"]:
        writer.writerow(row)

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={tpl['filename']}"},
    )


# ─── Onboard Students via CSV ───────────────────────────────

@router.post("/onboard-students")
async def onboard_students(
    file: UploadFile = File(...),
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Onboard students from CSV. Columns: full_name, email, password, class_name"""
    safe_filename = file.filename or ""
    ext = safe_filename.split(".")[-1].lower() if "." in safe_filename else ""
    if ext not in ("csv", "txt"):
        raise HTTPException(status_code=400, detail="Only CSV/TXT files allowed.")

    content = await file.read()
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Invalid encoding. Use UTF-8.")

    try:
        from auth.auth import pwd_context as pwctx
    except ImportError:
        from passlib.context import CryptContext
        pwctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

    reader = csv.DictReader(io.StringIO(text))
    created = 0
    errors = []
    for row_num, row in enumerate(reader, start=2):
        name = (row.get("full_name") or "").strip()
        email = (row.get("email") or "").strip().lower()
        password = (row.get("password") or "Student123!").strip()
        class_name = (row.get("class_name") or "").strip()

        if not name or not email:
            errors.append(f"Row {row_num}: missing name or email")
            continue

        existing = db.query(User).filter(User.email == email).first()
        if existing:
            errors.append(f"Row {row_num}: email {email} already exists")
            continue

        # Find class by name if provided
        class_id = None
        if class_name:
            cls = db.query(Class).filter(
                Class.tenant_id == current_user.tenant_id,
                Class.name == class_name,
            ).first()
            if cls:
                class_id = cls.id

        student = User(
            tenant_id=current_user.tenant_id,
            email=email,
            full_name=name,
            role="student",
            hashed_password=pwctx.hash(password),
            is_active=True,
        )
        db.add(student)
        db.flush()

        if class_id:
            enrollment = Enrollment(
                tenant_id=current_user.tenant_id,
                student_id=student.id,
                class_id=class_id,
            )
            db.add(enrollment)

        created += 1

    db.commit()
    return {"success": True, "created": created, "errors": errors}


# ─── QR Code Login Tokens ───────────────────────────────────

class QrTokenBatchRequest(BaseModel):
    student_ids: list[str] | None = None
    class_id: str | None = None
    expires_in_days: int = 30
    regenerate: bool = False


@router.post("/generate-qr-tokens")
async def generate_qr_tokens(
    data: QrTokenBatchRequest | None = None,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Generate QR login tokens for students.
    Supports optional class filtering and token reuse when still valid."""
    import secrets
    from datetime import datetime, timedelta, timezone

    payload = data or QrTokenBatchRequest()
    if payload.expires_in_days <= 0:
        raise HTTPException(status_code=400, detail="expires_in_days must be positive")

    query = db.query(User).filter(
        User.tenant_id == current_user.tenant_id,
        User.role == "student",
        User.is_active == True,
        User.is_deleted == False,
    )

    student_ids: list[UUID] | None = None
    if payload.student_ids:
        student_ids = [_parse_uuid(sid, "student_id") for sid in payload.student_ids]
        query = query.filter(User.id.in_(student_ids))
    elif payload.class_id:
        class_uuid = _parse_uuid(payload.class_id, "class_id")
        enrollments = db.query(Enrollment).filter(
            Enrollment.tenant_id == current_user.tenant_id,
            Enrollment.class_id == class_uuid,
        ).all()
        student_ids = [e.student_id for e in enrollments]
        if not student_ids:
            return {"success": True, "tokens": [], "count": 0}
        query = query.filter(User.id.in_(student_ids))

    students = query.order_by(User.full_name.asc()).all()

    class_by_student: dict[UUID, str] = {}
    if students:
        ids = [s.id for s in students]
        enrollment_rows = db.query(Enrollment, Class).join(
            Class, Enrollment.class_id == Class.id
        ).filter(
            Enrollment.tenant_id == current_user.tenant_id,
            Enrollment.student_id.in_(ids),
        ).all()
        class_by_student = {row[0].student_id: row[1].name for row in enrollment_rows}

    now = datetime.now(timezone.utc)
    expiry = now + timedelta(days=payload.expires_in_days)
    results = []

    for student in students:
        token = student.qr_login_token
        expires_at = student.qr_login_expires_at
        if payload.regenerate or not token or (expires_at and expires_at <= now):
            token = secrets.token_urlsafe(32)
            student.qr_login_token = token
            student.qr_login_expires_at = expiry
            expires_at = expiry
        elif expires_at is None:
            student.qr_login_expires_at = expiry
            expires_at = expiry

        results.append({
            "student_id": str(student.id),
            "student_name": student.full_name,
            "email": student.email,
            "class_name": class_by_student.get(student.id),
            "qr_token": token,
            "expires_at": expires_at.isoformat() if expires_at else None,
            "login_url": f"/api/auth/qr-login/{token}",
        })

    db.commit()
    return {"success": True, "tokens": results, "count": len(results)}


# ─── Report Card PDF ────────────────────────────────────────

@router.get("/report-card/{student_id}")
async def download_report_card(
    student_id: str,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Generate and download a PDF report card for a student."""
    from starlette.responses import Response as StarletteResponse
    from services.report_card import generate_report_card_pdf

    student_uuid = _parse_uuid(student_id, "student_id")
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    school_name = tenant.name if tenant and hasattr(tenant, "name") else "VidyaOS School"

    try:
        pdf_bytes = generate_report_card_pdf(
            db,
            student_id=str(student_uuid),
            tenant_id=str(current_user.tenant_id),
            school_name=school_name,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return StarletteResponse(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=report_card_{student_id}.pdf"},
    )


# ─── WhatsApp Bulk Digest ───────────────────────────────────

class WhatsAppDigestRequest(BaseModel):
    phone_numbers: list[str] | None = None  # if None, send to all parents with phone numbers


@router.post("/whatsapp-digest")
async def send_whatsapp_digest_bulk(
    data: WhatsAppDigestRequest | None = None,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Send weekly digest via WhatsApp to all parents or specified phone numbers."""
    from services.whatsapp import send_weekly_digest
    from models.parent_link import ParentLink

    links = db.query(ParentLink).filter(
        ParentLink.tenant_id == current_user.tenant_id,
    ).all()

    sent = 0
    errors = []
    for link in links:
        parent = db.query(User).filter(User.id == link.parent_id).first()
        child = db.query(User).filter(User.id == link.child_id).first()
        if not parent or not child:
            continue

        # Use parent email as phone placeholder (in production, use a phone field)
        phone = parent.email.split("@")[0] if parent.email else None
        if not phone:
            continue

        # Calculate child stats
        from models.attendance import Attendance
        total_att = db.query(Attendance).filter(
            Attendance.tenant_id == current_user.tenant_id,
            Attendance.student_id == child.id,
        ).count()
        present_att = db.query(Attendance).filter(
            Attendance.tenant_id == current_user.tenant_id,
            Attendance.student_id == child.id,
            Attendance.status == "present",
        ).count()
        att_pct = round(present_att / total_att * 100) if total_att > 0 else 0

        result = await send_weekly_digest(
            to_phone=phone,
            student_name=child.full_name or child.email,
            attendance_pct=att_pct,
            avg_marks=0,
            top_subject="N/A",
            weak_subject="N/A",
        )
        if result.get("success"):
            sent += 1
        else:
            errors.append(f"{parent.email}: {result.get('error', 'Unknown')}")

    return {"success": True, "sent": sent, "errors": errors}
