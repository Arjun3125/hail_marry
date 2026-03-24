"""Teacher class scoping helpers."""
from fastapi import Depends
from sqlalchemy.orm import Session

from database import get_db
from auth.dependencies import get_current_user
from src.domains.identity.models.user import User
from src.domains.academic.models.timetable import Timetable
from src.domains.academic.models.core import Class


def get_teacher_class_ids(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list:
    """
    Return class IDs the current user is allowed to access for teacher flows.
    - Teachers: only timetable-assigned classes.
    - Admins: all tenant classes.
    """
    if current_user.role == "admin":
        all_classes = db.query(Class.id).filter(
            Class.tenant_id == current_user.tenant_id,
        ).all()
        return [c[0] for c in all_classes]

    if current_user.role != "teacher":
        return []

    slots = db.query(Timetable.class_id).filter(
        Timetable.tenant_id == current_user.tenant_id,
        Timetable.teacher_id == current_user.id,
    ).distinct().all()
    return [slot[0] for slot in slots]
