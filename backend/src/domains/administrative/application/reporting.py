"""Application helpers for admin reporting and billing workflows."""

from __future__ import annotations

import csv
import io

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from constants import performance_color
from src.domains.academic.models.attendance import Attendance
from src.domains.academic.models.core import Class, Subject
from src.domains.academic.models.marks import Exam, Mark
from src.domains.identity.models.tenant import Tenant
from src.domains.identity.models.user import User
from src.domains.platform.models.ai import AIQuery
from src.domains.platform.models.audit import AuditLog
from src.domains.platform.models.document import Document


def build_admin_attendance_report(*, db: Session, tenant_id) -> list[dict]:
    classes = db.query(Class).filter(Class.tenant_id == tenant_id).all()
    class_ids = [class_row.id for class_row in classes]
    attendance_rows = (
        db.query(
            Attendance.class_id,
            func.count(Attendance.student_id),
            func.sum(case((Attendance.status == "present", 1), else_=0)),
        )
        .filter(
            Attendance.tenant_id == tenant_id,
            Attendance.class_id.in_(class_ids),
        )
        .group_by(Attendance.class_id)
        .all()
        if class_ids
        else []
    )
    attendance_by_class = {
        class_id: {"total": total or 0, "present": present or 0}
        for class_id, total, present in attendance_rows
    }
    report = []
    for class_row in classes:
        counts = attendance_by_class.get(class_row.id, {"total": 0, "present": 0})
        total = int(counts["total"] or 0)
        present = int(counts["present"] or 0)
        report.append(
            {
                "class": class_row.name,
                "total_records": total,
                "present": present,
                "pct": round(present / total * 100) if total > 0 else 0,
            }
        )
    return report


def build_admin_performance_report(*, db: Session, tenant_id) -> list[dict]:
    subjects = db.query(Subject).filter(Subject.tenant_id == tenant_id).all()
    subject_ids = [subject.id for subject in subjects]
    exams = (
        db.query(Exam)
        .filter(
            Exam.tenant_id == tenant_id,
            Exam.subject_id.in_(subject_ids),
        )
        .all()
        if subject_ids
        else []
    )
    avg_rows = (
        db.query(
            Exam.subject_id,
            func.avg(Mark.marks_obtained),
        )
        .join(Mark, Mark.exam_id == Exam.id)
        .filter(
            Exam.tenant_id == tenant_id,
            Mark.tenant_id == tenant_id,
            Exam.subject_id.in_(subject_ids),
        )
        .group_by(Exam.subject_id)
        .all()
        if subject_ids
        else []
    )
    exams_by_subject: dict[object, list[Exam]] = {}
    for exam in exams:
        exams_by_subject.setdefault(exam.subject_id, []).append(exam)
    avg_by_subject = {subject_id: avg for subject_id, avg in avg_rows}
    report = []
    for subject in subjects:
        subject_exams = exams_by_subject.get(subject.id, [])
        if not subject_exams:
            continue
        avg = avg_by_subject.get(subject.id)
        max_marks = max(exam.max_marks for exam in subject_exams)
        report.append(
            {
                "subject": subject.name,
                "avg_marks": round(float(avg)) if avg else 0,
                "max_marks": max_marks,
                "pct": round(float(avg) / max_marks * 100) if avg and max_marks else 0,
            }
        )
    return report


def build_admin_ai_usage_report(*, db: Session, tenant_id) -> list[dict]:
    queries = db.query(AIQuery, User.full_name).join(
        User,
        AIQuery.user_id == User.id,
    ).filter(
        AIQuery.tenant_id == tenant_id,
    ).order_by(AIQuery.created_at.desc()).limit(200).all()
    return [
        {
            "user": full_name,
            "query": query.query_text[:100],
            "mode": query.mode,
            "tokens": query.token_usage,
            "time_ms": query.response_time_ms,
            "date": str(query.created_at),
        }
        for query, full_name in queries
    ]


def build_admin_security_logs(*, db: Session, tenant_id) -> list[dict]:
    logs = db.query(AuditLog, User.full_name).join(
        User,
        AuditLog.user_id == User.id,
    ).filter(
        AuditLog.tenant_id == tenant_id,
    ).order_by(AuditLog.created_at.desc()).limit(50).all()
    return [
        {
            "id": str(log.id),
            "user": full_name,
            "action": log.action,
            "entity_type": log.entity_type,
            "metadata": log.metadata_,
            "date": str(log.created_at),
        }
        for log, full_name in logs
    ]


def build_admin_billing_info(*, db: Session, tenant_id) -> dict:
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    total_queries = db.query(AIQuery).filter(AIQuery.tenant_id == tenant_id).count()
    total_tokens = db.query(func.sum(AIQuery.token_usage)).filter(
        AIQuery.tenant_id == tenant_id,
    ).scalar()
    total_documents = db.query(Document).filter(Document.tenant_id == tenant_id).count()
    return {
        "plan": tenant.plan_tier if tenant else "basic",
        "max_students": tenant.max_students if tenant else 50,
        "ai_daily_limit": tenant.ai_daily_limit if tenant else 50,
        "total_queries": total_queries,
        "total_tokens": total_tokens or 0,
        "total_documents": total_documents,
        "estimated_cost": "Pilot - Free tier",
    }


def build_admin_performance_heatmap(*, db: Session, tenant_id) -> dict:
    classes = db.query(Class).filter(Class.tenant_id == tenant_id).all()
    subjects = db.query(Subject).filter(Subject.tenant_id == tenant_id).all()
    subject_ids = [subject.id for subject in subjects]
    exams = (
        db.query(Exam)
        .filter(
            Exam.tenant_id == tenant_id,
            Exam.subject_id.in_(subject_ids),
        )
        .all()
        if subject_ids
        else []
    )
    avg_rows = (
        db.query(
            Exam.subject_id,
            func.avg(Mark.marks_obtained),
        )
        .join(Mark, Mark.exam_id == Exam.id)
        .filter(
            Exam.tenant_id == tenant_id,
            Mark.tenant_id == tenant_id,
            Exam.subject_id.in_(subject_ids),
        )
        .group_by(Exam.subject_id)
        .all()
        if subject_ids
        else []
    )
    subjects_by_class: dict[object, list[Subject]] = {}
    for subject in subjects:
        subjects_by_class.setdefault(subject.class_id, []).append(subject)
    exams_by_subject: dict[object, list[Exam]] = {}
    for exam in exams:
        exams_by_subject.setdefault(exam.subject_id, []).append(exam)
    avg_by_subject = {subject_id: avg for subject_id, avg in avg_rows}

    heatmap = []
    for class_row in classes:
        row = {"class": class_row.name, "class_id": str(class_row.id), "subjects": []}
        for subject in subjects_by_class.get(class_row.id, []):
            subject_exams = exams_by_subject.get(subject.id, [])
            if not subject_exams:
                row["subjects"].append({"subject": subject.name, "avg": 0, "color": "gray"})
                continue
            max_marks_val = max(exam.max_marks for exam in subject_exams)
            avg = avg_by_subject.get(subject.id)
            avg_pct = round(float(avg) / max_marks_val * 100) if avg and max_marks_val else 0
            row["subjects"].append(
                {"subject": subject.name, "avg": avg_pct, "color": performance_color(avg_pct)}
            )
        heatmap.append(row)

    return {"heatmap": heatmap, "classes": len(classes), "subjects": len(subjects)}


def build_admin_attendance_csv_export(*, db: Session, tenant_id) -> dict:
    query = db.query(Attendance, User.full_name, Class.name.label("class_name")).join(
        User,
        Attendance.student_id == User.id,
    ).join(
        Class,
        Attendance.class_id == Class.id,
    ).filter(Attendance.tenant_id == tenant_id)

    records = query.order_by(Attendance.date.desc()).limit(5000).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Student", "Class", "Date", "Status"])
    for attendance, name, class_name in records:
        writer.writerow([name, class_name, str(attendance.date), attendance.status])

    output.seek(0)
    return {
        "content": output.getvalue(),
        "filename": "attendance_export.csv",
        "media_type": "text/csv",
    }


def build_admin_performance_csv_export(*, db: Session, tenant_id) -> dict:
    marks = db.query(
        Mark,
        User.full_name,
        Exam.name.label("exam_name"),
        Exam.max_marks.label("exam_max_marks"),
        Subject.name.label("subject_name"),
    ).join(
        User,
        Mark.student_id == User.id,
    ).join(
        Exam,
        Mark.exam_id == Exam.id,
    ).join(
        Subject,
        Exam.subject_id == Subject.id,
    ).filter(
        Mark.tenant_id == tenant_id,
    ).order_by(User.full_name).limit(5000).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Student", "Subject", "Exam", "Marks Obtained", "Max Marks"])
    for mark, name, exam_name, exam_max_marks, subject_name in marks:
        writer.writerow(
            [
                name,
                subject_name,
                exam_name,
                mark.marks_obtained,
                exam_max_marks or "",
            ]
        )

    output.seek(0)
    return {
        "content": output.getvalue(),
        "filename": "performance_export.csv",
        "media_type": "text/csv",
    }


def build_admin_ai_usage_csv_export(*, db: Session, tenant_id) -> dict:
    queries = db.query(AIQuery, User.full_name).join(
        User,
        AIQuery.user_id == User.id,
    ).filter(
        AIQuery.tenant_id == tenant_id,
    ).order_by(AIQuery.created_at.desc()).limit(5000).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["User", "Query", "Mode", "Tokens", "Response Time (ms)", "Date"])
    for query, name in queries:
        writer.writerow(
            [
                name,
                query.query_text[:200],
                query.mode,
                query.token_usage,
                query.response_time_ms,
                str(query.created_at),
            ]
        )

    output.seek(0)
    return {
        "content": output.getvalue(),
        "filename": "ai_usage_export.csv",
        "media_type": "text/csv",
    }
