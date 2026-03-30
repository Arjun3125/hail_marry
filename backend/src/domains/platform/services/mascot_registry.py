"""Canonical mascot capability metadata."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from src.domains.platform.services.mascot_schemas import MascotActionKind, MascotChannel


MascotRiskLevel = Literal["low", "high"]


@dataclass(frozen=True)
class MascotCapability:
    key: str
    kind: MascotActionKind
    roles: tuple[str, ...]
    channels: tuple[MascotChannel, ...]
    risk: MascotRiskLevel = "low"
    description: str = ""


MASCOT_CAPABILITIES: dict[str, MascotCapability] = {
    "ask_ai_question": MascotCapability(
        key="ask_ai_question",
        kind="query",
        roles=("student", "teacher", "parent", "admin"),
        channels=("web", "whatsapp"),
        description="Grounded question answering through the shared AI query stack.",
    ),
    "study_guide": MascotCapability(
        key="study_guide",
        kind="query",
        roles=("student", "teacher", "parent", "admin"),
        channels=("web", "whatsapp"),
        description="Grounded study-guide generation.",
    ),
    "socratic": MascotCapability(
        key="socratic",
        kind="query",
        roles=("student", "teacher", "parent", "admin"),
        channels=("web", "whatsapp"),
        description="Socratic tutoring with grounded context.",
    ),
    "debate": MascotCapability(
        key="debate",
        kind="query",
        roles=("student", "teacher", "parent", "admin"),
        channels=("web", "whatsapp"),
        description="Grounded debate assistance.",
    ),
    "essay_review": MascotCapability(
        key="essay_review",
        kind="query",
        roles=("student", "teacher", "parent", "admin"),
        channels=("web", "whatsapp"),
        description="Grounded essay review.",
    ),
    "quiz": MascotCapability(
        key="quiz",
        kind="study_tool",
        roles=("student", "teacher", "parent", "admin"),
        channels=("web", "whatsapp"),
        description="Quiz generation.",
    ),
    "flashcards": MascotCapability(
        key="flashcards",
        kind="study_tool",
        roles=("student", "teacher", "parent", "admin"),
        channels=("web", "whatsapp"),
        description="Flashcard generation.",
    ),
    "mindmap": MascotCapability(
        key="mindmap",
        kind="study_tool",
        roles=("student", "teacher", "parent", "admin"),
        channels=("web", "whatsapp"),
        description="Mind map generation.",
    ),
    "flowchart": MascotCapability(
        key="flowchart",
        kind="study_tool",
        roles=("student", "teacher", "parent", "admin"),
        channels=("web", "whatsapp"),
        description="Flowchart generation.",
    ),
    "concept_map": MascotCapability(
        key="concept_map",
        kind="study_tool",
        roles=("student", "teacher", "parent", "admin"),
        channels=("web", "whatsapp"),
        description="Concept map generation.",
    ),
    "notebook_create": MascotCapability(
        key="notebook_create",
        kind="notebook_create",
        roles=("student", "teacher", "parent", "admin"),
        channels=("web", "whatsapp"),
        description="Create a notebook and switch scope.",
    ),
    "notebook_update": MascotCapability(
        key="notebook_update",
        kind="notebook_update",
        roles=("student", "teacher", "parent", "admin"),
        channels=("web", "whatsapp"),
        risk="high",
        description="Rename or archive notebooks.",
    ),
    "content_ingest": MascotCapability(
        key="content_ingest",
        kind="content_ingest",
        roles=("student", "teacher", "parent", "admin"),
        channels=("web", "whatsapp"),
        description="Ingest URL or YouTube content into the knowledge base.",
    ),
    "teacher_roster_import": MascotCapability(
        key="teacher_roster_import",
        kind="structured_import",
        roles=("teacher", "admin"),
        channels=("web",),
        risk="high",
        description="Preview and confirm OCR or CSV student roster imports.",
    ),
    "teacher_attendance_import": MascotCapability(
        key="teacher_attendance_import",
        kind="structured_import",
        roles=("teacher", "admin"),
        channels=("web",),
        risk="high",
        description="Preview and confirm OCR or CSV attendance imports.",
    ),
    "teacher_marks_import": MascotCapability(
        key="teacher_marks_import",
        kind="structured_import",
        roles=("teacher", "admin"),
        channels=("web",),
        risk="high",
        description="Preview and confirm OCR or CSV marks imports.",
    ),
    "admin_teacher_import": MascotCapability(
        key="admin_teacher_import",
        kind="structured_import",
        roles=("admin",),
        channels=("web",),
        risk="high",
        description="Preview and confirm teacher onboarding imports.",
    ),
    "admin_student_import": MascotCapability(
        key="admin_student_import",
        kind="structured_import",
        roles=("admin",),
        channels=("web",),
        risk="high",
        description="Preview and confirm student onboarding imports.",
    ),
    "teacher_insights_report": MascotCapability(
        key="teacher_insights_report",
        kind="query",
        roles=("teacher", "admin"),
        channels=("web", "whatsapp"),
        description="Summarize class weak-topic insights for teachers.",
    ),
    "teacher_doubt_heatmap_report": MascotCapability(
        key="teacher_doubt_heatmap_report",
        kind="query",
        roles=("teacher", "admin"),
        channels=("web", "whatsapp"),
        description="Summarize student doubt hotspots for teachers.",
    ),
    "teacher_assessment_generate": MascotCapability(
        key="teacher_assessment_generate",
        kind="query",
        roles=("teacher", "admin"),
        channels=("web", "whatsapp"),
        description="Generate a teacher assessment from grounded subject context.",
    ),
    "parent_progress_report": MascotCapability(
        key="parent_progress_report",
        kind="query",
        roles=("parent",),
        channels=("web", "whatsapp"),
        description="Summarize linked child attendance and performance.",
    ),
    "admin_release_gate_report": MascotCapability(
        key="admin_release_gate_report",
        kind="query",
        roles=("admin",),
        channels=("web", "whatsapp"),
        description="Summarize WhatsApp release-gate operational health.",
    ),
    "admin_onboarding_report": MascotCapability(
        key="admin_onboarding_report",
        kind="query",
        roles=("admin",),
        channels=("web", "whatsapp"),
        description="Summarize setup wizard progress and next onboarding steps.",
    ),
    "admin_ai_review_report": MascotCapability(
        key="admin_ai_review_report",
        kind="query",
        roles=("admin",),
        channels=("web", "whatsapp"),
        description="Summarize pending AI review workload and recent status.",
    ),
    "navigate": MascotCapability(
        key="navigate",
        kind="navigate",
        roles=("student", "teacher", "parent", "admin"),
        channels=("web", "whatsapp"),
        description="Navigate to a relevant page or guide the user there.",
    ),
}


def get_capability(key: str) -> MascotCapability | None:
    return MASCOT_CAPABILITIES.get(key)


def is_capability_allowed(key: str, role: str, channel: MascotChannel) -> bool:
    capability = get_capability(key)
    if capability is None:
        return False
    return role in capability.roles and channel in capability.channels


def capability_requires_confirmation(key: str) -> bool:
    capability = get_capability(key)
    if capability is None:
        return False
    return capability.risk == "high"


ROLE_ROUTE_MAP: dict[str, dict[str, str]] = {
    "student": {
        "assistant": "/student/assistant",
        "ai_studio": "/student/ai-studio",
        "upload": "/student/upload",
        "attendance": "/student/attendance",
        "marks": "/student/results",
        "overview": "/student/overview",
    },
    "teacher": {
        "assistant": "/teacher/assistant",
        "ai_studio": "/teacher/assistant",
        "upload": "/teacher/upload",
        "attendance": "/teacher/attendance",
        "marks": "/teacher/marks",
        "classes": "/teacher/classes",
    },
    "parent": {
        "assistant": "/parent/assistant",
        "overview": "/parent/dashboard",
        "attendance": "/parent/attendance",
        "reports": "/parent/reports",
    },
    "admin": {
        "assistant": "/admin/assistant",
        "overview": "/admin/dashboard",
        "onboarding": "/admin/setup-wizard",
        "dashboard": "/admin/dashboard",
        "whatsapp_release_gate": "/admin/dashboard",
    },
}


def resolve_navigation_target(role: str, target: str) -> str | None:
    return ROLE_ROUTE_MAP.get(role, {}).get(target)
