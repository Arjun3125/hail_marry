"""Tests for services/alerting.py — alert evaluation rules."""
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ["DEBUG"] = "true"


def _make_metrics(**overrides):
    """Return a healthy-looking queue metrics dict with optional overrides."""
    base = {
        "pending_depth": 0,
        "processing_depth": 1,
        "failed_last_window": 0,
        "failure_rate_pct": 0,
        "stuck_jobs": 0,
        "dead_letter_count": 0,
        "max_pending_jobs_per_tenant": 200,
        "retry_count": 0,
    }
    base.update(overrides)
    return base


class AlertingTests(unittest.TestCase):
    """Verify each alert condition in get_active_alerts."""

    def _get(self, tenant_id, metrics):
        from src.domains.platform.services import alerting
        with patch.object(alerting, "get_queue_metrics", return_value=metrics):
            return alerting.get_active_alerts(tenant_id)

    def test_no_alerts_for_healthy_queue(self):
        alerts = self._get("t1", _make_metrics())
        self.assertEqual(alerts, [])

    def test_alerting_disabled_returns_empty(self):
        from src.domains.platform.services import alerting
        original = alerting.settings.observability.alerting_enabled
        alerting.settings.observability.alerting_enabled = False
        try:
            alerts = alerting.get_active_alerts("t1")
            self.assertEqual(alerts, [])
        finally:
            alerting.settings.observability.alerting_enabled = original

    def test_queue_depth_high(self):
        alerts = self._get("t1", _make_metrics(pending_depth=180, max_pending_jobs_per_tenant=200))
        codes = [a["code"] for a in alerts]
        self.assertIn("queue_depth_high", codes)

    def test_queue_failure_rate_high(self):
        alerts = self._get("t1", _make_metrics(failure_rate_pct=25, failed_last_window=5))
        codes = [a["code"] for a in alerts]
        self.assertIn("queue_failure_rate_high", codes)

    def test_queue_jobs_stuck(self):
        alerts = self._get("t1", _make_metrics(stuck_jobs=3))
        codes = [a["code"] for a in alerts]
        self.assertIn("queue_jobs_stuck", codes)

    def test_queue_worker_idle(self):
        alerts = self._get("t1", _make_metrics(pending_depth=5, processing_depth=0))
        codes = [a["code"] for a in alerts]
        self.assertIn("queue_worker_idle", codes)

    def test_queue_dead_letter_present(self):
        alerts = self._get("t1", _make_metrics(dead_letter_count=2))
        codes = [a["code"] for a in alerts]
        self.assertIn("queue_dead_letter_present", codes)

    def test_multiple_alerts_simultaneously(self):
        alerts = self._get("t1", _make_metrics(
            pending_depth=190,
            max_pending_jobs_per_tenant=200,
            stuck_jobs=2,
            dead_letter_count=1,
            processing_depth=0,
        ))
        codes = [a["code"] for a in alerts]
        self.assertIn("queue_depth_high", codes)
        self.assertIn("queue_jobs_stuck", codes)
        self.assertIn("queue_dead_letter_present", codes)
        self.assertIn("queue_worker_idle", codes)
        self.assertTrue(len(alerts) >= 4)


if __name__ == "__main__":
    unittest.main()
