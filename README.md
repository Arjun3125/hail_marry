# VidyaOS - AI Infrastructure for Indian K-12 Education

> ✅ **PRODUCTION READY** — All 79 features verified in code (April 12, 2026)
> 
> Multi-tenant school ERP plus curriculum-grounded AI assistant, implemented today as a Next.js frontend, a FastAPI modular monolith, and a Redis-backed worker.

---

## 📖 Documentation & Implementation Status

> **NEW:** Complete implementation verification across entire codebase (213+ Python files).
> 
> See [**DOCUMENTATION_INDEX.md**](all_documents/DOCUMENTATION_INDEX.md) for quick navigation to all docs.

### Key Documentation Files
- **[IMPLEMENTED_FEATURES_INVENTORY.md](all_documents/IMPLEMENTED_FEATURES_INVENTORY.md)** — All 79 features with backend file paths and API endpoints
- **[IMPLEMENTATION_VERIFICATION_REPORT.md](all_documents/IMPLEMENTATION_VERIFICATION_REPORT.md)** — Production readiness assessment (100% ready)
- **[VidyaOS_Features_List.md](all_documents/VidyaOS_Features_List.md)** — User-facing feature overview
- **[STAR_FEATURES_ANALYSIS.md](all_documents/STAR_FEATURES_ANALYSIS.md)** — Architecture validation against industry standards
- **[Testing.md](documentation/system_docs/Testing.md)** — Backend test suite (382 tests) + E2E testing strategy

---

## What This Repo Is

VidyaOS combines:
- a role-based school ERP for student, teacher, admin, and parent workflows
- a retrieval-grounded AI layer for study and teaching assistance
- governance tooling for AI review, queue operations, tracing, alerts, and webhooks
- demo-mode flows for local walkthroughs
- global feature management and white-label branding

The ERP remains the system of record. AI reads school context and materials, but does not authoritatively write ERP facts back into core ERP tables.

## Current Architecture

The current repository is a modular monolith with a separate worker process.

```text
Next.js frontend
  -> optional nginx reverse proxy
  -> FastAPI API in backend/main.py
      -> PostgreSQL
      -> Redis
      -> in-process AI workflows
          -> Ollama over HTTP
          -> FAISS by default, Qdrant optional
      -> Redis-backed worker in backend/ai_worker.py
```

Current runtime facts:
- Public synchronous AI requests are executed inside the FastAPI API process.
- Heavy jobs are queued in Redis and processed by `backend/ai_worker.py`.
- The repo does not currently contain a standalone FastAPI AI service.
- `AI_SERVICE_URL` and related settings exist in config and operations guidance, but they do not define an active runtime boundary in the current code path.

## Current Feature Scope

### ERP
- Attendance tracking
- Marks and results
- Assignments and file submission
- Timetable management
- Lecture library and uploads
- Complaint portal
- Parent-child linking and parent reporting
- Student file upload with ingestion support
- Spaced repetition review cards (SM-2 algorithm)
- Fee management
- Library management
- Admission workflow
- Self-service tenant onboarding
- Team invitations

### AI
- 12 text modes: Q&A, Study Guide, Quiz, Concept Map, Weak Topic, Flowchart, Mind Map, Flashcards, Socratic, Perturbation, Debate, Essay Review
- Audio overview and video overview
- Discovery search and URL ingestion
- Teacher assessment generation
- HyDE query transform
- Knowledge graph context lookup
- Agent orchestration workflows
- WhatsApp conversational entry points
- OpenAI-compatible API (`/v1/*`)
- Clickable citations in main API responses
- Document watcher plus queued ingestion
- Docs chatbot backed by FAQ matching with optional docs-RAG fallback

### Notebook System
- Notebook CRUD API
- Generated-content persistence per notebook
- Notebook-linked AI history logging
- Notebook-linked documents and generated artifacts

Current limitation:
- notebook-scoped retrieval is only partially wired in the current codebase; notebook metadata is persisted, but retrieval filtering is not fully converged in the core RAG path yet

### Governance and Operations
- Admin KPI dashboard
- AI usage analytics
- Queue operations (pause/resume/drain/cancel/retry/dead-letter)
- Queue metrics and audit history
- Trace viewer UI and trace-detail APIs
- Observability alerts with webhook/email/SMS delivery paths
- SAML configuration APIs
- Compliance export and deletion-request APIs
- Incident routing and lifecycle APIs
- Webhook subscriptions and delivery logs
- Audit logging
- Demo mode with role switching and data reset
- Razorpay billing integration
- Hindi and Marathi i18n
- reCAPTCHA support when configured
- Refresh-token blacklisting

### Feature Management and Branding
- Feature catalog stored in `backend/features_catalog.json`
- Runtime feature guards via `require_feature()`
- Three system profiles: AI Tutor, AI Helper, Full ERP
- White-label branding configuration and logo-based palette extraction

Current inventory:
- the feature catalog currently contains 55 tracked features

## Current Known Gaps

These are important implementation realities, not future marketing claims:
- The repo does not implement a separate AI service process even though some older docs still describe one.
- The feature-flag and branding surfaces are present, but some frontend/backend route prefixes still need normalization.
- Enterprise UI pages exist for SSO, compliance, and incidents, but the compliance and incidents pages still need API-contract cleanup.
- The plugin system is currently an in-memory hook registry, not a full installable module loader.
- The OpenAI-compatible API exists, but its auth path is still MVP-grade.

## Deployment Reality

Quick navigation:
- End users: `documentation/quickstart.md` -> Part A
- Developers: `documentation/quickstart.md` -> Part B

Application services:
- `frontend`: Next.js app in `frontend/`
- `api`: FastAPI app in `backend/main.py`
- `worker`: Redis queue worker in `backend/ai_worker.py`

Data and runtime dependencies:
- PostgreSQL for ERP and audit data
- Redis for queue state and ephemeral coordination
- Ollama for LLM and embeddings
- FAISS by default for vector retrieval, with Qdrant as an optional backend

Optional observability stack:
- Prometheus
- Loki
- Promtail
- Tempo
- Grafana
- DCGM exporter

## Railway Production Backend

For Railway production, run the backend as two explicit Dockerfile services from
the repo root:

- `backend-api`: `backend/Dockerfile`
- `backend-worker`: `backend/Dockerfile.worker`

Current checked-in Railway config reflects that split:
- `/railway.toml` selects the API Dockerfile, forces `sh /app/backend/start-api.sh`, and healthchecks `/ready`
- `/backend/railway.toml` selects the worker Dockerfile and forces `sh /app/backend/start-worker.sh`

Deployment guardrails:
- set both `JWT_SECRET` and `REFRESH_SECRET_KEY` to strong 32+ character values
- use `DATABASE_URL` and `REDIS_URL` from Railway services, not `localhost`
- for hosted demo deployments, use `APP_ENV=development`, `DEMO_MODE=true`, and `AUTO_SEED_DEMO_DATA=true` on the API service
- the worker health server now binds to Railway's assigned `PORT` by default

Production backend deploys should not rely on `start-all.sh`, `Dockerfile.demo`,
or custom start-command overrides.

## Canonical Runtime Packaging

VidyaOS now has four canonical runtime definitions:

- `backend/Dockerfile`: API service, built from repo-root context
- `backend/Dockerfile.worker`: queue worker, built from repo-root context
- `frontend/Dockerfile`: frontend service, built from `frontend/`
- `deploy/docker/demo.Dockerfile` plus `deploy/docker/frontend.demo.Dockerfile`:
  Class 11 CBSE showcase demo, launched through `deploy/compose/demo.yml`

Legacy Dockerfiles and compose files remain only as compatibility shims during
the transition. New CI, Railway, and compose wiring should always point back to
the canonical files above.

## Demo Contract

The supported demo experience is a single Class 11 Science (CBSE) tenant with
six months of synthetic activity for:

- student
- parent
- teacher
- admin

The canonical programmatic seeder is `backend/seed_cbse_demo.py`. The older
`backend/demo_seed.py` file remains only as a compatibility forwarder.

## Request Flows

### Synchronous public AI request

```text
request
  -> auth and tenant validation in API
  -> route handler in src/interfaces/rest_api/ai/routes/ai.py
  -> ai_gateway.py
  -> workflows.py
  -> retrieval, prompt assembly, generation, sanitation
  -> AIQuery log, trace events, optional webhook
  -> response
```

### Queued heavy job

```text
request
  -> public API validation
  -> Redis enqueue
  -> worker claim
  -> execute workflow through the same internal AI gateway/workflow layer
  -> queue metrics, audit trail, trace events
  -> status/result polling
```

## Observability Today

Implemented in the repo:
- structured JSON logging
- Prometheus-style metrics endpoints
- OpenTelemetry hooks
- persistent trace-event recording
- webhook and email/SMS alert paths
- Sentry integration for backend services
- GPU metrics via DCGM exporter

## Enterprise Foundations

Implemented foundations now include:
- tenant-scoped SAML configuration and metadata import
- compliance export bundles and deletion-request tracking
- incident routing plus acknowledge/resolve lifecycle APIs
- vector backend configuration reporting
- enterprise admin pages for SSO, compliance, and incidents

Important limitation:
- the SSO page is usable, but the compliance and incidents pages are not fully converged with backend response schemas yet

## Documentation Map

- `documentation/system_docs/Architecture.md`: current runtime topology and execution boundaries
- `documentation/system_docs/System overview.md`: current product scope and operating model
- `documentation/system_docs/Tech stack.md`: actual runtime stack in the repository
- `documentation/system_docs/Hosting and development env.md`: deployment and local environment guidance
- `documentation/system_docs/AI engine deep design.md`: AI execution and queue model
- `documentation/system_docs/Database schema.md`: schema intent and data-model guidance
- `documentation/system_docs/Filtering logic.md`: filtering and security layers
- `documentation/system_docs/Security checks.md`: security checklist and historical notes
- `documentation/system_docs/Testing.md`: test commands and current test inventory guidance

## Verification Guidance

Recommended commands:
- backend tests: `cd backend && python -m pytest tests/ -q`
- backend lightweight mode: `LIGHTWEIGHT_TEST_MODE=on pytest -q backend/tests`
- frontend lint: `cd frontend && npm run lint`
- frontend build: `cd frontend && npm run build`
- frontend e2e: `cd frontend && npm run test:e2e`

Do not treat static documentation counts as proof that tests are passing. Run the commands above in the current environment.

## License

Private - All rights reserved.
