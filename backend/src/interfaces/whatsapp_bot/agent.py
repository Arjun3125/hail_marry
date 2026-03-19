"""WhatsApp LangGraph Agent — intent classification → tool dispatch → response formatting.

A dedicated StateGraph that processes inbound WhatsApp messages:
1. classify_intent: LLM classifies the user's intent and selects the right ERP tool
2. execute_tool: Calls the selected tool with RBAC enforcement
3. format_response: Formats the tool output for WhatsApp delivery
"""
import json
import logging
from typing import TypedDict, Optional

try:
    from langgraph.graph import StateGraph, END
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

# Deterministic tools: produce tabular/structured data that does NOT need LLM summarization.
# These bypass the chat node entirely for zero-latency responses.
DETERMINISTIC_TOOLS = {
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
}


# ─── State Schema ─────────────────────────────────────────────

class WhatsAppAgentState(TypedDict):
    message: str                         # raw inbound message
    user_id: str                         # ERP user UUID
    tenant_id: str                       # tenant UUID
    role: str                            # student | teacher | parent | admin
    conversation_history: list           # last N messages for context
    intent: Optional[str]                # classified intent
    tool_name: Optional[str]             # selected ERP tool
    tool_args: Optional[dict]            # arguments for the tool
    tool_result: Optional[str]           # tool execution output
    response: Optional[str]              # formatted response text
    response_type: str                   # text | list | buttons


# ─── Intent Classification ────────────────────────────────────

INTENT_MAP = {
    # Student intents
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
    "study": "get_student_weak_topics",

    # Teacher intents (resolved after role check)
    "absent students": "get_teacher_absent_students",
    "who is absent": "get_teacher_absent_students",
    "generate quiz": "generate_quiz",

    # Parent intents
    "child performance": "get_child_performance",
    "performance": "get_child_performance",
    "child attendance": "get_child_attendance",
    "child homework": "get_child_homework",

    # Admin intents
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

# Role-aware overrides: same keyword yields different tools based on role
ROLE_INTENT_OVERRIDES = {
    "teacher": {
        "generate quiz": "generate_quiz",
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


def _classify_intent_heuristic(message: str, role: str) -> Optional[str]:
    """Fast heuristic intent classification using keyword matching.

    Falls back to None if no match (triggers LLM classification).
    """
    msg_lower = message.lower().strip()

    # Check role-specific overrides first
    overrides = ROLE_INTENT_OVERRIDES.get(role, {})
    for keyword, tool_name in overrides.items():
        if keyword in msg_lower:
            return tool_name

    # General keyword matching
    for keyword, tool_name in INTENT_MAP.items():
        if keyword in msg_lower:
            return tool_name

    return None


def _classify_intent_similarity(message: str, role: str) -> dict:
    """Use blazingly fast Jaccard similarity to map user queries to tool descriptions.

    Returns dict with 'tool_name' and 'is_general_chat'.
    """
    STOPWORDS = {"what", "is", "my", "the", "a", "an", "can", "you", "show", "me", "tell", "about", "did", "do", "i", "have", "any", "for", "of", "to", "please", "kindly", "are", "there"}

    TOOL_CORPUS = {
        "get_student_timetable": {"class", "classes", "schedule", "timetable", "period", "today", "subject", "teach"},
        "get_student_tests": {"test", "tests", "exam", "exams", "quiz", "quizzes", "assessment", "score"},
        "get_student_assignments": {"assignment", "assignments", "homework", "pending", "due", "task", "project"},
        "get_student_attendance": {"attendance", "absent", "present", "leave", "holiday", "attended"},
        "get_student_results": {"marks", "results", "score", "grade", "report", "passed", "failed"},
        "get_student_weak_topics": {"weak", "improve", "study", "guide", "bad", "failing", "attention"},
        "generate_study_guide": {"study", "guide", "summary", "notes", "chapter", "topic"},
        "generate_audio_overview": {"audio", "overview", "podcast", "listen", "summary", "topic"},
        "get_teacher_absent_students": {"absent", "students", "who", "missing", "attendance", "today"},
        "generate_quiz": {"generate", "quiz", "mcq", "assessment", "class", "topic"},
        "get_child_performance": {"child", "performance", "doing", "progress", "marks", "results"},
        "get_child_attendance": {"child", "attendance", "absent", "present", "school"},
        "get_child_homework": {"child", "homework", "assignment", "pending", "due"},
        "get_school_attendance_summary": {"attendance", "summary", "school", "total", "students", "present", "absent"},
        "get_fee_pending_report": {"fee", "fees", "pending", "outstanding", "money", "paid", "due", "report"},
        "get_ai_usage_stats": {"ai", "usage", "stats", "statistics", "queries", "bot"},
        "check_library_catalog": {"library", "books", "book", "author", "catalog", "read", "borrow"}
    }

    import re
    msg_tokens = set(re.findall(r'\b\w+\b', message.lower())) - STOPWORDS

    if not msg_tokens:
        return {"tool_name": None, "is_general_chat": True}

    best_tool = None
    best_score = 0.0

    from src.shared.ai_tools.whatsapp_tools import TOOL_ROLE_MAP

    for tool_name, corpus_tokens in TOOL_CORPUS.items():
        # Enforce RBAC at the routing level
        if role not in TOOL_ROLE_MAP.get(tool_name, set()):
            continue

        intersection = len(msg_tokens.intersection(corpus_tokens))
        union = len(msg_tokens.union(corpus_tokens))
        score = float(intersection) / union if union > 0 else 0.0

        if score > best_score:
            best_score = score
            best_tool = tool_name

    # Threshold for vector similarity match
    if best_score >= 0.15:
        return {"tool_name": best_tool, "is_general_chat": False}

    return {"tool_name": None, "is_general_chat": True}


# ─── Graph Nodes ──────────────────────────────────────────────

def classify_intent(state: WhatsAppAgentState) -> dict:
    """Node 1: Classify the user's intent and select a tool."""
    message = state["message"]
    role = state["role"]
    history = state.get("conversation_history", [])

    # Try fast heuristic first
    tool_name = _classify_intent_heuristic(message, role)

    if tool_name:
        return {
            "intent": tool_name,
            "tool_name": tool_name,
            "response_type": "text",
        }

    # Fall back to similarity classification
    llm_result = _classify_intent_similarity(message, role)

    if llm_result.get("tool_name"):
        return {
            "intent": llm_result["tool_name"],
            "tool_name": llm_result["tool_name"],
            "response_type": "text",
        }

    # General chat — generate a direct response
    return {
        "intent": "general_chat",
        "tool_name": None,
        "response_type": "text",
    }


def execute_tool(state: WhatsAppAgentState) -> dict:
    """Node 2: Execute the selected ERP tool with RBAC enforcement."""
    tool_name = state.get("tool_name")

    if not tool_name:
        return {"tool_result": None}

    from src.shared.ai_tools.whatsapp_tools import authorize_tool, ALL_WHATSAPP_TOOLS

    # RBAC check
    if not authorize_tool(tool_name, state["role"]):
        return {
            "tool_result": f"⚠️ Sorry, {tool_name.replace('_', ' ')} is not available for {state['role']} accounts.",
        }

    # Find the tool function
    tool_fn = None
    for t in ALL_WHATSAPP_TOOLS:
        if t.name == tool_name:
            tool_fn = t
            break

    if not tool_fn:
        return {"tool_result": "❌ Tool not found."}

    # Determine arguments based on tool and role
    try:
        if tool_name in {"generate_quiz", "generate_study_guide", "generate_audio_overview"}:
            topic = _extract_topic_from_message(state["message"])
            result = tool_fn.invoke({
                "user_id": state["user_id"],
                "tenant_id": state["tenant_id"],
                "topic": topic,
            })
            return {"tool_result": result}
        if state["role"] == "parent" and tool_name.startswith("get_child_"):
            # Parent tools use child_id instead of user_id
            # If no active_child_id, the gateway should have handled child selection
            result = tool_fn.invoke({
                "child_id": state["user_id"],  # Will be overridden by session's active_child_id
                "tenant_id": state["tenant_id"],
            })
        elif tool_name in ("get_school_attendance_summary", "get_fee_pending_report", "get_ai_usage_stats"):
            # Admin tools only need tenant_id
            result = tool_fn.invoke({"tenant_id": state["tenant_id"]})
        else:
            result = tool_fn.invoke({
                "user_id": state["user_id"],
                "tenant_id": state["tenant_id"],
            })
        return {"tool_result": result}
    except Exception as e:
        logger.exception("Tool execution failed: %s", tool_name)
        return {"tool_result": f"❌ Error executing request: {str(e)}"}


def _extract_topic_from_message(message: str) -> str:
    """Best-effort extraction of a user-requested quiz/study topic."""
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
        "generate study guide for",
        "create study guide for",
        "make study guide for",
        "generate study guide on",
        "create study guide on",
        "make study guide on",
        "study guide for",
        "study guide on",
        "generate audio overview for",
        "create audio overview for",
        "make audio overview for",
        "generate audio overview on",
        "create audio overview on",
        "make audio overview on",
        "audio overview for",
        "audio overview on",
        "audio summary for",
        "audio summary on",
        "podcast for",
        "podcast on",
    ]
    for prefix in prefixes:
        if lowered.startswith(prefix):
            return text[len(prefix):].strip(" :-")
    return text


def generate_response(state: WhatsAppAgentState) -> dict:
    """Node 3: Generate a response — either from tool result or via LLM for general chat."""
    # If we have a tool result, use it directly
    if state.get("tool_result"):
        return {"response": state["tool_result"]}

    # General chat — use configurable LLM provider to respond
    try:
        from src.infrastructure.llm.providers import get_llm_provider
        import asyncio
        llm = get_llm_provider()

        system_prompt = (
            f"You are VidyaOS, a school WhatsApp assistant. "
            f"The user is a {state['role']}. Be helpful, concise, and friendly. "
            f"Use emojis. Keep responses under 200 words. "
            f"If asked about something you need ERP data for, suggest they ask more specifically."
        )

        history_str = ""
        for msg in state.get("conversation_history", [])[-6:]:
            history_str += f"\n{msg.get('role', 'user')}: {msg.get('content', '')}"

        full_prompt = f"{system_prompt}\n\nConversation:{history_str}\n\nuser: {state['message']}\n\nassistant:"

        # Use asyncio to call the async generate method
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                result = pool.submit(asyncio.run, llm.generate(full_prompt, temperature=0.7)).result()
        else:
            result = asyncio.run(llm.generate(full_prompt, temperature=0.7))

        return {"response": result.get("response", "")}
    except Exception:
        logger.exception("LLM response generation failed")
        return {
            "response": (
                "🤖 I can help you check your timetable, attendance, assignments, "
                "test schedule, and more! Type *help* to see all options."
            ),
        }


def format_for_whatsapp(state: WhatsAppAgentState) -> dict:
    """Node 4: Ensure the response is properly formatted for WhatsApp delivery."""
    response = state.get("response", "")

    # Truncate to WhatsApp's 4096 character limit
    if len(response) > 4000:
        response = response[:3990] + "\n\n_...truncated_"

    return {"response": response, "response_type": "text"}


# ─── Conditional Edge ─────────────────────────────────────────

def needs_tool(state: WhatsAppAgentState) -> str:
    """Route: if a tool was selected, execute it; otherwise generate a direct response."""
    if state.get("tool_name"):
        return "execute_tool"
    return "generate_response"


def route_after_tool(state: WhatsAppAgentState) -> str:
    """Route after tool execution: deterministic tools skip LLM formatting completely."""
    tool_name = state.get("tool_name", "")
    if tool_name in DETERMINISTIC_TOOLS:
        # Pure data — skip the LLM chat node, go straight to WhatsApp formatting
        return "format_for_whatsapp"
    # Non-deterministic tools (e.g., quiz generation) may need LLM post-processing
    return "generate_response"


# ─── Build Graph ──────────────────────────────────────────────

def build_whatsapp_agent_graph() -> StateGraph:
    """Construct the WhatsApp agent StateGraph."""
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

    # After tool execution, deterministic tools skip the LLM entirely
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


# Compile once at module level
_whatsapp_graph = None


def _get_graph():
    global _whatsapp_graph
    if _whatsapp_graph is None:
        _whatsapp_graph = build_whatsapp_agent_graph().compile()
    return _whatsapp_graph


# ─── Public API ───────────────────────────────────────────────

async def run_whatsapp_agent(
    message: str,
    user_id: str,
    tenant_id: str,
    role: str,
    conversation_history: list | None = None,
) -> dict:
    """Run the WhatsApp agent graph for a single message.

    Returns:
        Dict with 'response', 'response_type', 'intent', 'tool_name'.
    """
    initial_state: WhatsAppAgentState = {
        "message": message,
        "user_id": user_id,
        "tenant_id": tenant_id,
        "role": role,
        "conversation_history": conversation_history or [],
        "intent": None,
        "tool_name": None,
        "tool_args": None,
        "tool_result": None,
        "response": None,
        "response_type": "text",
    }

    graph = _get_graph()
    result = graph.invoke(initial_state)

    return {
        "response": result.get("response", "❌ No response generated."),
        "response_type": result.get("response_type", "text"),
        "intent": result.get("intent"),
        "tool_name": result.get("tool_name"),
    }
