"""Application helpers for admin onboarding workflows."""

from __future__ import annotations

import csv
import io
import re

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.domains.academic.models.core import Class, Enrollment
from src.domains.identity.models.tenant import Tenant
from src.domains.identity.models.user import User
from src.shared.ocr_imports import make_generated_email


def process_teacher_onboarding_upload(
    *,
    db: Session,
    tenant_id,
    safe_filename: str,
    content: bytes,
    preview: bool,
    get_extension_fn,
    extract_upload_content_result_fn,
    parse_account_rows_with_diagnostics_fn,
    hash_password_fn,
) -> dict:
    ext = get_extension_fn(safe_filename)
    teachers_to_create = []
    ocr_processed = False
    ocr_review_required = False
    ocr_warning = None
    ocr_languages: list[str] = []
    ocr_preprocessing: list[str] = []
    ocr_confidence: float | None = None
    parsed = None

    if ext not in ("csv", "txt", "jpg", "jpeg", "png"):
        raise HTTPException(status_code=400, detail="Only CSV, TXT, JPG, JPEG, PNG allowed")

    try:
        extraction = extract_upload_content_result_fn(safe_filename, content)
    except ValueError as exc:
        detail = str(exc)
        if ext in ("csv", "txt") and "Invalid encoding" in detail:
            detail = "Invalid text encoding. Please use UTF-8."
        raise HTTPException(status_code=400, detail=detail) from exc

    text = extraction.text
    ocr_processed = extraction.used_ocr
    ocr_review_required = extraction.review_required
    ocr_warning = extraction.warning
    ocr_languages = extraction.languages
    ocr_preprocessing = extraction.preprocessing_applied
    ocr_confidence = getattr(extraction, "confidence", None)

    if extraction.used_ocr:
        parsed = parse_account_rows_with_diagnostics_fn(text, default_password="Teacher123!")
        teachers_to_create = [row for _, row in parsed.rows]
        if parsed.review_required:
            ocr_review_required = True
        if parsed.warning:
            ocr_warning = parsed.warning
    else:
        reader = csv.reader(io.StringIO(text))
        for row in reader:
            if not row or not any(row):
                continue
            name = row[0].strip()
            email = row[1].strip() if len(row) > 1 else f"{re.sub(r'[^a-zA-Z0-9]', '.', name.lower())}@example.com"
            password = row[2].strip() if len(row) > 2 else "Teacher123!"
            teachers_to_create.append({"name": name, "email": email, "password": password})

    if not teachers_to_create:
        raise HTTPException(status_code=400, detail="No readable names found in the file")

    response = {
        "ocr_processed": ocr_processed,
        "ocr_review_required": ocr_review_required,
        "ocr_warning": ocr_warning,
        "ocr_languages": ocr_languages,
        "ocr_preprocessing": ocr_preprocessing,
        "ocr_confidence": ocr_confidence,
        "ocr_unmatched_lines": parsed.total_nonempty_lines - len(parsed.rows) if ocr_processed and parsed is not None else 0,
    }

    if preview:
        return {
            "success": True,
            "preview": True,
            "preview_rows": teachers_to_create,
            "total_rows": len(teachers_to_create),
            **response,
        }

    created_count = 0
    tenant_domain = db.query(Tenant.domain).filter(Tenant.id == tenant_id).scalar()

    for teacher in teachers_to_create:
        email = teacher["email"]
        if "@example.com" in email and tenant_domain:
            email = email.replace("@example.com", f"@{tenant_domain}")

        existing = db.query(User).filter(User.email == email).first()
        if existing:
            continue

        new_teacher = User(
            tenant_id=tenant_id,
            email=email,
            full_name=teacher["name"],
            role="teacher",
            hashed_password=hash_password_fn(teacher["password"]),
            is_active=True,
        )
        db.add(new_teacher)
        created_count += 1

    db.commit()
    return {
        "success": True,
        "message": f"Successfully onboarded {created_count} teachers.",
        "created_count": created_count,
        **response,
    }


def process_student_onboarding_upload(
    *,
    db: Session,
    tenant_id,
    safe_filename: str,
    content: bytes,
    preview: bool,
    get_extension_fn,
    extract_upload_content_result_fn,
    parse_student_import_rows_with_diagnostics_fn,
    hash_password_fn,
) -> dict:
    ext = get_extension_fn(safe_filename)
    if ext not in ("csv", "txt", "jpg", "jpeg", "png"):
        raise HTTPException(status_code=400, detail="Only CSV, TXT, JPG, JPEG, PNG files allowed.")

    try:
        extraction = extract_upload_content_result_fn(safe_filename, content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    text = extraction.text
    parsed = None
    if extraction.used_ocr:
        parsed = parse_student_import_rows_with_diagnostics_fn(text)
        source_rows = []
        for row_num, (_, row) in enumerate(parsed.rows, start=2):
            source_rows.append(
                {
                    "row_num": row_num,
                    "full_name": row["full_name"],
                    "email": row["email"],
                    "password": "Student123!",
                    "class_name": row["class_name"],
                }
            )
    else:
        source_rows = []
        reader = csv.DictReader(io.StringIO(text))
        for row_num, row in enumerate(reader, start=2):
            name = (row.get("full_name") or "").strip()
            email = (row.get("email") or "").strip().lower()
            if name and not email:
                email = make_generated_email(name)
            source_rows.append(
                {
                    "row_num": row_num,
                    "full_name": name,
                    "email": email,
                    "password": (row.get("password") or "Student123!").strip(),
                    "class_name": (row.get("class_name") or "").strip(),
                }
            )

    response = {
        "ocr_processed": extraction.used_ocr,
        "ocr_review_required": extraction.review_required,
        "ocr_warning": extraction.warning,
        "ocr_languages": extraction.languages,
        "ocr_preprocessing": extraction.preprocessing_applied,
        "ocr_confidence": getattr(extraction, "confidence", None),
    }
    if parsed is not None:
        response["ocr_review_required"] = extraction.review_required or parsed.review_required
        response["ocr_warning"] = parsed.warning or extraction.warning
        response["ocr_unmatched_lines"] = len(parsed.unmatched_lines)

    if preview:
        preview_errors = []
        for row in source_rows:
            row_num = row["row_num"]
            name = row["full_name"]
            email = row["email"] or make_generated_email(name)
            if not name or not email:
                preview_errors.append(f"Row {row_num}: missing name or email")
                continue
            existing = db.query(User).filter(User.email == email).first()
            if existing:
                preview_errors.append(f"Row {row_num}: email {email} already exists")
        return {
            "success": True,
            "preview": True,
            "preview_rows": source_rows,
            "errors": preview_errors,
            **response,
        }

    created = 0
    errors = []
    for row in source_rows:
        row_num = row["row_num"]
        name = row["full_name"]
        email = row["email"] or make_generated_email(name)
        password = row["password"]
        class_name = row["class_name"]

        if not name or not email:
            errors.append(f"Row {row_num}: missing name or email")
            continue

        existing = db.query(User).filter(User.email == email).first()
        if existing:
            errors.append(f"Row {row_num}: email {email} already exists")
            continue

        class_id = None
        if class_name:
            cls = db.query(Class).filter(
                Class.tenant_id == tenant_id,
                Class.name == class_name,
            ).first()
            if cls:
                class_id = cls.id

        student = User(
            tenant_id=tenant_id,
            email=email,
            full_name=name,
            role="student",
            hashed_password=hash_password_fn(password),
            is_active=True,
        )
        db.add(student)
        db.flush()

        if class_id:
            enrollment = Enrollment(
                tenant_id=tenant_id,
                student_id=student.id,
                class_id=class_id,
            )
            db.add(enrollment)

        created += 1

    db.commit()
    return {
        "success": True,
        "created": created,
        "errors": errors,
        **response,
    }
