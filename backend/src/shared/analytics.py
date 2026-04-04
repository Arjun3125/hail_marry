import os
import logging
from posthog import Posthog

logger = logging.getLogger("analytics")

class AnalyticsService:
    def __init__(self):
        self.api_key = os.getenv("POSTHOG_API_KEY")
        self.host = os.getenv("POSTHOG_HOST", "https://us.i.posthog.com")
        self.client = None
        
        if self.api_key:
            try:
                self.client = Posthog(self.api_key, host=self.host)
                logger.info("PostHog initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize PostHog: {e}")
        else:
            logger.warning("POSTHOG_API_KEY not found. Analytics will be disabled.")

    def track_event(self, distinct_id: str, event_name: str, properties: dict = None):
        """Track a backend event in PostHog."""
        if not self.client:
            return
            
        try:
            self.client.capture(distinct_id, event_name, properties or {})
        except Exception as e:
            logger.error(f"Error tracking event {event_name}: {e}")

    def identify_user(self, user_id: str, properties: dict):
        """Identify a user and set their properties in PostHog."""
        if not self.client:
            return
            
        try:
            self.client.identify(user_id, properties)
        except Exception as e:
            logger.error(f"Error identifying user {user_id}: {e}")

    def shutdown(self):
        """Flush and shutdown the PostHog client."""
        if self.client:
            self.client.flush()
            self.client.shutdown()

# Singleton instance
analytics = AnalyticsService()
