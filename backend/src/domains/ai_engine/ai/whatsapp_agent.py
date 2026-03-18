"""WhatsApp LangGraph Agent — intent classification → tool dispatch → response formatting.

A dedicated StateGraph that processes inbound WhatsApp messages:
1. classify_intent: LLM classifies the user's intent and selects the right ERP tool
2. execute_tool: Calls the selected tool with RBAC enforcement
3. format_response: Formats the tool output for WhatsApp delivery
"""
import json
import logging
from typing import TypedDict, Optional

from langgraph.graph import StateGraph, END

logger = logging.getLogger(__name__)


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
    "study": "get_student_weak_topics",

    # Teacher intents (resolved after role check)
    "absent students": "get_teacher_absent_students",
    "who is absent": "get_teacher_absent_students",

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


def _classify_intent_llm(message: str, role: str, history: list) -> dict:
    """Use LLM to classify intent when heuristics fail.

    Returns dict with 'tool_name' and 'is_general_chat'.
    """
    try:
        from langchain_ollama import ChatOllama

        llm = ChatOllama(model="llama3.2", temperature=0, format="json")

        from src.domains.ai_engine.ai.whatsapp_tools import TOOL_ROLE_MAP
        available_tools = [t for t, roles in TOOL_ROLE_MAP.items() if role in roles]

        system_prompt = (
            f"You are a WhatsApp assistant for a school ERP. The user's role is: {role}.\n"
            f"Classify the user's message into one of these tool names: {available_tools}\n"
            f"If the message is general chat or a question you can answer directly, set tool_name to null.\n"
            f"Respond ONLY as JSON: {{\"tool_name\": \"...\", \"is_general_chat\": true/false}}"
        )

        response = llm.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ])

        result = json.loads(response.content)
        return result
    except Exception:
        logger.exception("LLM intent classification failed")
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

    # Fall back to LLM classification
    llm_result = _classify_intent_llm(message, role, history)

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

    from src.domains.ai_engine.ai.whatsapp_tools import authorize_tool, ALL_WHATSAPP_TOOLS

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


def generate_response(state: WhatsAppAgentState) -> dict:
    """Node 3: Generate a response — either from tool result or via LLM for general chat."""
    # If we have a tool result, use it directly
    if state.get("tool_result"):
        return {"response": state["tool_result"]}

    # General chat — use LLM to respond
    try:
        from langchain_ollama import ChatOllama
        llm = ChatOllama(model="llama3.2", temperature=0.7)

        system_prompt = (
            f"You are VidyaOS, a school WhatsApp assistant. "
            f"The user is a {state['role']}. Be helpful, concise, and friendly. "
            f"Use emojis. Keep responses under 200 words. "
            f"If asked about something you need ERP data for, suggest they ask more specifically."
        )

        messages = [{"role": "system", "content": system_prompt}]
        for msg in state.get("conversation_history", [])[-6:]:
            messages.append(msg)
        messages.append({"role": "user", "content": state["message"]})

        response = llm.invoke(messages)
        return {"response": response.content}
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

    graph.add_edge("execute_tool", "format_for_whatsapp")
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
