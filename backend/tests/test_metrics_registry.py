import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ["DEBUG"] = "true"


class MetricsRegistryTests(unittest.TestCase):
    def setUp(self):
        from src.domains.platform.services.metrics_registry import reset_metrics_registry

        reset_metrics_registry()

    def tearDown(self):
        from src.domains.platform.services.metrics_registry import reset_metrics_registry

        reset_metrics_registry()

    def test_stage_latency_metrics_are_snapshotted_and_exported(self):
        from src.domains.platform.services.metrics_registry import (
            export_prometheus_text,
            observe_stage_latency,
            snapshot_stage_latency_metrics,
        )

        observe_stage_latency("ai_query", "retrieval", 120.0, "success")
        observe_stage_latency("ai_query", "retrieval", 80.0, "success")
        rows = snapshot_stage_latency_metrics()

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["stage"], "ai_query")
        self.assertEqual(rows[0]["operation"], "retrieval")
        self.assertEqual(rows[0]["count"], 2.0)
        self.assertEqual(rows[0]["duration_ms_sum"], 200.0)
        self.assertEqual(rows[0]["duration_ms_max"], 120.0)

        with patch("src.domains.platform.services.metrics_registry._get_global_queue_metrics", return_value={
            "pending_depth": 0,
            "processing_depth": 0,
            "tracked_jobs_total": 0,
            "retry_total": 0,
            "dead_letter_total": 0,
            "ready_tenants": 0,
        }):
            exported = export_prometheus_text()

        self.assertIn('vidyaos_stage_latency_total{stage="ai_query",operation="retrieval",outcome="success"} 2.0', exported)
        self.assertIn('vidyaos_stage_latency_duration_ms_sum{stage="ai_query",operation="retrieval",outcome="success"} 200.0', exported)
        self.assertIn('vidyaos_stage_latency_duration_ms_max{stage="ai_query",operation="retrieval",outcome="success"} 120.0', exported)

    def test_personalization_metrics_are_snapshotted_and_exported(self):
        from src.domains.platform.services.metrics_registry import (
            export_prometheus_text,
            observe_personalization_event,
            snapshot_personalization_metrics,
        )

        observe_personalization_event("recommendation_served", surface="overview", target="quiz")
        observe_personalization_event("recommendation_click", surface="overview", target="quiz")
        observe_personalization_event("study_path_view", surface="overview", target="study_guide")
        rows = snapshot_personalization_metrics()

        self.assertEqual(len(rows), 3)
        self.assertTrue(
            any(
                row["metric"] == "recommendation_click"
                and row["surface"] == "overview"
                and row["target"] == "quiz"
                and row["count"] == 1.0
                for row in rows
            )
        )

        with patch("src.domains.platform.services.metrics_registry._get_global_queue_metrics", return_value={
            "pending_depth": 0,
            "processing_depth": 0,
            "tracked_jobs_total": 0,
            "retry_total": 0,
            "dead_letter_total": 0,
            "ready_tenants": 0,
        }):
            exported = export_prometheus_text()

        self.assertIn(
            'vidyaos_personalization_events_total{metric="recommendation_served",surface="overview",target="quiz"} 1.0',
            exported,
        )
        self.assertIn(
            'vidyaos_personalization_events_total{metric="study_path_view",surface="overview",target="study_guide"} 1.0',
            exported,
        )


if __name__ == "__main__":
    unittest.main()
