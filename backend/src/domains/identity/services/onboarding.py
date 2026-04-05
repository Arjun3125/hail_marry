"""Self-service tenant onboarding — school registration, class/subject setup, student import."""
import csv
import io
from typing import Optional

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.domains.academic.models.core import Class, Enrollment, Subject
from src.domains.identity.models.tenant import Tenant
from src.domains.identity.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_tenant_with_admin(
    db: Session,
    school_name: str,
    domain: Optional[str],
    admin_email: str,
    admin_name: str,
    password: str,
    plan_tier: str = "basic",
) -> dict:
    """Create a new tenant and its first admin user in a single transaction."""
    # Check for duplicate domain
    if domain:
        existing = db.query(Tenant).filter(Tenant.domain == domain).first()
        if existing:
            raise ValueError(f"Domain '{domain}' is already registered")

    # Check for duplicate admin email
    existing_user = db.query(User).filter(User.email == admin_email).first()
    if existing_user:
        raise ValueError(f"Email '{admin_email}' is already registered")

    tenant = Tenant(
        name=school_name,
        domain=domain,
        plan_tier=plan_tier,
        is_active=1,
    )
    db.add(tenant)
    db.flush()  # Get tenant.id without committing

    admin_user = User(
        tenant_id=tenant.id,
        email=admin_email,
        full_name=admin_name,
        hashed_password=pwd_context.hash(password),
        role="admin",
        is_active=True,
    )
    db.add(admin_user)
    db.commit()
    db.refresh(tenant)
    db.refresh(admin_user)

    return {
        "tenant_id": str(tenant.id),
        "tenant_name": tenant.name,
        "admin_id": str(admin_user.id),
        "admin_email": admin_user.email,
    }


def setup_classes(db: Session, tenant_id, classes_data: list[dict]) -> list[dict]:
    """Bulk-create classes for a tenant.

    classes_data: [{"name": "Class 1", "section": "A"}, ...]
    """
    created = []
    for c in classes_data:
        cls = Class(
            tenant_id=tenant_id,
            name=c["name"],
            section=c.get("section", "A"),
        )
        db.add(cls)
        db.flush()
        created.append({"id": str(cls.id), "name": cls.name, "section": cls.section})
    db.commit()
    return created


def setup_subjects(db: Session, tenant_id, subjects_data: list[dict]) -> list[dict]:
    """Bulk-create subjects for a tenant.

    subjects_data: [{"name": "Mathematics", "code": "MATH"}, ...]
    """
    created = []
    for s in subjects_data:
        subj = Subject(
            tenant_id=tenant_id,
            name=s["name"],
            code=s.get("code", s["name"][:4].upper()),
        )
        db.add(subj)
        db.flush()
        created.append({"id": str(subj.id), "name": subj.name, "code": subj.code})
    db.commit()
    return created


def import_students_from_csv(db: Session, tenant_id, csv_content: str) -> dict:
    """Import students from CSV content.

    Expected CSV columns: full_name, email, class_name
    Returns summary of imported/skipped/errors.
    """
    reader = csv.DictReader(io.StringIO(csv_content))
    imported = 0
    skipped = 0
    errors = []

    for row_num, row in enumerate(reader, start=2):  # Row 1 = header
        name = row.get("full_name", "").strip()
        email = row.get("email", "").strip()
        class_name = row.get("class_name", "").strip()

        if not name or not email:
            errors.append(f"Row {row_num}: missing name or email")
            continue

        # Check for duplicate
        existing = db.query(User).filter(User.email == email, User.tenant_id == tenant_id).first()
        if existing:
            skipped += 1
            continue

        student = User(
            tenant_id=tenant_id,
            email=email,
            full_name=name,
            role="student",
            is_active=True,
        )
        db.add(student)
        db.flush()

        # Find and enroll in class if specified
        if class_name:
            cls = db.query(Class).filter(
                Class.tenant_id == tenant_id,
                Class.name == class_name,
            ).first()
            if cls:
                enrollment = Enrollment(
                    student_id=student.id,
                    class_id=cls.id,
                    tenant_id=tenant_id,
                )
                db.add(enrollment)

        imported += 1

    db.commit()
    return {"imported": imported, "skipped": skipped, "errors": errors}


def get_onboarding_status(db: Session, tenant_id) -> dict:
    """Return onboarding checklist status."""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    admin_count = db.query(User).filter(User.tenant_id == tenant_id, User.role == "admin").count()
    class_count = db.query(Class).filter(Class.tenant_id == tenant_id).count()
    subject_count = db.query(Subject).filter(Subject.tenant_id == tenant_id).count()
    student_count = db.query(User).filter(User.tenant_id == tenant_id, User.role == "student").count()

    return {
        "tenant_created": tenant is not None,
        "admin_created": admin_count > 0,
        "classes_created": class_count > 0,
        "subjects_created": subject_count > 0,
        "students_enrolled": student_count > 0,
        "counts": {
            "admins": admin_count,
            "classes": class_count,
            "subjects": subject_count,
            "students": student_count,
        },
        "completion_pct": sum([
            tenant is not None,
            admin_count > 0,
            class_count > 0,
            subject_count > 0,
            student_count > 0,
        ]) * 20,
    }
