"""Application helpers for admin user management and QR token workflows."""

from __future__ import annotations

import csv
import io
import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.domains.academic.models.core import Class, Enrollment
from src.domains.identity.models.user import User
from src.domains.platform.models.ai import AIQuery
from src.domains.platform.models.audit import AuditLog

ALLOWED_USER_ROLES = ("student", "teacher", "admin", "parent")

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


def build_admin_users_response(*, db: Session, tenant_id) -> list[dict]:
    users = db.query(User).filter(
        User.tenant_id == tenant_id,
        User.is_deleted.is_(False),
    ).order_by(User.created_at.desc()).all()

    user_ids = [user.id for user in users]
    ai_queries_30d_by_user: dict[UUID, int] = {}
    if user_ids:
        count_rows = db.query(
            AIQuery.user_id,
            func.count(AIQuery.id),
        ).filter(
            AIQuery.tenant_id == tenant_id,
            AIQuery.user_id.in_(user_ids),
        ).group_by(AIQuery.user_id).all()
        ai_queries_30d_by_user = {row[0]: int(row[1] or 0) for row in count_rows}

    return [
        {
            "id": str(user.id),
            "name": user.full_name,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "last_login": str(user.last_login) if user.last_login else None,
            "ai_queries_30d": ai_queries_30d_by_user.get(user.id, 0),
        }
        for user in users
    ]


def build_admin_students_response(*, db: Session, tenant_id) -> list[dict]:
    students = db.query(User).filter(
        User.tenant_id == tenant_id,
        User.role == "student",
        User.is_deleted.is_(False),
    ).order_by(User.full_name.asc()).all()

    class_by_student: dict[UUID, tuple[UUID | None, str | None]] = {}
    if students:
        student_ids = [student.id for student in students]
        enrollment_rows = db.query(Enrollment, Class).join(
            Class, Enrollment.class_id == Class.id
        ).filter(
            Enrollment.tenant_id == tenant_id,
            Enrollment.student_id.in_(student_ids),
        ).all()
        class_by_student = {
            row[0].student_id: (row[0].class_id, row[1].name)
            for row in enrollment_rows
        }

    return [
        {
            "id": str(student.id),
            "name": student.full_name or student.email,
            "email": student.email,
            "is_active": student.is_active,
            "class_id": (
                str(class_by_student.get(student.id, (None, None))[0])
                if student.id in class_by_student
                else None
            ),
            "class_name": class_by_student.get(student.id, (None, None))[1],
        }
        for student in students
    ]


def change_admin_user_role(
    *,
    db: Session,
    tenant_id,
    actor_user_id,
    user_id: str,
    role: str,
    parse_uuid_fn,
) -> dict:
    user_uuid = parse_uuid_fn(user_id, "user_id")
    user = db.query(User).filter(
        User.id == user_uuid,
        User.tenant_id == tenant_id,
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if role not in ALLOWED_USER_ROLES:
        raise HTTPException(status_code=400, detail="Invalid role")

    old_role = user.role
    user.role = role
    db.add(
        AuditLog(
            tenant_id=tenant_id,
            user_id=actor_user_id,
            action="role.changed",
            entity_type="user",
            entity_id=user.id,
            metadata_={"old": old_role, "new": role},
        )
    )
    db.commit()
    return {"success": True}


def toggle_admin_user_active(
    *,
    db: Session,
    tenant_id,
    actor_user_id,
    user_id: str,
    parse_uuid_fn,
) -> dict:
    user_uuid = parse_uuid_fn(user_id, "user_id")
    user = db.query(User).filter(
        User.id == user_uuid,
        User.tenant_id == tenant_id,
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = not user.is_active
    db.add(
        AuditLog(
            tenant_id=tenant_id,
            user_id=actor_user_id,
            action="user.toggled",
            entity_type="user",
            entity_id=user.id,
            metadata_={"is_active": user.is_active},
        )
    )
    db.commit()
    return {"success": True, "is_active": user.is_active}


def build_admin_csv_template_payload(*, template_type: str) -> dict:
    template = CSV_TEMPLATES.get(template_type)
    if not template:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown template type. Available: {', '.join(CSV_TEMPLATES.keys())}",
        )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(template["headers"])
    for row in template["sample_rows"]:
        writer.writerow(row)
    output.seek(0)

    return {
        "filename": template["filename"],
        "content": output.getvalue(),
        "media_type": "text/csv",
    }


def generate_admin_qr_tokens(
    *,
    db: Session,
    tenant_id,
    student_ids: list[str] | None,
    class_id: str | None,
    expires_in_days: int,
    regenerate: bool,
    parse_uuid_fn,
) -> dict:
    if expires_in_days <= 0:
        raise HTTPException(status_code=400, detail="expires_in_days must be positive")

    query = db.query(User).filter(
        User.tenant_id == tenant_id,
        User.role == "student",
        User.is_active,
        User.is_deleted.is_(False),
    )

    parsed_student_ids: list[UUID] | None = None
    if student_ids:
        parsed_student_ids = [parse_uuid_fn(student_id, "student_id") for student_id in student_ids]
        query = query.filter(User.id.in_(parsed_student_ids))
    elif class_id:
        class_uuid = parse_uuid_fn(class_id, "class_id")
        enrollments = db.query(Enrollment).filter(
            Enrollment.tenant_id == tenant_id,
            Enrollment.class_id == class_uuid,
        ).all()
        parsed_student_ids = [enrollment.student_id for enrollment in enrollments]
        if not parsed_student_ids:
            return {"success": True, "tokens": [], "count": 0}
        query = query.filter(User.id.in_(parsed_student_ids))

    students = query.order_by(User.full_name.asc()).all()

    class_by_student: dict[UUID, str] = {}
    if students:
        student_ids_for_lookup = [student.id for student in students]
        enrollment_rows = db.query(Enrollment, Class).join(
            Class, Enrollment.class_id == Class.id
        ).filter(
            Enrollment.tenant_id == tenant_id,
            Enrollment.student_id.in_(student_ids_for_lookup),
        ).all()
        class_by_student = {
            row[0].student_id: row[1].name
            for row in enrollment_rows
        }

    now = datetime.now(timezone.utc)
    expires_at_default = now + timedelta(days=expires_in_days)
    tokens_payload = []

    for student in students:
        token = student.qr_login_token
        expires_at = student.qr_login_expires_at
        if regenerate or not token or (expires_at and expires_at <= now):
            token = secrets.token_urlsafe(32)
            student.qr_login_token = token
            student.qr_login_expires_at = expires_at_default
            expires_at = expires_at_default
        elif expires_at is None:
            student.qr_login_expires_at = expires_at_default
            expires_at = expires_at_default

        tokens_payload.append(
            {
                "student_id": str(student.id),
                "student_name": student.full_name,
                "email": student.email,
                "class_name": class_by_student.get(student.id),
                "qr_token": token,
                "expires_at": expires_at.isoformat() if expires_at else None,
                "login_url": f"/api/auth/qr-login/{token}",
            }
        )

    db.commit()
    return {"success": True, "tokens": tokens_payload, "count": len(tokens_payload)}
