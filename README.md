# VidyaOS - AI Infrastructure for Indian K-12 Education

> Multi-tenant school ERP plus curriculum-grounded AI assistant, implemented as a Next.js frontend, a FastAPI API tier, a dedicated AI service, and a Redis-backed worker queue.

## What This Repo Is

VidyaOS combines:
- a role-based school ERP for student, teacher, admin, and parent workflows
- a retrieval-grounded AI layer for study and teaching assistance
- governance tooling for AI review, queue operations, tracing, alerts, and webhooks
- a demo mode with role switching and guided walkthrough

The ERP remains the system of record. AI reads school context and materials, but does not authoritatively write back ERP facts.

## Current Architecture

```text
Next.js frontend
    -> optional nginx reverse proxy
    -> FastAPI public API
        -> PostgreSQL
        -> Redis
        -> AI gateway
            -> dedicated FastAPI AI service
                -> Ollama via OLLAMA_URL
                -> FAISS vector store
        -> Redis-backed worker
            -> queued jobs dispatched to AI service
```

Current runtime facts:
- Public synchronous AI endpoints call the dedicated AI service through `backend/services/ai_gateway.py`.
- Heavy jobs are queued in Redis and processed by `backend/ai_worker.py`.
- All queued AI-heavy jobs use the AI service boundary.
- FAISS remains the current vector backend.
- Ollama remains an external dependency configured through `OLLAMA_URL`.

## Current Feature Scope

### ERP
- Attendance tracking
- Marks and results
- Assignments and file submission
- Timetable management
- Lecture library and uploads
- Complaint portal
- Parent-child linking and parent reporting
- Student file upload with RAG ingestion
- Spaced repetition review cards (SM-2 algorithm)
- CSV exports for attendance, performance, AI usage
- Performance heatmap (subjects × classes)

### AI
- Q&A
- Study Guide
- Quiz
- Concept Map
- Weak Topic
- Flowchart
- Mind Map
- Flashcards
- Socratic
- Perturbation
- Debate
- Essay Review
- Career Simulation
- Audio overview and video overview
- Discovery search and URL ingestion
- Teacher assessment generation
- Doubt heatmap aggregation
- Language, response length, and expertise level personalization

### Teacher Tools
- Class insights with weak topic analysis
- Doubt heatmap (aggregated student AI queries by subject)
- Assessment generator (NCERT-aligned formative assessments via RAG + LLM)
- Source discovery (DuckDuckGo-powered) and URL ingestion
- YouTube transcript ingestion

### Parent Portal
- Dashboard with child's performance summary
- Attendance and results views
- Downloadable reports and audio report generation

### Governance and Operations
- Admin KPI dashboard
- AI usage analytics
- AI review actions with approve / flag
- Queue operations with cancel / retry / dead-letter controls
- Queue metrics and audit history
- Trace viewer
- Observability alerts with webhook dispatch
- Enterprise SSO foundation with tenant-scoped SAML configuration and ACS / metadata endpoints
- Compliance export and deletion-request tracking APIs
- Incident routing and acknowledgement / resolution APIs
- Webhook subscriptions and delivery logs
- Audit logging for admin and queue actions
- Demo mode with role switching and data reset

## Deployment Reality

### Application services
- `frontend`: Next.js app in `frontend/`
- `api`: public FastAPI app in `backend/main.py`
- `ai-service`: dedicated AI execution app in `backend/ai_service_app.py`
- `worker`: Redis queue worker in `backend/ai_worker.py`

### Data and runtime dependencies
- PostgreSQL for ERP and audit data
- Redis for queue state, rate limiting, and related ephemeral state
- Ollama for LLM and embedding access
- FAISS for tenant-scoped vector retrieval

### Optional observability stack
The compose stack can also start:
- Prometheus
- Loki
- Promtail
- Tempo
- Grafana

Prebuilt observability assets tracked in the repo:
- Prometheus alert rules in `ops/observability/alert_rules.yml`
- provisioned Grafana datasources and dashboards in `ops/observability/grafana/provisioning/`

## AI Execution Model Today

### Synchronous public AI request
```text
request
  -> auth / tenant validation in public API
  -> AI gateway
  -> dedicated AI service
      -> embed
      -> retrieve from FAISS
      -> rerank / dedup / compress
      -> prompt assembly with personalization
      -> Ollama generation
      -> sanitize + citation validation
  -> AIQuery log + trace events + optional webhook
  -> response
```

### Queued heavy job
```text
request
  -> public API validation
  -> Redis enqueue
  -> worker claim
  -> queued workflow execution through dedicated AI service
  -> queue metrics + audit trail + trace events
  -> status/result polling
```

## Observability Today

Implemented in the repo:
- structured JSON logging
- Prometheus-style metrics endpoints on API, AI service, and worker health app
- OpenTelemetry export hooks
- Tempo / Loki / Grafana / Prometheus compose integration
- persistent trace-event recording
- admin alerts and trace viewer
- webhook dispatch for active alerts

This is now more than app-local inspection. It is still not a full external incident-management stack with pager/email integrations.

## Enterprise Foundations

Implemented foundations in the repo now include:
- tenant-scoped SAML SSO configuration and metadata import
- pluggable vector backend selection with FAISS default and Qdrant provider path
- compliance export bundles and deletion-request tracking
- incident routing for webhook, Slack webhook, PagerDuty Events, and Opsgenie-style targets
- incident acknowledgement, resolution, and timeline events

## Middleware Stack

| Middleware | Purpose |
|---|---|
| `ObservabilityMiddleware` | Structured logging and request metrics |
| `CORSMiddleware` | Cross-origin request control |
| `CSRFMiddleware` | CSRF protection (disabled in demo mode) |
| `TenantMiddleware` | Tenant context injection from JWT |
| `RateLimitMiddleware` | Request throttling (disabled in demo mode) |

## Roadmap, Not Current Reality

These are still open or partial:
- stronger operator tooling beyond current queue controls
- dedicated admin UI for SAML SSO, compliance, and incident management
- service-grade vector backend
- broader external alert transports such as email / pager integrations

## Documentation Map
- `documentation/system_docs/Architecture.md`: current service topology and execution boundaries
- `documentation/system_docs/System overview.md`: current product scope and operating model
- `documentation/system_docs/Tech stack.md`: actual runtime stack in the repository
- `documentation/system_docs/Hosting and development env.md`: current deployment model and compose topology
- `documentation/system_docs/AI engine deep design.md`: current AI execution and queue model
- `documentation/system_docs/Database schema.md`: complete database schema with all tables
- `documentation/system_docs/Sitemap wireframe.md`: full sitemap for all four roles
- `documentation/system_docs/Admin review dashboard.md`: admin dashboard capabilities
- `documentation/system_docs/Filtering logic.md`: filtering and security layers
- `documentation/system_docs/Security checks.md`: pre-launch security checklist
- `documentation/system_docs/Ui design.md`: UI design system and component patterns
- `documentation/system_docs/Backup and recovery policy.md`: backup and recovery procedures

## Verification Status

Current local verification target:
- backend tests: `python -m pytest -q -p no:cacheprovider backend/tests`
- frontend lint: `npm run lint`
- frontend production build: `npm run build`
- frontend e2e: `npm run test:e2e`

## License

Private - All rights reserved.
