"""
Seed script — creates demo tenant and users for development/demo.
Run: python seed.py
"""
import uuid
from database import SessionLocal, engine, Base
import models  # noqa — register all models

# Create tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    from src.domains.identity.models.tenant import Tenant
    from src.domains.identity.models.user import User
    from src.domains.academic.models.core import Class, Subject, Enrollment
    from src.domains.academic.models.parent_link import ParentLink
    from src.domains.academic.models.attendance import Attendance
    from src.domains.academic.models.marks import Exam, Mark
    from src.domains.academic.models.timetable import Timetable
    from src.domains.academic.models.lecture import Lecture
    from datetime import date, time

    # ─── Tenant ──────────────────────────────────
    tenant_id = uuid.uuid4()
    tenant = Tenant(
        id=tenant_id,
        name="Demo School",
        domain="gmail.com",  # For pilot: maps gmail.com users to this tenant
        plan_tier="pro",
        max_students=50,
        ai_daily_limit=100,
    )
    db.add(tenant)
    db.flush()

    # ─── Admin User ──────────────────────────────
    admin = User(
        tenant_id=tenant_id,
        email="admin@demo.school",
        full_name="Admin User",
        role="admin",
    )
    db.add(admin)

    # ─── Teacher ─────────────────────────────────
    teacher_id = uuid.uuid4()
    teacher = User(
        id=teacher_id,
        tenant_id=tenant_id,
        email="teacher@demo.school",
        full_name="Ms. Sharma",
        role="teacher",
    )
    db.add(teacher)

    parent_id = uuid.uuid4()
    parent = User(
        id=parent_id,
        tenant_id=tenant_id,
        email="parent@demo.school",
        full_name="Parent User",
        role="parent",
    )
    db.add(parent)

    # ─── Students ────────────────────────────────
    student_ids = []
    students_data = [
        ("Arjun Patel", "student1@gmail.com"),
        ("Priya Singh", "student2@gmail.com"),
        ("Rahul Kumar", "student3@gmail.com"),
    ]
    for name, email in students_data:
        sid = uuid.uuid4()
        student_ids.append(sid)
        db.add(User(
            id=sid,
            tenant_id=tenant_id,
            email=email,
            full_name=name,
            role="student",
        ))

    db.flush()

    # ─── Classes ─────────────────────────────────
    class_10a_id = uuid.uuid4()
    db.add(Class(
        id=class_10a_id,
        tenant_id=tenant_id,
        name="Class 10-A",
        grade_level="10",
        academic_year="2025-26",
    ))

    # ─── Subjects ────────────────────────────────
    subjects = {}
    for subj_name in ["Mathematics", "Science", "English", "Hindi", "Social Studies"]:
        subj_id = uuid.uuid4()
        subjects[subj_name] = subj_id
        db.add(Subject(
            id=subj_id,
            tenant_id=tenant_id,
            name=subj_name,
            class_id=class_10a_id,
        ))

    db.flush()

    # ─── Enrollments ─────────────────────────────
    for i, sid in enumerate(student_ids):
        db.add(Enrollment(
            tenant_id=tenant_id,
            student_id=sid,
            class_id=class_10a_id,
            roll_number=str(i + 1),
            academic_year="2025-26",
        ))

    db.add(ParentLink(
        tenant_id=tenant_id,
        parent_id=parent_id,
        child_id=student_ids[0],
    ))

    # ─── Attendance (sample 5 days) ──────────────
    import random
    for sid in student_ids:
        for day_offset in range(5):
            d = date(2026, 3, 1 + day_offset)
            status = random.choices(["present", "absent", "late"], weights=[85, 10, 5])[0]
            db.add(Attendance(
                tenant_id=tenant_id,
                student_id=sid,
                class_id=class_10a_id,
                date=d,
                status=status,
            ))

    # ─── Exams & Marks ───────────────────────────
    for subj_name, subj_id in list(subjects.items())[:3]:  # Math, Science, English
        exam_id = uuid.uuid4()
        db.add(Exam(
            id=exam_id,
            tenant_id=tenant_id,
            name=f"Midterm - {subj_name}",
            subject_id=subj_id,
            max_marks=100,
            exam_date=date(2026, 2, 15),
        ))
        db.flush()

        for sid in student_ids:
            db.add(Mark(
                tenant_id=tenant_id,
                student_id=sid,
                exam_id=exam_id,
                marks_obtained=random.randint(55, 95),
            ))

    # ─── Timetable (Mon-Fri full week) ───────────
    subject_names = ["Mathematics", "Science", "English", "Hindi", "Social Studies"]
    time_slots = [
        (time(9, 0), time(9, 45)),
        (time(9, 45), time(10, 30)),
        (time(11, 0), time(11, 45)),
        (time(11, 45), time(12, 30)),
        (time(13, 30), time(14, 15)),
    ]
    for day in range(5):  # 0=Mon through 4=Fri
        for slot_idx, (start, end) in enumerate(time_slots):
            # Rotate subjects across days for variety
            subj = subject_names[(slot_idx + day) % len(subject_names)]
            db.add(Timetable(
                tenant_id=tenant_id,
                class_id=class_10a_id,
                subject_id=subjects[subj],
                teacher_id=teacher_id,
                day_of_week=day,
                start_time=start,
                end_time=end,
            ))

    # ─── Lectures (sample) ───────────────────────
    # Removed auxiliary lectures seeding to prevent schema constraint failure

    db.commit()
    print("Demo data seeded successfully!")
    print(f"   Tenant: Demo School ({tenant_id})")
    print(f"   Admin:  admin@demo.school")
    print(f"   Teacher: teacher@demo.school")
    print(f"   Parent:  parent@demo.school")
    print(f"   Students: student1@gmail.com, student2@gmail.com, student3@gmail.com")

except Exception as e:
    db.rollback()
    print(f"Seed failed: {e}")
    raise
finally:
    db.close()
