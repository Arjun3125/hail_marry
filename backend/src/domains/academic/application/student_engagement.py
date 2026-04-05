"""Application helpers for student engagement and competitive workflows."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class StudentMockTestSubmissionError(Exception):
    status_code: int
    detail: str


def get_student_streak_overview(
    *,
    db,
    user_id,
    tenant_id,
    record_login_fn,
    get_streak_info_fn,
) -> dict[str, Any]:
    record_login_fn(db, user_id, tenant_id)
    return get_streak_info_fn(db, user_id, tenant_id)


def get_student_weakness_alerts(
    *,
    db,
    user_id,
    tenant_id,
    generate_weakness_alerts_fn,
) -> list[dict[str, Any]]:
    return generate_weakness_alerts_fn(db, user_id=user_id, tenant_id=tenant_id)


def list_student_test_series(
    *,
    db,
    tenant_id,
    get_all_series_fn,
) -> list[dict[str, Any]]:
    return get_all_series_fn(db, tenant_id=str(tenant_id))


def get_student_test_series_leaderboard(
    *,
    db,
    series_id: str,
    tenant_id,
    get_leaderboard_fn,
) -> dict[str, Any]:
    return get_leaderboard_fn(db, test_series_id=series_id, tenant_id=str(tenant_id))


def get_student_test_series_rank(
    *,
    db,
    series_id: str,
    student_id,
    tenant_id,
    get_student_rank_fn,
) -> dict[str, Any]:
    return get_student_rank_fn(
        db,
        test_series_id=series_id,
        student_id=str(student_id),
        tenant_id=str(tenant_id),
    )


def submit_student_mock_test(
    *,
    db,
    series_id: str,
    tenant_id,
    student_id,
    marks_obtained: float,
    time_taken_minutes: int | None,
    test_series_model,
    mock_test_attempt_model,
    calculate_rankings_fn,
) -> dict[str, Any]:
    series = (
        db.query(test_series_model)
        .filter(
            test_series_model.id == series_id,
            test_series_model.tenant_id == tenant_id,
            test_series_model.is_active,
        )
        .first()
    )
    if not series:
        raise StudentMockTestSubmissionError(404, "Test series not found")

    existing = (
        db.query(mock_test_attempt_model)
        .filter(
            mock_test_attempt_model.test_series_id == series_id,
            mock_test_attempt_model.student_id == student_id,
            mock_test_attempt_model.tenant_id == tenant_id,
        )
        .first()
    )
    if existing:
        raise StudentMockTestSubmissionError(409, "You have already attempted this test")

    attempt = mock_test_attempt_model(
        tenant_id=tenant_id,
        test_series_id=series.id,
        student_id=student_id,
        marks_obtained=marks_obtained,
        total_marks=series.total_marks,
        time_taken_minutes=time_taken_minutes,
    )
    db.add(attempt)
    db.commit()

    rankings = calculate_rankings_fn(db, test_series_id=series_id, tenant_id=str(tenant_id))
    my_rank = next((item for item in rankings if item["student_id"] == str(student_id)), None)

    return {
        "success": True,
        "attempt_id": str(attempt.id),
        "rank": my_rank["rank"] if my_rank else None,
        "percentile": my_rank["percentile"] if my_rank else None,
        "total_students": len(rankings),
    }
