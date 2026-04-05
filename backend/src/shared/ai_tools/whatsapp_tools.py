"""WhatsApp-specific ERP and AI tools for the LangGraph agent."""
import asyncio
import concurrent.futures
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
AI_ASSISTANT_ROLES = frozenset({"student", "teacher", "parent", "admin"})


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


@dataclass(frozen=True)
class WhatsAppFeatureTarget:
    """Tier 4.5 feature surface that must remain reachable through WhatsApp."""

    feature_key: str
    description: str
    tool_names: tuple[str, ...]
    required_roles: frozenset[str]

# ─── RBAC Map ─────────────────────────────────────────────────

TOOL_ROLE_MAP = {
    "ask_ai_question": {"student", "teacher", "parent", "admin"},
    "get_student_timetable": {"student"},
    "get_student_tests": {"student"},
    "get_student_assignments": {"student"},
    "get_student_attendance": {"student"},
    "get_student_results": {"student"},
    "get_student_weak_topics": {"student"},
    "generate_study_guide": {"student", "teacher", "parent", "admin"},
    "generate_audio_overview": {"student", "teacher", "parent", "admin"},
    "generate_quiz_now": {"student", "teacher", "parent", "admin"},
    "generate_quiz": {"student", "teacher", "parent", "admin"},
    "generate_flashcards": {"student", "teacher", "parent", "admin"},
    "generate_mindmap": {"student", "teacher", "parent", "admin"},
    "generate_flowchart": {"student", "teacher", "parent", "admin"},
    "generate_concept_map": {"student", "teacher", "parent", "admin"},
    "socratic_tutor": {"student", "teacher", "parent", "admin"},
    "debate_assistant": {"student", "teacher", "parent", "admin"},
    "essay_review": {"student", "teacher", "parent", "admin"},
    "get_teacher_schedule": {"teacher"},
    "get_teacher_absent_students": {"teacher"},
    "get_child_performance": {"parent"},
    "get_child_attendance": {"parent"},
    "get_child_homework": {"parent"},
    "get_school_attendance_summary": {"admin"},
    "get_fee_pending_report": {"admin"},
    "get_ai_usage_stats": {"admin"},
    "check_library_catalog": {"student", "teacher", "admin"},
}


TIER_4_5_FEATURE_TARGETS = (
    WhatsAppFeatureTarget(
        feature_key="grounded_qa",
        description="RAG-backed Q&A through WhatsApp.",
        tool_names=("ask_ai_question",),
        required_roles=AI_ASSISTANT_ROLES,
    ),
    WhatsAppFeatureTarget(
        feature_key="study_guide",
        description="Study-guide generation through WhatsApp.",
        tool_names=("generate_study_guide",),
        required_roles=AI_ASSISTANT_ROLES,
    ),
    WhatsAppFeatureTarget(
        feature_key="audio_overview",
        description="Audio overview generation through WhatsApp.",
        tool_names=("generate_audio_overview",),
        required_roles=AI_ASSISTANT_ROLES,
    ),
    WhatsAppFeatureTarget(
        feature_key="quiz",
        description="Quiz generation through WhatsApp.",
        tool_names=("generate_quiz_now",),
        required_roles=AI_ASSISTANT_ROLES,
    ),
    WhatsAppFeatureTarget(
        feature_key="flashcards",
        description="Flashcard generation through WhatsApp.",
        tool_names=("generate_flashcards",),
        required_roles=AI_ASSISTANT_ROLES,
    ),
    WhatsAppFeatureTarget(
        feature_key="mindmap",
        description="Mind-map generation through WhatsApp.",
        tool_names=("generate_mindmap",),
        required_roles=AI_ASSISTANT_ROLES,
    ),
    WhatsAppFeatureTarget(
        feature_key="flowchart",
        description="Flowchart generation through WhatsApp.",
        tool_names=("generate_flowchart",),
        required_roles=AI_ASSISTANT_ROLES,
    ),
    WhatsAppFeatureTarget(
        feature_key="concept_map",
        description="Concept-map generation through WhatsApp.",
        tool_names=("generate_concept_map",),
        required_roles=AI_ASSISTANT_ROLES,
    ),
    WhatsAppFeatureTarget(
        feature_key="socratic_tutor",
        description="Socratic tutoring through WhatsApp.",
        tool_names=("socratic_tutor",),
        required_roles=AI_ASSISTANT_ROLES,
    ),
    WhatsAppFeatureTarget(
        feature_key="debate_assistant",
        description="Debate assistance through WhatsApp.",
        tool_names=("debate_assistant",),
        required_roles=AI_ASSISTANT_ROLES,
    ),
    WhatsAppFeatureTarget(
        feature_key="essay_review",
        description="Essay review through WhatsApp.",
        tool_names=("essay_review",),
        required_roles=AI_ASSISTANT_ROLES,
    ),
    WhatsAppFeatureTarget(
        feature_key="student_erp",
        description="Student ERP lookups through WhatsApp.",
        tool_names=(
            "get_student_timetable",
            "get_student_tests",
            "get_student_assignments",
            "get_student_attendance",
            "get_student_results",
            "get_student_weak_topics",
        ),
        required_roles=frozenset({"student"}),
    ),
    WhatsAppFeatureTarget(
        feature_key="teacher_erp",
        description="Teacher ERP lookups through WhatsApp.",
        tool_names=("get_teacher_schedule", "get_teacher_absent_students"),
        required_roles=frozenset({"teacher"}),
    ),
    WhatsAppFeatureTarget(
        feature_key="parent_erp",
        description="Parent ERP lookups through WhatsApp.",
        tool_names=("get_child_performance", "get_child_attendance", "get_child_homework"),
        required_roles=frozenset({"parent"}),
    ),
    WhatsAppFeatureTarget(
        feature_key="admin_erp",
        description="Admin ERP lookups through WhatsApp.",
        tool_names=("get_school_attendance_summary", "get_fee_pending_report", "get_ai_usage_stats"),
        required_roles=frozenset({"admin"}),
    ),
)


def authorize_tool(tool_name: str, user_role: str) -> bool:
    """Check if a user role is authorized to call a specific tool."""
    spec = WHATSAPP_TOOL_REGISTRY.get(tool_name)
    allowed = spec.roles if spec else TOOL_ROLE_MAP.get(tool_name, set())
    return user_role in allowed


def _run_async(coro):
    """Run async AI helpers safely from synchronous LangChain tool wrappers."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coro).result()


def _append_citations(text: str, citations: list[dict] | None) -> str:
    if not citations:
        return text.strip()
    lines = [text.strip(), "", "Sources:"]
    for citation in citations[:5]:
        source = str(citation.get("source") or citation.get("title") or "Document").strip()
        if source:
            lines.append(f"- {source}")
    return "\n".join(lines).strip()


def _invoke_text_mode(tenant_id: str, prompt: str, mode: str, notebook_id: str | None = None) -> dict:
    from src.domains.platform.schemas.ai_runtime import InternalAIQueryRequest
    from src.domains.platform.services.ai_gateway import run_text_query

    request = InternalAIQueryRequest(
        tenant_id=str(tenant_id),
        query=prompt,
        mode=mode,
        notebook_id=notebook_id,
        language="english",
        response_length="default",
        expertise_level="standard",
    )
    return _run_async(run_text_query(request))


def _invoke_study_mode(
    tenant_id: str,
    tool_name: str,
    topic: str,
    notebook_id: str | None = None,
) -> dict:
    from src.domains.platform.schemas.ai_runtime import InternalStudyToolGenerateRequest
    from src.domains.platform.services.ai_gateway import run_study_tool

    request = InternalStudyToolGenerateRequest(
        tenant_id=str(tenant_id),
        tool=tool_name,
        topic=topic,
        subject_id=None,
        notebook_id=notebook_id,
    )
    return _run_async(run_study_tool(request))


def _format_study_tool_payload(tool_name: str, topic: str, result: dict) -> str:
    data = result.get("data")
    title = topic.strip() or "your topic"

    if tool_name == "quiz":
        lines = [f"📝 *Quiz: {title}*"]
        for item in data[:5]:
            lines.append("")
            lines.append(f"{item.get('index', 0)}. {item.get('question', '')}")
            for idx, option in enumerate(item.get("options", [])):
                lines.append(f"   {chr(65 + idx)}. {option}")
            correct = item.get("correct")
            if correct:
                lines.append(f"   Answer: {correct}")
            citation = str(item.get("citation") or "").strip()
            if citation:
                lines.append(f"   Source: {citation}")
        return _append_citations("\n".join(lines), result.get("citations"))

    if tool_name == "flashcards":
        lines = [f"🗂️ *Flashcards: {title}*"]
        for idx, card in enumerate(data[:8], start=1):
            lines.append("")
            lines.append(f"{idx}. Q: {card.get('front', '')}")
            lines.append(f"   A: {card.get('back', '')}")
            citation = str(card.get("citation") or "").strip()
            if citation:
                lines.append(f"   Source: {citation}")
        return _append_citations("\n".join(lines), result.get("citations"))

    if tool_name == "mindmap":
        root = str((data or {}).get("label") or title).strip() or title
        def walk_mindmap(node: dict, depth: int = 0) -> list[str]:
            lines: list[str] = []
            label = str(node.get("label") or "").strip()
            citation = str(node.get("citation") or "").strip()
            if label and depth > 0:
                prefix = "  " * max(depth - 1, 0)
                suffix = f" [{citation}]" if citation else ""
                lines.append(f"{prefix}- {label}{suffix}")
            for child in node.get("children", []) or []:
                if isinstance(child, dict):
                    lines.extend(walk_mindmap(child, depth + 1))
            return lines
        lines = [f"🧠 *Mind Map: {root}*"]
        lines.extend(walk_mindmap(data or {}, 0)[:10])
        lines.append("")
        lines.append("Open the web app for the full visual diagram.")
        return _append_citations("\n".join(lines), result.get("citations"))

    if tool_name == "concept_map":
        nodes = (data or {}).get("nodes") or []
        edges = (data or {}).get("edges") or []
        lines = [f"🔗 *Concept Map: {title}*"]
        for edge in edges[:8]:
            edge_from = edge.get("from")
            edge_to = edge.get("to")
            edge_label = edge.get("label")
            edge_citation = str(edge.get("citation") or "").strip()
            if edge_from and edge_to:
                relation = f" ({edge_label})" if edge_label else ""
                citation = f" [{edge_citation}]" if edge_citation else ""
                lines.append(f"- {edge_from} -> {edge_to}{relation}{citation}")
        if not edges:
            for node in nodes[:8]:
                label = str(node.get("label") or "").strip()
                if label:
                    lines.append(f"- {label}")
        lines.append("")
        lines.append("Open the web app for the full visual diagram.")
        return _append_citations("\n".join(lines), result.get("citations"))

    if tool_name == "flowchart":
        steps = (data or {}).get("steps") or []
        lines = [f"🪜 *Flowchart: {title}*"]
        for idx, step in enumerate(steps[:6], start=1):
            label = str(step.get("label") or "").strip()
            detail = str(step.get("detail") or "").strip()
            citation = str(step.get("citation") or "").strip()
            if label:
                lines.append(f"{idx}. {label}")
                if detail:
                    lines.append(f"   {detail}")
                if citation:
                    lines.append(f"   Source: {citation}")
        lines.extend(["", "Open the web app for the full visual diagram."])
        return _append_citations("\n".join(lines), result.get("citations"))

    return _append_citations(str(data or "").strip(), result.get("citations"))


# ─── Student Tools ────────────────────────────────────────────

@tool
def ask_ai_question(user_id: str, tenant_id: str, question: str, notebook_id: str | None = None) -> str:
    """Answer a user's question with the same AI stack used by the main app."""
    del user_id
    cleaned_question = (question or "").strip()
    if not cleaned_question:
        return "Please send a question, for example: *Explain photosynthesis*."

    try:
        result = _invoke_text_mode(str(tenant_id), cleaned_question, "qa", notebook_id=notebook_id)
        return _append_citations(str(result.get("answer", "")).strip(), result.get("citations"))
    except Exception as e:
        logger.error("ask_ai_question error: %s", e)
        return "Sorry, I couldn't answer that right now."


@tool
def generate_quiz_now(user_id: str, tenant_id: str, topic: str, notebook_id: str | None = None) -> str:
    """Generate a quiz directly for WhatsApp delivery."""
    del user_id
    cleaned_topic = (topic or "").strip()
    if not cleaned_topic:
        return "Please include a topic, for example: *Generate quiz for Class 8 science*."

    try:
        result = _invoke_study_mode(str(tenant_id), "quiz", cleaned_topic, notebook_id=notebook_id)
        return _format_study_tool_payload("quiz", cleaned_topic, result)
    except Exception as e:
        logger.error("generate_quiz_now error: %s", e)
        return "Sorry, I couldn't generate the quiz right now."


@tool
def generate_flashcards(user_id: str, tenant_id: str, topic: str, notebook_id: str | None = None) -> str:
    """Generate flashcards directly for WhatsApp delivery."""
    del user_id
    cleaned_topic = (topic or "").strip()
    if not cleaned_topic:
        return "Please include a topic, for example: *Create flashcards for photosynthesis*."

    try:
        result = _invoke_study_mode(str(tenant_id), "flashcards", cleaned_topic, notebook_id=notebook_id)
        return _format_study_tool_payload("flashcards", cleaned_topic, result)
    except Exception as e:
        logger.error("generate_flashcards error: %s", e)
        return "Sorry, I couldn't generate flashcards right now."


@tool
def generate_mindmap(user_id: str, tenant_id: str, topic: str, notebook_id: str | None = None) -> str:
    """Generate a mind map summary for WhatsApp delivery."""
    del user_id
    cleaned_topic = (topic or "").strip()
    if not cleaned_topic:
        return "Please include a topic, for example: *Create a mind map on biology chapter 3*."

    try:
        result = _invoke_study_mode(str(tenant_id), "mindmap", cleaned_topic, notebook_id=notebook_id)
        return _format_study_tool_payload("mindmap", cleaned_topic, result)
    except Exception as e:
        logger.error("generate_mindmap error: %s", e)
        return "Sorry, I couldn't generate the mind map right now."


@tool
def generate_flowchart(user_id: str, tenant_id: str, topic: str, notebook_id: str | None = None) -> str:
    """Generate a flowchart summary for WhatsApp delivery."""
    del user_id
    cleaned_topic = (topic or "").strip()
    if not cleaned_topic:
        return "Please include a topic, for example: *Create a flowchart for cell division*."

    try:
        result = _invoke_study_mode(str(tenant_id), "flowchart", cleaned_topic, notebook_id=notebook_id)
        return _format_study_tool_payload("flowchart", cleaned_topic, result)
    except Exception as e:
        logger.error("generate_flowchart error: %s", e)
        return "Sorry, I couldn't generate the flowchart right now."


@tool
def generate_concept_map(user_id: str, tenant_id: str, topic: str, notebook_id: str | None = None) -> str:
    """Generate a concept map summary for WhatsApp delivery."""
    del user_id
    cleaned_topic = (topic or "").strip()
    if not cleaned_topic:
        return "Please include a topic, for example: *Create a concept map for ecosystems*."

    try:
        result = _invoke_study_mode(str(tenant_id), "concept_map", cleaned_topic, notebook_id=notebook_id)
        return _format_study_tool_payload("concept_map", cleaned_topic, result)
    except Exception as e:
        logger.error("generate_concept_map error: %s", e)
        return "Sorry, I couldn't generate the concept map right now."


@tool
def socratic_tutor(user_id: str, tenant_id: str, topic: str, notebook_id: str | None = None) -> str:
    """Guide the user with Socratic questioning."""
    del user_id
    cleaned_topic = (topic or "").strip()
    if not cleaned_topic:
        return "Please include a topic, for example: *Teach me photosynthesis using Socratic questions*."

    try:
        result = _invoke_text_mode(str(tenant_id), cleaned_topic, "socratic", notebook_id=notebook_id)
        return _append_citations(str(result.get("answer", "")).strip(), result.get("citations"))
    except Exception as e:
        logger.error("socratic_tutor error: %s", e)
        return "Sorry, I couldn't start the Socratic tutor right now."


@tool
def debate_assistant(user_id: str, tenant_id: str, topic: str, notebook_id: str | None = None) -> str:
    """Generate a debate response or structure for the given topic."""
    del user_id
    cleaned_topic = (topic or "").strip()
    if not cleaned_topic:
        return "Please include a topic, for example: *Help me debate renewable energy*."

    try:
        result = _invoke_text_mode(str(tenant_id), cleaned_topic, "debate", notebook_id=notebook_id)
        return _append_citations(str(result.get("answer", "")).strip(), result.get("citations"))
    except Exception as e:
        logger.error("debate_assistant error: %s", e)
        return "Sorry, I couldn't prepare the debate help right now."


@tool
def essay_review(user_id: str, tenant_id: str, topic: str, notebook_id: str | None = None) -> str:
    """Review an essay or long-form answer through the AI review mode."""
    del user_id
    cleaned_topic = (topic or "").strip()
    if not cleaned_topic:
        return "Please include the essay or prompt you want reviewed."

    try:
        result = _invoke_text_mode(str(tenant_id), cleaned_topic, "essay_review", notebook_id=notebook_id)
        return _append_citations(str(result.get("answer", "")).strip(), result.get("citations"))
    except Exception as e:
        logger.error("essay_review error: %s", e)
        return "Sorry, I couldn't review the essay right now."

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
def generate_study_guide(user_id: str, tenant_id: str, topic: str, notebook_id: str | None = None) -> str:
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
            notebook_id=notebook_id,
            language="english",
            response_length="default",
            expertise_level="standard",
            tenant_id=str(tenant_id),
        )
        job = enqueue_job(
            JOB_TYPE_QUERY,
            payload.model_dump(mode="json"),
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
def generate_audio_overview(user_id: str, tenant_id: str, topic: str, notebook_id: str | None = None) -> str:
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
            notebook_id=notebook_id,
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


@tool
def check_library_catalog(query: str, tenant_id: str) -> str:
    """Search the school library catalog."""
    try:
        from src.shared.ai_tools.erp_tools import check_library_catalog as erp_check_library_catalog

        return erp_check_library_catalog.invoke({"query": query, "tenant_id": tenant_id})
    except Exception as e:
        logger.error("check_library_catalog error: %s", e)
        return "Sorry, I couldn't search the library right now."


# ─── Tool Registry ────────────────────────────────────────────

TOOL_SPECS = (
    WhatsAppToolSpec(
        name="ask_ai_question",
        handler=ask_ai_question,
        description="RAG-backed question answering using the same AI stack as the main app.",
        roles=AI_ASSISTANT_ROLES,
        required_params=("user_id", "tenant_id", "question"),
        feature_category="ai_sync",
        execution_mode="sync",
        output_type="text",
        channel_suitability="direct",
    ),
    WhatsAppToolSpec(
        name="generate_quiz_now",
        handler=generate_quiz_now,
        description="Generate a quiz directly in WhatsApp.",
        roles=AI_ASSISTANT_ROLES,
        required_params=("user_id", "tenant_id", "topic"),
        feature_category="ai_sync",
        execution_mode="sync",
        output_type="text",
        channel_suitability="direct",
    ),
    WhatsAppToolSpec(
        name="generate_flashcards",
        handler=generate_flashcards,
        description="Generate flashcards directly in WhatsApp.",
        roles=AI_ASSISTANT_ROLES,
        required_params=("user_id", "tenant_id", "topic"),
        feature_category="ai_sync",
        execution_mode="sync",
        output_type="text",
        channel_suitability="direct",
    ),
    WhatsAppToolSpec(
        name="generate_mindmap",
        handler=generate_mindmap,
        description="Generate a mind map summary for WhatsApp.",
        roles=AI_ASSISTANT_ROLES,
        required_params=("user_id", "tenant_id", "topic"),
        feature_category="ai_sync",
        execution_mode="sync",
        output_type="text",
        channel_suitability="summary_plus_link",
    ),
    WhatsAppToolSpec(
        name="generate_flowchart",
        handler=generate_flowchart,
        description="Generate a flowchart summary for WhatsApp.",
        roles=AI_ASSISTANT_ROLES,
        required_params=("user_id", "tenant_id", "topic"),
        feature_category="ai_sync",
        execution_mode="sync",
        output_type="text",
        channel_suitability="summary_plus_link",
    ),
    WhatsAppToolSpec(
        name="generate_concept_map",
        handler=generate_concept_map,
        description="Generate a concept map summary for WhatsApp.",
        roles=AI_ASSISTANT_ROLES,
        required_params=("user_id", "tenant_id", "topic"),
        feature_category="ai_sync",
        execution_mode="sync",
        output_type="text",
        channel_suitability="summary_plus_link",
    ),
    WhatsAppToolSpec(
        name="socratic_tutor",
        handler=socratic_tutor,
        description="Use Socratic tutoring mode on a topic.",
        roles=AI_ASSISTANT_ROLES,
        required_params=("user_id", "tenant_id", "topic"),
        feature_category="ai_sync",
        execution_mode="sync",
        output_type="text",
        channel_suitability="direct",
    ),
    WhatsAppToolSpec(
        name="debate_assistant",
        handler=debate_assistant,
        description="Get debate help for a topic or claim.",
        roles=AI_ASSISTANT_ROLES,
        required_params=("user_id", "tenant_id", "topic"),
        feature_category="ai_sync",
        execution_mode="sync",
        output_type="text",
        channel_suitability="direct",
    ),
    WhatsAppToolSpec(
        name="essay_review",
        handler=essay_review,
        description="Review an essay or answer draft.",
        roles=AI_ASSISTANT_ROLES,
        required_params=("user_id", "tenant_id", "topic"),
        feature_category="ai_sync",
        execution_mode="sync",
        output_type="text",
        channel_suitability="direct",
    ),
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
        roles=AI_ASSISTANT_ROLES,
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
        roles=AI_ASSISTANT_ROLES,
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
    WhatsAppToolSpec(
        name="check_library_catalog",
        handler=check_library_catalog,
        description="Search the school library catalog.",
        roles=frozenset({"student", "teacher", "admin"}),
        required_params=("query", "tenant_id"),
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


def serialize_tier_4_5_feature_matrix() -> list[dict]:
    """Return a machine-checkable status view of the Tier 4.5 WhatsApp feature surface."""
    matrix: list[dict] = []
    for target in TIER_4_5_FEATURE_TARGETS:
        tool_statuses = []
        missing_tools: list[str] = []
        for tool_name in target.tool_names:
            spec = get_tool_spec(tool_name)
            if spec is None:
                missing_tools.append(tool_name)
                tool_statuses.append(
                    {
                        "tool_name": tool_name,
                        "exists": False,
                        "roles": [],
                        "missing_roles": sorted(target.required_roles),
                    }
                )
                continue

            missing_roles = sorted(target.required_roles.difference(spec.roles))
            tool_statuses.append(
                {
                    "tool_name": tool_name,
                    "exists": True,
                    "roles": sorted(spec.roles),
                    "missing_roles": missing_roles,
                    "execution_mode": spec.execution_mode,
                    "channel_suitability": spec.channel_suitability,
                }
            )

        missing_role_bindings = [
            item["tool_name"]
            for item in tool_statuses
            if item.get("exists") and item.get("missing_roles")
        ]
        status = "complete" if not missing_tools and not missing_role_bindings else "partial"
        matrix.append(
            {
                "feature_key": target.feature_key,
                "description": target.description,
                "required_roles": sorted(target.required_roles),
                "tools": tool_statuses,
                "missing_tools": missing_tools,
                "missing_role_bindings": missing_role_bindings,
                "status": status,
            }
        )
    return matrix


def get_tools_for_role(role: str) -> list:
    """Return only the handlers authorized for a given role."""
    return [spec.handler for spec in get_tool_specs_for_role(role)]
