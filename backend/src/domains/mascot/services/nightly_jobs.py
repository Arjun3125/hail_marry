"""Background jobs for mascot system maintenance."""

from __future__ import annotations

import logging
from typing import Dict

from sqlalchemy.orm import Session

from database import get_db as get_db_session
from src.domains.mascot.services.profile_manager import promote_signals_to_profile

logger = logging.getLogger(__name__)


async def run_mascot_nightly_jobs() -> Dict[str, int]:
    """
    Runs once per night. Processes all students with unpromoted signals.

    Steps:
    1. Open a DB session
    2. Query all distinct student_ids from profile_signals
       WHERE promoted_to_profile = false
       GROUP BY student_id, tenant_id
    3. For each student, call profile_manager.promote_signals_to_profile()
    4. Log the count of students processed and total signals promoted
    5. Close DB session
    6. Return {"students_processed": int, "signals_promoted": int}

    Wrap entire function in try/except — never crash the worker.
    Log all errors with logger.exception().
    """
    try:
        db: Session = next(get_db_session())

        # Get distinct student_ids with unpromoted signals
        from src.domains.mascot.models.signals import ProfileSignal

        student_query = db.query(
            ProfileSignal.student_id,
            ProfileSignal.tenant_id
        ).filter(
            ProfileSignal.promoted_to_profile.is_(False)
        ).distinct().all()

        students_processed = 0
        total_signals_promoted = 0

        for student_id, tenant_id in student_query:
            try:
                promoted = promote_signals_to_profile(db, student_id, tenant_id)
                total_signals_promoted += promoted
                students_processed += 1
            except Exception as e:
                logger.exception(f"Failed to promote signals for student {student_id}: {e}")

        logger.info(f"Mascot nightly jobs: processed {students_processed} students, promoted {total_signals_promoted} signals")
        return {"students_processed": students_processed, "signals_promoted": total_signals_promoted}

    except Exception as e:
        logger.exception(f"Mascot nightly jobs failed: {e}")
        return {"students_processed": 0, "signals_promoted": 0}


async def run_context_snapshot_refresh(student_id: str, tenant_id: str,
                                        student_name: str) -> None:
    """
    Refreshes the context_snapshot JSONB column in student_mascot_memory.
    Called before the first message of the day for active students.
    This pre-assembles context so the first mascot response is instant.
    """
    try:
        from uuid import UUID
        from src.domains.mascot.models.mascot_memory import MascotMemoryUpdate
        from src.domains.mascot.services.context_assembler import assemble_context
        from src.domains.mascot.services.memory_manager import update_memory

        db: Session = next(get_db_session())
        context = assemble_context(db, UUID(student_id), UUID(tenant_id), student_name)

        # Update memory with new context snapshot
        update_data = MascotMemoryUpdate(context_snapshot=context.__dict__)
        update_memory(db, UUID(student_id), UUID(tenant_id), update_data)

    except Exception as e:
        logger.exception(f"Failed to refresh context snapshot for student {student_id}: {e}")
