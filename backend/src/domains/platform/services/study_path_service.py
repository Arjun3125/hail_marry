"""Study path and remediation plan builder for personalized learning."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from src.domains.platform.models.study_path_plan import StudyPathPlan
from src.domains.platform.models.topic_mastery import TopicMastery
from src.domains.platform.services.learner_profile_service import get_learner_profile_dict
from src.domains.platform.services.mastery_tracking_service import (
    build_profile_aware_recommendations,
    get_topic_mastery_snapshot,
    normalize_topic_name,
)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _serialize_plan(plan: StudyPathPlan) -> dict[str, Any]:
    items = list(plan.items or [])
    current_index = int(plan.current_step_index or 0)
    next_action = items[current_index] if 0 <= current_index < len(items) else None
    return {
        "id": str(plan.id),
        "plan_type": plan.plan_type,
        "focus_topic": plan.focus_topic,
        "status": plan.status,
        "current_step_index": current_index,
        "items": items,
        "next_action": next_action,
        "source_context": dict(plan.source_context or {}),
        "notebook_id": str(plan.notebook_id) if plan.notebook_id else None,
        "subject_id": str(plan.subject_id) if plan.subject_id else None,
        "completed_at": plan.completed_at.isoformat() if plan.completed_at else None,
    }


def build_remediation_candidates(
    db: Session,
    *,
    tenant_id: UUID,
    user_id: UUID,
    learner_profile: dict[str, Any] | None = None,
    limit: int = 3,
) -> list[dict[str, Any]]:
    learner_profile = learner_profile or get_learner_profile_dict(
        db,
        tenant_id=tenant_id,
        user_id=user_id,
    )
    rows = (
        db.query(TopicMastery)
        .filter(
            TopicMastery.tenant_id == tenant_id,
            TopicMastery.user_id == user_id,
            TopicMastery.concept == "core",
        )
        .order_by(TopicMastery.mastery_score.asc(), TopicMastery.confidence_score.asc(), TopicMastery.updated_at.desc())
        .limit(limit)
        .all()
    )

    items: list[dict[str, Any]] = []
    for row in rows:
        topic = normalize_topic_name(row.topic or "")
        if not topic:
            continue
        suggested_tool = "study_guide"
        if float(row.mastery_score or 0) >= 55:
            suggested_tool = "quiz"
        elif float(row.confidence_score or 0) >= 0.45:
            suggested_tool = "flashcards"
        items.append(
            {
                "topic": topic,
                "mastery_score": round(float(row.mastery_score or 0.0), 1),
                "confidence_score": round(float(row.confidence_score or 0.0), 2),
                "suggested_tool": suggested_tool,
                "reason": "mastery_gap",
                "review_due_at": row.review_due_at.isoformat() if row.review_due_at else None,
            }
        )
    return items


def _build_plan_items(
    *,
    topic: str,
    learner_profile: dict[str, Any] | None,
    mastery_snapshot: dict[str, Any],
) -> list[dict[str, Any]]:
    expertise = str((learner_profile or {}).get("inferred_expertise_level") or "standard").lower()
    mastery_score = float(mastery_snapshot.get("mastery_score") or 0.0)
    focus_concepts = [
        item.get("concept")
        for item in mastery_snapshot.get("concepts", [])
        if isinstance(item, dict) and item.get("concept")
    ]
    focus_summary = ", ".join(focus_concepts[:3]) if focus_concepts else topic

    guide_prompt = f"Create a study guide for {topic} focused on the basics I need to rebuild first."
    if expertise == "advanced" and mastery_score >= 75:
        guide_prompt = f"Create a concise advanced study guide for {topic} focused on deeper relationships and applications."

    return [
        {
            "id": "guide",
            "title": f"Relearn {topic}",
            "target_tool": "study_guide",
            "prompt": guide_prompt,
            "estimated_minutes": 8,
            "status": "pending",
            "reason": "foundation_first",
        },
        {
            "id": "flashcards",
            "title": f"Memorize the weak concepts in {topic}",
            "target_tool": "flashcards",
            "prompt": f"Generate flashcards for {topic} prioritizing {focus_summary}.",
            "estimated_minutes": 6,
            "status": "pending",
            "reason": "focus_concepts",
        },
        {
            "id": "quiz",
            "title": f"Check understanding of {topic}",
            "target_tool": "quiz",
            "prompt": f"Create a short quiz for {topic} that starts from the basics and checks whether I improved.",
            "estimated_minutes": 7,
            "status": "pending",
            "reason": "verification",
        },
        {
            "id": "recheck",
            "title": f"Reflect on what is still unclear in {topic}",
            "target_tool": "socratic",
            "prompt": f"Ask me Socratic follow-up questions on {topic} to identify any remaining confusion.",
            "estimated_minutes": 5,
            "status": "pending",
            "reason": "confidence_recheck",
        },
    ]


def get_or_create_study_path(
    db: Session,
    *,
    tenant_id: UUID,
    user_id: UUID,
    topic: str | None = None,
    notebook_id: UUID | None = None,
    subject_id: UUID | None = None,
    current_surface: str | None = None,
    force_refresh: bool = False,
) -> dict[str, Any]:
    learner_profile = get_learner_profile_dict(
        db,
        tenant_id=tenant_id,
        user_id=user_id,
    )
    remediation_candidates = build_remediation_candidates(
        db,
        tenant_id=tenant_id,
        user_id=user_id,
        learner_profile=learner_profile,
        limit=3,
    )
    focus_topic = normalize_topic_name(topic or "")
    if not focus_topic and remediation_candidates:
        focus_topic = remediation_candidates[0]["topic"]
    if not focus_topic:
        focus_topic = normalize_topic_name((learner_profile or {}).get("primary_subjects", ["My next topic"])[0])

    existing = None
    if not force_refresh:
        existing = (
            db.query(StudyPathPlan)
            .filter(
                StudyPathPlan.tenant_id == tenant_id,
                StudyPathPlan.user_id == user_id,
                StudyPathPlan.focus_topic == focus_topic,
                StudyPathPlan.is_active.is_(True),
            )
            .order_by(StudyPathPlan.created_at.desc())
            .first()
        )
    if existing is not None:
        return _serialize_plan(existing)

    mastery_snapshot = get_topic_mastery_snapshot(
        db,
        tenant_id=tenant_id,
        user_id=user_id,
        topic=focus_topic,
        subject_id=subject_id,
    )
    items = _build_plan_items(
        topic=focus_topic,
        learner_profile=learner_profile,
        mastery_snapshot=mastery_snapshot,
    )
    recommendations = build_profile_aware_recommendations(
        db,
        tenant_id=tenant_id,
        user_id=user_id,
        notebook_id=notebook_id,
        current_surface=current_surface,
        current_topic=focus_topic,
        learner_profile=learner_profile,
        limit=3,
    )
    plan = StudyPathPlan(
        tenant_id=tenant_id,
        user_id=user_id,
        notebook_id=notebook_id,
        subject_id=subject_id,
        plan_type="remediation",
        focus_topic=focus_topic,
        status="active",
        current_step_index=0,
        items=items,
        source_context={
            "learner_profile": learner_profile,
            "mastery_snapshot": mastery_snapshot,
            "recommendations": recommendations,
            "surface": current_surface,
            "remediation_candidates": remediation_candidates,
        },
        is_active=True,
    )
    db.add(plan)
    db.flush()
    return _serialize_plan(plan)


def get_active_study_path_for_topic(
    db: Session,
    *,
    tenant_id: UUID,
    user_id: UUID,
    topic: str,
) -> dict[str, Any] | None:
    focus_topic = normalize_topic_name(topic)
    if not focus_topic:
        return None

    plan = (
        db.query(StudyPathPlan)
        .filter(
            StudyPathPlan.tenant_id == tenant_id,
            StudyPathPlan.user_id == user_id,
            StudyPathPlan.focus_topic == focus_topic,
            StudyPathPlan.is_active.is_(True),
        )
        .order_by(StudyPathPlan.created_at.desc())
        .first()
    )
    if plan is None:
        return None
    return _serialize_plan(plan)


def complete_study_path_step(
    db: Session,
    *,
    tenant_id: UUID,
    user_id: UUID,
    plan_id: UUID,
    step_id: str,
) -> dict[str, Any]:
    plan = (
        db.query(StudyPathPlan)
        .filter(
            StudyPathPlan.id == plan_id,
            StudyPathPlan.tenant_id == tenant_id,
            StudyPathPlan.user_id == user_id,
        )
        .first()
    )
    if plan is None:
        raise ValueError("study_path_not_found")

    updated_items: list[dict[str, Any]] = []
    matched = False
    for item in list(plan.items or []):
        normalized = dict(item)
        if str(normalized.get("id")) == step_id:
            normalized["status"] = "completed"
            matched = True
        updated_items.append(normalized)
    if not matched:
        raise ValueError("study_path_step_not_found")

    next_index = 0
    for idx, item in enumerate(updated_items):
        if item.get("status") != "completed":
            next_index = idx
            break
    else:
        next_index = len(updated_items)

    plan.items = updated_items
    plan.current_step_index = next_index
    plan.updated_at = _utcnow()
    if next_index >= len(updated_items):
        plan.status = "completed"
        plan.is_active = False
        plan.completed_at = _utcnow()

    db.flush()
    return _serialize_plan(plan)
