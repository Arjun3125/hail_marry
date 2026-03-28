# System Overview

**Project Name:** VidyaOS  
**Version:** v0.1 pilot  
**Current Deployment Model:** Frontend, FastAPI modular monolith, Redis worker, and optional observability stack  
**Status:** Updated to match the repository on 2026-03-28

---

## 1. Product Vision

VidyaOS is a multi-tenant school platform that combines:
- a deterministic ERP for school operations
- a grounded AI assistance layer for curriculum materials
- an admin governance and operations surface
- parent reporting and communication paths

The current repository implements that as one main API process plus a worker, not as separate public API and AI-service processes.

## 2. Current System Pillars

| Pillar | Current Meaning |
|---|---|
| Multi-tenant by default | Major ERP, queue, and audit paths are scoped by `tenant_id` |
| AI as augmentation | AI reads school data and materials but does not authoritatively mutate ERP facts |
| Citation-grounded responses | Retrieval-backed responses include sanitation and citation-aware response handling |
| Governance visibility | Admins can inspect AI usage, traces, alerts, and queue state |
| Operational pragmatism | The stack uses an API plus a worker, while keeping Ollama external |

## 3. Current Product Scope

### ERP
- Student, class, enrollment, attendance, marks, assignments, timetable, complaints, lectures
- Student file upload and ingestion support
- Assignment file submission
- CSV exports for attendance, performance, and AI usage
- Fee management, library, admissions, onboarding, and invitations

### AI
- 12 text modes: Q&A, Study Guide, Quiz, Concept Map, Weak Topic, Flowchart, Mind Map, Flashcards, Socratic, Perturbation, Debate, Essay Review
- Audio overview generation
- Video overview generation
- Discovery search and URL ingestion
- Teacher assessment generation
- Tenant-scoped retrieval over uploaded materials
- Language, response length, and expertise-level personalization
- Spaced repetition scheduling for review cards
- OpenAI-compatible `/v1/*` endpoints

### Governance and operations
- Admin KPIs and performance heatmap
- AI review actions
- Queue operations and metrics
- Queue audit history
- Trace viewer and observability alerts
- QR login support for student accounts
- Incident routing plus acknowledge/resolve workflow
- Compliance export and deletion-request tracking
- Webhook subscriptions and delivery logs
- Parent-link management

### Feature management and branding
- Feature catalog and runtime feature guards
- Three system profiles: AI Tutor, AI Helper, Full ERP
- White-label branding engine with logo color extraction
- Admin dashboards at `/admin/feature-flags` and `/admin/branding`

Current inventory:
- the feature catalog currently contains 55 entries

### Teacher tools
- Class insights with weak topic analysis
- Doubt heatmap
- Assessment generator
- Source discovery and URL ingestion
- YouTube transcript ingestion

### Parent experience
- Dashboard with attendance, marks, and next-class context
- Attendance and results views
- Downloadable reports and audio reporting hooks

### Demo mode
- Role switching between student, teacher, admin, and parent
- Guided walkthrough support
- Database reset capability

### Notebook system
- Notebook CRUD
- Notebook-linked AI history
- Notebook-linked generated content
- Notebook-linked document metadata

Known limitation:
- notebook-scoped retrieval is not yet fully converged in the core RAG path

## 4. Current Operational Flows

### Public AI query flow

```text
student or teacher request
  -> API auth and tenant validation
  -> internal AI gateway
  -> retrieval and generation workflow
  -> sanitize, enrich citations, log AIQuery
  -> optional webhook emission
```

### Queued heavy-work flow

```text
request
  -> API validation
  -> Redis enqueue
  -> worker claim
  -> execute internal workflow
  -> queue metrics, audit history, trace events
  -> client polls status
```

### Ingestion flow

```text
upload or URL input
  -> extraction and chunking
  -> embedding generation
  -> vector storage
  -> ingestion status update
```

### Parent reporting flow

```text
parent request
  -> auth and parent-role validation
  -> parent_links lookup
  -> child attendance and marks retrieval
  -> optional audio report generation
```

## 5. Current Constraints

Important current realities:
- public synchronous generation runs inside the API process
- long-running jobs are queue-backed
- Ollama is external to the tracked stack
- enterprise admin pages exist for SSO, compliance, and incidents

## 6. Known Gaps

The following areas are still partial or inconsistent:
- notebook-scoped retrieval filtering in the core RAG path
- compliance and incidents frontend pages need response-schema cleanup
- some admin API clients still assume `/api/...` prefixes where backend routes currently use non-`/api` prefixes
- the plugin architecture is a hook registry, not a full plugin installation system
- AI grading remains limited compared with the broader product vision

## 7. Maturity Statement

The repo is broader than a prototype and supports meaningful local/demo workflows, but it should still be treated as pilot-stage software rather than a fully converged production platform.

Use this overview as the current product picture.
