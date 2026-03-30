"""Self-service onboarding API routes — school registration, setup wizard, student import."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
import csv
import io
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from typing import Optional

from auth.dependencies import require_role
from database import get_db
from src.domains.identity.services.onboarding import (
    create_tenant_with_admin,
    get_onboarding_status,
    import_students_from_csv,
    setup_classes,
    setup_subjects,
)
from src.shared.ocr_imports import (
    extract_upload_content_result,
    get_extension,
    parse_student_import_rows_with_diagnostics,
)

router = APIRouter(prefix="/api/onboarding", tags=["Onboarding"])


# ── Request schemas ──

class RegisterSchoolRequest(BaseModel):
    school_name: str
    domain: Optional[str] = None
    admin_email: str
    admin_name: str
    password: str
    plan_tier: str = "basic"


class SetupClassesRequest(BaseModel):
    classes: list[dict]  # [{"name": "Class 1", "section": "A"}]


class SetupSubjectsRequest(BaseModel):
    subjects: list[dict]  # [{"name": "Mathematics", "code": "MATH"}]


# ── Endpoints ──

@router.post("/register")
def register_school(body: RegisterSchoolRequest, db: Session = Depends(get_db)):
    """Register a new school and create the first admin user. Public endpoint."""
    if len(body.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    if not body.school_name.strip():
        raise HTTPException(status_code=400, detail="School name is required")

    try:
        result = create_tenant_with_admin(
            db,
            school_name=body.school_name.strip(),
            domain=body.domain,
            admin_email=body.admin_email.strip(),
            admin_name=body.admin_name.strip(),
            password=body.password,
            plan_tier=body.plan_tier,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))

    return {"status": "registered", **result}


@router.post("/setup-classes")
def setup_school_classes(
    body: SetupClassesRequest,
    user=Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Bulk create classes for the school. Admin only."""
    if not body.classes:
        raise HTTPException(status_code=400, detail="At least one class is required")
    classes = setup_classes(db, user.tenant_id, body.classes)
    return {"created": len(classes), "classes": classes}


@router.post("/setup-subjects")
def setup_school_subjects(
    body: SetupSubjectsRequest,
    user=Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Bulk create subjects for the school. Admin only."""
    if not body.subjects:
        raise HTTPException(status_code=400, detail="At least one subject is required")
    subjects = setup_subjects(db, user.tenant_id, body.subjects)
    return {"created": len(subjects), "subjects": subjects}


@router.post("/import-students")
async def import_students(
    file: UploadFile = File(...),
    user=Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Import students from CSV/TXT or OCR image. Admin only.

    CSV columns: full_name, email, class_name (optional)
    """
    filename = file.filename or ""
    ext = get_extension(filename)
    if ext not in {"csv", "txt", "jpg", "jpeg", "png"}:
        raise HTTPException(status_code=400, detail="Only CSV, TXT, JPG, JPEG, PNG files are accepted")

    content = await file.read()
    try:
        extraction = extract_upload_content_result(filename, content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    parsed = None
    if extraction.used_ocr:
        parsed = parse_student_import_rows_with_diagnostics(extraction.text)
        if not parsed.rows:
            raise HTTPException(status_code=400, detail="No readable student rows found in the image.")
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["full_name", "email", "class_name"])
        for _, row in parsed.rows:
            writer.writerow([row["full_name"], row["email"], row["class_name"]])
        csv_text = output.getvalue()
    else:
        csv_text = extraction.text

    result = import_students_from_csv(db, user.tenant_id, csv_text)
    response = {
        "status": "import_complete",
        "imported": result["imported"],
        "skipped": result["skipped"],
        "errors": result["errors"],
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
    return response


@router.get("/status")
def onboarding_checklist(
    user=Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Get onboarding completion checklist. Admin only."""
    status = get_onboarding_status(db, user.tenant_id)
    return {"onboarding": status}
