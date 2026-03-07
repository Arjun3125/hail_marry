# System Overview

**Project Name:** VidyaOS  
**Version:** v0.1 pilot  
**Current Deployment Model:** Split application runtime with frontend, public API, dedicated AI service, worker, and optional observability stack  
**Status:** Updated to match the repository on 2026-03-06

---

## 1. Product Vision

VidyaOS is a multi-tenant school platform that combines:
- a deterministic ERP for school operations
- a grounded AI assistance layer for curriculum materials
- an admin governance and operations surface
- a parent reporting portal

The product goal is privacy-conscious, institution-ready AI for schools. The implementation now reaches that through a split runtime rather than the older single-backend description.

## 2. Current System Pillars

| Pillar | Current Meaning |
|---|---|
| Multi-tenant by default | Major data paths, queue metrics, and audit trails are scoped by `tenant_id` |
| AI as augmentation | AI reads school data and materials, but does not authoritatively write ERP records |
| Citation-grounded responses | Retrieval-backed responses include citation validation and source fallback behavior |
| Governance visibility | Admins can inspect AI usage, review responses, inspect traces, and operate the queue |
| Operational pragmatism | The stack now uses a dedicated AI service and worker queue, while keeping Ollama external |

## 3. Current Product Scope

### ERP
- Student, class, enrollment, attendance, marks, assignments, timetable, complaints, lectures
- Student file upload with RAG ingestion
- Assignment file submission
- CSV exports for attendance, performance, AI usage

### AI
- 13 text-generation / study modes: Q&A, Study Guide, Quiz, Concept Map, Weak Topic, Flowchart, Mind Map, Flashcards, Socratic, Perturbation, Debate, Essay Review, Career Simulation
- Audio overview generation (podcast-style dialogue)
- Video overview generation (narrated slide presentation)
- Discovery search (DuckDuckGo-powered) and URL ingestion
- Teacher assessment generation (NCERT-aligned formative assessments)
- Tenant-scoped retrieval over uploaded materials
- Language, response length, and expertise level personalization
- SM-2 spaced repetition scheduling for review cards

### Governance and operations
- Admin KPIs and performance heatmap (subjects × classes)
- AI review actions (approve / flag)
- Queue operations and metrics (pause / resume / drain / cancel / retry / dead-letter controls)
- Persistent audit history for queue actions
- Trace viewer and observability alerts
- Incident routing plus acknowledge / resolve workflow
- Compliance export and deletion-request tracking
- Webhook subscriptions and delivery logs
- Parent link management

### Teacher tools
- Class insights with weak topic analysis
- Doubt heatmap (aggregated student AI queries by subject)
- Assessment generator (RAG + LLM)
- Source discovery and URL ingestion
- YouTube transcript ingestion

### Parent experience
- Dashboard with child's performance summary
- Attendance and results views
- Downloadable reports and audio report generation

### Demo mode
- Role switching between student, teacher, admin, parent
- Guided walkthrough for each role
- Database reset capability

## 4. Current Operational Flows

### Public AI query flow
```text
student or teacher request
  -> public API auth + tenant validation
  -> AI gateway
  -> dedicated AI service
  -> retrieval + Ollama generation
  -> sanitize, validate citations, log AIQuery
  -> optional webhook emission
```

### Queued heavy-work flow
```text
request
  -> public API validation
  -> Redis enqueue
  -> worker claim
  -> dispatch workflow to dedicated AI service
  -> queue metrics, audit history, trace events
  -> client polls status
```

### Ingestion flow
```text
upload or URL input
  -> extraction and chunking
  -> embedding generation
  -> FAISS storage in tenant namespace
  -> ingestion status update
```

### Parent reporting flow
```text
parent request
  -> auth + parent role validation
  -> parent_links lookup for child_id
  -> child's attendance / marks / performance
  -> optional audio report generation
```

## 5. Current Constraints

Important current realities:
- Public synchronous generation goes through the AI service
- Generation-heavy long-running tasks are queue-backed
- All queued workflows (ingestion, teacher assessment, study tools) dispatch through the dedicated AI service
- Ollama is still external to the tracked stack
- SAML SSO configuration backend is implemented; no dedicated admin UI for it yet

## 6. Roadmap Items Still Pending

- Dedicated admin UI for SAML SSO, compliance, and incident management
- Android app
- Service-grade vector backend for multi-node scaling

Use this overview as the current product picture.
