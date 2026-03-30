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
        with patch.object(alerting, "get_queue_metrics", return_value=metrics), \
             patch.object(alerting, "snapshot_stage_latency_metrics", return_value=[]):
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

    def test_stage_latency_alert_when_average_exceeds_budget(self):
        from src.domains.platform.services import alerting

        stage_rows = [{
            "stage": "ai_query",
            "operation": "generation",
            "outcome": "success",
            "count": 4.0,
            "duration_ms_sum": 52000.0,
            "duration_ms_max": 15000.0,
        }]
        with patch.object(alerting, "get_queue_metrics", return_value=_make_metrics()), \
             patch.object(alerting, "snapshot_stage_latency_metrics", return_value=stage_rows):
            alerts = alerting.get_active_alerts("t1")

        latency_alert = next((alert for alert in alerts if alert["code"] == "stage_latency_high"), None)
        self.assertIsNotNone(latency_alert)
        self.assertEqual(latency_alert["stage"], "ai_query")
        self.assertEqual(latency_alert["operation"], "generation")
        self.assertGreater(latency_alert["avg_latency_ms"], latency_alert["budget_ms"])

    def test_stage_latency_ignores_low_sample_counts(self):
        from src.domains.platform.services import alerting

        stage_rows = [{
            "stage": "whatsapp_media_ingest",
            "operation": "transcription",
            "outcome": "success",
            "count": 1.0,
            "duration_ms_sum": 90000.0,
            "duration_ms_max": 90000.0,
        }]
        with patch.object(alerting, "get_queue_metrics", return_value=_make_metrics()), \
             patch.object(alerting, "snapshot_stage_latency_metrics", return_value=stage_rows):
            alerts = alerting.get_active_alerts("t1")

        codes = [a["code"] for a in alerts]
        self.assertNotIn("stage_latency_high", codes)

    def test_mascot_failure_alert_when_error_rate_is_high(self):
        from src.domains.platform.services import alerting

        stage_rows = [
            {"stage": "mascot", "operation": "execution", "outcome": "success", "count": 8.0, "duration_ms_sum": 3200.0, "duration_ms_max": 700.0},
            {"stage": "mascot", "operation": "execution", "outcome": "error", "count": 3.0, "duration_ms_sum": 900.0, "duration_ms_max": 400.0},
        ]
        with patch.object(alerting, "get_queue_metrics", return_value=_make_metrics()), \
             patch.object(alerting, "snapshot_stage_latency_metrics", return_value=stage_rows):
            alerts = alerting.get_active_alerts("t1")

        mascot_alert = next((alert for alert in alerts if alert["code"] == "mascot_failure_rate_high"), None)
        self.assertIsNotNone(mascot_alert)
        self.assertEqual(mascot_alert["stage"], "mascot")
        self.assertEqual(mascot_alert["operation"], "execution")
        self.assertGreaterEqual(mascot_alert["failure_rate_pct"], 15.0)

    def test_mascot_failure_alert_ignores_low_sample_counts(self):
        from src.domains.platform.services import alerting

        stage_rows = [
            {"stage": "mascot", "operation": "upload", "outcome": "success", "count": 3.0, "duration_ms_sum": 900.0, "duration_ms_max": 400.0},
            {"stage": "mascot", "operation": "upload", "outcome": "error", "count": 1.0, "duration_ms_sum": 300.0, "duration_ms_max": 300.0},
        ]
        with patch.object(alerting, "get_queue_metrics", return_value=_make_metrics()), \
             patch.object(alerting, "snapshot_stage_latency_metrics", return_value=stage_rows):
            alerts = alerting.get_active_alerts("t1")

        codes = [a["code"] for a in alerts]
        self.assertNotIn("mascot_failure_rate_high", codes)


if __name__ == "__main__":
    unittest.main()
