"""Application helpers for student study-tool generation."""

from __future__ import annotations

import json
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from src.domains.identity.models.user import User
from src.domains.platform.schemas.ai_runtime import (
    InternalStudyToolGenerateRequest,
    StudyToolGenerateRequest,
)
from src.domains.platform.services.learner_profile_service import get_learner_profile_dict
from src.domains.platform.services.mastery_tracking_service import (
    build_adaptive_quiz_profile,
    count_recent_confusion_queries,
    ensure_topic_mastery_seed,
    get_topic_mastery_snapshot,
    record_study_tool_activity,
)
from src.domains.platform.services.usage_governance import (
    apply_model_override,
    approximate_token_count,
    evaluate_governance,
    record_usage_event,
    resolve_metric_for_mode,
)


def build_study_tool_personalization(
    db: Session,
    *,
    current_user: User,
    topic: str,
    subject_uuid: UUID | None,
) -> tuple[dict | None, dict | None]:
    learner_profile = get_learner_profile_dict(
        db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
    )
    mastery_snapshot = get_topic_mastery_snapshot(
        db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        topic=topic,
        subject_id=subject_uuid,
    )
    learner_topic_context = {
        "topic": topic,
        "mastery_score": mastery_snapshot.get("mastery_score"),
        "confidence_score": mastery_snapshot.get("confidence_score"),
        "focus_concepts": [
            item.get("concept")
            for item in mastery_snapshot.get("concepts", [])
            if isinstance(item, dict) and item.get("concept")
        ],
        "repeated_confusion_count": count_recent_confusion_queries(
            db,
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            topic=topic,
        ),
    }
    return learner_profile, learner_topic_context


def mark_demo_payload(payload: dict[str, Any], *, demo_notice: str, demo_sources: list[str]) -> dict[str, Any]:
    """Attach explicit demo markers so clients and tests can distinguish mock output."""
    result = dict(payload)
    result["runtime_mode"] = "demo"
    result["is_demo_response"] = True
    result["demo_notice"] = demo_notice
    result["demo_sources"] = demo_sources
    return result


def _build_demo_study_tool_payload(
    *,
    tool: str,
    topic: str,
    demo_notice: str,
    demo_sources: list[str],
) -> dict[str, Any]:
    demo_tools = {
        "quiz": {
            "data": [
                {
                    "question": f"What is {topic}?",
                    "options": ["A. A branch of science", "B. A type of art", "C. A form of literature", "D. None of the above"],
                    "correct": "A",
                    "citation": "Demo Materials p.1",
                },
                {
                    "question": f"Which concept is central to {topic}?",
                    "options": ["A. Equilibrium", "B. Entropy", "C. Evolution", "D. Elasticity"],
                    "correct": "A",
                    "citation": "Demo Materials p.3",
                },
                {
                    "question": f"Who is a notable contributor to {topic}?",
                    "options": ["A. Albert Einstein", "B. Isaac Newton", "C. Marie Curie", "D. Charles Darwin"],
                    "correct": "B",
                    "citation": "Demo Materials p.5",
                },
            ],
            "citations": [{"source": "Demo Study Materials", "page": "1-5"}],
        },
        "flashcards": {
            "data": [
                {
                    "front": f"Define {topic}",
                    "back": f"{topic} is a fundamental area of study that explores key principles and theories.",
                    "citation": "Demo Materials p.1",
                },
                {
                    "front": f"Key principle of {topic}",
                    "back": "The principle of conservation states that certain properties remain constant.",
                    "citation": "Demo Materials p.2",
                },
                {
                    "front": f"Application of {topic}",
                    "back": f"{topic} is applied in engineering, medicine, and technology.",
                    "citation": "Demo Materials p.3",
                },
            ],
            "citations": [{"source": "Demo Study Materials", "page": "1-3"}],
        },
        "mindmap": {
            "data": {
                "label": topic,
                "children": [
                    {
                        "label": "Fundamentals",
                        "citation": "Demo Materials p.1",
                        "children": [
                            {"label": "Core Concepts", "citation": "Demo Materials p.2"},
                            {"label": "Key Theories", "citation": "Demo Materials p.3"},
                        ],
                    },
                    {
                        "label": "Applications",
                        "citation": "Demo Materials p.4",
                        "children": [
                            {"label": "Engineering", "citation": "Demo Materials p.5"},
                            {"label": "Medicine", "citation": "Demo Materials p.6"},
                        ],
                    },
                    {
                        "label": "History",
                        "citation": "Demo Materials p.7",
                        "children": [
                            {"label": "Key Discoveries", "citation": "Demo Materials p.8"},
                            {"label": "Notable Scientists", "citation": "Demo Materials p.9"},
                        ],
                    },
                ],
            },
            "content": {
                "label": topic,
                "children": [
                    {
                        "label": "Fundamentals",
                        "citation": "Demo Materials p.1",
                        "children": [
                            {"label": "Core Concepts", "citation": "Demo Materials p.2"},
                            {"label": "Key Theories", "citation": "Demo Materials p.3"},
                        ],
                    },
                    {
                        "label": "Applications",
                        "citation": "Demo Materials p.4",
                        "children": [
                            {"label": "Engineering", "citation": "Demo Materials p.5"},
                            {"label": "Medicine", "citation": "Demo Materials p.6"},
                        ],
                    },
                    {
                        "label": "History",
                        "citation": "Demo Materials p.7",
                        "children": [
                            {"label": "Key Discoveries", "citation": "Demo Materials p.8"},
                            {"label": "Notable Scientists", "citation": "Demo Materials p.9"},
                        ],
                    },
                ],
            },
            "citations": [{"source": "Demo Study Materials", "page": "1-10"}],
        },
        "flowchart": {
            "data": {
                "mermaid": f"flowchart TD\nA[Start {topic}] --> B[Learn basics]\nB --> C[Study concepts]\nC --> D[Practice tasks]\nD --> E[Apply learning]",
                "steps": [
                    {"id": "A", "label": "Start", "detail": f"Begin by introducing {topic}.", "citation": "Demo Materials p.1"},
                    {"id": "B", "label": "Learn basics", "detail": "Review the fundamental ideas first.", "citation": "Demo Materials p.2"},
                    {"id": "C", "label": "Study concepts", "detail": "Focus on the main concepts and their meaning.", "citation": "Demo Materials p.3"},
                    {"id": "D", "label": "Practice tasks", "detail": "Work through guided examples or exercises.", "citation": "Demo Materials p.4"},
                    {"id": "E", "label": "Apply learning", "detail": "Use the concepts in a final application step.", "citation": "Demo Materials p.5"},
                ],
            },
            "citations": [{"source": "Demo Study Materials", "page": "1-8"}],
        },
        "concept_map": {
            "data": {
                "nodes": [
                    {"id": "1", "label": topic},
                    {"id": "2", "label": "Theory"},
                    {"id": "3", "label": "Practice"},
                    {"id": "4", "label": "Application"},
                    {"id": "5", "label": "Research"},
                ],
                "edges": [
                    {"from": "1", "to": "2", "label": "requires", "citation": "Demo Materials p.2"},
                    {"from": "1", "to": "3", "label": "involves", "citation": "Demo Materials p.3"},
                    {"from": "2", "to": "4", "label": "leads to", "citation": "Demo Materials p.4"},
                    {"from": "3", "to": "4", "label": "supports", "citation": "Demo Materials p.5"},
                    {"from": "4", "to": "5", "label": "drives", "citation": "Demo Materials p.6"},
                ],
            },
            "citations": [{"source": "Demo Study Materials", "page": "1-6"}],
        },
    }
    return mark_demo_payload(
        demo_tools.get(tool, {"data": f"Demo content for {tool}: {topic}", "citations": []}),
        demo_notice=demo_notice,
        demo_sources=demo_sources,
    )


async def generate_student_study_tool(
    *,
    db: Session,
    current_user: User,
    data: StudyToolGenerateRequest,
    settings_obj,
    demo_notice: str,
    demo_sources: list[str],
    parse_uuid_fn,
    run_study_tool_fn,
    make_citations_clickable_fn,
    record_usage_event_fn=record_usage_event,
    record_study_tool_activity_fn=record_study_tool_activity,
) -> dict[str, Any]:
    topic = data.topic.strip()
    metric = resolve_metric_for_mode(data.tool)
    governance = evaluate_governance(
        db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        metric=metric,
        mode=data.tool,
        estimated_prompt_tokens=approximate_token_count(topic),
    )
    if not governance.allowed:
        raise ValueError(governance.detail)

    if settings_obj.app.demo_mode:
        payload = _build_demo_study_tool_payload(
            tool=data.tool,
            topic=topic,
            demo_notice=demo_notice,
            demo_sources=demo_sources,
        )
        record_usage_event_fn(
            db,
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            metric=metric,
            model_used="demo",
            metadata={"route": "student.tools.generate", "tool": data.tool},
        )
        db.commit()
        return payload

    subject_uuid = parse_uuid_fn(data.subject_id, "subject_id") if data.subject_id else None
    ensure_topic_mastery_seed(
        db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        topic=topic,
        subject_id=subject_uuid,
        evidence_type="study_tool_requested",
    )

    adaptive_quiz_profile = None
    if data.tool == "quiz":
        adaptive_quiz_profile = build_adaptive_quiz_profile(
            db,
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            topic=topic,
            subject_id=subject_uuid,
        )
    learner_profile, learner_topic_context = build_study_tool_personalization(
        db,
        current_user=current_user,
        topic=topic,
        subject_uuid=subject_uuid,
    )

    result = await run_study_tool_fn(
        InternalStudyToolGenerateRequest(
            tool=data.tool,
            topic=topic,
            subject_id=data.subject_id,
            notebook_id=data.notebook_id,
            tenant_id=str(current_user.tenant_id),
            user_id=str(current_user.id),
            adaptive_quiz_profile=adaptive_quiz_profile,
            learner_profile=learner_profile,
            learner_topic_context=learner_topic_context,
            model_override=apply_model_override(
                settings_obj.llm.model,
                settings_obj.llm.fallback_model,
                governance.model_override,
            ),
            max_prompt_tokens=governance.max_prompt_tokens,
            max_completion_tokens=governance.max_completion_tokens,
        )
    )
    record_usage_event_fn(
        db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        metric=metric,
        token_usage=int(result.get("token_usage", 0) or 0),
        model_used=result.get("model_used")
        or apply_model_override(
            settings_obj.llm.model,
            settings_obj.llm.fallback_model,
            governance.model_override,
        ),
        used_fallback_model=governance.model_override == "fallback",
        metadata={
            "route": "student.tools.generate",
            "tool": data.tool,
            "queue_recommended": governance.queue_recommended,
        },
    )
    record_study_tool_activity_fn(
        db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        topic=topic,
        subject_id=subject_uuid,
        tool=data.tool,
    )
    db.commit()
    return make_citations_clickable_fn(result, current_user.tenant_id, db)


async def generate_student_study_tool_job(
    *,
    db: Session,
    current_user: User,
    data: StudyToolGenerateRequest,
    settings_obj,
    demo_notice: str,
    demo_sources: list[str],
    parse_uuid_fn,
    enqueue_job_fn,
    session_factory,
    ai_query_model,
    build_public_job_response_fn,
    persist_job_state_fn,
    status_completed: str,
    job_type_study_tool: str,
    record_usage_event_fn=record_usage_event,
    record_study_tool_activity_fn=record_study_tool_activity,
) -> dict[str, Any]:
    topic = data.topic.strip()
    metric = resolve_metric_for_mode(data.tool)
    governance = evaluate_governance(
        db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        metric=metric,
        mode=data.tool,
        estimated_prompt_tokens=approximate_token_count(topic),
    )
    if not governance.allowed:
        raise ValueError(governance.detail)

    subject_uuid = parse_uuid_fn(data.subject_id, "subject_id") if data.subject_id else None
    adaptive_quiz_profile = None
    if data.tool == "quiz":
        adaptive_quiz_profile = build_adaptive_quiz_profile(
            db,
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            topic=topic,
            subject_id=subject_uuid,
        )
    learner_profile, learner_topic_context = build_study_tool_personalization(
        db,
        current_user=current_user,
        topic=topic,
        subject_uuid=subject_uuid,
    )
    ensure_topic_mastery_seed(
        db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        topic=topic,
        subject_id=subject_uuid,
        evidence_type="study_tool_queued",
    )
    record_study_tool_activity_fn(
        db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        topic=topic,
        subject_id=subject_uuid,
        tool=data.tool,
    )
    db.commit()

    payload = InternalStudyToolGenerateRequest(
        tool=data.tool,
        topic=topic,
        subject_id=data.subject_id,
        notebook_id=data.notebook_id,
        tenant_id=str(current_user.tenant_id),
        user_id=str(current_user.id),
        adaptive_quiz_profile=adaptive_quiz_profile,
        learner_profile=learner_profile,
        learner_topic_context=learner_topic_context,
        model_override=governance.model_override,
        max_prompt_tokens=governance.max_prompt_tokens,
        max_completion_tokens=governance.max_completion_tokens,
    )

    if settings_obj.app.demo_mode:
        demo_db = session_factory()
        try:
            try:
                demo_log = demo_db.query(ai_query_model).filter(
                    ai_query_model.tenant_id == current_user.tenant_id,
                    ai_query_model.mode == data.tool,
                ).first()
            except Exception:
                demo_log = None

            response_data = None
            if demo_log and demo_log.response_text:
                try:
                    response_data = json.loads(demo_log.response_text)
                except Exception:
                    response_data = {"output": demo_log.response_text}

            if not response_data:
                response_data = {"message": f"This is a mocked response for the '{data.tool}' tool generated in Demo Mode."}
            if not isinstance(response_data, dict):
                response_data = {"data": response_data}
            response_data = mark_demo_payload(
                response_data,
                demo_notice=demo_notice,
                demo_sources=demo_sources,
            )
        finally:
            demo_db.close()

        import uuid
        from datetime import datetime, timezone

        now_str = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        mock_job = {
            "job_id": str(uuid.uuid4()),
            "job_type": job_type_study_tool,
            "priority": 30,
            "trace_id": str(uuid.uuid4())[:8],
            "status": status_completed,
            "tenant_id": str(current_user.tenant_id),
            "user_id": str(current_user.id),
            "worker_id": "demo-worker",
            "runtime_mode": "demo",
            "is_demo_response": True,
            "demo_notice": demo_notice,
            "demo_sources": demo_sources,
            "request": payload.model_dump(mode="json"),
            "result": response_data,
            "error": None,
            "attempts": 1,
            "max_retries": 3,
            "created_at": now_str,
            "updated_at": now_str,
            "started_at": now_str,
            "completed_at": now_str,
            "events": [],
        }
        try:
            persist_job_state_fn(mock_job)
        except Exception:
            pass
        record_usage_event_fn(
            db,
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            metric=metric,
            model_used="demo",
            metadata={"route": "student.tools.generate.jobs", "tool": data.tool, "queued": True},
        )
        record_usage_event_fn(
            db,
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            metric="batch_jobs_queued",
            metadata={"route": "student.tools.generate.jobs", "tool": data.tool},
        )
        db.commit()
        return build_public_job_response_fn(mock_job)

    response = enqueue_job_fn(
        job_type_study_tool,
        payload.model_dump(mode="json"),
        tenant_id=str(current_user.tenant_id),
        user_id=str(current_user.id),
    )
    record_usage_event_fn(
        db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        metric=metric,
        used_fallback_model=governance.model_override == "fallback",
        metadata={"route": "student.tools.generate.jobs", "tool": data.tool, "queued": True},
    )
    record_usage_event_fn(
        db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        metric="batch_jobs_queued",
        metadata={"route": "student.tools.generate.jobs", "tool": data.tool},
    )
    db.commit()
    return response
