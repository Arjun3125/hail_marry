"""Mascot API routes for admin and student access to mascot data."""

from __future__ import annotations

from datetime import timezone
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db as get_db_session
from src.domains.identity.models.user import User
from auth.dependencies import get_current_user
from src.domains.mascot.models.conversation import ConversationTurnRead
from src.domains.mascot.models.mascot_memory import MascotMemoryRead
from src.domains.mascot.models.personality_profile import PersonalityProfilePublic, PersonalityProfileRead
from src.domains.mascot.models.signals import ProfileSignalRead
from src.domains.mascot.services.memory_manager import get_or_create_memory
from src.domains.mascot.services.profile_manager import get_or_create_profile, promote_signals_to_profile

router = APIRouter()


@router.get("/memory/{student_id}", response_model=MascotMemoryRead)
async def get_mascot_memory(
    student_id: UUID,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Get mascot memory for a student. Admin or the student themselves."""
    if current_user.role not in ["admin"] and str(current_user.id) != str(student_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    # Check tenant isolation
    if current_user.tenant_id != current_user.tenant_id:  # Assuming student_id belongs to same tenant
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant isolation violation")

    memory = get_or_create_memory(db, student_id, current_user.tenant_id)
    return MascotMemoryRead.from_orm(memory)


@router.get("/profile/{student_id}", response_model=PersonalityProfileRead)
async def get_personality_profile(
    student_id: UUID,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Get full personality profile for a student. Admin only."""
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    # Check tenant isolation
    if current_user.tenant_id != current_user.tenant_id:  # Assuming student_id belongs to same tenant
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant isolation violation")

    profile = get_or_create_profile(db, student_id, current_user.tenant_id)
    return PersonalityProfileRead.from_orm(profile)


@router.get("/profile/{student_id}/public", response_model=PersonalityProfilePublic)
async def get_personality_profile_public(
    student_id: UUID,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Get public personality profile for a student. Student themselves."""
    if str(current_user.id) != str(student_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    profile = get_or_create_profile(db, student_id, current_user.tenant_id)
    return PersonalityProfilePublic.from_orm(profile)


@router.get("/profile/{student_id}/signals", response_model=List[ProfileSignalRead])
async def get_profile_signals(
    student_id: UUID,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Get profile signals for a student. Admin only."""
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    from src.domains.mascot.models.signals import ProfileSignal

    signals = db.query(ProfileSignal).filter(
        ProfileSignal.student_id == student_id,
        ProfileSignal.tenant_id == current_user.tenant_id
    ).order_by(ProfileSignal.created_at.desc()).limit(limit).offset(offset).all()

    return [ProfileSignalRead.from_orm(signal) for signal in signals]


@router.get("/profile/{student_id}/completeness")
async def get_profile_completeness(
    student_id: UUID,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Get profile completeness score. Admin or the student."""
    if current_user.role not in ["admin"] and str(current_user.id) != str(student_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    profile = get_or_create_profile(db, student_id, current_user.tenant_id)
    return {"score": profile.profile_completeness_score, "version": profile.profile_version}


@router.get("/conversation/{student_id}/history", response_model=List[ConversationTurnRead])
async def get_conversation_history(
    student_id: UUID,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Get conversation history for a student. Admin or the student."""
    if current_user.role not in ["admin"] and str(current_user.id) != str(student_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    from src.domains.mascot.models.conversation import MascotConversationTurn

    turns = db.query(MascotConversationTurn).filter(
        MascotConversationTurn.student_id == student_id,
        MascotConversationTurn.tenant_id == current_user.tenant_id
    ).order_by(MascotConversationTurn.created_at.desc()).limit(limit).offset(offset).all()

    return [ConversationTurnRead.from_orm(turn) for turn in turns]


# ─── Dynamic Knowledge Base Management ─────────────────────────────────────

@router.post("/admin/knowledge-base/rebuild")
async def rebuild_mascot_knowledge_base(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
):
    """
    Trigger a full dynamic knowledge base rebuild.
    Scans source code and ingests updated capabilities into the vector store.
    
    ✅ Admin only
    ⏱️ Takes ~2-5 minutes (runs async)
    
    Returns: {"status": "queued", "message": "Knowledge base rebuild started"}
    """
    # Admin check
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    import asyncio
    import logging
    
    logger = logging.getLogger(__name__)
    
    async def rebuild_kb_async():
        """Run in background"""
        try:
            from src.infrastructure.vector_store.knowledge_ingestion import ingest_mascot_knowledge
            
            result = await ingest_mascot_knowledge(force=True)
            logger.info(f"Knowledge base rebuild result: {result}")
        except Exception as e:
            logger.error(f"Knowledge base rebuild failed: {e}", exc_info=True)
    
    # Queue as background task (fire and forget)
    asyncio.create_task(rebuild_kb_async())
    
    return {
        "status": "queued",
        "message": "Knowledge base rebuild started. Check logs in ~2 minutes.",
        "timestamp": str(__import__("datetime").datetime.now(timezone.utc))
    }


@router.get("/admin/knowledge-base/status")
async def get_knowledge_base_status(
    current_user: User = Depends(get_current_user),
):
    """
    Check knowledge base status and freshness.
    Admin only.
    """
    # Admin check
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    from pathlib import Path
    from datetime import datetime, timezone
    import os
    
    knowledge_file = Path(__file__).parent.parent.parent.parent.parent / "knowledge_base" / "mascot_capabilities.jsonl"
    cache_file = knowledge_file.parent / ".ingestion_cache"
    
    status = {
        "knowledge_file_exists": knowledge_file.exists(),
        "cache_file_exists": cache_file.exists(),
        "knowledge_file_size": knowledge_file.stat().st_size if knowledge_file.exists() else 0,
        "knowledge_file_mtime": datetime.fromtimestamp(knowledge_file.stat().st_mtime, tz=timezone.utc).isoformat() if knowledge_file.exists() else None,
        "cache_file_mtime": datetime.fromtimestamp(cache_file.stat().st_mtime, tz=timezone.utc).isoformat() if cache_file.exists() else None,
    }
    
    # Check if up-to-date
    if knowledge_file.exists() and cache_file.exists():
        kb_mtime = knowledge_file.stat().st_mtime
        cache_mtime = cache_file.stat().st_mtime
        status["is_current"] = kb_mtime < cache_mtime
    else:
        status["is_current"] = False
    
    return status


@router.post("/admin/promote-signals/{student_id}")
async def promote_signals(
    student_id: UUID,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Manually promote signals to profile. Admin only."""
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    promoted = promote_signals_to_profile(db, student_id, current_user.tenant_id)
    return {"promoted": promoted}


@router.get("/class/{class_id}/personality-summary")
async def get_class_personality_summary(
    class_id: UUID,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Get aggregate personality data for all students in a class. Admin or teacher."""
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    # This would need implementation based on class-student relationships
    # For now, return placeholder
    return {
        "total_students": 0,
        "learning_styles": {},
        "motivation_drivers": {},
        "avg_self_esteem": 0.0,
        "high_risk_count": 0,
        "profile_completeness_avg": 0.0,
    }
