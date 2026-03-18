# VidyaOS - AI Infrastructure for Indian K-12 Education

> Multi-tenant school ERP plus curriculum-grounded AI assistant, implemented as a Next.js frontend, a FastAPI API tier, a dedicated AI service, and a Redis-backed worker queue.

## What This Repo Is

VidyaOS combines:
- a role-based school ERP for student, teacher, admin, and parent workflows
- a retrieval-grounded AI layer for study and teaching assistance
- governance tooling for AI review, queue operations, tracing, alerts, and webhooks
- a demo mode with role switching and guided walkthrough

The ERP remains the system of record. AI reads school context and materials, but does not authoritatively write back ERP facts.

## Current Architecture (Modular Monolith)

```text
Next.js frontend
    -> optional nginx reverse proxy
    -> FastAPI public API (Bounded Contexts: Identity, Academic, Admin, AI Engine, Platform)
        -> PostgreSQL
        -> Redis
        -> Native AI Service Execution (No HTTP Hop)
            -> Ollama via OLLAMA_URL
            -> FAISS vector store
        -> Redis-backed worker
            -> queued jobs dispatched to AI service
```

Current runtime facts:
- Public synchronous AI endpoints run directly within the native FastAPI API instance through Domain-Driven routing.
- Heavy jobs are queued in Redis and processed by `backend/ai_worker.py`.
- FAISS is the default vector backend; Qdrant is available for scale-out.
- LLM inference and reasoning is natively orchestrated via LangGraph.

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
- Fee management (structures, invoices, payments, reports)
- Library management (catalog, lending, returns, overdue tracking)
- Admission workflow (application pipeline with status tracking)
- Self-service tenant onboarding
- Self-service team invitation (invite-by-email flow)

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
- HyDE query transform (True zero-shot LLM hypothetical document generation)
- Knowledge graph index (Vector embeddings and Recursive PostgreSQL CTE query matching)
- Agent orchestration (LangGraph stateful dynamic planning/tool routing for deep study, exam prep, admin tasks)
- Extended data connectors (PPTX, Excel, Google Docs, Notion)
- Clickable citations (source-document linking)
- OpenAI-compatible API (/v1/chat/completions, /v1/models)
- Document ingestion watch (auto-ingest from folders)
- Docs-as-AI chatbot (self-service support from VidyaOS documentation)

Note: Clickable citations, docs chatbot, and document ingestion watch exist in code
but are not yet wired into the main AI request flow. Extended connectors are wired
for PPTX/XLSX uploads and Google Docs/Notion URL ingestion when dependencies and API
tokens are configured.

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
- Queue operations (pause/resume/drain/cancel/retry/dead-letter)
- Queue metrics and audit history
- Trace viewer UI + trace-detail API
- Observability alerts with admin APIs + webhook/email/SMS dispatch
- Enterprise SSO foundation with tenant-scoped SAML configuration and ACS / metadata endpoints
- Compliance export and deletion-request tracking APIs
- Incident routing and acknowledgement / resolution APIs
- Webhook subscriptions and delivery logs
- Audit logging for admin and queue actions
- Demo mode with role switching and data reset
- Razorpay billing integration (plans, subscriptions, payment records)
- Hindi + Marathi i18n (locale-based translations)
- reCAPTCHA / bot protection on public endpoints
- Refresh token blacklisting (JTI-based)
- Module plugin architecture (6 hooks, extensible registry)
- DPDP Act 2023 compliance review

## Deployment Reality

Quick navigation:
- **End users (hosted website login/use):** see `documentation/quickstart.md` → **Part A — User Quickstart**.
- **Developers (local setup/contribution):** see `documentation/quickstart.md` → **Part B — Developer Quickstart**.

### Application services
- `frontend`: Next.js app in `frontend/`
- `api`: Domain-Driven FastAPI app in `backend/main.py`
- `worker`: Redis queue worker in `backend/ai_worker.py`

### Data and runtime dependencies
- PostgreSQL for ERP and audit data
- Redis for queue state, rate limiting, and related ephemeral state
- Ollama for LLM and embedding access
- FAISS for tenant-scoped vector retrieval (Qdrant optional)

### Optional observability stack
The compose stack can also start:
- Prometheus
- Loki
- Promtail
- Tempo
- Grafana
- DCGM exporter (GPU metrics)

Prebuilt observability assets tracked in the repo:
- Prometheus alert rules in `ops/observability/alert_rules.yml`
- provisioned Grafana datasources and dashboards in `ops/observability/grafana/provisioning/`

### Synchronous public AI request
```text
request
  -> auth / tenant validation in public API
  -> domain router (src/domains/ai_engine)
  -> stateful LangGraph orchestrator
      -> bind tools (academic, admin, platform)
      -> embed & FAISS retrieve / Rerank
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
- webhook + email/SMS dispatch for active alerts
- Sentry error tracking for backend services
- GPU metrics via DCGM exporter (Grafana dashboard)

This is now more than app-local inspection, with webhook + email/SMS alerting and Sentry error tracking wired in.

## Enterprise Foundations

Implemented foundations in the repo now include:
- tenant-scoped SAML SSO configuration and metadata import
- pluggable vector backend selection with FAISS default and Qdrant provider path
- compliance export bundles and deletion-request tracking
- incident routing for webhook, Slack webhook, PagerDuty Events, and Opsgenie-style targets
- incident acknowledgement, resolution, and timeline events

## Known Gaps (Current Status)

The following items remain partially wired or incomplete:
- AI grading currently returns OCR extraction + manual review; full rubric scoring is pending.
- Clickable citations
- Docs-as-AI chatbot API
- Document ingestion watch scheduler

## Middleware Stack

| Middleware | Purpose |
|---|---|
| `ObservabilityMiddleware` | Structured logging and request metrics |
| `CORSMiddleware` | Cross-origin request control |
| `CSRFMiddleware` | CSRF protection (disabled in demo mode) |
| `TenantMiddleware` | Tenant context injection from JWT |
| `RateLimitMiddleware` | Request throttling (disabled in demo mode) |
| `CaptchaMiddleware` | reCAPTCHA v3 bot protection on public endpoints (enabled when secret is configured) |

## Backend Code Quality

All magic numbers, thresholds, and configuration constants are centralized in `backend/constants.py`:
- grading thresholds and `compute_grade()` helper
- attendance / performance thresholds with `attendance_emoji()` and `performance_color()` helpers
- file upload limits and allowed extensions
- rate limiting window
- PDF generation color constants
- fee types, frequencies, and invoice statuses
- LLM provider defaults and supported providers
- extended file types (PPTX, XLSX, Google Docs, Notion)

Frontend uses 50+ dark-mode-safe semantic CSS utilities in `frontend/src/app/globals.css`, replacing all hardcoded Tailwind color classes.

## Roadmap, Not Current Reality

These are still open or partial:
- dedicated admin UI for SAML SSO, compliance, and incident management
- mobile app shell (Capacitor/TWA) for Play Store
- AI grading rubric scoring (OCR-only today)
- clickable citations + docs chatbot + document ingestion watch wiring

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
- `documentation/system_docs/Testing.md`: test suite map, quick start, dependencies, and guide for adding tests
- `documentation/DPDP_COMPLIANCE.md`: DPDP Act 2023 compliance review for student data
- `documentation/timetable_generator_spec.md`: timetable generator algorithm specification (no code)

## Verification Status

Current local verification targets:
- backend tests: `cd backend && python -m pytest tests/ -q` — **438 tests fully passing**
- frontend lint: `cd frontend && npm run lint`
- frontend production build: `cd frontend && npm run build`
- frontend e2e: `cd frontend && npm run test:e2e`

Test coverage spans: auth security, RBAC, CSRF, file uploads, AI queue, alerting, gamification, config validation, tenant isolation, security regressions, constants, whatsapp, webhooks, leaderboard, rate limiting, compliance, incident management, upload security, report card, infrastructure utilities, fee management, OpenAI-compat API, knowledge graph, HyDE, connectors, token blacklisting, citations, doc watcher, agent orchestrator, captcha, plugin registry, library, team invitations, docs chatbot.

## License

Private - All rights reserved.
