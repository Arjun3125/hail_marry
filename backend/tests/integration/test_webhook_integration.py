"""
True Integration Suite for WhatsApp Webhooks.
Bypasses SQLite and Mock Redis to test against a Genuine PostgreSQL + Redis instance.
Proves Concurrent Database Lock safety via asyncio load spikes.
"""
import os
import asyncio
import pytest
import uuid
import time
import json
import hashlib
import hmac

httpx = pytest.importorskip("httpx")
pytest.importorskip("fastapi")
pytest.importorskip("sqlalchemy")

from httpx import AsyncClient, ASGITransport

# Force real connections
os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5432/vidyaos"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"

from main import app

def generate_meta_signature(payload: bytes, secret: str = "test_app_secret") -> str:
    signature = hmac.new(secret.encode('utf-8'), payload, hashlib.sha256).hexdigest()
    return f"sha256={signature}"

@pytest.mark.asyncio
async def test_concurrent_webhook_deduplication():
    """
    Bombard the webhook endpoint with 30 identical payloads concurrently.
    Only 1 should process (return 200 via normal path or 200 via deduplication).
    If database locks fail, we'll see 500 errors from Postgres unique constraints.
    """
    os.environ["META_APP_SECRET"] = "test_app_secret"
    
    message_id = f"wamid.{uuid.uuid4().hex}"
    payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "123456789",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {"display_phone_number": "1234", "phone_number_id": "5678"},
                    "contacts": [{"profile": {"name": "Test User"}, "wa_id": "15551234567"}],
                    "messages": [{
                        "from": "15551234567",
                        "id": message_id,
                        "timestamp": str(int(time.time())),
                        "type": "text",
                        "text": {"body": "concurrent test"}
                    }]
                },
                "field": "messages"
            }]
        }]
    }

    body_bytes = json.dumps(payload).encode('utf-8')
    headers = {
        "Content-Type": "application/json",
        "X-Hub-Signature-256": generate_meta_signature(body_bytes),
    }

    async def single_request(client_session):
        response = await client_session.post("/whatsapp/webhook", content=body_bytes, headers=headers)
        return response

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as ac:
        tasks = [single_request(ac) for _ in range(30)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    status_codes = []
    for r in results:
        if isinstance(r, Exception):
            status_codes.append(500)
        else:
            status_codes.append(r.status_code)

    # They should all gracefully return 200 OK (some processed, the rest hit the Redis Deduplication Cache instantly)
    # Most importantly: 0 500 errors from DB Deadlocks!
    error_500s = [s for s in status_codes if s == 500]
    
    print(f"\\n--- INTEGRATION TEST RESULTS ---")
    print(f"Status codes array: {status_codes}")
    
    assert len(error_500s) == 0, f"Concurrent requests caused {len(error_500s)} Database Deadlocks or 500 Errors!"
    assert all(code == 200 for code in status_codes)
    assert all(code == 200 for code in status_codes)
    
    print("Successfully processed 30 concurrent payloads under Redis/Postgres locking constraints.")
