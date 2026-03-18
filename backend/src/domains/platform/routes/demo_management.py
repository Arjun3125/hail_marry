"""Demo management routes — role switching, data reset, status."""
import os
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from database import get_db, Base, engine
from config import settings

router = APIRouter(prefix="/api/demo", tags=["Demo"])

DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() in ("true", "1", "yes")


def _cookie_policy() -> tuple[bool, str]:
    app_env = (settings.app.env or "").lower()
    if app_env in {"production", "prod", "staging"}:
        return True, "none"
    return (not settings.app.debug), "lax"


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


@router.get("/profiles")
async def demo_profiles(db: Session = Depends(get_db)):
    """Return demo personas plus role-specific walkthrough steps."""
    from src.domains.identity.models.user import User

    role_order = ["student", "teacher", "admin", "parent"]
    users = db.query(User).filter(User.role.in_(role_order), User.is_active == True).all()
    user_by_role = {u.role: u for u in users}

    profile_templates = [
        {
            "role": "student",
            "persona": "Student Learner",
            "landing_path": "/student/overview",
            "feature_showcase": [
                "Dashboard KPIs",
                "AI chat with citations",
                "Study tools (quiz, flashcards, mind map, flowchart)",
                "Spaced repetition reviews",
                "Assignments and uploads",
            ],
            "walkthrough": [
                {
                    "step": 1,
                    "title": "Open Student Dashboard",
                    "path": "/student/overview",
                    "outcome": "See attendance, marks trend, pending assignments, and AI usage.",
                },
                {
                    "step": 2,
                    "title": "Try AI Assistant",
                    "path": "/student/ai",
                    "outcome": "Ask a curriculum question and verify grounded response + citations.",
                },
                {
                    "step": 3,
                    "title": "Generate Study Tools",
                    "path": "/student/tools",
                    "outcome": "Create a quiz/flashcards/mind map from a topic.",
                },
                {
                    "step": 4,
                    "title": "Review Planner",
                    "path": "/student/reviews",
                    "outcome": "Check due review cards and mark completion with self-rating.",
                },
            ],
        },
        {
            "role": "teacher",
            "persona": "Class Teacher",
            "landing_path": "/teacher/dashboard",
            "feature_showcase": [
                "Class overview",
                "Attendance and marks entry",
                "Assignment creation",
                "Assessment generation",
                "Doubt heatmap and insights",
            ],
            "walkthrough": [
                {
                    "step": 1,
                    "title": "Open Teacher Dashboard",
                    "path": "/teacher/dashboard",
                    "outcome": "View classes, student counts, attendance %, and average marks.",
                },
                {
                    "step": 2,
                    "title": "Take Attendance",
                    "path": "/teacher/attendance",
                    "outcome": "Submit class attendance and verify records update.",
                },
                {
                    "step": 3,
                    "title": "Create Assignment",
                    "path": "/teacher/assignments",
                    "outcome": "Create and list assignments tied to class subjects.",
                },
                {
                    "step": 4,
                    "title": "Generate Assessment",
                    "path": "/teacher/generate-assessment",
                    "outcome": "Generate MCQs from topic + subject context.",
                },
            ],
        },
        {
            "role": "admin",
            "persona": "School Admin",
            "landing_path": "/admin/dashboard",
            "feature_showcase": [
                "Institution KPI dashboard",
                "User and role management",
                "Complaints oversight",
                "AI usage analytics + review",
                "Settings, reports, webhooks, audit logs",
            ],
            "walkthrough": [
                {
                    "step": 1,
                    "title": "Open Admin Dashboard",
                    "path": "/admin/dashboard",
                    "outcome": "See school KPIs: active users, AI usage, attendance, performance.",
                },
                {
                    "step": 2,
                    "title": "Review Users",
                    "path": "/admin/users",
                    "outcome": "Inspect users and role assignment state.",
                },
                {
                    "step": 3,
                    "title": "Handle Complaints",
                    "path": "/admin/complaints",
                    "outcome": "Track and resolve student complaints.",
                },
                {
                    "step": 4,
                    "title": "Check AI Analytics",
                    "path": "/admin/ai-usage",
                    "outcome": "Review query volume, heavy users, and adoption trends.",
                },
            ],
        },
        {
            "role": "parent",
            "persona": "Parent Guardian",
            "landing_path": "/parent/dashboard",
            "feature_showcase": [
                "Child progress dashboard",
                "Attendance visibility",
                "Exam results overview",
                "Audio report summary",
            ],
            "walkthrough": [
                {
                    "step": 1,
                    "title": "Open Parent Dashboard",
                    "path": "/parent/dashboard",
                    "outcome": "See child attendance %, average marks, and pending assignments.",
                },
                {
                    "step": 2,
                    "title": "View Attendance and Results",
                    "path": "/parent/attendance",
                    "outcome": "Review detailed day-wise attendance and subject-wise performance.",
                },
                {
                    "step": 3,
                    "title": "Play Progress Report",
                    "path": "/parent/reports",
                    "outcome": "Use generated summary for quick parent-friendly progress updates.",
                },
            ],
        },
    ]

    profiles = []
    for template in profile_templates:
        role = template["role"]
        user = user_by_role.get(role)
        profiles.append(
            {
                "role": role,
                "persona": user.full_name if user and user.full_name else template["persona"],
                "email": user.email if user else None,
                "landing_path": template["landing_path"],
                "feature_showcase": template["feature_showcase"],
                "walkthrough": template["walkthrough"],
            }
        )

    return {
        "demo_mode": DEMO_MODE,
        "profiles": profiles,
        "notes": [
            "Use 'Demo: Login as <Role>' or the Demo page role cards to switch persona.",
            "If data gets modified, use /api/demo/reset (or Demo toolbar reset) to restore baseline data.",
        ],
    }


@router.post("/switch-role")
async def switch_role(data: dict, response: Response):
    """Switch the active demo role via cookie."""
    role = data.get("role", "student")
    if role not in ("student", "teacher", "admin", "parent"):
        role = "student"
    cookie_secure, cookie_samesite = _cookie_policy()

    response.set_cookie(
        key="demo_role",
        value=role,
        httponly=False,  # readable by frontend
        secure=cookie_secure,
        samesite=cookie_samesite,
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
