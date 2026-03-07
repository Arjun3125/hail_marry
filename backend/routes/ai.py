"""AI query route orchestrating cache, quotas, logging, and AI execution."""
import time
import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from ai.cache import cache_response, get_cached_response
from auth.dependencies import get_current_user
from database import get_db
from models.ai_query import AIQuery
from models.tenant import Tenant
from models.user import User
from schemas.ai_runtime import AIQueryRequest, InternalAIQueryRequest
from services.ai_gateway import run_text_query
from services.webhooks import emit_webhook_event

router = APIRouter(prefix="/api/ai", tags=["AI"])


@router.post("/query")
async def ai_query(
    request: AIQueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
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

    cached = get_cached_response(
        tenant_id=str(current_user.tenant_id),
        query=request.query,
        mode=request.mode,
        subject_id=request.subject_id or "",
    )
    if cached:
        cached["cached"] = True
        return cached

    ai_result = await run_text_query(
        InternalAIQueryRequest(
            **request.model_dump(),
            tenant_id=str(current_user.tenant_id),
        ),
        trace_id=trace_id,
    )

    elapsed_ms = int((time.time() - start_time) * 1000)

    ai_log = AIQuery(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
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

    result = {
        "answer": ai_result["answer"],
        "citations": ai_result.get("citations", []),
        "trace_id": trace_id,
        "token_usage": ai_result.get("token_usage", 0),
        "response_time_ms": elapsed_ms,
        "mode": ai_result["mode"],
        "has_context": ai_result.get("has_context", True),
        "citation_valid": ai_result.get("citation_valid", False),
    }

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

    cache_response(
        tenant_id=str(current_user.tenant_id),
        query=request.query,
        mode=ai_result["mode"],
        response=result,
        subject_id=request.subject_id or "",
    )

    return result
