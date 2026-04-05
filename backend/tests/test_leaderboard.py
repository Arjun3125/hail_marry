"""Tests for the leaderboard service."""
from unittest.mock import MagicMock
from uuid import uuid4

from src.domains.academic.services.leaderboard import calculate_rankings, get_leaderboard, get_student_rank


class TestCalculateRankings:
    """Test leaderboard ranking calculation."""

    def test_empty_attempts_returns_empty(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.all.return_value = []
        result = calculate_rankings(db, str(uuid4()), str(uuid4()))
        assert result == []

    def test_single_attempt_gets_rank_1(self):
        db = MagicMock()
        attempt = MagicMock()
        attempt.marks_obtained = 80
        attempt.total_marks = 100
        attempt.time_taken_minutes = 45
        attempt.student_id = uuid4()
        attempt.rank = None
        attempt.percentile = None

        db.query.return_value.filter.return_value.all.return_value = [attempt]

        result = calculate_rankings(db, str(uuid4()), str(uuid4()))
        assert len(result) == 1
        assert result[0]["rank"] == 1
        assert attempt.rank == 1

    def test_multiple_attempts_ranked_by_score(self):
        db = MagicMock()

        top = MagicMock()
        top.marks_obtained = 95
        top.total_marks = 100
        top.time_taken_minutes = 30
        top.student_id = uuid4()
        top.rank = None
        top.percentile = None

        mid = MagicMock()
        mid.marks_obtained = 70
        mid.total_marks = 100
        mid.time_taken_minutes = 40
        mid.student_id = uuid4()
        mid.rank = None
        mid.percentile = None

        low = MagicMock()
        low.marks_obtained = 50
        low.total_marks = 100
        low.time_taken_minutes = 55
        low.student_id = uuid4()
        low.rank = None
        low.percentile = None

        db.query.return_value.filter.return_value.all.return_value = [top, mid, low]

        result = calculate_rankings(db, str(uuid4()), str(uuid4()))
        assert len(result) == 3
        assert result[0]["rank"] == 1
        assert result[1]["rank"] == 2
        assert result[2]["rank"] == 3

    def test_zero_total_marks_no_division_error(self):
        db = MagicMock()
        attempt = MagicMock()
        attempt.marks_obtained = 0
        attempt.total_marks = 0
        attempt.time_taken_minutes = 10
        attempt.student_id = uuid4()
        attempt.rank = None
        attempt.percentile = None

        db.query.return_value.filter.return_value.all.return_value = [attempt]
        result = calculate_rankings(db, str(uuid4()), str(uuid4()))
        assert result[0]["pct"] == 0


class TestGetLeaderboard:
    """Test leaderboard retrieval."""

    def test_default_limit_is_50(self):
        import inspect
        sig = inspect.signature(get_leaderboard)
        assert sig.parameters["limit"].default == 50

    def test_series_not_found(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None
        result = get_leaderboard(db, str(uuid4()), str(uuid4()))
        assert "error" in result


class TestGetStudentRank:
    """Test individual student rank lookup."""

    def test_no_attempt_found(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None
        result = get_student_rank(db, str(uuid4()), str(uuid4()), str(uuid4()))
        assert result["rank"] is None
