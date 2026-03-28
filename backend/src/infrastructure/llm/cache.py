"""
AI Response Cache — Redis-backed caching for AI query responses.
Caches by query hash + mode + tenant to avoid redundant LLM calls.
"""
import hashlib
import json
import os
from typing import Optional


from config import settings

_redis = None
_redis_available = None


def _get_redis():
    """Lazy-load Redis client."""
    global _redis, _redis_available
    if _redis_available is None:
        try:
            import redis as redis_lib
            redis_url = (
                os.getenv("REDIS_STATE_URL")
                or os.getenv("REDIS_URL")
                or settings.redis.state_url
            )
            _redis = redis_lib.from_url(redis_url, decode_responses=True)
            _redis.ping()
            _redis_available = True
        except Exception:
            _redis_available = False
            _redis = None
    return _redis if _redis_available else None


# TTL per mode (seconds)
MODE_TTL = {
    "qa": 86400,           # 24 hours
    "study_guide": 604800, # 7 days
    "quiz": 604800,        # 7 days
    "concept_map": 604800, # 7 days
    "flashcards": 604800,  # 7 days
    "mindmap": 604800,     # 7 days
    "flowchart": 604800,   # 7 days
    "weak_topic": 86400,   # 24 hours
}


def _cache_key(tenant_id: str, query: str, mode: str, subject_id: str = "") -> str:
    """Generate cache key from query parameters."""
    raw = f"{tenant_id}:{mode}:{subject_id}:{query.strip().lower()}"
    query_hash = hashlib.sha256(raw.encode()).hexdigest()[:16]
    return f"ai_cache:{query_hash}"


def get_cached_response(
    tenant_id: str, query: str, mode: str, subject_id: str = ""
) -> Optional[dict]:
    """
    Check if a cached response exists for this query.
    Returns the cached response dict or None.
    """
    redis_client = _get_redis()
    if not redis_client:
        return None

    try:
        key = _cache_key(tenant_id, query, mode, subject_id)
        cached = redis_client.get(key)
        if cached:
            return json.loads(cached)
    except Exception:
        pass

    return None


def cache_response(
    tenant_id: str,
    query: str,
    mode: str,
    response: dict,
    subject_id: str = "",
) -> bool:
    """
    Cache an AI response. Returns True if cached successfully.
    """
    redis_client = _get_redis()
    if not redis_client:
        return False

    try:
        key = _cache_key(tenant_id, query, mode, subject_id)
        ttl = MODE_TTL.get(mode, 86400)
        data = json.dumps(response)
        redis_client.setex(key, ttl, data)
        return True
    except Exception:
        return False


def invalidate_tenant_cache(tenant_id: str) -> int:
    """Invalidate all cached AI responses for a tenant."""
    redis_client = _get_redis()
    if not redis_client:
        return 0

    try:
        # Scan for matching keys (not ideal at scale, but fine for pilot)
        count = 0
        for key in redis_client.scan_iter(f"ai_cache:*"):
            redis_client.delete(key)
            count += 1
        return count
    except Exception:
        return 0
