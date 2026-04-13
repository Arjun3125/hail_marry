# Architecture

**Project:** VidyaOS  
**Version:** v0.1 current implementation  
**Status:** Source of truth for the repository structure as of 2026-04-12

---

## 1. Architecture Decision

The current repository is a modular monolith with a separate worker process.

Current practical service roles:
- Next.js frontend
- FastAPI public API
- Redis-backed worker

Core data services:
- PostgreSQL
- Redis
- FAISS vector storage by default
- Qdrant as an optional vector backend
- Ollama over HTTP

Important clarification:
- the current repo does not implement a separate FastAPI AI service
- synchronous AI runs inside the API process
- queued AI runs inside the worker process through the same internal gateway/workflow layer

## 2. Current System Topology

```text
browser
  -> Next.js frontend
  -> optional nginx reverse proxy
  -> FastAPI public API
      -> PostgreSQL
      -> Redis
      -> internal AI gateway
          -> workflow execution
              -> Ollama
              -> retrieval runtime

Redis-backed worker
  -> queued job orchestration
  -> internal AI gateway
  -> same workflow layer used by the API
```

## 3. Module Responsibilities

### Frontend
Implemented in `frontend/src/app`:
- role-based pages for student, teacher, admin, and parent
- queue operations UI
- dashboard alert UI
- trace viewer UI
- demo mode with role switching
- feature management dashboard
- branding dashboard
- enterprise admin pages for SSO, compliance, and incidents

### Public API
Implemented in `backend/main.py` and routed through domain modules:
- auth and JWT handling
- tenant scoping and RBAC
- ERP APIs
- admin APIs
- queue enqueue/status routes
- AI query routes
- webhook emission
- dashboard and observability APIs
- demo management APIs
- enterprise APIs

### AI Execution Layer
Implemented across:
- `backend/src/interfaces/rest_api/ai/routes/`
- `backend/src/domains/platform/services/ai_gateway.py`
- `backend/src/interfaces/rest_api/ai/workflows.py`

Responsibilities:
- synchronous text/audio/video AI requests
- queued AI task execution
- retrieval, prompt assembly, generation, and sanitation
- citations, cache hooks, trace IDs, and AI query logging

### Worker
Implemented in:
- `backend/ai_worker.py`
- `backend/src/domains/platform/services/ai_queue.py`
- `backend/worker_health_app.py`

Responsibilities:
- Redis job claiming and execution
- queue state transitions
- retry and dead-letter handling
- worker health/readiness endpoint

### Platform Domain
Implemented in `backend/src/domains/platform/`:
- feature flag management
- feature catalog bootstrap
- runtime feature gating
- branding API
- docs chatbot
- notifications
- WhatsApp routes and gateway
- notebook and generated-content APIs

## 4. Execution Boundaries

### Public synchronous AI requests
- The public API executes generation locally through `ai_gateway.py`.
- The active path is route handler -> gateway -> workflow function -> retrieval/provider layer.

### Queued AI jobs
- The worker claims jobs from Redis.
- The worker also executes AI-heavy job types locally through the same internal gateway/workflow functions.
- There is no external AI-service hop in the current runtime.

## 5. Data Flow

### Synchronous generation

```text
client request
  -> public API auth and tenant checks
  -> AI route
  -> ai_gateway.py
  -> retrieval and generation workflow
  -> AIQuery log and trace events
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

### Document watch ingestion

```text
watched folder change
  -> runtime_scheduler.py
  -> document row creation
  -> queue enqueue
  -> worker ingestion workflow
```

## 6. Governance and Operations

Implemented operator surfaces:
- admin AI review
- admin queue operations
- queue metrics and audit history
- trace lookup by `trace_id`
- alert evaluation and dispatch
- enterprise APIs for SSO, compliance, and incidents

Known convergence gaps:
- compliance and incident frontend pages exist, but their payload contracts still need cleanup

## 7. Observability Architecture

Implemented in app code:
- structured JSON logging
- metrics endpoints on API and worker health app
- OpenTelemetry instrumentation hooks
- persistent trace-event recording
- Sentry integration

Implemented in compose profiles:
- Prometheus
- Loki
- Promtail
- Tempo
- Grafana
- DCGM exporter

## 8. Deployment Model

### Compose stack
Tracked services in `docker-compose.yml`:
- `postgres`
- `redis`
- `api`
- `worker`
- `frontend`
- `nginx`

Optional compose profiles:
- observability: `prometheus`, `loki`, `promtail`, `tempo`, `grafana`, `dcgm-exporter`
