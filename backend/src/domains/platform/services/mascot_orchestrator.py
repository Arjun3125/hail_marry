"""Shared mascot orchestration for web and WhatsApp conversational control."""
from __future__ import annotations

import logging
import re
import csv
import io
import time
from collections import Counter
from datetime import date, datetime
from pathlib import Path
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse
from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from constants import STUDENT_ALLOWED_EXTENSIONS, STUDENT_MAX_FILE_SIZE, TEACHER_ALLOWED_EXTENSIONS, TEACHER_MAX_FILE_SIZE
from src.domains.academic.models.attendance import Attendance
from src.domains.academic.models.core import Class, Enrollment, Subject
from src.domains.academic.models.marks import Exam, Mark
from src.domains.academic.models.parent_link import ParentLink
from src.domains.academic.models.timetable import Timetable
from src.domains.identity.models.user import User
from src.domains.identity.models.tenant import Tenant
from src.domains.platform.models.document import Document
from src.domains.platform.models.generated_content import GeneratedContent
from src.domains.platform.models.notebook import Notebook
from src.domains.platform.models.ai import AIQuery
from src.domains.platform.models.audit import AuditLog
from src.domains.platform.schemas.ai_runtime import InternalAIQueryRequest, InternalIngestURLRequest, InternalStudyToolGenerateRequest
from src.domains.platform.services.ai_gateway import run_study_tool, run_text_query, run_url_ingestion
from src.domains.platform.services.mascot_registry import capability_requires_confirmation, get_capability, is_capability_allowed, resolve_navigation_target
from src.domains.platform.services.mascot_schemas import MascotAction, MascotMessageRequest, MascotMessageResponse, PendingMascotAction
from src.domains.platform.services.mascot_session_store import build_session_id, clear_session, delete_pending_action, load_pending_action, load_session, mutation_seen_recently, remember_mutation, save_session, store_pending_action
from src.domains.platform.services.metrics_registry import observe_stage_latency
from src.domains.platform.services.trace_backend import record_trace_event
from src.shared.ocr_imports import extract_upload_content_result, get_extension, parse_account_rows_with_diagnostics, parse_attendance_rows_with_diagnostics, parse_marks_rows_with_diagnostics, parse_student_import_rows_with_diagnostics
from src.infrastructure.llm.providers import get_llm_provider
from utils.upload_security import UploadValidationError, ensure_storage_dir, sanitize_docx_bytes

logger = logging.getLogger(__name__)

_TOOLS = {
    "quiz": ("quiz", "mcq", "prashnottari"),
    "flashcards": ("flashcard", "flashcards"),
    "mindmap": ("mind map", "mindmap"),
    "flowchart": ("flowchart", "flow chart"),
    "concept_map": ("concept map", "concept-map"),
}
_QUERY_MODES = {
    "study_guide": ("study guide", "study notes"),
    "socratic": ("socratic", "guide me", "dont tell the answer", "don't tell the answer"),
    "debate": ("debate", "counterargument", "counter argument"),
    "essay_review": ("essay review", "review essay", "check essay"),
}
_NAVIGATION = {
    "ai_studio": ("ai studio", "assistant", "study assistant"),
    "upload": ("upload", "add document", "add pdf"),
    "attendance": ("attendance",),
    "marks": ("marks", "results", "gradebook"),
    "onboarding": ("setup wizard", "onboarding", "setup school"),
    "dashboard": ("dashboard", "release gate", "whatsapp release gate"),
}
_ROLE_REPORTS = {
    "teacher_insights_report": ("class insights", "weak topics", "class performance insights"),
    "teacher_doubt_heatmap_report": ("doubt heatmap", "student doubt hotspots", "where are students struggling", "doubt hotspots"),
    "parent_progress_report": ("child progress", "my child report", "progress report", "child summary", "report for my child"),
    "admin_release_gate_report": ("release gate summary", "release gate status", "whatsapp health", "whatsapp release gate summary"),
    "admin_onboarding_report": ("setup progress", "setup status", "onboarding progress", "wizard progress", "school setup progress"),
    "admin_ai_review_report": ("ai review summary", "review queue", "pending ai review", "ai review status"),
}
_TEACHER_ASSESSMENT_MARKERS = ("generate assessment", "create assessment", "create test", "generate test", "question paper", "worksheet")
_STRUCTURED_IMPORT_MARKERS = {
    "teacher_roster_import": ("student roster", "student list", "onboard students", "import students", "roster"),
    "teacher_attendance_import": ("attendance", "attendance sheet", "mark attendance"),
    "teacher_marks_import": ("marks", "mark sheet", "grade sheet", "results import", "import marks"),
    "admin_teacher_import": ("import teachers", "onboard teachers", "teacher list", "teacher roster"),
    "admin_student_import": ("import students", "onboard students", "student list", "student roster"),
}
_MASCOT_UPLOAD_DIR = ensure_storage_dir("uploads", "mascot")
_MASCOT_OCR_DIR = ensure_storage_dir("uploads", "mascot_ocr")


@dataclass
class _ResolvedIntent:
    intent: str
    translated_message: str
    normalized_message: str
    actions: list[dict[str, Any]]


class _MascotInterpretation(BaseModel):
    normalized_message: str = ""
    translated_message: str = ""
    intent: str | None = None
    topic: str | None = None
    notebook_name: str | None = None
    navigation_target: str | None = None
    tool: str | None = None


def _review_status_from_action(action: str | None) -> str:
    if not action:
        return "pending"
    if action.endswith("approved"):
        return "approved"
    if action.endswith("flagged"):
        return "flagged"
    return "pending"


def _safe_uuid(value: str | None) -> UUID | None:
    try:
        return UUID(str(value)) if value else None
    except Exception:
        return None


def _clean(text: str) -> str:
    return " ".join((text or "").strip().split())


def _ui_metadata(request: MascotMessageRequest) -> dict[str, Any]:
    return dict(request.ui_context.metadata) if request.ui_context and request.ui_context.metadata else {}


def _extract_urls(text: str) -> list[str]:
    return re.findall(r"https?://[^\s]+", text or "")


def _strip_urls(text: str) -> str:
    return re.sub(r"https?://[^\s]+", "", text or "").strip()


def _heuristic_translate(message: str) -> str:
    text = _clean(message)
    lowered = text.lower()
    replacements = (
        (" samjhao ", " explain "),
        (" samjha ", " explain "),
        (" batao ", " explain "),
        (" bana ", " create "),
        (" kar ", " "),
        (" pahije ", " need "),
        (" chahiye ", " need "),
        (" var ", " on "),
        (" ka ", " "),
        (" ka ", " "),
    )
    normalized = f" {lowered} "
    for source, target in replacements:
        normalized = normalized.replace(source, target)
    normalized = normalized.replace("mala ", "").replace("please", " ").strip()
    return _clean(normalized) or text


def _needs_llm(message: str) -> bool:
    text = f" {_clean(message).lower()} "
    if not text.strip():
        return False
    if any(ord(ch) > 127 for ch in text):
        return True
    return any(marker in text for marker in (" kar ", " bana ", " samjhao ", " batao ", " kaise ", " mala ", " pahije ", " chahiye ", " var "))


def _topic_from_message(message: str) -> str:
    text = _strip_urls(_clean(message))
    lowered = text.lower()
    prefixes = [
        "generate quiz for", "create quiz for", "make quiz for", "quiz for", "quiz bana",
        "generate flashcards for", "create flashcards for", "make flashcards for", "flashcards for", "mala flashcards pahije",
        "generate mind map for", "create mind map for", "mind map on", "mind map for", "mind map bana",
        "generate flowchart for", "create flowchart for", "flowchart for", "flowchart bana",
        "generate concept map for", "concept map for", "concept map bana",
        "study guide for", "study guide on", "explain", "summarize", "summary of", "tell me about", "what is", "why is", "how does",
        "help me debate", "review essay", "check essay", "essay review",
    ]
    for prefix in prefixes:
        if lowered.startswith(prefix):
            return text[len(prefix):].strip(" :-?") or text
    return text


def _notebook_name(message: str) -> str | None:
    text = _clean(message)
    patterns = (
        r"(?:create|make|new)\s+(?:a\s+)?notebook(?:\s+for|\s+called|\s+named)?\s+(?P<name>.+)$",
        r"(?:open|select|use|switch to)\s+(?P<name>.+?)\s+notebook$",
        r"(?:rename)\s+(?:the\s+)?notebook(?:\s+to)?\s+(?P<name>.+)$",
        r"(?:archive|delete)\s+(?P<name>.+?)\s+notebook$",
    )
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            name = match.group("name").strip(" .")
            if name:
                return name
    return None


def _detect_navigation(message: str, role: str) -> str | None:
    lowered = _clean(message).lower()
    for target, markers in _NAVIGATION.items():
        if any(marker in lowered for marker in markers) and resolve_navigation_target(role, target):
            return target
    return None


def _detect_navigation_targets(message: str, role: str) -> list[str]:
    lowered = _clean(message).lower()
    targets = []
    for target, markers in _NAVIGATION.items():
        if any(marker in lowered for marker in markers) and resolve_navigation_target(role, target):
            targets.append(target)
    return targets


def _detect_tools(message: str) -> list[str]:
    lowered = _clean(message).lower()
    return [tool for tool, markers in _TOOLS.items() if any(marker in lowered for marker in markers)]


def _detect_query_mode(message: str) -> str:
    lowered = _clean(message).lower()
    for mode, markers in _QUERY_MODES.items():
        if any(marker in lowered for marker in markers):
            return mode
    return "qa"


def _detect_role_report(message: str, role: str | None) -> str | None:
    lowered = _clean(message).lower()
    normalized_role = (role or "").strip().lower()
    if normalized_role in {"teacher", "admin"} and any(marker in lowered for marker in _ROLE_REPORTS["teacher_doubt_heatmap_report"]):
        return "teacher_doubt_heatmap_report"
    if normalized_role in {"teacher", "admin"} and any(marker in lowered for marker in _ROLE_REPORTS["teacher_insights_report"]):
        return "teacher_insights_report"
    if normalized_role == "parent" and any(marker in lowered for marker in _ROLE_REPORTS["parent_progress_report"]):
        return "parent_progress_report"
    if normalized_role == "admin" and any(marker in lowered for marker in _ROLE_REPORTS["admin_release_gate_report"]):
        return "admin_release_gate_report"
    if normalized_role == "admin" and any(marker in lowered for marker in _ROLE_REPORTS["admin_onboarding_report"]):
        return "admin_onboarding_report"
    if normalized_role == "admin" and any(marker in lowered for marker in _ROLE_REPORTS["admin_ai_review_report"]):
        return "admin_ai_review_report"
    return None


def _detect_teacher_assessment(message: str, role: str | None) -> bool:
    normalized_role = (role or "").strip().lower()
    lowered = _clean(message).lower()
    return normalized_role in {"teacher", "admin"} and any(marker in lowered for marker in _TEACHER_ASSESSMENT_MARKERS)


def _extract_question_count(message: str) -> int | None:
    match = re.search(r"\b(\d{1,2})\s+(?:question|questions|mcq|mcqs)\b", _clean(message).lower())
    if not match:
        return None
    try:
        return max(1, min(int(match.group(1)), 15))
    except ValueError:
        return None


def _structured_import_intent(request: MascotMessageRequest, filename: str) -> str | None:
    normalized_role = (request.role or "").strip().lower()
    if normalized_role not in {"teacher", "admin"}:
        return None
    ext = get_extension(filename)
    if ext not in {"csv", "txt", "jpg", "jpeg", "png"}:
        return None
    route = (request.ui_context.current_route if request.ui_context else "") or ""
    route = route.lower()
    metadata = _ui_metadata(request)
    if normalized_role == "teacher":
        if "teacher/classes" in route:
            return "teacher_roster_import"
        if "teacher/attendance" in route:
            return "teacher_attendance_import"
        if "teacher/marks" in route or "teacher/results" in route:
            return "teacher_marks_import"
    if normalized_role == "admin" and "admin/setup-wizard" in route:
        step = str(metadata.get("setup_step") or "").strip().lower()
        if step == "teachers":
            return "admin_teacher_import"
        if step == "students":
            return "admin_student_import"
    lowered = _clean(request.message).lower()
    for intent, markers in _STRUCTURED_IMPORT_MARKERS.items():
        if normalized_role == "teacher" and intent.startswith("teacher_") and any(marker in lowered for marker in markers):
            return intent
        if normalized_role == "admin" and intent.startswith("admin_") and any(marker in lowered for marker in markers):
            return intent
    return None


def _summarize_rows(rows: list[Any], limit: int = 3) -> list[Any]:
    return rows[:limit]


def _parse_date_hint(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    except ValueError:
        return None


def _parse_int_hint(value: Any) -> int | None:
    try:
        if value is None or str(value).strip() == "":
            return None
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return None


def _follow_ups(intent: str, notebook_name: str | None = None) -> list[str]:
    if intent == "notebook_create":
        label = notebook_name or "this notebook"
        return [f"Generate flashcards from {label}", f"Create a flowchart for {label}", f"Open {label} in AI Studio"]
    if intent == "teacher_insights_report":
        return ["Show doubt heatmap", "Open attendance page", "Create quiz for Chapter 10"]
    if intent == "teacher_doubt_heatmap_report":
        return ["Show class insights", "Open marks page", "Create quiz for weak topics"]
    if intent == "teacher_assessment_generate":
        return ["Show class insights", "Open marks page", "Generate quiz for Chapter 10"]
    if intent == "teacher_roster_import":
        return ["Open classes page", "Import attendance from image", "Generate a Biology assessment"]
    if intent == "teacher_attendance_import":
        return ["Open attendance page", "Show class insights", "Import marks from image"]
    if intent == "teacher_marks_import":
        return ["Open marks page", "Show class insights", "Generate assessment for this class"]
    if intent == "parent_progress_report":
        return ["Open reports", "Show attendance", "Summarize my child's weak topics"]
    if intent == "admin_release_gate_report":
        return ["Open dashboard", "Open setup wizard", "Review WhatsApp release gate"]
    if intent == "admin_onboarding_report":
        return ["Open setup wizard", "Import teachers", "Import students"]
    if intent == "admin_ai_review_report":
        return ["Open AI review", "Open dashboard", "Review WhatsApp release gate"]
    if intent in {"query", "study_tool"}:
        return ["Generate flashcards", "Create a flowchart", "Open AI Studio"]
    return ["Create a notebook", "Ask a question", "Generate a quiz"]


def _web_nav(role: str, target: str, notebook_id: str | None = None) -> dict[str, Any] | None:
    href = resolve_navigation_target(role, target)
    if not href:
        return None
    payload: dict[str, Any] = {"target": target, "href": href}
    if notebook_id and target in {"assistant", "ai_studio"}:
        payload["notebook_id"] = notebook_id
    return payload


def _whatsapp_nav(reply: str, navigation: dict[str, Any] | None) -> str:
    if not navigation:
        return reply
    href = navigation.get("href")
    target = str(navigation.get("target", "that page")).replace("_", " ")
    return f"{reply}\n\nOpen {target} in the app: {href}" if href else reply


def _compact_whatsapp_line(value: Any, *, fallback: str = "") -> str:
    if isinstance(value, str):
        return _clean(value)
    if isinstance(value, dict):
        for key in ("question", "q", "front", "back", "title", "label", "name", "text", "summary", "content"):
            item = value.get(key)
            if isinstance(item, str) and item.strip():
                return _clean(item)
    return fallback


def _collect_mindmap_lines(node: Any, *, depth: int = 0, limit: int = 6) -> list[str]:
    if not isinstance(node, dict) or limit <= 0:
        return []
    label = _clean(str(node.get("label") or node.get("title") or node.get("name") or "").strip())
    lines: list[str] = []
    if label:
        prefix = "  " * min(depth, 2)
        lines.append(f"{prefix}- {label}")
        limit -= 1
    for child in node.get("children", []) or []:
        if limit <= 0:
            break
        child_lines = _collect_mindmap_lines(child, depth=depth + 1, limit=limit)
        lines.extend(child_lines)
        limit -= len(child_lines)
    return lines


def _format_flowchart_steps(data: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    steps = data.get("steps")
    if isinstance(steps, list):
        for index, step in enumerate(steps[:5], start=1):
            if isinstance(step, dict):
                label = _clean(str(step.get("label") or step.get("title") or f"Step {index}"))
                detail = _clean(str(step.get("detail") or step.get("description") or ""))
                lines.append(f"{index}. {label}" + (f": {detail}" if detail else ""))
            else:
                lines.append(f"{index}. {_compact_whatsapp_line(step, fallback=str(step))}")
    return lines


def _format_concept_relationships(data: dict[str, Any]) -> list[str]:
    nodes = data.get("nodes")
    edges = data.get("edges")
    if not isinstance(nodes, list) or not isinstance(edges, list):
        return []
    label_by_id = {
        str(node.get("id")): _clean(str(node.get("label") or node.get("name") or "").strip())
        for node in nodes
        if isinstance(node, dict) and node.get("id")
    }
    lines: list[str] = []
    for edge in edges[:5]:
        if not isinstance(edge, dict):
            continue
        from_label = label_by_id.get(str(edge.get("from") or edge.get("source") or ""), "")
        to_label = label_by_id.get(str(edge.get("to") or edge.get("target") or ""), "")
        relation = _clean(str(edge.get("label") or edge.get("relation") or "relates to").strip())
        if from_label and to_label:
            lines.append(f"- {from_label} -> {relation} -> {to_label}")
    return lines


def _format_whatsapp_study_artifact(artifact: dict[str, Any]) -> str | None:
    tool = str(artifact.get("tool") or "").strip().lower()
    data = artifact.get("data")
    if tool == "quiz" and isinstance(data, list):
        lines = ["Quiz preview:"]
        for index, item in enumerate(data[:3], start=1):
            question = _compact_whatsapp_line(item, fallback=f"Question {index}")
            lines.append(f"{index}. {question}")
            options = item.get("options") if isinstance(item, dict) else None
            if isinstance(options, list):
                for option_index, option in enumerate(options[:4], start=1):
                    marker = chr(64 + option_index)
                    lines.append(f"   {marker}. {_compact_whatsapp_line(option, fallback=str(option))}")
        return "\n".join(lines)
    if tool == "flashcards" and isinstance(data, list):
        lines = ["Flashcards preview:"]
        for index, item in enumerate(data[:5], start=1):
            if isinstance(item, dict):
                front = _clean(str(item.get("front") or item.get("term") or f"Card {index}"))
                back = _clean(str(item.get("back") or item.get("definition") or item.get("answer") or ""))
                lines.append(f"{index}. {front}: {back}".rstrip(": "))
            else:
                lines.append(f"{index}. {_compact_whatsapp_line(item, fallback=str(item))}")
        return "\n".join(lines)
    if tool in {"mindmap", "flowchart", "concept_map"}:
        label = {
            "mindmap": "Mind map",
            "flowchart": "Flowchart",
            "concept_map": "Concept map",
        }[tool]
        lines: list[str] = []
        if tool == "mindmap":
            if isinstance(data, dict):
                lines = _collect_mindmap_lines(data, limit=6)
            elif isinstance(data, list):
                lines = [f"- {_compact_whatsapp_line(item, fallback=str(item))}" for item in data[:6]]
        elif tool == "flowchart" and isinstance(data, dict):
            lines = _format_flowchart_steps(data)
        elif tool == "concept_map" and isinstance(data, dict):
            lines = _format_concept_relationships(data)
            if not lines:
                candidate_nodes = data.get("nodes")
                if isinstance(candidate_nodes, list):
                    lines = [f"- {_compact_whatsapp_line(item, fallback=str(item))}" for item in candidate_nodes[:5]]
        if not lines and isinstance(data, dict):
            candidate_lists = [
                data.get("nodes"),
                data.get("steps"),
                data.get("items"),
                data.get("concepts"),
                data.get("branches"),
            ]
            for candidate in candidate_lists:
                if isinstance(candidate, list) and candidate:
                    lines = [f"- {_compact_whatsapp_line(item, fallback=str(item))}" for item in candidate[:6]]
                    break
            if not lines:
                summary = _compact_whatsapp_line(data)
                if summary:
                    lines = [f"- {summary}"]
        if lines:
            return "\n".join([f"{label} preview:"] + [line for line in lines if line])
    return None


def _format_whatsapp_reply(reply: str, *, intent: str, artifacts: list[dict[str, Any]], navigation: dict[str, Any] | None) -> str:
    formatted = reply
    if intent == "study_tool":
        for artifact in artifacts:
            if isinstance(artifact, dict):
                preview = _format_whatsapp_study_artifact(artifact)
                if preview:
                    formatted = preview
                    break
    return _whatsapp_nav(formatted, navigation)


def _store_session(request: MascotMessageRequest, *, notebook_id: str | None, intent: str, navigation: dict[str, Any] | None) -> None:
    session_id = build_session_id(channel=request.channel, user_id=request.user_id or "anonymous", provided=request.session_id)
    existing = load_session(session_id)
    existing.update({
        "active_notebook_id": notebook_id,
        "last_intent": intent,
        "last_suggestions": _follow_ups(intent),
        "last_navigation": navigation,
    })
    save_session(session_id, existing)


def _explicit_notebook_target(request: MascotMessageRequest) -> str | None:
    direct = str(request.notebook_id or "").strip()
    if direct:
        return direct
    if request.ui_context and request.ui_context.selected_notebook_id:
        selected = str(request.ui_context.selected_notebook_id).strip()
        if selected:
            return selected
    return None


def _mutation_signature(request: MascotMessageRequest, action: dict[str, Any], active_notebook: Notebook | None) -> str | None:
    intent = str(action.get("intent") or "")
    if intent not in {"notebook_create", "notebook_update", "teacher_roster_import", "teacher_attendance_import", "teacher_marks_import", "admin_teacher_import", "admin_student_import"}:
        return None
    parts = [request.channel, request.user_id or "", intent]
    if intent == "notebook_create":
        parts.append(str(action.get("name") or "").strip().lower())
    elif intent == "notebook_update":
        parts.extend([
            str(action.get("operation") or "").strip().lower(),
            str(action.get("notebook_name") or getattr(active_notebook, "id", "") or "").strip().lower(),
            str(action.get("name") or "").strip().lower(),
        ])
    else:
        parts.extend([
            str(action.get("class_id") or ""),
            str(action.get("subject_id") or ""),
            str(action.get("exam_name") or ""),
            str(action.get("date") or ""),
            str(len(action.get("rows", []) or [])),
        ])
    return "|".join(parts)


def _stage_elapsed_ms(started_at: float) -> float:
    return max((time.perf_counter() - started_at) * 1000.0, 0.0)


def _record_mascot_stage(*, trace_id: str | None, tenant_id: str | None, stage: str, operation: str, started_at: float, outcome: str, user_id: str | None = None, metadata: dict[str, Any] | None = None) -> None:
    duration_ms = _stage_elapsed_ms(started_at)
    observe_stage_latency(stage, operation, duration_ms, outcome)
    record_trace_event(
        trace_id=trace_id,
        tenant_id=tenant_id,
        user_id=user_id,
        source="mascot",
        stage=f"{stage}.{operation}",
        status=outcome,
        metadata={"duration_ms": round(duration_ms, 2), **(metadata or {})},
    )


async def _append_mascot_audit_log(
    session: AsyncSession,
    *,
    request: MascotMessageRequest,
    trace_id: str,
    action: str,
    status: str,
    entity_type: str = "mascot_session",
    entity_id: UUID | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    tenant_uuid = _safe_uuid(request.tenant_id)
    if tenant_uuid is None:
        return
    session.add(
        AuditLog(
            tenant_id=tenant_uuid,
            user_id=_safe_uuid(request.user_id),
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            metadata_={
                "trace_id": trace_id,
                "channel": request.channel,
                "role": request.role,
                "status": status,
                **(metadata or {}),
            },
        )
    )


async def _llm_interpret(message: str, role: str) -> _MascotInterpretation | None:
    prompt = (
        "You are a multilingual request interpreter for an educational AI mascot.\n"
        "The user may write in English, Hindi, Marathi, or mixed Hinglish/Marathi-English.\n"
        "Return structured data only.\n"
        "Decide the primary intent among: notebook_create, notebook_update, navigate, content_ingest, query, study_tool.\n"
        "Include translated_message in clear English.\n"
        f"Role: {role}\nUser message: {message}"
    )
    try:
        payload = await get_llm_provider().generate_structured(prompt, _MascotInterpretation)
        response = payload.get("response", payload)
        if isinstance(response, _MascotInterpretation):
            return response
        if isinstance(response, dict):
            return _MascotInterpretation(**response)
    except Exception:
        logger.exception("Mascot LLM interpretation failed")
    return None


async def _find_notebook_candidates(session: AsyncSession, request: MascotMessageRequest, notebook_name: str | None) -> list[Notebook]:
    if not notebook_name or not request.user_id or not request.tenant_id:
        return []
    lowered = notebook_name.strip().lower()
    result = await session.execute(
        select(Notebook).where(
            Notebook.user_id == _safe_uuid(request.user_id),
            Notebook.tenant_id == _safe_uuid(request.tenant_id),
            Notebook.is_active.is_(True),
        )
    )
    notebooks = result.scalars().all()
    exact = [item for item in notebooks if item.name.strip().lower() == lowered]
    if exact:
        return exact[:1]
    partial = [
        item for item in notebooks
        if lowered in item.name.strip().lower() or (item.subject and lowered in item.subject.strip().lower())
    ]
    unique: list[Notebook] = []
    seen: set[UUID] = set()
    for item in partial:
        if item.id not in seen:
            unique.append(item)
            seen.add(item.id)
    return unique


async def _notebook_by_id(session: AsyncSession, request: MascotMessageRequest, notebook_id: str | None) -> Notebook | None:
    notebook_uuid = _safe_uuid(notebook_id)
    if notebook_uuid is None or not request.user_id or not request.tenant_id:
        return None
    result = await session.execute(select(Notebook).where(
        Notebook.id == notebook_uuid,
        Notebook.user_id == _safe_uuid(request.user_id),
        Notebook.tenant_id == _safe_uuid(request.tenant_id),
        Notebook.is_active.is_(True),
    ))
    return result.scalar_one_or_none()


async def _notebook_by_name(session: AsyncSession, request: MascotMessageRequest, notebook_name: str | None) -> Notebook | None:
    candidates = await _find_notebook_candidates(session, request, notebook_name)
    return candidates[0] if len(candidates) == 1 else None


async def _resolve_notebook(session: AsyncSession, request: MascotMessageRequest, hint: str | None) -> Notebook | None:
    if hint:
        notebook = await _notebook_by_name(session, request, hint)
        if notebook:
            return notebook
    for candidate in (request.notebook_id, request.ui_context.selected_notebook_id if request.ui_context else None):
        notebook = await _notebook_by_id(session, request, candidate)
        if notebook:
            return notebook
    session_id = build_session_id(channel=request.channel, user_id=request.user_id or "", provided=request.session_id)
    stored = load_session(session_id)
    return await _notebook_by_id(session, request, stored.get("active_notebook_id"))


async def _create_notebook(session: AsyncSession, request: MascotMessageRequest, name: str) -> Notebook:
    notebook = Notebook(tenant_id=_safe_uuid(request.tenant_id), user_id=_safe_uuid(request.user_id), name=name[:150], subject=name[:100])
    session.add(notebook)
    await session.commit()
    await session.refresh(notebook)
    return notebook


async def _save_generated(session: AsyncSession, request: MascotMessageRequest, notebook: Notebook | None, tool: str, topic: str, result: dict[str, Any]) -> GeneratedContent | None:
    if notebook is None or not request.user_id or not request.tenant_id:
        return None
    generated = GeneratedContent(
        tenant_id=_safe_uuid(request.tenant_id),
        notebook_id=notebook.id,
        user_id=_safe_uuid(request.user_id),
        type=tool,
        title=f"{tool.replace('_', ' ').title()} - {topic[:60]}",
        content={"topic": topic, "data": result.get("data"), "citations": result.get("citations", [])},
        source_query=topic,
    )
    session.add(generated)
    await session.commit()
    await session.refresh(generated)
    return generated


async def _interpret(request: MascotMessageRequest) -> _ResolvedIntent:
    message = _clean(request.message)
    translated = message
    if _needs_llm(message):
        llm = await _llm_interpret(message, request.role or "student")
        if llm and llm.translated_message:
            translated = llm.translated_message.strip()
        else:
            translated = _heuristic_translate(message)

    actions: list[dict[str, Any]] = []
    lowered = translated.lower()
    urls = _extract_urls(message) + [item.url for item in request.attachments if item.url]

    if "archive" in lowered or re.search(r"\bdelete\b", lowered):
        actions.append({"intent": "notebook_update", "kind": "notebook_update", "operation": "archive", "notebook_name": _notebook_name(translated)})
    elif any(token in lowered for token in ("create notebook", "make notebook", "new notebook")):
        actions.append({"intent": "notebook_create", "kind": "notebook_create", "name": _notebook_name(translated) or _topic_from_message(translated)})
    elif "rename notebook" in lowered:
        actions.append({"intent": "notebook_update", "kind": "notebook_update", "operation": "rename", "name": _notebook_name(translated)})

    tools = _detect_tools(translated)
    if len(set(tools)) > 1:
        return _ResolvedIntent("clarify_request", translated, message, [{"intent": "clarify_request", "kind": "clarify", "reason": "multiple_study_tools"}])
    if tools:
        actions.append({"intent": "study_tool", "kind": "study_tool", "tool": tools[0], "topic": _topic_from_message(translated)})

    if urls:
        parsed = urlparse(urls[0])
        source_kind = "youtube" if "youtube.com" in parsed.netloc or "youtu.be" in parsed.netloc else "url"
        actions.append({"intent": "content_ingest", "kind": "content_ingest", "source_kind": source_kind, "url": urls[0]})

    role_report = _detect_role_report(translated, request.role)
    if role_report:
        actions.append({"intent": role_report, "kind": "query"})

    if _detect_teacher_assessment(translated, request.role):
        actions.append(
            {
                "intent": "teacher_assessment_generate",
                "kind": "query",
                "topic": _topic_from_message(translated),
                "num_questions": _extract_question_count(translated) or 5,
            }
        )

    navigation_targets = _detect_navigation_targets(translated, request.role or "student")
    if len(set(navigation_targets)) > 1:
        return _ResolvedIntent(
            "clarify_request",
            translated,
            message,
            [{"intent": "clarify_request", "kind": "clarify", "reason": "multiple_navigation_targets", "targets": navigation_targets}],
        )
    nav = navigation_targets[0] if navigation_targets else None
    if nav and not role_report and not _detect_teacher_assessment(translated, request.role):
        actions.append({"intent": "navigate", "kind": "navigate", "target": nav})

    if not actions:
        actions.append({"intent": "query", "kind": "query", "mode": _detect_query_mode(translated), "topic": _topic_from_message(translated)})

    return _ResolvedIntent(actions[-1]["intent"], translated, message, actions)


async def _execute_actions(
    *,
    request: MascotMessageRequest,
    session: AsyncSession,
    resolved_actions: list[dict[str, Any]],
    translated_message: str,
    normalized_message: str,
    trace_id: str,
    allow_high_risk: bool = False,
) -> MascotMessageResponse:
    notebook_hint = _notebook_name(translated_message)
    active_notebook = await _resolve_notebook(session, request, notebook_hint)
    explicit_notebook_target = _explicit_notebook_target(request)
    notebook_candidates: list[Notebook] = []
    if notebook_hint:
        notebook_candidates = await _find_notebook_candidates(session, request, notebook_hint)
    results: list[MascotAction] = []
    artifacts: list[dict[str, Any]] = []
    navigation: dict[str, Any] | None = None
    reply_parts: list[str] = []
    requires_confirmation = False
    confirmation_id: str | None = None
    intent = resolved_actions[-1]["intent"] if resolved_actions else "query"

    for action in resolved_actions:
        capability_key = action["intent"] if action["intent"] != "query" else ("ask_ai_question" if action.get("mode", "qa") == "qa" else action.get("mode", "qa"))
        if action["intent"] == "study_tool":
            capability_key = action["tool"]

        if capability_key and get_capability(capability_key) and not is_capability_allowed(capability_key, request.role or "student", request.channel):
            results.append(MascotAction(kind=action["kind"], status="failed", payload=action, result_summary="This action is not available for your account."))
            reply_parts.append("That action is not available for your account.")
            continue

        if action["intent"] == "clarify_request":
            results.append(MascotAction(kind="clarify", status="needs_input", payload=action, result_summary="The request needs a clearer instruction."))
            if action.get("reason") == "multiple_study_tools":
                reply_parts.append("Choose one format first: quiz, flashcards, mind map, flowchart, or concept map.")
            elif action.get("reason") == "multiple_navigation_targets":
                reply_parts.append("Tell me one page at a time: upload, attendance, marks, setup wizard, or dashboard.")
            else:
                reply_parts.append("Tell me a bit more clearly what you want me to do.")
            break

        if notebook_hint and len(notebook_candidates) > 1 and action["intent"] in {"query", "study_tool", "content_ingest", "notebook_update"}:
            results.append(
                MascotAction(
                    kind="clarify",
                    status="needs_input",
                    payload={"notebook_hint": notebook_hint, "candidates": [item.name for item in notebook_candidates[:5]]},
                    result_summary="Multiple notebooks match this request.",
                )
            )
            reply_parts.append(f"I found multiple notebooks matching '{notebook_hint}': {', '.join(item.name for item in notebook_candidates[:3])}. Tell me the exact notebook name.")
            break

        if explicit_notebook_target and active_notebook is None and action["intent"] in {"query", "study_tool", "content_ingest", "notebook_update"}:
            results.append(
                MascotAction(
                    kind=action["kind"],
                    status="failed",
                    payload={"intent": action["intent"], "notebook_id": explicit_notebook_target},
                    result_summary="The requested notebook is not accessible to this user.",
                )
            )
            reply_parts.append("I can't access that notebook from your account, so I did not run that action.")
            break

        if capability_key and capability_requires_confirmation(capability_key) and not allow_high_risk:
            pending = PendingMascotAction(
                kind=action["kind"],
                channel=request.channel,
                tenant_id=request.tenant_id or "",
                user_id=request.user_id or "",
                role=request.role or "student",
                payload={**action, "message": normalized_message, "translated_message": translated_message},
                notebook_id=str(active_notebook.id) if active_notebook else request.notebook_id,
                session_id=request.session_id,
            )
            store_pending_action(pending)
            requires_confirmation = True
            confirmation_id = pending.confirmation_id
            results.append(MascotAction(kind=action["kind"], status="pending_confirmation", payload=action, result_summary="Confirmation required before this change is applied."))
            reply_parts.append("Please confirm before I make that change.")
            break

        session_key = build_session_id(channel=request.channel, user_id=request.user_id or "anonymous", provided=request.session_id)
        mutation_signature = _mutation_signature(request, action, active_notebook)
        if mutation_signature and mutation_seen_recently(session_key, mutation_signature):
            results.append(
                MascotAction(
                    kind=action["kind"],
                    status="completed",
                    payload={"deduplicated": True, "intent": action["intent"]},
                    result_summary="Skipped a duplicate mutation that was already applied in this session.",
                )
            )
            reply_parts.append("I already applied that change in this session, so I skipped the duplicate request.")
            continue

        if action["intent"] == "notebook_create":
            notebook_name = (action.get("name") or "New Notebook").strip()
            active_notebook = await _create_notebook(session, request, notebook_name)
            navigation = _web_nav(request.role or "student", "ai_studio", str(active_notebook.id))
            results.append(MascotAction(kind="notebook_create", status="completed", payload={"name": notebook_name, "notebook_id": str(active_notebook.id)}, result_summary=f"Created notebook '{active_notebook.name}'.")) 
            reply_parts.append(f"Created notebook '{active_notebook.name}'.")
            if mutation_signature:
                remember_mutation(session_key, mutation_signature)
            continue

        if action["intent"] == "notebook_update":
            target = active_notebook or await _notebook_by_name(session, request, action.get("notebook_name"))
            if target is None:
                results.append(MascotAction(kind="notebook_update", status="failed", payload=action, result_summary="Notebook not found."))
                reply_parts.append("I could not find that notebook.")
                continue
            if action.get("operation") == "rename":
                new_name = (action.get("name") or "").strip()
                if not new_name:
                    results.append(MascotAction(kind="clarify", status="needs_input", payload=action, result_summary="Missing new notebook name."))
                    reply_parts.append("Tell me the new notebook name too.")
                    continue
                target.name = new_name
                await session.commit()
                await session.refresh(target)
                active_notebook = target
                results.append(MascotAction(kind="notebook_update", status="completed", payload={"operation": "rename", "notebook_id": str(target.id)}, result_summary=f"Renamed notebook to '{new_name}'.")) 
                reply_parts.append(f"Renamed the notebook to '{new_name}'.")
                if mutation_signature:
                    remember_mutation(session_key, mutation_signature)
            elif action.get("operation") == "archive":
                target.is_active = False
                await session.commit()
                results.append(MascotAction(kind="notebook_update", status="completed", payload={"operation": "archive", "notebook_id": str(target.id)}, result_summary=f"Archived notebook '{target.name}'.")) 
                reply_parts.append(f"Archived notebook '{target.name}'.")
                if mutation_signature:
                    remember_mutation(session_key, mutation_signature)
            continue

        if action["intent"] == "navigate":
            navigation = _web_nav(request.role or "student", action["target"], str(active_notebook.id) if active_notebook else None)
            if navigation:
                results.append(MascotAction(kind="navigate", status="completed", payload=navigation, result_summary=f"Prepared navigation to {navigation['href']}.")) 
                reply_parts.append(f"Opening {str(action['target']).replace('_', ' ')}.")
            else:
                results.append(MascotAction(kind="navigate", status="failed", payload=action, result_summary="No route available for that target."))
                reply_parts.append("I could not find that page for your account.")
            continue

        if action["intent"] == "teacher_insights_report":
            class_ids = await _teacher_class_ids(session, request)
            insights = await _build_teacher_insights(session, request, class_ids)
            artifacts.append({"tool": "teacher_insights_report", **insights})
            results.append(MascotAction(kind="query", status="completed", payload={"report": "teacher_insights_report"}, result_summary=insights["summary"]))
            reply_parts.append(insights["summary"])
            continue

        if action["intent"] == "teacher_doubt_heatmap_report":
            class_ids = await _teacher_class_ids(session, request)
            heatmap = await _build_teacher_doubt_heatmap(session, request, class_ids)
            artifacts.append({"tool": "teacher_doubt_heatmap_report", **heatmap})
            results.append(MascotAction(kind="query", status="completed", payload={"report": "teacher_doubt_heatmap_report"}, result_summary=heatmap["summary"]))
            reply_parts.append(heatmap["summary"])
            continue

        if action["intent"] == "teacher_assessment_generate":
            topic = (action.get("topic") or translated_message).strip()
            subject = await _resolve_subject(session, request, translated_message)
            if subject is None:
                results.append(MascotAction(kind="clarify", status="needs_input", payload=action, result_summary="I need the subject name to generate a teacher assessment."))
                reply_parts.append("Tell me the subject name too, for example: generate a Biology assessment on photosynthesis.")
                continue
            prompt_query = (
                f"Generate exactly {int(action.get('num_questions') or 5)} multiple-choice questions about: {topic}. "
                f"Subject: {subject.name}. Format as JSON array."
            )
            assessment = await run_text_query(
                InternalAIQueryRequest(
                    tenant_id=request.tenant_id or "",
                    query=prompt_query,
                    mode="quiz",
                    subject_id=str(subject.id),
                ),
                trace_id=trace_id,
            )
            summary = f"Generated an assessment for {subject.name} on {topic}."
            artifacts.append(
                {
                    "tool": "teacher_assessment_generate",
                    "subject": subject.name,
                    "topic": topic,
                    "assessment": assessment.get("answer", ""),
                    "citations": assessment.get("citations", []),
                }
            )
            results.append(MascotAction(kind="query", status="completed", payload={"report": "teacher_assessment_generate", "subject_id": str(subject.id), "topic": topic}, result_summary=summary))
            reply_parts.append(summary)
            continue

        if action["intent"] == "parent_progress_report":
            progress = await _build_parent_progress_report(session, request)
            artifacts.append({"tool": "parent_progress_report", **progress})
            results.append(MascotAction(kind="query", status="completed", payload={"report": "parent_progress_report"}, result_summary=progress["summary"]))
            reply_parts.append(progress["summary"])
            continue

        if action["intent"] == "admin_release_gate_report":
            snapshot = _build_admin_release_gate_report(request)
            artifacts.append({"tool": "admin_release_gate_report", **snapshot})
            results.append(MascotAction(kind="query", status="completed", payload={"report": "admin_release_gate_report"}, result_summary=snapshot["summary"]))
            reply_parts.append(snapshot["summary"])
            continue

        if action["intent"] == "admin_onboarding_report":
            onboarding = await _build_admin_onboarding_report(session, request)
            artifacts.append({"tool": "admin_onboarding_report", **onboarding})
            results.append(MascotAction(kind="query", status="completed", payload={"report": "admin_onboarding_report"}, result_summary=onboarding["summary"]))
            reply_parts.append(onboarding["summary"])
            continue

        if action["intent"] == "admin_ai_review_report":
            review = await _build_admin_ai_review_report(session, request)
            artifacts.append({"tool": "admin_ai_review_report", **review})
            results.append(MascotAction(kind="query", status="completed", payload={"report": "admin_ai_review_report"}, result_summary=review["summary"]))
            reply_parts.append(review["summary"])
            continue

        if action["intent"] == "teacher_roster_import":
            roster_result = await _apply_teacher_roster_import(session, request, action)
            artifacts.append(roster_result)
            results.append(
                MascotAction(
                    kind="structured_import",
                    status="completed",
                    payload={"intent": "teacher_roster_import", "created_count": roster_result.get("created_count", 0)},
                    result_summary=roster_result["summary"],
                )
            )
            reply_parts.append(roster_result["summary"])
            if mutation_signature:
                remember_mutation(session_key, mutation_signature)
            continue

        if action["intent"] == "admin_teacher_import":
            teacher_import = await _apply_admin_teacher_import(session, request, action)
            artifacts.append(teacher_import)
            results.append(
                MascotAction(
                    kind="structured_import",
                    status="completed",
                    payload={"intent": "admin_teacher_import", "created_count": teacher_import.get("created_count", 0)},
                    result_summary=teacher_import["summary"],
                )
            )
            reply_parts.append(teacher_import["summary"])
            if mutation_signature:
                remember_mutation(session_key, mutation_signature)
            continue

        if action["intent"] == "admin_student_import":
            student_import = await _apply_admin_student_import(session, request, action)
            artifacts.append(student_import)
            results.append(
                MascotAction(
                    kind="structured_import",
                    status="completed",
                    payload={"intent": "admin_student_import", "created": student_import.get("created", 0)},
                    result_summary=student_import["summary"],
                )
            )
            reply_parts.append(student_import["summary"])
            if mutation_signature:
                remember_mutation(session_key, mutation_signature)
            continue

        if action["intent"] == "teacher_attendance_import":
            attendance_result = await _apply_teacher_attendance_import(session, request, action)
            artifacts.append(attendance_result)
            results.append(
                MascotAction(
                    kind="structured_import",
                    status="completed",
                    payload={"intent": "teacher_attendance_import", "imported": attendance_result.get("imported", 0)},
                    result_summary=attendance_result["summary"],
                )
            )
            reply_parts.append(attendance_result["summary"])
            if mutation_signature:
                remember_mutation(session_key, mutation_signature)
            continue

        if action["intent"] == "teacher_marks_import":
            marks_result = await _apply_teacher_marks_import(session, request, action)
            artifacts.append(marks_result)
            results.append(
                MascotAction(
                    kind="structured_import",
                    status="completed",
                    payload={"intent": "teacher_marks_import", "imported": marks_result.get("imported", 0), "exam_id": marks_result.get("exam_id")},
                    result_summary=marks_result["summary"],
                )
            )
            reply_parts.append(marks_result["summary"])
            if mutation_signature:
                remember_mutation(session_key, mutation_signature)
            continue

        if action["intent"] == "content_ingest":
            url = str(action.get("url") or "").strip()
            if not url:
                results.append(MascotAction(kind="content_ingest", status="failed", payload=action, result_summary="Missing content URL."))
                reply_parts.append("I need a URL or YouTube link to ingest.")
                continue
            if action.get("source_kind") == "youtube":
                from src.infrastructure.llm.cache import invalidate_tenant_cache
                from src.infrastructure.llm.providers import get_embedding_provider, get_vector_store_provider
                from src.infrastructure.vector_store.ingestion import ingest_youtube

                subject = await _resolve_subject(session, request, translated_message)
                document_id = str(uuid4())
                chunks = ingest_youtube(
                    url=url,
                    document_id=document_id,
                    tenant_id=request.tenant_id or "",
                    subject_id=str(subject.id) if subject else None,
                    notebook_id=str(active_notebook.id) if active_notebook else None,
                )
                if chunks:
                    embeddings = await get_embedding_provider().embed_batch([chunk.text for chunk in chunks])
                    get_vector_store_provider(request.tenant_id or "").add_chunks(
                        [
                            {
                                "text": chunk.text,
                                "document_id": chunk.document_id,
                                "page_number": chunk.page_number,
                                "section_title": chunk.section_title or "",
                                "subject_id": chunk.subject_id or "",
                                "notebook_id": chunk.notebook_id or "",
                                "source_file": chunk.source_file or "",
                            }
                            for chunk in chunks
                        ],
                        embeddings,
                    )
                invalidate_tenant_cache(request.tenant_id or "")
                ingest = {
                    "document_id": document_id,
                    "title": action.get("title") or "YouTube lecture",
                    "chunks_created": len(chunks),
                }
            else:
                ingest = await run_url_ingestion(
                    InternalIngestURLRequest(
                        tenant_id=request.tenant_id or "",
                        url=url,
                        title=action.get("title"),
                        notebook_id=UUID(str(active_notebook.id)) if active_notebook else None,
                    ),
                    trace_id=trace_id,
                )
                if active_notebook and request.user_id and request.tenant_id:
                    document = Document(
                        id=UUID(str(ingest["document_id"])),
                        tenant_id=_safe_uuid(request.tenant_id),
                        subject_id=subject.id if action.get("source_kind") == "youtube" and subject else None,
                        notebook_id=active_notebook.id,
                        uploaded_by=_safe_uuid(request.user_id),
                        file_name=ingest.get("title") or url[:120],
                    file_type="youtube" if action.get("source_kind") == "youtube" else "url",
                    storage_path=url,
                    ingestion_status="completed",
                    chunk_count=int(ingest.get("chunks_created", 0)),
                )
                session.add(document)
                await session.commit()
            results.append(MascotAction(kind="content_ingest", status="completed", payload={"url": url, "document_id": ingest.get("document_id")}, result_summary=f"Ingested {ingest.get('title') or 'that link'} into the knowledge base.")) 
            reply_parts.append(f"Ingested {ingest.get('title') or 'that link'} into the knowledge base.")
            continue

        if action["intent"] == "study_tool":
            topic = (action.get("topic") or translated_message).strip()
            if not topic:
                results.append(MascotAction(kind="clarify", status="needs_input", payload=action, result_summary="Missing topic for study tool."))
                reply_parts.append("Tell me the topic too.")
                continue
            tool = action["tool"]
            tool_result = await run_study_tool(
                InternalStudyToolGenerateRequest(
                    tenant_id=request.tenant_id or "",
                    tool=tool,
                    topic=topic,
                    notebook_id=UUID(str(active_notebook.id)) if active_notebook else None,
                ),
                trace_id=trace_id,
            )
            generated = await _save_generated(session, request, active_notebook, tool, topic, tool_result)
            if generated:
                results.append(MascotAction(kind="generated_content_save", status="completed", payload={"generated_content_id": str(generated.id)}, result_summary="Saved generated content to the notebook library."))
            artifacts.append({"tool": tool, "data": tool_result.get("data"), "citations": tool_result.get("citations", [])})
            results.append(MascotAction(kind="study_tool", status="completed", payload={"tool": tool, "topic": topic}, result_summary=f"Generated {tool.replace('_', ' ')} for {topic}.")) 
            reply_parts.append(f"Generated {tool.replace('_', ' ')} for {topic}.")
            continue

        if action["intent"] == "query":
            topic = (action.get("topic") or translated_message).strip()
            mode = action.get("mode", "qa")
            query_result = await run_text_query(
                InternalAIQueryRequest(
                    tenant_id=request.tenant_id or "",
                    query=topic or translated_message,
                    mode=mode,
                    notebook_id=UUID(str(active_notebook.id)) if active_notebook else None,
                    language="english",
                    response_length="default",
                    expertise_level="standard",
                ),
                trace_id=trace_id,
            )
            artifacts.append({"tool": mode, "answer": query_result.get("answer"), "citations": query_result.get("citations", []), "mode": query_result.get("mode")})
            results.append(MascotAction(kind="query", status="completed", payload={"mode": mode, "topic": topic}, result_summary=f"Answered using {mode.replace('_', ' ')} mode."))
            if query_result.get("answer"):
                reply_parts.append(str(query_result["answer"]).strip())

    notebook_id = str(active_notebook.id) if active_notebook else request.notebook_id
    _store_session(request, notebook_id=notebook_id, intent=intent, navigation=navigation)
    reply = "\n\n".join(part for part in reply_parts if part).strip() or "I’m ready. Tell me what you want to do."
    if request.channel == "whatsapp":
        reply = _format_whatsapp_reply(reply, intent=intent, artifacts=artifacts, navigation=navigation)
        navigation = None
    return MascotMessageResponse(
        reply_text=reply,
        intent=intent,
        normalized_message=normalized_message,
        translated_message=translated_message if translated_message != normalized_message else None,
        actions=results,
        artifacts=artifacts,
        navigation=navigation,
        requires_confirmation=requires_confirmation,
        confirmation_id=confirmation_id,
        follow_up_suggestions=_follow_ups(intent, active_notebook.name if active_notebook else None),
        notebook_id=notebook_id,
        trace_id=trace_id,
    )


async def execute_pending_confirmation(*, confirmation_id: str, approved: bool, channel: str, session_id: str | None, tenant_id: str, user_id: str, role: str, session: AsyncSession) -> MascotMessageResponse:
    trace_id = f"mascot-{uuid4().hex[:8]}"
    confirmation_started_at = time.perf_counter()
    pending = load_pending_action(confirmation_id)
    request = MascotMessageRequest(message="", channel=channel, role=role, tenant_id=tenant_id, user_id=user_id, session_id=session_id)
    if pending is None or pending.tenant_id != tenant_id or pending.user_id != user_id:
        _record_mascot_stage(trace_id=trace_id, tenant_id=tenant_id, user_id=user_id, stage="mascot", operation="confirmation", started_at=confirmation_started_at, outcome="failed", metadata={"approved": approved, "reason": "missing_pending"})
        response = MascotMessageResponse(reply_text="That pending action was not found or no longer exists.", intent="confirm", normalized_message="confirm", actions=[MascotAction(kind="confirm", status="failed", result_summary="Pending action missing.")], trace_id=trace_id)
        await _append_mascot_audit_log(session, request=request, trace_id=trace_id, action="mascot.confirmation", status="failed", metadata={"approved": approved, "reason": "missing_pending"})
        await session.commit()
        return response
    if not approved:
        delete_pending_action(confirmation_id)
        _record_mascot_stage(trace_id=trace_id, tenant_id=tenant_id, user_id=user_id, stage="mascot", operation="confirmation", started_at=confirmation_started_at, outcome="cancelled", metadata={"approved": approved})
        response = MascotMessageResponse(reply_text="Cancelled. I did not make any changes.", intent="confirm", normalized_message="confirm", actions=[MascotAction(kind="confirm", status="completed", result_summary="Pending action cancelled.")], trace_id=trace_id)
        await _append_mascot_audit_log(session, request=request, trace_id=trace_id, action="mascot.confirmation", status="cancelled", metadata={"approved": approved})
        await session.commit()
        return response
    request = MascotMessageRequest(message=str(pending.payload.get("message") or ""), channel=channel, role=role, tenant_id=tenant_id, user_id=user_id, notebook_id=pending.notebook_id, session_id=session_id or pending.session_id)
    try:
        response = await _execute_actions(request=request, session=session, resolved_actions=[pending.payload], translated_message=str(pending.payload.get("translated_message") or pending.payload.get("message") or ""), normalized_message=str(pending.payload.get("message") or ""), trace_id=trace_id, allow_high_risk=True)
    except Exception:
        _record_mascot_stage(trace_id=trace_id, tenant_id=tenant_id, user_id=user_id, stage="mascot", operation="confirmation", started_at=confirmation_started_at, outcome="error", metadata={"approved": approved})
        await _append_mascot_audit_log(session, request=request, trace_id=trace_id, action="mascot.confirmation", status="error", metadata={"approved": approved})
        await session.commit()
        raise
    delete_pending_action(confirmation_id)
    _record_mascot_stage(trace_id=trace_id, tenant_id=tenant_id, user_id=user_id, stage="mascot", operation="confirmation", started_at=confirmation_started_at, outcome="success", metadata={"approved": approved})
    await _append_mascot_audit_log(session, request=request, trace_id=trace_id, action="mascot.confirmation", status="success", metadata={"approved": approved, "intent": pending.payload.get("intent")})
    await session.commit()
    return response


async def handle_mascot_message(request: MascotMessageRequest, session: AsyncSession) -> MascotMessageResponse:
    trace_id = f"mascot-{uuid4().hex[:8]}"
    request.message = _clean(request.message)
    interpret_started_at = time.perf_counter()
    try:
        interpreted = await _interpret(request)
    except Exception:
        _record_mascot_stage(trace_id=trace_id, tenant_id=request.tenant_id, user_id=request.user_id, stage="mascot", operation="interpretation", started_at=interpret_started_at, outcome="error")
        await _append_mascot_audit_log(session, request=request, trace_id=trace_id, action="mascot.message", status="error", metadata={"phase": "interpretation"})
        await session.commit()
        raise
    _record_mascot_stage(trace_id=trace_id, tenant_id=request.tenant_id, user_id=request.user_id, stage="mascot", operation="interpretation", started_at=interpret_started_at, outcome="success", metadata={"intent": interpreted.intent})
    execute_started_at = time.perf_counter()
    try:
        response = await _execute_actions(request=request, session=session, resolved_actions=interpreted.actions, translated_message=interpreted.translated_message, normalized_message=interpreted.normalized_message, trace_id=trace_id)
    except Exception:
        _record_mascot_stage(trace_id=trace_id, tenant_id=request.tenant_id, user_id=request.user_id, stage="mascot", operation="execution", started_at=execute_started_at, outcome="error", metadata={"intent": interpreted.intent})
        await _append_mascot_audit_log(session, request=request, trace_id=trace_id, action="mascot.message", status="error", metadata={"phase": "execution", "intent": interpreted.intent})
        await session.commit()
        raise
    _record_mascot_stage(trace_id=trace_id, tenant_id=request.tenant_id, user_id=request.user_id, stage="mascot", operation="execution", started_at=execute_started_at, outcome="success", metadata={"intent": response.intent})
    await _append_mascot_audit_log(session, request=request, trace_id=trace_id, action="mascot.message", status="success", metadata={"intent": response.intent, "requires_confirmation": response.requires_confirmation, "notebook_id": response.notebook_id})
    await session.commit()
    return response


def _upload_constraints(role: str | None) -> tuple[set[str], int]:
    normalized = (role or "").strip().lower()
    if normalized in {"teacher", "admin"}:
        return set(TEACHER_ALLOWED_EXTENSIONS), TEACHER_MAX_FILE_SIZE
    return set(STUDENT_ALLOWED_EXTENSIONS), STUDENT_MAX_FILE_SIZE


async def _candidate_subjects(session: AsyncSession, request: MascotMessageRequest) -> list[Subject]:
    tenant_uuid = _safe_uuid(request.tenant_id)
    if tenant_uuid is None:
        return []
    normalized_role = (request.role or "").strip().lower()
    if normalized_role not in {"teacher", "admin"}:
        return []
    if normalized_role == "admin":
        result = await session.execute(select(Subject).where(Subject.tenant_id == tenant_uuid))
        return list(result.scalars().all())
    class_ids = await _teacher_class_ids(session, request)
    if not class_ids:
        return []
    result = await session.execute(select(Subject).where(Subject.tenant_id == tenant_uuid, Subject.class_id.in_(class_ids)))
    return list(result.scalars().all())


async def _resolve_subject(session: AsyncSession, request: MascotMessageRequest, message: str) -> Subject | None:
    subjects = await _candidate_subjects(session, request)
    if not subjects:
        return None
    lowered = _clean(message).lower()
    exact = next((subject for subject in subjects if subject.name.strip().lower() in lowered), None)
    if exact:
        return exact
    token_matches = [subject for subject in subjects if any(token and token in lowered for token in subject.name.strip().lower().split())]
    if len(token_matches) == 1:
        return token_matches[0]
    if len(subjects) == 1:
        return subjects[0]
    return None


async def _teacher_class_ids(session: AsyncSession, request: MascotMessageRequest) -> list[UUID]:
    tenant_uuid = _safe_uuid(request.tenant_id)
    user_uuid = _safe_uuid(request.user_id)
    if tenant_uuid is None:
        return []
    if (request.role or "").strip().lower() == "admin":
        result = await session.execute(select(Class.id).where(Class.tenant_id == tenant_uuid))
        return list(result.scalars().all())
    if (request.role or "").strip().lower() != "teacher" or user_uuid is None:
        return []
    result = await session.execute(
        select(Timetable.class_id).where(
            Timetable.tenant_id == tenant_uuid,
            Timetable.teacher_id == user_uuid,
        ).distinct()
    )
    return list(result.scalars().all())


async def _candidate_classes(session: AsyncSession, request: MascotMessageRequest) -> list[Class]:
    tenant_uuid = _safe_uuid(request.tenant_id)
    if tenant_uuid is None:
        return []
    class_ids = await _teacher_class_ids(session, request)
    if not class_ids:
        return []
    result = await session.execute(select(Class).where(Class.tenant_id == tenant_uuid, Class.id.in_(class_ids)))
    return list(result.scalars().all())


async def _teacher_can_access_class(session: AsyncSession, request: MascotMessageRequest, class_id: UUID | None) -> bool:
    if class_id is None:
        return False
    if (request.role or "").strip().lower() == "admin":
        return True
    return class_id in await _teacher_class_ids(session, request)


async def _teacher_can_access_subject(session: AsyncSession, request: MascotMessageRequest, subject_id: UUID | None) -> bool:
    if subject_id is None:
        return False
    if (request.role or "").strip().lower() == "admin":
        return True
    subjects = await _candidate_subjects(session, request)
    return any(subject.id == subject_id for subject in subjects)


async def _resolve_class(
    session: AsyncSession,
    request: MascotMessageRequest,
    message: str,
    *,
    explicit_id: str | None = None,
) -> Class | None:
    classes = await _candidate_classes(session, request)
    if not classes:
        return None
    if explicit_id:
        class_uuid = _safe_uuid(explicit_id)
        if class_uuid is not None:
            exact = next((item for item in classes if item.id == class_uuid), None)
            if exact:
                return exact
    lowered = _clean(message).lower()
    exact_name = next((item for item in classes if item.name.strip().lower() in lowered), None)
    if exact_name:
        return exact_name
    if len(classes) == 1:
        return classes[0]
    return None


async def _resolve_subject_with_context(session: AsyncSession, request: MascotMessageRequest, message: str) -> Subject | None:
    metadata = _ui_metadata(request)
    explicit_id = str(
        metadata.get("subject_id")
        or (request.ui_context.current_page_entity_id if request.ui_context and request.ui_context.current_page_entity == "subject" else "")
        or ""
    ).strip()
    if explicit_id:
        subject_uuid = _safe_uuid(explicit_id)
        if subject_uuid is not None:
            subjects = await _candidate_subjects(session, request)
            exact = next((item for item in subjects if item.id == subject_uuid), None)
            if exact:
                return exact
    return await _resolve_subject(session, request, message)


async def _resolve_student_identifier_in_class_async(
    session: AsyncSession,
    request: MascotMessageRequest,
    identifier: str,
    class_id: UUID,
) -> UUID | None:
    tenant_uuid = _safe_uuid(request.tenant_id)
    if tenant_uuid is None:
        return None
    cleaned = identifier.strip()
    if not cleaned:
        return None
    direct_uuid = _safe_uuid(cleaned)
    if direct_uuid is not None:
        enrollment_result = await session.execute(
            select(Enrollment).where(
                Enrollment.tenant_id == tenant_uuid,
                Enrollment.student_id == direct_uuid,
                Enrollment.class_id == class_id,
            )
        )
        if enrollment_result.scalar_one_or_none() is not None:
            return direct_uuid

    enrollment_result = await session.execute(
        select(Enrollment.student_id).where(
            Enrollment.tenant_id == tenant_uuid,
            Enrollment.class_id == class_id,
        )
    )
    student_ids = [item for item in enrollment_result.scalars().all() if item]
    if not student_ids:
        return None
    users_result = await session.execute(
        select(User).where(
            User.tenant_id == tenant_uuid,
            User.id.in_(student_ids),
        )
    )
    match_value = cleaned.casefold()
    for student in users_result.scalars().all():
        if student.email and student.email.casefold() == match_value:
            return student.id
        if student.full_name and student.full_name.casefold() == match_value:
            return student.id
    return None


async def _tenant_domain(session: AsyncSession, tenant_id: str | None) -> str | None:
    tenant_uuid = _safe_uuid(tenant_id)
    if tenant_uuid is None:
        return None
    result = await session.execute(select(Tenant.domain).where(Tenant.id == tenant_uuid))
    return result.scalar_one_or_none()


def _structured_import_metadata(extraction: Any, parsed: Any | None = None) -> dict[str, Any]:
    review_required = bool(getattr(extraction, "review_required", False) or getattr(parsed, "review_required", False))
    warning = getattr(parsed, "warning", None) or getattr(extraction, "warning", None)
    unmatched_count = len(getattr(parsed, "unmatched_lines", []) or [])
    return {
        "ocr_processed": bool(getattr(extraction, "used_ocr", False)),
        "ocr_review_required": review_required,
        "ocr_warning": warning,
        "ocr_languages": list(getattr(extraction, "languages", []) or []),
        "ocr_preprocessing": list(getattr(extraction, "preprocessing_applied", []) or []),
        "ocr_confidence": getattr(extraction, "confidence", None),
        "ocr_unmatched_lines": unmatched_count,
    }


async def _prepare_teacher_roster_import(
    session: AsyncSession,
    request: MascotMessageRequest,
    filename: str,
    content: bytes,
) -> dict[str, Any]:
    extraction = extract_upload_content_result(filename, content)
    rows: list[dict[str, str]] = []
    parsed = None
    if extraction.used_ocr:
        parsed = parse_account_rows_with_diagnostics(extraction.text, default_password="Student123!")
        rows = [dict(row) for _, row in parsed.rows]
    else:
        reader = csv.reader(io.StringIO(extraction.text))
        for row in reader:
            if not row or not any(row):
                continue
            name = (row[0] or "").strip()
            if not name:
                continue
            email = row[1].strip() if len(row) > 1 and row[1].strip() else f"{re.sub(r'[^a-zA-Z0-9]', '.', name.lower())}@example.com"
            password = row[2].strip() if len(row) > 2 and row[2].strip() else "Student123!"
            rows.append({"name": name, "email": email, "password": password})
    if not rows:
        raise ValueError("No readable student rows found in that roster.")
    metadata = _structured_import_metadata(extraction, parsed)
    count = len(rows)
    parts = [f"Prepared {count} student row{'s' if count != 1 else ''} for onboarding."]
    if isinstance(metadata["ocr_confidence"], (int, float)):
        parts.append(f"OCR confidence {(float(metadata['ocr_confidence']) * 100):.0f}%.")
    if metadata["ocr_review_required"]:
        parts.append("Review is recommended before importing.")
    if metadata["ocr_unmatched_lines"]:
        parts.append(f"{metadata['ocr_unmatched_lines']} line{'s' if metadata['ocr_unmatched_lines'] != 1 else ''} could not be mapped cleanly.")
    if metadata["ocr_warning"]:
        parts.append(str(metadata["ocr_warning"]))
    return {
        "intent": "teacher_roster_import",
        "kind": "structured_import",
        "rows": rows,
        "metadata": metadata,
        "filename": filename,
        "result_summary": " ".join(parts),
        "artifact": {"tool": "teacher_roster_import", "preview_rows": _summarize_rows(rows), "total_rows": count, **metadata},
    }


async def _prepare_admin_teacher_import(
    session: AsyncSession,
    request: MascotMessageRequest,
    filename: str,
    content: bytes,
) -> dict[str, Any]:
    extraction = extract_upload_content_result(filename, content)
    rows: list[dict[str, str]] = []
    parsed = None
    if extraction.used_ocr:
        parsed = parse_account_rows_with_diagnostics(extraction.text, default_password="Teacher123!")
        rows = [dict(row) for _, row in parsed.rows]
    else:
        reader = csv.reader(io.StringIO(extraction.text))
        for row in reader:
            if not row or not any(row):
                continue
            name = (row[0] or "").strip()
            if not name:
                continue
            email = row[1].strip() if len(row) > 1 and row[1].strip() else f"{re.sub(r'[^a-zA-Z0-9]', '.', name.lower())}@example.com"
            password = row[2].strip() if len(row) > 2 and row[2].strip() else "Teacher123!"
            rows.append({"name": name, "email": email, "password": password})
    if not rows:
        raise ValueError("No readable teacher rows found in that onboarding file.")
    metadata = _structured_import_metadata(extraction, parsed)
    count = len(rows)
    parts = [f"Prepared {count} teacher row{'s' if count != 1 else ''} for onboarding."]
    if isinstance(metadata["ocr_confidence"], (int, float)):
        parts.append(f"OCR confidence {(float(metadata['ocr_confidence']) * 100):.0f}%.")
    if metadata["ocr_review_required"]:
        parts.append("Review is recommended before importing.")
    if metadata["ocr_unmatched_lines"]:
        parts.append(f"{metadata['ocr_unmatched_lines']} line{'s' if metadata['ocr_unmatched_lines'] != 1 else ''} could not be mapped cleanly.")
    if metadata["ocr_warning"]:
        parts.append(str(metadata["ocr_warning"]))
    return {
        "intent": "admin_teacher_import",
        "kind": "structured_import",
        "rows": rows,
        "metadata": metadata,
        "filename": filename,
        "result_summary": " ".join(parts),
        "artifact": {"tool": "admin_teacher_import", "preview_rows": _summarize_rows(rows), "total_rows": count, **metadata},
    }


async def _prepare_admin_student_import(
    session: AsyncSession,
    request: MascotMessageRequest,
    filename: str,
    content: bytes,
) -> dict[str, Any]:
    extraction = extract_upload_content_result(filename, content)
    rows: list[dict[str, str]] = []
    parsed = None
    if extraction.used_ocr:
        parsed = parse_student_import_rows_with_diagnostics(extraction.text)
        rows = [
            {
                "full_name": row["full_name"],
                "email": row["email"],
                "password": "Student123!",
                "class_name": row["class_name"],
            }
            for _, row in parsed.rows
        ]
    else:
        reader = csv.DictReader(io.StringIO(extraction.text))
        for row in reader:
            name = (row.get("full_name") or "").strip()
            email = (row.get("email") or "").strip().lower()
            if name and not email:
                email = re.sub(r"[^a-zA-Z0-9]", ".", name.lower()).strip(".") + "@example.com"
            if not name and not email:
                continue
            rows.append(
                {
                    "full_name": name,
                    "email": email,
                    "password": (row.get("password") or "Student123!").strip(),
                    "class_name": (row.get("class_name") or "").strip(),
                }
            )
    if not rows:
        raise ValueError("No readable student rows found in that onboarding file.")
    metadata = _structured_import_metadata(extraction, parsed)
    count = len(rows)
    parts = [f"Prepared {count} student row{'s' if count != 1 else ''} for onboarding."]
    if isinstance(metadata["ocr_confidence"], (int, float)):
        parts.append(f"OCR confidence {(float(metadata['ocr_confidence']) * 100):.0f}%.")
    if metadata["ocr_review_required"]:
        parts.append("Review is recommended before importing.")
    if metadata["ocr_unmatched_lines"]:
        parts.append(f"{metadata['ocr_unmatched_lines']} line{'s' if metadata['ocr_unmatched_lines'] != 1 else ''} could not be mapped cleanly.")
    if metadata["ocr_warning"]:
        parts.append(str(metadata["ocr_warning"]))
    return {
        "intent": "admin_student_import",
        "kind": "structured_import",
        "rows": rows,
        "metadata": metadata,
        "filename": filename,
        "result_summary": " ".join(parts),
        "artifact": {"tool": "admin_student_import", "preview_rows": _summarize_rows(rows), "total_rows": count, **metadata},
    }


async def _prepare_teacher_attendance_import(
    session: AsyncSession,
    request: MascotMessageRequest,
    filename: str,
    content: bytes,
) -> dict[str, Any]:
    metadata = _ui_metadata(request)
    explicit_class_id = str(
        metadata.get("class_id")
        or (request.ui_context.current_page_entity_id if request.ui_context else "")
        or ""
    )
    school_class = await _resolve_class(
        session,
        request,
        request.message,
        explicit_id=explicit_class_id,
    )
    if school_class is None:
        raise ValueError("I need the class context before importing attendance. Open the attendance page for a class or mention the class name.")
    attendance_date = _parse_date_hint(str(metadata.get("date") or "").strip()) or _parse_date_hint(request.message)
    if attendance_date is None:
        raise ValueError("I need the attendance date before importing. Set the date on the attendance page or mention YYYY-MM-DD in your message.")
    extraction = extract_upload_content_result(filename, content)
    parsed = parse_attendance_rows_with_diagnostics(extraction.text)
    rows = [{"identifier": identifier, "status": status} for identifier, status in parsed.rows]
    if not rows:
        raise ValueError("No readable attendance rows found in that file.")
    import_metadata = _structured_import_metadata(extraction, parsed)
    count = len(rows)
    parts = [f"Prepared {count} attendance row{'s' if count != 1 else ''} for {school_class.name} on {attendance_date.isoformat()}."]
    if isinstance(import_metadata["ocr_confidence"], (int, float)):
        parts.append(f"OCR confidence {(float(import_metadata['ocr_confidence']) * 100):.0f}%.")
    if import_metadata["ocr_review_required"]:
        parts.append("Review is recommended before import.")
    if import_metadata["ocr_unmatched_lines"]:
        parts.append(f"{import_metadata['ocr_unmatched_lines']} line{'s' if import_metadata['ocr_unmatched_lines'] != 1 else ''} need manual cleanup.")
    if import_metadata["ocr_warning"]:
        parts.append(str(import_metadata["ocr_warning"]))
    return {
        "intent": "teacher_attendance_import",
        "kind": "structured_import",
        "class_id": str(school_class.id),
        "class_name": school_class.name,
        "date": attendance_date.isoformat(),
        "rows": rows,
        "metadata": import_metadata,
        "filename": filename,
        "result_summary": " ".join(parts),
        "artifact": {"tool": "teacher_attendance_import", "class_name": school_class.name, "date": attendance_date.isoformat(), "preview_rows": _summarize_rows(rows), "total_rows": count, **import_metadata},
    }


async def _prepare_teacher_marks_import(
    session: AsyncSession,
    request: MascotMessageRequest,
    filename: str,
    content: bytes,
) -> dict[str, Any]:
    metadata = _ui_metadata(request)
    subject = await _resolve_subject_with_context(session, request, request.message)
    if subject is None:
        raise ValueError("I need the subject before importing marks. Select a subject on the marks page or mention it in your message.")
    exam_name = str(metadata.get("exam_name") or "").strip()
    if not exam_name:
        raise ValueError("I need the exam name before importing marks.")
    max_marks = _parse_int_hint(metadata.get("max_marks"))
    if max_marks is None or max_marks <= 0:
        raise ValueError("I need valid max marks before importing marks.")
    exam_date = _parse_date_hint(str(metadata.get("exam_date") or "").strip())
    extraction = extract_upload_content_result(filename, content)
    parsed = parse_marks_rows_with_diagnostics(extraction.text)
    rows = [{"identifier": identifier, "marks_obtained": marks} for identifier, marks in parsed.rows]
    if not rows:
        raise ValueError("No readable marks rows found in that file.")
    import_metadata = _structured_import_metadata(extraction, parsed)
    count = len(rows)
    parts = [f"Prepared {count} marks row{'s' if count != 1 else ''} for {subject.name} ({exam_name})."]
    if isinstance(import_metadata["ocr_confidence"], (int, float)):
        parts.append(f"OCR confidence {(float(import_metadata['ocr_confidence']) * 100):.0f}%.")
    if import_metadata["ocr_review_required"]:
        parts.append("Review is recommended before import.")
    if import_metadata["ocr_unmatched_lines"]:
        parts.append(f"{import_metadata['ocr_unmatched_lines']} line{'s' if import_metadata['ocr_unmatched_lines'] != 1 else ''} need manual cleanup.")
    if import_metadata["ocr_warning"]:
        parts.append(str(import_metadata["ocr_warning"]))
    return {
        "intent": "teacher_marks_import",
        "kind": "structured_import",
        "class_id": str(subject.class_id),
        "subject_id": str(subject.id),
        "subject_name": subject.name,
        "exam_name": exam_name,
        "exam_date": exam_date.isoformat() if exam_date else None,
        "max_marks": max_marks,
        "rows": rows,
        "metadata": import_metadata,
        "filename": filename,
        "result_summary": " ".join(parts),
        "artifact": {"tool": "teacher_marks_import", "subject": subject.name, "exam_name": exam_name, "max_marks": max_marks, "preview_rows": _summarize_rows(rows), "total_rows": count, **import_metadata},
    }


async def _apply_teacher_roster_import(session: AsyncSession, request: MascotMessageRequest, action: dict[str, Any]) -> dict[str, Any]:
    rows = [dict(item) for item in action.get("rows", []) if isinstance(item, dict)]
    if not rows:
        return {"summary": "No student rows were available to import.", "created_count": 0, "tool": "teacher_roster_import", "errors": []}
    try:
        from src.domains.identity.routes.auth import pwd_context
    except Exception:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    tenant_domain = await _tenant_domain(session, request.tenant_id)
    tenant_uuid = _safe_uuid(request.tenant_id)
    created_count = 0
    skipped: list[str] = []
    for row in rows:
        email = str(row.get("email") or "").strip()
        if "@example.com" in email and tenant_domain:
            email = email.replace("@example.com", f"@{tenant_domain}")
        if not email:
            skipped.append(str(row.get("name") or "Unnamed student"))
            continue
        existing_result = await session.execute(select(User).where(User.email == email))
        if existing_result.scalar_one_or_none() is not None:
            skipped.append(email)
            continue
        student = User(
            tenant_id=tenant_uuid,
            email=email,
            full_name=str(row.get("name") or "").strip() or email,
            role="student",
            hashed_password=pwd_context.hash(str(row.get("password") or "Student123!")),
            is_active=True,
        )
        session.add(student)
        created_count += 1
    await session.commit()
    summary = f"Imported {created_count} student{'s' if created_count != 1 else ''}."
    if skipped:
        summary += f" Skipped {len(skipped)} duplicate or invalid row{'s' if len(skipped) != 1 else ''}."
    return {"summary": summary, "created_count": created_count, "errors": skipped[:10], "tool": "teacher_roster_import"}


async def _apply_admin_teacher_import(session: AsyncSession, request: MascotMessageRequest, action: dict[str, Any]) -> dict[str, Any]:
    rows = [dict(item) for item in action.get("rows", []) if isinstance(item, dict)]
    if not rows:
        return {"summary": "No teacher rows were available to import.", "created_count": 0, "tool": "admin_teacher_import", "errors": []}
    try:
        from src.domains.identity.routes.auth import pwd_context
    except Exception:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    tenant_domain = await _tenant_domain(session, request.tenant_id)
    tenant_uuid = _safe_uuid(request.tenant_id)
    created_count = 0
    skipped: list[str] = []
    for row in rows:
        email = str(row.get("email") or "").strip()
        if "@example.com" in email and tenant_domain:
            email = email.replace("@example.com", f"@{tenant_domain}")
        if not email:
            skipped.append(str(row.get("name") or "Unnamed teacher"))
            continue
        existing_result = await session.execute(select(User).where(User.email == email))
        if existing_result.scalar_one_or_none() is not None:
            skipped.append(email)
            continue
        teacher = User(
            tenant_id=tenant_uuid,
            email=email,
            full_name=str(row.get("name") or "").strip() or email,
            role="teacher",
            hashed_password=pwd_context.hash(str(row.get("password") or "Teacher123!")),
            is_active=True,
        )
        session.add(teacher)
        created_count += 1
    await session.commit()
    summary = f"Imported {created_count} teacher{'s' if created_count != 1 else ''}."
    if skipped:
        summary += f" Skipped {len(skipped)} duplicate or invalid row{'s' if len(skipped) != 1 else ''}."
    return {"summary": summary, "created_count": created_count, "errors": skipped[:10], "tool": "admin_teacher_import"}


async def _apply_admin_student_import(session: AsyncSession, request: MascotMessageRequest, action: dict[str, Any]) -> dict[str, Any]:
    rows = [dict(item) for item in action.get("rows", []) if isinstance(item, dict)]
    if not rows:
        return {"summary": "No student rows were available to import.", "created": 0, "tool": "admin_student_import", "errors": []}
    try:
        from src.domains.identity.routes.auth import pwd_context
    except Exception:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    tenant_uuid = _safe_uuid(request.tenant_id)
    created = 0
    errors: list[str] = []
    class_result = await session.execute(select(Class).where(Class.tenant_id == tenant_uuid))
    classes = class_result.scalars().all()
    class_map = {cls.name.strip().lower(): cls for cls in classes}
    for index, row in enumerate(rows, start=1):
        name = str(row.get("full_name") or "").strip()
        email = str(row.get("email") or "").strip().lower()
        password = str(row.get("password") or "Student123!").strip()
        class_name = str(row.get("class_name") or "").strip()
        if name and not email:
            email = re.sub(r"[^a-zA-Z0-9]", ".", name.lower()).strip(".") + "@example.com"
        if not name or not email:
            errors.append(f"Row {index}: missing name or email")
            continue
        existing_result = await session.execute(select(User).where(User.email == email))
        if existing_result.scalar_one_or_none() is not None:
            errors.append(f"Row {index}: email {email} already exists")
            continue
        student = User(
            tenant_id=tenant_uuid,
            email=email,
            full_name=name,
            role="student",
            hashed_password=pwd_context.hash(password),
            is_active=True,
        )
        session.add(student)
        await session.commit()
        await session.refresh(student)
        if class_name:
            target_class = class_map.get(class_name.strip().lower())
            if target_class is not None:
                session.add(Enrollment(tenant_id=tenant_uuid, student_id=student.id, class_id=target_class.id))
                await session.commit()
        created += 1
    summary = f"Imported {created} student{'s' if created != 1 else ''}."
    if errors:
        summary += f" {len(errors)} row{'s' if len(errors) != 1 else ''} were skipped."
    return {"summary": summary, "created": created, "errors": errors[:10], "tool": "admin_student_import"}


async def _apply_teacher_attendance_import(session: AsyncSession, request: MascotMessageRequest, action: dict[str, Any]) -> dict[str, Any]:
    tenant_uuid = _safe_uuid(request.tenant_id)
    class_uuid = _safe_uuid(action.get("class_id"))
    attendance_date = _parse_date_hint(action.get("date"))
    if tenant_uuid is None or class_uuid is None or attendance_date is None:
        return {"summary": "Attendance import is missing class or date context.", "imported": 0, "errors": ["missing_context"], "tool": "teacher_attendance_import"}
    if not await _teacher_can_access_class(session, request, class_uuid):
        return {"summary": "That class is outside your allowed teaching scope.", "imported": 0, "errors": ["forbidden_scope"], "tool": "teacher_attendance_import", "forbidden": True}
    rows = [dict(item) for item in action.get("rows", []) if isinstance(item, dict)]
    imported = 0
    errors: list[str] = []
    for index, row in enumerate(rows, start=1):
        identifier = str(row.get("identifier") or "").strip()
        status = str(row.get("status") or "").strip().lower()
        if status not in {"present", "absent", "late"}:
            errors.append(f"Row {index}: invalid status '{status}'")
            continue
        student_uuid = await _resolve_student_identifier_in_class_async(session, request, identifier, class_uuid)
        if student_uuid is None:
            errors.append(f"Row {index}: student {identifier} not in class")
            continue
        existing_result = await session.execute(
            select(Attendance).where(
                Attendance.tenant_id == tenant_uuid,
                Attendance.student_id == student_uuid,
                Attendance.class_id == class_uuid,
                Attendance.date == attendance_date,
            )
        )
        existing = existing_result.scalar_one_or_none()
        if existing is not None:
            existing.status = status
        else:
            session.add(
                Attendance(
                    tenant_id=tenant_uuid,
                    student_id=student_uuid,
                    class_id=class_uuid,
                    date=attendance_date,
                    status=status,
                )
            )
        imported += 1
    await session.commit()
    summary = f"Imported {imported} attendance row{'s' if imported != 1 else ''}."
    if errors:
        summary += f" {len(errors)} row{'s' if len(errors) != 1 else ''} still need manual cleanup."
    return {"summary": summary, "imported": imported, "errors": errors[:10], "tool": "teacher_attendance_import"}


async def _apply_teacher_marks_import(session: AsyncSession, request: MascotMessageRequest, action: dict[str, Any]) -> dict[str, Any]:
    tenant_uuid = _safe_uuid(request.tenant_id)
    subject_uuid = _safe_uuid(action.get("subject_id"))
    class_uuid = _safe_uuid(action.get("class_id"))
    if tenant_uuid is None or subject_uuid is None or class_uuid is None:
        return {"summary": "Marks import is missing subject or class context.", "imported": 0, "errors": ["missing_context"], "tool": "teacher_marks_import"}
    if not await _teacher_can_access_class(session, request, class_uuid) or not await _teacher_can_access_subject(session, request, subject_uuid):
        return {"summary": "That subject or class is outside your allowed teaching scope.", "imported": 0, "errors": ["forbidden_scope"], "tool": "teacher_marks_import", "forbidden": True}
    max_marks = _parse_int_hint(action.get("max_marks"))
    if max_marks is None or max_marks <= 0:
        return {"summary": "Marks import is missing valid max marks.", "imported": 0, "errors": ["invalid_max_marks"], "tool": "teacher_marks_import"}
    exam = Exam(
        tenant_id=tenant_uuid,
        name=str(action.get("exam_name") or "Imported Exam")[:150],
        subject_id=subject_uuid,
        max_marks=max_marks,
        exam_date=_parse_date_hint(action.get("exam_date")),
    )
    session.add(exam)
    await session.commit()
    await session.refresh(exam)
    rows = [dict(item) for item in action.get("rows", []) if isinstance(item, dict)]
    imported = 0
    errors: list[str] = []
    for index, row in enumerate(rows, start=1):
        identifier = str(row.get("identifier") or "").strip()
        marks_value = _parse_int_hint(row.get("marks_obtained"))
        if marks_value is None or marks_value < 0 or marks_value > max_marks:
            errors.append(f"Row {index}: marks out of range [0, {max_marks}]")
            continue
        student_uuid = await _resolve_student_identifier_in_class_async(session, request, identifier, class_uuid)
        if student_uuid is None:
            errors.append(f"Row {index}: student {identifier} not in class")
            continue
        existing_result = await session.execute(
            select(Mark).where(
                Mark.tenant_id == tenant_uuid,
                Mark.exam_id == exam.id,
                Mark.student_id == student_uuid,
            )
        )
        existing = existing_result.scalar_one_or_none()
        if existing is not None:
            existing.marks_obtained = marks_value
        else:
            session.add(
                Mark(
                    tenant_id=tenant_uuid,
                    student_id=student_uuid,
                    exam_id=exam.id,
                    marks_obtained=marks_value,
                )
            )
        imported += 1
    await session.commit()
    summary = f"Imported {imported} marks row{'s' if imported != 1 else ''} for {exam.name}."
    if errors:
        summary += f" {len(errors)} row{'s' if len(errors) != 1 else ''} still need manual cleanup."
    return {"summary": summary, "imported": imported, "errors": errors[:10], "tool": "teacher_marks_import", "exam_id": str(exam.id), "exam_name": exam.name}

async def _build_teacher_insights(session: AsyncSession, request: MascotMessageRequest, class_ids: list[UUID]) -> dict[str, Any]:
    tenant_uuid = _safe_uuid(request.tenant_id)
    if tenant_uuid is None or not class_ids:
        return {"summary": "No class insight data is available yet.", "insights": []}
    result = await session.execute(select(Class).where(Class.tenant_id == tenant_uuid, Class.id.in_(class_ids)))
    classes = result.scalars().all()
    insights: list[dict[str, Any]] = []
    for cls in classes:
        subject_result = await session.execute(select(Subject).where(Subject.tenant_id == tenant_uuid, Subject.class_id == cls.id))
        subjects = subject_result.scalars().all()
        subject_stats: list[dict[str, Any]] = []
        for subject in subjects:
            exam_result = await session.execute(select(Exam).where(Exam.tenant_id == tenant_uuid, Exam.subject_id == subject.id))
            exams = exam_result.scalars().all()
            if not exams:
                continue
            exam_ids = [exam.id for exam in exams]
            average_result = await session.execute(
                select(func.avg(Mark.marks_obtained)).where(Mark.tenant_id == tenant_uuid, Mark.exam_id.in_(exam_ids))
            )
            average = average_result.scalar()
            max_marks = max(exam.max_marks for exam in exams)
            pct = round(float(average) / max_marks * 100) if average and max_marks else 0
            subject_stats.append({"subject": subject.name, "avg_pct": pct, "is_weak": pct < 60})
        weak_topics = [item["subject"] for item in subject_stats if item["is_weak"]]
        insights.append(
            {
                "class": cls.name,
                "subjects": subject_stats,
                "weak_topics": weak_topics,
                "recommendation": f"Focus on: {', '.join(weak_topics)}" if weak_topics else "All subjects performing well",
            }
        )
    if not insights:
        return {"summary": "No marked exams are available yet to build class insights.", "insights": []}
    highlights = []
    for item in insights[:3]:
        if item["weak_topics"]:
            highlights.append(f"{item['class']} needs focus on {', '.join(item['weak_topics'][:2])}.")
        else:
            highlights.append(f"{item['class']} is performing steadily.")
    return {"summary": " ".join(highlights), "insights": insights}


async def _build_teacher_doubt_heatmap(session: AsyncSession, request: MascotMessageRequest, class_ids: list[UUID]) -> dict[str, Any]:
    tenant_uuid = _safe_uuid(request.tenant_id)
    if tenant_uuid is None or not class_ids:
        return {"summary": "No doubt heatmap data is available yet.", "heatmap": [], "top_topics": []}
    enrollment_result = await session.execute(
        select(Enrollment.student_id).where(Enrollment.tenant_id == tenant_uuid, Enrollment.class_id.in_(class_ids))
    )
    student_ids = list({student_id for student_id in enrollment_result.scalars().all() if student_id})
    if not student_ids:
        return {"summary": "No enrolled students were found for your classes yet.", "heatmap": [], "top_topics": []}
    query_result = await session.execute(
        select(AIQuery).where(AIQuery.tenant_id == tenant_uuid, AIQuery.user_id.in_(student_ids)).order_by(AIQuery.created_at.desc()).limit(500)
    )
    queries = query_result.scalars().all()
    if not queries:
        return {"summary": "Students have not generated enough AI queries yet for a doubt heatmap.", "heatmap": [], "top_topics": []}
    class_result = await session.execute(select(Class).where(Class.tenant_id == tenant_uuid, Class.id.in_(class_ids)))
    classes = {item.id: item.name for item in class_result.scalars().all()}
    subject_result = await session.execute(select(Subject).where(Subject.tenant_id == tenant_uuid, Subject.class_id.in_(class_ids)))
    subjects = subject_result.scalars().all()
    subject_map = {subject.id: {"subject": subject.name, "class": classes.get(subject.class_id, "Unknown")} for subject in subjects}
    topic_counter: Counter[str] = Counter()
    subject_counter: Counter[str] = Counter()
    queries_by_subject: dict[str, list[str]] = {}
    for query in queries:
        topic = (query.query_text or "Unknown").strip()[:60] or "Unknown"
        topic_counter[topic] += 1
        lowered_query = (query.query_text or "").lower()
        for info in subject_map.values():
            subject_name = info["subject"]
            key = f"{info['class']} - {subject_name}"
            if subject_name.lower() in lowered_query:
                subject_counter[key] += 1
                queries_by_subject.setdefault(key, []).append(topic)
                break
    heatmap = [
        {
            "label": label,
            "query_count": count,
            "intensity": min(1.0, count / max(1, len(queries)) * 10),
            "sample_topics": list(dict.fromkeys(queries_by_subject.get(label, [])))[:5],
        }
        for label, count in subject_counter.most_common(5)
    ]
    top_topics = [{"topic": topic, "count": count} for topic, count in topic_counter.most_common(5)]
    summary_parts = []
    if heatmap:
        hottest = heatmap[0]
        summary_parts.append(f"Highest doubt activity is in {hottest['label']} with {hottest['query_count']} recent AI queries.")
    if top_topics:
        summary_parts.append(f"Top query themes: {', '.join(item['topic'] for item in top_topics[:3])}.")
    return {
        "summary": " ".join(summary_parts) or "No doubt heatmap data is available yet.",
        "heatmap": heatmap,
        "top_topics": top_topics,
        "total_queries": len(queries),
        "student_count": len(student_ids),
    }


async def _build_parent_progress_report(session: AsyncSession, request: MascotMessageRequest) -> dict[str, Any]:
    tenant_uuid = _safe_uuid(request.tenant_id)
    parent_uuid = _safe_uuid(request.user_id)
    if tenant_uuid is None or parent_uuid is None:
        return {"summary": "Parent progress data is not available.", "child": None}
    link_result = await session.execute(
        select(ParentLink).where(ParentLink.tenant_id == tenant_uuid, ParentLink.parent_id == parent_uuid).order_by(ParentLink.created_at.asc())
    )
    link = link_result.scalars().first()
    if link is None:
        return {"summary": "No linked child was found for this parent account.", "child": None}
    child_result = await session.execute(
        select(User).where(User.id == link.child_id, User.tenant_id == tenant_uuid, User.role == "student", User.is_active.is_(True))
    )
    child = child_result.scalars().first()
    if child is None:
        return {"summary": "The linked child record is no longer available.", "child": None}
    attendance_result = await session.execute(
        select(Attendance).where(Attendance.tenant_id == tenant_uuid, Attendance.student_id == child.id).order_by(Attendance.date.desc()).limit(30)
    )
    attendance = attendance_result.scalars().all()
    total_attendance = len(attendance)
    present_attendance = sum(1 for item in attendance if item.status == "present")
    attendance_pct = round((present_attendance / total_attendance * 100) if total_attendance else 0)
    marks_result = await session.execute(
        select(Mark, Exam, Subject)
        .join(Exam, Mark.exam_id == Exam.id)
        .join(Subject, Exam.subject_id == Subject.id)
        .where(Mark.tenant_id == tenant_uuid, Mark.student_id == child.id, Subject.tenant_id == tenant_uuid)
    )
    rows = marks_result.all()
    subject_stats: dict[str, dict[str, Any]] = {}
    for mark, exam, subject in rows:
        item = subject_stats.setdefault(subject.name, {"name": subject.name, "scores": []})
        pct = round(mark.marks_obtained / exam.max_marks * 100) if exam.max_marks else 0
        item["scores"].append(pct)
    results = []
    weak_subjects = []
    for item in subject_stats.values():
        average = round(sum(item["scores"]) / len(item["scores"])) if item["scores"] else 0
        results.append({"name": item["name"], "avg": average})
        if average < 60:
            weak_subjects.append(item["name"])
    results.sort(key=lambda item: item["name"])
    summary_parts = [f"{child.full_name}'s attendance is {attendance_pct}% over the last 30 records."]
    if results:
        strongest = max(results, key=lambda item: item["avg"])
        summary_parts.append(f"Strongest subject: {strongest['name']} at {strongest['avg']}%.")
    if weak_subjects:
        summary_parts.append(f"Attention is needed in {', '.join(weak_subjects[:3])}.")
    else:
        summary_parts.append("No weak subjects are currently flagged.")
    return {
        "summary": " ".join(summary_parts),
        "child": {"id": str(child.id), "name": child.full_name},
        "attendance_pct_30d": attendance_pct,
        "results": results,
        "weak_subjects": weak_subjects,
    }


async def _build_admin_onboarding_report(session: AsyncSession, request: MascotMessageRequest) -> dict[str, Any]:
    tenant_uuid = _safe_uuid(request.tenant_id)
    if tenant_uuid is None:
        return {"summary": "Onboarding status is unavailable.", "counts": {}}
    class_count = (await session.execute(select(func.count()).select_from(Class).where(Class.tenant_id == tenant_uuid))).scalar() or 0
    teacher_count = (
        await session.execute(
            select(func.count()).select_from(User).where(
                User.tenant_id == tenant_uuid,
                User.role == "teacher",
                User.is_active.is_(True),
            )
        )
    ).scalar() or 0
    student_count = (
        await session.execute(
            select(func.count()).select_from(User).where(
                User.tenant_id == tenant_uuid,
                User.role == "student",
                User.is_active.is_(True),
            )
        )
    ).scalar() or 0
    timetable_count = (await session.execute(select(func.count()).select_from(Timetable).where(Timetable.tenant_id == tenant_uuid))).scalar() or 0
    if class_count == 0:
        next_step = "Add classes in the setup wizard first."
    elif teacher_count == 0:
        next_step = "Import teachers next."
    elif student_count == 0:
        next_step = "Import students next."
    elif timetable_count == 0:
        next_step = "Set up the timetable to complete onboarding."
    else:
        next_step = "Core onboarding is complete. Review users and queue health."
    summary = f"Setup progress: {class_count} classes, {teacher_count} teachers, {student_count} students, and {timetable_count} timetable slots configured. {next_step}"
    return {
        "summary": summary,
        "counts": {
            "classes": int(class_count),
            "teachers": int(teacher_count),
            "students": int(student_count),
            "timetable_slots": int(timetable_count),
        },
        "next_step": next_step,
    }


async def _build_admin_ai_review_report(session: AsyncSession, request: MascotMessageRequest) -> dict[str, Any]:
    tenant_uuid = _safe_uuid(request.tenant_id)
    if tenant_uuid is None:
        return {"summary": "AI review status is unavailable.", "pending": 0}
    query_result = await session.execute(
        select(AIQuery).where(AIQuery.tenant_id == tenant_uuid).order_by(AIQuery.created_at.desc()).limit(50)
    )
    queries = query_result.scalars().all()
    if not queries:
        return {"summary": "No AI responses have been generated yet for review.", "pending": 0, "approved": 0, "flagged": 0}
    query_ids = [query.id for query in queries]
    audit_result = await session.execute(
        select(AuditLog).where(
            AuditLog.tenant_id == tenant_uuid,
            AuditLog.entity_type == "ai_review",
            AuditLog.entity_id.in_(query_ids),
        ).order_by(AuditLog.created_at.desc())
    )
    latest_status: dict[UUID, str] = {}
    for row in audit_result.scalars().all():
        if row.entity_id in latest_status:
            continue
        latest_status[row.entity_id] = _review_status_from_action(row.action)
    approved = sum(1 for query in queries if latest_status.get(query.id) == "approved")
    flagged = sum(1 for query in queries if latest_status.get(query.id) == "flagged")
    pending = len(queries) - approved - flagged
    summary = f"AI review queue: {pending} pending, {approved} approved, {flagged} flagged across the latest {len(queries)} responses."
    return {"summary": summary, "pending": pending, "approved": approved, "flagged": flagged, "sample_size": len(queries)}


def _build_admin_release_gate_report(request: MascotMessageRequest) -> dict[str, Any]:
    from src.domains.platform.services.whatsapp_gateway import get_whatsapp_metrics

    metrics = get_whatsapp_metrics(request.tenant_id)
    inbound_total = metrics.get("inbound_total", 0)
    routing_total = metrics.get("routing_success_total", 0) + metrics.get("routing_failure_total", 0)
    outbound_total = metrics.get("outbound_success_total", 0) + metrics.get("outbound_failure_total", 0)

    def _pct(numerator: int, denominator: int) -> float:
        if denominator <= 0:
            return 0.0
        return round((numerator / denominator) * 100, 2)

    derived_rates = {
        "routing_failure_pct": _pct(metrics.get("routing_failure_total", 0), routing_total),
        "duplicate_inbound_pct": _pct(metrics.get("duplicate_inbound_total", 0), inbound_total),
        "visible_failure_pct": _pct(metrics.get("visible_failure_total", 0), inbound_total),
        "outbound_retryable_failure_pct": _pct(metrics.get("outbound_retryable_failure_total", 0), outbound_total),
    }
    summary = (
        f"WhatsApp release gate snapshot: routing failure {derived_rates['routing_failure_pct']}%, "
        f"duplicate inbound {derived_rates['duplicate_inbound_pct']}%, visible failure {derived_rates['visible_failure_pct']}%."
    )
    return {"summary": summary, "release_gate_metrics": metrics, "derived_rates": derived_rates}


def _chunk_payloads(chunks: list[Any]) -> list[dict[str, Any]]:
    return [
        {
            "text": chunk.text,
            "document_id": chunk.document_id,
            "page_number": chunk.page_number,
            "section_title": chunk.section_title or "",
            "subject_id": chunk.subject_id or "",
            "notebook_id": chunk.notebook_id or "",
            "source_file": chunk.source_file or "",
        }
        for chunk in chunks
    ]


async def handle_mascot_upload(
    *,
    request: MascotMessageRequest,
    session: AsyncSession,
    filename: str,
    content: bytes,
) -> MascotMessageResponse:
    upload_started_at = time.perf_counter()
    safe_filename = Path(filename or "").name
    if not safe_filename:
        raise ValueError("Filename is required.")

    structured_import_intent = _structured_import_intent(request, safe_filename)
    allowed_extensions, max_file_size = _upload_constraints(request.role)
    extension = safe_filename.rsplit(".", 1)[-1].lower() if "." in safe_filename else ""
    if extension not in allowed_extensions and not structured_import_intent:
        raise ValueError(f"Only {', '.join(sorted(allowed_extensions))} files are supported in the mascot.")

    display_name = safe_filename
    macros_removed = False
    ocr_processed = False
    ocr_review_required = False
    ocr_warning: str | None = None
    ocr_languages: list[str] = []
    ocr_preprocessing: list[str] = []
    ocr_confidence: float | None = None

    if extension == "docx":
        try:
            content, macros_removed = sanitize_docx_bytes(content)
        except UploadValidationError as exc:
            raise ValueError(str(exc)) from exc

    if len(content) > max_file_size:
        raise ValueError(f"File exceeds {max_file_size // (1024 * 1024)}MB limit.")

    if structured_import_intent:
        if structured_import_intent == "teacher_roster_import":
            prepared_import = await _prepare_teacher_roster_import(session, request, display_name, content)
        elif structured_import_intent == "admin_teacher_import":
            prepared_import = await _prepare_admin_teacher_import(session, request, display_name, content)
        elif structured_import_intent == "admin_student_import":
            prepared_import = await _prepare_admin_student_import(session, request, display_name, content)
        elif structured_import_intent == "teacher_attendance_import":
            prepared_import = await _prepare_teacher_attendance_import(session, request, display_name, content)
        else:
            prepared_import = await _prepare_teacher_marks_import(session, request, display_name, content)

        pending = PendingMascotAction(
            kind="structured_import",
            channel=request.channel,
            tenant_id=request.tenant_id or "",
            user_id=request.user_id or "",
            role=request.role or "teacher",
            payload={
                **prepared_import,
                "message": request.message or f"Import {prepared_import['intent']}",
                "translated_message": request.message or f"Import {prepared_import['intent']}",
            },
            notebook_id=request.notebook_id,
            session_id=request.session_id,
        )
        store_pending_action(pending)
        _store_session(request, notebook_id=request.notebook_id, intent=prepared_import["intent"], navigation=None)
        response = MascotMessageResponse(
            reply_text=f"{prepared_import['result_summary']}\n\nPlease confirm before I import these records.",
            intent=prepared_import["intent"],
            normalized_message=request.message or prepared_import["intent"],
            translated_message=request.message or None,
            actions=[
                MascotAction(
                    kind="structured_import",
                    status="pending_confirmation",
                    payload={
                        "intent": prepared_import["intent"],
                        "filename": prepared_import["filename"],
                        "total_rows": len(prepared_import.get("rows", [])),
                    },
                    result_summary="Confirmation required before these records are saved.",
                )
            ],
            artifacts=[prepared_import["artifact"]],
            requires_confirmation=True,
            confirmation_id=pending.confirmation_id,
            follow_up_suggestions=_follow_ups(prepared_import["intent"]),
            notebook_id=request.notebook_id,
            trace_id=f"mascot-{uuid4().hex[:8]}",
        )
        _record_mascot_stage(trace_id=response.trace_id, tenant_id=request.tenant_id, user_id=request.user_id, stage="mascot", operation="upload", started_at=upload_started_at, outcome="success", metadata={"intent": prepared_import["intent"], "requires_confirmation": True})
        await _append_mascot_audit_log(session, request=request, trace_id=response.trace_id, action="mascot.upload", status="success", metadata={"intent": prepared_import["intent"], "requires_confirmation": True, "filename": display_name})
        await session.commit()
        return response

    if extension in {"jpg", "jpeg", "png"}:
        from src.infrastructure.vector_store.ocr_service import image_bytes_to_pdf, validate_image_size

        try:
            validate_image_size(content)
        except ValueError as exc:
            raise ValueError(str(exc)) from exc

        generated_name = f"{request.tenant_id}_{request.user_id}_{uuid4().hex}_ocr.pdf"
        file_path = _MASCOT_OCR_DIR / generated_name
        try:
            ocr_result = image_bytes_to_pdf(
                content,
                str(file_path),
                suffix=f".{extension}",
                title=display_name,
                source_name=display_name,
            )
        except Exception as exc:
            logger.exception("Mascot OCR upload failed")
            _record_mascot_stage(trace_id=None, tenant_id=request.tenant_id, user_id=request.user_id, stage="mascot", operation="upload", started_at=upload_started_at, outcome="error", metadata={"phase": "ocr", "filename": display_name})
            raise ValueError("OCR processing failed. Please upload a clearer image or a PDF.") from exc
        safe_filename = generated_name
        extension = "pdf"
        ocr_processed = True
        ocr_review_required = ocr_result.review_required
        ocr_warning = ocr_result.warning
        ocr_languages = list(ocr_result.languages)
        ocr_preprocessing = list(ocr_result.preprocessing_applied)
        ocr_confidence = getattr(ocr_result, "confidence", None)
    else:
        stored_name = f"{request.tenant_id}_{request.user_id}_{uuid4().hex}_{safe_filename}"
        file_path = _MASCOT_UPLOAD_DIR / stored_name
        with open(file_path, "wb") as handle:
            handle.write(content)

    active_notebook = await _resolve_notebook(session, request, _notebook_name(request.message))
    if _explicit_notebook_target(request) and active_notebook is None:
        raise ValueError("I can't access that notebook from your account.")
    document = Document(
        tenant_id=_safe_uuid(request.tenant_id),
        notebook_id=active_notebook.id if active_notebook else None,
        uploaded_by=_safe_uuid(request.user_id),
        file_name=safe_filename,
        file_type=extension,
        storage_path=str(file_path),
        ingestion_status="processing",
    )
    session.add(document)
    await session.commit()
    await session.refresh(document)

    chunk_count = 0
    try:
        from src.infrastructure.llm.cache import invalidate_tenant_cache
        from src.infrastructure.llm.providers import get_embedding_provider, get_vector_store_provider
        from src.infrastructure.vector_store.ingestion import ingest_document

        chunks = ingest_document(
            file_path=str(file_path),
            document_id=str(document.id),
            tenant_id=request.tenant_id or "",
            notebook_id=str(active_notebook.id) if active_notebook else None,
        )
        if chunks:
            embeddings = await get_embedding_provider().embed_batch([chunk.text for chunk in chunks])
            get_vector_store_provider(request.tenant_id or "").add_chunks(_chunk_payloads(chunks), embeddings)
            chunk_count = len(chunks)
        invalidate_tenant_cache(request.tenant_id or "")
        document.ingestion_status = "completed"
        document.chunk_count = chunk_count
        await session.commit()
    except Exception as exc:
        logger.exception("Mascot document ingestion failed", extra={"document_id": str(document.id)})
        document.ingestion_status = "failed"
        await session.commit()
        _record_mascot_stage(trace_id=None, tenant_id=request.tenant_id, user_id=request.user_id, stage="mascot", operation="upload", started_at=upload_started_at, outcome="error", metadata={"phase": "ingestion", "filename": display_name, "document_id": str(document.id)})
        await _append_mascot_audit_log(session, request=request, trace_id=f"mascot-{uuid4().hex[:8]}", action="mascot.upload", status="error", metadata={"phase": "ingestion", "filename": display_name, "document_id": str(document.id)})
        await session.commit()
        raise ValueError("Document ingestion failed.") from exc

    notebook_id = str(active_notebook.id) if active_notebook else request.notebook_id
    notebook_label = active_notebook.name if active_notebook else "your workspace"
    summary_parts = [f"Ingested {display_name} into {notebook_label}."]
    if chunk_count:
        summary_parts.append(f"Indexed {chunk_count} chunks.")
    if macros_removed:
        summary_parts.append("Unsafe DOCX macros were removed.")
    if ocr_processed:
        if isinstance(ocr_confidence, (int, float)):
            summary_parts.append(f"OCR confidence {(float(ocr_confidence) * 100):.0f}%.")
        if ocr_warning:
            summary_parts.append(ocr_warning)

    upload_action = MascotAction(
        kind="ocr_ingest" if ocr_processed else "content_ingest",
        status="completed",
        payload={
            "document_id": str(document.id),
            "file_name": display_name,
            "stored_file_name": safe_filename,
            "file_type": extension,
            "chunks": chunk_count,
            "ocr_processed": ocr_processed,
            "ocr_review_required": ocr_review_required,
            "ocr_warning": ocr_warning,
            "ocr_confidence": ocr_confidence,
        },
        result_summary=" ".join(summary_parts),
    )
    upload_artifact = {
        "document_id": str(document.id),
        "file_name": display_name,
        "file_type": extension,
        "chunks": chunk_count,
        "ocr_processed": ocr_processed,
        "ocr_review_required": ocr_review_required,
        "ocr_warning": ocr_warning,
        "ocr_languages": ocr_languages,
        "ocr_preprocessing": ocr_preprocessing,
        "ocr_confidence": ocr_confidence,
    }

    if request.message.strip():
        follow_up_request = MascotMessageRequest(
            message=request.message,
            channel=request.channel,
            role=request.role,
            tenant_id=request.tenant_id,
            user_id=request.user_id,
            notebook_id=notebook_id,
            session_id=request.session_id,
            conversation_history=request.conversation_history,
            attachments=request.attachments,
            ui_context=request.ui_context,
        )
        follow_up_response = await handle_mascot_message(follow_up_request, session)
        reply_text = " ".join(summary_parts)
        if follow_up_response.reply_text:
            reply_text = f"{reply_text}\n\n{follow_up_response.reply_text}"
        response = MascotMessageResponse(
            reply_text=reply_text,
            intent=follow_up_response.intent,
            normalized_message=follow_up_response.normalized_message,
            translated_message=follow_up_response.translated_message,
            actions=[upload_action, *follow_up_response.actions],
            artifacts=[upload_artifact, *follow_up_response.artifacts],
            navigation=follow_up_response.navigation,
            requires_confirmation=follow_up_response.requires_confirmation,
            confirmation_id=follow_up_response.confirmation_id,
            follow_up_suggestions=follow_up_response.follow_up_suggestions,
            notebook_id=follow_up_response.notebook_id or notebook_id,
            trace_id=follow_up_response.trace_id,
        )
        _record_mascot_stage(trace_id=response.trace_id, tenant_id=request.tenant_id, user_id=request.user_id, stage="mascot", operation="upload", started_at=upload_started_at, outcome="success", metadata={"intent": response.intent, "filename": display_name, "ocr_processed": ocr_processed})
        await _append_mascot_audit_log(session, request=request, trace_id=response.trace_id, action="mascot.upload", status="success", metadata={"intent": response.intent, "filename": display_name, "ocr_processed": ocr_processed, "chunks": chunk_count})
        await session.commit()
        return response

    trace_id = f"mascot-{uuid4().hex[:8]}"
    _store_session(request, notebook_id=notebook_id, intent="content_ingest", navigation=None)
    response = MascotMessageResponse(
        reply_text=" ".join(summary_parts),
        intent="content_ingest",
        normalized_message=request.message or "upload",
        actions=[upload_action],
        artifacts=[upload_artifact],
        follow_up_suggestions=[
            "Summarize this upload",
            "Generate flashcards from this notebook",
            "Create a flowchart from this upload",
        ],
        notebook_id=notebook_id,
        trace_id=trace_id,
    )
    _record_mascot_stage(trace_id=trace_id, tenant_id=request.tenant_id, user_id=request.user_id, stage="mascot", operation="upload", started_at=upload_started_at, outcome="success", metadata={"intent": "content_ingest", "filename": display_name, "ocr_processed": ocr_processed})
    await _append_mascot_audit_log(session, request=request, trace_id=trace_id, action="mascot.upload", status="success", metadata={"intent": "content_ingest", "filename": display_name, "ocr_processed": ocr_processed, "chunks": chunk_count})
    await session.commit()
    return response


def get_mascot_suggestions(
    *,
    role: str,
    current_route: str | None,
    notebook_id: str | None,
    current_page_entity: str | None = None,
) -> list[str]:
    route = (current_route or "").lower()
    entity = (current_page_entity or "").lower()
    if notebook_id:
        if role == "teacher":
            return ["Generate assessment for this notebook", "Create a quiz from this notebook", "Open this notebook in AI Studio"]
        return ["Generate flashcards from this notebook", "Create a flowchart from this notebook", "Open this notebook in AI Studio"]
    if "upload" in route:
        if role == "teacher":
            return ["Add this upload to class knowledge", "Summarize my latest upload", "Generate assessment from this upload"]
        return ["Create a notebook for these uploads", "Summarize my latest upload", "Generate flashcards from this upload"]
    if entity == "student_onboarding" or "teacher/classes" in route:
        return ["Import student roster from image", "Review extracted student rows", "Generate a Biology assessment"]
    if entity == "class" or "attendance" in route:
        return ["Import attendance from image", "Review OCR attendance rows", "Summarize this class attendance"]
    if entity == "subject" or "marks" in route or "results" in route:
        return ["Import marks from image", "Review OCR marks rows", "Generate assessment for this subject"]
    if entity == "setup_step" or "setup-wizard" in route:
        return ["Show setup progress", "Import teachers", "Import students"]
    if "setup-wizard" in route:
        return ["Show setup progress", "Import teachers", "Import students"]
    if "ai-review" in route:
        return ["Show AI review summary", "Open dashboard", "Review WhatsApp release gate"]
    defaults = {
        "student": ["Create a Biology notebook", "Open AI Studio", "Generate flashcards for photosynthesis"],
        "teacher": ["Show class insights", "Generate a Biology assessment", "Import attendance from image"],
        "parent": ["Show attendance", "Open reports", "Show my child report"],
        "admin": ["Show setup progress", "Show WhatsApp health", "Open setup wizard"],
    }
    return defaults.get(role, ["Open assistant", "Create a notebook", "Ask a question"])


def get_mascot_session(*, channel: str, user_id: str, session_id: str | None = None) -> dict:
    return load_session(build_session_id(channel=channel, user_id=user_id, provided=session_id))


def clear_mascot_session(*, channel: str, user_id: str, session_id: str | None = None) -> None:
    clear_session(build_session_id(channel=channel, user_id=user_id, provided=session_id))
