"""Application helpers for teacher analytics and class insights."""

from __future__ import annotations

from collections import Counter
from datetime import datetime
import re
from typing import Any

from sqlalchemy import case, func


def _normalized_tokens(value: str) -> list[str]:
    return [token for token in re.split(r"[^a-z0-9]+", (value or "").lower()) if token]


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
    if class_ids:
        class_rows = (
            db.query(class_model)
            .filter(
                class_model.id.in_(class_ids),
                class_model.tenant_id == current_user.tenant_id,
            )
            .all()
        )
        available_class_ids = [row.id for row in class_rows]
        student_count_rows = (
            db.query(
                enrollment_model.class_id,
                func.count(enrollment_model.student_id),
            )
            .filter(
                enrollment_model.tenant_id == current_user.tenant_id,
                enrollment_model.class_id.in_(available_class_ids),
            )
            .group_by(enrollment_model.class_id)
            .all()
            if available_class_ids
            else []
        )
        attendance_rows = (
            db.query(
                attendance_model.class_id,
                func.count(attendance_model.student_id),
                func.sum(case((attendance_model.status == "present", 1), else_=0)),
            )
            .filter(
                attendance_model.tenant_id == current_user.tenant_id,
                attendance_model.class_id.in_(available_class_ids),
            )
            .group_by(attendance_model.class_id)
            .all()
            if available_class_ids
            else []
        )
        avg_mark_rows = (
            db.query(
                subject_model.class_id,
                func.avg(mark_model.marks_obtained),
            )
            .join(exam_model, exam_model.subject_id == subject_model.id)
            .join(mark_model, mark_model.exam_id == exam_model.id)
            .filter(
                subject_model.tenant_id == current_user.tenant_id,
                exam_model.tenant_id == current_user.tenant_id,
                mark_model.tenant_id == current_user.tenant_id,
                subject_model.class_id.in_(available_class_ids),
            )
            .group_by(subject_model.class_id)
            .all()
            if available_class_ids
            else []
        )

        student_count_by_class = {class_id: count for class_id, count in student_count_rows}
        attendance_by_class = {
            class_id: {"total": total or 0, "present": present or 0}
            for class_id, total, present in attendance_rows
        }
        avg_marks_by_class = {class_id: avg for class_id, avg in avg_mark_rows}

        for cls in class_rows:
            attendance = attendance_by_class.get(cls.id, {"total": 0, "present": 0})
            total_att = int(attendance["total"] or 0)
            present_att = int(attendance["present"] or 0)
            avg_att = round(present_att / total_att * 100) if total_att > 0 else 0
            avg_m = avg_marks_by_class.get(cls.id)
            classes.append(
                {
                    "id": str(cls.id),
                    "name": cls.name,
                    "students": int(student_count_by_class.get(cls.id, 0) or 0),
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
            assignment_submission_model.grade is None,
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
    class_row_ids = [cls.id for cls in classes]
    enrollments = (
        db.query(enrollment_model)
        .filter(
            enrollment_model.tenant_id == current_user.tenant_id,
            enrollment_model.class_id.in_(class_row_ids),
        )
        .all()
        if class_row_ids
        else []
    )
    student_ids = list({enrollment.student_id for enrollment in enrollments})
    students = (
        db.query(user_model)
        .filter(
            user_model.id.in_(student_ids),
            user_model.tenant_id == current_user.tenant_id,
        )
        .all()
        if student_ids
        else []
    )
    subjects = (
        db.query(subject_model)
        .filter(
            subject_model.tenant_id == current_user.tenant_id,
            subject_model.class_id.in_(class_row_ids),
        )
        .all()
        if class_row_ids
        else []
    )

    student_by_id = {student.id: student for student in students}
    enrollments_by_class: dict[Any, list[Any]] = {}
    for enrollment in enrollments:
        enrollments_by_class.setdefault(enrollment.class_id, []).append(enrollment)
    subjects_by_class: dict[Any, list[Any]] = {}
    for subject in subjects:
        subjects_by_class.setdefault(subject.class_id, []).append(subject)

    result = []
    for cls in classes:
        students = []
        for enrollment in enrollments_by_class.get(cls.id, []):
            student = student_by_id.get(enrollment.student_id)
            if student:
                students.append(
                    {
                        "id": str(student.id),
                        "name": student.full_name,
                        "email": student.email,
                        "roll_number": enrollment.roll_number,
                    }
                )

        result.append(
            {
                "id": str(cls.id),
                "name": cls.name,
                "grade": cls.grade_level,
                "students": students,
                "subjects": [{"id": str(subject.id), "name": subject.name} for subject in subjects_by_class.get(cls.id, [])],
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

    class_row_ids = [cls.id for cls in classes]
    subjects = (
        db.query(subject_model)
        .filter(
            subject_model.tenant_id == current_user.tenant_id,
            subject_model.class_id.in_(class_row_ids),
        )
        .all()
        if class_row_ids
        else []
    )
    subject_ids = [subject.id for subject in subjects]
    exams = (
        db.query(exam_model)
        .filter(
            exam_model.tenant_id == current_user.tenant_id,
            exam_model.subject_id.in_(subject_ids),
        )
        .all()
        if subject_ids
        else []
    )
    avg_mark_rows = (
        db.query(
            exam_model.subject_id,
            func.avg(mark_model.marks_obtained),
        )
        .join(mark_model, mark_model.exam_id == exam_model.id)
        .filter(
            exam_model.tenant_id == current_user.tenant_id,
            mark_model.tenant_id == current_user.tenant_id,
            exam_model.subject_id.in_(subject_ids),
        )
        .group_by(exam_model.subject_id)
        .all()
        if subject_ids
        else []
    )

    subjects_by_class: dict[Any, list[Any]] = {}
    for subject in subjects:
        subjects_by_class.setdefault(subject.class_id, []).append(subject)
    exams_by_subject: dict[Any, list[Any]] = {}
    for exam in exams:
        exams_by_subject.setdefault(exam.subject_id, []).append(exam)
    avg_marks_by_subject = {subject_id: avg for subject_id, avg in avg_mark_rows}

    insights = []
    for cls in classes:
        subject_stats = []
        for subj in subjects_by_class.get(cls.id, []):
            subject_exams = exams_by_subject.get(subj.id, [])
            if not subject_exams:
                continue
            avg = avg_marks_by_subject.get(subj.id)
            max_m = max(exam.max_marks for exam in subject_exams)
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

    enrollments = (
        db.query(enrollment_model)
        .filter(
            enrollment_model.tenant_id == current_user.tenant_id,
            enrollment_model.class_id.in_(allowed_class_ids),
        )
        .all()
    )
    student_ids = list({enrollment.student_id for enrollment in enrollments})

    if not student_ids:
        return {"heatmap": []}

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

    classes = (
        db.query(class_model)
        .filter(
            class_model.id.in_(allowed_class_ids),
            class_model.tenant_id == current_user.tenant_id,
        )
        .all()
    )
    subjects = (
        db.query(subject_model)
        .filter(
            subject_model.tenant_id == current_user.tenant_id,
            subject_model.class_id.in_(allowed_class_ids),
        )
        .all()
    )
    class_by_id = {cls.id: cls for cls in classes}
    subjects_by_class: dict[Any, list[Any]] = {}
    for subject in subjects:
        subjects_by_class.setdefault(subject.class_id, []).append(subject)

    subject_entries: list[tuple[str, str]] = []
    token_index: dict[str, list[int]] = {}
    for cid in allowed_class_ids:
        cls = class_by_id.get(cid)
        for subj in subjects_by_class.get(cid, []):
            key = f"{cls.name if cls else 'Unknown'} - {subj.name}"
            subject_entries.append((subj.name, key))
            entry_index = len(subject_entries) - 1
            for token in dict.fromkeys(_normalized_tokens(subj.name)):
                token_index.setdefault(token, []).append(entry_index)

    topic_counter: Counter = Counter()
    subject_counter: Counter = Counter()
    queries_by_subject: dict[str, list[str]] = {}

    for query in queries:
        query_text = query.query_text or ""
        topic = query_text[:60].strip() if query_text else "Unknown"
        topic_counter[topic] += 1

        candidate_indices: list[int] = []
        seen_indices: set[int] = set()
        for token in _normalized_tokens(query_text):
            for index in token_index.get(token, []):
                if index not in seen_indices:
                    seen_indices.add(index)
                    candidate_indices.append(index)

        lowered_query = query_text.lower()
        for index in candidate_indices:
            subj_name, key = subject_entries[index]
            if subj_name.lower() in lowered_query:
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
