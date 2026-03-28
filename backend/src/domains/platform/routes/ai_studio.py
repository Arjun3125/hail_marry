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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    # Get last session stats
    session = db.query(StudySession).filter(
        StudySession.tenant_id == current_user.tenant_id,
        StudySession.user_id == current_user.id,
    ).order_by(StudySession.last_active_at.desc()).first()
    
    # Get last query
    last_query = db.query(AIQuery).filter(
        AIQuery.tenant_id == current_user.tenant_id,
        AIQuery.user_id == current_user.id,
    ).order_by(AIQuery.created_at.desc()).first()
    
    suggestions: list[dict[str, Any]] = []
    
    time_spent = session.duration_seconds // 60 if session else 0
    q_answered = session.questions_answered if session else 0
    query_text = last_query.query_text if last_query else None
    
    # Suggest knowledge tests
    if query_text:
        suggestions.append({
            "id": "1",
            "type": "quiz",
            "title": "Test your understanding",
            "description": f"Create a quiz about an aspect of '{query_text[:30]}...'",
            "confidence": 85,
        })
        suggestions.append({
            "id": "2",
            "type": "flashcards",
            "title": "Make study cards",
            "description": "Extract key facts for spaced repetition",
            "confidence": 75,
        })
        
    if time_spent > 10 and q_answered > 3:
        suggestions.append({
            "id": "3",
            "type": "practice",
            "title": "Take a break?",
            "description": f"You've been studying for {time_spent} minutes",
            "confidence": 60,
        })
        
    if not suggestions:
        suggestions.append({
            "id": "welcome",
            "type": "deep_dive",
            "title": "Start your session",
            "description": "Ask a question about your study materials",
            "confidence": 95,
        })
        
    return suggestions[:3]
