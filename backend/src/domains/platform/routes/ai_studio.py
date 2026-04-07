"""Routes for AI Studio session tracking and smart suggestions."""

import uuid
from typing import Any
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from auth.dependencies import get_current_user
from database import get_db
from src.domains.identity.models.user import User
from src.domains.platform.models.study_session import StudySession
from src.domains.platform.models.ai import AIQuery
from src.domains.platform.services import (
    mastery_tracking_service,
)
from src.domains.platform.models.topic_mastery import TopicMastery

router = APIRouter(prefix="/api/ai-studio", tags=["AI Studio"])

class SessionStartRequest(BaseModel):
    topic: str | None = None

class SessionStartResponse(BaseModel):
    session_id: uuid.UUID

class SessionHeartbeatRequest(BaseModel):
    duration_increment_seconds: int
    questions_answered_increment: int

@router.post("/sessions", response_model=SessionStartResponse)
async def start_session(
    request: SessionStartRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = StudySession(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        topic=request.topic,
        duration_seconds=0,
        questions_answered=0,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return {"session_id": session.id}

@router.put("/sessions/{session_id}")
async def heartbeat_session(
    session_id: uuid.UUID,
    request: SessionHeartbeatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = db.query(StudySession).filter(
        StudySession.id == session_id,
        StudySession.tenant_id == current_user.tenant_id,
        StudySession.user_id == current_user.id,
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Study session not found")
        
    session.duration_seconds += request.duration_increment_seconds
    session.questions_answered += request.questions_answered_increment
    session.last_active_at = datetime.now(timezone.utc)
    
    db.commit()
    return {"status": "ok"}

@router.get("/suggestions")
async def get_smart_suggestions(
    notebook_id: uuid.UUID | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    # 1. Get recent context
    session = db.query(StudySession).filter(
        StudySession.tenant_id == current_user.tenant_id,
        StudySession.user_id == current_user.id,
    ).order_by(StudySession.last_active_at.desc()).first()
    
    last_query = db.query(AIQuery).filter(
        AIQuery.tenant_id == current_user.tenant_id,
        AIQuery.user_id == current_user.id,
    ).order_by(AIQuery.created_at.desc()).first()
    
    # 2. Build profile-aware recommendations
    recommendations = mastery_tracking_service.build_profile_aware_recommendations(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        notebook_id=notebook_id,
        current_surface="ai_studio",
        current_topic=session.topic if session else None,
        current_query=last_query.query_text if last_query else None,
        limit=4
    )
    
    # 3. Augment with confidence and metadata for UI compatibility
    return [
        {
            "id": rec.get("id", str(uuid.uuid4())),
            "type": rec.get("target_tool", "quiz"),
            "title": rec.get("label", "Next Step"),
            "description": rec.get("description", "Continue your study session"),
            "prompt": rec.get("prompt"),
            "reason": rec.get("reason"),
            "priority": rec.get("priority", "medium"),
            "confidence": 90 if rec.get("priority") == "high" else 75
        }
        for rec in recommendations
    ]

@router.get("/mastery")
async def get_student_mastery(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    mastery_records = db.query(TopicMastery).filter(
        TopicMastery.tenant_id == current_user.tenant_id,
        TopicMastery.user_id == current_user.id,
    ).order_by(TopicMastery.mastery_score.asc()).limit(10).all()
    
    return [
        {
            "topic": record.topic,
            "score": record.mastery_score,
            "level": "novice" if record.mastery_score < 40 else "intermediate" if record.mastery_score < 80 else "master",
            "last_activity": record.updated_at.isoformat()
        }
        for record in mastery_records
    ]
