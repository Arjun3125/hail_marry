# Architecture

**Project:** VidyaOS  
**Version:** v0.1 current implementation  
**Status:** Source of truth for the repo as implemented on 2026-03-06

---

## 1. Architecture Decision

The repository no longer matches the earlier fully monolithic description.

Current implementation is a split runtime with four practical service roles:
- Next.js frontend
- FastAPI public API
- dedicated FastAPI AI service
- Redis-backed worker

Core data services:
- PostgreSQL
- Redis
- FAISS vector storage
- Ollama over HTTP

## 2. Current System Topology

```text
browser
  -> Next.js frontend
  -> optional nginx reverse proxy
  -> FastAPI public API
      -> PostgreSQL
      -> Redis
      -> AI gateway
          -> dedicated AI service
              -> Ollama
              -> FAISS retrieval runtime
      -> worker queue producer

Redis-backed worker
  -> queued job orchestration
  -> dedicated AI service for all AI-heavy execution
```

## 3. Module Responsibilities

### Frontend
Implemented in `frontend/src/app`:
- role-based pages for student, teacher, admin, and parent
- queue operations UI
- dashboard alert UI
- trace viewer UI
- demo mode with role switching and guided walkthrough

### Public API
Implemented in `backend/main.py` and `backend/routes/`:
- auth and JWT handling
- tenant scoping and RBAC
- ERP APIs
- admin APIs
- queue enqueue/status routes
- webhook emission
- dashboard and observability APIs
- demo management APIs (role switching, data reset)
- enterprise APIs (SSO, compliance, incidents)

### Dedicated AI service
Implemented in `backend/ai_service_app.py`:
- query generation
- audio overview generation
- video overview generation
- study-tool generation
- teacher assessment generation
- URL ingestion
- teacher document ingestion
- teacher YouTube ingestion

### Worker
Implemented in `backend/ai_worker.py` and `backend/services/ai_queue.py`:
- Redis job claiming and execution
- queue state transitions
- retry and dead-letter handling
- dedicated AI service dispatch
- worker health/readiness endpoint served by `backend/worker_health_app.py`

## 4. Execution Boundaries

### Public synchronous AI requests
- Public API does not execute generation locally.
- It calls the dedicated AI service through `backend/services/ai_gateway.py`.

### Queued AI jobs
- Worker claims jobs from Redis.
- Worker dispatches all AI-heavy job types to the dedicated AI service.

## 5. Data Flow

### Synchronous generation
```text
client request
  -> public API auth / tenant checks
  -> AI gateway
  -> AI service
      -> embed
      -> FAISS retrieval
      -> rerank / dedup / compress
      -> prompt assembly
      -> Ollama generation
      -> sanitize + citation validation
  -> AIQuery log + trace events
  -> response
```

### Queued heavy work
```text
client request
  -> public API validation
  -> Redis enqueue
  -> worker claim
  -> execute workflow
  -> update queue metrics, audit history, trace events
  -> client polls status endpoint
```

## 6. Governance and Operations

Implemented operator surfaces:
- admin AI review with approve / flag
- admin queue operations with pause / resume / drain / cancel / retry / dead-letter
- queue metrics and audit history
- trace lookup by `trace_id`
- active alert evaluation and dispatch through webhook subscriptions and email transports
- enterprise APIs for SAML SSO settings, compliance exports, deletion tracking, and incident lifecycle

## 7. Observability Architecture

Implemented in app code:
- structured JSON logging
- metrics endpoints on API, AI service, and worker
- OpenTelemetry instrumentation hooks
- persistent trace-event recording

Implemented in compose:
- Prometheus
- Loki
- Promtail
- Tempo
- Grafana
- prebuilt alert rules and Grafana dashboards provisioned from `ops/observability/`

## 8. Deployment Model

### Compose stack
Tracked services in `docker-compose.yml`:
- `postgres`
- `redis`
- `api`
- `ai-service`
- `worker`
- `frontend`
- `nginx`

Optional compose profile:
- `prometheus`
- `loki`
- `promtail`
- `tempo`
- `grafana`

### External dependency
- Ollama is still external to the compose stack and is reached through `OLLAMA_URL`.

## 9. Middleware Stack

The public API applies these middleware layers (last added executes first):
- `ObservabilityMiddleware` — structured logging and request metrics
- `CORSMiddleware` — cross-origin request control
- `CSRFMiddleware` — CSRF protection (disabled in demo mode)
- `TenantMiddleware` — tenant context injection from JWT
- `RateLimitMiddleware` — request throttling (disabled in demo mode)

## 10. Remaining Architectural Gaps

Still not fully closed:
- enterprise features are backend-first; there is not yet a dedicated admin UI for the SAML, compliance, and incident routes

## 11. Convergence Rule

Use this file as the source of truth for current runtime topology. Older references to:
- fully monolithic AI execution
- no worker queue
- no observability stack
- no parent portal
- no demo mode

should be treated as historical unless updated.
