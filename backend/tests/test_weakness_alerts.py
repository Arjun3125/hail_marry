"""Tests for services/weakness_alerts.py — threshold-based alert generation."""
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock
from uuid import uuid4

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ["DEBUG"] = "true"


class FakePerformance:
    def __init__(self, subject_id, average_score):
        self.subject_id = subject_id
        self.average_score = average_score


class FakeSubject:
    def __init__(self, name):
        self.name = name


class WeaknessAlertTests(unittest.TestCase):
    def _run(self, performances, subject_map=None):
        """Run generate_weakness_alerts with properly mocked db.
        subject_map: dict mapping subject_id -> name
        """
        from src.domains.academic.services.weakness_alerts import generate_weakness_alerts

        if subject_map is None:
            subject_map = {}

        db = MagicMock()

        # Mock db.query(SubjectPerformance).filter(...).all()
        perf_query = MagicMock()
        perf_query.filter.return_value.all.return_value = performances

        # Mock db.query(Subject).filter(Subject.id == ...).first()
        def query_dispatch(model):
            from src.domains.academic.models.performance import SubjectPerformance
            from src.domains.academic.models.core import Subject
            if model is SubjectPerformance:
                return perf_query
            if model is Subject:
                subj_mock = MagicMock()
                def subj_filter(*args, **kwargs):
                    result = MagicMock()
                    # Try to find the subject_id from the filter args
                    for perf in performances:
                        if perf.subject_id in subject_map:
                            result.first.return_value = FakeSubject(subject_map[perf.subject_id])
                            return result
                    result.first.return_value = FakeSubject("Unknown")
                    return result
                subj_mock.filter = subj_filter
                return subj_mock
            return MagicMock()

        db.query = query_dispatch

        return generate_weakness_alerts(db, user_id=uuid4(), tenant_id=uuid4())

    def test_no_performances_returns_empty(self):
        alerts = self._run([])
        self.assertEqual(alerts, [])

    def test_strong_subject_no_alert(self):
        sid = uuid4()
        perf = FakePerformance(sid, 85.0)
        alerts = self._run([perf], {sid: "Math"})
        self.assertEqual(alerts, [])

    def test_weak_subject_generates_alert(self):
        sid = uuid4()
        perf = FakePerformance(sid, 45.0)
        alerts = self._run([perf], {sid: "Physics"})
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["severity"], "warning")

    def test_critical_severity_below_40(self):
        sid = uuid4()
        perf = FakePerformance(sid, 30.0)
        alerts = self._run([perf], {sid: "Math"})
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["severity"], "critical")

    def test_exactly_60_no_alert(self):
        sid = uuid4()
        perf = FakePerformance(sid, 60.0)
        alerts = self._run([perf], {sid: "English"})
        self.assertEqual(alerts, [])

    def test_none_average_skipped(self):
        sid = uuid4()
        perf = FakePerformance(sid, None)
        alerts = self._run([perf], {sid: "Science"})
        self.assertEqual(alerts, [])

    def test_alert_has_action(self):
        sid = uuid4()
        perf = FakePerformance(sid, 50.0)
        alerts = self._run([perf], {sid: "Chemistry"})
        self.assertEqual(len(alerts), 1)
        self.assertIn("action", alerts[0])
        self.assertEqual(alerts[0]["action"]["type"], "create_review")

    def test_alert_has_recommendation(self):
        sid = uuid4()
        perf = FakePerformance(sid, 40.0)
        alerts = self._run([perf], {sid: "Biology"})
        self.assertIn("recommendation", alerts[0])


if __name__ == "__main__":
    unittest.main()
