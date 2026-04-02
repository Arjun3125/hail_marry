"""Test every endpoint the student overview page calls."""
import urllib.request
import json
import sys

# Login
req = urllib.request.Request(
    "http://localhost:8080/api/auth/demo-login",
    data=json.dumps({"role": "student"}).encode(),
    headers={"Content-Type": "application/json"},
    method="POST",
)
resp = urllib.request.urlopen(req, timeout=10)
token = json.loads(resp.read())["access_token"]
h = {"Authorization": f"Bearer {token}"}

# These are the EXACT 5 endpoints called in Promise.all on the overview page
tests = [
    ("api.student.dashboard()", "/api/student/dashboard"),
    ("api.student.weakTopics()", "/api/student/weak-topics"),
    ("api.student.streaks()", "/api/student/streaks"),
    ("api.personalization.recommendations()", "/api/personalization/recommendations?current_surface=overview"),
    ("api.personalization.studyPath()", "/api/personalization/study-path?current_surface=overview"),
]

for name, ep in tests:
    try:
        req = urllib.request.Request(f"http://localhost:8080{ep}", headers=h)
        resp = urllib.request.urlopen(req, timeout=15)
        data = resp.read().decode()
        print(f"✅ {name}: {resp.status} ({len(data)} bytes)")
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:300]
        print(f"❌ {name}: HTTP {e.code}")
        print(f"   Response: {body}")
    except Exception as e:
        print(f"❌ {name}: {type(e).__name__}: {e}")
