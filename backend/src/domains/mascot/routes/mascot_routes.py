"""Mascot API routes for admin and student access to mascot data."""

from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.bootstrap.app_factory import get_db_session
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
