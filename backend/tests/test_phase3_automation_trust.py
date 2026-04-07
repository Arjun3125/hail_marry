import asyncio
import sys
import unittest
import uuid
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


class NotificationDispatchAuditTests(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        from database import Base, engine
        from src.domains.identity.models.tenant import Tenant  # noqa: F401
        from src.domains.identity.models.user import User  # noqa: F401
        from src.domains.academic.models.parent_link import ParentLink  # noqa: F401
        from src.domains.platform.models.notification import Notification, NotificationPreference  # noqa: F401
        from src.domains.platform.models.whatsapp_models import PhoneUserLink  # noqa: F401

        Base.metadata.create_all(bind=engine)

    def setUp(self):
        from database import SessionLocal
        from src.domains.identity.models.tenant import Tenant
        from src.domains.identity.models.user import User
        from src.domains.academic.models.parent_link import ParentLink
        from src.domains.platform.models.notification import Notification, NotificationPreference
        from src.domains.platform.models.whatsapp_models import PhoneUserLink
        from src.domains.platform.services import notifications

        self.db = SessionLocal()
        self.Tenant = Tenant
        self.User = User
        self.ParentLink = ParentLink
        self.Notification = Notification
        self.NotificationPreference = NotificationPreference
        self.PhoneUserLink = PhoneUserLink
        self.notifications = notifications

        self.notifications._notifications.clear()
        self.notifications._subscribers.clear()

        self.tenant_id = uuid.uuid4()
        self.parent_id = uuid.uuid4()
        self.student_id = uuid.uuid4()

        self.db.add(Tenant(id=self.tenant_id, name="Vidya Test", domain=f"vidya-{self.tenant_id}.edu"))
        self.db.add(User(
            id=self.parent_id,
            tenant_id=self.tenant_id,
            email=f"parent-{self.parent_id}@example.com",
            full_name="Parent User",
            role="parent",
        ))
        self.db.add(User(
            id=self.student_id,
            tenant_id=self.tenant_id,
            email=f"student-{self.student_id}@example.com",
            full_name="Student User",
            role="student",
            preferred_locale="hi",
        ))
        self.db.add(ParentLink(
            tenant_id=self.tenant_id,
            parent_id=self.parent_id,
            child_id=self.student_id,
            relationship_type="parent",
        ))
        self.db.commit()

    def tearDown(self):
        self.db.query(self.NotificationPreference).delete()
        self.db.query(self.Notification).delete()
        self.db.query(self.PhoneUserLink).delete()
        self.db.query(self.ParentLink).delete()
        self.db.query(self.User).delete()
        self.db.query(self.Tenant).delete()
        self.db.commit()
        self.db.close()

    async def test_dispatch_notification_persists_one_row_per_channel_without_duplicate_in_app_copy(self):
        from src.domains.platform.services.notification_dispatch import dispatch_notification

        results = await dispatch_notification(
            tenant_id=str(self.tenant_id),
            recipient_id=str(self.parent_id),
            recipient_role="parent",
            category="attendance",
            title="Attendance Alert",
            body="Student User was absent today.",
            related_entity_type="attendance",
            related_entity_id=str(self.student_id),
            preferred_channel="whatsapp",
        )

        rows = self.db.query(self.Notification).filter(
            self.Notification.user_id == self.parent_id,
        ).all()

        self.assertEqual(len(rows), 2)
        self.assertEqual({row.recipient_channel for row in rows}, {"whatsapp", "in_app"})
        self.assertEqual(sorted(result["channel"] for result in results), ["in_app", "whatsapp"])

    async def test_attendance_notifier_creates_auditable_parent_communication_records(self):
        from src.domains.academic.services.attendance_notifier import notify_parents_on_absence

        results = await notify_parents_on_absence(
            tenant_id=str(self.tenant_id),
            student_id=str(self.student_id),
            class_name="Class 10 A",
            date_str="2026-04-06",
            status="absent",
        )

        rows = self.db.query(self.Notification).filter(
            self.Notification.user_id == self.parent_id,
        ).all()

        self.assertEqual(len(rows), 2)
        self.assertTrue(all(row.category == "attendance" for row in rows))
        self.assertTrue(all(row.related_entity_type == "attendance" for row in rows))
        self.assertTrue(all(row.triggered_by == "system" for row in rows))
        self.assertTrue(any((row.data or {}).get("student_id") == str(self.student_id) for row in rows))
        self.assertEqual(sorted(result["channel"] for result in results), ["in_app", "whatsapp"])


class BackgroundRuntimeTests(unittest.TestCase):
    def test_submit_async_job_runs_coroutine_on_local_runtime(self):
        from src.domains.platform.services.background_runtime import submit_async_job

        async def _sample(value: int) -> int:
            await asyncio.sleep(0)
            return value * 2

        future = submit_async_job("phase3-sample", _sample, 7)
        self.assertEqual(future.result(timeout=2), 14)

    def test_teacher_attendance_tool_submits_parent_notifications_to_background_runtime(self):
        from src.shared.ai_tools.whatsapp_teacher_tools import (
            mark_batch_attendance,
            notify_parents_bulk_absence,
        )

        student = SimpleNamespace(id=uuid.uuid4(), full_name="Rohan Sharma")
        teacher_id = str(uuid.uuid4())
        tenant_id = str(uuid.uuid4())

        class _FakeQuery:
            def __init__(self, result):
                self._result = result

            def filter(self, *_args, **_kwargs):
                return self

            def all(self):
                return list(self._result)

            def first(self):
                return self._result

        class _FakeDb:
            def __init__(self):
                self.added = []

            def query(self, model):
                from src.domains.academic.models.attendance import Attendance
                from src.domains.identity.models.user import User

                if model is User:
                    return _FakeQuery([student])
                if model is Attendance:
                    return _FakeQuery(None)
                raise AssertionError(f"Unexpected model query: {model}")

            def add(self, item):
                self.added.append(item)

            def commit(self):
                return None

            def close(self):
                return None

        fake_db = _FakeDb()

        with patch("src.shared.ai_tools.whatsapp_teacher_tools.SessionLocal", return_value=fake_db), \
             patch("src.shared.ai_tools.whatsapp_teacher_tools.submit_async_job") as submit_async_job:
            result = mark_batch_attendance(
                tenant_id=tenant_id,
                user_id=teacher_id,
                class_name="Class 10 A",
                absent_student_names=["Rohan"],
            )

        self.assertIn("1 students marked absent", result)
        submit_async_job.assert_called_once()
        args, kwargs = submit_async_job.call_args
        self.assertEqual(args[0], "parent-attendance-notifications")
        self.assertIs(args[1], notify_parents_bulk_absence)
        self.assertEqual(kwargs["tenant_id"], tenant_id)
        self.assertEqual(kwargs["absences"][0]["student_id"], str(student.id))


if __name__ == "__main__":
    unittest.main()
