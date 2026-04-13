import importlib
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException


BACKEND_DIR = Path(__file__).resolve().parents[1]
TESTS_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

os.environ["DEBUG"] = "true"

from test_ai_queue import _FakeRedis, _install_ai_queue_import_stubs, _restore_modules


class WhatsAppMediaQueueFailureTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self._previous_modules = _install_ai_queue_import_stubs()
        sys.modules.pop("src.domains.platform.services.ai_queue", None)
        self.queue = importlib.import_module("src.domains.platform.services.ai_queue")
        self.queue = importlib.reload(self.queue)
        self.fake_redis = _FakeRedis()
        self.redis_patch = patch.object(self.queue, "_get_redis_client", return_value=self.fake_redis)
        self.audit_patch = patch.object(self.queue, "_record_audit_event", return_value=None)
        self.persist_patch = patch.object(self.queue, "_persist_job_state", return_value=None)
        self.redis_patch.start()
        self.audit_patch.start()
        self.persist_patch.start()

    def tearDown(self):
        self.persist_patch.stop()
        self.audit_patch.stop()
        self.redis_patch.stop()
        sys.modules.pop("src.domains.platform.services.ai_queue", None)
        _restore_modules(self._previous_modules)

    async def test_whatsapp_media_ingest_failure_is_requeued_when_retryable(self):
        self.queue.enqueue_job(
            self.queue.JOB_TYPE_WHATSAPP_MEDIA_INGEST,
            {
                "tenant_id": "tenant-1",
                "document_id": "doc-1",
                "file_path": "C:/tmp/lesson.mp4",
                "display_name": "lesson.mp4",
                "media_kind": "video",
            },
            tenant_id="tenant-1",
            user_id="11111111-1111-1111-1111-111111111111",
        )
        job_id = self.queue.claim_next_job(timeout_seconds=0)

        with patch.object(
            self.queue,
            "run_whatsapp_media_ingestion",
            AsyncMock(side_effect=RuntimeError("transcriber temporarily unavailable")),
        ) as media_mock, patch.object(
            sys.modules["src.domains.platform.services.whatsapp_gateway"],
            "send_ai_job_status_notification",
            AsyncMock(return_value=True),
        ) as notify_mock:
            updated = await self.queue.process_job(job_id, worker_id="worker-1")

        media_mock.assert_awaited_once()
        notify_mock.assert_not_awaited()
        self.assertEqual(updated["status"], self.queue.STATUS_QUEUED)
        self.assertEqual(updated["attempts"], 1)
        self.assertEqual(updated["error"], "transcriber temporarily unavailable")
        self.assertTrue(any(event["stage"] == "worker.retry_scheduled" for event in updated["events"]))
        self.assertEqual(
            self.fake_redis.hashes[self.queue._tenant_metrics_key("tenant-1")]["retry_total"],
            1,
        )

    async def test_whatsapp_media_ingest_failure_notifies_when_retries_exhausted(self):
        public_job = self.queue.enqueue_job(
            self.queue.JOB_TYPE_WHATSAPP_MEDIA_INGEST,
            {
                "tenant_id": "tenant-1",
                "document_id": "doc-2",
                "file_path": "C:/tmp/lesson.mp4",
                "display_name": "lesson.mp4",
                "media_kind": "video",
            },
            tenant_id="tenant-1",
            user_id="11111111-1111-1111-1111-111111111111",
        )
        job = self.queue.get_job(public_job["job_id"])
        job["max_retries"] = 0
        self.queue.save_job(job)
        job_id = self.queue.claim_next_job(timeout_seconds=0)

        with patch.object(
            self.queue,
            "run_whatsapp_media_ingestion",
            AsyncMock(side_effect=HTTPException(status_code=500, detail="transcriber timeout")),
        ) as media_mock, patch.object(
            sys.modules["src.domains.platform.services.whatsapp_gateway"],
            "send_ai_job_status_notification",
            AsyncMock(return_value=True),
        ) as notify_mock:
            updated = await self.queue.process_job(job_id, worker_id="worker-1")

        media_mock.assert_awaited_once()
        notify_mock.assert_awaited_once()
        self.assertEqual(updated["status"], self.queue.STATUS_FAILED)
        self.assertEqual(updated["error"], "transcriber timeout")
        self.assertTrue(any(event["stage"] == "worker.failed" for event in updated["events"]))
