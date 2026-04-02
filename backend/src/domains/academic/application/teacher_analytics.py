"""Application helpers for teacher analytics and class insights."""

from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Any

from sqlalchemy import func


def build_teacher_dashboard_response(
    *,
    db,
    current_user,
    class_ids: list,
    class_model,
    enrollment_model,
    attendance_model,
    subject_model,
    exam_model,
    mark_model,
    timetable_model,
    assignment_model,
    assignment_submission_model,
) -> dict[str, Any]:
    classes = []
    for cid in class_ids:
        cls = (
            db.query(class_model)
            .filter(
                class_model.id == cid,
                class_model.tenant_id == current_user.tenant_id,
            )
            .first()
        )
        if not cls:
            continue
        student_count = (
            db.query(enrollment_model)
            .filter(
                enrollment_model.tenant_id == current_user.tenant_id,
                enrollment_model.class_id == cid,
            )
            .count()
        )
        total_att = (
            db.query(attendance_model)
            .filter(
                attendance_model.tenant_id == current_user.tenant_id,
                attendance_model.class_id == cid,
            )
            .count()
        )
        present_att = (
            db.query(attendance_model)
            .filter(
                attendance_model.tenant_id == current_user.tenant_id,
                attendance_model.class_id == cid,
                attendance_model.status == "present",
            )
            .count()
        )
        avg_att = round(present_att / total_att * 100) if total_att > 0 else 0
        subject_ids = [
            s.id
            for s in db.query(subject_model)
            .filter(
                subject_model.tenant_id == current_user.tenant_id,
                subject_model.class_id == cid,
            )
            .all()
        ]
        exam_ids = (
            [
                e.id
                for e in db.query(exam_model)
                .filter(
                    exam_model.tenant_id == current_user.tenant_id,
                    exam_model.subject_id.in_(subject_ids),
                )
                .all()
            ]
            if subject_ids
            else []
        )
        avg_m = (
            db.query(func.avg(mark_model.marks_obtained))
            .filter(
                mark_model.tenant_id == current_user.tenant_id,
                mark_model.exam_id.in_(exam_ids),
            )
            .scalar()
            if exam_ids
            else None
        )
        classes.append(
            {
                "id": str(cls.id),
                "name": cls.name,
                "students": student_count,
                "avg_attendance": avg_att,
                "avg_marks": round(float(avg_m)) if avg_m else 0,
            }
        )

    today = datetime.now().weekday()
    today_slots = (
        db.query(timetable_model)
        .filter(
            timetable_model.tenant_id == current_user.tenant_id,
            timetable_model.teacher_id == current_user.id,
            timetable_model.day_of_week == today,
        )
        .order_by(timetable_model.start_time.asc())
        .all()
    )

    subject_ids = list({slot.subject_id for slot in today_slots})
    class_ids_for_slots = list({slot.class_id for slot in today_slots})
    subjects = (
        db.query(subject_model)
        .filter(
            subject_model.tenant_id == current_user.tenant_id,
            subject_model.id.in_(subject_ids),
        )
        .all()
        if subject_ids
        else []
    )
    classes_for_slots = (
        db.query(class_model)
        .filter(
            class_model.tenant_id == current_user.tenant_id,
            class_model.id.in_(class_ids_for_slots),
        )
        .all()
        if class_ids_for_slots
        else []
    )

    subject_by_id = {s.id: s.name for s in subjects}
    class_by_id = {c.id: c.name for c in classes_for_slots}

    today_classes = [
        {
            "class_id": str(slot.class_id),
            "class_name": class_by_id.get(slot.class_id, "Unknown"),
            "subject": subject_by_id.get(slot.subject_id, "Unknown"),
            "start_time": slot.start_time.strftime("%H:%M"),
            "end_time": slot.end_time.strftime("%H:%M"),
        }
        for slot in today_slots
    ]

    pending_reviews = (
        db.query(assignment_submission_model)
        .join(
            assignment_model,
            assignment_submission_model.assignment_id == assignment_model.id,
        )
        .filter(
            assignment_model.tenant_id == current_user.tenant_id,
            assignment_model.created_by == current_user.id,
            assignment_submission_model.grade == None,
        )
        .count()
    )

    open_assignments = (
        db.query(assignment_model)
        .filter(
            assignment_model.tenant_id == current_user.tenant_id,
            assignment_model.created_by == current_user.id,
        )
        .count()
    )

    return {
        "classes": classes,
        "today_classes": today_classes,
        "pending_reviews": pending_reviews,
        "open_assignments": open_assignments,
    }


def build_teacher_classes_response(
    *,
    db,
    current_user,
    allowed_class_ids: list,
    class_model,
    enrollment_model,
    user_model,
    subject_model,
) -> list[dict[str, Any]]:
    if not allowed_class_ids:
        return []

    classes = (
        db.query(class_model)
        .filter(
            class_model.tenant_id == current_user.tenant_id,
            class_model.id.in_(allowed_class_ids),
        )
        .all()
    )

    result = []
    for cls in classes:
        enrollments = (
            db.query(enrollment_model)
            .filter(
                enrollment_model.tenant_id == current_user.tenant_id,
                enrollment_model.class_id == cls.id,
            )
            .all()
        )
        students = []
        for enrollment in enrollments:
            student = (
                db.query(user_model)
                .filter(
                    user_model.id == enrollment.student_id,
                    user_model.tenant_id == current_user.tenant_id,
                )
                .first()
            )
            if student:
                students.append(
                    {
                        "id": str(student.id),
                        "name": student.full_name,
                        "email": student.email,
                        "roll_number": enrollment.roll_number,
                    }
                )

        subjects = (
            db.query(subject_model)
            .filter(
                subject_model.tenant_id == current_user.tenant_id,
                subject_model.class_id == cls.id,
            )
            .all()
        )
        result.append(
            {
                "id": str(cls.id),
                "name": cls.name,
                "grade": cls.grade_level,
                "students": students,
                "subjects": [{"id": str(subject.id), "name": subject.name} for subject in subjects],
            }
        )
    return result


def build_teacher_insights_response(
    *,
    db,
    current_user,
    allowed_class_ids: list,
    class_model,
    subject_model,
    exam_model,
    mark_model,
) -> dict[str, Any]:
    if not allowed_class_ids:
        return {"insights": []}

    classes = (
        db.query(class_model)
        .filter(
            class_model.tenant_id == current_user.tenant_id,
            class_model.id.in_(allowed_class_ids),
        )
        .all()
    )

    insights = []
    for cls in classes:
        subjects = (
            db.query(subject_model)
            .filter(
                subject_model.tenant_id == current_user.tenant_id,
                subject_model.class_id == cls.id,
            )
            .all()
        )
        subject_stats = []
        for subj in subjects:
            exams = (
                db.query(exam_model)
                .filter(
                    exam_model.tenant_id == current_user.tenant_id,
                    exam_model.subject_id == subj.id,
                )
                .all()
            )
            if not exams:
                continue
            exam_ids = [exam.id for exam in exams]
            avg = (
                db.query(func.avg(mark_model.marks_obtained))
                .filter(
                    mark_model.tenant_id == current_user.tenant_id,
                    mark_model.exam_id.in_(exam_ids),
                )
                .scalar()
            )
            max_m = max(exam.max_marks for exam in exams)
            pct = round(float(avg) / max_m * 100) if avg and max_m else 0
            subject_stats.append({"subject": subj.name, "avg_pct": pct, "is_weak": pct < 60})

        weak_topics = [stat["subject"] for stat in subject_stats if stat.get("is_weak")]
        insights.append(
            {
                "class": cls.name,
                "subjects": subject_stats,
                "weak_topics": weak_topics,
                "recommendation": (
                    f"Focus on: {', '.join(weak_topics)}"
                    if weak_topics
                    else "All subjects performing well"
                ),
            }
        )

    return {"insights": insights}


def build_teacher_doubt_heatmap_response(
    *,
    db,
    current_user,
    allowed_class_ids: list,
    class_model,
    subject_model,
    enrollment_model,
    ai_query_model,
) -> dict[str, Any]:
    if not allowed_class_ids:
        return {"heatmap": []}

    student_ids = []
    for cid in allowed_class_ids:
        enrollments = (
            db.query(enrollment_model)
            .filter(
                enrollment_model.tenant_id == current_user.tenant_id,
                enrollment_model.class_id == cid,
            )
            .all()
        )
        student_ids.extend([enrollment.student_id for enrollment in enrollments])

    if not student_ids:
        return {"heatmap": []}

    student_ids = list(set(student_ids))
    queries = (
        db.query(ai_query_model)
        .filter(
            ai_query_model.tenant_id == current_user.tenant_id,
            ai_query_model.user_id.in_(student_ids),
        )
        .order_by(ai_query_model.created_at.desc())
        .limit(500)
        .all()
    )

    subject_map = {}
    for cid in allowed_class_ids:
        cls = (
            db.query(class_model)
            .filter(
                class_model.id == cid,
                class_model.tenant_id == current_user.tenant_id,
            )
            .first()
        )
        subjects = (
            db.query(subject_model)
            .filter(
                subject_model.tenant_id == current_user.tenant_id,
                subject_model.class_id == cid,
            )
            .all()
        )
        for subj in subjects:
            subject_map[str(subj.id)] = {
                "subject": subj.name,
                "class": cls.name if cls else "Unknown",
            }

    topic_counter: Counter = Counter()
    subject_counter: Counter = Counter()
    queries_by_subject: dict[str, list[str]] = {}

    for query in queries:
        topic = query.query_text[:60].strip() if query.query_text else "Unknown"
        topic_counter[topic] += 1

        for _, info in subject_map.items():
            subj_name = info["subject"]
            cls_name = info["class"]
            key = f"{cls_name} - {subj_name}"
            if subj_name.lower() in (query.query_text or "").lower():
                subject_counter[key] += 1
                if key not in queries_by_subject:
                    queries_by_subject[key] = []
                queries_by_subject[key].append(topic)
                break

    heatmap = []
    for key, count in subject_counter.most_common(20):
        sample_topics = list(set(queries_by_subject.get(key, [])))[:5]
        heatmap.append(
            {
                "label": key,
                "query_count": count,
                "intensity": min(1.0, count / max(1, len(queries)) * 10),
                "sample_topics": sample_topics,
            }
        )

    top_topics = [{"topic": topic, "count": count} for topic, count in topic_counter.most_common(15)]

    return {
        "heatmap": heatmap,
        "top_topics": top_topics,
        "total_queries": len(queries),
        "student_count": len(student_ids),
    }
