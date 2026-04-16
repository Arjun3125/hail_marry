"""Tool dispatch node for the Mascot LangGraph agent.

Performs a keyword intent check, looks up a matching tool from WHATSAPP_TOOL_REGISTRY
filtered by role, calls it, and injects the result into state for the generate_response
node to use.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# ERP data-read tools only — action/write tools are out of scope (Sub-project 3)
_ERP_READ_TOOLS = frozenset({
    "get_student_attendance",
    "get_student_assignments",
    "get_student_results",
    "get_student_timetable",
    "get_student_tests",
    "get_student_weak_topics",
    "get_teacher_schedule",
    "get_teacher_absent_students",
    "get_child_attendance",
    "get_child_performance",
    "get_child_homework",
    "get_school_attendance_summary",
    "get_fee_pending_report",
    "get_ai_usage_stats",
})

# Keyword hints per tool to avoid a full LLM call for obvious matches
_KEYWORD_HINTS: dict[str, list[str]] = {
    "get_student_attendance": ["attendance", "hazir", "present", "absent", "aaya"],
    "get_student_assignments": ["homework", "assignment", "kaam", "submit", "due"],
    "get_student_results": ["result", "marks", "score", "nambr", "number", "exam"],
    "get_student_timetable": ["timetable", "schedule", "time table", "class time", "period"],
    "get_student_tests": ["test", "quiz", "upcoming"],
    "get_student_weak_topics": ["weak", "struggle", "difficult", "topic", "concept"],
    "get_teacher_absent_students": ["absent", "attendance", "kaun aaya", "who came", "who absent"],
    "get_teacher_schedule": ["schedule", "timetable", "class", "period", "aaj"],
    "get_child_attendance": ["attendance", "gaya", "school", "present", "absent"],
    "get_child_performance": ["marks", "result", "performance", "score", "exam"],
    "get_child_homework": ["homework", "assignment", "kaam", "due"],
    "get_school_attendance_summary": ["attendance", "summary", "school", "present", "absent", "aaj"],
    "get_fee_pending_report": ["fee", "fees", "pending", "payment", "defaulter"],
    "get_ai_usage_stats": ["ai", "usage", "stats", "queue", "analytics"],
}


def _find_tool(tool_name: str, role: str):
    """Return WhatsAppToolSpec if the tool exists and is allowed for role, else None."""
    try:
        from src.shared.ai_tools.whatsapp_tools import WHATSAPP_TOOL_REGISTRY
        spec = WHATSAPP_TOOL_REGISTRY.get(tool_name)
        if spec and role in spec.roles and tool_name in _ERP_READ_TOOLS:
            return spec
        return None
    except Exception as e:
        logger.warning("tool_dispatcher: failed to look up tool %s: %s", tool_name, e)
        return None


def _keyword_match(message: str, role: str) -> Optional[str]:
    """
    Fast keyword check — returns a tool_name if message clearly matches, else None.
    Only matches tools allowed for the given role.
    """
    lower = message.lower()
    for tool_name, keywords in _KEYWORD_HINTS.items():
        spec = _find_tool(tool_name, role)
        if spec and any(kw in lower for kw in keywords):
            return tool_name
    return None


def _build_call_params(spec, state: Dict[str, Any]) -> dict:
    """Build kwargs dict for a tool handler based on its required_params."""
    params = {}
    mascot_ctx = state.get("mascot_context") or {}
    for param in spec.required_params:
        if param == "user_id":
            params["user_id"] = state.get("student_id", "")
        elif param == "tenant_id":
            params["tenant_id"] = state.get("tenant_id", "")
        elif param == "child_id":
            # ParentContext stores child_id in mascot_context dict
            params["child_id"] = mascot_ctx.get("child_id", "")
        # topic/query params are not auto-filled — skip
    return params


async def tool_dispatch_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node: check if the message needs an ERP data fetch, call the tool,
    inject result into state["tool_result"].

    Returns {"tool_result": str | None}.
    """
    role = state.get("role", "student")
    message = state.get("student_message", "")

    tool_name = _keyword_match(message, role)
    if not tool_name:
        return {"tool_result": None}

    spec = _find_tool(tool_name, role)
    if not spec:
        return {"tool_result": None}

    try:
        params = _build_call_params(spec, state)
        import asyncio
        result = await asyncio.get_event_loop().run_in_executor(
            None, lambda: spec.handler(**params)
        )
        return {"tool_result": f"TOOL_RESULT ({spec.name}):\n{result}"}
    except Exception as e:
        logger.warning("tool_dispatch_node: tool %s failed: %s", tool_name, e)
        return {"tool_result": None}
