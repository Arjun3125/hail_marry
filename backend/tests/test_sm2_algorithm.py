"""Tests for the SM-2 spaced repetition algorithm in routes/students.py."""
import os
import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ["DEBUG"] = "true"

from routes.students import _sm2_update


class SM2AlgorithmTests(unittest.TestCase):
    """Verify SM-2 interval and ease factor calculations."""

    def test_rating_1_resets_interval_and_decreases_ease(self):
        interval, ef = _sm2_update(10, 2.5, 1)
        self.assertEqual(interval, 1)
        self.assertAlmostEqual(ef, 2.3)

    def test_rating_2_resets_interval_and_decreases_ease(self):
        interval, ef = _sm2_update(10, 2.5, 2)
        self.assertEqual(interval, 1)
        self.assertAlmostEqual(ef, 2.3)

    def test_rating_below_3_ease_never_below_min(self):
        interval, ef = _sm2_update(5, 1.3, 1)
        self.assertEqual(interval, 1)
        self.assertEqual(ef, 1.3)

    def test_rating_3_interval_0_becomes_1(self):
        interval, ef = _sm2_update(0, 2.5, 3)
        self.assertEqual(interval, 1)
        self.assertGreaterEqual(ef, 1.3)

    def test_rating_3_interval_1_becomes_6(self):
        interval, ef = _sm2_update(1, 2.5, 3)
        self.assertEqual(interval, 6)
        self.assertGreaterEqual(ef, 1.3)

    def test_rating_3_interval_6_multiplies_by_ease(self):
        interval, ef = _sm2_update(6, 2.5, 3)
        # EF adjustment for rating 3: 2.5 + (0.1 - (5-3)*(0.08+(5-3)*0.02)) = 2.5 + (0.1 - 2*0.12) = 2.5 - 0.14 = 2.36
        self.assertEqual(interval, round(6 * ef))
        self.assertAlmostEqual(ef, 2.36)

    def test_rating_4_increases_ease(self):
        interval, ef = _sm2_update(6, 2.5, 4)
        # EF adjustment for rating 4: 2.5 + (0.1 - (5-4)*(0.08+(5-4)*0.02)) = 2.5 + (0.1 - 0.1) = 2.5
        self.assertAlmostEqual(ef, 2.5)
        self.assertEqual(interval, round(6 * 2.5))

    def test_rating_5_perfect_increases_ease(self):
        interval, ef = _sm2_update(6, 2.5, 5)
        # EF adjustment for rating 5: 2.5 + (0.1 - 0) = 2.6
        self.assertAlmostEqual(ef, 2.6)
        self.assertEqual(interval, round(6 * 2.6))

    def test_repeated_failures_keep_ease_at_minimum(self):
        ef = 2.5
        interval = 10
        for _ in range(20):
            interval, ef = _sm2_update(interval, ef, 1)
        self.assertEqual(ef, 1.3)
        self.assertEqual(interval, 1)

    def test_graduated_learning_sequence(self):
        """Simulate a realistic study sequence: fail → good → easy → perfect."""
        interval, ef = _sm2_update(0, 2.5, 1)   # Fail
        self.assertEqual(interval, 1)
        interval, ef = _sm2_update(interval, ef, 3)  # Good
        self.assertEqual(interval, 6)
        interval, ef = _sm2_update(interval, ef, 4)  # Easy
        self.assertGreater(interval, 6)
        interval, ef = _sm2_update(interval, ef, 5)  # Perfect
        self.assertGreater(ef, 2.0)


if __name__ == "__main__":
    unittest.main()
