"""Phase 0 stability tests for Vidya OS transformation hardening."""

import hashlib
import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ["DEBUG"] = "true"

from starlette.requests import Request
from starlette.responses import JSONResponse

from auth import oauth
from middleware import tenant as tenant_middleware
from middleware.tenant import TenantMiddleware
from src.domains.academic.application import student_reviews
from src.domains.academic.routes import students as student_routes


def _make_request(path="/api/student/dashboard", token="stable-token"):
    scope = {
        "type": "http",
        "method": "GET",
        "path": path,
        "headers": [(b"authorization", f"Bearer {token}".encode())],
        "query_string": b"",
        "state": {},
    }
    return Request(scope)


async def _ok_handler(_request):
    return JSONResponse({"ok": True}, status_code=200)


class OAuthConcurrencyTests(unittest.IsolatedAsyncioTestCase):
    async def test_verify_google_token_offloads_sync_work_to_threadpool(self):
        payload = {"email": "student@example.com"}
        with patch.object(oauth.asyncio, "to_thread", new=AsyncMock(return_value=payload)) as to_thread:
            result = await oauth.verify_google_token("sample-token")

        self.assertEqual(result, payload)
        to_thread.assert_awaited_once()
        args = to_thread.await_args.args
        self.assertIs(args[0], oauth._cached_verify)
        self.assertEqual(args[1], hashlib.sha256(b"sample-token").hexdigest())
        self.assertEqual(args[2], "sample-token")

    async def test_verify_google_token_returns_none_when_threadpool_call_fails(self):
        with patch.object(oauth.asyncio, "to_thread", new=AsyncMock(side_effect=RuntimeError("boom"))):
            result = await oauth.verify_google_token("sample-token")

        self.assertIsNone(result)


class TenantCacheReuseTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        tenant_middleware._jwt_cache.clear()
        self.middleware = TenantMiddleware(app=None)

    def tearDown(self):
        tenant_middleware._jwt_cache.clear()

    async def test_reuses_cached_payload_for_repeat_requests(self):
        payload = {"tenant_id": "tenant-1", "role": "student", "user_id": "user-1"}

        with patch("middleware.tenant.decode_access_token", return_value=payload) as decode_mock:
            first_request = _make_request(token="cache-me")
            second_request = _make_request(token="cache-me")

            await self.middleware.dispatch(first_request, _ok_handler)
            await self.middleware.dispatch(second_request, _ok_handler)

        decode_mock.assert_called_once_with("cache-me")
        self.assertEqual(first_request.state.tenant_id, "tenant-1")
        self.assertEqual(second_request.state.tenant_id, "tenant-1")


class DeferredReviewExecutionTests(unittest.TestCase):
    def _make_review_db(self):
        review = SimpleNamespace(
            topic="Quadratics",
            subject_id=uuid4(),
            interval_days=1,
            ease_factor=2.5,
            review_count=0,
            updated_at=None,
            next_review_at=None,
        )
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = review
        return db, review

    def test_complete_student_review_submits_deferred_work_with_fresh_session(self):
        db, review = self._make_review_db()
        review_uuid = uuid4()
        bg_db = MagicMock()
        session_factory = MagicMock(return_value=bg_db)
        snapshot_mock = MagicMock(
            side_effect=[
                {"mastery_score": 32.0},
                {"mastery_score": 46.0},
            ]
        )
        record_completion = MagicMock()
        record_outcome = MagicMock()

        with patch.object(student_reviews._DEFERRED_REVIEW_EXECUTOR, "submit") as submit_mock:
            result = student_reviews.complete_student_review(
                db=db,
                tenant_id=uuid4(),
                student_id=uuid4(),
                review_id=str(review_uuid),
                rating=4,
                parse_uuid_fn=lambda value, _field: UUID(str(value)),
                get_topic_mastery_snapshot_fn=snapshot_mock,
                record_review_completion_fn=record_completion,
                record_mastery_outcome_fn=record_outcome,
                db_session_factory=session_factory,
            )

        db.commit.assert_called_once()
        submit_mock.assert_called_once()
        deferred_fn = submit_mock.call_args.args[0]
        deferred_fn()

        session_factory.assert_called_once_with()
        self.assertEqual(snapshot_mock.call_count, 2)
        record_completion.assert_called_once()
        record_outcome.assert_called_once()
        bg_db.commit.assert_called_once()
        bg_db.close.assert_called_once()
        self.assertEqual(result["review_id"], str(review_uuid))
        self.assertEqual(result["review_count"], 1)
        self.assertGreater(review.interval_days, 1)

    def test_deferred_review_work_skips_background_io_without_session_factory(self):
        db, _review = self._make_review_db()
        snapshot_mock = MagicMock()
        record_completion = MagicMock()
        record_outcome = MagicMock()

        with (
            patch.object(student_reviews._DEFERRED_REVIEW_EXECUTOR, "submit") as submit_mock,
            patch.object(student_reviews.logger, "info") as info_mock,
        ):
            student_reviews.complete_student_review(
                db=db,
                tenant_id=uuid4(),
                student_id=uuid4(),
                review_id=str(uuid4()),
                rating=3,
                parse_uuid_fn=lambda value, _field: UUID(str(value)),
                get_topic_mastery_snapshot_fn=snapshot_mock,
                record_review_completion_fn=record_completion,
                record_mastery_outcome_fn=record_outcome,
                db_session_factory=None,
            )
            deferred_fn = submit_mock.call_args.args[0]
            deferred_fn()

        info_mock.assert_called_once()
        snapshot_mock.assert_not_called()
        record_completion.assert_not_called()
        record_outcome.assert_not_called()


class StudentReviewRouteWiringTests(unittest.IsolatedAsyncioTestCase):
    async def test_complete_review_route_passes_session_factory(self):
        current_user = SimpleNamespace(tenant_id=uuid4(), id=uuid4())
        db = MagicMock()

        with patch.object(student_routes, "_complete_student_review_impl", return_value={"success": True}) as impl_mock:
            payload = await student_routes.complete_review(
                str(uuid4()),
                student_routes.ReviewCompleteRequest(rating=4),
                current_user,
                db,
            )

        self.assertEqual(payload, {"success": True})
        self.assertIs(
            impl_mock.call_args.kwargs["db_session_factory"],
            student_routes.SessionLocal,
        )


if __name__ == "__main__":
    unittest.main()
