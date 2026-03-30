"""WhatsApp LangGraph agent for intent interpretation, tool dispatch, and response formatting."""
from __future__ import annotations

import asyncio
import concurrent.futures
import logging
import re
from typing import Optional, TypedDict

from pydantic import BaseModel, Field

try:
    from langgraph.graph import END, StateGraph
except ModuleNotFoundError:  # Lightweight test environments
    END = "__end__"

    class _CompiledGraph:
        def __init__(self, graph):
            self._graph = graph

        def invoke(self, state):
            current = self._graph.entry_point
            current_state = dict(state)
            while current and current != END:
                node_fn = self._graph.nodes[current]
                result = node_fn(current_state) or {}
                current_state.update(result)
                if current in self._graph.conditional_edges:
                    router, mapping = self._graph.conditional_edges[current]
                    current = mapping[router(current_state)]
                else:
                    current = self._graph.edges.get(current, END)
            return current_state

    class StateGraph:
        def __init__(self, _state_type):
            self.nodes = {}
            self.edges = {}
            self.conditional_edges = {}
            self.entry_point = None

        def add_node(self, name, fn):
            self.nodes[name] = fn

        def set_entry_point(self, name):
            self.entry_point = name

        def add_conditional_edges(self, source, router, mapping):
            self.conditional_edges[source] = (router, mapping)

        def add_edge(self, source, target):
            self.edges[source] = target

        def compile(self):
            return _CompiledGraph(self)


logger = logging.getLogger(__name__)

WHATSAPP_CONFIRM_TOKENS = {"confirm", "yes", "approve", "approved", "ok", "okay", "proceed", "do it"}
WHATSAPP_CANCEL_TOKENS = {"cancel", "stop", "reject", "no", "abort", "skip", "dont", "don't"}

DETERMINISTIC_TOOLS = {
    "ask_ai_question",
    "get_student_timetable",
    "get_student_tests",
    "get_student_assignments",
    "get_student_attendance",
    "get_student_results",
    "get_teacher_absent_students",
    "get_teacher_schedule",
    "get_child_performance",
    "get_child_attendance",
    "get_child_homework",
    "get_school_attendance_summary",
    "get_fee_pending_report",
    "get_ai_usage_stats",
    "check_library_catalog",
    "generate_quiz",
    "generate_quiz_now",
    "generate_flashcards",
    "generate_mindmap",
    "generate_flowchart",
    "generate_concept_map",
    "socratic_tutor",
    "debate_assistant",
    "essay_review",
}

TOOL_ALIASES = {
    "generate_quiz": "generate_quiz_now",
}

STUDY_OUTPUT_TOOLS = {
    "generate_study_guide",
    "generate_audio_overview",
    "generate_quiz",
    "generate_flashcards",
    "generate_mindmap",
    "generate_flowchart",
    "generate_concept_map",
    "socratic_tutor",
    "debate_assistant",
    "essay_review",
    "ask_ai_question",
}

TOOL_HINT_LABELS = {
    "generate_quiz": "quiz",
    "generate_flashcards": "flashcards",
    "generate_mindmap": "mind map",
    "generate_flowchart": "flowchart",
    "generate_concept_map": "concept map",
    "generate_study_guide": "study guide",
    "generate_audio_overview": "audio overview",
    "ask_ai_question": "explanation",
}


class WhatsAppAgentState(TypedDict):
    message: str
    user_id: str
    tenant_id: str
    notebook_id: Optional[str]
    role: str
    conversation_history: list
    intent: Optional[str]
    tool_name: Optional[str]
    tool_args: Optional[dict]
    tool_result: Optional[str]
    response: Optional[str]
    response_type: str


class IntentInterpretation(BaseModel):
    normalized_message: str = Field(default="")
    translated_message: str = Field(default="")
    tool_name: Optional[str] = Field(default=None)
    question: Optional[str] = Field(default=None)
    topic: Optional[str] = Field(default=None)
    is_general_chat: bool = Field(default=False)


INTENT_MAP = {
    "timetable": "get_student_timetable",
    "schedule": "get_student_timetable",
    "class today": "get_student_timetable",
    "classes": "get_student_timetable",
    "test": "get_student_tests",
    "exam": "get_student_tests",
    "assignment": "get_student_assignments",
    "homework": "get_student_assignments",
    "pending": "get_student_assignments",
    "attendance": "get_student_attendance",
    "absent": "get_student_attendance",
    "marks": "get_student_results",
    "results": "get_student_results",
    "score": "get_student_results",
    "grade": "get_student_results",
    "weak": "get_student_weak_topics",
    "improve": "get_student_weak_topics",
    "study guide": "generate_study_guide",
    "audio overview": "generate_audio_overview",
    "audio summary": "generate_audio_overview",
    "podcast": "generate_audio_overview",
    "quiz bana": "generate_quiz",
    "generate quiz": "generate_quiz",
    "create quiz": "generate_quiz",
    "make quiz": "generate_quiz",
    "flashcard": "generate_flashcards",
    "flashcards": "generate_flashcards",
    "mind map": "generate_mindmap",
    "mindmap": "generate_mindmap",
    "flow chart": "generate_flowchart",
    "flowchart": "generate_flowchart",
    "concept map": "generate_concept_map",
    "concept-map": "generate_concept_map",
    "socratic": "socratic_tutor",
    "debate": "debate_assistant",
    "essay review": "essay_review",
    "review essay": "essay_review",
    "check essay": "essay_review",
    "explain": "ask_ai_question",
    "summary": "ask_ai_question",
    "summarize": "ask_ai_question",
    "what is": "ask_ai_question",
    "why is": "ask_ai_question",
    "how does": "ask_ai_question",
    "tell me about": "ask_ai_question",
    "samjha": "ask_ai_question",
    "samjhao": "ask_ai_question",
    "samajh": "ask_ai_question",
    "bata": "ask_ai_question",
    "batao": "ask_ai_question",
    "kaise": "ask_ai_question",
    "mala": "ask_ai_question",
    "pahije": "ask_ai_question",
    "child performance": "get_child_performance",
    "performance": "get_child_performance",
    "child attendance": "get_child_attendance",
    "child homework": "get_child_homework",
    "attendance summary": "get_school_attendance_summary",
    "school attendance": "get_school_attendance_summary",
    "fee": "get_fee_pending_report",
    "fees": "get_fee_pending_report",
    "pending fees": "get_fee_pending_report",
    "ai usage": "get_ai_usage_stats",
    "ai stats": "get_ai_usage_stats",
    "usage": "get_ai_usage_stats",
    "library": "check_library_catalog",
    "books": "check_library_catalog",
}

ROLE_INTENT_OVERRIDES = {
    "teacher": {
        "generate quiz": "generate_quiz",
        "quiz bana": "generate_quiz",
        "attendance": "get_teacher_absent_students",
        "absent": "get_teacher_absent_students",
        "schedule": "get_teacher_schedule",
        "timetable": "get_teacher_schedule",
        "classes": "get_teacher_schedule",
        "class today": "get_teacher_schedule",
    },
    "parent": {
        "attendance": "get_child_attendance",
        "homework": "get_child_homework",
        "assignment": "get_child_homework",
        "pending": "get_child_homework",
        "marks": "get_child_performance",
        "results": "get_child_performance",
        "performance": "get_child_performance",
    },
    "admin": {
        "attendance": "get_school_attendance_summary",
        "fee": "get_fee_pending_report",
        "fees": "get_fee_pending_report",
        "pending": "get_fee_pending_report",
        "library": "check_library_catalog",
        "books": "check_library_catalog",
    },
}


def _run_async(coro):
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coro).result()


def _extract_topic_from_message(message: str) -> str:
    text = (message or "").strip()
    lowered = text.lower()
    prefixes = [
        "generate quiz for",
        "create quiz for",
        "make quiz for",
        "generate quiz on",
        "create quiz on",
        "make quiz on",
        "quiz on",
        "quiz for",
        "quiz bana",
        "generate flashcards for",
        "create flashcards for",
        "make flashcards for",
        "flashcards for",
        "mala flashcards pahije",
        "generate mind map for",
        "create mind map for",
        "mind map on",
        "mind map for",
        "generate flowchart for",
        "create flowchart for",
        "flowchart for",
        "flow chart for",
        "generate concept map for",
        "concept map for",
        "teach me",
        "explain",
        "summarize",
        "summary of",
        "tell me about",
        "what is",
        "why is",
        "how does",
        "help me debate",
        "review essay",
        "check essay",
        "essay review",
        "study guide for",
        "study guide on",
        "generate study guide for",
        "create study guide for",
        "audio overview for",
        "audio overview on",
        "generate audio overview for",
        "create audio overview for",
        "podcast for",
        "podcast on",
        "books on",
        "library books on",
    ]
    for prefix in prefixes:
        if lowered.startswith(prefix):
            return text[len(prefix):].strip(" :-?") or text
    return text


def _extract_explicit_topic(message: str) -> str:
    text = (message or "").strip()
    lowered = text.lower()
    prefixes = [
        "generate quiz for",
        "create quiz for",
        "make quiz for",
        "generate quiz on",
        "create quiz on",
        "make quiz on",
        "quiz on",
        "quiz for",
        "quiz bana",
        "generate flashcards for",
        "create flashcards for",
        "make flashcards for",
        "flashcards for",
        "mala flashcards pahije",
        "generate mind map for",
        "create mind map for",
        "mind map on",
        "mind map for",
        "mind map bana",
        "generate flowchart for",
        "create flowchart for",
        "flowchart for",
        "flow chart for",
        "flowchart bana",
        "generate concept map for",
        "concept map for",
        "concept map bana",
        "teach me",
        "explain",
        "summarize",
        "summary of",
        "tell me about",
        "what is",
        "why is",
        "how does",
        "help me debate",
        "review essay",
        "check essay",
        "essay review",
        "study guide for",
        "study guide on",
        "generate study guide for",
        "create study guide for",
        "audio overview for",
        "audio overview on",
        "generate audio overview for",
        "create audio overview for",
        "podcast for",
        "podcast on",
    ]
    for prefix in prefixes:
        if lowered.startswith(prefix):
            return text[len(prefix):].strip(" :-?")
    return text


def _detect_conflicting_study_tools(message: str) -> list[str]:
    msg = (message or "").lower()
    matched: list[str] = []
    checks = (
        ("generate_quiz", ("quiz", "mcq", "prashnottari")),
        ("generate_flashcards", ("flashcard", "flashcards")),
        ("generate_mindmap", ("mind map", "mindmap")),
        ("generate_flowchart", ("flowchart", "flow chart")),
        ("generate_concept_map", ("concept map", "concept-map")),
        ("generate_study_guide", ("study guide", "notes")),
        ("generate_audio_overview", ("audio overview", "audio summary", "podcast")),
    )
    for tool_name, markers in checks:
        if any(marker in msg for marker in markers):
            matched.append(tool_name)
    return matched


def _build_clarification_result(message: str, prompt: str, *, reason: str) -> dict:
    return {
        "intent": "clarify_request",
        "tool_name": None,
        "tool_args": {
            "normalized_message": message.strip(),
            "clarification_prompt": prompt.strip(),
            "clarification_reason": reason,
        },
        "response_type": "text",
    }


def _maybe_build_clarification(
    message: str,
    *,
    heuristic_tool: Optional[str],
    similarity_tool: Optional[str],
    llm_tool: Optional[str],
) -> Optional[dict]:
    explicit_topic = _extract_explicit_topic(message).strip()
    conflicting_tools = _detect_conflicting_study_tools(message)
    if len(set(conflicting_tools)) > 1:
        return _build_clarification_result(
            message,
            (
                "I can do that, but choose one format first: *quiz*, *flashcards*, *mind map*, "
                "*flowchart*, *concept map*, or *study guide*."
            ),
            reason="multiple_study_tools",
        )

    resolved_tool = llm_tool or heuristic_tool or similarity_tool
    if resolved_tool in STUDY_OUTPUT_TOOLS and not explicit_topic:
        label = TOOL_HINT_LABELS.get(resolved_tool, "topic")
        example = "Explain photosynthesis" if resolved_tool == "ask_ai_question" else f"{label} on photosynthesis"
        return _build_clarification_result(
            message,
            f"Tell me the topic too. Example: *{example}*.",
            reason="missing_topic",
        )
    return None


def _log_intent_decision(
    *,
    role: str,
    message: str,
    heuristic_tool: Optional[str],
    similarity_tool: Optional[str],
    llm_tool: Optional[str],
    final_intent: str,
    normalized_message: Optional[str] = None,
    translated_message: Optional[str] = None,
    clarification_reason: Optional[str] = None,
) -> None:
    logger.info(
        "whatsapp_intent_decision role=%s heuristic=%s similarity=%s llm=%s final=%s clarify=%s normalized=%r translated=%r message=%r",
        role,
        heuristic_tool,
        similarity_tool,
        llm_tool,
        final_intent,
        clarification_reason,
        normalized_message,
        translated_message,
        message,
    )


def _classify_intent_heuristic(message: str, role: str) -> Optional[str]:
    msg_lower = message.lower().strip()

    for keyword, tool_name in ROLE_INTENT_OVERRIDES.get(role, {}).items():
        if keyword in msg_lower:
            return tool_name

    for keyword, tool_name in INTENT_MAP.items():
        if keyword in msg_lower:
            return tool_name

    return None


def _classify_intent_similarity(message: str, role: str) -> dict:
    stopwords = {
        "what", "is", "my", "the", "a", "an", "can", "you", "show", "me", "tell",
        "about", "did", "do", "i", "have", "any", "for", "of", "to", "please",
        "kindly", "are", "there",
    }
    tool_corpus = {
        "ask_ai_question": {"explain", "question", "topic", "why", "how", "summary", "meaning", "describe", "samjhao", "batao"},
        "get_student_timetable": {"class", "classes", "schedule", "timetable", "period", "today", "subject", "teach"},
        "get_student_tests": {"test", "tests", "exam", "exams", "quiz", "quizzes", "assessment", "score"},
        "get_student_assignments": {"assignment", "assignments", "homework", "pending", "due", "task", "project"},
        "get_student_attendance": {"attendance", "absent", "present", "leave", "holiday", "attended"},
        "get_student_results": {"marks", "results", "score", "grade", "report", "passed", "failed"},
        "get_student_weak_topics": {"weak", "improve", "study", "guide", "bad", "failing", "attention"},
        "generate_study_guide": {"study", "guide", "summary", "notes", "chapter", "topic"},
        "generate_audio_overview": {"audio", "overview", "podcast", "listen", "summary", "topic"},
        "generate_quiz": {"generate", "quiz", "mcq", "assessment", "class", "topic", "bana"},
        "generate_flashcards": {"flashcard", "flashcards", "cards", "memorize", "pahije"},
        "generate_mindmap": {"mind", "map", "mindmap"},
        "generate_flowchart": {"flowchart", "flow", "steps", "process"},
        "generate_concept_map": {"concept", "map", "conceptmap", "relationship"},
        "socratic_tutor": {"socratic", "questions", "guide", "teach"},
        "debate_assistant": {"debate", "argument", "counterargument", "claim"},
        "essay_review": {"essay", "review", "feedback", "draft"},
        "get_teacher_absent_students": {"absent", "students", "who", "missing", "attendance", "today"},
        "get_teacher_schedule": {"teach", "schedule", "timetable", "classes", "today"},
        "get_child_performance": {"child", "performance", "doing", "progress", "marks", "results"},
        "get_child_attendance": {"child", "attendance", "absent", "present", "school"},
        "get_child_homework": {"child", "homework", "assignment", "pending", "due"},
        "get_school_attendance_summary": {"attendance", "summary", "school", "total", "students", "present", "absent"},
        "get_fee_pending_report": {"fee", "fees", "pending", "outstanding", "money", "paid", "due", "report"},
        "get_ai_usage_stats": {"ai", "usage", "stats", "statistics", "queries", "bot"},
        "check_library_catalog": {"library", "books", "book", "author", "catalog", "read", "borrow"},
    }

    from src.shared.ai_tools.whatsapp_tools import TOOL_ROLE_MAP

    msg_tokens = set(re.findall(r"\b\w+\b", message.lower())) - stopwords
    if not msg_tokens:
        return {"tool_name": None, "is_general_chat": True}

    best_tool = None
    best_score = 0.0
    for tool_name, corpus_tokens in tool_corpus.items():
        if role not in TOOL_ROLE_MAP.get(tool_name, set()):
            continue
        intersection = len(msg_tokens.intersection(corpus_tokens))
        union = len(msg_tokens.union(corpus_tokens))
        score = float(intersection) / union if union > 0 else 0.0
        if score > best_score:
            best_score = score
            best_tool = tool_name

    if best_score >= 0.15:
        return {"tool_name": best_tool, "is_general_chat": False}
    return {"tool_name": None, "is_general_chat": True}


def _looks_like_ai_query(message: str) -> bool:
    msg = (message or "").strip().lower()
    if not msg:
        return False

    excluded = {
        "hello",
        "hi",
        "hey",
        "thank you",
        "thanks",
        "tell me a joke",
        "what's the weather today?",
        "what is the capital of france?",
    }
    if msg in excluded:
        return False

    query_markers = (
        "?",
        "explain",
        "summary",
        "summarize",
        "what is",
        "why",
        "how",
        "tell me about",
        "samjha",
        "samjhao",
        "bata",
        "batao",
        "kaise",
    )
    return any(marker in msg for marker in query_markers)


def _message_needs_llm_interpretation(message: str) -> bool:
    text = (message or "").strip().lower()
    if not text:
        return False
    if any(ord(ch) > 127 for ch in text):
        return True

    mixed_language_markers = (
        " kar",
        " karo",
        " bana",
        " banao",
        " samjha",
        " samjhao",
        " bata",
        " batao",
        " kaise",
        " mala",
        " pahije",
        " ahe",
        " chahiye",
        " hai",
        " adhyay",
        " prashnottari",
        " var",
        " cha ",
        " ki ",
    )
    return any(marker in f" {text} " for marker in mixed_language_markers)


def _build_intent_result(
    tool_name: Optional[str],
    message: str,
    *,
    topic: Optional[str] = None,
    question: Optional[str] = None,
    normalized_message: Optional[str] = None,
    translated_message: Optional[str] = None,
) -> dict:
    resolved_topic = (topic or _extract_topic_from_message(message) or message).strip()
    resolved_question = (question or resolved_topic or message).strip()
    return {
        "intent": tool_name,
        "tool_name": tool_name,
        "tool_args": {
            "topic": resolved_topic,
            "question": resolved_question,
            "normalized_message": (normalized_message or message).strip(),
            "translated_message": (translated_message or resolved_question).strip(),
        },
        "response_type": "text",
    }


def _llm_interpretation(message: str, role: str) -> Optional[IntentInterpretation]:
    from src.infrastructure.llm.providers import get_llm_provider
    from src.shared.ai_tools.whatsapp_tools import serialize_tool_catalog

    catalog = serialize_tool_catalog(role)
    allowed_tools = [item["name"] for item in catalog]
    if "ask_ai_question" not in allowed_tools:
        allowed_tools.append("ask_ai_question")

    prompt = (
        "You are a WhatsApp request interpreter for a school AI assistant.\n"
        "The user may write in English, Hindi, Marathi, or mixed Hinglish.\n"
        "Translate the request to clear English, infer what the user wants, and choose the best tool.\n"
        "If the request is an educational or app-use request but does not match a specialized tool, use ask_ai_question.\n"
        "If it is casual small talk, set is_general_chat=true and tool_name=null.\n"
        f"Allowed tools for this role: {', '.join(sorted(set(allowed_tools)))}.\n"
        "Return structured data only.\n\n"
        f"Role: {role}\n"
        f"User message: {message}"
    )

    try:
        provider = get_llm_provider()
        raw = _run_async(provider.generate_structured(prompt, IntentInterpretation))
        payload = raw.get("response", raw)
        if isinstance(payload, IntentInterpretation):
            return payload
        if isinstance(payload, dict):
            tool_name = payload.get("tool_name")
            if tool_name not in allowed_tools and tool_name != "ask_ai_question":
                tool_name = None
            return IntentInterpretation(
                normalized_message=str(payload.get("normalized_message") or "").strip(),
                translated_message=str(payload.get("translated_message") or "").strip(),
                tool_name=tool_name,
                question=str(payload.get("question") or "").strip() or None,
                topic=str(payload.get("topic") or "").strip() or None,
                is_general_chat=bool(payload.get("is_general_chat", False)),
            )
    except Exception:
        logger.exception("LLM intent interpretation failed")
    return None


def classify_intent(state: WhatsAppAgentState) -> dict:
    message = state["message"]
    role = state["role"]

    heuristic_tool = _classify_intent_heuristic(message, role)
    tool_name = heuristic_tool
    similarity = {"tool_name": None, "is_general_chat": True}
    if not tool_name:
        similarity = _classify_intent_similarity(message, role)
        tool_name = similarity.get("tool_name")

    interpretation = None
    if tool_name is None or _message_needs_llm_interpretation(message):
        interpretation = _llm_interpretation(message, role)

    clarification = _maybe_build_clarification(
        message,
        heuristic_tool=heuristic_tool,
        similarity_tool=similarity.get("tool_name"),
        llm_tool=interpretation.tool_name if interpretation else None,
    )
    if clarification:
        _log_intent_decision(
            role=role,
            message=message,
            heuristic_tool=heuristic_tool,
            similarity_tool=similarity.get("tool_name"),
            llm_tool=interpretation.tool_name if interpretation else None,
            final_intent="clarify_request",
            normalized_message=clarification["tool_args"].get("normalized_message"),
            clarification_reason=clarification["tool_args"].get("clarification_reason"),
        )
        return clarification

    if interpretation and interpretation.tool_name:
        result = _build_intent_result(
            interpretation.tool_name,
            message,
            topic=interpretation.topic or interpretation.translated_message,
            question=interpretation.question or interpretation.translated_message,
            normalized_message=interpretation.normalized_message,
            translated_message=interpretation.translated_message,
        )
        _log_intent_decision(
            role=role,
            message=message,
            heuristic_tool=heuristic_tool,
            similarity_tool=similarity.get("tool_name"),
            llm_tool=interpretation.tool_name,
            final_intent=result["intent"] or "general_chat",
            normalized_message=result["tool_args"].get("normalized_message"),
            translated_message=result["tool_args"].get("translated_message"),
        )
        return result

    if tool_name:
        result = _build_intent_result(tool_name, message)
        _log_intent_decision(
            role=role,
            message=message,
            heuristic_tool=heuristic_tool,
            similarity_tool=similarity.get("tool_name"),
            llm_tool=interpretation.tool_name if interpretation else None,
            final_intent=result["intent"] or "general_chat",
            normalized_message=result["tool_args"].get("normalized_message"),
            translated_message=result["tool_args"].get("translated_message"),
        )
        return result

    if _looks_like_ai_query(message):
        topic = _extract_topic_from_message(message)
        result = _build_intent_result(
            "ask_ai_question",
            message,
            topic=topic,
            question=topic or message,
        )
        _log_intent_decision(
            role=role,
            message=message,
            heuristic_tool=heuristic_tool,
            similarity_tool=similarity.get("tool_name"),
            llm_tool=interpretation.tool_name if interpretation else None,
            final_intent=result["intent"] or "general_chat",
            normalized_message=result["tool_args"].get("normalized_message"),
            translated_message=result["tool_args"].get("translated_message"),
        )
        return result

    result = {
        "intent": "general_chat",
        "tool_name": None,
        "tool_args": {"normalized_message": message.strip()},
        "response_type": "text",
    }
    _log_intent_decision(
        role=role,
        message=message,
        heuristic_tool=heuristic_tool,
        similarity_tool=similarity.get("tool_name"),
        llm_tool=interpretation.tool_name if interpretation else None,
        final_intent="general_chat",
        normalized_message=message.strip(),
    )
    return result


def execute_tool(state: WhatsAppAgentState) -> dict:
    tool_name = state.get("tool_name")
    tool_args = state.get("tool_args") or {}

    if not tool_name:
        return {"tool_result": None}

    from src.shared.ai_tools.whatsapp_tools import ALL_WHATSAPP_TOOLS, authorize_tool

    if not authorize_tool(tool_name, state["role"]):
        return {
            "tool_result": f"Sorry, {tool_name.replace('_', ' ')} is not available for {state['role']} accounts.",
        }

    lookup_name = TOOL_ALIASES.get(tool_name, tool_name)
    tool_fn = next((tool for tool in ALL_WHATSAPP_TOOLS if tool.name == lookup_name), None)
    if tool_fn is None:
        return {"tool_result": "Tool not found."}

    try:
        topic = str(tool_args.get("topic") or _extract_topic_from_message(state["message"]) or state["message"]).strip()
        question = str(tool_args.get("question") or topic or state["message"]).strip()

        if tool_name == "ask_ai_question":
            result = tool_fn.invoke({
                "user_id": state["user_id"],
                "tenant_id": state["tenant_id"],
                "question": question,
                "notebook_id": state.get("notebook_id"),
            })
            return {"tool_result": result}

        if tool_name == "check_library_catalog":
            result = tool_fn.invoke({
                "query": topic or state["message"],
                "tenant_id": state["tenant_id"],
            })
            return {"tool_result": result}

        if tool_name in {
            "generate_quiz",
            "generate_study_guide",
            "generate_audio_overview",
            "generate_flashcards",
            "generate_mindmap",
            "generate_flowchart",
            "generate_concept_map",
            "socratic_tutor",
            "debate_assistant",
            "essay_review",
        }:
            result = tool_fn.invoke({
                "user_id": state["user_id"],
                "tenant_id": state["tenant_id"],
                "topic": topic,
                "notebook_id": state.get("notebook_id"),
            })
            return {"tool_result": result}

        if state["role"] == "parent" and tool_name.startswith("get_child_"):
            result = tool_fn.invoke({
                "child_id": state["user_id"],
                "tenant_id": state["tenant_id"],
            })
            return {"tool_result": result}

        if tool_name in {"get_school_attendance_summary", "get_fee_pending_report", "get_ai_usage_stats"}:
            result = tool_fn.invoke({"tenant_id": state["tenant_id"]})
            return {"tool_result": result}

        result = tool_fn.invoke({
            "user_id": state["user_id"],
            "tenant_id": state["tenant_id"],
        })
        return {"tool_result": result}
    except Exception as exc:
        logger.exception("Tool execution failed: %s", tool_name)
        return {"tool_result": f"Error executing request: {exc}"}


def generate_response(state: WhatsAppAgentState) -> dict:
    if state.get("tool_result"):
        return {"response": state["tool_result"]}

    if state.get("intent") == "clarify_request":
        prompt = str((state.get("tool_args") or {}).get("clarification_prompt") or "").strip()
        if prompt:
            return {"response": prompt}

    try:
        from src.infrastructure.llm.providers import get_llm_provider

        llm = get_llm_provider()
        history_str = ""
        for msg in state.get("conversation_history", [])[-6:]:
            history_str += f"\n{msg.get('role', 'user')}: {msg.get('content', '')}"

        prompt = (
            f"You are VidyaOS, a school WhatsApp assistant. The user is a {state['role']}.\n"
            "Reply briefly, clearly, and helpfully. Keep it under 180 words.\n"
            "If the user needs ERP or AI actions, tell them to ask directly in natural language.\n"
            f"Conversation:{history_str}\n\n"
            f"user: {state['message']}\nassistant:"
        )
        result = _run_async(llm.generate(prompt, temperature=0.4))
        return {"response": result.get("response", "")}
    except Exception:
        logger.exception("LLM response generation failed")
        return {
            "response": (
                "I can help with timetable, attendance, assignments, results, uploaded study material, "
                "and AI study tools. Ask naturally, for example: *Explain photosynthesis*."
            ),
        }


def format_for_whatsapp(state: WhatsAppAgentState) -> dict:
    response = str(state.get("response") or "").strip()
    return {"response": response, "response_type": "text"}


def needs_tool(state: WhatsAppAgentState) -> str:
    if state.get("tool_name"):
        return "execute_tool"
    return "generate_response"


def route_after_tool(state: WhatsAppAgentState) -> str:
    if state.get("tool_name", "") in DETERMINISTIC_TOOLS:
        return "format_for_whatsapp"
    return "generate_response"


def build_whatsapp_agent_graph() -> StateGraph:
    graph = StateGraph(WhatsAppAgentState)
    graph.add_node("classify_intent", classify_intent)
    graph.add_node("execute_tool", execute_tool)
    graph.add_node("generate_response", generate_response)
    graph.add_node("format_for_whatsapp", format_for_whatsapp)
    graph.set_entry_point("classify_intent")
    graph.add_conditional_edges(
        "classify_intent",
        needs_tool,
        {
            "execute_tool": "execute_tool",
            "generate_response": "generate_response",
        },
    )
    graph.add_conditional_edges(
        "execute_tool",
        route_after_tool,
        {
            "format_for_whatsapp": "format_for_whatsapp",
            "generate_response": "generate_response",
        },
    )
    graph.add_edge("generate_response", "format_for_whatsapp")
    graph.add_edge("format_for_whatsapp", END)
    return graph


_whatsapp_graph = None


def _get_graph():
    global _whatsapp_graph
    if _whatsapp_graph is None:
        _whatsapp_graph = build_whatsapp_agent_graph().compile()
    return _whatsapp_graph


async def run_whatsapp_agent(
    message: str,
    user_id: str,
    tenant_id: str,
    role: str,
    notebook_id: str | None = None,
    conversation_history: list | None = None,
    session_id: str | None = None,
    pending_confirmation_id: str | None = None,
) -> dict:
    from database import AsyncSessionLocal
    from src.domains.platform.services.mascot_orchestrator import execute_pending_confirmation, handle_mascot_message
    from src.domains.platform.services.mascot_schemas import MascotMessageRequest

    normalized = (message or "").strip().lower()
    is_confirm = normalized in WHATSAPP_CONFIRM_TOKENS
    is_cancel = normalized in WHATSAPP_CANCEL_TOKENS

    async with AsyncSessionLocal() as session:
        if pending_confirmation_id and (is_confirm or is_cancel):
            result = await execute_pending_confirmation(
                confirmation_id=pending_confirmation_id,
                approved=is_confirm,
                channel="whatsapp",
                session_id=session_id,
                tenant_id=tenant_id,
                user_id=user_id,
                role=role,
                session=session,
            )
            confirmation_cleared = True
        else:
            result = await handle_mascot_message(
                MascotMessageRequest(
                    message=message,
                    channel="whatsapp",
                    role=role,
                    tenant_id=tenant_id,
                    user_id=user_id,
                    notebook_id=notebook_id,
                    session_id=session_id,
                    conversation_history=conversation_history or [],
                ),
                session,
            )
            confirmation_cleared = False
    response_text = result.reply_text
    if result.requires_confirmation and result.confirmation_id:
        response_text = (
            f"{response_text}\n\nReply *CONFIRM* to continue or *CANCEL* to stop."
        ).strip()
    return {
        "response": response_text,
        "response_type": "text",
        "intent": result.intent,
        "tool_name": (
            result.actions[-1].payload.get("tool")
            if result.actions and isinstance(result.actions[-1].payload, dict) and result.actions[-1].payload.get("tool")
            else (result.actions[-1].payload.get("mode") if result.actions and isinstance(result.actions[-1].payload, dict) else None)
        ) or (result.actions[-1].kind if result.actions else None),
        "requires_confirmation": result.requires_confirmation,
        "confirmation_id": result.confirmation_id,
        "confirmation_cleared": confirmation_cleared,
        "notebook_id": result.notebook_id,
    }
