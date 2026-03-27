"""AI query route orchestrating cache, quotas, logging, and AI execution."""
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
from src.domains.platform.schemas.ai_runtime import AIQueryRequest, InternalAIQueryRequest
from src.domains.platform.services.ai_gateway import run_text_query
from src.domains.platform.services.context_memory import get_context_memory_service
from src.domains.platform.services.knowledge_graph import get_concept_context
from src.domains.platform.services.webhooks import emit_webhook_event
from src.domains.platform.services.feature_flags import require_feature

router = APIRouter(prefix="/api/ai", tags=["AI"])


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
    trace_id = str(uuid.uuid4())[:8]
    start_time = time.time()

    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    daily_limit = tenant.ai_daily_limit if tenant else 50

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
    import random
    knowledge_context: list[dict] = []
    hyde_query = request.query
    conversation_context = ""
    if settings.app.demo_mode:
        demo_log = db.query(AIQuery).filter(
            AIQuery.tenant_id == current_user.tenant_id,
            AIQuery.mode == request.mode
        ).first()

        ai_result = {
            "answer": demo_log.response_text if demo_log else f"This is a mocked response for {request.mode} mode generated in Demo Mode.",
            "mode": request.mode,
            "citations": [],
            "token_usage": random.randint(150, 500),
            "citation_count": 0,
            "has_context": True,
            "citation_valid": True,
        }
    else:
        cached = get_cached_response(
            tenant_id=current_user.tenant_id,
            query=request.query,
            mode=request.mode,
            subject_id=request.subject_id or "",
        )
        if cached:
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
            InternalAIQueryRequest(
                **{**request.model_dump(), "query": prepared_query},
                tenant_id=str(current_user.tenant_id),
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
    }
    result = make_citations_clickable(result, current_user.tenant_id, db)

    if settings.app.demo_mode:
        return result

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
    db.commit()

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
            import json
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
            )
            db.add(generated)
            db.commit()
        except Exception:
            pass  # Don't fail the request if saving content fails

    cache_response(
        tenant_id=str(current_user.tenant_id),
        query=request.query,
        mode=ai_result["mode"],
        response=result,
        subject_id=request.subject_id or "",
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

    prepared_query, knowledge_context, hyde_query = await _prepare_ai_query(
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
