import importlib
import os
import sys
import tempfile
import shutil
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from uuid import uuid4

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ["DEBUG"] = "true"

from test_ai_queue import _FakeRedis, _install_ai_queue_import_stubs, _restore_modules


class TeacherAIDraftContractTests(unittest.TestCase):
    def test_queue_teacher_ai_grade_job_preserves_review_context(self):
        from src.domains.academic.application.teacher_reporting import queue_teacher_ai_grade_job

        captured = {}

        def _fake_enqueue(job_type, payload, tenant_id, user_id, trace_id=None, source="api"):
            captured["job_type"] = job_type
            captured["payload"] = payload
            captured["tenant_id"] = tenant_id
            captured["user_id"] = user_id
            return {"job_id": "job-123"}

        current_user = SimpleNamespace(id=uuid4(), tenant_id=uuid4())

        temp_dir = BACKEND_DIR / "tmp_phase3_ai_grade_job"
        temp_dir.mkdir(exist_ok=True)
        try:
            result = queue_teacher_ai_grade_job(
                file_name="sheet.png",
                content=b"image-bytes",
                current_user=current_user,
                max_file_size=1024 * 1024,
                upload_dir=temp_dir,
                enqueue_job_fn=_fake_enqueue,
                exam_id="exam-1",
                exam_name="Unit Test 1",
                exam_max_marks=25,
                student_id="student-1",
                student_name="Asha",
                answer_key="Quadratic formula",
                rubric="Award partial marks for correct steps.",
            )
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

        self.assertTrue(result["success"])
        self.assertEqual(captured["job_type"], "ai_grade")
        self.assertEqual(captured["payload"]["exam_id"], "exam-1")
        self.assertEqual(captured["payload"]["exam_name"], "Unit Test 1")
        self.assertEqual(captured["payload"]["exam_max_marks"], 25)
        self.assertEqual(captured["payload"]["student_id"], "student-1")
        self.assertEqual(captured["payload"]["student_name"], "Asha")
        self.assertEqual(captured["payload"]["answer_key"], "Quadratic formula")
        self.assertEqual(captured["payload"]["rubric"], "Award partial marks for correct steps.")


class AIGradingDraftResultTests(unittest.IsolatedAsyncioTestCase):
    async def test_run_ai_grade_returns_draft_review_contract_and_not_final_marks(self):
        from src.domains.platform.services import ai_grading as ai_grading_mod

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp.write(b"fake image")
            temp_path = tmp.name

        llm_stub = SimpleNamespace(
            generate=AsyncMock(return_value={"response": '{"score": 18, "max_score": 20, "feedback": "Strong logic."}'})
        )

        try:
            with patch.object(
                ai_grading_mod,
                "extract_ocr_result_from_image_path",
                return_value=SimpleNamespace(
                    text="student answer",
                    used_ocr=True,
                    review_required=False,
                    warning=None,
                    languages=["en"],
                    preprocessing_applied=["grayscale"],
                    confidence=0.91,
                ),
            ), patch.object(ai_grading_mod, "record_trace_event"), patch(
                "src.infrastructure.llm.providers.get_llm_provider",
                return_value=llm_stub,
            ):
                payload = await ai_grading_mod.run_ai_grade(
                    {
                        "file_path": temp_path,
                        "file_name": "answer.png",
                        "exam_id": "exam-1",
                        "exam_name": "Unit Test 1",
                        "exam_max_marks": 25,
                        "student_id": "student-1",
                        "student_name": "Asha",
                        "answer_key": "Quadratic formula",
                        "rubric": "Award partial marks for steps.",
                    },
                    trace_id="trace-1",
                    tenant_id=str(uuid4()),
                )
        finally:
            Path(temp_path).unlink(missing_ok=True)

        self.assertEqual(payload["status"], "draft_ready")
        self.assertTrue(payload["review_required"])
        self.assertEqual(payload["proposed_mark"], 22)
        self.assertEqual(payload["teacher_review"]["status"], "draft_ready")
        self.assertFalse(payload["teacher_review"]["finalized"])
        self.assertEqual(payload["teacher_review"]["exam_id"], "exam-1")
        self.assertEqual(payload["teacher_review"]["student_id"], "student-1")
        self.assertIn("must be reviewed by a teacher", payload["teacher_review"]["notes"])


class AIQueueDraftNotificationTests(unittest.IsolatedAsyncioTestCase):
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

    async def test_process_job_notifies_teacher_when_ai_grading_draft_is_ready(self):
        self.queue.enqueue_job(
            self.queue.JOB_TYPE_AI_GRADE,
            {
                "tenant_id": "tenant-1",
                "file_path": "C:/tmp/answer.png",
                "file_name": "answer.png",
                "teacher_id": "11111111-1111-1111-1111-111111111111",
                "exam_id": "exam-1",
                "student_id": "student-1",
                "student_name": "Asha",
                "answer_key": "Quadratic formula",
            },
            tenant_id="tenant-1",
            user_id="11111111-1111-1111-1111-111111111111",
        )
        job_id = self.queue.claim_next_job(timeout_seconds=0)

        with patch.object(
            self.queue,
            "run_ai_grade",
            AsyncMock(return_value={
                "status": "draft_ready",
                "teacher_review": {
                    "required": True,
                    "finalized": False,
                    "status": "draft_ready",
                    "proposed_mark": 22,
                    "max_marks": 25,
                    "exam_id": "exam-1",
                    "student_id": "student-1",
                    "student_name": "Asha",
                },
            }),
        ), patch.object(
            self.queue,
            "add_notification",
        ) as add_notification_mock, patch.object(
            sys.modules["src.domains.platform.services.whatsapp_gateway"],
            "send_ai_job_status_notification",
            AsyncMock(return_value=True),
        ):
            updated = await self.queue.process_job(job_id, worker_id="worker-1")

        self.assertEqual(updated["status"], self.queue.STATUS_COMPLETED)
        add_notification_mock.assert_called_once()
        args, kwargs = add_notification_mock.call_args
        self.assertEqual(args[0], "11111111-1111-1111-1111-111111111111")
        self.assertEqual(kwargs["category"], "grading")
        self.assertEqual(kwargs["data"]["review_required"], True)
        self.assertEqual(kwargs["data"]["review_status"], "draft_ready")


if __name__ == "__main__":
    unittest.main()
