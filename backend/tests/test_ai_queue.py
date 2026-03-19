import os
import sys
import importlib
import unittest
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import AsyncMock, patch

try:
    from fastapi import HTTPException
except ModuleNotFoundError:
    class HTTPException(Exception):
        def __init__(self, status_code: int, detail: str):
            super().__init__(detail)
            self.status_code = status_code
            self.detail = detail


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ["DEBUG"] = "true"


def _install_ai_queue_import_stubs():
    class _DummyRequest:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    async def _dummy_async(*args, **kwargs):
        return {"ok": True}

    stubbed = {}

    sqlalchemy_mod = ModuleType("sqlalchemy")
    sqlalchemy_mod.desc = lambda value: value
    stubbed["sqlalchemy"] = sqlalchemy_mod

    config_mod = ModuleType("config")
    config_mod.settings = SimpleNamespace(
        redis=SimpleNamespace(broker_url="redis://localhost:6379/0"),
        ai_queue=SimpleNamespace(
            enabled=True,
            max_retries=2,
            result_ttl_seconds=3600,
            metrics_window_seconds=3600,
            stuck_after_seconds=60,
            max_pending_jobs=100,
            max_pending_jobs_per_tenant=20,
            poll_timeout_seconds=1,
            processing_key="ai_jobs:processing",
        ),
    )
    stubbed["config"] = config_mod

    database_mod = ModuleType("database")
    database_mod.SessionLocal = lambda: None
    stubbed["database"] = database_mod

    ai_job_mod = ModuleType("src.domains.platform.models.ai_job")
    ai_job_mod.AIJob = type("AIJob", (), {"id": None, "created_at": None})
    ai_job_mod.AIJobEvent = type("AIJobEvent", (), {})
    stubbed["src.domains.platform.models.ai_job"] = ai_job_mod

    audit_mod = ModuleType("models.audit_log")
    audit_mod.AuditLog = type("AuditLog", (), {})
    stubbed["models.audit_log"] = audit_mod

    runtime_mod = ModuleType("src.domains.platform.schemas.ai_runtime")
    runtime_mod.InternalAIQueryRequest = _DummyRequest
    runtime_mod.InternalAudioOverviewRequest = _DummyRequest
    runtime_mod.InternalIngestURLRequest = _DummyRequest
    runtime_mod.InternalStudyToolGenerateRequest = _DummyRequest
    runtime_mod.InternalTeacherDocumentIngestRequest = _DummyRequest
    runtime_mod.InternalTeacherAssessmentRequest = _DummyRequest
    runtime_mod.InternalTeacherYoutubeIngestRequest = _DummyRequest
    runtime_mod.InternalVideoOverviewRequest = _DummyRequest
    stubbed["src.domains.platform.schemas.ai_runtime"] = runtime_mod

    ai_gateway_mod = ModuleType("src.domains.platform.services.ai_gateway")
    ai_gateway_mod.run_audio_overview = _dummy_async
    ai_gateway_mod.run_study_tool = _dummy_async
    ai_gateway_mod.run_teacher_assessment = _dummy_async
    ai_gateway_mod.run_teacher_document_ingestion = _dummy_async
    ai_gateway_mod.run_teacher_youtube_ingestion = _dummy_async
    ai_gateway_mod.run_text_query = _dummy_async
    ai_gateway_mod.run_url_ingestion = _dummy_async
    ai_gateway_mod.run_video_overview = _dummy_async
    stubbed["src.domains.platform.services.ai_gateway"] = ai_gateway_mod

    ai_grading_mod = ModuleType("src.domains.platform.services.ai_grading")
    ai_grading_mod.run_ai_grade = _dummy_async
    stubbed["src.domains.platform.services.ai_grading"] = ai_grading_mod

    telemetry_mod = ModuleType("src.domains.platform.services.telemetry")
    telemetry_mod.extract_context_from_traceparent = lambda traceparent: None
    telemetry_mod.get_current_traceparent = lambda: None
    telemetry_mod.get_tracer = lambda name: None
    stubbed["src.domains.platform.services.telemetry"] = telemetry_mod

    whatsapp_mod = ModuleType("src.domains.platform.services.whatsapp_gateway")
    whatsapp_mod.send_ai_job_status_notification = _dummy_async
    stubbed["src.domains.platform.services.whatsapp_gateway"] = whatsapp_mod

    previous = {name: sys.modules.get(name) for name in stubbed}
    parent_services = sys.modules.get("src.domains.platform.services")
    previous["src.domains.platform.services.__whatsapp_gateway_attr__"] = getattr(parent_services, "whatsapp_gateway", None) if parent_services else None
    sys.modules.update(stubbed)
    if parent_services is not None:
        parent_services.whatsapp_gateway = whatsapp_mod
    return previous


def _restore_modules(previous):
    parent_services = sys.modules.get("src.domains.platform.services")
    prior_attr = previous.pop("src.domains.platform.services.__whatsapp_gateway_attr__", None)
    for name, module in previous.items():
        if module is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = module
    if parent_services is not None:
        if prior_attr is None:
            try:
                delattr(parent_services, "whatsapp_gateway")
            except AttributeError:
                pass
        else:
            parent_services.whatsapp_gateway = prior_attr



class _FakePipeline:
    def __init__(self, client):
        self.client = client
        self.operations = []

    def __getattr__(self, name):
        def wrapper(*args, **kwargs):
            self.operations.append((name, args, kwargs))
            return self
        return wrapper

    def execute(self):
        for name, args, kwargs in self.operations:
            getattr(self.client, name)(*args, **kwargs)
        self.operations.clear()
        return []


class _FakeRedis:
    def __init__(self):
        self.values = {}
        self.lists = {}
        self.sorted_sets = {}
        self.expiries = {}
        self.sets = {}
        self.hashes = {}

    def ping(self):
        return True

    def pipeline(self):
        return _FakePipeline(self)

    def get(self, key):
        return self.values.get(key)

    def setex(self, key, ttl, value):
        self.values[key] = value
        self.expiries[key] = ttl

    def expire(self, key, ttl):
        self.expiries[key] = ttl

    def zadd(self, key, mapping):
        bucket = self.sorted_sets.setdefault(key, {})
        bucket.update(mapping)

    def zrevrange(self, key, start, end):
        items = sorted(self.sorted_sets.get(key, {}).items(), key=lambda item: (item[1], item[0]), reverse=True)
        if end == -1:
            selected = items[start:]
        else:
            selected = items[start:end + 1]
        return [member for member, _score in selected]

    def zpopmin(self, key, count=1):
        items = sorted(self.sorted_sets.get(key, {}).items(), key=lambda item: (item[1], item[0]))
        selected = items[:count]
        for member, _score in selected:
            self.sorted_sets.get(key, {}).pop(member, None)
        return selected

    def zrem(self, key, *members):
        bucket = self.sorted_sets.get(key, {})
        removed = 0
        for member in members:
            if member in bucket:
                removed += 1
                bucket.pop(member, None)
        return removed

    def zcard(self, key):
        return len(self.sorted_sets.get(key, {}))

    def zremrangebyscore(self, key, minimum, maximum):
        bucket = self.sorted_sets.get(key, {})
        to_remove = [member for member, score in bucket.items() if minimum <= score <= maximum]
        for member in to_remove:
            bucket.pop(member, None)
        return len(to_remove)

    def lpush(self, key, value):
        self.lists.setdefault(key, []).insert(0, value)

    def rpush(self, key, value):
        self.lists.setdefault(key, []).append(value)

    def lpop(self, key):
        values = self.lists.get(key, [])
        if not values:
            return None
        return values.pop(0)

    def rpop(self, key):
        values = self.lists.get(key, [])
        if not values:
            return None
        return values.pop()

    def lrem(self, key, count, value):
        values = self.lists.get(key, [])
        removed = 0
        kept = []
        for item in values:
            if item == value and (count == 0 or removed < count):
                removed += 1
                continue
            kept.append(item)
        self.lists[key] = kept
        return removed

    def sadd(self, key, value):
        self.sets.setdefault(key, set()).add(value)

    def srem(self, key, value):
        existed = value in self.sets.get(key, set())
        self.sets.setdefault(key, set()).discard(value)
        return 1 if existed else 0

    def sismember(self, key, value):
        return value in self.sets.get(key, set())

    def hincrby(self, key, field, delta):
        self.hashes.setdefault(key, {})
        self.hashes[key][field] = int(self.hashes[key].get(field, 0)) + delta
        return self.hashes[key][field]

    def hget(self, key, field):
        return self.hashes.get(key, {}).get(field)

    def eval(self, script, numkeys, *keys_and_args):
        # We only use eval for _CLAIM_JOB_LUA in our application logic
        queue_key = keys_and_args[0]
        processing_key = keys_and_args[1]
        
        # zpopmin pops from queue
        job = self.zpopmin(queue_key, 1)
        if job and len(job) > 0:
            job_id = job[0][0]  # (member, score)
            self.lpush(processing_key, job_id)
            return job_id
        return None


class AIQueueTests(unittest.IsolatedAsyncioTestCase):
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

    async def test_enqueue_job_tracks_priority_and_queue_metrics(self):
        job = self.queue.enqueue_job(
            self.queue.JOB_TYPE_AUDIO,
            {"tenant_id": "tenant-1", "topic": "Atoms", "format": "brief", "language": "english"},
            tenant_id="tenant-1",
            user_id="11111111-1111-1111-1111-111111111111",
        )

        self.assertEqual(job["status"], self.queue.STATUS_QUEUED)
        self.assertTrue(job["trace_id"])
        self.assertEqual(job["priority"], self.queue.JOB_PRIORITIES[self.queue.JOB_TYPE_AUDIO])
        self.assertEqual(self.fake_redis.lists[self.queue.READY_TENANTS_KEY], ["tenant-1"])
        self.assertEqual(
            self.fake_redis.hashes[self.queue._tenant_metrics_key("tenant-1")]["pending_depth"],
            1,
        )

    async def test_claim_next_job_rotates_between_tenants_fairly(self):
        self.queue.enqueue_job(
            self.queue.JOB_TYPE_QUERY,
            {"tenant_id": "tenant-a", "query": "One", "mode": "qa", "language": "english", "tenant_id": "tenant-a"},
            tenant_id="tenant-a",
            user_id="11111111-1111-1111-1111-111111111111",
        )
        self.queue.enqueue_job(
            self.queue.JOB_TYPE_QUERY,
            {"tenant_id": "tenant-a", "query": "Two", "mode": "qa", "language": "english", "tenant_id": "tenant-a"},
            tenant_id="tenant-a",
            user_id="11111111-1111-1111-1111-111111111111",
        )
        self.queue.enqueue_job(
            self.queue.JOB_TYPE_QUERY,
            {"tenant_id": "tenant-b", "query": "Three", "mode": "qa", "language": "english", "tenant_id": "tenant-b"},
            tenant_id="tenant-b",
            user_id="22222222-2222-2222-2222-222222222222",
        )

        first = self.queue.get_job(self.queue.claim_next_job(timeout_seconds=0))
        second = self.queue.get_job(self.queue.claim_next_job(timeout_seconds=0))
        third = self.queue.get_job(self.queue.claim_next_job(timeout_seconds=0))

        self.assertEqual(first["tenant_id"], "tenant-a")
        self.assertEqual(second["tenant_id"], "tenant-b")
        self.assertEqual(third["tenant_id"], "tenant-a")

    async def test_process_job_uses_ai_service_path_for_generation_jobs(self):
        job = self.queue.enqueue_job(
            self.queue.JOB_TYPE_AUDIO,
            {"tenant_id": "tenant-1", "topic": "Atoms", "format": "brief", "language": "english"},
            tenant_id="tenant-1",
            user_id="11111111-1111-1111-1111-111111111111",
        )
        job_id = self.queue.claim_next_job(timeout_seconds=0)

        with patch.object(
            self.queue,
            "run_audio_overview",
            AsyncMock(return_value={"title": "Atoms", "dialogue": [], "duration_estimate": "3 minutes"}),
        ), patch.object(
            sys.modules["src.domains.platform.services.whatsapp_gateway"],
            "send_ai_job_status_notification",
            AsyncMock(return_value=True),
        ) as notify_mock:
            updated = await self.queue.process_job(job_id, worker_id="worker-1")

        notify_mock.assert_awaited_once()

        self.assertEqual(updated["status"], self.queue.STATUS_COMPLETED)
        self.assertEqual(updated["result"]["title"], "Atoms")
        self.assertTrue(any(event["stage"] == "ai_service.completed" for event in updated["events"]))

    async def test_process_job_uses_ai_service_path_for_teacher_assessment_jobs(self):
        job = self.queue.enqueue_job(
            self.queue.JOB_TYPE_TEACHER_ASSESSMENT,
            {
                "tenant_id": "tenant-1",
                "subject_id": "subject-1",
                "subject_name": "Science",
                "topic": "Atoms",
                "num_questions": 5,
            },
            tenant_id="tenant-1",
            user_id="11111111-1111-1111-1111-111111111111",
        )
        job_id = self.queue.claim_next_job(timeout_seconds=0)

        with patch.object(
            self.queue,
            "run_teacher_assessment",
            AsyncMock(return_value={"success": True, "assessment": "[]"}),
        ) as assessment_mock:
            updated = await self.queue.process_job(job_id, worker_id="worker-1")

        self.assertEqual(updated["status"], self.queue.STATUS_COMPLETED)
        self.assertEqual(updated["result"]["assessment"], "[]")
        self.assertTrue(any(event["stage"] == "ai_service.completed" for event in updated["events"]))
        assessment_mock.assert_awaited_once()

    async def test_cancel_retry_and_dead_letter_controls(self):
        queued = self.queue.enqueue_job(
            self.queue.JOB_TYPE_QUERY,
            {"tenant_id": "tenant-1", "query": "Cancel me", "mode": "qa", "language": "english"},
            tenant_id="tenant-1",
            user_id="11111111-1111-1111-1111-111111111111",
        )
        cancelled = self.queue.cancel_job(queued["job_id"], "tenant-1", actor_user_id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
        self.assertEqual(cancelled["status"], self.queue.STATUS_CANCELLED)

        failed = self.queue.enqueue_job(
            self.queue.JOB_TYPE_AUDIO,
            {"tenant_id": "tenant-1", "topic": "Fail me", "format": "brief", "language": "english"},
            tenant_id="tenant-1",
            user_id="11111111-1111-1111-1111-111111111111",
        )
        failed_job = self.queue.get_job(failed["job_id"])
        failed_job["max_retries"] = 0
        self.queue.save_job(failed_job)
        claimed_failed_job_id = self.queue.claim_next_job(timeout_seconds=0)
        with patch.object(self.queue, "run_audio_overview", AsyncMock(side_effect=HTTPException(status_code=500, detail="boom"))), patch.object(
            sys.modules["src.domains.platform.services.whatsapp_gateway"],
            "send_ai_job_status_notification",
            AsyncMock(return_value=True),
        ) as notify_mock:
            failed_result = await self.queue.process_job(claimed_failed_job_id, worker_id="worker-1")
        notify_mock.assert_awaited_once()
        self.assertEqual(failed_result["status"], self.queue.STATUS_FAILED)

        dead_lettered = self.queue.move_to_dead_letter(failed_result["job_id"], "tenant-1", actor_user_id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
        self.assertEqual(dead_lettered["status"], self.queue.STATUS_DEAD_LETTER)

        retried = self.queue.retry_job(failed_result["job_id"], "tenant-1", actor_user_id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
        self.assertEqual(retried["status"], self.queue.STATUS_QUEUED)

    async def test_queue_metrics_include_dead_letter_and_retry_counts(self):
        job = self.queue.enqueue_job(
            self.queue.JOB_TYPE_AUDIO,
            {"tenant_id": "tenant-1", "topic": "Metrics", "format": "brief", "language": "english"},
            tenant_id="tenant-1",
            user_id="11111111-1111-1111-1111-111111111111",
        )
        job_data = self.queue.get_job(job["job_id"])
        job_data.update({
            "status": self.queue.STATUS_RUNNING,
            "started_at": "2020-03-06T00:00:00+00:00",
        })
        self.queue.save_job(job_data)
        self.fake_redis.hashes[self.queue._tenant_metrics_key("tenant-1")]["retry_total"] = 2
        self.fake_redis.sorted_sets[self.queue._tenant_dead_letter_key("tenant-1")] = {"job-x": 1.0}

        metrics = self.queue.get_queue_metrics("tenant-1")

        self.assertEqual(metrics["pending_depth"], 1)
        self.assertEqual(metrics["retry_count"], 2)
        self.assertEqual(metrics["dead_letter_count"], 1)
        self.assertGreaterEqual(metrics["stuck_jobs"], 1)


if __name__ == "__main__":
    unittest.main()
