"""Application helpers for teacher attendance and marks bulk updates."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from src.domains.identity.models.user import User


def apply_bulk_attendance_entries(
    *,
    db: Session,
    current_user: User,
    entries,
    class_uuid: UUID,
    att_date,
    allowed_statuses: set[str],
    validate_student_in_class_fn,
    attendance_model,
) -> int:
    for entry in entries:
        if entry.status not in allowed_statuses:
            raise ValueError(f"Invalid attendance status for student {entry.student_id}")
        student_uuid = validate_student_in_class_fn(
            db,
            current_user,
            entry.student_id,
            class_uuid,
        )
        existing = db.query(attendance_model).filter(
            attendance_model.tenant_id == current_user.tenant_id,
            attendance_model.student_id == student_uuid,
            attendance_model.class_id == class_uuid,
            attendance_model.date == att_date,
        ).first()
        if existing:
            existing.status = entry.status
        else:
            db.add(
                attendance_model(
                    tenant_id=current_user.tenant_id,
                    student_id=student_uuid,
                    class_id=class_uuid,
                    date=att_date,
                    status=entry.status,
                )
            )
    db.commit()
    return len(entries)


def apply_bulk_marks_entries(
    *,
    db: Session,
    current_user: User,
    entries,
    exam,
    subject,
    validate_student_in_class_fn,
    mark_model,
) -> int:
    for entry in entries:
        if entry.marks_obtained < 0 or entry.marks_obtained > exam.max_marks:
            raise ValueError(
                f"Invalid marks for student {entry.student_id}. Must be between 0 and {exam.max_marks}."
            )

        student_uuid = validate_student_in_class_fn(
            db=db,
            current_user=current_user,
            student_id=entry.student_id,
            class_id=subject.class_id,
        )

        existing = db.query(mark_model).filter(
            mark_model.tenant_id == current_user.tenant_id,
            mark_model.exam_id == exam.id,
            mark_model.student_id == student_uuid,
        ).first()
        if existing:
            existing.marks_obtained = entry.marks_obtained
        else:
            db.add(
                mark_model(
                    tenant_id=current_user.tenant_id,
                    student_id=student_uuid,
                    exam_id=exam.id,
                    marks_obtained=entry.marks_obtained,
                )
            )
    db.commit()
    return len(entries)


def apply_structured_attendance_import_rows(
    *,
    db: Session,
    current_user: User,
    rows: list[tuple[str, str]],
    class_uuid: UUID,
    att_date,
    allowed_statuses: set[str],
    resolve_student_identifier_in_class_fn,
    attendance_model,
) -> tuple[int, list[str]]:
    count = 0
    errors: list[str] = []
    for row_num, (identifier, status) in enumerate(rows, start=2):
        if status not in allowed_statuses:
            errors.append(f"Row {row_num}: invalid status '{status}'")
            continue
        try:
            student_uuid = resolve_student_identifier_in_class_fn(
                db,
                current_user,
                identifier,
                class_uuid,
            )
        except Exception:
            errors.append(f"Row {row_num}: student {identifier} not in class")
            continue

        existing = db.query(attendance_model).filter(
            attendance_model.tenant_id == current_user.tenant_id,
            attendance_model.student_id == student_uuid,
            attendance_model.class_id == class_uuid,
            attendance_model.date == att_date,
        ).first()
        if existing:
            existing.status = status
        else:
            db.add(
                attendance_model(
                    tenant_id=current_user.tenant_id,
                    student_id=student_uuid,
                    class_id=class_uuid,
                    date=att_date,
                    status=status,
                )
            )
        count += 1

    db.commit()
    return count, errors


def apply_structured_marks_import_rows(
    *,
    db: Session,
    current_user: User,
    rows: list[tuple[str, int]],
    exam,
    subject,
    resolve_student_identifier_in_class_fn,
    mark_model,
) -> tuple[int, list[str]]:
    count = 0
    errors: list[str] = []
    for row_num, (identifier, marks_val) in enumerate(rows, start=2):
        if marks_val < 0 or marks_val > exam.max_marks:
            errors.append(f"Row {row_num}: marks out of range [0, {exam.max_marks}]")
            continue
        try:
            student_uuid = resolve_student_identifier_in_class_fn(
                db,
                current_user,
                identifier,
                subject.class_id,
            )
        except Exception:
            errors.append(f"Row {row_num}: student {identifier} not in class")
            continue

        existing = db.query(mark_model).filter(
            mark_model.tenant_id == current_user.tenant_id,
            mark_model.exam_id == exam.id,
            mark_model.student_id == student_uuid,
        ).first()
        if existing:
            existing.marks_obtained = marks_val
        else:
            db.add(
                mark_model(
                    tenant_id=current_user.tenant_id,
                    student_id=student_uuid,
                    exam_id=exam.id,
                    marks_obtained=marks_val,
                )
            )
        count += 1

    db.commit()
    return count, errors
