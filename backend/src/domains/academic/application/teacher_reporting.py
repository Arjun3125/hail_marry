"""Application helpers for teacher exports, grading queue, and test series."""

from __future__ import annotations

import csv
import io
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4


def _parse_uuid(value: str | None, field_name: str) -> UUID | None:
    if value is None:
        return None
    try:
        return UUID(str(value))
    except (TypeError, ValueError):
        raise ValueError(f"Invalid {field_name}")


def build_attendance_csv_payload(
    *,
    db,
    current_user,
    class_uuid,
    requested_class_id: str,
    attendance_model,
    user_model,
) -> dict[str, str]:
    records = (
        db.query(attendance_model)
        .filter(
            attendance_model.tenant_id == current_user.tenant_id,
            attendance_model.class_id == class_uuid,
        )
        .order_by(attendance_model.date.desc())
        .all()
    )

    student_ids = list({record.student_id for record in records})
    users = db.query(user_model).filter(user_model.id.in_(student_ids)).all() if student_ids else []
    name_map = {user.id: user.full_name for user in users}

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["student_id", "student_name", "date", "status"])
    for record in records:
        writer.writerow(
            [
                str(record.student_id),
                name_map.get(record.student_id, ""),
                str(record.date),
                record.status,
            ]
        )
    return {
        "filename": f"attendance_{requested_class_id}.csv",
        "content": output.getvalue(),
    }


def build_marks_csv_payload(
    *,
    db,
    current_user,
    exam,
    requested_exam_id: str,
    mark_model,
    user_model,
) -> dict[str, str]:
    marks = (
        db.query(mark_model)
        .filter(
            mark_model.tenant_id == current_user.tenant_id,
            mark_model.exam_id == exam.id,
        )
        .all()
    )

    student_ids = [mark.student_id for mark in marks]
    users = db.query(user_model).filter(user_model.id.in_(student_ids)).all() if student_ids else []
    name_map = {user.id: user.full_name for user in users}

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["student_id", "student_name", "marks_obtained", "max_marks"])
    for mark in marks:
        writer.writerow(
            [
                str(mark.student_id),
                name_map.get(mark.student_id, ""),
                mark.marks_obtained,
                exam.max_marks,
            ]
        )
    return {
        "filename": f"marks_{requested_exam_id}.csv",
        "content": output.getvalue(),
    }


def queue_teacher_ai_grade_job(
    *,
    file_name: str,
    content: bytes,
    current_user,
    max_file_size: int,
    upload_dir,
    enqueue_job_fn,
    exam_id: str | None = None,
    exam_name: str | None = None,
    exam_max_marks: int | None = None,
    student_id: str | None = None,
    student_name: str | None = None,
    answer_key: str | None = None,
    rubric: str | None = None,
) -> dict[str, Any]:
    safe_filename = Path(file_name or "").name
    if not safe_filename:
        raise ValueError("Filename is required.")

    ext = safe_filename.split(".")[-1].lower() if "." in safe_filename else ""
    if ext not in {"jpg", "jpeg", "png", "pdf"}:
        raise ValueError("Only JPG, JPEG, PNG, PDF files allowed.")

    if len(content) > max_file_size:
        raise ValueError("File exceeds 50MB limit.")

    file_path = upload_dir / f"{current_user.tenant_id}_grade_{uuid4().hex}_{safe_filename}"
    with open(file_path, "wb") as output_file:
        output_file.write(content)

    job = enqueue_job_fn(
        job_type="ai_grade",
        payload={
            "file_path": str(file_path),
            "file_name": safe_filename,
            "teacher_id": str(current_user.id),
            "exam_id": exam_id,
            "exam_name": exam_name,
            "exam_max_marks": exam_max_marks,
            "student_id": student_id,
            "student_name": student_name,
            "answer_key": answer_key,
            "rubric": rubric,
        },
        tenant_id=str(current_user.tenant_id),
        user_id=str(current_user.id),
    )

    job_id = job.get("job_id") if isinstance(job, dict) else str(job)

    return {
        "success": True,
        "message": "Answer sheet queued for AI grading.",
        "job_id": job_id,
        "file_name": safe_filename,
    }


def build_created_test_series_response(
    *,
    db,
    current_user,
    name: str,
    description: str,
    total_marks: int,
    duration_minutes: int,
    class_id: str | None,
    subject_id: str | None,
    test_series_model,
    class_model,
    subject_model,
) -> dict[str, Any]:
    class_uuid = _parse_uuid(class_id, "class_id")
    subject_uuid = _parse_uuid(subject_id, "subject_id")

    if class_uuid is not None:
        school_class = db.query(class_model).filter(
            class_model.id == class_uuid,
            class_model.tenant_id == current_user.tenant_id,
        ).first()
        if school_class is None:
            raise ValueError("Class not found")

    if subject_uuid is not None:
        subject = db.query(subject_model).filter(
            subject_model.id == subject_uuid,
            subject_model.tenant_id == current_user.tenant_id,
        ).first()
        if subject is None:
            raise ValueError("Subject not found")
        if class_uuid is not None and subject.class_id != class_uuid:
            raise ValueError("Subject does not belong to the selected class")
        if class_uuid is None:
            class_uuid = subject.class_id

    series = test_series_model(
        tenant_id=current_user.tenant_id,
        name=name,
        description=description,
        total_marks=total_marks,
        duration_minutes=duration_minutes,
        class_id=class_uuid,
        subject_id=subject_uuid,
        assessment_kind="mock_test",
        grading_mode="manual_review",
        status="published",
        published_at=datetime.now(timezone.utc),
        created_by=current_user.id,
    )
    db.add(series)
    db.commit()
    db.refresh(series)
    return {
        "success": True,
        "series_id": str(series.id),
        "name": series.name,
        "status": series.status,
        "published_at": series.published_at.isoformat() if series.published_at else None,
    }


def list_teacher_test_series_response(
    *,
    db,
    current_user,
    get_all_series_fn,
):
    return get_all_series_fn(db, tenant_id=str(current_user.tenant_id))


def build_teacher_test_series_leaderboard_response(
    *,
    db,
    current_user,
    series_id: str,
    get_leaderboard_fn,
):
    return get_leaderboard_fn(db, test_series_id=series_id, tenant_id=str(current_user.tenant_id))
