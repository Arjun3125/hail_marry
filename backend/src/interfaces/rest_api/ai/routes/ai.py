"""AI query route orchestrating cache, quotas, logging, and AI execution."""
import json
import random
from typing import Optional
from uuid import UUID
import time
import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.interfaces.rest_api.ai.agent_orchestrator import (
    get_next_step,
    get_workflow,
    get_workflow_state,
    list_workflows,
    record_step_result,
    start_workflow,
)
from src.infrastructure.vector_store.hyde import hyde_transform
from src.infrastructure.llm.cache import cache_response, get_cached_response
from src.infrastructure.vector_store.citation_linker import make_citations_clickable
from auth.dependencies import get_current_user
from database import get_db
from src.domains.platform.models.ai import AIQuery
from src.domains.identity.models.tenant import Tenant
from src.domains.identity.models.user import User
from src.domains.platform.models.generated_content import GeneratedContent
from src.domains.platform.models.notebook import Notebook
from src.domains.platform.schemas.ai_runtime import AIQueryRequest, InternalAIQueryRequest
from src.domains.platform.services.ai_gateway import run_text_query
from src.domains.platform.services.context_memory import get_context_memory_service
from src.domains.platform.services.knowledge_graph import get_concept_context
from src.domains.platform.services.webhooks import emit_webhook_event
from src.domains.platform.services.feature_flags import require_feature
from src.domains.platform.services.learner_profile_service import get_learner_profile_dict
from src.domains.platform.services.mastery_tracking_service import (
    count_recent_confusion_queries,
    get_topic_mastery_snapshot,
    infer_topic_from_query,
    record_ai_confusion_pattern,
)
from src.domains.platform.services.usage_governance import (
    GovernanceDecision,
    apply_model_override,
    approximate_token_count,
    evaluate_governance,
    record_usage_event,
    resolve_metric_for_mode,
)
from config import settings

router = APIRouter(prefix="/api/ai", tags=["AI"])


def _compact_topic(query: str, *, fallback: str = "the selected topic") -> str:
    topic = " ".join(query.strip().split())
    if not topic:
        return fallback
    return topic[:120]


def _build_demo_ai_result(request: AIQueryRequest) -> dict:
    """Return prompt-aware demo content instead of replaying stale historical logs."""
    topic = _compact_topic(request.query)
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


def _validate_notebook_access(db: Session, current_user: User, notebook_id: UUID | None) -> None:
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


def _request_field_was_provided(request: AIQueryRequest, field_name: str) -> bool:
    field_set = getattr(request, "model_fields_set", None)
    if field_set is None:
        field_set = getattr(request, "__fields_set__", set())
    return field_name in set(field_set or set())


def _build_personalized_ai_request(
    *,
    db: Session,
    current_user: User,
    request: AIQueryRequest,
    prepared_query: str,
    governance: GovernanceDecision | None = None,
) -> InternalAIQueryRequest:
    learner_profile = get_learner_profile_dict(
        db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
    )

    effective_language = request.language
    preferred_language = str(learner_profile.get("preferred_language") or "").lower()
    if (
        not _request_field_was_provided(request, "language")
        and request.language == "english"
        and preferred_language in {"hindi", "marathi"}
    ):
        effective_language = preferred_language

    effective_response_length = request.response_length
    preferred_length = str(learner_profile.get("preferred_response_length") or "").lower()
    if (
        not _request_field_was_provided(request, "response_length")
        and request.response_length == "default"
        and preferred_length in {"brief", "detailed"}
    ):
        effective_response_length = preferred_length

    effective_expertise = request.expertise_level
    inferred_expertise = str(learner_profile.get("inferred_expertise_level") or "").lower()
    if (
        not _request_field_was_provided(request, "expertise_level")
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
    inferred_topic = infer_topic_from_query(request.query)
    if inferred_topic:
        repeated_confusion_count = count_recent_confusion_queries(
            db,
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            topic=request.query,
        )
        mastery_snapshot = get_topic_mastery_snapshot(
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


async def _prepare_ai_query(
    *,
    db: Session,
    tenant_id: str | UUID,
    query: str,
    mode: str,
    notebook_id: Optional[str | UUID] = None,
    user_id: Optional[str | UUID] = None,
) -> tuple[str, list[dict], str, str]:
    """Prepare AI query with knowledge graph and context memory."""
    # Get knowledge graph context
    knowledge_context = await get_concept_context(
        db, tenant_id, query, notebook_id=notebook_id
    )
    
    # Get conversation history for context memory
    conversation_context = ""
    if user_id:
        context_service = get_context_memory_service(db)
        history = await context_service.get_conversation_history(
            user_id=user_id,
            notebook_id=notebook_id,
            limit=5,
            hours=2,  # Recent context only
        )
        conversation_context = context_service.format_context_for_prompt(history)
    
    hyde_query = await hyde_transform(query, mode)
    knowledge_text = _format_knowledge_graph_context(knowledge_context)
    
    # Combine contexts
    prepared_query = hyde_query
    if conversation_context:
        prepared_query = f"{conversation_context}\n\n{prepared_query}"
    if knowledge_text:
        prepared_query = f"{prepared_query}\n\n{knowledge_text}"
    
    return prepared_query, knowledge_context, hyde_query, conversation_context


@router.post("/query")
async def ai_query(
    request: AIQueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    _feat: bool = Depends(require_feature("ai_chat")),
):
    """Process an AI query while keeping quota, caching, and audit logging in the API tier."""
    _validate_notebook_access(db, current_user, request.notebook_id)

    trace_id = str(uuid.uuid4())[:8]
    start_time = time.time()

    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    daily_limit = tenant.ai_daily_limit if tenant else 50
    metric = resolve_metric_for_mode(request.mode)
    governance = evaluate_governance(
        db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        metric=metric,
        mode=request.mode,
        estimated_prompt_tokens=approximate_token_count(request.query),
    )
    if not governance.allowed:
        raise HTTPException(status_code=429, detail=governance.detail)

    today_count = db.query(AIQuery).filter(
        AIQuery.tenant_id == current_user.tenant_id,
        AIQuery.user_id == current_user.id,
        func.date(AIQuery.created_at) == date.today(),
    ).count()

    if today_count >= daily_limit:
        raise HTTPException(
            status_code=429,
            detail=f"Daily AI query limit reached ({daily_limit}). Try again tomorrow.",
        )

    from config import settings
    knowledge_context: list[dict] = []
    hyde_query = request.query
    conversation_context = ""
    if settings.app.demo_mode:
        ai_result = _build_demo_ai_result(request)
    else:
        if not request.audit_retrieval:
            cached = get_cached_response(
                tenant_id=str(current_user.tenant_id),
                query=request.query,
                mode=request.mode,
                subject_id=request.subject_id or "",
                notebook_id=str(request.notebook_id) if request.notebook_id else "",
            )
            if cached:
                record_usage_event(
                    db,
                    tenant_id=current_user.tenant_id,
                    user_id=current_user.id,
                    metric=metric,
                    token_usage=0,
                    cache_hit=True,
                    model_used="cache",
                    metadata={"route": "ai.query", "mode": request.mode, "cached": True},
                )
                db.commit()
                cached["cached"] = True
                if cached.get("citations"):
                    cached = make_citations_clickable(cached, current_user.tenant_id, db)
                return cached

        prepared_query, knowledge_context, hyde_query, conversation_context = await _prepare_ai_query(
            db=db,
            tenant_id=current_user.tenant_id,
            query=request.query,
            mode=request.mode,
            notebook_id=request.notebook_id,
            user_id=current_user.id,
        )

        ai_result = await run_text_query(
            _build_personalized_ai_request(
                db=db,
                current_user=current_user,
                request=request,
                prepared_query=prepared_query,
                governance=governance,
            ),
            trace_id=trace_id,
        )

    elapsed_ms = int((time.time() - start_time) * 1000)

    result = {
        "answer": ai_result["answer"],
        "citations": ai_result.get("citations", []),
        "trace_id": trace_id,
        "token_usage": ai_result.get("token_usage", 0),
        "response_time_ms": elapsed_ms,
        "mode": ai_result["mode"],
        "has_context": ai_result.get("has_context", True),
        "citation_valid": ai_result.get("citation_valid", False),
        "hyde_used": hyde_query != request.query,
        "hyde_query": hyde_query if hyde_query != request.query else None,
        "knowledge_graph": knowledge_context,
        "conversation_context_used": bool(conversation_context),
        "runtime_mode": ai_result.get("runtime_mode", "live"),
        "is_demo_response": ai_result.get("is_demo_response", False),
        "demo_notice": ai_result.get("demo_notice"),
        "demo_sources": ai_result.get("demo_sources", []),
    }
    if request.audit_retrieval:
        result["retrieval_audit"] = ai_result.get("retrieval_audit") or {
            "enabled": False,
            "reason": "demo_mode" if settings.app.demo_mode else "unavailable",
        }
    result = make_citations_clickable(result, current_user.tenant_id, db)

    ai_log = AIQuery(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        notebook_id=request.notebook_id if request.notebook_id else None,
        query_text=request.query,
        mode=ai_result["mode"],
        response_text=ai_result["answer"],
        token_usage=ai_result.get("token_usage", 0),
        response_time_ms=elapsed_ms,
        trace_id=trace_id,
        citation_count=ai_result.get("citation_count", 0),
    )
    db.add(ai_log)
    record_usage_event(
        db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        metric=metric,
        token_usage=int(ai_result.get("token_usage", 0) or 0),
        cache_hit=False,
        model_used=apply_model_override(settings.llm.model, settings.llm.fallback_model, governance.model_override)
        if not settings.app.demo_mode
        else "demo",
        used_fallback_model=governance.model_override == "fallback",
        metadata={
            "route": "ai.query",
            "mode": request.mode,
            "guardrail_active": governance.guardrail_active,
            "queue_recommended": governance.queue_recommended,
        },
    )
    db.commit()
    db.refresh(ai_log)

    if request.mode in {"qa", "study_guide", "socratic"}:
        subject_uuid = None
        if request.subject_id:
            try:
                subject_uuid = UUID(str(request.subject_id))
            except (TypeError, ValueError):
                subject_uuid = None
        repeated_count = count_recent_confusion_queries(
            db,
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            topic=request.query,
        )
        if repeated_count >= 2:
            record_ai_confusion_pattern(
                db,
                tenant_id=current_user.tenant_id,
                user_id=current_user.id,
                query=request.query,
                repeated_count=repeated_count,
                subject_id=subject_uuid,
            )
            db.commit()

    if not settings.app.demo_mode:
        try:
            await emit_webhook_event(
                db=db,
                tenant_id=current_user.tenant_id,
                event_type="ai.query.completed",
                data={
                    "query_id": str(ai_log.id),
                    "user_id": str(current_user.id),
                    "mode": ai_result["mode"],
                    "trace_id": trace_id,
                    "token_usage": ai_result.get("token_usage", 0),
                    "response_time_ms": elapsed_ms,
                },
            )
        except Exception:
            pass

    # Save structured content (quiz, flashcards, mindmap, etc.) to generated_content table
    structured_modes = {"quiz", "flashcards", "mindmap", "concept_map", "flowchart"}
    if request.notebook_id and ai_result["mode"] in structured_modes:
        try:
            content_data = {
                "query": request.query,
                "mode": ai_result["mode"],
                "answer": ai_result["answer"],
                "citations": ai_result.get("citations", []),
            }
            generated = GeneratedContent(
                tenant_id=current_user.tenant_id,
                user_id=current_user.id,
                notebook_id=request.notebook_id,
                type=ai_result["mode"],
                title=f"{ai_result['mode'].replace('_', ' ').title()} - {request.query[:50]}",
                content=content_data,
                source_query=request.query,
                parent_conversation_id=ai_log.id,
            )
            db.add(generated)
            db.commit()
        except Exception:
            pass  # Don't fail the request if saving content fails

    if not settings.app.demo_mode and not request.audit_retrieval:
        cache_response(
            tenant_id=str(current_user.tenant_id),
            query=request.query,
            mode=ai_result["mode"],
            response=result,
            subject_id=request.subject_id or "",
            notebook_id=str(request.notebook_id) if request.notebook_id else "",
        )

    return result


class WorkflowStartRequest(BaseModel):
    workflow_type: str
    topic: str
    subject_id: str | None = None
    language: str = "english"
    response_length: str = "default"
    expertise_level: str = "standard"


@router.get("/workflows")
async def list_ai_workflows(current_user: User = Depends(get_current_user)):
    return list_workflows()


@router.post("/workflows")
async def start_ai_workflow(
    request: WorkflowStartRequest,
    current_user: User = Depends(get_current_user),
    _feat: bool = Depends(require_feature("agent_orchestrator")),
):
    state = await start_workflow(request.workflow_type, {
        "topic": request.topic,
        "subject_id": request.subject_id,
        "language": request.language,
        "response_length": request.response_length,
        "expertise_level": request.expertise_level,
    })
    return {"workflow": state.to_dict()}


@router.post("/workflows/{workflow_id}/next")
async def run_ai_workflow_step(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    state = get_workflow_state(workflow_id)
    if not state:
        raise HTTPException(status_code=404, detail="Workflow not found")

    step = get_next_step(workflow_id)
    if not step:
        return {"workflow": get_workflow(workflow_id), "completed": True}

    prepared_query, knowledge_context, hyde_query, _conversation_context = await _prepare_ai_query(
        db=db,
        tenant_id=str(current_user.tenant_id),
        query=step["prompt"],
        mode=step["mode"],
    )

    ai_result = await run_text_query(
        InternalAIQueryRequest(
            query=prepared_query,
            mode=step["mode"],
            subject_id=state.params.get("subject_id"),
            language=state.params.get("language", "english"),
            response_length=state.params.get("response_length", "default"),
            expertise_level=state.params.get("expertise_level", "standard"),
            tenant_id=str(current_user.tenant_id),
        ),
        trace_id=str(uuid.uuid4())[:8],
    )

    ai_result = make_citations_clickable(ai_result, current_user.tenant_id, db)
    record_step_result(workflow_id, ai_result)
    return {
        "workflow": get_workflow(workflow_id),
        "step": step,
        "result": ai_result,
        "hyde_used": hyde_query != step["prompt"],
        "knowledge_graph": knowledge_context,
    }
