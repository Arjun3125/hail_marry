import os
import sys
import importlib
import unittest
import io
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, mock_open, patch

from fastapi import HTTPException, Response, UploadFile
from starlette.requests import Request
from starlette.responses import JSONResponse


# Ensure backend modules can be imported when tests are run from repo root.
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Avoid env parsing failures from non-boolean DEBUG values.
os.environ["DEBUG"] = "true"


class _QueryStub:
    def __init__(self, result):
        self._result = result

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return self._result


class _DBStub:
    def __init__(self, results_by_model_name):
        self.results_by_model_name = results_by_model_name
        self.queried_models = []

    def query(self, model):
        name = getattr(model, "__name__", str(model))
        self.queried_models.append(name)
        return _QueryStub(self.results_by_model_name.get(name))

    def add(self, _obj):
        return None

    def commit(self):
        return None

    def refresh(self, _obj):
        return None


class _ScenarioQueryStub:
    def __init__(self, db, key):
        self.db = db
        self.key = key

    def join(self, *args, **kwargs):
        return self

    def filter(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def limit(self, *args, **kwargs):
        return self

    def distinct(self, *args, **kwargs):
        return self

    def all(self):
        if self.key == "Mark+Exam":
            return self.db.mark_exam_rows
        if self.key == "Subject":
            if self.db.subjects is not None:
                return self.db.subjects
            return [self.db.subject] if self.db.subject is not None else []
        return []

    def first(self):
        if self.key == "Enrollment":
            return self.db.enrollment
        if self.key == "Assignment":
            return self.db.assignment
        if self.key == "Subject":
            return self.db.subject
        if self.key == "AssignmentSubmission":
            return self.db.submission
        return None


class _ScenarioDBStub:
    def __init__(
        self,
        *,
        mark_exam_rows=None,
        subjects=None,
        enrollment=None,
        assignment=None,
        subject=None,
        submission=None,
    ):
        self.mark_exam_rows = mark_exam_rows or []
        self.subjects = subjects
        self.enrollment = enrollment
        self.assignment = assignment
        self.subject = subject
        self.submission = submission

    def query(self, *models):
        names = [getattr(model, "__name__", str(model)) for model in models]
        key = "+".join(names)
        return _ScenarioQueryStub(self, key)

    def add(self, obj):
        if obj.__class__.__name__ == "AssignmentSubmission":
            if getattr(obj, "id", None) is None:
                obj.id = uuid4()
            self.submission = obj

    def commit(self):
        return None

    def refresh(self, obj):
        if obj.__class__.__name__ == "AssignmentSubmission" and getattr(obj, "id", None) is None:
            obj.id = uuid4()
        return None


class MiddlewareOrderingTests(unittest.TestCase):
    def test_tenant_middleware_precedes_rate_limit_middleware(self):
        main = importlib.import_module("main")
        main = importlib.reload(main)
        middleware_names = [mw.cls.__name__ for mw in main.app.user_middleware]
        self.assertIn("TenantMiddleware", middleware_names)
        self.assertIn("RateLimitMiddleware", middleware_names)
        self.assertLess(
            middleware_names.index("TenantMiddleware"),
            middleware_names.index("RateLimitMiddleware"),
            msg=f"Unexpected middleware order: {middleware_names}",
        )


class AuthRouteRegressionTests(unittest.IsolatedAsyncioTestCase):
    async def test_google_login_rejects_unmapped_email_domain(self):
        auth_routes = importlib.import_module("routes.auth")

        fake_google_user = {
            "email": "student@unknown-school.example",
            "google_id": "gid-123",
            "full_name": "Student User",
            "avatar_url": "https://example.com/avatar.png",
        }
        db = _DBStub({"Tenant": None})

        with patch.object(
            auth_routes,
            "verify_google_token",
            AsyncMock(return_value=fake_google_user),
        ):
            with self.assertRaises(HTTPException) as ctx:
                await auth_routes.google_login(
                    auth_routes.GoogleLoginRequest(token="test-token"),
                    Response(),
                    db,
                )

        self.assertEqual(ctx.exception.status_code, 403)
        self.assertEqual(db.queried_models, ["Tenant"])

    async def test_refresh_tokens_accepts_refresh_cookie_when_body_missing(self):
        auth_routes = importlib.import_module("routes.auth")

        fake_user = SimpleNamespace(
            id=uuid4(),
            tenant_id=uuid4(),
            email="student@school.example",
            role="student",
            is_active=True,
        )
        db = _DBStub({"User": fake_user})
        request = SimpleNamespace(cookies={"refresh_token": "cookie-refresh-token"})
        response = Response()

        with (
            patch.object(
                auth_routes,
                "decode_refresh_token",
                return_value={"user_id": str(fake_user.id)},
            ) as decode_mock,
            patch.object(auth_routes, "create_access_token", return_value="access-token"),
            patch.object(auth_routes, "create_refresh_token", return_value="refresh-token"),
        ):
            payload = await auth_routes.refresh_tokens(
                auth_routes.RefreshRequest(refresh_token=None),
                request,
                response,
                db,
            )

        self.assertEqual(payload["access_token"], "access-token")
        self.assertEqual(payload["token_type"], "bearer")
        decode_mock.assert_called_once_with("cookie-refresh-token")

    async def test_demo_login_blocked_when_debug_disabled(self):
        demo_routes = importlib.import_module("routes.demo")
        db = _DBStub({})

        original_debug = demo_routes.settings.app.debug
        demo_routes.settings.app.debug = False
        try:
            with self.assertRaises(HTTPException) as ctx:
                await demo_routes.demo_login({"role": "student"}, Response(), db)
        finally:
            demo_routes.settings.app.debug = original_debug

        self.assertEqual(ctx.exception.status_code, 404)
        self.assertEqual(db.queried_models, [])


class TeacherScopingRegressionTests(unittest.TestCase):
    def test_teacher_with_no_timetable_assignments_gets_no_class_access(self):
        scoping = importlib.import_module("auth.scoping")

        teacher_user = SimpleNamespace(
            role="teacher",
            tenant_id=uuid4(),
            id=uuid4(),
        )
        db = MagicMock()
        db.query.return_value.filter.return_value.distinct.return_value.all.return_value = []

        class_ids = scoping.get_teacher_class_ids(current_user=teacher_user, db=db)

        self.assertEqual(class_ids, [])

    def test_admin_gets_all_tenant_classes_for_teacher_routes(self):
        scoping = importlib.import_module("auth.scoping")

        class_id_1 = uuid4()
        class_id_2 = uuid4()
        admin_user = SimpleNamespace(
            role="admin",
            tenant_id=uuid4(),
            id=uuid4(),
        )
        db = MagicMock()
        db.query.return_value.filter.return_value.all.return_value = [
            (class_id_1,),
            (class_id_2,),
        ]

        class_ids = scoping.get_teacher_class_ids(current_user=admin_user, db=db)

        self.assertEqual(class_ids, [class_id_1, class_id_2])

    def test_teacher_route_scope_guard_blocks_unassigned_class(self):
        teacher_routes = importlib.import_module("routes.teacher")
        teacher_user = SimpleNamespace(role="teacher")
        blocked_class_id = uuid4()
        allowed = {uuid4()}

        with self.assertRaises(HTTPException) as ctx:
            teacher_routes._ensure_class_access(teacher_user, blocked_class_id, allowed)

        self.assertEqual(ctx.exception.status_code, 403)


class AdminRouteRegressionTests(unittest.IsolatedAsyncioTestCase):
    async def test_create_subject_rejects_class_outside_tenant(self):
        admin_routes = importlib.import_module("routes.admin")
        current_user = SimpleNamespace(tenant_id=uuid4())
        db = _DBStub({"Class": None})

        with self.assertRaises(HTTPException) as ctx:
            await admin_routes.create_subject(
                admin_routes.SubjectCreate(name="Math", class_id=str(uuid4())),
                current_user,
                db,
            )

        self.assertEqual(ctx.exception.status_code, 404)

    async def test_update_complaint_rejects_invalid_status(self):
        admin_routes = importlib.import_module("routes.admin")
        current_user = SimpleNamespace(tenant_id=uuid4(), id=uuid4())
        complaint = SimpleNamespace(
            id=uuid4(),
            tenant_id=current_user.tenant_id,
            status="open",
            resolution_note="",
            resolved_by=None,
            resolved_at=None,
        )
        db = _DBStub({"Complaint": complaint})

        with self.assertRaises(HTTPException) as ctx:
            await admin_routes.update_complaint(
                str(complaint.id),
                admin_routes.ComplaintAction(status="bad-status", resolution_note=""),
                current_user,
                db,
            )

        self.assertEqual(ctx.exception.status_code, 400)

    async def test_create_webhook_rejects_unsupported_event(self):
        admin_routes = importlib.import_module("routes.admin")
        current_user = SimpleNamespace(tenant_id=uuid4(), id=uuid4())
        db = _DBStub({})

        with self.assertRaises(HTTPException) as ctx:
            await admin_routes.create_webhook(
                admin_routes.WebhookCreate(
                    event_type="unsupported.event",
                    target_url="https://example.com/hook",
                ),
                current_user,
                db,
            )

        self.assertEqual(ctx.exception.status_code, 400)

    async def test_create_parent_link_rejects_missing_parent(self):
        admin_routes = importlib.import_module("routes.admin")
        current_user = SimpleNamespace(tenant_id=uuid4(), id=uuid4())
        db = _DBStub({"User": None})

        with self.assertRaises(HTTPException) as ctx:
            await admin_routes.create_parent_link(
                admin_routes.ParentLinkCreate(parent_id=str(uuid4()), child_id=str(uuid4())),
                current_user,
                db,
            )

        self.assertEqual(ctx.exception.status_code, 404)

    async def test_create_timetable_slot_rejects_invalid_day(self):
        admin_routes = importlib.import_module("routes.admin")
        current_user = SimpleNamespace(tenant_id=uuid4(), id=uuid4())
        db = _DBStub({})

        with self.assertRaises(HTTPException) as ctx:
            await admin_routes.create_timetable_slot(
                admin_routes.TimetableSlotCreate(
                    class_id=str(uuid4()),
                    subject_id=str(uuid4()),
                    teacher_id=str(uuid4()),
                    day_of_week=9,
                    start_time="09:00",
                    end_time="10:00",
                ),
                current_user,
                db,
            )

        self.assertEqual(ctx.exception.status_code, 400)


class StudentRouteRegressionTests(unittest.IsolatedAsyncioTestCase):
    async def test_student_upload_returns_failure_when_ingestion_fails(self):
        student_routes = importlib.import_module("routes.students")
        current_user = SimpleNamespace(tenant_id=uuid4(), id=uuid4())
        db = _DBStub({})
        file = UploadFile(filename="notes.pdf", file=io.BytesIO(b"small pdf payload"))

        with patch("ai.ingestion.ingest_document", side_effect=RuntimeError("ingest failed")):
            payload = await student_routes.student_upload(file, current_user, db)

        self.assertEqual(payload["status"], "failed")
        self.assertFalse(payload["success"])

    def test_tool_normalizer_rejects_invalid_quiz_payload(self):
        student_routes = importlib.import_module("routes.students")
        with self.assertRaises(HTTPException) as ctx:
            student_routes._normalize_tool_output("quiz", "not valid json")
        self.assertEqual(ctx.exception.status_code, 422)

    async def test_assignment_submit_rejects_invalid_assignment_uuid(self):
        student_routes = importlib.import_module("routes.students")
        current_user = SimpleNamespace(tenant_id=uuid4(), id=uuid4())
        db = _DBStub({})
        file = UploadFile(filename="submission.pdf", file=io.BytesIO(b"payload"))

        with self.assertRaises(HTTPException) as ctx:
            await student_routes.submit_assignment("bad-uuid", file, current_user, db)

        self.assertEqual(ctx.exception.status_code, 400)

    async def test_results_trends_returns_sorted_subject_and_points(self):
        from datetime import date

        student_routes = importlib.import_module("routes.students")
        tenant_id = uuid4()
        student_id = uuid4()

        math_subject_id = uuid4()
        sci_subject_id = uuid4()

        rows = [
            (
                SimpleNamespace(marks_obtained=88),
                SimpleNamespace(subject_id=math_subject_id, name="Final", exam_date=date(2026, 3, 1), max_marks=100, created_at=None),
            ),
            (
                SimpleNamespace(marks_obtained=72),
                SimpleNamespace(subject_id=math_subject_id, name="Midterm", exam_date=date(2026, 1, 15), max_marks=100, created_at=None),
            ),
            (
                SimpleNamespace(marks_obtained=42),
                SimpleNamespace(subject_id=sci_subject_id, name="Unit 1", exam_date=date(2026, 2, 1), max_marks=50, created_at=None),
            ),
        ]
        subjects = [
            SimpleNamespace(id=math_subject_id, name="Math"),
            SimpleNamespace(id=sci_subject_id, name="Science"),
        ]
        db = _ScenarioDBStub(mark_exam_rows=rows, subjects=subjects)
        current_user = SimpleNamespace(tenant_id=tenant_id, id=student_id)

        payload = await student_routes.student_result_trends(current_user, db)

        self.assertEqual([item["subject"] for item in payload], ["Math", "Science"])
        self.assertEqual(payload[0]["points"][0]["exam"], "Midterm")
        self.assertEqual(payload[0]["points"][1]["exam"], "Final")
        self.assertIn("percentage", payload[0]["points"][0])

    async def test_tools_generate_parses_structured_output_for_all_modes(self):
        student_routes = importlib.import_module("routes.students")
        current_user = SimpleNamespace(tenant_id=uuid4(), id=uuid4())
        db = _DBStub({})

        answers = {
            "quiz": '[{"question":"Q1","options":["A. One","B. Two"],"correct":"B"}]',
            "flashcards": '[{"front":"F1","back":"B1"}]',
            "mindmap": '{"label":"Root","children":[{"label":"Child"}]}',
            "flowchart": "flowchart TD\nA[Start] --> B[End]",
            "concept_map": '{"nodes":[{"id":"1","label":"Cell"}],"edges":[{"from":"1","to":"1","label":"self"}]}',
        }

        async def fake_ai_query(request, current_user, db):
            return {
                "answer": answers[request.mode],
                "citations": [{"source": "notes.pdf", "page": "1"}],
                "trace_id": "t123",
                "token_usage": 12,
                "response_time_ms": 120,
                "citation_valid": True,
            }

        with patch("routes.ai.ai_query", AsyncMock(side_effect=fake_ai_query)):
            for mode in ["quiz", "flashcards", "mindmap", "flowchart", "concept_map"]:
                payload = await student_routes.generate_study_tool(
                    student_routes.StudyToolGenerateRequest(tool=mode, topic="Biology"),
                    current_user,
                    db,
                )
                self.assertEqual(payload["tool"], mode)
                self.assertIn("data", payload)

    async def test_tools_generate_retries_once_when_json_is_malformed(self):
        student_routes = importlib.import_module("routes.students")
        current_user = SimpleNamespace(tenant_id=uuid4(), id=uuid4())
        db = _DBStub({})

        ai_mock = AsyncMock(
            side_effect=[
                {
                    "answer": "not-json",
                    "citations": [],
                    "trace_id": "t1",
                    "token_usage": 1,
                    "response_time_ms": 10,
                    "citation_valid": False,
                },
                {
                    "answer": '[{"question":"Q1","options":["A. One","B. Two"],"correct":"A"}]',
                    "citations": [],
                    "trace_id": "t2",
                    "token_usage": 1,
                    "response_time_ms": 12,
                    "citation_valid": True,
                },
            ]
        )

        with patch("routes.ai.ai_query", ai_mock):
            payload = await student_routes.generate_study_tool(
                student_routes.StudyToolGenerateRequest(tool="quiz", topic="Retry topic"),
                current_user,
                db,
            )

        self.assertEqual(ai_mock.await_count, 2)
        self.assertEqual(payload["tool"], "quiz")
        self.assertTrue(isinstance(payload["data"], list))

    async def test_assignment_submit_create_then_replace_flow(self):
        student_routes = importlib.import_module("routes.students")

        tenant_id = uuid4()
        student_id = uuid4()
        class_id = uuid4()
        assignment_id = uuid4()
        subject_id = uuid4()

        db = _ScenarioDBStub(
            enrollment=SimpleNamespace(tenant_id=tenant_id, student_id=student_id, class_id=class_id),
            assignment=SimpleNamespace(id=assignment_id, tenant_id=tenant_id, subject_id=subject_id),
            subject=SimpleNamespace(id=subject_id, tenant_id=tenant_id, class_id=class_id),
            submission=None,
        )
        current_user = SimpleNamespace(tenant_id=tenant_id, id=student_id)

        with patch("builtins.open", mock_open()):
            first = await student_routes.submit_assignment(
                str(assignment_id),
                UploadFile(filename="first.pdf", file=io.BytesIO(b"first")),
                current_user,
                db,
            )
            first_submission_id = first["submission_id"]

            second = await student_routes.submit_assignment(
                str(assignment_id),
                UploadFile(filename="second.pdf", file=io.BytesIO(b"second")),
                current_user,
                db,
            )

        self.assertTrue(first["success"])
        self.assertTrue(second["success"])
        self.assertEqual(first_submission_id, second["submission_id"])
        self.assertIsNotNone(db.submission)
        self.assertIsNone(db.submission.grade)
        self.assertIn("assignment_submissions", db.submission.submission_url)

    def test_assignment_submission_model_has_unique_constraint(self):
        assignment_models = importlib.import_module("models.assignment")
        constraints = [
            constraint
            for constraint in assignment_models.AssignmentSubmission.__table__.constraints
            if constraint.__class__.__name__ == "UniqueConstraint"
        ]
        self.assertTrue(
            any(set(constraint.columns.keys()) == {"tenant_id", "assignment_id", "student_id"} for constraint in constraints)
        )


class WebhookServiceRegressionTests(unittest.IsolatedAsyncioTestCase):
    async def test_emit_webhook_event_returns_zero_when_no_subscriptions(self):
        webhooks_service = importlib.import_module("services.webhooks")
        db = MagicMock()
        db.query.return_value.filter.return_value.all.return_value = []

        result = await webhooks_service.emit_webhook_event(
            db=db,
            tenant_id=uuid4(),
            event_type="ai.query.completed",
            data={"query_id": "q1"},
        )

        self.assertEqual(result["subscriptions"], 0)
        self.assertEqual(result["delivered"], 0)


class ParentRouteRegressionTests(unittest.TestCase):
    def test_parent_child_lookup_requires_existing_link(self):
        parent_routes = importlib.import_module("routes.parent")
        current_user = SimpleNamespace(tenant_id=uuid4(), id=uuid4())
        db = MagicMock()
        db.query.return_value.filter.return_value.order_by.return_value.first.return_value = None

        with self.assertRaises(HTTPException) as ctx:
            parent_routes._get_child_for_parent(current_user=current_user, db=db)

        self.assertEqual(ctx.exception.status_code, 404)


class RateLimitRegressionTests(unittest.IsolatedAsyncioTestCase):
    async def test_rate_limiter_blocks_after_limit_for_same_user(self):
        rate_limit = importlib.import_module("middleware.rate_limit")

        # Keep the test deterministic and isolated from global state.
        rate_limit._memory_store.clear()
        rate_limit._redis_available = False
        rate_limit._redis = None

        middleware = rate_limit.RateLimitMiddleware(app=lambda *_args, **_kwargs: None)
        middleware.MAX_REQUESTS = 2
        middleware.WINDOW_SECONDS = 60

        async def call_next(_request):
            return JSONResponse({"ok": True}, status_code=200)

        def make_request(user_id: str):
            req = Request(
                {
                    "type": "http",
                    "method": "POST",
                    "path": "/api/ai/query",
                    "headers": [],
                    "query_string": b"",
                    "state": {},
                }
            )
            req.state.user_id = user_id
            return req

        first = await middleware.dispatch(make_request("u1"), call_next)
        second = await middleware.dispatch(make_request("u1"), call_next)
        third = await middleware.dispatch(make_request("u1"), call_next)

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(third.status_code, 429)


if __name__ == "__main__":
    unittest.main()
