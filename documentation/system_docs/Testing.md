# Testing Guide

**Project:** VidyaOS  
**Status:** Updated on 2026-03-12  
**Test Framework:** pytest + pytest-asyncio  
**Total Tests:** 382 across 48 files

---

## Quick Start

```bash
cd backend
python -m pytest tests/ -q         # Quick run
python -m pytest tests/ -v         # Verbose run
python -m pytest tests/ -x         # Stop on first failure
python -m pytest tests/test_constants.py  # Run specific file
```

## Dependencies

```bash
pip install pytest pytest-asyncio httpx "bcrypt<5"
pip install fastapi sqlalchemy pydantic pydantic-settings
pip install python-jose python-multipart redis pyyaml
pip install google-auth passlib python-dotenv numpy
```

> **Note:** bcrypt must be < 5.0 for passlib compatibility. Python 3.14+ requires latest unpinned packages.

---

## Test File Map

### Security & Auth (3 files)

| File | Tests | Coverage |
|------|-------|----------|
| `test_auth_security.py` | 3 | JWT none-algorithm rejection, RBAC student→admin boundary, rate limit enforcement |
| `test_csrf_middleware.py` | — | CSRF origin/referer validation |
| `test_security_regressions.py` | 60+ | Comprehensive security regression tests: tenant isolation, IDOR, role boundaries |

### Core Services (5 files)

| File | Tests | Coverage |
|------|-------|----------|
| `test_constants.py` | 30 | Grading logic (every boundary), emoji/color helpers, type checks, constant integrity |
| `test_whatsapp.py` | 12 | Message sending, attendance alerts, weekly digest, exam results with emoji selection |
| `test_leaderboard.py` | 7 | Ranking calculation, zero division, default limits, missing series, student rank |
| `test_webhooks.py` | 2 | No subscriptions, delivery creation |
| `test_weakness_alerts.py` | — | Weakness detection thresholds |

### Enterprise (2 files)

| File | Tests | Coverage |
|------|-------|----------|
| `test_compliance.py` | 3 | Export listing, deletion requests, 404 handling |
| `test_incident_management.py` | 4 | Incident listing, routes, detail retrieval, resolution |

### Middleware & Infrastructure (4 files)

| File | Tests | Coverage |
|------|-------|----------|
| `test_rate_limit.py` | 4 | Constant verification, non-AI path bypass, burst enforcement |
| `test_tenant_middleware.py` | — | Multi-tenant isolation in middleware |
| `test_upload_security.py` | 5 | DOCX macro stripping, content type rewriting, non-zip handling |
| `test_infra_utils.py` | 6 | Structured logging, startup checks, pagination edge cases |

### AI & Queue (4 files)

| File | Tests | Coverage |
|------|-------|----------|
| `test_ai_queue.py` | — | AI job queue lifecycle |
| `test_queue_resiliency.py` | — | Paused queue behavior |
| `test_normalize_tool_output.py` | — | AI tool output normalization |
| `test_runtime_ops.py` | — | Worker runtime operations |

### Routes & Features (5 files)

| File | Tests | Coverage |
|------|-------|----------|
| `test_file_uploads.py` | 2 | CSV upload validation (empty, binary) |
| `test_enterprise_routes.py` | — | Enterprise API route tests |
| `test_gamification.py` | — | XP and streak mechanics |
| `test_notifications.py` | — | Notification dispatch |
| `test_report_card.py` | 3 | Grading integration, imports from constants, PDF color constants |

### Configuration (1 file)

| File | Tests | Coverage |
|------|-------|----------|
| `test_config_validation.py` | — | Settings parsing, CORS origins |
| `test_sm2_algorithm.py` | — | Spaced repetition algorithm |

### Gap Implementations — Medium Priority (7 files)

| File | Tests | Coverage |
|------|-------|----------|
| `test_fee_management.py` | 9 | Fee constants, model instantiation, payment status transitions, report structure |
| `test_openai_compat.py` | 11 | Constants, provider registry (list/get/unknown), Ollama format conversion, custom providers |
| `test_knowledge_graph.py` | 6 | Relation types, model instantiation, invalid type handling, traversal, context structure |
| `test_hyde.py` | 12 | Short query passthrough, complex/compare/explain detection, multi-clause, hypothetical generation |
| `test_connectors.py` | 8 | Extended file types, registry, get_connector (known/unknown), PPTX missing file, output format |
| `test_token_blacklist.py` | 6 | Model fields, cache type, JTI in refresh tokens, function existence |
| `test_citations.py` | 10 | Citation parsing, URL generation, format validation, enrichment pipeline |

### Gap Implementations — Final Batch (7 files)

| File | Tests | Coverage |
|------|-------|----------|
| `test_doc_watcher.py` | 7 | Supported extensions, file hashing, scan (empty/found/skip), mark-processed dedup, status |
| `test_agent_orchestrator.py` | 10 | Workflow templates, step count, start/advance/complete, unknown workflow, list, state |
| `test_captcha.py` | 6 | Protected endpoints, non-protected, human detection (success/low/failed), threshold default |
| `test_plugin_registry.py` | 9 | Hook names, meta creation, register/list, enable/disable, hook execution (normal/error) |
| `test_library.py` | 7 | Lending config, model instantiation, categories, status pipeline, stats structure |
| `test_team_invite.py` | 9 | Expiry config, create, validate (valid/nonexistent), accept (normal/double), revoke, list |
| `test_docs_chatbot.py` | 8 | FAQ database, search (match/no-match), categories, FAQs by category, support response |

---

## Test Infrastructure

### `conftest.py`

- SQLite in-memory database for isolation
- Per-test transaction rollback (no test pollution)
- `client` fixture: FastAPI `TestClient` with DB override
- `active_tenant` fixture: pre-created `Tenant` record

### Environment

Tests run with:
```env
DEBUG=true
DEMO_MODE=false
DATABASE_URL=sqlite:///:memory:
TESTING=true
```

---

## Adding New Tests

1. Create `tests/test_<module>.py`
2. Use `client` fixture for HTTP tests, `db_session` fixture for DB tests
3. For async functions, use `@pytest.mark.asyncio`
4. Mock external services (Redis, httpx, Ollama) — don't hit real endpoints
5. Run `python -m pytest tests/test_<module>.py -v` to verify
