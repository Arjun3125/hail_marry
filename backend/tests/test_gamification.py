"""Tests for services/gamification.py — streak tracking and badge logic."""
import os
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch
from uuid import uuid4

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ["DEBUG"] = "true"


class FakeStreak:
    """Minimal LoginStreak stand-in for unit tests."""
    def __init__(self, current_streak=0, longest_streak=0, total_sessions=0, last_login_date=None):
        self.current_streak = current_streak
        self.longest_streak = longest_streak
        self.total_sessions = total_sessions
        self.last_login_date = last_login_date


class GetBadgesTests(unittest.TestCase):
    def test_no_badges_at_zero(self):
        from src.domains.academic.services.gamification import get_badges
        streak = FakeStreak(current_streak=0, total_sessions=0, longest_streak=0)
        badges = get_badges(streak)
        self.assertEqual(badges, [])

    def test_first_login_badge(self):
        from src.domains.academic.services.gamification import get_badges
        streak = FakeStreak(current_streak=1, total_sessions=1, longest_streak=1)
        badge_ids = [b["id"] for b in get_badges(streak)]
        self.assertIn("first_login", badge_ids)

    def test_7_day_streak_badges(self):
        from src.domains.academic.services.gamification import get_badges
        streak = FakeStreak(current_streak=7, total_sessions=7, longest_streak=7)
        badge_ids = [b["id"] for b in get_badges(streak)]
        self.assertIn("first_login", badge_ids)
        self.assertIn("streak_3", badge_ids)
        self.assertIn("streak_7", badge_ids)
        self.assertNotIn("streak_14", badge_ids)

    def test_100_sessions_badge(self):
        from src.domains.academic.services.gamification import get_badges
        streak = FakeStreak(current_streak=1, total_sessions=100, longest_streak=5)
        badge_ids = [b["id"] for b in get_badges(streak)]
        self.assertIn("sessions_100", badge_ids)
        self.assertIn("sessions_50", badge_ids)
        self.assertIn("sessions_10", badge_ids)

    def test_all_badges_at_max(self):
        from src.domains.academic.services.gamification import get_badges, BADGES
        streak = FakeStreak(current_streak=100, total_sessions=100, longest_streak=100)
        badges = get_badges(streak)
        self.assertEqual(len(badges), len(BADGES))


class GetStreakInfoTests(unittest.TestCase):
    def test_no_streak_returns_defaults(self):
        from src.domains.academic.services.gamification import get_streak_info
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None
        info = get_streak_info(db, uuid4(), uuid4())
        self.assertEqual(info["current_streak"], 0)
        self.assertEqual(info["badges"], [])

    def test_existing_streak_returns_data(self):
        from src.domains.academic.services.gamification import get_streak_info
        db = MagicMock()
        fake = FakeStreak(current_streak=5, longest_streak=10, total_sessions=20, last_login_date=date.today())
        db.query.return_value.filter.return_value.first.return_value = fake
        info = get_streak_info(db, uuid4(), uuid4())
        self.assertEqual(info["current_streak"], 5)
        self.assertEqual(info["longest_streak"], 10)
        self.assertEqual(info["total_sessions"], 20)
        self.assertTrue(len(info["badges"]) > 0)


if __name__ == "__main__":
    unittest.main()
