# Tech Stack

**Project:** VidyaOS  
**Version:** v0.1 current implementation  
**Status:** Updated to match the repository on 2026-04-12

---

## 1. Frontend Stack

| Layer | Technology in Repo |
|---|---|
| Framework | Next.js 16 |
| UI runtime | React 19 |
| Language | TypeScript |
| Styling | Tailwind CSS 4 |
| Icons | lucide-react |
| Routing | Next.js App Router |
| E2E testing | Playwright |

## 2. Backend Stack

| Layer | Technology in Repo |
|---|---|
| API framework | FastAPI |
| Worker runtime | Python process using Redis-backed queue services |
| Language | Python 3.11+ |
| ORM | SQLAlchemy |
| Validation | Pydantic |
| Migrations | Alembic |
| Auth | Google OAuth, email/password, JWT, SAML configuration APIs |
| Queue/cache support | Redis |

### Middleware Stack

| Middleware | Purpose |
|---|---|
| `ObservabilityMiddleware` | Structured logging and request metrics |
| `CORSMiddleware` | Cross-origin request control |
| `CSRFMiddleware` | CSRF protection when enabled |
| `TenantMiddleware` | Tenant context injection from JWT |
| `RateLimitMiddleware` | Request throttling when enabled |
| `CaptchaMiddleware` | Public-endpoint bot protection when configured |

## 3. AI Stack

| Capability | Current Implementation |
|---|---|
| Public synchronous execution boundary | `backend/src/interfaces/rest_api/ai/routes/ai.py` -> `backend/src/domains/platform/services/ai_gateway.py` -> `backend/src/interfaces/rest_api/ai/workflows.py` |
| Queued execution boundary | `backend/ai_worker.py` -> `backend/src/domains/platform/services/ai_queue.py` -> same internal gateway/workflow layer |
| LLM runner | Ollama over HTTP |
| Default model | Config-driven, default local path targets Ollama |
| Embeddings | `nomic-embed-text` through the internal embedding layer |
| Vector store | FAISS by default |
| Optional vector backend | Qdrant |
| Reranking | cross-encoder reranking when dependencies are available |
| Agent orchestration | LangGraph-based workflow helper in `agent_orchestrator.py` |
| OpenAI compatibility | `/v1/*` routes with separate provider registry |
| Source discovery | DuckDuckGo HTML search |
| Spaced repetition | SM-2 algorithm |
| Brand color extraction | `colorthief` plus WCAG contrast logic |

Important current reality:
- the repo does not contain a dedicated FastAPI AI service
- `AI_SERVICE_URL` settings exist, but they are not the active execution path for core AI requests

## 4. Infrastructure and Local Deployment

| Layer | Current Implementation |
|---|---|
| Local container orchestration | Docker Compose |
| Reverse proxy | Nginx |
| Database | PostgreSQL 15+ |
| Queue/cache | Redis 7 |
| Frontend container | `frontend/Dockerfile` |
| API container | `backend/Dockerfile` |
| Worker container | `backend/Dockerfile.worker` |

Current compose stack:
- `postgres`
- `redis`
- `api`
- `worker`
- `frontend`
- `nginx`

Optional profiles:
- observability
- vector (`qdrant`)

External dependency:
- Ollama reachable over HTTP

## 5. Observability Stack

| Capability | Current Implementation |
|---|---|
| Structured logs | JSON logs written by app services |
| Metrics export | Prometheus-style `/metrics` endpoints |
| Tracing | OpenTelemetry hooks plus Tempo profile |
| Log aggregation | Loki plus Promtail |
| Dashboarding | Grafana |
| Error tracking | Sentry integration in backend services |
| GPU monitoring | DCGM exporter |
| Alert rules | Prometheus rule file in `ops/observability/alert_rules.yml` |

## 6. Testing and Verification

Current static inventory in the repository:
- backend: 53 `test_*.py` files under `backend/tests`
- frontend: 3 Playwright specs under `frontend/tests/e2e`

Do not treat static inventory as pass/fail status. Run:
- `cd backend && python -m pytest tests/ -q`
- `cd frontend && npm run build`
- `cd frontend && npm run test:e2e`

## 7. Code Quality Notes

| Layer | Implementation |
|---|---|
| Backend constants | `backend/constants.py` centralizes thresholds, file limits, and helpers |
| Frontend design tokens | `frontend/src/app/globals.css` carries semantic CSS variables and utility tokens |
| Upload security | `backend/utils/upload_security.py` strips DOCX macros and validates storage paths |

## 8. Current Caveats

- Feature-flag and branding routes exist, but frontend/backend route prefixes are not fully normalized yet.
- OpenAI-compatible auth is present, but still MVP-grade.
- The platform contains two provider abstractions: one for core RAG/runtime use and one for `/v1/*` compatibility routes.

Use this document for the actual runtime stack in the repo.
