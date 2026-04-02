"""AI query route orchestrating cache, quotas, logging, and AI execution."""
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
from src.infrastructure.llm.cache import cache_response, get_cached_response
from src.infrastructure.vector_store.citation_linker import make_citations_clickable
from auth.dependencies import get_current_user
from database import get_db
from src.domains.platform.application.ai_queries import (
    build_demo_ai_result as _build_demo_ai_result,
    build_personalized_ai_request as _build_personalized_ai_request_impl,
    prepare_ai_query as _prepare_ai_query,
    request_field_was_provided as _request_field_was_provided,
    validate_notebook_access as _validate_notebook_access,
)
from src.domains.platform.models.ai import AIQuery
from src.domains.identity.models.tenant import Tenant
from src.domains.identity.models.user import User
from src.domains.platform.models.generated_content import GeneratedContent
from src.domains.platform.schemas.ai_runtime import AIQueryRequest, InternalAIQueryRequest
from src.domains.platform.services.ai_gateway import run_text_query
from src.domains.platform.services.feature_flags import require_feature
from src.domains.platform.services.learner_profile_service import get_learner_profile_dict
from src.domains.platform.services.mastery_tracking_service import (
    count_recent_confusion_queries,
    get_topic_mastery_snapshot,
    infer_topic_from_query,
    record_ai_confusion_pattern,
)
from src.domains.platform.services.usage_governance import (
    apply_model_override,
    approximate_token_count,
    evaluate_governance,
    record_usage_event,
    resolve_metric_for_mode,
)
from src.infrastructure.messaging import emit_webhook_event
from config import settings

router = APIRouter(prefix="/api/ai", tags=["AI"])


def _build_personalized_ai_request(*, db: Session, current_user: User, request: AIQueryRequest, prepared_query: str, governance=None) -> InternalAIQueryRequest:
    return _build_personalized_ai_request_impl(
        db=db,
        current_user=current_user,
        request=request,
        prepared_query=prepared_query,
        governance=governance,
        get_learner_profile_dict_fn=get_learner_profile_dict,
        request_field_was_provided_fn=_request_field_was_provided,
        infer_topic_from_query_fn=infer_topic_from_query,
        count_recent_confusion_queries_fn=count_recent_confusion_queries,
        get_topic_mastery_snapshot_fn=get_topic_mastery_snapshot,
    )


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
                elapsed_ms = int((time.time() - start_time) * 1000)
                cached_result = dict(cached)
                cached_result["cached"] = True
                cached_result["trace_id"] = trace_id
                cached_result["response_time_ms"] = elapsed_ms
                if cached_result.get("citations"):
                    cached_result = make_citations_clickable(cached_result, current_user.tenant_id, db)

                ai_log = AIQuery(
                    tenant_id=current_user.tenant_id,
                    user_id=current_user.id,
                    notebook_id=request.notebook_id if request.notebook_id else None,
                    query_text=request.query,
                    mode=str(cached_result.get("mode") or request.mode),
                    response_text=str(cached_result.get("answer") or ""),
                    token_usage=0,
                    response_time_ms=elapsed_ms,
                    trace_id=trace_id,
                    citation_count=len(cached_result.get("citations", []) or []),
                )
                db.add(ai_log)
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

                return cached_result

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
