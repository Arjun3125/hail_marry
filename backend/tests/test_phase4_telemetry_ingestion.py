import sys
import unittest
import uuid
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


class Phase4TelemetryIngestionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from database import Base, engine
        from src.domains.identity.models.tenant import Tenant  # noqa: F401
        from src.domains.identity.models.user import User  # noqa: F401
        from src.domains.platform.models.analytics_event import AnalyticsEvent  # noqa: F401

        Base.metadata.create_all(bind=engine)

    def setUp(self):
        from database import SessionLocal
        from src.domains.identity.models.tenant import Tenant
        from src.domains.identity.models.user import User
        from src.domains.platform.models.analytics_event import AnalyticsEvent

        self.db = SessionLocal()
        self.Tenant = Tenant
        self.User = User
        self.AnalyticsEvent = AnalyticsEvent

        self.tenant_id = uuid.uuid4()
        self.user_id = uuid.uuid4()
        self.db.add(Tenant(id=self.tenant_id, name="Vidya Test", domain=f"telemetry-{self.tenant_id}.edu"))
        self.db.add(
            User(
                id=self.user_id,
                tenant_id=self.tenant_id,
                email=f"telemetry-{self.user_id}@example.com",
                full_name="Telemetry Student",
                role="student",
            )
        )
        self.db.commit()

    def tearDown(self):
        self.db.query(self.AnalyticsEvent).delete()
        self.db.query(self.User).delete()
        self.db.query(self.Tenant).delete()
        self.db.commit()
        self.db.close()

    def test_record_business_event_persists_warehouse_friendly_row(self):
        from src.domains.platform.services.telemetry_events import record_business_event

        record_business_event(
            "student_risk_recomputed",
            db=self.db,
            tenant_id=str(self.tenant_id),
            user_id=str(self.user_id),
            event_family="risk",
            surface="risk_cron",
            target="student_profile",
            channel="system",
            value=2.0,
            metadata={"academic_risk": "high"},
        )
        self.db.commit()

        row = self.db.query(self.AnalyticsEvent).one()
        self.assertEqual(row.event_name, "student_risk_recomputed")
        self.assertEqual(row.event_family, "risk")
        self.assertEqual(row.surface, "risk_cron")
        self.assertEqual(row.target, "student_profile")
        self.assertEqual(row.channel, "system")
        self.assertEqual(row.value, 2.0)
        self.assertEqual((row.metadata_ or {}).get("academic_risk"), "high")

    def test_observe_personalization_event_persists_analytics_event(self):
        from src.domains.platform.services.metrics_registry import observe_personalization_event

        observe_personalization_event(
            "study_path_view",
            surface="overview",
            target="study_guide",
            db=self.db,
            tenant_id=str(self.tenant_id),
            user_id=str(self.user_id),
            channel="web",
            metadata={"topic": "Photosynthesis"},
        )
        self.db.commit()

        row = self.db.query(self.AnalyticsEvent).filter(self.AnalyticsEvent.event_family == "personalization").one()
        self.assertEqual(row.event_name, "study_path_view")
        self.assertEqual(row.surface, "overview")
        self.assertEqual(row.target, "study_guide")
        self.assertEqual(row.channel, "web")
        self.assertEqual((row.metadata_ or {}).get("topic"), "Photosynthesis")


if __name__ == "__main__":
    unittest.main()
