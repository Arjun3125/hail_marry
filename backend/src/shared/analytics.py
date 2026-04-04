import os
import logging

logger = logging.getLogger("analytics")

try:
    from posthog import Posthog
    _HAS_POSTHOG = True
except ImportError:
    _HAS_POSTHOG = False
    logger.debug("posthog package not installed — analytics disabled.")

class AnalyticsService:
    def __init__(self):
        self.client = None

        if not _HAS_POSTHOG:
            return

        api_key = os.getenv("POSTHOG_API_KEY")
        host = os.getenv("POSTHOG_HOST", "https://us.i.posthog.com")

        if api_key:
            try:
                self.client = Posthog(api_key, host=host)
                logger.info("PostHog initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize PostHog: {e}")
        else:
            logger.info("PostHog analytics disabled (no POSTHOG_API_KEY).")

    def track_event(self, distinct_id: str, event_name: str, properties: dict = None):
        if not self.client:
            return
        try:
            self.client.capture(distinct_id, event_name, properties or {})
        except Exception as e:
            logger.error(f"Error tracking event {event_name}: {e}")

    def identify_user(self, user_id: str, properties: dict):
        if not self.client:
            return
        try:
            self.client.identify(user_id, properties)
        except Exception as e:
            logger.error(f"Error identifying user {user_id}: {e}")

    def shutdown(self):
        if self.client:
            self.client.flush()
            self.client.shutdown()

# Singleton instance
analytics = AnalyticsService()
