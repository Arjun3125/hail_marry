"""Tests for services/notifications.py — durable notification store."""
import os
import sys
import asyncio
import unittest
import uuid
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ["DEBUG"] = "true"


class NotificationStoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from database import Base, engine
        from src.domains.platform.models.notification import Notification  # noqa: F401 - ensure table registered
        Base.metadata.create_all(bind=engine)

    def setUp(self):
        from src.domains.platform.services import notifications
        from database import SessionLocal
        from src.domains.platform.models.notification import Notification
        from src.domains.identity.models.tenant import Tenant
        from src.domains.identity.models.user import User

        self.db = SessionLocal()
        self.tenant_id = uuid.uuid4()
        self.user_id = uuid.uuid4()
        self.Tenant = Tenant
        self.User = User
        self.db.add(Tenant(id=self.tenant_id, name="Test School", domain=f"test-{self.tenant_id}.edu"))
        self.db.add(User(
            id=self.user_id,
            tenant_id=self.tenant_id,
            email=f"user-{self.user_id}@example.com",
            full_name="Test User",
            role="student",
        ))
        self.db.commit()

        self.Notification = Notification
        notifications._notifications.clear()
        notifications._subscribers.clear()
        self.ns = notifications

    def tearDown(self):
        self.db.query(self.Notification).delete()
        self.db.query(self.User).delete()
        self.db.query(self.Tenant).delete()
        self.db.commit()
        self.db.close()

    def test_add_and_get(self):
        self.ns.add_notification(str(self.user_id), title="Test", body="Hello")
        items = self.ns.get_notifications(str(self.user_id))
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["title"], "Test")
        self.assertFalse(items[0]["read"])

    def test_get_empty_user(self):
        items = self.ns.get_notifications(str(uuid.uuid4()))
        self.assertEqual(items, [])

    def test_mark_read(self):
        n = self.ns.add_notification(str(self.user_id), title="T", body="B")
        self.assertTrue(self.ns.mark_read(str(self.user_id), n["id"]))
        items = self.ns.get_notifications(str(self.user_id))
        self.assertTrue(items[0]["read"])

    def test_mark_read_nonexistent(self):
        self.assertFalse(self.ns.mark_read(str(self.user_id), str(uuid.uuid4())))

    def test_unread_filter(self):
        self.ns.add_notification(str(self.user_id), title="A", body="1")
        n2 = self.ns.add_notification(str(self.user_id), title="B", body="2")
        self.ns.mark_read(str(self.user_id), n2["id"])
        unread = self.ns.get_notifications(str(self.user_id), unread_only=True)
        self.assertEqual(len(unread), 1)
        self.assertEqual(unread[0]["title"], "A")

    def test_newest_first_ordering(self):
        self.ns.add_notification(str(self.user_id), title="First", body="1")
        self.ns.add_notification(str(self.user_id), title="Second", body="2")
        items = self.ns.get_notifications(str(self.user_id))
        self.assertEqual(items[0]["title"], "Second")

    def test_category_preserved(self):
        self.ns.add_notification(str(self.user_id), title="T", body="B", category="ai_complete")
        items = self.ns.get_notifications(str(self.user_id))
        self.assertEqual(items[0]["category"], "ai_complete")


class SubscriptionTests(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        from database import Base, engine
        from src.domains.platform.models.notification import Notification  # noqa: F401 - ensure table registered
        Base.metadata.create_all(bind=engine)

    def setUp(self):
        from src.domains.platform.services import notifications
        from database import SessionLocal
        from src.domains.platform.models.notification import Notification
        from src.domains.identity.models.tenant import Tenant
        from src.domains.identity.models.user import User

        self.db = SessionLocal()
        self.tenant_id = uuid.uuid4()
        self.user_id = uuid.uuid4()
        self.Tenant = Tenant
        self.User = User
        self.db.add(Tenant(id=self.tenant_id, name="Test School", domain=f"test-{self.tenant_id}.edu"))
        self.db.add(User(
            id=self.user_id,
            tenant_id=self.tenant_id,
            email=f"user-{self.user_id}@example.com",
            full_name="Test User",
            role="student",
        ))
        self.db.commit()

        self.Notification = Notification
        notifications._notifications.clear()
        notifications._subscribers.clear()
        self.ns = notifications

    def tearDown(self):
        self.db.query(self.Notification).delete()
        self.db.query(self.User).delete()
        self.db.query(self.Tenant).delete()
        self.db.commit()
        self.db.close()

    async def test_subscriber_receives_push(self):
        queue = self.ns.subscribe(str(self.user_id))
        self.ns.add_notification(str(self.user_id), title="Push", body="Hello")
        msg = await asyncio.wait_for(queue.get(), timeout=1.0)
        self.assertEqual(msg["title"], "Push")
        self.ns.unsubscribe(str(self.user_id), queue)

    async def test_unsubscribe_removes_queue(self):
        queue = self.ns.subscribe(str(self.user_id))
        self.ns.unsubscribe(str(self.user_id), queue)
        self.assertNotIn(queue, self.ns._subscribers.get(str(self.user_id), []))


if __name__ == "__main__":
    unittest.main()
