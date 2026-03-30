"""Shared mascot request/response schemas for web and WhatsApp orchestration."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field


MascotChannel = Literal["web", "whatsapp"]
MascotActionKind = Literal[
    "query",
    "study_tool",
    "notebook_create",
    "notebook_update",
    "content_ingest",
    "ocr_ingest",
    "structured_import",
    "navigate",
    "generated_content_save",
    "clarify",
    "confirm",
]
MascotActionStatus = Literal["planned", "completed", "failed", "needs_input", "pending_confirmation"]


class MascotAttachment(BaseModel):
    kind: Literal["url", "youtube", "file", "image", "audio", "video"] = "url"
    url: str | None = None
    label: str | None = None
    content_type: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class MascotUIContext(BaseModel):
    current_route: str | None = None
    selected_notebook_id: str | None = None
    current_page_entity: str | None = None
    current_page_entity_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class MascotAction(BaseModel):
    kind: MascotActionKind
    status: MascotActionStatus = "planned"
    payload: dict[str, Any] = Field(default_factory=dict)
    result_summary: str | None = None


class PendingMascotAction(BaseModel):
    confirmation_id: str = Field(default_factory=lambda: f"mascot-confirm-{uuid4().hex[:12]}")
    kind: MascotActionKind
    channel: MascotChannel
    tenant_id: str
    user_id: str
    role: str
    payload: dict[str, Any] = Field(default_factory=dict)
    notebook_id: str | None = None
    session_id: str | None = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class MascotMessageRequest(BaseModel):
    message: str
    channel: MascotChannel = "web"
    role: str | None = None
    tenant_id: str | None = None
    user_id: str | None = None
    notebook_id: str | None = None
    session_id: str | None = None
    conversation_history: list[dict[str, Any]] = Field(default_factory=list)
    attachments: list[MascotAttachment] = Field(default_factory=list)
    ui_context: MascotUIContext | None = None


class MascotMessageResponse(BaseModel):
    reply_text: str
    intent: str
    normalized_message: str
    translated_message: str | None = None
    actions: list[MascotAction] = Field(default_factory=list)
    artifacts: list[dict[str, Any]] = Field(default_factory=list)
    navigation: dict[str, Any] | None = None
    requires_confirmation: bool = False
    confirmation_id: str | None = None
    follow_up_suggestions: list[str] = Field(default_factory=list)
    notebook_id: str | None = None
    trace_id: str


class MascotConfirmRequest(BaseModel):
    confirmation_id: str
    approved: bool = True
    channel: MascotChannel = "web"
    session_id: str | None = None
