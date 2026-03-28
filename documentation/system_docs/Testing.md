# Testing Guide

**Project:** VidyaOS  
**Status:** Updated on 2026-03-28  
**Test Frameworks:** pytest, pytest-asyncio, Playwright

---

## 1. Important Note About Counts

Older docs in this repo used hardcoded "passing test" totals that drifted over time.

Current static inventory in the repository:
- backend: 53 `test_*.py` files under `backend/tests`
- frontend: 3 Playwright specs under `frontend/tests/e2e`

Treat those as file inventory only, not proof that the suite is passing on your machine.

## 2. Quick Start

### Backend

```bash
cd backend
python -m pytest tests/ -q
python -m pytest tests/ -v
python -m pytest tests/ -x
python -m pytest tests/test_constants.py
```

### Frontend

```bash
cd frontend
npm run build
npm run test:e2e
```

## 3. Dependencies

Backend test dependencies commonly required:

```bash
pip install pytest pytest-asyncio httpx "bcrypt<5"
pip install fastapi sqlalchemy pydantic pydantic-settings
pip install python-jose python-multipart redis pyyaml
pip install google-auth passlib python-dotenv numpy
```

Frontend test dependencies come from `frontend/package.json` and are installed with:

```bash
cd frontend
npm install
```

## 4. Current Backend Coverage Areas

The backend test suite covers areas including:
- auth and security
- CSRF and tenant middleware
- AI queue and queue resiliency
- file uploads and upload security
- constants and grading helpers
- WhatsApp flows
- webhooks
- leaderboard and gamification
- compliance and incident management
- OpenAI-compatible API
- knowledge graph
- HyDE
- connectors
- token blacklist
- citations
- doc watcher
- agent orchestrator
- captcha
- plugin registry
- library
- invitations
- docs chatbot

## 5. Test Infrastructure

Common backend test setup:
- SQLite in-memory database for isolation
- per-test transaction rollback
- FastAPI `TestClient` fixture
- seeded tenant/user fixtures through `conftest.py`

Typical backend test environment:

```env
DEBUG=true
DEMO_MODE=false
DATABASE_URL=sqlite:///:memory:
TESTING=true
```

## 6. Lightweight Backend Test Mode

In minimal environments where optional dependencies are unavailable, the backend pytest harness can fall back to lightweight collection mode.

You can control this explicitly with `LIGHTWEIGHT_TEST_MODE`:

```bash
pytest -q backend/tests
LIGHTWEIGHT_TEST_MODE=on pytest -q backend/tests
./scripts/run_backend_tests_lightweight.sh -q
LIGHTWEIGHT_TEST_MODE=off pytest -q backend/tests
```

## 7. Frontend Coverage Reality

Current frontend automated coverage is much thinner than backend coverage.

Tracked frontend specs:
- `frontend/tests/e2e/admin-dashboard.spec.ts`
- `frontend/tests/e2e/admin-queue.spec.ts`
- `frontend/tests/e2e/smoke.spec.ts`

If you change admin UI, notebook UI, or enterprise UI flows, add tests rather than relying on the current small Playwright surface.

## 8. Adding New Tests

1. Create `backend/tests/test_<module>.py` for backend work.
2. Use `client` fixtures for HTTP tests and `db_session` for DB-facing tests.
3. For async functions, use `@pytest.mark.asyncio`.
4. Mock external services such as Redis, Ollama, and remote HTTP integrations.
5. For frontend behavior, add Playwright coverage under `frontend/tests/e2e`.

## 9. Documentation Rule

Do not update this file with "all tests passing" claims unless the suite was actually executed in the same environment and the exact command/result are recorded alongside the update.
