"""Quick end-to-end RAG verification."""
import httpx, json, base64

BASE = "http://localhost:7125"

# 1. Login
print("1. Demo login...")
r = httpx.post(f"{BASE}/api/auth/demo-login", json={"role": "student"})
assert r.status_code == 200, f"Login failed: {r.status_code}"
token = r.json()["access_token"]
print(f"   ✅ Got token")

# Decode JWT to see tenant_id
payload_b64 = token.split(".")[1] + "=="
payload = json.loads(base64.b64decode(payload_b64))
print(f"   email:     {payload.get('email')}")
print(f"   tenant_id: {payload.get('tenant_id')}")
print(f"   role:      {payload.get('role')}")

headers = {"Authorization": f"Bearer {token}"}

# 2. Test AI history
print("\n2. AI History...")
r2 = httpx.get(f"{BASE}/api/student/ai-history", headers=headers, timeout=10)
print(f"   Status: {r2.status_code}")
if r2.status_code == 200:
    data = r2.json()
    items = data.get("items", data.get("queries", []))
    print(f"   ✅ Found {len(items)} history items")
else:
    print(f"   Response: {r2.text[:300]}")

# 3. Test notebooks
print("\n3. Notebooks...")
r3 = httpx.get(f"{BASE}/api/notebooks", headers=headers, timeout=10)
print(f"   Status: {r3.status_code}")
if r3.status_code == 200:
    nbs = r3.json()
    if isinstance(nbs, list):
        print(f"   ✅ Found {len(nbs)} notebooks")
        for nb in nbs[:4]:
            print(f"      - {nb.get('name', '?')} ({nb.get('subject', '?')})")
    elif isinstance(nbs, dict):
        items = nbs.get("notebooks", nbs.get("items", []))
        print(f"   ✅ Found {len(items)} notebooks")
else:
    print(f"   Response: {r3.text[:300]}")

# 4. Test mascot RAG
print("\n4. Mascot RAG query...")
r4 = httpx.post(
    f"{BASE}/api/mascot/message",
    headers=headers,
    json={"message": "What is the difference between displacement and distance?"},
    timeout=60,
)
print(f"   Status: {r4.status_code}")
if r4.status_code == 200:
    data = r4.json()
    reply = data.get("reply", data.get("response", data.get("message", "")))
    print(f"   ✅ RAG Response ({len(reply)} chars):")
    print(f"   {reply[:400]}...")
else:
    print(f"   ❌ Error: {r4.text[:500]}")

print("\n=== DONE ===")
