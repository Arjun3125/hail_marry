"""Student gamification — login streaks and achievement badges."""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from models.streak import LoginStreak


BADGES = [
    {"id": "first_login",    "name": "First Login",       "icon": "🏅", "threshold": 1,   "field": "current_streak"},
    {"id": "streak_3",       "name": "3-Day Streak",      "icon": "⚡", "threshold": 3,   "field": "current_streak"},
    {"id": "streak_7",       "name": "Week Warrior",      "icon": "🔥", "threshold": 7,   "field": "current_streak"},
    {"id": "streak_14",      "name": "Fortnight Focus",   "icon": "💪", "threshold": 14,  "field": "current_streak"},
    {"id": "streak_30",      "name": "30-Day Scholar",    "icon": "⭐", "threshold": 30,  "field": "current_streak"},
    {"id": "streak_100",     "name": "100-Day Champion",  "icon": "🏆", "threshold": 100, "field": "current_streak"},
    {"id": "sessions_10",    "name": "10 Sessions",       "icon": "📚", "threshold": 10,  "field": "total_sessions"},
    {"id": "sessions_50",    "name": "50 Sessions",       "icon": "🎓", "threshold": 50,  "field": "total_sessions"},
    {"id": "sessions_100",   "name": "Century Club",      "icon": "💯", "threshold": 100, "field": "total_sessions"},
    {"id": "longest_30",     "name": "All-Time 30",       "icon": "🌟", "threshold": 30,  "field": "longest_streak"},
]


def record_login(db: Session, user_id: UUID, tenant_id: UUID) -> LoginStreak:
    """Update the user's login streak. Call on each authenticated session."""
    today = date.today()
    streak = db.query(LoginStreak).filter(
        LoginStreak.user_id == user_id,
        LoginStreak.tenant_id == tenant_id,
    ).first()

    if not streak:
        streak = LoginStreak(
            user_id=user_id,
            tenant_id=tenant_id,
            current_streak=1,
            longest_streak=1,
            total_sessions=1,
            last_login_date=today,
        )
        db.add(streak)
        db.commit()
        db.refresh(streak)
        return streak

    if streak.last_login_date == today:
        # Already logged in today
        return streak

    if streak.last_login_date == today - timedelta(days=1):
        streak.current_streak += 1
    else:
        streak.current_streak = 1

    streak.longest_streak = max(streak.longest_streak, streak.current_streak)
    streak.total_sessions += 1
    streak.last_login_date = today
    db.commit()
    db.refresh(streak)
    return streak


def get_badges(streak: LoginStreak) -> list[dict[str, Any]]:
    """Return badges earned based on streak thresholds."""
    earned = []
    for badge in BADGES:
        value = getattr(streak, badge["field"], 0)
        if value >= badge["threshold"]:
            earned.append({
                "id": badge["id"],
                "name": badge["name"],
                "icon": badge["icon"],
                "earned": True,
            })
    return earned


def get_streak_info(db: Session, user_id: UUID, tenant_id: UUID) -> dict[str, Any]:
    """Return full streak + badge data for the student dashboard."""
    streak = db.query(LoginStreak).filter(
        LoginStreak.user_id == user_id,
        LoginStreak.tenant_id == tenant_id,
    ).first()

    if not streak:
        return {
            "current_streak": 0,
            "longest_streak": 0,
            "total_sessions": 0,
            "badges": [],
        }

    return {
        "current_streak": streak.current_streak,
        "longest_streak": streak.longest_streak,
        "total_sessions": streak.total_sessions,
        "last_login": str(streak.last_login_date) if streak.last_login_date else None,
        "badges": get_badges(streak),
    }
