"""Memory management service for mascot conversation state."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Mapping, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from ..models.mascot_memory import StudentMascotMemory, MascotMemoryUpdate


def get_or_create_memory(db: Session, student_id: UUID, tenant_id: UUID) -> StudentMascotMemory:
    """
    Query student_mascot_memory WHERE student_id=student_id AND tenant_id=tenant_id.
    If not found, create a new record with defaults and commit.
    Return the record.
    """
    memory = db.query(StudentMascotMemory).filter(
        StudentMascotMemory.student_id == student_id,
        StudentMascotMemory.tenant_id == tenant_id
    ).first()

    if not memory:
        memory = StudentMascotMemory(
            student_id=student_id,
            tenant_id=tenant_id,
            total_interactions=0,
            mascot_tone_setting="encouraging"
        )
        db.add(memory)
        db.commit()
        db.refresh(memory)

    return memory


def update_memory(db: Session, student_id: UUID, tenant_id: UUID,
                  update: MascotMemoryUpdate | Mapping[str, object]) -> StudentMascotMemory:
    """
    Fetch existing record (create if missing).
    Apply all non-None fields from update using setattr.
    Set updated_at to now(timezone.utc).
    Commit and refresh. Return record.
    """
    memory = get_or_create_memory(db, student_id, tenant_id)

    if isinstance(update, Mapping):
        update = MascotMemoryUpdate(**update)

    for field, value in update.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(memory, field, value)

    memory.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(memory)
    return memory


def increment_interaction_count(db: Session, student_id: UUID,
                                tenant_id: UUID) -> None:
    """
    Increment total_interactions by 1 and set last_interaction_at to now.
    Commit. No return needed.
    """
    memory = get_or_create_memory(db, student_id, tenant_id)
    memory.total_interactions += 1
    memory.last_interaction_at = datetime.now(timezone.utc)
    memory.updated_at = datetime.now(timezone.utc)
    db.commit()


def save_session_summary(db: Session, student_id: UUID, tenant_id: UUID,
                         summary: str, emotional_state: str) -> None:
    """
    Update last_summary and last_emotional_state in memory record.
    Commit.
    """
    memory = get_or_create_memory(db, student_id, tenant_id)
    memory.last_summary = summary
    memory.last_emotional_state = emotional_state
    memory.updated_at = datetime.now(timezone.utc)
    db.commit()


def get_days_since_last_interaction(db: Session, student_id: UUID,
                                    tenant_id: UUID) -> Optional[int]:
    """
    Return None if no prior interaction. Else return (now - last_interaction_at).days
    """
    memory = db.query(StudentMascotMemory).filter(
        StudentMascotMemory.student_id == student_id,
        StudentMascotMemory.tenant_id == tenant_id
    ).first()

    if not memory or not memory.last_interaction_at:
        return None

    now = datetime.now(timezone.utc)
    return (now - memory.last_interaction_at).days
