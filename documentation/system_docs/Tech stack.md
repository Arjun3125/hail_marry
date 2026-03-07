# Tech Stack

**Project:** VidyaOS  
**Version:** v0.1 current implementation  
**Status:** Updated to match the repository on 2026-03-06

---

## 1. Frontend Stack

| Layer | Actual Technology in Repo |
|---|---|
| Framework | Next.js 16 |
| UI runtime | React 19 |
| Language | TypeScript |
| Styling | Tailwind CSS 4 |
| Icons | lucide-react |
| Routing | Next.js app router |
| E2E testing | Playwright |

## 2. Backend Stack

| Layer | Actual Technology in Repo |
|---|---|
| Public API framework | FastAPI |
| Dedicated AI service | FastAPI |
| Worker runtime | Python process using Redis queue service |
| Language | Python 3.11+ |
| ORM | SQLAlchemy |
| Validation | Pydantic |
| Migration tooling | Alembic |
| Auth | Google OAuth + JWT |
| Queue state and cache support | Redis |

### Middleware Stack

| Middleware | Purpose |
|---|---|
| `ObservabilityMiddleware` | Structured logging, request metrics |
| `CORSMiddleware` | Cross-origin request control |
| `CSRFMiddleware` | CSRF protection on state-changing requests (disabled in demo mode) |
| `TenantMiddleware` | Tenant context injection from JWT |
| `RateLimitMiddleware` | Request throttling (disabled in demo mode) |

## 3. AI Stack

| Capability | Current Implementation |
|---|---|
| Public synchronous execution boundary | `backend/services/ai_gateway.py` -> `backend/ai_service_app.py` |
| LLM runner | Ollama over HTTP |
| Default model | `llama3.2` |
| Fallback model | configurable, default currently also `llama3.2` |
| Embedding model | `nomic-embed-text` |
| Vector store | FAISS |
| Reranking | `cross-encoder/ms-marco-MiniLM-L-2-v2` when available |
| Provider abstraction | implemented and used through provider adapters |
| Queueing | Redis-backed tenant-fair queue |
| Enterprise SSO library | `python3-saml` when installed |
| Service-grade vector option | Qdrant HTTP provider path |
| Source discovery | DuckDuckGo HTML search |
| Spaced repetition | SM-2 algorithm (custom implementation) |

Important current reality:
- public synchronous generation is no longer executed directly in the public API
- queued generation calls the dedicated AI service
- queued ingestion and teacher assessment also dispatch through the dedicated AI service

## 4. Infrastructure and Local Deployment

| Layer | Current Implementation |
|---|---|
| Local container orchestration | Docker Compose |
| Reverse proxy | Nginx |
| Database | PostgreSQL 15+ |
| Queue / cache | Redis 7 |
| Frontend container | tracked `frontend/Dockerfile` |
| API container | tracked `backend/Dockerfile` |
| Worker container | tracked `backend/Dockerfile.worker` |

Current compose stack:
- postgres
- redis
- api
- ai-service
- worker
- frontend
- nginx

External dependency:
- Ollama reachable via `OLLAMA_URL`

## 5. Observability Stack

| Capability | Current Implementation |
|---|---|
| Structured logs | JSON logs written by app services |
| Metrics export | Prometheus-style `/metrics` endpoints |
| Tracing | OpenTelemetry export hooks plus Tempo profile |
| Log aggregation | Loki + Promtail compose profile |
| Dashboarding | Grafana compose profile with provisioned overview dashboard |
| Alert rules | Prometheus rule file in `ops/observability/alert_rules.yml` |
| Admin observability UI | queue metrics, alerts, and trace viewer |
| Incident routing | webhook, Slack webhook, PagerDuty Events API, Opsgenie API |

## 6. Testing and Verification

| Area | Tooling in Repo |
|---|---|
| Backend tests | pytest |
| Frontend lint | eslint |
| Frontend build verification | next build |
| E2E framework | Playwright |

## 7. Not Yet Implemented in the Tracked Stack

Still not first-class runtime components:
- external pager / email alert transport
- SAML SSO (backend configuration exists, no admin UI)
- Qdrant / Weaviate / Pinecone as active vector backends

Use this document for the actual runtime stack, not the older roadmap-only descriptions.
