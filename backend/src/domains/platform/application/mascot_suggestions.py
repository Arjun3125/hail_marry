"""Application helpers for mascot suggestion APIs."""

from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.domains.platform.services.learner_profile_service import get_learner_profile_dict
from src.domains.platform.services.mastery_tracking_service import build_profile_aware_recommendations


def build_student_mascot_suggestions(
    *,
    db: Session,
    tenant_id,
    user_id,
    current_route: str | None,
    notebook_id: str | None,
) -> list[str]:
    notebook_uuid: UUID | None = None
    if notebook_id:
        try:
            notebook_uuid = UUID(str(notebook_id))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid notebook_id") from exc

    route = (current_route or "").lower()
    if "ai-studio" in route:
        current_surface = "ai_studio"
    elif "overview" in route:
        current_surface = "overview"
    elif "assistant" in route:
        current_surface = "assistant"
    elif "upload" in route:
        current_surface = "upload"
    else:
        current_surface = None

    learner_profile = get_learner_profile_dict(
        db,
        tenant_id=tenant_id,
        user_id=user_id,
    )
    items = build_profile_aware_recommendations(
        db,
        tenant_id=tenant_id,
        user_id=user_id,
        notebook_id=notebook_uuid,
        current_surface=current_surface,
        learner_profile=learner_profile,
    )
    db.commit()
    return [
        str(item.get("label") or item.get("prompt") or "")
        for item in items[:4]
        if item.get("label") or item.get("prompt")
    ]
