"""Leaderboard ranking service for competitive exam test series."""
import uuid as _uuid
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from src.domains.academic.models.test_series import TestSeries, MockTestAttempt
from src.domains.identity.models.user import User


def _to_uuid(value):
    """Convert a string to uuid.UUID if needed (SQLite compatibility)."""
    if isinstance(value, _uuid.UUID):
        return value
    return _uuid.UUID(str(value))


def calculate_rankings(db: Session, test_series_id: str, tenant_id: str) -> list[dict]:
    """Calculate and store rankings for all attempts in a test series.

    Rankings are based on:
    1. Highest percentage score
    2. Time taken (less is better)

    Returns ordered list of ranked students.
    """
    attempts = db.query(MockTestAttempt).filter(
        MockTestAttempt.test_series_id == _to_uuid(test_series_id),
        MockTestAttempt.tenant_id == _to_uuid(tenant_id),
    ).all()

    if not attempts:
        return []

    # Sort: highest percentage first, then lowest time
    scored = []
    for a in attempts:
        pct = (a.marks_obtained / a.total_marks * 100) if a.total_marks > 0 else 0
        scored.append({"attempt": a, "pct": pct})

    scored.sort(key=lambda x: (-x["pct"], x["attempt"].time_taken_minutes or 999))

    total = len(scored)
    results = []
    for rank_idx, item in enumerate(scored, start=1):
        attempt = item["attempt"]
        attempt.rank = rank_idx
        # Percentile = % of students you scored better than
        attempt.percentile = round((total - rank_idx) / total * 100, 1) if total > 1 else 100.0
        results.append({
            "rank": rank_idx,
            "student_id": str(attempt.student_id),
            "marks_obtained": attempt.marks_obtained,
            "total_marks": attempt.total_marks,
            "pct": round(item["pct"], 1),
            "percentile": attempt.percentile,
            "time_taken_minutes": attempt.time_taken_minutes,
        })

    db.commit()
    return results


def get_leaderboard(db: Session, test_series_id: str, tenant_id: str, limit: int = 50) -> dict:
    """Get the leaderboard for a test series with student names."""
    series = db.query(TestSeries).filter(
        TestSeries.id == _to_uuid(test_series_id),
        TestSeries.tenant_id == _to_uuid(tenant_id),
    ).first()

    if not series:
        return {"error": "Test series not found"}

    attempts = db.query(MockTestAttempt, User.full_name, User.email).join(
        User, MockTestAttempt.student_id == User.id,
    ).filter(
        MockTestAttempt.test_series_id == _to_uuid(test_series_id),
        MockTestAttempt.tenant_id == _to_uuid(tenant_id),
    ).order_by(MockTestAttempt.rank.asc().nullslast()).limit(limit).all()

    return {
        "series_name": series.name,
        "total_marks": series.total_marks,
        "total_attempts": len(attempts),
        "leaderboard": [{
            "rank": a.rank or idx + 1,
            "student_name": name or email,
            "student_id": str(a.student_id),
            "marks_obtained": a.marks_obtained,
            "total_marks": a.total_marks,
            "percentile": a.percentile,
            "pct": round(a.marks_obtained / a.total_marks * 100, 1) if a.total_marks > 0 else 0,
            "time_taken": a.time_taken_minutes,
        } for idx, (a, name, email) in enumerate(attempts)],
    }


def get_student_rank(db: Session, test_series_id: str, student_id: str, tenant_id: str) -> dict:
    """Get a specific student's rank in a test series."""
    attempt = db.query(MockTestAttempt).filter(
        MockTestAttempt.test_series_id == _to_uuid(test_series_id),
        MockTestAttempt.student_id == _to_uuid(student_id),
        MockTestAttempt.tenant_id == _to_uuid(tenant_id),
    ).first()

    if not attempt:
        return {"rank": None, "message": "No attempt found for this test"}

    total_attempts = db.query(MockTestAttempt).filter(
        MockTestAttempt.test_series_id == _to_uuid(test_series_id),
        MockTestAttempt.tenant_id == _to_uuid(tenant_id),
    ).count()

    pct = round(attempt.marks_obtained / attempt.total_marks * 100, 1) if attempt.total_marks > 0 else 0

    return {
        "rank": attempt.rank,
        "total_students": total_attempts,
        "marks_obtained": attempt.marks_obtained,
        "total_marks": attempt.total_marks,
        "percentile": attempt.percentile,
        "pct": pct,
    }


def get_all_series(db: Session, tenant_id: str) -> list[dict]:
    """Get all active test series for a tenant with attempt counts."""
    series_list = db.query(TestSeries).filter(
        TestSeries.tenant_id == _to_uuid(tenant_id),
        TestSeries.is_active == True,
    ).order_by(desc(TestSeries.created_at)).all()

    results = []
    for s in series_list:
        attempt_count = db.query(MockTestAttempt).filter(
            MockTestAttempt.test_series_id == s.id,
            MockTestAttempt.tenant_id == _to_uuid(tenant_id),
        ).count()
        results.append({
            "id": str(s.id),
            "name": s.name,
            "description": s.description,
            "total_marks": s.total_marks,
            "duration_minutes": s.duration_minutes,
            "attempts": attempt_count,
            "created_at": str(s.created_at),
        })
    return results
