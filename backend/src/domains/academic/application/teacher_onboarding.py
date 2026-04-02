"""Application helpers for teacher-managed student onboarding."""

from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass
from typing import Any


@dataclass
class TeacherOnboardingError(Exception):
    status_code: int
    detail: str


async def onboard_students_from_upload(
    *,
    file,
    preview: bool,
    current_user,
    db,
    get_extension_fn,
    extract_upload_content_result_fn,
    parse_account_rows_with_diagnostics_fn,
    user_model,
    tenant_model,
    hash_password_fn,
) -> dict[str, Any]:
    """
    Onboard students from CSV/TXT or OCR image input.

    Preserves route-level behavior and response shape for preview + create flows.
    """
    safe_filename = file.filename or ""
    ext = get_extension_fn(safe_filename)
    content = await file.read()
    students_to_create: list[dict[str, str]] = []
    ocr_processed = False
    ocr_review_required = False
    ocr_warning = None
    ocr_languages: list[str] = []
    ocr_preprocessing: list[str] = []
    ocr_confidence: float | None = None
    parsed = None

    if ext in ("csv", "txt", "jpg", "jpeg", "png"):
        try:
            extraction = extract_upload_content_result_fn(safe_filename, content)
        except ValueError as exc:
            raise TeacherOnboardingError(400, str(exc))

        text = extraction.text
        ocr_processed = extraction.used_ocr
        ocr_review_required = extraction.review_required
        ocr_warning = extraction.warning
        ocr_languages = extraction.languages
        ocr_preprocessing = extraction.preprocessing_applied
        ocr_confidence = getattr(extraction, "confidence", None)

        if extraction.used_ocr:
            parsed = parse_account_rows_with_diagnostics_fn(text, default_password="Student123!")
            students_to_create = [row for _, row in parsed.rows]
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
                email = (
                    row[1].strip()
                    if len(row) > 1
                    else f"{re.sub(r'[^a-zA-Z0-9]', '.', name.lower())}@example.com"
                )
                password = row[2].strip() if len(row) > 2 else "Student123!"
                students_to_create.append({"name": name, "email": email, "password": password})
    else:
        raise TeacherOnboardingError(400, "Only CSV, TXT, JPG, JPEG, PNG allowed")

    if not students_to_create:
        raise TeacherOnboardingError(400, "No readable names found in the file")

    if preview:
        return {
            "success": True,
            "preview": True,
            "preview_rows": students_to_create,
            "total_rows": len(students_to_create),
            "ocr_processed": ocr_processed,
            "ocr_review_required": ocr_review_required,
            "ocr_warning": ocr_warning,
            "ocr_languages": ocr_languages,
            "ocr_preprocessing": ocr_preprocessing,
            "ocr_confidence": ocr_confidence,
            "ocr_unmatched_lines": len(parsed.unmatched_lines) if ocr_processed and parsed is not None else 0,
        }

    created_count = 0
    tenant_domain = db.query(tenant_model.domain).filter(tenant_model.id == current_user.tenant_id).scalar()

    for row in students_to_create:
        email = row["email"]
        if "@example.com" in email and tenant_domain:
            email = email.replace("@example.com", f"@{tenant_domain}")

        existing = db.query(user_model).filter(user_model.email == email).first()
        if existing:
            continue

        new_student = user_model(
            tenant_id=current_user.tenant_id,
            email=email,
            full_name=row["name"],
            role="student",
            hashed_password=hash_password_fn(row["password"]),
            is_active=True,
        )
        db.add(new_student)
        created_count += 1

    db.commit()

    return {
        "success": True,
        "message": f"Successfully onboarded {created_count} students.",
        "created_count": created_count,
        "ocr_processed": ocr_processed,
        "ocr_review_required": ocr_review_required,
        "ocr_warning": ocr_warning,
        "ocr_languages": ocr_languages,
        "ocr_preprocessing": ocr_preprocessing,
        "ocr_confidence": ocr_confidence,
        "ocr_unmatched_lines": len(parsed.unmatched_lines) if ocr_processed and parsed is not None else 0,
    }
