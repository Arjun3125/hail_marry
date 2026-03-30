# Production Certification Execution Checklist

**Date:** 2026-03-30  
**Source plan:** [production_certification_implementation_plan.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/production_certification_implementation_plan.md)  
**Source audit:** [full_system_audit_report.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/full_system_audit_report.md)  
**Purpose:** Convert the open production-certification gaps into concrete implementation work with code ownership, acceptance criteria, and execution order.

## Current Progress

### 2026-03-29 update

The first implementation slice is now underway.

Implemented in this pass:

- WhatsApp audio/video uploads are now accepted into a queued ingestion path instead of being rejected up front
- audio/video uploads are persisted and queued as `whatsapp_media_ingest` AI jobs
- queued media jobs execute transcript ingestion asynchronously through the shared AI queue
- WhatsApp completion notifications now support media-ingest jobs using the worker `response_text` when available
- the gateway no longer tries to run an inline grounded follow-up before queued media ingestion finishes
- the original user follow-up prompt is now carried through the queued media job and answered after transcript ingestion completes
- stage latency instrumentation now exists for AI retrieval, AI generation, WhatsApp media transcription, embedding, deferred follow-up generation, and whole queue job execution
- Prometheus export now includes stage latency counters, sums, and max latency gauges
- observability alerting now raises latency warnings when core pipeline stages exceed configured budgets with enough sample volume
- focused queue, WhatsApp, alerting, and metrics regression tests were updated and are passing
- Playwright now blocks service workers so browser-side API route mocking is deterministic during E2E runs
- a student browser E2E slice now verifies OCR-aware upload UX and study-tool generation against mocked API responses in the real built app
- the new student E2E spec passes locally against the production Next.js build
- deterministic textbook grounding coverage now includes debate assistant and essay review
- browser E2E now verifies admin OCR preview/edit/confirm import and student assignment OCR review warnings
- the expanded student plus OCR review browser suite passes locally against the production Next.js build
- Playwright scripts now expose separate smoke and full entrypoints for faster local and CI execution
- the smoke suite now covers landing, student upload OCR review, and student study-tool generation
- the fuller browser regression slice now also covers a study-tool failure path alongside admin queue/dashboard and OCR review flows
- the OCR benchmark gate has been re-run after selector/preprocessing tuning and now passes cleanly across the full fixture set
- teacher-side student roster OCR imports now expose preview, inline edit, and explicit confirm import on the classes page
- browser E2E now verifies the teacher student-roster OCR preview/edit/confirm flow
- browser E2E now also verifies teacher student-roster OCR preview failure handling before any import is committed
- teacher attendance now supports OCR/CSV import directly from the attendance screen with review-warning feedback
- teacher marks now support OCR/CSV import from the marks screen after exam creation with review-warning feedback
- browser E2E now verifies teacher attendance OCR import and teacher marks OCR import flows
- GitHub Actions now runs the Playwright smoke suite automatically on normal CI and can run the full suite on manual dispatch with artifact upload

Still remaining inside Workstream A:

- real staging/device validation of the queued media behavior

Workstream F status after this pass:

- target warning budgets are now defined in configuration for retrieval, generation, transcription, and embedding
- subsystem latency is measurable in-process and exportable through the existing metrics endpoint
- remaining work is operator-facing rollout: dashboards, live traffic baselines, and staged validation against real workload patterns

Workstream B status after this pass:

- browser coverage now includes the student upload flow with OCR confidence/review messaging
- browser coverage now includes student study-tool generation rendering in the real built app
- browser coverage now includes admin onboarding OCR preview/edit/confirm and student assignment OCR review warnings
- browser coverage now includes teacher-side OCR roster preview/edit/confirm for student onboarding
- browser coverage now includes a teacher-side OCR preview failure path for unreadable roster uploads
- browser coverage now includes teacher attendance OCR import with low-confidence review messaging
- browser coverage now includes teacher marks OCR import with low-confidence review messaging
- smoke coverage now runs automatically in CI, while the fuller regression suite is available through workflow dispatch with artifact capture
- browser coverage now includes a non-happy-path study-tool generation failure case
- remaining work is broader failure-path coverage and staged rollout/monitoring of the suite

Workstream E status after this pass:

- the WhatsApp release gate already existed and now has a structured staging evidence template
- operators can now capture a single `release-gate-snapshot` endpoint output that bundles analytics, release metrics, and derived failure percentages
- the admin dashboard now surfaces the WhatsApp release-gate snapshot for operator review without raw API calls
- the manual staging script now requires pre-run and post-run snapshot capture for auditable sign-off
- remaining work is the real external execution itself: live credentials, real device traffic, and signed staging evidence

Workstream C status after this pass:

- OCR selector/preprocessing tuning has been revalidated against the full benchmark fixture set
- the current OCR regression gate passes end-to-end (`12 passed`)
- benchmark documentation now records that hard categories still require review-first UX even though the regression gate is green
- remaining work is future quality uplift, not a missing release guardrail

Workstream G status after this pass:

- admin onboarding and teacher-side student roster imports now both enforce preview/edit/confirm before OCR-derived structured data is persisted
- low-confidence OCR remains visible through warning/confidence metadata during review flows
- teacher attendance and marks imports now surface OCR confidence and review warnings in the UI before/after structured import submission
- browser verification now covers admin onboarding, teacher roster, teacher attendance, and teacher marks OCR flows
- this workstream is complete for the currently implemented structured OCR import surfaces

## 1. Priority Order

Execute in this order:

1. move WhatsApp media transcription off the synchronous request path
2. add latency budgets and subsystem observability
3. add browser-level E2E coverage for critical OCR and RAG flows
4. add deterministic grounding coverage for debate assistant and essay review
5. improve OCR accuracy on the hardest benchmark categories
6. expand OCR review/edit UX to every structured import surface
7. run live WhatsApp staging certification and close the release gate

## 2. Workstream A: Async WhatsApp Media Transcription

### Problem

Media transcription exists, but the expensive path is still too close to synchronous WhatsApp request handling for production confidence.

### Files

- [whatsapp_gateway.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/platform/services/whatsapp_gateway.py)
- [ai_queue.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/platform/services/ai_queue.py)
- [ingestion.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/infrastructure/vector_store/ingestion.py)
- [ai_jobs.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/routes/ai_jobs.py)
- WhatsApp queue/integration tests

### Tasks

- Define queue-backed job types for media transcription and indexing.
- Replace inline audio/video transcription in WhatsApp ingestion with job enqueue + immediate acknowledgement.
- Persist enough metadata to resume notebook-scoped follow-up after job completion.
- Send job completion/failure notifications back to WhatsApp users.
- Add retry, dead-letter, and user-visible remediation behavior.
- Add regression tests for:
  - media accepted -> job queued
  - job completed -> WhatsApp notified
  - job failed -> actionable WhatsApp message

### Acceptance criteria

- large media no longer blocks synchronous WhatsApp handling
- queued media jobs are recoverable, observable, and retry-safe
- user messaging remains coherent before and after background completion

## 3. Workstream B: Browser-Level E2E Coverage

### Problem

UI wiring is present, but production certification requires browser-level proof that users can actually complete the core workflows.

### Files

- [playwright.config.ts](/c:/Users/naren/Work/Projects/proxy_notebooklm/frontend/playwright.config.ts)
- [smoke.spec.ts](/c:/Users/naren/Work/Projects/proxy_notebooklm/frontend/tests/e2e/smoke.spec.ts)
- student and admin E2E specs under `frontend/tests/e2e/`
- [student upload page](/c:/Users/naren/Work/Projects/proxy_notebooklm/frontend/src/app/student/upload/page.tsx)
- [student tools page](/c:/Users/naren/Work/Projects/proxy_notebooklm/frontend/src/app/student/tools/page.tsx)
- [student assignments page](/c:/Users/naren/Work/Projects/proxy_notebooklm/frontend/src/app/student/assignments/page.tsx)
- [setup wizard page](/c:/Users/naren/Work/Projects/proxy_notebooklm/frontend/src/app/admin/setup-wizard/page.tsx)

### Tasks

- Add E2E coverage for student upload including OCR metadata visibility.
- Add E2E coverage for study-tool generation and async polling.
- Add E2E coverage for OCR review/edit flow in admin onboarding.
- Add E2E coverage for assignment image submission review signals.
- Define fixture strategy for stable local/CI runs.
- Split smoke and full suites for faster execution.

### Acceptance criteria

- browser tests cover the main OCR + RAG user journeys
- failures in UI rendering/state transitions are detectable in CI or staging
- at least one fast smoke suite and one fuller regression suite exist

## 4. Workstream C: OCR Accuracy Tuning

### Problem

The OCR benchmark passes as a regression gate, but difficult categories still show weak practical accuracy.

### Files

- [ocr_service.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/infrastructure/vector_store/ocr_service.py)
- [test_ocr_benchmark.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/tests/evaluation/test_ocr_benchmark.py)
- [ocr_benchmark_report.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/ocr_benchmark_report.md)
- OCR fixture scripts and assets under `backend/scripts/` and `backend/tests/fixtures/ocr/`

### Tasks

- Rank worst OCR categories by current benchmark results.
- Add targeted preprocessing for handwriting and classroom-board conditions.
- Add threshold or warning tuning based on benchmark evidence.
- Re-run the benchmark after each major tuning change.
- Update the report with before/after accuracy numbers.
- Document any categories that remain intentionally review-required.

### Acceptance criteria

- hard OCR categories show measurable improvement
- OCR warnings and confidence rules are benchmark-informed
- updated benchmark evidence is recorded in documentation

## 5. Workstream D: Deterministic Grounding for Debate and Essay Review

### Problem

Debate assistant and essay review are implemented, but they still lag behind the core study tools in grounding certification.

### Files

- [workflows.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/workflows.py)
- [study_tools.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/shared/ai_tools/study_tools.py)
- [test_textbook_feature_grounding.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/tests/evaluation/test_textbook_feature_grounding.py)

### Tasks

- Add debate assistant fixture outputs and thresholds.
- Add essay review fixture outputs and thresholds.
- Add hallucination rejection checks for off-topic criticism or unsupported claims.
- Add citation coverage checks where the feature expects contextual references.
- Keep the evaluation deterministic and runnable without live model dependence.

### Acceptance criteria

- debate assistant has deterministic grounding coverage
- essay review has deterministic grounding coverage
- all major study features now share the same evaluation discipline

## 6. Workstream E: Live WhatsApp Staging Certification

### Problem

The local WhatsApp backend is strong, but production certification needs real external validation.

### Files

- [whatsapp_release_gate.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/whatsapp_release_gate.md)
- [whatsapp_staging_manual_test_script.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/whatsapp_staging_manual_test_script.md)
- WhatsApp service/route files under `backend/src/domains/platform/`

### Tasks

- prepare staging credentials and webhook target
- run the real-device test script
- verify auth, uploads, links, follow-up queries, async completion, and response formatting
- capture screenshots/logs/error evidence for failures
- mark each release-gate item pass/fail with date and tester

### Acceptance criteria

- a real device completed the critical WhatsApp flows
- webhook delivery and outbound response are validated against the live external system
- release gate evidence exists in documentation

## 7. Workstream F: Latency Budgets and Observability

### Problem

Metrics exist, but not enough subsystem-level timing exists yet to certify latency expectations.

### Files

- [metrics_registry.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/platform/services/metrics_registry.py)
- [alerting.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/platform/services/alerting.py)
- [telemetry.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/platform/services/telemetry.py)
- [ai_queue.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/platform/services/ai_queue.py)
- [ingestion.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/infrastructure/vector_store/ingestion.py)
- [whatsapp_gateway.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/platform/services/whatsapp_gateway.py)

### Tasks

- define target budgets for each major pipeline stage
- instrument transcription timing
- instrument embedding timing
- instrument retrieval timing
- instrument tool-generation timing
- instrument end-to-end WhatsApp request latency
- expose metrics and alert conditions for sustained degradation

### Acceptance criteria

- major slow stages are measurable independently
- alert conditions exist for material latency regressions
- operators can localize performance problems quickly

## 8. Workstream G: OCR Review/Edit UX Expansion

### Problem

Some OCR review UX exists, but structured imports still do not all have a full preview/edit-confirm experience.

### Files

- [teacher.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/academic/routes/teacher.py)
- [admin.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/administrative/routes/admin.py)
- [onboarding.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/identity/routes/onboarding.py)
- related frontend pages for teacher/admin/onboarding import flows

### Tasks

- inventory every OCR-backed structured import surface
- add preview/edit UI where missing
- standardize confidence, warning, and unmatched-line messaging
- require explicit confirm before final import on OCR-derived structured data
- add frontend regression coverage for the review flows

### Acceptance criteria

- all structured OCR imports support review/edit before persistence
- low-confidence OCR never silently commits structured changes
- UX is consistent across admin, teacher, and onboarding flows

## 9. Recommended First Implementation Slice

Start here:

1. queue WhatsApp media transcription
2. instrument transcription/embedding/retrieval/generation latency
3. add one student upload + study tool Playwright test
4. extend deterministic grounding coverage to debate assistant

This sequence gives the fastest improvement in reliability, certification evidence, and operational visibility.

## 10. Suggested Status Tracking

Use this status model while executing:

- `Not started`
- `In progress`
- `Partially complete`
- `Complete`
- `Blocked`

Recommended current state:

- `A`: In progress
- `B`: In progress
- `C`: Complete
- `D`: Complete
- `E`: Partially complete
- `F`: In progress
- `G`: Complete
