"""Application-layer orchestration helpers for AI query routes."""

from __future__ import annotations

import json
import random
from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from config import settings
from src.domains.identity.models.user import User
from src.domains.platform.models.notebook import Notebook
from src.domains.platform.schemas.ai_runtime import AIQueryRequest, InternalAIQueryRequest
from src.domains.platform.services.context_memory import get_context_memory_service
from src.domains.platform.services.knowledge_graph import get_concept_context
from src.domains.platform.services.learner_profile_service import get_learner_profile_dict
from src.domains.platform.services.mastery_tracking_service import (
    count_recent_confusion_queries,
    get_topic_mastery_snapshot,
    infer_topic_from_query,
)
from src.domains.platform.services.usage_governance import (
    GovernanceDecision,
    apply_model_override,
)
from src.infrastructure.vector_store.hyde import hyde_transform


def compact_topic(query: str, *, fallback: str = "the selected topic") -> str:
    topic = " ".join(query.strip().split())
    if not topic:
        return fallback
    return topic[:120]


def build_demo_ai_result(request: AIQueryRequest) -> dict:
    """Return prompt-aware demo content instead of replaying stale historical logs."""
    topic = compact_topic(request.query)
    topic_label = topic.title()
    source_label = "Demo notebook preview" if request.notebook_id else "Demo source preview"
    demo_notice = "Demo mode preview. This response is generated from the current prompt without live retrieval or citations."

    if request.mode == "quiz":
        answer = json.dumps(
            {
                "questions": [
                    {
                        "q": f"What is the main idea behind {topic}?",
                        "options": [
                            f"It explains a core principle of {topic}.",
                            f"It describes an unrelated historical event.",
                            f"It is only a mathematical formula.",
                            f"It has no practical meaning.",
                        ],
                        "answer": 0,
                    },
                    {
                        "q": f"Which study action best helps review {topic}?",
                        "options": [
                            "Ignore examples and memorize headings only.",
                            f"Summarize {topic} in your own words and test recall.",
                            "Skip revision and move to a different chapter.",
                            "Only copy notes without checking understanding.",
                        ],
                        "answer": 1,
                    },
                ]
            }
        )
    elif request.mode == "flashcards":
        answer = json.dumps(
            {
                "cards": [
                    {
                        "front": f"What is {topic}?",
                        "back": f"{topic_label} is the focus of this demo prompt. In live mode, the back would be grounded in uploaded materials.",
                    },
                    {
                        "front": f"Why does {topic} matter?",
                        "back": f"It helps the student understand the core concepts, vocabulary, and applications connected to {topic}.",
                    },
                ]
            }
        )
    elif request.mode == "mindmap":
        answer = json.dumps(
            {
                "label": topic_label,
                "children": [
                    {"label": "Definition"},
                    {"label": "Key Steps"},
                    {"label": "Examples"},
                ],
            }
        )
    elif request.mode == "concept_map":
        answer = json.dumps(
            {
                "nodes": [
                    {"id": "topic", "label": topic_label},
                    {"id": "basics", "label": "Basics"},
                    {"id": "application", "label": "Application"},
                ],
                "edges": [
                    {"from": "topic", "to": "basics", "label": "includes"},
                    {"from": "topic", "to": "application", "label": "supports"},
                ],
            }
        )
    elif request.mode == "flowchart":
        answer = "\n".join(
            [
                "flowchart TD",
                f'A["Start: {topic_label}"] --> B["Review core idea"]',
                'B --> C["Break into steps"]',
                'C --> D["Apply to an example"]',
                'D --> E["Check understanding"]',
            ]
        )
    elif request.mode == "study_guide":
        answer = "\n".join(
            [
                f"# Demo Study Guide: {topic_label}",
                "",
                "## What to learn",
                f"- Define {topic}",
                f"- Identify the main parts or stages of {topic}",
                f"- Explain one example or application of {topic}",
                "",
                "## Revision prompts",
                f"- How would you explain {topic} to a classmate?",
                f"- What are the most important terms connected to {topic}?",
                "",
                "_Demo mode note: use live mode for grounded study guidance from uploaded materials._",
            ]
        )
    elif request.mode == "socratic":
        answer = (
            f"Demo Socratic prompt for '{topic}': what do you already know about it, "
            f"and which part feels least clear right now? Start there and try one concrete example."
        )
    elif request.mode == "perturbation":
        answer = "\n".join(
            [
                f"1. Explain {topic} using a simpler real-world example.",
                f"2. Compare {topic} with a related but different concept.",
                f"3. Solve a variation where one condition of {topic} changes.",
                "",
                "Great that you're practicing deeply - this builds real mastery!",
            ]
        )
    elif request.mode == "debate":
        answer = (
            f"Demo debate response for '{topic}': your starting claim needs one clear reason, "
            f"one counterargument, and one example before it becomes persuasive."
        )
    elif request.mode == "essay_review":
        answer = "\n".join(
            [
                f"Demo essay review for '{topic}':",
                "- Strength: the topic is clearly stated.",
                "- Improve: add more evidence or examples.",
                "- Next question: which paragraph best supports your thesis, and why?",
            ]
        )
    elif request.mode == "weak_topic":
        answer = (
            f"Demo remediation plan for '{topic}': review the definition, practice one worked example, "
            "and test yourself with two short recall questions."
        )
    else:
        answer = (
            f"Demo answer for '{topic}'. Live mode would retrieve notebook or document context before generating a grounded response."
        )

    return {
        "answer": answer,
        "mode": request.mode,
        "citations": [],
        "token_usage": random.randint(120, 260),
        "citation_count": 0,
        "has_context": False,
        "citation_valid": False,
        "is_demo_response": True,
        "runtime_mode": "demo",
        "demo_notice": demo_notice,
        "demo_sources": [source_label],
    }


def _format_knowledge_graph_context(context: list[dict]) -> str:
    if not context:
        return ""
    lines = []
    for entry in context:
        concept = entry.get("concept")
        if not concept:
            continue
        related = entry.get("related") or []
        related_names = ", ".join(
            rel.get("concept") for rel in related if rel.get("concept")
        )
        if related_names:
            lines.append(f"- {concept}: {related_names}")
        else:
            lines.append(f"- {concept}")
    if not lines:
        return ""
    return "Relevant concepts:\n" + "\n".join(lines)


def validate_notebook_access(db: Session, current_user: User, notebook_id: UUID | None) -> None:
    if not notebook_id:
        return
    notebook = db.query(Notebook).filter(
        Notebook.id == notebook_id,
        Notebook.tenant_id == current_user.tenant_id,
        Notebook.user_id == current_user.id,
        Notebook.is_active == True,
    ).first()
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")


def request_field_was_provided(request: AIQueryRequest, field_name: str) -> bool:
    field_set = getattr(request, "model_fields_set", None)
    if field_set is None:
        field_set = getattr(request, "__fields_set__", set())
    return field_name in set(field_set or set())


def build_personalized_ai_request(
    *,
    db: Session,
    current_user: User,
    request: AIQueryRequest,
    prepared_query: str,
    governance: GovernanceDecision | None = None,
    get_learner_profile_dict_fn=get_learner_profile_dict,
    request_field_was_provided_fn=request_field_was_provided,
    infer_topic_from_query_fn=infer_topic_from_query,
    count_recent_confusion_queries_fn=count_recent_confusion_queries,
    get_topic_mastery_snapshot_fn=get_topic_mastery_snapshot,
) -> InternalAIQueryRequest:
    learner_profile = get_learner_profile_dict_fn(
        db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
    )

    effective_language = request.language
    preferred_language = str(learner_profile.get("preferred_language") or "").lower()
    if (
        not request_field_was_provided_fn(request, "language")
        and request.language == "english"
        and preferred_language in {"hindi", "marathi"}
    ):
        effective_language = preferred_language

    effective_response_length = request.response_length
    preferred_length = str(learner_profile.get("preferred_response_length") or "").lower()
    if (
        not request_field_was_provided_fn(request, "response_length")
        and request.response_length == "default"
        and preferred_length in {"brief", "detailed"}
    ):
        effective_response_length = preferred_length

    effective_expertise = request.expertise_level
    inferred_expertise = str(learner_profile.get("inferred_expertise_level") or "").lower()
    if (
        not request_field_was_provided_fn(request, "expertise_level")
        and request.expertise_level == "standard"
        and inferred_expertise in {"simple", "advanced"}
    ):
        effective_expertise = inferred_expertise

    subject_uuid = None
    if request.subject_id:
        try:
            subject_uuid = UUID(str(request.subject_id))
        except (TypeError, ValueError):
            subject_uuid = None

    learner_topic_context = None
    inferred_topic = infer_topic_from_query_fn(request.query)
    if inferred_topic:
        repeated_confusion_count = count_recent_confusion_queries_fn(
            db,
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            topic=request.query,
        )
        mastery_snapshot = get_topic_mastery_snapshot_fn(
            db,
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            topic=inferred_topic,
            subject_id=subject_uuid,
        )
        learner_topic_context = {
            "topic": inferred_topic,
            "mastery_score": mastery_snapshot.get("mastery_score"),
            "confidence_score": mastery_snapshot.get("confidence_score"),
            "focus_concepts": [item.get("concept") for item in mastery_snapshot.get("concepts", []) if isinstance(item, dict)],
            "repeated_confusion_count": repeated_confusion_count,
        }

    return InternalAIQueryRequest(
        **{
            **request.model_dump(),
            "query": prepared_query,
            "language": effective_language,
            "response_length": effective_response_length,
            "expertise_level": effective_expertise,
        },
        tenant_id=str(current_user.tenant_id),
        user_id=str(current_user.id),
        learner_profile=learner_profile,
        learner_topic_context=learner_topic_context,
        model_override=(
            apply_model_override(settings.llm.model, settings.llm.fallback_model, governance.model_override)
            if governance
            else None
        ),
        max_prompt_tokens=governance.max_prompt_tokens if governance else None,
        max_completion_tokens=governance.max_completion_tokens if governance else None,
    )


async def prepare_ai_query(
    *,
    db: Session,
    tenant_id: str | UUID,
    query: str,
    mode: str,
    notebook_id: Optional[str | UUID] = None,
    user_id: Optional[str | UUID] = None,
) -> tuple[str, list[dict], str, str]:
    """Prepare AI query with knowledge graph and context memory."""
    knowledge_context = await get_concept_context(
        db, tenant_id, query, notebook_id=notebook_id
    )

    conversation_context = ""
    if user_id:
        context_service = get_context_memory_service(db)
        history = await context_service.get_conversation_history(
            user_id=user_id,
            notebook_id=notebook_id,
            limit=5,
            hours=2,
        )
        conversation_context = context_service.format_context_for_prompt(history)

    hyde_query = await hyde_transform(query, mode)
    knowledge_text = _format_knowledge_graph_context(knowledge_context)

    prepared_query = hyde_query
    if conversation_context:
        prepared_query = f"{conversation_context}\n\n{prepared_query}"
    if knowledge_text:
        prepared_query = f"{prepared_query}\n\n{knowledge_text}"

    return prepared_query, knowledge_context, hyde_query, conversation_context
