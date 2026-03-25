# Tech Stack

**Project:** VidyaOS  
**Version:** v0.1 current implementation  
**Status:** Updated to match the repository on 2026-03-25

---

## 1. Frontend Stack

| Layer | Actual Technology in Repo |
|---|---|
| Framework | Next.js 16 |
| UI runtime | React 19 |
| Language | TypeScript |
| Styling | Tailwind CSS 4 |
| Theme engine | CSS Custom Properties via `BrandingProvider` context |
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
| Auth | Google OAuth + email/password + JWT (SAML config via enterprise routes) |
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
| Public synchronous execution boundary | `backend/services/ai_gateway.py` -> `backend/src/domains/ai_engine/router.py` |
| LLM runner | Ollama over HTTP |
| Default model | `llama3.2` |
| Fallback model | configurable, default currently also `llama3.2` |
| Embedding model | `nomic-embed-text` |
| Vector store | FAISS |
| Reranking | `cross-encoder/ms-marco-MiniLM-L-2-v2` when available |
| Provider abstraction | implemented for internal Ollama usage; multi-provider use is limited to the OpenAI-compatible API |
| Queueing | Redis-backed tenant-fair queue |
| Enterprise SSO library | `python3-saml` when installed |
| Service-grade vector option | Qdrant HTTP provider path |
| Source discovery | DuckDuckGo HTML search |
| Spaced repetition | SM-2 algorithm (custom implementation) |
| Brand color extraction | `colorthief` + WCAG 2.1 luminance math |
| Feature management | `features_catalog.json` + `FeatureFlag` model + runtime guards |

Important current reality:
- public synchronous generation is no longer executed directly in the public API
- queued generation calls the dedicated AI service
- queued ingestion and teacher assessment also dispatch through the dedicated AI service
- multi-provider support (OpenAI/Anthropic) is exposed via `/v1/*` endpoints, not the core RAG pipeline

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
- api
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
| Error tracking | Sentry SDK wired into API, AI service, worker |
| GPU monitoring | DCGM exporter + Grafana GPU dashboard |
| Alert rules | Prometheus rule file in `ops/observability/alert_rules.yml` |
| Admin observability UI | queue metrics UI + alert/trace APIs exposed |
| Incident routing | webhook, Slack webhook, PagerDuty Events API, Opsgenie API, email/SMS |

## 6. Testing and Verification

| Area | Tooling in Repo | Current Count |
|---|---|---|
| Backend tests | pytest | 382 tests across 48 files |
| Frontend lint | eslint | 0 errors |
| Frontend build verification | next build | All 50 pages compile |
| E2E framework | Playwright | — |

## 7. Code Quality

| Layer | Implementation |
|---|---|
| Backend constants | `backend/constants.py` — centralized thresholds, file limits, helpers |
| Frontend design tokens | `frontend/src/app/globals.css` — 50+ dark-mode-safe semantic CSS utilities |
| Upload security | `backend/utils/upload_security.py` — DOCX macro stripping, storage path validation |

## 8. Not Yet Implemented in the Tracked Stack

Still not first-class runtime components:
- Weaviate / Pinecone (Qdrant available)

Use this document for the actual runtime stack, not the older roadmap-only descriptions.
