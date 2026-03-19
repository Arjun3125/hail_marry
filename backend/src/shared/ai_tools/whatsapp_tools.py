"""WhatsApp-specific ERP tools for the LangGraph agent.

Provides role-scoped tools for:
- Students: timetable, tests, assignments, attendance, results, weak topics
- Teachers: schedule, absent students
- Parents: child performance, child attendance, child homework
- Admin: school attendance summary, fee pending report, AI usage stats
"""
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import UUID

try:
    from langchain_core.tools import tool
except ModuleNotFoundError:  # Lightweight test environments
    def tool(fn):
        fn.name = fn.__name__
        fn.invoke = lambda params, _fn=fn: _fn(**params)
        return fn

try:
    from sqlalchemy import func as sqlfunc
except ModuleNotFoundError:  # Lightweight test environments
    sqlfunc = None

try:
    from database import SessionLocalRO
except ModuleNotFoundError:  # Lightweight test environments
    SessionLocalRO = None

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class WhatsAppToolSpec:
    """Canonical metadata for a WhatsApp-accessible tool.

    This is the Phase 0 foundation from `documentation/whatsapp_access_implementation_plan.md`:
    one registry that captures role access, invocation shape, output characteristics,
    and execution mode so future WhatsApp routing/formatting logic can stay centralized.
    """

    name: str
    handler: callable
    description: str
    roles: frozenset[str]
    required_params: tuple[str, ...]
    feature_category: str
    execution_mode: str
    output_type: str
    channel_suitability: str

# ─── RBAC Map ─────────────────────────────────────────────────

TOOL_ROLE_MAP = {
    "get_student_timetable": {"student"},
    "get_student_tests": {"student"},
    "get_student_assignments": {"student"},
    "get_student_attendance": {"student"},
    "get_student_results": {"student"},
    "get_student_weak_topics": {"student"},
    "generate_study_guide": {"student"},
    "generate_audio_overview": {"student"},
    "get_teacher_schedule": {"teacher"},
    "get_teacher_absent_students": {"teacher"},
    "generate_quiz": {"teacher"},
    "get_child_performance": {"parent"},
    "get_child_attendance": {"parent"},
    "get_child_homework": {"parent"},
    "get_school_attendance_summary": {"admin"},
    "get_fee_pending_report": {"admin"},
    "get_ai_usage_stats": {"admin"},
    "check_library_catalog": {"student", "teacher", "admin"},
}


def authorize_tool(tool_name: str, user_role: str) -> bool:
    """Check if a user role is authorized to call a specific tool."""
    spec = WHATSAPP_TOOL_REGISTRY.get(tool_name)
    allowed = spec.roles if spec else TOOL_ROLE_MAP.get(tool_name, set())
    return user_role in allowed


# ─── Student Tools ────────────────────────────────────────────

@tool
def get_student_timetable(user_id: str, tenant_id: str) -> str:
    """Get today's class timetable for a student.

    Args:
        user_id: The student's UUID.
        tenant_id: The school tenant UUID.
    """
    db = SessionLocalRO()
    try:
        from src.domains.academic.models.academic import Timetable, Enrollment, Subject
        enrollment = db.query(Enrollment).filter(
            Enrollment.tenant_id == UUID(tenant_id),
            Enrollment.student_id == UUID(user_id),
        ).first()
        if not enrollment:
            return "You are not enrolled in any class."

        today = datetime.now().strftime("%A")
        slots = db.query(Timetable).filter(
            Timetable.tenant_id == UUID(tenant_id),
            Timetable.class_id == enrollment.class_id,
            Timetable.day_of_week == today,
        ).order_by(Timetable.start_time).all()

        if not slots:
            return f"📅 No classes scheduled for {today}. Enjoy your free day!"

        lines = [f"📅 *{today}'s Timetable:*"]
        for s in slots:
            subject = db.query(Subject).filter(Subject.id == s.subject_id).first()
            subj_name = subject.name if subject else "TBD"
            lines.append(f"  {s.start_time} – {s.end_time} | {subj_name}")
        return "\n".join(lines)
    except Exception as e:
        logger.error("get_student_timetable error: %s", e)
        return "Sorry, I couldn't fetch your timetable right now."
    finally:
        db.close()


@tool
def get_student_tests(user_id: str, tenant_id: str) -> str:
    """Check if the student has any tests or exams this week.

    Args:
        user_id: The student's UUID.
        tenant_id: The school tenant UUID.
    """
    db = SessionLocalRO()
    try:
        from src.domains.academic.models.academic import Exam, Enrollment
        enrollment = db.query(Enrollment).filter(
            Enrollment.tenant_id == UUID(tenant_id),
            Enrollment.student_id == UUID(user_id),
        ).first()
        if not enrollment:
            return "You are not enrolled in any class."

        today = datetime.now(timezone.utc).date()
        week_end = today + timedelta(days=7)

        exams = db.query(Exam).filter(
            Exam.tenant_id == UUID(tenant_id),
            Exam.class_id == enrollment.class_id,
            Exam.date >= today,
            Exam.date <= week_end,
        ).order_by(Exam.date).all()

        if not exams:
            return "✅ No tests scheduled this week!"

        lines = ["📝 *Upcoming Tests:*"]
        for e in exams:
            lines.append(f"  📌 {e.name} — {e.date}")
        return "\n".join(lines)
    except Exception as e:
        logger.error("get_student_tests error: %s", e)
        return "Sorry, I couldn't check your test schedule right now."
    finally:
        db.close()


@tool
def get_student_assignments(user_id: str, tenant_id: str) -> str:
    """Get pending assignments for a student.

    Args:
        user_id: The student's UUID.
        tenant_id: The school tenant UUID.
    """
    db = SessionLocalRO()
    try:
        from src.domains.academic.models.academic import Assignment, Submission, Enrollment
        enrollment = db.query(Enrollment).filter(
            Enrollment.tenant_id == UUID(tenant_id),
            Enrollment.student_id == UUID(user_id),
        ).first()
        if not enrollment:
            return "You are not enrolled in any class."

        today = datetime.now(timezone.utc).date()

        # Get assignments for this class with future due dates
        assignments = db.query(Assignment).filter(
            Assignment.tenant_id == UUID(tenant_id),
            Assignment.class_id == enrollment.class_id,
            Assignment.due_date >= today,
        ).order_by(Assignment.due_date).all()

        if not assignments:
            return "✅ No pending assignments!"

        # Check which ones already have submissions
        submitted_ids = set()
        submissions = db.query(Submission).filter(
            Submission.student_id == UUID(user_id),
            Submission.assignment_id.in_([a.id for a in assignments]),
        ).all()
        submitted_ids = {s.assignment_id for s in submissions}

        pending = [a for a in assignments if a.id not in submitted_ids]
        if not pending:
            return "✅ All assignments submitted!"

        lines = ["📋 *Pending Assignments:*"]
        for a in pending:
            days_left = (a.due_date - today).days
            urgency = "🔴" if days_left <= 1 else "🟡" if days_left <= 3 else "🟢"
            lines.append(f"  {urgency} {a.title} — due {a.due_date} ({days_left}d left)")
        return "\n".join(lines)
    except Exception as e:
        logger.error("get_student_assignments error: %s", e)
        return "Sorry, I couldn't fetch your assignments right now."
    finally:
        db.close()


@tool
def get_student_attendance(user_id: str, tenant_id: str) -> str:
    """Get the student's attendance summary for the current month.

    Args:
        user_id: The student's UUID.
        tenant_id: The school tenant UUID.
    """
    db = SessionLocalRO()
    try:
        from src.domains.academic.models.academic import Attendance
        today = datetime.now(timezone.utc).date()
        month_start = today.replace(day=1)

        records = db.query(Attendance).filter(
            Attendance.tenant_id == UUID(tenant_id),
            Attendance.student_id == UUID(user_id),
            Attendance.date >= month_start,
            Attendance.date <= today,
        ).all()

        if not records:
            return "📊 No attendance records found for this month."

        total = len(records)
        present = sum(1 for r in records if r.status == "present")
        absent = total - present
        pct = round(present / total * 100) if total > 0 else 0

        emoji = "✅" if pct >= 90 else "⚠️" if pct >= 75 else "🔴"

        return (
            f"📊 *Attendance ({today.strftime('%B %Y')}):*\n"
            f"  Present: {present}/{total} days ({pct}%) {emoji}\n"
            f"  Absent: {absent} days"
        )
    except Exception as e:
        logger.error("get_student_attendance error: %s", e)
        return "Sorry, I couldn't fetch your attendance right now."
    finally:
        db.close()


@tool
def get_student_results(user_id: str, tenant_id: str) -> str:
    """Get the student's latest exam results.

    Args:
        user_id: The student's UUID.
        tenant_id: The school tenant UUID.
    """
    db = SessionLocalRO()
    try:
        from src.domains.academic.models.academic import Mark
        marks = db.query(Mark).filter(
            Mark.tenant_id == UUID(tenant_id),
            Mark.student_id == UUID(user_id),
        ).order_by(Mark.created_at.desc()).limit(10).all()

        if not marks:
            return "📈 No exam results found yet."

        lines = ["📈 *Recent Results:*"]
        for m in marks:
            pct = round(m.marks_obtained / m.max_marks * 100) if m.max_marks > 0 else 0
            emoji = "⭐" if pct >= 90 else "✅" if pct >= 75 else "⚠️" if pct >= 50 else "🔴"
            lines.append(f"  {emoji} {m.subject_name or 'Subject'}: {m.marks_obtained}/{m.max_marks} ({pct}%)")
        return "\n".join(lines)
    except Exception as e:
        logger.error("get_student_results error: %s", e)
        return "Sorry, I couldn't fetch your results right now."
    finally:
        db.close()


@tool
def get_student_weak_topics(user_id: str, tenant_id: str) -> str:
    """Identify subjects where the student is scoring below 60%.

    Args:
        user_id: The student's UUID.
        tenant_id: The school tenant UUID.
    """
    db = SessionLocalRO()
    try:
        from src.domains.academic.models.academic import Mark
        marks = db.query(Mark).filter(
            Mark.tenant_id == UUID(tenant_id),
            Mark.student_id == UUID(user_id),
        ).all()

        if not marks:
            return "💡 Not enough data to identify weak areas yet."

        # Group by subject
        subjects: dict[str, list] = {}
        for m in marks:
            name = m.subject_name or "Unknown"
            subjects.setdefault(name, []).append(
                (m.marks_obtained / m.max_marks * 100) if m.max_marks > 0 else 0
            )

        weak = []
        for subj, pcts in subjects.items():
            avg = sum(pcts) / len(pcts)
            if avg < 60:
                weak.append((subj, round(avg)))

        if not weak:
            return "🌟 Great job! No weak subjects — keep it up!"

        lines = ["⚠️ *Subjects Needing Attention:*"]
        for subj, avg in sorted(weak, key=lambda x: x[1]):
            lines.append(f"  🔴 {subj} — avg {avg}%")
        lines.append("\n💡 _Ask me to generate a quiz or study guide for any subject!_")
        return "\n".join(lines)
    except Exception as e:
        logger.error("get_student_weak_topics error: %s", e)
        return "Sorry, I couldn't analyze your weak topics right now."
    finally:
        db.close()


@tool
def generate_study_guide(user_id: str, tenant_id: str, topic: str) -> str:
    """Queue a study-guide job for a student topic."""
    cleaned_topic = (topic or "").strip()
    if not cleaned_topic:
        return "⚠️ Please include a topic, for example: *Generate study guide for photosynthesis*."

    try:
        from src.domains.platform.schemas.ai_runtime import InternalAIQueryRequest
        from src.domains.platform.services.ai_queue import JOB_TYPE_QUERY, enqueue_job

        payload = InternalAIQueryRequest(
            query=cleaned_topic,
            mode="study_guide",
            language="english",
            response_length="default",
            expertise_level="standard",
            tenant_id=str(tenant_id),
        )
        job = enqueue_job(
            JOB_TYPE_QUERY,
            payload.model_dump(),
            tenant_id=str(tenant_id),
            user_id=str(user_id),
        )
        job_id = job.get("job_id", "unknown")
        return (
            f"📘 Study guide queued for *{cleaned_topic}*.\n"
            f"Job ID: `{job_id}`\n"
            "I'll send the guide once it's ready."
        )
    except Exception as e:
        logger.error("generate_study_guide error: %s", e)
        return "Sorry, I couldn't queue the study guide right now."


@tool
def generate_audio_overview(user_id: str, tenant_id: str, topic: str) -> str:
    """Queue an audio-overview job for a student topic."""
    cleaned_topic = (topic or "").strip()
    if not cleaned_topic:
        return "⚠️ Please include a topic, for example: *Create audio overview for photosynthesis*."

    try:
        from src.domains.platform.schemas.ai_runtime import InternalAudioOverviewRequest
        from src.domains.platform.services.ai_queue import JOB_TYPE_AUDIO, enqueue_job

        payload = InternalAudioOverviewRequest(
            topic=cleaned_topic,
            format="deep_dive",
            language="english",
            tenant_id=str(tenant_id),
        )
        job = enqueue_job(
            JOB_TYPE_AUDIO,
            payload.model_dump(),
            tenant_id=str(tenant_id),
            user_id=str(user_id),
        )
        job_id = job.get("job_id", "unknown")
        return (
            f"🎧 Audio overview queued for *{cleaned_topic}*.\n"
            f"Job ID: `{job_id}`\n"
            "I'll send it here once it's ready."
        )
    except Exception as e:
        logger.error("generate_audio_overview error: %s", e)
        return "Sorry, I couldn't queue the audio overview right now."


# ─── Teacher Tools ────────────────────────────────────────────

@tool
def get_teacher_schedule(user_id: str, tenant_id: str) -> str:
    """Get today's teaching schedule for a teacher.

    Args:
        user_id: The teacher's UUID.
        tenant_id: The school tenant UUID.
    """
    db = SessionLocalRO()
    try:
        from src.domains.academic.models.academic import Timetable, Subject, SchoolClass
        today = datetime.now().strftime("%A")

        slots = db.query(Timetable).filter(
            Timetable.tenant_id == UUID(tenant_id),
            Timetable.teacher_id == UUID(user_id),
            Timetable.day_of_week == today,
        ).order_by(Timetable.start_time).all()

        if not slots:
            return f"📅 No classes scheduled for {today}."

        lines = [f"📅 *{today}'s Teaching Schedule:*"]
        for s in slots:
            subject = db.query(Subject).filter(Subject.id == s.subject_id).first()
            cls = db.query(SchoolClass).filter(SchoolClass.id == s.class_id).first()
            subj_name = subject.name if subject else "TBD"
            cls_name = cls.name if cls else "TBD"
            lines.append(f"  {s.start_time} – {s.end_time} | {subj_name} | {cls_name}")
        return "\n".join(lines)
    except Exception as e:
        logger.error("get_teacher_schedule error: %s", e)
        return "Sorry, I couldn't fetch your schedule right now."
    finally:
        db.close()


@tool
def get_teacher_absent_students(user_id: str, tenant_id: str) -> str:
    """Get students marked absent today across the teacher's classes.

    Args:
        user_id: The teacher's UUID.
        tenant_id: The school tenant UUID.
    """
    db = SessionLocalRO()
    try:
        from src.domains.academic.models.academic import Attendance, Timetable, Enrollment
        from src.domains.identity.models.user import User
        today = datetime.now(timezone.utc).date()

        # Find classes this teacher teaches
        teacher_classes = db.query(Timetable.class_id).filter(
            Timetable.tenant_id == UUID(tenant_id),
            Timetable.teacher_id == UUID(user_id),
        ).distinct().all()
        class_ids = [c[0] for c in teacher_classes]

        if not class_ids:
            return "📋 You don't have any assigned classes."

        # Find absent students today
        absents = db.query(Attendance).filter(
            Attendance.tenant_id == UUID(tenant_id),
            Attendance.date == today,
            Attendance.status == "absent",
        ).join(Enrollment, Attendance.student_id == Enrollment.student_id).filter(
            Enrollment.class_id.in_(class_ids),
        ).all()

        if not absents:
            return "✅ All students present today!"

        lines = [f"❌ *Students Absent Today ({today}):*"]
        for a in absents:
            student = db.query(User).filter(User.id == a.student_id).first()
            name = student.full_name if student else str(a.student_id)
            lines.append(f"  • {name}")
        lines.append(f"\nTotal absent: {len(absents)}")
        return "\n".join(lines)
    except Exception as e:
        logger.error("get_teacher_absent_students error: %s", e)
        return "Sorry, I couldn't fetch absent students right now."
    finally:
        db.close()


@tool
def generate_quiz(user_id: str, tenant_id: str, topic: str) -> str:
    """Queue a quiz-generation job for a teacher.

    Args:
        user_id: The teacher's UUID.
        tenant_id: The school tenant UUID.
        topic: Topic or instruction to generate the quiz for.
    """
    cleaned_topic = (topic or "").strip()
    if not cleaned_topic:
        return "⚠️ Please include a topic, for example: *Generate quiz for Class 8 science*."

    try:
        from src.domains.platform.schemas.ai_runtime import InternalStudyToolGenerateRequest
        from src.domains.platform.services.ai_queue import JOB_TYPE_STUDY_TOOL, enqueue_job

        payload = InternalStudyToolGenerateRequest(
            tool="quiz",
            topic=cleaned_topic,
            tenant_id=str(tenant_id),
        )
        job = enqueue_job(
            JOB_TYPE_STUDY_TOOL,
            payload.model_dump(),
            tenant_id=str(tenant_id),
            user_id=str(user_id),
        )
        job_id = job.get("job_id", "unknown")
        return (
            f"⏳ Quiz generation queued for *{cleaned_topic}*.\n"
            f"Job ID: `{job_id}`\n"
            "I'll share the result as soon as it's ready."
        )
    except Exception as e:
        logger.error("generate_quiz error: %s", e)
        return "Sorry, I couldn't queue the quiz right now."


# ─── Parent Tools ─────────────────────────────────────────────

@tool
def get_child_performance(child_id: str, tenant_id: str) -> str:
    """Get academic performance summary for a parent's child.

    Args:
        child_id: The child student's UUID.
        tenant_id: The school tenant UUID.
    """
    db = SessionLocalRO()
    try:
        from src.domains.academic.models.academic import Mark, Attendance
        from src.domains.identity.models.user import User
        child = db.query(User).filter(User.id == UUID(child_id)).first()
        name = child.full_name if child else "Your child"

        # Marks
        marks = db.query(Mark).filter(
            Mark.tenant_id == UUID(tenant_id),
            Mark.student_id == UUID(child_id),
        ).all()

        # Attendance
        today = datetime.now(timezone.utc).date()
        month_start = today.replace(day=1)
        att_records = db.query(Attendance).filter(
            Attendance.tenant_id == UUID(tenant_id),
            Attendance.student_id == UUID(child_id),
            Attendance.date >= month_start,
        ).all()

        lines = [f"📊 *{name}'s Performance Summary:*\n"]

        if marks:
            total_pct = sum(
                (m.marks_obtained / m.max_marks * 100) for m in marks if m.max_marks > 0
            ) / len(marks)
            lines.append(f"📈 Average Score: *{round(total_pct)}%*")
            best = max(marks, key=lambda m: m.marks_obtained / m.max_marks if m.max_marks > 0 else 0)
            lines.append(f"⭐ Best Subject: *{best.subject_name or 'N/A'}*")
        else:
            lines.append("📈 No exam results yet.")

        if att_records:
            present = sum(1 for r in att_records if r.status == "present")
            pct = round(present / len(att_records) * 100)
            lines.append(f"📅 Attendance: *{pct}%* ({present}/{len(att_records)} days)")
        else:
            lines.append("📅 No attendance data this month.")

        return "\n".join(lines)
    except Exception as e:
        logger.error("get_child_performance error: %s", e)
        return "Sorry, I couldn't fetch the performance summary right now."
    finally:
        db.close()


@tool
def get_child_attendance(child_id: str, tenant_id: str) -> str:
    """Get this week's attendance for a parent's child.

    Args:
        child_id: The child student's UUID.
        tenant_id: The school tenant UUID.
    """
    db = SessionLocalRO()
    try:
        from src.domains.academic.models.academic import Attendance
        from src.domains.identity.models.user import User
        child = db.query(User).filter(User.id == UUID(child_id)).first()
        name = child.full_name if child else "Your child"

        today = datetime.now(timezone.utc).date()
        week_start = today - timedelta(days=today.weekday())

        records = db.query(Attendance).filter(
            Attendance.tenant_id == UUID(tenant_id),
            Attendance.student_id == UUID(child_id),
            Attendance.date >= week_start,
            Attendance.date <= today,
        ).order_by(Attendance.date).all()

        if not records:
            return f"📅 No attendance records for {name} this week."

        present = sum(1 for r in records if r.status == "present")
        pct = round(present / len(records) * 100)

        lines = [f"📅 *{name}'s Attendance This Week:*"]
        for r in records:
            emoji = "✅" if r.status == "present" else "❌"
            lines.append(f"  {emoji} {r.date.strftime('%A, %b %d')} — {r.status}")
        lines.append(f"\n*Weekly: {present}/{len(records)} ({pct}%)*")
        return "\n".join(lines)
    except Exception as e:
        logger.error("get_child_attendance error: %s", e)
        return "Sorry, I couldn't fetch the attendance report right now."
    finally:
        db.close()


@tool
def get_child_homework(child_id: str, tenant_id: str) -> str:
    """Get pending homework/assignments for a parent's child.

    Args:
        child_id: The child student's UUID.
        tenant_id: The school tenant UUID.
    """
    db = SessionLocalRO()
    try:
        from src.domains.academic.models.academic import Assignment, Submission, Enrollment
        enrollment = db.query(Enrollment).filter(
            Enrollment.tenant_id == UUID(tenant_id),
            Enrollment.student_id == UUID(child_id),
        ).first()
        if not enrollment:
            return "Your child is not enrolled in any class."

        today = datetime.now(timezone.utc).date()
        assignments = db.query(Assignment).filter(
            Assignment.tenant_id == UUID(tenant_id),
            Assignment.class_id == enrollment.class_id,
            Assignment.due_date >= today,
        ).order_by(Assignment.due_date).all()

        if not assignments:
            return "✅ No pending homework!"

        submitted_ids = set()
        submissions = db.query(Submission).filter(
            Submission.student_id == UUID(child_id),
            Submission.assignment_id.in_([a.id for a in assignments]),
        ).all()
        submitted_ids = {s.assignment_id for s in submissions}

        pending = [a for a in assignments if a.id not in submitted_ids]
        if not pending:
            return "✅ All homework submitted!"

        lines = ["📋 *Pending Homework:*"]
        for a in pending:
            days_left = (a.due_date - today).days
            urgency = "🔴" if days_left <= 1 else "🟡" if days_left <= 3 else "🟢"
            lines.append(f"  {urgency} {a.title} — due {a.due_date}")
        return "\n".join(lines)
    except Exception as e:
        logger.error("get_child_homework error: %s", e)
        return "Sorry, I couldn't fetch homework right now."
    finally:
        db.close()


# ─── Admin Tools ──────────────────────────────────────────────

@tool
def get_school_attendance_summary(tenant_id: str) -> str:
    """Get today's school-wide attendance summary."""
    try:
        from src.domains.platform.services.ai_queue import _get_redis_client
        redis_client = _get_redis_client()
        data = redis_client.get(f"tenant:{tenant_id}:analytics:attendance")
        if data:
            import json
            parsed = json.loads(data)
            return f"School Attendance Summary:\nTotal Students: {parsed['total_students']}\nPresent: {parsed['present_today']}\nAbsent: {parsed['absent_today']}"
        return "Attendance summary not available right now. Please try again later."
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error("get_school_attendance_summary error: %s", e)
        return "Error accessing attendance summary."

@tool
def get_fee_pending_report(tenant_id: str) -> str:
    """Get outstanding fee report for the school."""
    try:
        from src.domains.platform.services.ai_queue import _get_redis_client
        redis_client = _get_redis_client()
        data = redis_client.get(f"tenant:{tenant_id}:analytics:fees")
        if data:
            import json
            parsed = json.loads(data)
            return f"Total pending fees: {parsed.get('total_pending_amount')} {parsed.get('currency', 'USD')}"
        return "Financial report not available right now. Please try again later."
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error("get_fee_pending_report error: %s", e)
        return "Error fetching fee report."

@tool
def get_ai_usage_stats(tenant_id: str) -> str:
    """Get AI usage analytics for the school.

    Args:
        tenant_id: The school tenant UUID.
    """
    db = SessionLocalRO()
    try:
        from src.domains.platform.models.ai_models import AIQuery
        from datetime import timedelta

        today = datetime.now(timezone.utc).date()
        week_ago = today - timedelta(days=7)

        total = db.query(AIQuery).filter(
            AIQuery.tenant_id == UUID(tenant_id),
        ).count()

        this_week = db.query(AIQuery).filter(
            AIQuery.tenant_id == UUID(tenant_id),
            AIQuery.created_at >= week_ago,
        ).count()

        return (
            f"🤖 *AI Usage Stats:*\n"
            f"  Total queries: {total}\n"
            f"  This week: {this_week}\n"
            f"  Avg/day: {round(this_week / 7, 1)}"
        )
    except Exception as e:
        logger.error("get_ai_usage_stats error: %s", e)
        return "Sorry, I couldn't fetch AI usage stats right now."
    finally:
        db.close()


# ─── Tool Registry ────────────────────────────────────────────

TOOL_SPECS = (
    WhatsAppToolSpec(
        name="get_student_timetable",
        handler=get_student_timetable,
        description="Today's timetable for a student.",
        roles=frozenset({"student"}),
        required_params=("user_id", "tenant_id"),
        feature_category="erp_read",
        execution_mode="sync",
        output_type="text",
        channel_suitability="direct",
    ),
    WhatsAppToolSpec(
        name="get_student_tests",
        handler=get_student_tests,
        description="Upcoming tests and exams for the current week.",
        roles=frozenset({"student"}),
        required_params=("user_id", "tenant_id"),
        feature_category="erp_read",
        execution_mode="sync",
        output_type="text",
        channel_suitability="direct",
    ),
    WhatsAppToolSpec(
        name="get_student_assignments",
        handler=get_student_assignments,
        description="Pending assignments for the student.",
        roles=frozenset({"student"}),
        required_params=("user_id", "tenant_id"),
        feature_category="erp_read",
        execution_mode="sync",
        output_type="text",
        channel_suitability="direct",
    ),
    WhatsAppToolSpec(
        name="get_student_attendance",
        handler=get_student_attendance,
        description="Current-month attendance summary.",
        roles=frozenset({"student"}),
        required_params=("user_id", "tenant_id"),
        feature_category="erp_read",
        execution_mode="sync",
        output_type="text",
        channel_suitability="direct",
    ),
    WhatsAppToolSpec(
        name="get_student_results",
        handler=get_student_results,
        description="Latest exam results for the student.",
        roles=frozenset({"student"}),
        required_params=("user_id", "tenant_id"),
        feature_category="erp_read",
        execution_mode="sync",
        output_type="text",
        channel_suitability="direct",
    ),
    WhatsAppToolSpec(
        name="get_student_weak_topics",
        handler=get_student_weak_topics,
        description="Subjects needing attention based on marks.",
        roles=frozenset({"student"}),
        required_params=("user_id", "tenant_id"),
        feature_category="erp_read",
        execution_mode="sync",
        output_type="text",
        channel_suitability="direct",
    ),
    WhatsAppToolSpec(
        name="generate_study_guide",
        handler=generate_study_guide,
        description="Queue a study-guide job for a student topic.",
        roles=frozenset({"student"}),
        required_params=("user_id", "tenant_id", "topic"),
        feature_category="ai_async",
        execution_mode="async",
        output_type="text",
        channel_suitability="direct",
    ),
    WhatsAppToolSpec(
        name="generate_audio_overview",
        handler=generate_audio_overview,
        description="Queue an audio-overview job for a student topic.",
        roles=frozenset({"student"}),
        required_params=("user_id", "tenant_id", "topic"),
        feature_category="ai_async",
        execution_mode="async",
        output_type="text",
        channel_suitability="direct",
    ),
    WhatsAppToolSpec(
        name="get_teacher_schedule",
        handler=get_teacher_schedule,
        description="Today's teaching schedule.",
        roles=frozenset({"teacher"}),
        required_params=("user_id", "tenant_id"),
        feature_category="erp_read",
        execution_mode="sync",
        output_type="text",
        channel_suitability="direct",
    ),
    WhatsAppToolSpec(
        name="get_teacher_absent_students",
        handler=get_teacher_absent_students,
        description="Students absent today in the teacher's classes.",
        roles=frozenset({"teacher"}),
        required_params=("user_id", "tenant_id"),
        feature_category="erp_read",
        execution_mode="sync",
        output_type="text",
        channel_suitability="direct",
    ),
    WhatsAppToolSpec(
        name="generate_quiz",
        handler=generate_quiz,
        description="Queue a quiz-generation job for a teacher topic.",
        roles=frozenset({"teacher"}),
        required_params=("user_id", "tenant_id", "topic"),
        feature_category="ai_async",
        execution_mode="async",
        output_type="text",
        channel_suitability="direct",
    ),
    WhatsAppToolSpec(
        name="get_child_performance",
        handler=get_child_performance,
        description="Parent summary of a child's marks and attendance.",
        roles=frozenset({"parent"}),
        required_params=("child_id", "tenant_id"),
        feature_category="erp_read",
        execution_mode="sync",
        output_type="text",
        channel_suitability="direct",
    ),
    WhatsAppToolSpec(
        name="get_child_attendance",
        handler=get_child_attendance,
        description="This week's attendance for a linked child.",
        roles=frozenset({"parent"}),
        required_params=("child_id", "tenant_id"),
        feature_category="erp_read",
        execution_mode="sync",
        output_type="text",
        channel_suitability="direct",
    ),
    WhatsAppToolSpec(
        name="get_child_homework",
        handler=get_child_homework,
        description="Pending homework for a linked child.",
        roles=frozenset({"parent"}),
        required_params=("child_id", "tenant_id"),
        feature_category="erp_read",
        execution_mode="sync",
        output_type="text",
        channel_suitability="direct",
    ),
    WhatsAppToolSpec(
        name="get_school_attendance_summary",
        handler=get_school_attendance_summary,
        description="School-wide attendance summary.",
        roles=frozenset({"admin"}),
        required_params=("tenant_id",),
        feature_category="erp_read",
        execution_mode="sync",
        output_type="text",
        channel_suitability="direct",
    ),
    WhatsAppToolSpec(
        name="get_fee_pending_report",
        handler=get_fee_pending_report,
        description="Outstanding fee summary for the school.",
        roles=frozenset({"admin"}),
        required_params=("tenant_id",),
        feature_category="erp_read",
        execution_mode="sync",
        output_type="text",
        channel_suitability="direct",
    ),
    WhatsAppToolSpec(
        name="get_ai_usage_stats",
        handler=get_ai_usage_stats,
        description="School-level AI usage analytics.",
        roles=frozenset({"admin"}),
        required_params=("tenant_id",),
        feature_category="erp_read",
        execution_mode="sync",
        output_type="text",
        channel_suitability="direct",
    ),
)

WHATSAPP_TOOL_REGISTRY = {spec.name: spec for spec in TOOL_SPECS}
ALL_WHATSAPP_TOOLS = [spec.handler for spec in TOOL_SPECS]


def get_tool_spec(tool_name: str) -> WhatsAppToolSpec | None:
    """Return the canonical metadata entry for a WhatsApp tool."""
    return WHATSAPP_TOOL_REGISTRY.get(tool_name)


def get_tool_specs_for_role(role: str) -> list[WhatsAppToolSpec]:
    """Return metadata entries for tools a role can access."""
    return [spec for spec in TOOL_SPECS if role in spec.roles]


def serialize_tool_catalog(role: str | None = None) -> list[dict]:
    """Return registry metadata in JSON-safe form for future admin/debug endpoints."""
    specs = TOOL_SPECS if role is None else get_tool_specs_for_role(role)
    return [
        {
            "name": spec.name,
            "description": spec.description,
            "roles": sorted(spec.roles),
            "required_params": list(spec.required_params),
            "feature_category": spec.feature_category,
            "execution_mode": spec.execution_mode,
            "output_type": spec.output_type,
            "channel_suitability": spec.channel_suitability,
        }
        for spec in specs
    ]


def get_tools_for_role(role: str) -> list:
    """Return only the handlers authorized for a given role."""
    return [spec.handler for spec in get_tool_specs_for_role(role)]
