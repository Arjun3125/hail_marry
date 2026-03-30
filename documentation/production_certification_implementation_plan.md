# Production Certification Implementation Plan

**Date:** 2026-03-29  
**Source audit:** [full_system_audit_report.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/full_system_audit_report.md)  
**Goal:** Close the remaining gaps between "implemented and locally verified" and "fully production-certified end-to-end".

## 1. Objective

Move the system from strong internal integration quality to full production certification across:

- live WhatsApp external integration
- browser-level user workflows
- OCR quality on difficult inputs
- deterministic grounding coverage for remaining AI features
- latency and observability standards
- OCR review/edit UX consistency

## 2. What Production-Certified Means

The system is only considered production-certified when all of the following are true:

1. Live external integrations are validated in a staging or production-like environment.
2. Core user journeys are verified in the browser, not just at API level.
3. Heavy background work does not block user-facing request paths.
4. OCR quality on real-world difficult inputs is benchmarked and improved to an acceptable operational level.
5. All major RAG-backed AI features have deterministic grounding acceptance coverage.
6. Operators can measure latency, failures, retries, and degraded states across ingestion, retrieval, and generation.
7. Users can review and correct OCR output anywhere structured data quality matters.

## 3. Current State Summary

Based on [full_system_audit_report.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/full_system_audit_report.md):

- the backend architecture is implemented and locally verified
- RAG, OCR, study tools, WhatsApp routing, and ingestion are working in code
- the remaining gaps are mostly production hardening and live-environment validation

Open certification blockers:

1. large WhatsApp audio/video transcription still runs on a synchronous ingestion path
2. browser-level E2E coverage is incomplete for the most important OCR and RAG workflows
3. OCR accuracy is still weak on handwriting, classroom-board, and hard multilingual inputs
4. debate assistant and essay review are implemented, but lack deterministic grounding acceptance tests
5. no completed live staging pass exists for real WhatsApp Cloud API/device traffic
6. latency budgets and subsystem-level performance telemetry are incomplete
7. OCR review/edit UX is only present on some high-value surfaces, not all structured import paths

## 4. Definition of Done

This certification plan is complete only when all of the following are true:

1. WhatsApp media transcription for large inputs is queue-backed or otherwise non-blocking.
2. Playwright or equivalent E2E coverage exists for:
   - upload
   - OCR review
   - study tool generation
   - admin onboarding
3. OCR benchmark improvement work is complete and documented with updated reported metrics.
4. Debate assistant and essay review have deterministic grounding tests comparable to other core study tools.
5. A real-device WhatsApp staging pass is executed and documented.
6. Latency metrics and alert thresholds exist for:
   - transcription
   - embedding
   - retrieval
   - tool generation
7. OCR review/edit UX is available across all structured import surfaces that can materially corrupt data if OCR is wrong.

## 5. Execution Strategy

Execute in seven workstreams, in order of operational risk.

---

## Workstream A: Move Large WhatsApp Media Transcription to Background Jobs

### Objective

Remove expensive media transcription from the synchronous WhatsApp request path so large audio/video ingestion does not block webhook handling or degrade user response reliability.

### Problem

The system now supports audio/video transcription in the ingestion layer, but the current request path is still too expensive for production if users send larger clips or several clips at once.

### Tasks

1. Define job types for media transcription and media ingestion completion.
2. Move WhatsApp audio/video ingestion from inline execution to queue-backed processing.
3. Return immediate WhatsApp acknowledgement when a media file is accepted for background processing.
4. Send completion/failure notification back to WhatsApp when transcript indexing finishes.
5. Preserve notebook/session state so the user can continue in the same conversation after the job completes.
6. Add retry rules, file retention windows, and failure classification for:
   - ffmpeg missing
   - decode failure
   - transcription failure
   - embedding failure
   - vector-store write failure

### Primary files

- [whatsapp_gateway.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/platform/services/whatsapp_gateway.py)
- [ai_queue.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/platform/services/ai_queue.py)
- [ingestion.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/infrastructure/vector_store/ingestion.py)
- [ai_jobs.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/routes/ai_jobs.py)
- WhatsApp queue/integration tests

### Acceptance criteria

- large media transcription no longer blocks the synchronous WhatsApp webhook path
- users receive immediate acknowledgement plus a later success/failure notification
- queue retries and dead-letter behavior are defined and test-covered

---

## Workstream B: Add Browser-Level E2E Coverage for Critical User Journeys

### Objective

Verify that real users can complete the most important workflows through the actual web UI, not just through API or unit tests.

### Problem

The frontend is wired correctly, but production certification requires browser-level validation of inputs, state transitions, rendering, and error messaging.

### Tasks

1. Add E2E coverage for student upload and post-upload visibility.
2. Add E2E coverage for OCR review signals on image upload paths.
3. Add E2E coverage for study-tool generation and job polling.
4. Add E2E coverage for admin onboarding preview/edit and final submit.
5. Add stable test fixtures and environment bootstrapping for AI/runtime dependencies.
6. Add CI execution strategy for smoke vs. full regression E2E suites.

### Primary files

- [playwright.config.ts](/c:/Users/naren/Work/Projects/proxy_notebooklm/frontend/playwright.config.ts)
- [smoke.spec.ts](/c:/Users/naren/Work/Projects/proxy_notebooklm/frontend/tests/e2e/smoke.spec.ts)
- [student upload page](/c:/Users/naren/Work/Projects/proxy_notebooklm/frontend/src/app/student/upload/page.tsx)
- [student tools page](/c:/Users/naren/Work/Projects/proxy_notebooklm/frontend/src/app/student/tools/page.tsx)
- [student assignments page](/c:/Users/naren/Work/Projects/proxy_notebooklm/frontend/src/app/student/assignments/page.tsx)
- [setup wizard page](/c:/Users/naren/Work/Projects/proxy_notebooklm/frontend/src/app/admin/setup-wizard/page.tsx)

### Acceptance criteria

- core upload, OCR, study-tool, and onboarding flows are exercised in the browser
- failures are visible in browser tests, not only backend tests
- a repeatable E2E command exists for staging and CI

---

## Workstream C: Improve OCR Accuracy Using Benchmark-Driven Tuning

### Objective

Raise OCR quality on the hardest real-world inputs using the benchmark corpus that already exists.

### Problem

OCR is enabled system-wide, but difficult categories such as handwriting, classroom-board photos, and mixed-language low-quality captures are still too weak for production confidence.

### Tasks

1. Use the current benchmark report to identify the worst categories by accuracy.
2. Add category-targeted preprocessing improvements such as:
   - deskew
   - adaptive thresholding
   - blur/noise handling
   - contrast heuristics
   - morphology for board/handwriting cases
3. Evaluate selective fallback behavior for difficult categories.
4. Add confidence thresholds or warning rules tuned by benchmark data.
5. Re-run the benchmark after each tuning slice and record results.
6. Update the OCR report with before/after metrics.

### Primary files

- [ocr_service.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/infrastructure/vector_store/ocr_service.py)
- [test_ocr_benchmark.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/tests/evaluation/test_ocr_benchmark.py)
- [ocr_benchmark_report.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/ocr_benchmark_report.md)
- OCR fixture scripts under `backend/scripts/`

### Acceptance criteria

- benchmark report shows measurable improvement on hard categories
- review-required thresholds are tied to benchmarked behavior, not guesswork
- OCR quality claims are backed by updated metrics

---

## Workstream D: Add Deterministic Grounding Coverage for Debate Assistant and Essay Review

### Objective

Bring debate assistant and essay review up to the same grounding-certification standard as the already tested core study tools.

### Problem

These features exist in prompts and orchestration, but they still lack deterministic acceptance tests proving that they stay grounded in retrieved textbook context.

### Tasks

1. Extend the textbook grounding suite to cover debate assistant.
2. Extend the textbook grounding suite to cover essay review.
3. Define feature-specific scoring rules for:
   - concept coverage
   - grounding ratio
   - citation coverage
   - forbidden hallucinations
4. Add positive and failure fixtures for unsupported/context-missing cases.
5. Integrate these checks into the same evaluation discipline used by the other study tools.

### Primary files

- [workflows.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/workflows.py)
- [study_tools.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/shared/ai_tools/study_tools.py)
- [test_textbook_feature_grounding.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/tests/evaluation/test_textbook_feature_grounding.py)

### Acceptance criteria

- debate assistant and essay review are covered by deterministic grounding tests
- failures are distinguishable as retrieval/grounding/template problems
- all major study features have explicit grounding acceptance coverage

---

## Workstream E: Run Live WhatsApp Staging Certification

### Objective

Prove the WhatsApp channel against the real external system, not only through local mocks and route tests.

### Problem

Local WhatsApp tests are strong, but production certification requires real webhook traffic, real credentials, and actual device interaction.

### Tasks

1. Prepare staging credentials and webhook configuration.
2. Run the existing manual script against a real phone/device.
3. Validate:
   - signup/linking
   - session restore
   - file upload
   - URL ingestion
   - same-message link/file plus question
   - study-tool generation
   - async notifications
4. Record failures with timestamps, payloads, and recovery actions.
5. Update the release gate with pass/fail evidence and sign-off notes.

### Primary files

- [whatsapp_release_gate.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/whatsapp_release_gate.md)
- [whatsapp_staging_manual_test_script.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/whatsapp_staging_manual_test_script.md)
- WhatsApp route/service files under `backend/src/domains/platform/`

### Acceptance criteria

- a real staging pass is executed and documented
- real webhook send/receive behavior is verified
- production-certification status can be updated from "No" to "Yes" for the external integration part

---

## Workstream F: Add Latency Budgets and Observability for the AI Pipeline

### Objective

Make the slowest subsystems measurable and enforce explicit latency expectations.

### Problem

Metrics exist for HTTP, OCR, queue depth, and some WhatsApp events, but not enough subsystem timing exists yet for certification and operations.

### Tasks

1. Define latency budgets for:
   - media transcription
   - OCR extraction
   - embedding generation
   - retrieval
   - study-tool generation
   - WhatsApp end-to-end response
2. Add timing instrumentation to the relevant services.
3. Export counters/histograms or equivalent metrics for each stage.
4. Add alert thresholds for sustained degradation.
5. Document target SLO-style expectations for staging and production.

### Primary files

- [metrics_registry.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/platform/services/metrics_registry.py)
- [alerting.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/platform/services/alerting.py)
- [telemetry.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/platform/services/telemetry.py)
- [ai_queue.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/platform/services/ai_queue.py)
- [ingestion.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/infrastructure/vector_store/ingestion.py)
- [whatsapp_gateway.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/platform/services/whatsapp_gateway.py)

### Acceptance criteria

- subsystem-level latency is measurable
- alerting thresholds exist for major slow/failing paths
- operators can identify whether slowness comes from transcription, embeddings, retrieval, generation, or delivery

---

## Workstream G: Expand OCR Review/Edit UX to Every Structured Import Surface

### Objective

Ensure that any OCR-based structured import lets the user review and correct extracted content before committing changes that affect records.

### Problem

Some OCR review UX already exists, but not all structured import surfaces provide consistent preview/edit behavior before final persistence.

### Tasks

1. Inventory every OCR-backed structured import route.
2. Add preview/edit UX for:
   - attendance import
   - marks import
   - teacher onboarding
   - student onboarding
   - any remaining OCR-backed structured admin flows
3. Standardize review-required banners, confidence display, and unmatched-line feedback.
4. Add explicit "confirm import" vs. "edit and retry" flow.
5. Add frontend tests for these review screens.

### Primary files

- [teacher.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/academic/routes/teacher.py)
- [admin.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/administrative/routes/admin.py)
- [onboarding.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/identity/routes/onboarding.py)
- teacher/admin/onboarding frontend surfaces

### Acceptance criteria

- every structured OCR import has a review/edit path
- low-confidence or partially parsed OCR never commits silently
- OCR review UX is consistent across admin, teacher, and onboarding flows

## 6. Recommended Execution Phases

### Phase 1: Reliability and Observability Foundation

- Workstream A
- Workstream F

### Phase 2: Certification Test Surface

- Workstream B
- Workstream D

### Phase 3: Quality and UX Hardening

- Workstream C
- Workstream G

### Phase 4: External Certification

- Workstream E

## 7. Recommended First Implementation Slice

Start with this slice:

1. move WhatsApp media transcription to AI queue jobs
2. add timing instrumentation around transcription, embedding, retrieval, and tool generation
3. add one Playwright E2E for student upload plus study tool generation
4. extend deterministic grounding tests for debate assistant

This is the highest-leverage slice because it improves production reliability, closes visibility gaps, and expands certification evidence quickly.

## 8. Final Outcome Expected

After this plan is complete, the system should be able to change the audit answer for:

`Is the system fully production-certified end-to-end, including live external integrations and UX validation?`

from:

- `No`

to:

- `Yes`

with evidence, not assumption.
