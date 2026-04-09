# Production Readiness Report

Generated at: 2026-04-09T05:53:34.351911+00:00
Host OS: Windows-11-10.0.26200-SP0

## Summary

- Local production gate: FAIL
- External live staging: not executed by this script

## Gate Results

| Check | Status | Duration (s) | Exit code |
| --- | --- | ---: | ---: |
| Backend mascot routes | Pass | 464.37 | 0 |
| Backend mascot WhatsApp adapter | Pass | 4.6 | 0 |
| Backend alerting | Pass | 3.82 | 0 |
| OCR benchmark gate | Pass | 3.18 | 0 |
| Grounding suite | Pass | 3.5 | 0 |
| Backend compile | Pass | 0.22 | 0 |
| Frontend build | Fail | 20.2 | 1 |

## Detailed Output

### Backend mascot routes

- command: `C:\Python314\python.exe -m pytest -q -p no:cacheprovider backend/tests/test_mascot_routes.py`
- workdir: `C:\Users\naren\Work\Projects\proxy_notebooklm`
- status: `Pass`
- duration_seconds: `464.37`

```text
...........................................                              [100%]
43 passed in 459.03s (0:07:39)
```

### Backend mascot WhatsApp adapter

- command: `C:\Python314\python.exe -m pytest -q -p no:cacheprovider backend/tests/test_mascot_whatsapp_adapter.py`
- workdir: `C:\Users\naren\Work\Projects\proxy_notebooklm`
- status: `Pass`
- duration_seconds: `4.6`

```text
.....                                                                    [100%]
5 passed in 1.67s
```

### Backend alerting

- command: `C:\Python314\python.exe -m pytest -q -p no:cacheprovider backend/tests/test_alerting.py`
- workdir: `C:\Users\naren\Work\Projects\proxy_notebooklm`
- status: `Pass`
- duration_seconds: `3.82`

```text
.............                                                            [100%]
13 passed in 1.24s
```

### OCR benchmark gate

- command: `C:\Python314\python.exe -m pytest -q -p no:cacheprovider backend/tests/evaluation/test_ocr_benchmark.py`
- workdir: `C:\Users\naren\Work\Projects\proxy_notebooklm`
- status: `Pass`
- duration_seconds: `3.18`

```text
............                                                             [100%]
12 passed in 0.73s
```

### Grounding suite

- command: `C:\Python314\python.exe -m pytest -q -p no:cacheprovider backend/tests/evaluation/test_textbook_feature_grounding.py`
- workdir: `C:\Users\naren\Work\Projects\proxy_notebooklm`
- status: `Pass`
- duration_seconds: `3.5`

```text
.....................                                                    [100%]
21 passed in 1.15s
```

### Backend compile

- command: `C:\Python314\python.exe -m py_compile backend/src/domains/platform/routes/mascot.py backend/src/domains/platform/routes/whatsapp.py backend/src/domains/platform/services/mascot_orchestrator.py backend/src/domains/platform/services/alerting.py backend/config.py`
- workdir: `C:\Users\naren\Work\Projects\proxy_notebooklm`
- status: `Pass`
- duration_seconds: `0.22`

```text
(no output)
```

### Frontend build

- command: `npm.cmd run build`
- workdir: `C:\Users\naren\Work\Projects\proxy_notebooklm\frontend`
- status: `Fail`
- duration_seconds: `20.2`

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
âœ“ Compiled successfully in 11.7s
  Skipping validation of types
> Build error occurred
Error: local environment blocked completion of the build process after compile.
```

## External Work Still Required

- live WhatsApp/device staging pass
- evidence capture and sign-off
- any staging-only fixes found during the live run

Primary docs:

- `documentation/mascot_whatsapp_staging_manual_test_script.md`
- `documentation/mascot_whatsapp_staging_evidence_template.md`
- `documentation/mascot_release_gate.md`
