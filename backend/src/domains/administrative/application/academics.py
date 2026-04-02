"""Application helpers for admin class, subject, and timetable workflows."""

from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.domains.academic.models.timetable import Timetable
from src.domains.academic.models.core import Class, Enrollment, Subject
from src.domains.identity.models.user import User
from src.domains.platform.models.audit import AuditLog


def build_admin_classes_response(
    *,
    db: Session,
    tenant_id,
) -> list[dict]:
    classes = db.query(Class).filter(Class.tenant_id == tenant_id).all()
    return [
        {
            "id": str(class_row.id),
            "name": class_row.name,
            "grade": class_row.grade_level,
            "students": db.query(Enrollment).filter(
                Enrollment.tenant_id == tenant_id,
                Enrollment.class_id == class_row.id,
            ).count(),
            "subjects": [
                {"id": str(subject.id), "name": subject.name}
                for subject in db.query(Subject).filter(
                    Subject.tenant_id == tenant_id,
                    Subject.class_id == class_row.id,
                ).all()
            ],
        }
        for class_row in classes
    ]


def create_admin_class(
    *,
    db: Session,
    tenant_id,
    actor_user_id,
    name: str,
    grade_level: str,
    academic_year: str,
) -> dict:
    class_row = Class(
        tenant_id=tenant_id,
        name=name,
        grade_level=grade_level,
        academic_year=academic_year,
    )
    db.add(class_row)
    if hasattr(db, "flush"):
        db.flush()
    db.add(
        AuditLog(
            tenant_id=tenant_id,
            user_id=actor_user_id,
            action="class.created",
            entity_type="class",
            entity_id=class_row.id,
            metadata_={
                "name": class_row.name,
                "grade_level": class_row.grade_level,
                "academic_year": class_row.academic_year,
            },
        )
    )
    db.commit()
    if hasattr(db, "refresh"):
        db.refresh(class_row)
    return {"success": True, "class_id": str(class_row.id)}


def create_admin_subject(
    *,
    db: Session,
    tenant_id,
    actor_user_id,
    name: str,
    class_id: str,
    parse_uuid_fn,
) -> dict:
    class_uuid = parse_uuid_fn(class_id, "class_id")
    class_row = db.query(Class).filter(
        Class.id == class_uuid,
        Class.tenant_id == tenant_id,
    ).first()
    if not class_row:
        raise HTTPException(status_code=404, detail="Class not found")

    subject = Subject(tenant_id=tenant_id, name=name, class_id=class_uuid)
    db.add(subject)
    if hasattr(db, "flush"):
        db.flush()
    db.add(
        AuditLog(
            tenant_id=tenant_id,
            user_id=actor_user_id,
            action="subject.created",
            entity_type="subject",
            entity_id=subject.id,
            metadata_={"name": subject.name, "class_id": str(class_uuid)},
        )
    )
    db.commit()
    return {"success": True, "subject_id": str(subject.id)}


def build_admin_timetable_response(
    *,
    db: Session,
    tenant_id,
    class_id: str,
    parse_uuid_fn,
) -> list[dict]:
    class_uuid = parse_uuid_fn(class_id, "class_id")
    class_row = db.query(Class).filter(
        Class.id == class_uuid,
        Class.tenant_id == tenant_id,
    ).first()
    if not class_row:
        raise HTTPException(status_code=404, detail="Class not found")

    slots = db.query(Timetable).filter(
        Timetable.tenant_id == tenant_id,
        Timetable.class_id == class_uuid,
    ).order_by(Timetable.day_of_week, Timetable.start_time).all()

    subject_ids = list({slot.subject_id for slot in slots})
    teacher_ids = list({slot.teacher_id for slot in slots})
    subjects = []
    teachers = []
    if subject_ids:
        subjects = db.query(Subject).filter(
            Subject.tenant_id == tenant_id,
            Subject.id.in_(subject_ids),
        ).all()
    if teacher_ids:
        teachers = db.query(User).filter(
            User.tenant_id == tenant_id,
            User.id.in_(teacher_ids),
        ).all()
    subject_name_by_id = {subject.id: subject.name for subject in subjects}
    teacher_name_by_id = {teacher.id: (teacher.full_name or teacher.email) for teacher in teachers}

    return [
        {
            "id": str(slot.id),
            "class_id": str(slot.class_id),
            "subject_id": str(slot.subject_id),
            "subject": subject_name_by_id.get(slot.subject_id, "Unknown"),
            "teacher_id": str(slot.teacher_id),
            "teacher": teacher_name_by_id.get(slot.teacher_id, "Unknown"),
            "day_of_week": slot.day_of_week,
            "start_time": slot.start_time.strftime("%H:%M"),
            "end_time": slot.end_time.strftime("%H:%M"),
        }
        for slot in slots
    ]


def create_admin_timetable_slot(
    *,
    db: Session,
    tenant_id,
    actor_user_id,
    class_id: str,
    subject_id: str,
    teacher_id: str,
    day_of_week: int,
    start_time_raw: str,
    end_time_raw: str,
    parse_uuid_fn,
    parse_hhmm_fn,
) -> dict:
    class_uuid = parse_uuid_fn(class_id, "class_id")
    subject_uuid = parse_uuid_fn(subject_id, "subject_id")
    teacher_uuid = parse_uuid_fn(teacher_id, "teacher_id")

    if day_of_week < 0 or day_of_week > 6:
        raise HTTPException(status_code=400, detail="day_of_week must be between 0 and 6")

    start_time = parse_hhmm_fn(start_time_raw, "start_time")
    end_time = parse_hhmm_fn(end_time_raw, "end_time")
    if start_time >= end_time:
        raise HTTPException(status_code=400, detail="start_time must be before end_time")

    class_row = db.query(Class).filter(
        Class.id == class_uuid,
        Class.tenant_id == tenant_id,
    ).first()
    if not class_row:
        raise HTTPException(status_code=404, detail="Class not found")

    subject = db.query(Subject).filter(
        Subject.id == subject_uuid,
        Subject.tenant_id == tenant_id,
    ).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    if subject.class_id != class_uuid:
        raise HTTPException(status_code=400, detail="Subject does not belong to class")

    teacher = db.query(User).filter(
        User.id == teacher_uuid,
        User.tenant_id == tenant_id,
        User.role.in_(["teacher", "admin"]),
    ).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    conflict = db.query(Timetable).filter(
        Timetable.tenant_id == tenant_id,
        Timetable.class_id == class_uuid,
        Timetable.day_of_week == day_of_week,
        Timetable.start_time < end_time,
        Timetable.end_time > start_time,
    ).first()
    if conflict:
        raise HTTPException(status_code=409, detail="Time slot overlaps with an existing timetable entry")

    slot = Timetable(
        tenant_id=tenant_id,
        class_id=class_uuid,
        subject_id=subject_uuid,
        teacher_id=teacher_uuid,
        day_of_week=day_of_week,
        start_time=start_time,
        end_time=end_time,
    )
    db.add(slot)
    if hasattr(db, "flush"):
        db.flush()
    db.add(
        AuditLog(
            tenant_id=tenant_id,
            user_id=actor_user_id,
            action="timetable.slot.created",
            entity_type="timetable",
            entity_id=slot.id,
            metadata_={
                "class_id": str(class_uuid),
                "day_of_week": day_of_week,
                "start_time": start_time_raw,
                "end_time": end_time_raw,
                "subject_id": str(subject_uuid),
                "teacher_id": str(teacher_uuid),
            },
        )
    )
    db.commit()
    if hasattr(db, "refresh"):
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


def delete_admin_timetable_slot(
    *,
    db: Session,
    tenant_id,
    actor_user_id,
    slot_id: str,
    parse_uuid_fn,
) -> dict:
    slot_uuid = parse_uuid_fn(slot_id, "slot_id")
    slot = db.query(Timetable).filter(
        Timetable.id == slot_uuid,
        Timetable.tenant_id == tenant_id,
    ).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Timetable slot not found")

    db.delete(slot)
    db.add(
        AuditLog(
            tenant_id=tenant_id,
            user_id=actor_user_id,
            action="timetable.slot.deleted",
            entity_type="timetable",
            entity_id=slot_uuid,
            metadata_={
                "class_id": str(slot.class_id),
                "day_of_week": slot.day_of_week,
                "start_time": slot.start_time.strftime("%H:%M"),
                "end_time": slot.end_time.strftime("%H:%M"),
            },
        )
    )
    db.commit()
    return {"success": True}


def generate_admin_timetable_schedule(
    *,
    db: Session,
    tenant_id,
    actor_user_id,
    data,
    parse_uuid_fn,
    parse_hhmm_fn,
    generate_timetable_fn,
) -> dict:
    teacher_ids = {teacher.id for teacher in data.teachers}
    if not teacher_ids:
        raise HTTPException(status_code=400, detail="At least one teacher is required")

    class_ids = {req.class_id for req in data.requirements} | {
        lesson.class_id for lesson in data.fixed_lessons
    }
    subject_ids = {req.subject_id for req in data.requirements} | {
        lesson.subject_id for lesson in data.fixed_lessons
    }
    fixed_teacher_ids = {lesson.teacher_id for lesson in data.fixed_lessons}
    allowed_teacher_ids = set().union(*(req.allowed_teachers or [] for req in data.requirements))
    if not allowed_teacher_ids:
        allowed_teacher_ids = set(teacher_ids)
    missing_in_payload = (allowed_teacher_ids | fixed_teacher_ids) - teacher_ids
    if missing_in_payload:
        raise HTTPException(
            status_code=400,
            detail="All allowed/fixed teachers must be included in teachers list",
        )
    all_teacher_ids = teacher_ids | fixed_teacher_ids | allowed_teacher_ids

    if not class_ids or not subject_ids:
        raise HTTPException(status_code=400, detail="Requirements must include class and subject IDs")

    class_uuid_ids = [parse_uuid_fn(class_id, "class_id") for class_id in class_ids]
    classes = db.query(Class).filter(
        Class.tenant_id == tenant_id,
        Class.id.in_(class_uuid_ids),
    ).all()
    if len(classes) != len(class_ids):
        raise HTTPException(status_code=404, detail="One or more classes not found")

    subject_uuid_ids = [parse_uuid_fn(subject_id, "subject_id") for subject_id in subject_ids]
    subjects = db.query(Subject).filter(
        Subject.tenant_id == tenant_id,
        Subject.id.in_(subject_uuid_ids),
    ).all()
    if len(subjects) != len(subject_ids):
        raise HTTPException(status_code=404, detail="One or more subjects not found")

    teacher_uuid_ids = [parse_uuid_fn(teacher_id, "teacher_id") for teacher_id in all_teacher_ids]
    teachers = db.query(User).filter(
        User.tenant_id == tenant_id,
        User.id.in_(teacher_uuid_ids),
        User.role.in_(["teacher", "admin"]),
    ).all()
    if len(teachers) != len(all_teacher_ids):
        raise HTTPException(status_code=404, detail="One or more teachers not found")

    subject_by_id = {str(subject.id): subject for subject in subjects}
    for req in data.requirements:
        subject = subject_by_id.get(req.subject_id)
        if subject and str(subject.class_id) != req.class_id:
            raise HTTPException(status_code=400, detail="Subject does not belong to class")
        if not req.allowed_teachers:
            req.allowed_teachers = list(teacher_ids)

    for fixed in data.fixed_lessons:
        subject = subject_by_id.get(fixed.subject_id)
        if subject and str(subject.class_id) != fixed.class_id:
            raise HTTPException(
                status_code=400,
                detail="Fixed lesson subject does not belong to class",
            )

    payload = data.model_dump()
    if data.max_nodes is not None:
        payload["max_nodes"] = data.max_nodes

    result = generate_timetable_fn(payload)
    if result.get("status") != "success":
        return {"success": False, **result}

    assignments = result.get("assignments", [])
    if not data.apply_to_db:
        return {"success": True, "applied": False, **result}

    db.query(Timetable).filter(
        Timetable.tenant_id == tenant_id,
        Timetable.class_id.in_(class_uuid_ids),
    ).delete(synchronize_session=False)

    for assignment in assignments:
        start_time = parse_hhmm_fn(assignment["start_time"], "start_time")
        end_time = parse_hhmm_fn(assignment["end_time"], "end_time")
        db.add(
            Timetable(
                tenant_id=tenant_id,
                class_id=parse_uuid_fn(assignment["class_id"], "class_id"),
                subject_id=parse_uuid_fn(assignment["subject_id"], "subject_id"),
                teacher_id=parse_uuid_fn(assignment["teacher_id"], "teacher_id"),
                day_of_week=int(assignment["day"]),
                start_time=start_time,
                end_time=end_time,
            )
        )

    db.add(
        AuditLog(
            tenant_id=tenant_id,
            user_id=actor_user_id,
            action="timetable.generated",
            entity_type="timetable",
            entity_id=None,
            metadata_={
                "classes": [str(class_id) for class_id in class_ids],
                "slots_created": len(assignments),
            },
        )
    )
    db.commit()
    return {"success": True, "applied": True, "created": len(assignments), **result}
