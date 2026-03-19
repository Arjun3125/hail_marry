import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Ensure backend imports resolve
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Set test env vars before importing config
os.environ["REDIS_STATE_URL"] = "redis://state-host:6379/1"
os.environ["REDIS_BROKER_URL"] = "redis://broker-host:6379/2"

from config import Settings
from src.infrastructure.llm.cache import _get_redis as get_state_redis
from src.domains.platform.services.ai_queue import _get_redis_client as get_broker_redis
from middleware.rate_limit import _get_redis as get_rate_limit_redis

class TestRedisSplit(unittest.TestCase):
    def test_config_isolation(self):
        """Verify that RedisSettings correctly parses distinct URLs."""
        settings = Settings()
        self.assertEqual(settings.redis.state_url, "redis://state-host:6379/1")
        self.assertEqual(settings.redis.broker_url, "redis://broker-host:6379/2")

    @patch("redis.from_url")
    def test_service_routing(self, mock_from_url):
        """Verify that each service connects to the correct Redis role."""
        mock_redis = MagicMock()
        mock_from_url.return_value = mock_redis
        
        # 1. Test AI Cache / State
        from src.infrastructure.llm import cache
        cache._redis_available = None # Reset lazy init
        get_state_redis()
        mock_from_url.assert_any_call("redis://state-host:6379/1", decode_responses=True)
        
        # 2. Test AI Queue / Broker
        from src.domains.platform.services import ai_queue
        ai_queue._redis_available = None # Reset lazy init
        get_broker_redis()
        mock_from_url.assert_any_call("redis://broker-host:6379/2", decode_responses=True)
        
        # 3. Test Rate Limiter / State
        from middleware import rate_limit
        rate_limit._redis_available = None # Reset lazy init
        get_rate_limit_redis()
        mock_from_url.assert_any_call("redis://state-host:6379/1", decode_responses=True)

if __name__ == "__main__":
    unittest.main()
