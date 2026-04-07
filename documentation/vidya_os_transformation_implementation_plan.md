# Implementation Plan: Indian EdTech "Vidya OS" Transformation

This plan converts the broader Vidya OS architecture ambition into an execution
program anchored to the current repository structure.

It is intentionally sequential. Each phase must stabilize before the next one
becomes the primary delivery lane.

## Program Decision

Approved default sequence for this repository:

1. Phase 0: Critical Stability Fixes
2. Phase 1: Core Platform
3. Phase 2: India-First Experience and Localization
4. Phase 3: Automation and Trust Layer
5. Phase 4: Intelligence Layer

We are not front-loading WhatsApp Bot interfaces ahead of the core data layer.
The platform needs the data and permission model to be reliable before broader
automation is added on top.

## User Review Risks

### Data migration alert

Phase 1 may require schema and migration work affecting:

- unified learner and parent linkage
- tenant-scoped academic records
- fee and class/batch records
- assessment registry and grading relationships

Any migration touching existing rows must include:

- forward migration script
- rollback strategy
- tenant safety checks
- seed/demo fixture verification

### Infrastructure requirements

Phase 0 and Phase 3 require a reliable background execution layer. Current repo
foundations already exist in places such as:

- `backend/src/domains/platform/services/worker_runtime.py`
- `backend/src/domains/platform/services/ai_queue.py`
- `backend/src/domains/platform/services/grading_queue.py`
- `backend/src/domains/platform/services/notification_dispatch.py`
- `backend/src/domains/platform/services/whatsapp_gateway.py`

Before expanding automation load, we must decide whether the canonical runtime
is:

- FastAPI background tasks with Redis-backed queue semantics
- RQ
- Celery
- or a hardened internal worker runtime already present in this repo

## Phase 0: Critical Stability Fixes

Goal: prevent high-concurrency spikes from degrading auth, middleware, and
review workflows before more product weight is added.

### Backend resilience

1. Fix OAuth synchronous blocking
   Target path:
   - `backend/auth/oauth.py`
   Work:
   - audit Google request handling for blocking calls
   - move blocking external IO into `asyncio.to_thread` or equivalent safe executor path
   Exit criteria:
   - login path no longer blocks the event loop under concurrent load

2. Add JWT payload caching
   Target path:
   - `backend/middleware/tenant.py`
   Work:
   - add bounded TTL/LRU cache for repeat decode/tenant-resolution paths
   - preserve tenant safety and revocation behavior
   Exit criteria:
   - repeated authenticated requests avoid redundant heavy JWT decode work

3. Decouple SM-2 persistence pressure
   Target path:
   - `backend/src/domains/academic/application/student_reviews.py`
   Work:
   - isolate `_sm2_update()` side effects from request path
   - batch or queue write-heavy updates where safe
   Exit criteria:
   - review completion no longer depends on per-request row-lock-heavy write pattern

### Verification

- `backend/tests/test_openai_compat.py`
- `backend/tests/test_sm2_algorithm.py`
- targeted concurrency/load verification for OAuth and review completion

## Phase 1: Core Platform

Goal: make Vidya OS a unified platform instead of disconnected role surfaces.

### Data models and permissions

1. Unified student profile
   Existing repo anchor:
   - `backend/src/domains/academic/models/student_profile.py`
   Related models:
   - `backend/src/domains/academic/models/attendance.py`
   - `backend/src/domains/academic/models/performance.py`
   - `backend/src/domains/academic/models/parent_link.py`
   Work:
   - unify attendance, marks, parent linkage, and risk inputs around a stable student profile contract

2. Role-based access control
   Existing repo anchors:
   - `backend/auth/dependencies.py`
   - `backend/auth/scoping.py`
   - `backend/src/domains/identity/routes/auth.py`
   - route modules under `backend/src/domains/**/routes/`
   Work:
   - enforce Student, Teacher, Parent, Admin boundaries consistently across FastAPI dependencies and route entry points

3. Core administrative models
   Existing repo anchors:
   - `backend/src/domains/administrative/models/fee.py`
   - `backend/src/domains/academic/models/batch.py`
   - `backend/src/domains/identity/models/tenant.py`
   Work:
   - normalize institute/branch, fee, and class/batch ownership under strict tenant isolation

4. Mock test and assessment registry
   Existing repo anchors:
   - `backend/src/domains/academic/models/test_series.py`
   - `backend/src/domains/academic/application/assessment_generation.py`
   - `backend/src/domains/academic/models/marks.py`
   Work:
   - define assessment lifecycle, timing, grading state, and async job linkage

### Exit criteria

- unified student record can power parent, teacher, and admin insights
- tenant isolation is enforced at the model and route boundary
- assessment lifecycle is durable enough for automation and analytics phases

## Phase 2: India-First Experience and Localization

Goal: keep the product usable on low-cost Android hardware and lower-bandwidth
connections without degrading first paint or language correctness.

### Frontend optimization

1. Remove heavy aesthetics from operational surfaces
   Existing repo anchors:
   - `frontend/src/app/student/leaderboard/page.tsx`
   - shared Prism styles in `frontend/src/app/globals.css`
   Work:
   - reduce GPU-taxing blur, animation, and unnecessary visual load on dense screens

2. Fix vernacular SSR and eliminate flash-of-English content
   Existing repo anchors:
   - `frontend/src/i18n/LanguageProvider.tsx`
   - `backend/src/domains/platform/routes/i18n.py`
   Work:
   - move language preference from client-only storage to server-readable cookie strategy
   - ensure first HTML paint is already localized

3. Adaptive connection loading
   Existing repo anchors:
   - `frontend/src/hooks/useNetworkAware.ts`
   - landing 3D and other heavy surfaces under `frontend/src/components/prism/`
   Work:
   - disable non-critical polling, asset-heavy modules, and optional effects on constrained networks

### Exit criteria

- no flash of English before localized UI settles
- operational pages remain responsive on constrained devices
- heavy optional visuals degrade cleanly under network pressure

## Phase 3: Automation and Trust Layer

Goal: bring teacher and parent workflows into reliable automation channels with
auditable delivery.

### Triggers and webhooks

1. Parent WhatsApp workflow
   Existing repo anchors:
   - `backend/src/domains/academic/services/whatsapp.py`
   - `backend/src/domains/platform/routes/whatsapp.py`
   - `backend/src/domains/platform/services/whatsapp_gateway.py`
   - mascot/WhatsApp tests already present under `backend/tests/`
   Work:
   - automate attendance and homework reminders through Meta Cloud API-backed flows

2. Teacher WhatsApp assistant
   Existing repo anchors:
   - `backend/src/shared/ai_tools/whatsapp_teacher_tools.py`
   - `backend/src/interfaces/whatsapp/`
   - `backend/src/interfaces/rest_api/whatsapp/`
   Work:
   - expose controlled `/attendance` and `/lesson` style intents through chat workflows

3. Async AI auto-grading
   Existing repo anchors:
   - `backend/src/domains/platform/services/ai_grading.py`
   - `backend/src/domains/platform/services/grading_queue.py`
   - `backend/src/interfaces/rest_api/ai/routes/ai_jobs.py`
   Work:
   - route OCR-derived assessments through grading pipeline and teacher review surfaces

4. Notification event bus
   Existing repo anchors:
   - `backend/src/domains/platform/models/notification.py`
   - `backend/src/domains/platform/services/notification_dispatch.py`
   - `backend/src/domains/platform/services/notifications.py`
   - `backend/src/domains/platform/services/emailer.py`
   - `backend/src/domains/platform/services/sms.py`
   Work:
   - centralize outbound email, SMS, and WhatsApp events with audit history

### Exit criteria

- outbound parent communication is auditable
- teacher automation is permission-safe
- grading automation produces reviewable outputs, not silent final decisions

## Phase 4: Intelligence Layer

Goal: turn the aggregated operational and learning graph into principal- and
owner-level intelligence.

### Predictive analytics

1. Telemetry ingestion
   Existing repo anchors:
   - `backend/src/domains/platform/services/telemetry.py`
   - `backend/src/domains/platform/services/telemetry_events.py`
   Work:
   - normalize user and workflow events into analyzable warehouse-friendly records

2. Student risk flags
   Existing repo anchors:
   - `backend/src/domains/academic/services/risk_cron.py`
   - `backend/src/domains/academic/services/weakness_alerts.py`
   - `backend/src/domains/platform/services/alerting.py`
   Work:
   - daily scans for academic decline and fee-default risk

3. Personal mastery map
   Existing repo anchors:
   - `frontend/src/app/student/mastery/page.tsx`
   - `backend/src/domains/platform/services/mastery_tracking_service.py`
   - `backend/src/domains/platform/models/topic_mastery.py`
   Work:
   - move from coarse visualization to sub-topic-level actionable mastery maps

### Exit criteria

- principals and operators get visible risk alerts from unified records
- mastery map reflects actual sub-topic signal, not static demo-only structure

## Verification Plan

### Automated verification

Phase 0 minimum:

- `backend/tests/test_openai_compat.py`
- `backend/tests/test_sm2_algorithm.py`

Program-wide minimum:

- backend targeted pytest for touched domains
- `frontend/npm run lint`
- `frontend/npm run build`
- Playwright coverage for user-visible workflow changes

### Manual verification

- simulate Fast 3G in Chrome DevTools for localized first-paint behavior
- confirm no FOUC/FOEC on Hindi or other vernacular render paths
- load test auth and other concurrency-sensitive endpoints after Phase 0

## Non-Negotiables

- no phase may silently rewrite auth, tenant, or API boundaries without explicit migration planning
- no WhatsApp automation expansion before queue/runtime reliability is established
- no analytics claims without unified underlying records
- all new automation must be auditable

## Program Completion Definition

This transformation is done only when:

- Phase 0 concurrency hardening is merged and verified
- Phase 1 shared data layer and RBAC are stable
- Phase 2 localization and low-bandwidth UX are verified
- Phase 3 automation flows are auditable and worker-backed
- Phase 4 analytics are powered by real unified records

