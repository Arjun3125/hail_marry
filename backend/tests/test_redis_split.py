import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Ensure backend imports resolve
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from config import Settings
from src.infrastructure.llm.cache import _get_redis as get_state_redis
from src.domains.platform.services.ai_queue import _get_redis_client as get_broker_redis
from middleware.rate_limit import _get_redis as get_rate_limit_redis

class TestRedisSplit(unittest.TestCase):
    def test_config_isolation(self):
        """Verify that RedisSettings correctly parses distinct URLs."""
        with patch.dict(os.environ, {
            "REDIS_STATE_URL": "redis://state-host:6379/1",
            "REDIS_BROKER_URL": "redis://broker-host:6379/2",
            "DEBUG": "true",
            "APP_ENV": "test",
            "JWT_SECRET": "test-secret-key-that-is-at-least-32-chars-long",
            "REFRESH_SECRET_KEY": "test-refresh-key-that-is-at-least-32-chars-long",
        }):
            # Settings might have been initialized already, so we force-reparse for the test
            settings = Settings()
            self.assertEqual(settings.redis.state_url, "redis://state-host:6379/1")
            self.assertEqual(settings.redis.broker_url, "redis://broker-host:6379/2")

    @patch("redis.from_url")
    def test_service_routing(self, mock_from_url):
        """Verify that each service connects to the correct Redis role."""
        mock_redis = MagicMock()
        mock_from_url.return_value = mock_redis
        
        with patch.dict(os.environ, {
            "REDIS_STATE_URL": "redis://state-host:6379/1",
            "REDIS_BROKER_URL": "redis://broker-host:6379/2"
        }):
            # 1. Test AI Cache / State
            from src.infrastructure.llm import cache
            cache._redis_available = None # Reset lazy init
            get_state_redis()
            mock_from_url.assert_any_call("redis://state-host:6379/1", decode_responses=True, socket_timeout=1, socket_connect_timeout=1)
            
            # 2. Test AI Queue / Broker
            from src.domains.platform.services import ai_queue
            ai_queue._redis_available = None # Reset lazy init
            get_broker_redis()
            mock_from_url.assert_any_call("redis://broker-host:6379/2", decode_responses=True, socket_connect_timeout=1, socket_timeout=1)
            
            # 3. Test Rate Limiter / State
            from middleware import rate_limit
            rate_limit._redis_initialized = False  # Reset lazy init
            rate_limit._redis = None
            get_rate_limit_redis()
            mock_from_url.assert_any_call("redis://state-host:6379/1", decode_responses=True, socket_connect_timeout=5)

if __name__ == "__main__":
    unittest.main()
