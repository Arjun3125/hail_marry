import pytest
from unittest.mock import patch, MagicMock

def test_job_not_claimed_while_paused():
    """Verify that queue popping immediately stops while global Pause is active."""
    from services.ai_queue import claim_next_job
    
    with patch("services.ai_queue.is_queue_paused", return_value=True):
        job_id = claim_next_job(timeout_seconds=0)
        assert job_id is None, "Worker improperly attempted to claim a job while queue was globally paused."

def test_drain_queue_moves_to_dead_letter():
    """Verify jobs are swept cleanly to DLQ when drained."""
    import time
    from services.ai_queue import drain_queue
    
    # Mocking Redis pipeline and client actions
    mock_redis = MagicMock()
    # Let smembers return our mock tenant
    mock_redis.smembers.return_value = {"tenant_1"}
    # Let zpopmin return some fake jobs the first call, empty the next
    mock_redis.zpopmin.side_effect = [
        [("job-123", time.time()), ("job-456", time.time())],
        [] # Stop loop
    ]
    
    mock_job = {
        "job_id": "job-123",
        "job_type": "test",
        "priority": 10,
        "status": "pending",
        "tenant_id": "tenant_1",
        "user_id": "user_1",
        "events": [],
    }
    
    with patch("services.ai_queue._require_queue_client", return_value=mock_redis), \
         patch("services.ai_queue.get_job", return_value=mock_job), \
         patch("services.ai_queue.save_job"):
         
        drained_count = drain_queue()
        assert drained_count == 2
        mock_redis.zadd.assert_called()
