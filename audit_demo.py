"""Full feature audit."""
import urllib.request, json

BASE_API = "http://localhost:8080"
BASE_FE = "http://localhost:7125"

def get_token(role="student"):
    req = urllib.request.Request(f"{BASE_API}/api/auth/demo-login",
        data=json.dumps({"role": role}).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    return json.loads(urllib.request.urlopen(req).read().decode())["access_token"]

def check_api(path, token=None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        resp = urllib.request.urlopen(urllib.request.Request(f"{BASE_API}{path}", headers=headers))
        return f"OK {resp.status}"
    except urllib.error.HTTPError as e:
        return f"FAIL {e.code}"
    except Exception as e:
        return f"ERR"

def check_page(path):
    try:
        resp = urllib.request.urlopen(f"{BASE_FE}{path}")
        return f"OK {resp.status}"
    except urllib.error.HTTPError as e:
        return f"FAIL {e.code}"
    except Exception as e:
        return f"ERR"

st = get_token("student")
tt = get_token("teacher")
at = get_token("admin")

print("=== BACKEND APIs ===")
apis = [
    ("Auth me", "/api/auth/me", st),
    ("Student dashboard", "/api/student/dashboard", st),
    ("Student attendance", "/api/student/attendance", st),
    ("Student subjects", "/api/student/subjects", st),
    ("Student assignments", "/api/student/assignments", st),
    ("Student results", "/api/student/results", st),
    ("Student timetable", "/api/student/timetable", st),
    ("Student notebooks", "/api/student/notebooks", st),
    ("AI history", "/api/ai/history", st),
    ("Documents", "/api/documents", st),
    ("Notebooks", "/api/notebooks", st),
    ("Teacher dashboard", "/api/teacher/dashboard", tt),
    ("Teacher classes", "/api/teacher/classes", tt),
    ("Admin dashboard", "/api/admin/dashboard", at),
    ("Admin users", "/api/admin/users", at),
    ("Demo profiles", "/api/demo/profiles", None),
    ("Demo status", "/api/demo/status", None),
]
ok = fail = 0
for label, path, tok in apis:
    r = check_api(path, tok)
    s = "+" if r.startswith("OK") else "-"
    print(f"  [{s}] {r:12s} {label}")
    if s == "+": ok += 1
    else: fail += 1

print(f"\n  API: {ok} ok, {fail} fail")

print("\n=== FRONTEND PAGES ===")
pages = ["/","/demo","/login",
    "/student/overview","/student/attendance","/student/assignments",
    "/student/results","/student/timetable","/student/ai-studio",
    "/student/ai","/student/ai-library","/student/upload",
    "/student/profile","/student/leaderboard","/student/assistant",
    "/student/tools","/student/mind-map","/student/lectures",
    "/teacher/dashboard","/teacher/classes","/teacher/assignments",
    "/teacher/attendance","/teacher/marks","/teacher/upload",
    "/teacher/insights","/teacher/assistant",
    "/admin/dashboard","/admin/users","/admin/classes",
    "/admin/timetable","/admin/ai-usage","/admin/settings",
    "/admin/feature-flags","/admin/reports","/admin/billing",
    "/admin/assistant",
    "/parent/dashboard","/parent/attendance","/parent/results",
    "/parent/assistant",
]
ok2 = fail2 = 0
for p in pages:
    r = check_page(p)
    s = "+" if r.startswith("OK") else "-"
    print(f"  [{s}] {r:12s} {p}")
    if s == "+": ok2 += 1
    else: fail2 += 1

print(f"\n  Pages: {ok2} ok, {fail2} fail")
print(f"\n  TOTAL: {ok+ok2} ok, {fail+fail2} fail")
