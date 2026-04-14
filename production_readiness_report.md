# Production Readiness Report

Generated at: 2026-04-11T13:46:01.799407+00:00
Host OS: Windows-11-10.0.26200-SP0

## Summary

- Local production gate: PASS
- External live staging: not executed by this script

## Gate Results

| Check | Status | Duration (s) | Exit code |
| --- | --- | ---: | ---: |
| Backend mascot routes | Pass | 457.25 | 0 |
| Backend mascot WhatsApp adapter | Pass | 2.65 | 0 |
| Backend alerting | Pass | 2.24 | 0 |
| OCR benchmark gate | Pass | 1.9 | 0 |
| Grounding suite | Pass | 2.14 | 0 |
| Backend compile | Pass | 0.15 | 0 |
| Frontend build | Pass | 20.23 | 0 |

## Detailed Output

### Backend mascot routes

- command: `C:\Python314\python.exe -m pytest -q -p no:cacheprovider backend/tests/test_mascot_routes.py`
- workdir: `C:\Users\naren\Work\Projects\proxy_notebooklm`
- status: `Pass`
- duration_seconds: `457.25`

```text
...........................................                              [100%]
============================== warnings summary ===============================
backend/tests/test_mascot_routes.py::test_mascot_creates_notebook_and_returns_ai_studio_navigation
  C:\Users\naren\Work\Projects\proxy_notebooklm\backend\src\domains\academic\routes\parent.py:62: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class NotificationPreferencesResponse(BaseModel):

backend/tests/test_mascot_routes.py::test_mascot_creates_notebook_and_returns_ai_studio_navigation
  C:\Users\naren\Work\Projects\proxy_notebooklm\backend\src\interfaces\rest_api\ai\routes\session_tracking.py:24: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class AISessionEventCreate(BaseModel):

backend/tests/test_mascot_routes.py::test_mascot_creates_notebook_and_returns_ai_studio_navigation
  C:\Users\naren\AppData\Roaming\Python\Python314\site-packages\pydantic\_internal\_config.py:383: UserWarning: Valid config keys have changed in V2:
  * 'schema_extra' has been renamed to 'json_schema_extra'
    warnings.warn(message, UserWarning)

backend/tests/test_mascot_routes.py::test_mascot_creates_notebook_and_returns_ai_studio_navigation
  C:\Users\naren\Work\Projects\proxy_notebooklm\backend\src\interfaces\rest_api\ai\routes\session_tracking.py:77: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class AISessionEventResponse(BaseModel):

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
43 passed, 4 warnings in 451.75s (0:07:31)
```

### Backend mascot WhatsApp adapter

- command: `C:\Python314\python.exe -m pytest -q -p no:cacheprovider backend/tests/test_mascot_whatsapp_adapter.py`
- workdir: `C:\Users\naren\Work\Projects\proxy_notebooklm`
- status: `Pass`
- duration_seconds: `2.65`

```text
.....                                                                    [100%]
5 passed in 0.91s
```

### Backend alerting

- command: `C:\Python314\python.exe -m pytest -q -p no:cacheprovider backend/tests/test_alerting.py`
- workdir: `C:\Users\naren\Work\Projects\proxy_notebooklm`
- status: `Pass`
- duration_seconds: `2.24`

```text
.............                                                            [100%]
13 passed in 0.68s
```

### OCR benchmark gate

- command: `C:\Python314\python.exe -m pytest -q -p no:cacheprovider backend/tests/evaluation/test_ocr_benchmark.py`
- workdir: `C:\Users\naren\Work\Projects\proxy_notebooklm`
- status: `Pass`
- duration_seconds: `1.9`

```text
............                                                             [100%]
12 passed in 0.48s
```

### Grounding suite

- command: `C:\Python314\python.exe -m pytest -q -p no:cacheprovider backend/tests/evaluation/test_textbook_feature_grounding.py`
- workdir: `C:\Users\naren\Work\Projects\proxy_notebooklm`
- status: `Pass`
- duration_seconds: `2.14`

```text
.....................                                                    [100%]
21 passed in 0.64s
```

### Backend compile

- command: `C:\Python314\python.exe -m py_compile backend/src/domains/platform/routes/mascot.py backend/src/domains/platform/routes/whatsapp.py backend/src/domains/platform/services/mascot_orchestrator.py backend/src/domains/platform/services/alerting.py backend/config.py`
- workdir: `C:\Users\naren\Work\Projects\proxy_notebooklm`
- status: `Pass`
- duration_seconds: `0.15`

```text
(no output)
```

### Frontend build

- command: `npm.cmd run build`
- workdir: `C:\Users\naren\Work\Projects\proxy_notebooklm\frontend`
- status: `Pass`
- duration_seconds: `20.23`

```text
> frontend@0.1.0 prebuild
> npm run typecheck


> frontend@0.1.0 typecheck
> tsc --noEmit -p tsconfig.json


> frontend@0.1.0 build
> next build

â–² Next.js 16.1.6 (Turbopack)
- Environments: .env.local

  Creating an optimized production build ...
âœ“ Compiled successfully in 9.5s
  Skipping validation of types
  Collecting page data using 27 workers ...
  Generating static pages using 27 workers (0/68) ...
  Generating static pages using 27 workers (17/68) 
  Generating static pages using 27 workers (34/68) 
  Generating static pages using 27 workers (51/68) 
âœ“ Generating static pages using 27 workers (68/68) in 673.9ms
  Finalizing page optimization ...

Route (app)
â”Œ Æ’ /
â”œ Æ’ /_not-found
â”œ Æ’ /admin/ai-review
â”œ Æ’ /admin/ai-usage
â”œ Æ’ /admin/assistant
â”œ Æ’ /admin/billing
â”œ Æ’ /admin/branding
â”œ Æ’ /admin/classes
â”œ Æ’ /admin/complaints
â”œ Æ’ /admin/dashboard
â”œ Æ’ /admin/enterprise/compliance
â”œ Æ’ /admin/enterprise/incidents
â”œ Æ’ /admin/enterprise/sso
â”œ Æ’ /admin/feature-flags
â”œ Æ’ /admin/qr-cards
â”œ Æ’ /admin/queue
â”œ Æ’ /admin/reports
â”œ Æ’ /admin/security
â”œ Æ’ /admin/settings
â”œ Æ’ /admin/setup-wizard
â”œ Æ’ /admin/timetable
â”œ Æ’ /admin/traces
â”œ Æ’ /admin/users
â”œ Æ’ /admin/webhooks
â”œ Æ’ /demo
â”œ Æ’ /login
â”œ Æ’ /parent
â”œ Æ’ /parent/assistant
â”œ Æ’ /parent/attendance
â”œ Æ’ /parent/dashboard
â”œ Æ’ /parent/reports
â”œ Æ’ /parent/results
â”œ Æ’ /parent/settings
â”œ Æ’ /qr-login
â”œ Æ’ /student/ai
â”œ Æ’ /student/ai-library
â”œ Æ’ /student/ai-studio
â”œ Æ’ /student/assignments
â”œ Æ’ /student/assistant
â”œ Æ’ /student/attendance
â”œ Æ’ /student/audio-overview
â”œ Æ’ /student/complaints
â”œ Æ’ /student/leaderboard
â”œ Æ’ /student/lectures
â”œ Æ’ /student/mastery
â”œ Æ’ /student/mind-map
â”œ Æ’ /student/overview
â”œ Æ’ /student/profile
â”œ Æ’ /student/results
â”œ Æ’ /student/reviews
â”œ Æ’ /student/timetable
â”œ Æ’ /student/tools
â”œ Æ’ /student/upload
â”œ Æ’ /student/video-overview
â”œ Æ’ /teacher/assignments
â”œ Æ’ /teacher/assistant
â”œ Æ’ /teacher/attendance
â”œ Æ’ /teacher/classes
â”œ Æ’ /teacher/dashboard
â”œ Æ’ /teacher/discover
â”œ Æ’ /teacher/doubt-heatmap
â”œ Æ’ /teacher/generate-assessment
â”œ Æ’ /teacher/insights
â”œ Æ’ /teacher/marks
â”œ Æ’ /teacher/profile
â”” Æ’ /teacher/upload


Æ’  (Dynamic)  server-rendered on demand
Failed to fetch /api/parent/dashboard for parent dashboard page Error: Dynamic server usage: Route /parent/dashboard couldn't be rendered statically because it used `cookies`. See more info here: https://nextjs.org/docs/messages/dynamic-server-error
    at n (C:\Users\naren\Work\Projects\proxy_notebooklm\frontend\.next\server\chunks\ssr\_c9c1bb49._.js:1:12749)
    at e (C:\Users\naren\Work\Projects\proxy_notebooklm\frontend\.next\server\chunks\ssr\_c9c1bb49._.js:1:24363)
    at f (C:\Users\naren\Work\Projects\proxy_notebooklm\frontend\.next\server\chunks\ssr\_c9c1bb49._.js:1:24518)
    at e (C:\Users\naren\Work\Projects\proxy_notebooklm\frontend\.next\server\chunks\ssr\[root-of-the-server]__cefe88d5._.js:1:1491)
    at stringify (<anonymous>) {
  description: "Route /parent/dashboard couldn't be rendered statically because it used `cookies`. See more info here: https://nextjs.org/docs/messages/dynamic-server-error",
  digest: 'DYNAMIC_SERVER_USAGE'
}
Failed to fetch /api/admin/dashboard-bootstrap for admin dashboard page Error: Dynamic server usage: Route /admin/dashboard couldn't be rendered statically because it used `cookies`. See more info here: https://nextjs.org/docs/messages/dynamic-server-error
    at n (C:\Users\naren\Work\Projects\proxy_notebooklm\frontend\.next\server\chunks\ssr\_c9c1bb49._.js:1:12749)
    at e (C:\Users\naren\Work\Projects\proxy_notebooklm\frontend\.next\server\chunks\ssr\_c9c1bb49._.js:1:24363)
    at f (C:\Users\naren\Work\Projects\proxy_notebooklm\frontend\.next\server\chunks\ssr\_c9c1bb49._.js:1:24518)
    at e (C:\Users\naren\Work\Projects\proxy_notebooklm\frontend\.next\server\chunks\ssr\[root-of-the-server]__81
...[truncated]
```

## External Work Still Required

- live WhatsApp/device staging pass
- evidence capture and sign-off
- any staging-only fixes found during the live run

Primary docs:

- `documentation/mascot_whatsapp_staging_manual_test_script.md`
- `documentation/mascot_whatsapp_staging_evidence_template.md`
- `documentation/mascot_release_gate.md`

---

## Related
- [[INDEX]] — Knowledge hub
- [[PRODUCTION_READINESS_REPORTS_INDEX]] — Reports overview
- [[EXECUTIVE_BRIEFING]] — Executive summary
- [[CI_TEST_EXECUTION_REPORT]] — CI/lint results
- [[TEST_EXECUTION_SUMMARY_COMPLETE]] — Full test results
- [[OPERATIONS_MONITORING_GUIDE]]
