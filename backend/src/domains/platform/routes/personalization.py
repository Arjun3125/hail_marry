from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user, require_role
from database import get_db
from src.domains.identity.models.user import User
from src.domains.platform.application.personalization_queries import (
    build_completed_study_path_response as _build_completed_study_path_response_impl,
    build_personalization_profile_response as _build_personalization_profile_response_impl,
    build_personalization_metrics_summary as _build_personalization_metrics_summary_impl,
    build_personalized_recommendations_response as _build_personalized_recommendations_response_impl,
    build_personalization_remediation_response as _build_personalization_remediation_response_impl,
    build_personalization_study_path_response as _build_personalization_study_path_response_impl,
    build_recomputed_personalization_profile_response as _build_recomputed_personalization_profile_response_impl,
)
from src.domains.platform.services.learner_profile_service import (
    get_learner_profile_dict,
    recompute_learner_profile,
)
from src.domains.platform.services.mastery_tracking_service import build_profile_aware_recommendations
from src.domains.platform.services.metrics_registry import (
    observe_personalization_event,
    snapshot_personalization_metrics,
)
from src.domains.platform.services.study_path_service import (
    build_remediation_candidates,
    complete_study_path_step,
    get_or_create_study_path,
)

router = APIRouter(prefix="/api/personalization", tags=["Personalization"])
_ALLOWED_PERSONALIZATION_EVENTS = {
    "recommendation_click",
    "study_path_open",
    "study_path_step_complete",
}


class PersonalizationEventRequest(BaseModel):
    event_type: str
    surface: str | None = None
    target: str | None = None
    item_id: str | None = None


def _build_personalization_metrics_summary(rows: list[dict]) -> dict:
    return _build_personalization_metrics_summary_impl(rows)


@router.get("/recommendations")
async def get_personalized_recommendations(
    active_tool: str | None = None,
    notebook_id: str | None = None,
    current_surface: str | None = None,
    current_topic: str | None = None,
    current_query: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "student":
        return {"items": [], "learner_profile": None}
    return _build_personalized_recommendations_response_impl(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        active_tool=active_tool,
        notebook_id=notebook_id,
        current_surface=current_surface,
        current_topic=current_topic,
        current_query=current_query,
        build_profile_aware_recommendations_fn=build_profile_aware_recommendations,
        observe_personalization_event_fn=observe_personalization_event,
    )


@router.get("/profile")
async def get_personalization_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "student":
        return {"profile": None}
    return _build_personalization_profile_response_impl(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        get_learner_profile_dict_fn=get_learner_profile_dict,
    )


@router.post("/profile/recompute")
async def recompute_personalization_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "student":
        return {"profile": None}
    return _build_recomputed_personalization_profile_response_impl(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        recompute_learner_profile_fn=recompute_learner_profile,
        get_learner_profile_dict_fn=get_learner_profile_dict,
    )


@router.get("/remediation")
async def get_personalization_remediation(
    limit: int = 3,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "student":
        return {"items": []}
    return _build_personalization_remediation_response_impl(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        limit=limit,
        get_learner_profile_dict_fn=get_learner_profile_dict,
        build_remediation_candidates_fn=build_remediation_candidates,
    )


@router.get("/study-path")
async def get_personalization_study_path(
    topic: str | None = None,
    notebook_id: str | None = None,
    subject_id: str | None = None,
    current_surface: str | None = None,
    force_refresh: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "student":
        return {"plan": None}
    return _build_personalization_study_path_response_impl(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        topic=topic,
        notebook_id=notebook_id,
        subject_id=subject_id,
        current_surface=current_surface,
        force_refresh=force_refresh,
        get_or_create_study_path_fn=get_or_create_study_path,
        observe_personalization_event_fn=observe_personalization_event,
    )


@router.post("/study-path/{plan_id}/steps/{step_id}/complete")
async def complete_personalization_study_path_step(
    plan_id: str,
    step_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "student":
        return {"plan": None}
    return _build_completed_study_path_response_impl(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        plan_id=plan_id,
        step_id=step_id,
        complete_study_path_step_fn=complete_study_path_step,
        observe_personalization_event_fn=observe_personalization_event,
    )


@router.post("/events")
async def record_personalization_event(
    payload: PersonalizationEventRequest,
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "student":
        return {"success": False}
    if payload.event_type not in _ALLOWED_PERSONALIZATION_EVENTS:
        raise HTTPException(status_code=400, detail="Unsupported event_type")

    observe_personalization_event(
        payload.event_type,
        surface=payload.surface or "unknown",
        target=payload.target or "unknown",
    )
    return {"success": True}


@router.get("/metrics")
async def get_personalization_metrics(
    current_user: User = Depends(require_role("admin")),
):
    rows = snapshot_personalization_metrics()
    summary = _build_personalization_metrics_summary(rows)
    return {
        "metrics": rows,
        **summary,
    }
