"""Demo management routes — role switching, data reset, status."""
import os
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from database import get_db, Base, engine
from config import settings

router = APIRouter(prefix="/api/demo", tags=["Demo"])

DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() in ("true", "1", "yes")


@router.get("/status")
async def demo_status():
    """Return demo mode status and available roles."""
    return {
        "demo_mode": DEMO_MODE,
        "roles": ["student", "teacher", "admin", "parent"],
        "features": [
            "AI Assistant (13 modes)",
            "Audio Overview (Podcast)",
            "Video Overview (Slides)",
            "Interactive Mind Map",
            "Source Discovery",
            "Study Tools (Quiz, Flashcards, etc.)",
            "Attendance Tracking",
            "Marks & Results",
            "Timetable",
            "Assignments",
            "Teacher Assessment Generator",
            "Teacher Doubt Heatmap",
            "Parent Dashboard & Audio Report",
            "Admin Analytics & Settings",
            "Spaced Repetition Reviews",
        ],
    }


@router.post("/switch-role")
async def switch_role(data: dict, response: Response):
    """Switch the active demo role via cookie."""
    role = data.get("role", "student")
    if role not in ("student", "teacher", "admin", "parent"):
        role = "student"

    response.set_cookie(
        key="demo_role",
        value=role,
        httponly=False,  # readable by frontend
        samesite="lax",
        max_age=86400,
    )
    return {"role": role, "redirect": {
        "student": "/student/overview",
        "teacher": "/teacher/dashboard",
        "admin": "/admin/dashboard",
        "parent": "/parent/dashboard",
    }.get(role, "/")}


@router.post("/reset")
async def reset_demo(db: Session = Depends(get_db)):
    """Reset the demo database to its initial seeded state."""
    if not DEMO_MODE:
        return {"error": "Reset is only available in DEMO_MODE"}

    try:
        # Drop all tables and recreate
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

        # Re-run seed logic
        from demo_seed import seed_demo_data
        seed_demo_data(db)

        # Clear user cache
        from auth.dependencies import _demo_user_cache
        _demo_user_cache.clear()

        return {"status": "reset_complete", "message": "Demo environment restored to initial state"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
