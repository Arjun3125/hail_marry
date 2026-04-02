"""Application helpers for personalization route orchestration."""

from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.domains.platform.services.learner_profile_service import get_learner_profile_dict


def build_personalization_metrics_summary(rows: list[dict]) -> dict:
    metric_totals = {
        "recommendation_served": "recommendation_served_total",
        "recommendation_click": "recommendation_click_total",
        "study_path_view": "study_path_view_total",
        "study_path_step_complete": "study_path_step_complete_total",
        "mastery_improved": "mastery_improved_total",
        "mastery_recovered": "mastery_recovered_total",
        "guided_mastery_improved": "guided_mastery_improved_total",
        "guided_mastery_recovered": "guided_mastery_recovered_total",
    }
    overall = {
        "recommendation_served_total": 0.0,
        "recommendation_click_total": 0.0,
        "study_path_view_total": 0.0,
        "study_path_step_complete_total": 0.0,
        "mastery_improved_total": 0.0,
        "mastery_recovered_total": 0.0,
        "guided_mastery_improved_total": 0.0,
        "guided_mastery_recovered_total": 0.0,
    }
    by_surface: dict[str, dict[str, float | str]] = {}

    for row in rows:
        metric = str(row.get("metric") or "")
        surface = str(row.get("surface") or "unknown")
        count = float(row.get("count") or 0.0)
        surface_bucket = by_surface.setdefault(
            surface,
            {
                "surface": surface,
                "recommendation_served_total": 0.0,
                "recommendation_click_total": 0.0,
                "study_path_view_total": 0.0,
                "study_path_step_complete_total": 0.0,
                "mastery_improved_total": 0.0,
                "mastery_recovered_total": 0.0,
                "guided_mastery_improved_total": 0.0,
                "guided_mastery_recovered_total": 0.0,
            },
        )

        total_key = metric_totals.get(metric)
        if total_key:
            overall[total_key] += count
            surface_bucket[total_key] = float(surface_bucket.get(total_key, 0.0)) + count

    def _safe_rate(numerator: float, denominator: float) -> float:
        if denominator <= 0:
            return 0.0
        return round((numerator / denominator) * 100, 2)

    overall_summary = {
        **overall,
        "recommendation_ctr_pct": _safe_rate(
            overall["recommendation_click_total"],
            overall["recommendation_served_total"],
        ),
        "study_path_completion_rate_pct": _safe_rate(
            overall["study_path_step_complete_total"],
            overall["study_path_view_total"],
        ),
        "guided_improvement_rate_pct": _safe_rate(
            overall["guided_mastery_improved_total"],
            overall["study_path_step_complete_total"],
        ),
        "guided_recovery_rate_pct": _safe_rate(
            overall["guided_mastery_recovered_total"],
            overall["study_path_step_complete_total"],
        ),
        "recommendation_to_guided_improvement_pct": _safe_rate(
            overall["guided_mastery_improved_total"],
            overall["recommendation_click_total"],
        ),
    }

    surface_rows = []
    for surface in sorted(by_surface):
        bucket = by_surface[surface]
        recommendation_served_total = float(bucket["recommendation_served_total"])
        recommendation_click_total = float(bucket["recommendation_click_total"])
        study_path_view_total = float(bucket["study_path_view_total"])
        study_path_step_complete_total = float(bucket["study_path_step_complete_total"])
        guided_mastery_improved_total = float(bucket["guided_mastery_improved_total"])
        guided_mastery_recovered_total = float(bucket["guided_mastery_recovered_total"])
        surface_rows.append(
            {
                **bucket,
                "recommendation_ctr_pct": _safe_rate(
                    recommendation_click_total,
                    recommendation_served_total,
                ),
                "study_path_completion_rate_pct": _safe_rate(
                    study_path_step_complete_total,
                    study_path_view_total,
                ),
                "guided_improvement_rate_pct": _safe_rate(
                    guided_mastery_improved_total,
                    study_path_step_complete_total,
                ),
                "guided_recovery_rate_pct": _safe_rate(
                    guided_mastery_recovered_total,
                    study_path_step_complete_total,
                ),
            }
        )

    return {
        "summary": overall_summary,
        "by_surface": surface_rows,
    }


def build_personalized_recommendations_response(
    *,
    db: Session,
    tenant_id,
    user_id,
    active_tool: str | None,
    notebook_id: str | None,
    current_surface: str | None,
    current_topic: str | None,
    current_query: str | None,
    build_profile_aware_recommendations_fn,
    observe_personalization_event_fn,
) -> dict:
    notebook_uuid: UUID | None = None
    if notebook_id:
        try:
            notebook_uuid = UUID(str(notebook_id))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid notebook_id") from exc

    learner_profile = get_learner_profile_dict(
        db,
        tenant_id=tenant_id,
        user_id=user_id,
    )
    db.commit()

    items = build_profile_aware_recommendations_fn(
        db,
        tenant_id=tenant_id,
        user_id=user_id,
        active_tool=active_tool,
        notebook_id=notebook_uuid,
        current_surface=current_surface,
        current_topic=current_topic,
        current_query=current_query,
        learner_profile=learner_profile,
    )
    for item in items:
        observe_personalization_event_fn(
            "recommendation_served",
            surface=current_surface or "unknown",
            target=str(item.get("target_tool") or "assistant"),
        )
    return {
        "items": items,
        "learner_profile": learner_profile,
        "context": {
            "active_tool": active_tool,
            "current_surface": current_surface,
            "current_topic": current_topic,
            "current_query": current_query,
        },
    }


def build_personalization_profile_response(
    *,
    db: Session,
    tenant_id,
    user_id,
    get_learner_profile_dict_fn=get_learner_profile_dict,
) -> dict:
    profile = get_learner_profile_dict_fn(
        db,
        tenant_id=tenant_id,
        user_id=user_id,
    )
    db.commit()
    return {"profile": profile}


def build_recomputed_personalization_profile_response(
    *,
    db: Session,
    tenant_id,
    user_id,
    recompute_learner_profile_fn,
    get_learner_profile_dict_fn=get_learner_profile_dict,
) -> dict:
    recompute_learner_profile_fn(
        db,
        tenant_id=tenant_id,
        user_id=user_id,
    )
    db.commit()
    profile = get_learner_profile_dict_fn(
        db,
        tenant_id=tenant_id,
        user_id=user_id,
    )
    return {"profile": profile}


def build_personalization_remediation_response(
    *,
    db: Session,
    tenant_id,
    user_id,
    limit: int,
    get_learner_profile_dict_fn=get_learner_profile_dict,
    build_remediation_candidates_fn,
) -> dict:
    learner_profile = get_learner_profile_dict_fn(
        db,
        tenant_id=tenant_id,
        user_id=user_id,
    )
    items = build_remediation_candidates_fn(
        db,
        tenant_id=tenant_id,
        user_id=user_id,
        learner_profile=learner_profile,
        limit=max(1, min(limit, 10)),
    )
    return {"items": items, "learner_profile": learner_profile}


def build_personalization_study_path_response(
    *,
    db: Session,
    tenant_id,
    user_id,
    topic: str | None,
    notebook_id: str | None,
    subject_id: str | None,
    current_surface: str | None,
    force_refresh: bool,
    get_or_create_study_path_fn,
    observe_personalization_event_fn,
) -> dict:
    notebook_uuid: UUID | None = None
    subject_uuid: UUID | None = None
    if notebook_id:
        try:
            notebook_uuid = UUID(str(notebook_id))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid notebook_id") from exc
    if subject_id:
        try:
            subject_uuid = UUID(str(subject_id))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid subject_id") from exc

    plan = get_or_create_study_path_fn(
        db,
        tenant_id=tenant_id,
        user_id=user_id,
        topic=topic,
        notebook_id=notebook_uuid,
        subject_id=subject_uuid,
        current_surface=current_surface,
        force_refresh=force_refresh,
    )
    next_action = plan.get("next_action") or {}
    observe_personalization_event_fn(
        "study_path_view",
        surface=current_surface or "unknown",
        target=str(next_action.get("target_tool") or "assistant"),
    )
    db.commit()
    return {"plan": plan}


def build_completed_study_path_response(
    *,
    db: Session,
    tenant_id,
    user_id,
    plan_id: str,
    step_id: str,
    complete_study_path_step_fn,
    observe_personalization_event_fn,
) -> dict:
    try:
        plan_uuid = UUID(str(plan_id))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid plan_id") from exc

    try:
        plan = complete_study_path_step_fn(
            db,
            tenant_id=tenant_id,
            user_id=user_id,
            plan_id=plan_uuid,
            step_id=step_id,
        )
    except ValueError as exc:
        if str(exc) == "study_path_not_found":
            raise HTTPException(status_code=404, detail="Study path not found") from exc
        if str(exc) == "study_path_step_not_found":
            raise HTTPException(status_code=404, detail="Study path step not found") from exc
        raise

    completed_step = next((item for item in plan.get("items", []) if item.get("id") == step_id), None)
    observe_personalization_event_fn(
        "study_path_step_complete",
        surface="study_path",
        target=str((completed_step or {}).get("target_tool") or "assistant"),
    )
    db.commit()
    return {"plan": plan}
