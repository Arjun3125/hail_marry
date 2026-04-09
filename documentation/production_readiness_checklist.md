# Production Readiness Checklist

This document describes how to decide whether the current codebase is ready for CI, staging, and production deployment.

It is based on the actual workflows in:

- `.github/workflows/ci.yml`
- `.github/workflows/production-readiness.yml`
- `scripts/production_readiness_gate.py`

## Goal

A build is production-ready only when:

- backend tests are green
- frontend lint, TypeScript, and build are green
- smoke E2E passes
- container smoke passes
- no known blocking regressions remain
- manual staging-only checks are signed off where required

## 1. Backend Readiness

Run from repo root:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest backend/tests -q -p no:cacheprovider
```

Pass criteria:

- all backend tests pass
- no unexpected skips on critical flows

Optional static checks that match CI intent:

```powershell
cd backend
ruff check .
mypy --ignore-missing-imports .
cd ..
python scripts/check_architecture.py
```

## 2. Frontend Readiness

Run from `frontend`:

```powershell
npm.cmd run lint
npx.cmd tsc --noEmit -p tsconfig.json
npm.cmd run build
```

Pass criteria:

- eslint passes
- TypeScript passes
- production build completes

Notes:

- `npm run build` is the real production gate
- if `tsc` fails, treat that as a release blocker even if the app seems to run locally

## 3. Playwright Coverage

List tests:

```powershell
cd frontend
node_modules\.bin\playwright.cmd test --list
cd ..
```

Run smoke suite:

```powershell
cd frontend
npm.cmd run test:e2e:smoke
cd ..
```

Run full suite when preparing main/staging release:

```powershell
cd frontend
npm.cmd run test:e2e:full
cd ..
```

Pass criteria:

- smoke suite must pass for every release candidate
- full suite should pass before main-branch production promotion

## 4. Production Readiness Gate

Dry-run the gate:

```powershell
python scripts\production_readiness_gate.py --dry-run
```

Run the gate:

```powershell
python scripts\production_readiness_gate.py --output production_readiness_report.md
```

Pass criteria:

- report summary says `PASS`
- no failed section in the markdown output

This gate currently checks:

- mascot routes
- WhatsApp adapter
- alerting
- OCR benchmark
- grounding suite
- backend compile
- frontend build

## 5. Docker / Runtime Smoke

These are validated in CI and should be checked before production promotion:

- backend container builds successfully
- backend `/health` endpoint responds successfully
- environment variables are set for the target environment

Relevant workflow:

- `.github/workflows/ci.yml`

## 6. Manual Staging Sign-Off

Automated checks are not enough for final production readiness.

Manual staging checks still required:

- WhatsApp/device staging pass
- evidence capture
- release sign-off

Reference docs:

- `documentation/mascot_whatsapp_staging_manual_test_script.md`
- `documentation/mascot_whatsapp_staging_evidence_template.md`
- `documentation/mascot_release_gate.md`

## 7. Release Decision Rules

Release status should be:

- `READY`
  - backend tests pass
  - frontend lint/type/build pass
  - smoke E2E passes
  - no known blocking bugs

- `CONDITIONALLY READY`
  - core automated checks pass
  - only non-blocking environment-specific issues remain
  - manual staging sign-off still pending

- `NOT READY`
  - any backend test fails
  - any TypeScript/build failure exists
  - smoke E2E fails
  - known functional regression exists in a production path

## 8. Practical Release Sequence

Recommended order:

1. Run backend pytest suite.
2. Run frontend lint, TypeScript, and build.
3. Run Playwright smoke.
4. Run `production_readiness_gate.py`.
5. Review `production_readiness_report.md`.
6. Execute manual staging checks.
7. Promote only after all blockers are cleared.

## 9. Current Interpretation Rule

If you want a single quick answer, use this:

- if backend pytest is not fully green, do not release
- if frontend TypeScript or build is not green, do not release
- if smoke E2E is not green, do not release

