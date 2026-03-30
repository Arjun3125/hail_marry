"""Redis-backed mascot session state with an in-memory fallback."""
from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone

from src.infrastructure.llm.cache import _get_redis
from src.domains.platform.services.mascot_schemas import PendingMascotAction

_session_fallback: dict[str, dict] = {}
_pending_fallback: dict[str, dict] = {}
_TTL_SECONDS = 60 * 60 * 24
_RECENT_MUTATION_LIMIT = 20


def _session_key(session_id: str) -> str:
    return f"mascot:session:{session_id}"


def _pending_key(confirmation_id: str) -> str:
    return f"mascot:confirm:{confirmation_id}"


def build_session_id(*, channel: str, user_id: str, provided: str | None = None) -> str:
    if provided:
        return provided
    return f"{channel}:{user_id}"


def load_session(session_id: str) -> dict:
    redis = _get_redis()
    if redis:
        raw = redis.get(_session_key(session_id))
        if raw:
            try:
                return json.loads(raw)
            except Exception:
                return {}
    return deepcopy(_session_fallback.get(session_id, {}))


def save_session(session_id: str, payload: dict) -> None:
    data = deepcopy(payload)
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    redis = _get_redis()
    if redis:
        redis.setex(_session_key(session_id), _TTL_SECONDS, json.dumps(data))
        return
    _session_fallback[session_id] = data


def clear_session(session_id: str) -> None:
    redis = _get_redis()
    if redis:
        redis.delete(_session_key(session_id))
    _session_fallback.pop(session_id, None)


def store_pending_action(action: PendingMascotAction) -> None:
    payload = action.model_dump()
    redis = _get_redis()
    if redis:
        redis.setex(_pending_key(action.confirmation_id), _TTL_SECONDS, json.dumps(payload))
        return
    _pending_fallback[action.confirmation_id] = payload


def load_pending_action(confirmation_id: str) -> PendingMascotAction | None:
    redis = _get_redis()
    if redis:
        raw = redis.get(_pending_key(confirmation_id))
        if raw:
            try:
                return PendingMascotAction(**json.loads(raw))
            except Exception:
                return None
    payload = _pending_fallback.get(confirmation_id)
    return PendingMascotAction(**payload) if payload else None


def delete_pending_action(confirmation_id: str) -> None:
    redis = _get_redis()
    if redis:
        redis.delete(_pending_key(confirmation_id))
    _pending_fallback.pop(confirmation_id, None)


def mutation_seen_recently(session_id: str, signature: str) -> bool:
    session = load_session(session_id)
    recent = session.get("recent_mutations", [])
    return any(item.get("signature") == signature for item in recent if isinstance(item, dict))


def remember_mutation(session_id: str, signature: str) -> None:
    session = load_session(session_id)
    recent = [item for item in session.get("recent_mutations", []) if isinstance(item, dict)]
    recent = [item for item in recent if item.get("signature") != signature]
    recent.insert(0, {"signature": signature, "recorded_at": datetime.now(timezone.utc).isoformat()})
    session["recent_mutations"] = recent[:_RECENT_MUTATION_LIMIT]
    save_session(session_id, session)
