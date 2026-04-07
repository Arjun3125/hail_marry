# Vidya OS Transformation Execution Checklist

This checklist is the execution companion to:

- `documentation/vidya_os_transformation_implementation_plan.md`

Use it to control sequencing, evidence, and completion criteria across the full
program.

## Overall Status

- Program started: yes
- Active phase: `Complete`
- Sequence locked: yes
- WhatsApp-first shortcut approved: no

Done when:

- Phase 0 is implemented and verified
- Phase 1 is implemented and verified
- Phase 2 is implemented and verified
- Phase 3 is implemented and verified
- Phase 4 is implemented and verified

## Program Guardrails

- [x] Use `documentation/vidya_os_transformation_implementation_plan.md` as source of truth
- [x] Keep execution sequential:
  - `Phase 0 -> Phase 1 -> Phase 2 -> Phase 3 -> Phase 4`
- [x] Do not front-load WhatsApp interfaces ahead of core data stabilization
- [x] Record migration strategy before any Phase 1 schema change touching existing rows
- [x] Confirm canonical background execution runtime before expanding automation-heavy work
- [x] Keep verification evidence updated per phase

## Phase 0: Critical Stability Fixes

Goal:

- prevent concurrency-sensitive paths from degrading auth, tenant middleware, or review flows

Checklist:

- [x] Audit `backend/auth/oauth.py` for blocking Google/auth request paths
- [x] Move blocking auth IO off the event loop safely
- [x] Audit `backend/middleware/tenant.py` for repeated JWT decode / tenant-resolution work
- [x] Add bounded TTL/LRU caching without weakening tenant safety
- [x] Audit `_sm2_update()` path in `backend/src/domains/academic/application/student_reviews.py`
- [x] Decouple write-heavy SM-2 persistence from the main request path where safe
- [x] Document queue/runtime dependency for any new deferred review writes

Verification:

- [x] `backend/tests/test_openai_compat.py`
- [x] `backend/tests/test_sm2_algorithm.py`
- [x] targeted concurrency/load verification for OAuth
- [x] targeted concurrency/load verification for review completion

Done when:

- auth flow is non-blocking under concurrent load
- tenant middleware avoids redundant heavy JWT work
- review completion no longer depends on row-lock-heavy synchronous persistence

Evidence:

- `backend/auth/oauth.py` verified to offload Google token verification through `asyncio.to_thread(...)`
- `backend/middleware/tenant.py` hardened with a thread-safe bounded JWT payload cache plus explicit cache reset support for tests
- `backend/src/domains/academic/application/student_reviews.py` moved deferred mastery writes onto a bounded executor and now requires a fresh DB session factory for off-request work
- `backend/src/domains/academic/routes/students.py` passes `SessionLocal` into review completion so deferred writes never reuse the request session across threads
- added `backend/tests/test_phase0_stability.py` to cover OAuth offload, JWT cache reuse, deferred review submission, and route wiring
- verification run:
  - `python -m pytest -q -p no:cacheprovider backend/tests/test_phase0_stability.py backend/tests/test_tenant_middleware.py backend/tests/test_sm2_algorithm.py backend/tests/test_security_regressions.py`
  - `python -m pytest -q -p no:cacheprovider backend/tests/test_openai_compat.py backend/tests/test_sm2_algorithm.py backend/tests/test_phase0_stability.py`

Runtime note:

- Phase 0 deferred review work uses a local bounded `ThreadPoolExecutor` as an interim safety improvement
- Canonical worker/runtime selection remains a program-level prerequisite before Phase 3 automation-heavy delivery

## Phase 1: Core Platform

Goal:

- establish the shared data and permission layer required for the rest of the program

Checklist:

- [x] Unify learner record contract around `backend/src/domains/academic/models/student_profile.py`
- [x] Align attendance, performance, and parent linkage with the unified learner profile
- [x] Enforce role boundaries globally through auth/dependency and route entry points
- [x] Normalize fee, batch/class, and tenant ownership under strict multi-tenant rules
- [x] Define durable assessment registry and lifecycle around test series, marks, and async grading
- [x] Prepare migration scripts for any schema changes touching existing rows
- [x] Prepare rollback notes for any migration that changes live structures

Verification:

- [x] targeted backend tests for learner profile, tenant isolation, fee/class ownership, and assessment flows
- [x] seed/demo verification after migrations
- [x] route-level authorization regression checks

Done when:

- parent, teacher, and admin surfaces can rely on the same student record contract
- RBAC is consistent across route boundaries
- assessment lifecycle is stable enough for automation and analytics phases

Current progress:

- added learner-profile placement and guardian-link fields in `backend/src/domains/academic/models/student_profile.py`
- added live profile-sync hooks for parent linking, admissions, and CSV onboarding via `backend/src/domains/academic/services/student_profile_sync.py`
- extended `backend/src/domains/academic/services/student_profile_sync.py` to aggregate live attendance totals, attendance percentage, absent streak, overall score, strongest/weakest subject, and subject score map from existing academic tables
- tightened multi-tenant uniqueness in `backend/src/domains/academic/models/parent_link.py`, `backend/src/domains/academic/models/core.py`, and `backend/src/domains/academic/models/batch.py`
- added invoice/payment guard rails in `backend/src/domains/administrative/models/fee.py`
- added explicit assessment lifecycle fields in `backend/src/domains/academic/models/test_series.py`
- fixed `backend/models.py` so the canonical fresh-database model registry now includes the Phase 1 batch, fee, admission, and student-profile tables
- added `backend/tests/test_phase1_core_platform.py` as the first Phase 1 contract-verification slice
- added `backend/tests/test_phase1_student_profile_sync.py` to verify unified learner-profile synchronization from live enrollment, guardian-link, attendance, and subject-performance workflows
- hardened `backend/src/domains/administrative/routes/fees.py` so malformed UUID inputs fail with explicit `400` responses instead of leaking `500` route errors
- hardened `backend/src/domains/platform/routes/personalization.py` so student-only endpoints now enforce explicit `403` role boundaries through `require_role("student")`
- added `backend/tests/test_phase1_route_boundaries.py` to lock fee-route identifier validation and student-only personalization access rules
- expanded `backend/alembic/versions/20260406_0015_phase1_core_platform_contracts.py` so existing databases gain the missing `student_profiles` table and Phase 1 assessment columns during startup migration
- added `backend/tests/test_phase1_migration_rollout.py` to verify the real `db_migrate.run_migrations()` upgrade path from a pre-0015 existing schema
- hardened `backend/src/domains/administrative/services/fee_management.py` and `backend/src/domains/administrative/routes/fees.py` so fee structures cannot attach to classes owned by a different tenant
- hardened `backend/src/domains/academic/application/teacher_reporting.py` and `backend/src/domains/academic/routes/teacher.py` so created test series validate class and subject tenant ownership, reject subject/class mismatches, and publish with explicit lifecycle defaults
- hardened `backend/src/domains/academic/application/student_engagement.py` so mock-test submission enforces UUID validity, mark bounds, publication/open/close lifecycle gates, and safe timezone-normalized comparisons
- added `backend/tests/test_phase1_runtime_contracts.py` to verify cross-tenant fee rejection, assessment publication defaults, subject/class mismatch rejection, and student submission lifecycle enforcement
- hardened `backend/src/interfaces/rest_api/ai/routes/discovery.py` so teacher/admin discovery and ingestion routes enforce shared `require_role("teacher", "admin")` gates at the dependency layer
- hardened `backend/src/domains/platform/routes/whatsapp.py` and `backend/src/domains/platform/routes/mascot.py` so admin-only operational endpoints enforce shared `require_role("admin")` gates instead of ad hoc inline checks
- expanded `backend/tests/test_phase1_route_boundaries.py` to verify AI discovery, WhatsApp admin, and mascot admin endpoints reject unauthorized roles consistently with `403`
- updated `backend/seed_cbse_demo.py` so the canonical demo bootstrap now materializes `student_profiles` through `sync_student_profile_context(...)` instead of leaving the Phase 1 learner contract empty after seeding
- updated `backend/db_migrate.py` so `ensure_db_ready()` now fails if canonical seed bootstrapping fails instead of silently returning migration-only success
- added `backend/tests/test_phase1_seed_bootstrap.py` to verify the real fresh-database startup path creates schema, runs canonical demo seeding, and leaves a populated unified `student_profiles` record
- recorded migration and rollback strategy in `documentation/vidya_os_phase1_migration_strategy.md`
- verification run:
  - `python -m pytest -q -p no:cacheprovider backend/tests/test_phase1_core_platform.py backend/tests/test_fee_management.py`
  - `python -m pytest -q -p no:cacheprovider backend/tests/test_openai_compat.py backend/tests/test_sm2_algorithm.py backend/tests/test_phase0_stability.py backend/tests/test_phase1_core_platform.py backend/tests/test_fee_management.py`
  - `python -m pytest -q -p no:cacheprovider backend/tests/test_phase1_student_profile_sync.py backend/tests/test_phase1_core_platform.py backend/tests/test_fee_management.py`
  - `python -m pytest -q -p no:cacheprovider backend/tests/test_openai_compat.py backend/tests/test_sm2_algorithm.py backend/tests/test_phase0_stability.py backend/tests/test_phase1_core_platform.py backend/tests/test_phase1_student_profile_sync.py backend/tests/test_fee_management.py`
  - `python -m pytest -q -p no:cacheprovider backend/tests/test_phase1_route_boundaries.py backend/tests/test_personalization_learning.py backend/tests/test_fee_management.py`
  - `python -m pytest -q -p no:cacheprovider backend/tests/test_phase0_stability.py backend/tests/test_phase1_core_platform.py backend/tests/test_phase1_student_profile_sync.py backend/tests/test_phase1_route_boundaries.py backend/tests/test_fee_management.py backend/tests/test_personalization_learning.py`
  - `python -m pytest -q -p no:cacheprovider backend/tests/test_phase1_student_profile_sync.py`
  - `python -m pytest -q -p no:cacheprovider backend/tests/test_phase1_core_platform.py backend/tests/test_phase1_student_profile_sync.py backend/tests/test_phase1_route_boundaries.py backend/tests/test_fee_management.py backend/tests/test_personalization_learning.py`
  - `python -m pytest -q -p no:cacheprovider backend/tests/test_phase1_migration_rollout.py`
  - `python -m pytest -q -p no:cacheprovider backend/tests/test_phase1_core_platform.py backend/tests/test_phase1_student_profile_sync.py backend/tests/test_phase1_route_boundaries.py backend/tests/test_phase1_migration_rollout.py backend/tests/test_fee_management.py backend/tests/test_personalization_learning.py`
  - `python -m pytest -q -p no:cacheprovider backend/tests/test_phase1_runtime_contracts.py backend/tests/test_fee_management.py backend/tests/test_phase1_route_boundaries.py backend/tests/test_phase1_migration_rollout.py backend/tests/test_personalization_learning.py`
  - `python -m pytest -q -p no:cacheprovider backend/tests/test_phase1_core_platform.py backend/tests/test_phase1_student_profile_sync.py backend/tests/test_phase1_runtime_contracts.py backend/tests/test_phase1_route_boundaries.py backend/tests/test_phase1_migration_rollout.py backend/tests/test_fee_management.py backend/tests/test_personalization_learning.py`
  - `python -m pytest -q -p no:cacheprovider backend/tests/test_phase1_route_boundaries.py backend/tests/test_personalization_learning.py`
  - `python -m pytest -q -p no:cacheprovider backend/tests/test_phase1_seed_bootstrap.py backend/tests/test_phase1_migration_rollout.py`
  - `python -m pytest -q -p no:cacheprovider backend/tests/test_phase1_core_platform.py backend/tests/test_phase1_student_profile_sync.py backend/tests/test_phase1_runtime_contracts.py backend/tests/test_phase1_route_boundaries.py backend/tests/test_phase1_migration_rollout.py backend/tests/test_phase1_seed_bootstrap.py backend/tests/test_fee_management.py backend/tests/test_personalization_learning.py`
  - `$env:PYTHONDONTWRITEBYTECODE='1'; python -m compileall -q backend`

## Phase 2: India-First Experience and Localization

Goal:

- make the product resilient on low-cost hardware and lower-bandwidth connections

Checklist:

- [x] Reduce heavy operational-surface aesthetics where they tax low-end devices
- [x] Move language preference to server-readable cookie flow
- [x] Eliminate first-paint flash-of-English content
- [x] Expand adaptive loading rules around constrained connections
- [x] Ensure optional visuals degrade without harming core workflows

Verification:

- [x] localized first-paint check under Hindi or other vernacular setting
- [x] Fast 3G simulation review in DevTools
- [x] frontend lint/build after localization changes
- [x] representative UI regression for reduced asset mode / constrained networks

Done when:

- localized HTML is correct on first paint
- constrained-network users do not pay unnecessary visual/runtime cost
- operational pages stay readable and responsive on low-end devices

Current progress:

- moved the language contract to a shared server-readable cookie in `frontend/src/i18n/config.ts`
- updated `frontend/src/app/layout.tsx` to read the initial language from `next/headers` cookies and emit the correct `<html lang>` value on first render
- rebuilt `frontend/src/i18n/LanguageProvider.tsx` around a server-seeded initial language so client hydration no longer depends on `localStorage` for the first paint
- updated `frontend/src/components/prism/PrismHeroScene.tsx` to disable the interactive 3D hero on slow connections and data-saver mode while keeping the landing layout intact
- expanded adaptive connection behavior in `frontend/src/app/admin/queue/page.tsx`, `frontend/src/app/teacher/discover/page.tsx`, and `frontend/src/app/student/tools/page.tsx` so polling cadence falls back on slower networks
- trimmed `frontend/src/app/student/leaderboard/page.tsx` to a reduced-visual mode for slow connections by suppressing heavier gradient, animation, and shadow treatments
- added browser verification in `frontend/tests/e2e/prism-runtime-qa.spec.ts` for first-paint Hindi cookie rendering, Fast 3G landing stability, constrained-network landing fallback, and admin queue polling backoff
- verification run:
  - `frontend> npm run lint`
  - `frontend> npm run build`
  - `frontend> node_modules\.bin\playwright.cmd test tests/e2e/prism-runtime-qa.spec.ts`

## Phase 3: Automation and Trust Layer

Goal:

- introduce auditable teacher and parent automation on top of stable data/runtime foundations

Checklist:

- [x] Implement parent WhatsApp reminders through the shared delivery path
- [x] Implement teacher WhatsApp assistant intents for attendance / lesson workflows
- [x] Route OCR-driven grading into async reviewable AI grading flow
- [x] Centralize outbound email/SMS/WhatsApp into one notification event path
- [x] Preserve audit history for parent communications
- [x] Verify worker/runtime support for all new deferred automation

Verification:

- [x] targeted backend tests for WhatsApp gateway and notification dispatch
- [x] targeted grading queue / review dashboard tests
- [x] audit-log verification for outbound communication events
- [x] user-visible flow checks for teacher and parent automation entry points

Done when:

- outbound communication is auditable
- teacher automation is permission-safe
- AI grading is reviewable and not silently final

Current progress:

- fixed `backend/src/domains/platform/services/notification_dispatch.py` so the shared dispatcher no longer creates a duplicate in-app `Notification` row after channel dispatch
- promoted shared notification event serialization/push helpers in `backend/src/domains/platform/services/notifications.py` so already-persisted in-app events can be pushed to subscribers without a second DB write
- added `backend/src/domains/platform/services/background_runtime.py` as the local bounded runtime for deferred automation coroutines in non-request contexts
- updated `backend/src/shared/ai_tools/whatsapp_teacher_tools.py` so teacher attendance reminders enqueue onto the local background runtime instead of using ad hoc `loop.create_task(...)`
- confirmed `backend/src/domains/academic/services/attendance_notifier.py` already routes parent absence reminders through `dispatch_notification(...)`, preserving channel-level audit metadata in `notifications`
- hardened `backend/src/domains/platform/routes/whatsapp.py` so the admin-only tool-catalog route still rejects non-admin callers when invoked directly in tests
- added `backend/tests/test_phase3_automation_trust.py` to verify one-row-per-channel dispatch, auditable parent attendance reminder records, the local automation runtime, and teacher attendance tool runtime submission
- extended `backend/src/domains/academic/routes/teacher.py` and `backend/src/domains/academic/application/teacher_reporting.py` so `/teacher/ai-grade` can carry exam, student, answer-key, and rubric context into the queued grading job
- updated `backend/src/domains/platform/services/ai_grading.py` so AI grading returns an explicit teacher-review draft contract (`draft_ready` / `manual_review_required`) with `finalized: false` and a proposed mark instead of implying that marks were silently finalized
- updated `backend/src/domains/platform/services/ai_queue.py` so completed or failed AI grading jobs notify the teacher in-app with draft-review metadata tied to the queued job
- added `backend/tests/test_phase3_ai_grading_review_flow.py` to verify queued grading request context, non-final teacher-review draft results, and queue-driven teacher notifications for grading drafts
- extended `backend/src/domains/platform/services/mascot_registry.py`, `backend/src/domains/platform/services/mascot_schemas.py`, and `backend/src/domains/platform/services/mascot_orchestrator.py` so the live mascot/WhatsApp runtime now supports confirmation-gated teacher attendance marking and homework creation flows instead of leaving those actions outside the actual bot path
- updated `backend/src/domains/platform/routes/whatsapp.py` so linked admin manual text sends route through `dispatch_notification(...)` rather than bypassing the audited notification contract
- updated `backend/src/domains/platform/services/notification_dispatch.py` so successful WhatsApp deliveries logged through the notification bus also land in `whatsapp_messages`, keeping notification audit and WhatsApp operational analytics aligned
- added user-visible verification coverage in `backend/tests/test_mascot_routes.py` for teacher attendance marking and homework creation confirmation flows, and in `backend/tests/test_whatsapp_gateway.py` for linked admin manual sends through the notification dispatcher
- verification run:
  - `python -m pytest -q -p no:cacheprovider backend/tests/test_phase3_automation_trust.py backend/tests/test_notifications.py backend/tests/test_whatsapp_gateway.py backend/tests/test_phase1_route_boundaries.py backend/tests/test_personalization_learning.py`
  - `python -m pytest -q -p no:cacheprovider backend/tests/test_phase3_ai_grading_review_flow.py backend/tests/test_ocr_integration.py backend/tests/test_ai_queue.py`
  - `python -m pytest -q -p no:cacheprovider backend/tests/test_mascot_routes.py -k "teacher_attendance_mark or teacher_homework_create"`
  - `python -m pytest -q -p no:cacheprovider backend/tests/test_whatsapp_gateway.py -k "AdminManualSend or ToolCatalogEndpoint"`
  - `$env:PYTHONDONTWRITEBYTECODE='1'; python -m compileall -q backend`

## Phase 4: Intelligence Layer

Goal:

- convert unified operational and academic data into real institutional intelligence

Checklist:

- [x] Expand telemetry ingestion into analyzable event structures
- [x] Implement daily risk-flag scanning on unified records
- [x] Surface academic decline / fee risk alerts visibly
- [x] Upgrade the student mastery experience from coarse overview to sub-topic signal
- [x] Ensure analytics are powered by real underlying records, not demo-only placeholders

Verification:

- [x] targeted backend tests for telemetry ingestion and risk computation
- [x] alert generation verification across real record paths
- [x] frontend mastery visualization validation
- [x] representative admin/principal intelligence workflow checks

Done when:

- operators get real actionable alerts from unified records
- mastery map reflects real sub-topic signal
- intelligence surfaces are backed by stable data, not mocked assumptions

Current progress:

- added `backend/src/domains/platform/models/analytics_event.py` as the warehouse-friendly analytics event contract, then registered it through `backend/src/domains/platform/models/__init__.py` and `backend/models.py` so canonical startup and tests see the new table
- added `backend/alembic/versions/20260406_0016_create_analytics_events_table.py` to create the `analytics_events` table with tenant, user, event-family, surface, target, channel, event-date, and occurrence indexes
- extended `backend/src/domains/platform/services/telemetry_events.py` so `record_business_event(...)` now persists structured analytics rows while still emitting log and trace events
- extended `backend/src/domains/platform/services/metrics_registry.py` so `observe_personalization_event(...)` can bridge in-process counters into persistent analytics rows when tenant and user context is available
- updated `backend/src/domains/platform/routes/personalization.py` so recommendation, study-path, and explicit personalization event flows now write warehouse-friendly analytics rows with real tenant, user, and channel context
- updated `backend/src/domains/academic/routes/students.py` so mastery-outcome personalization metrics now persist topic-aware analytics events instead of remaining process-local counters only
- verified telemetry persistence directly in `backend/tests/test_phase4_telemetry_ingestion.py`
- verified route-level personalization analytics persistence and metrics behavior through `backend/tests/test_personalization_learning.py` and `backend/tests/test_metrics_registry.py`
- rebuilt `backend/src/domains/academic/services/risk_cron.py` so the daily risk scan now computes dropout, academic, and fee risk from unified profile fields plus live overdue invoices, stamps each profile with `last_computed_at`, and emits `student_risk_recomputed` analytics events for every scanned learner
- added `backend/tests/test_phase4_risk_cron.py` to verify high-risk and medium-risk classification, per-tenant scan scoping, profile updates, and persisted risk telemetry rows
- extended `backend/src/domains/administrative/application/dashboard.py` so the admin dashboard now exposes `student_risk_summary` and a ranked `student_risk_alerts` list from live `student_profiles` records joined to real student and class data
- added `backend/tests/test_phase4_admin_dashboard_alerts.py` to verify the admin dashboard exposes visible academic/attendance/fee risk alerts from real dashboard data, not mock-only placeholders
- updated `frontend/src/app/admin/dashboard/page.tsx` so `/admin/dashboard` now renders a `Student Risk Radar` panel with institution-level counts and a ranked intervention list for high/medium-risk learners
- updated `frontend/tests/e2e/admin-dashboard.spec.ts`, `frontend/tests/e2e/visual-smoke.spec.ts`, and `frontend/tests/e2e/prism-responsive.spec.ts` so the admin dashboard browser contract includes the new risk payload and visible alert surface
- added `backend/src/domains/academic/application/student_learning_insights.py::build_student_mastery_map(...)` so the student mastery surface is now derived from real `student_profiles` and `topic_mastery` rows, including subject-level radar values, due-review counts, and concept-level sub-topic signal
- exposed the live mastery contract through `/api/student/mastery` in `backend/src/domains/academic/routes/students.py` and `api.student.mastery()` in `frontend/src/lib/api.ts`
- replaced the mock-only `frontend/src/app/student/mastery/page.tsx` with a live Prism intelligence surface backed by the new mastery contract
- added `backend/tests/test_phase4_student_mastery_map.py` to verify the mastery endpoint returns persisted profile, subject, topic, concept, and recommendation data from real rows
- added `frontend/tests/e2e/student-mastery.spec.ts` to verify the browser contract for the student mastery page renders real sub-topic signal
- verification run:
  - `python -m pytest -q -p no:cacheprovider backend/tests/test_phase4_telemetry_ingestion.py backend/tests/test_personalization_learning.py backend/tests/test_metrics_registry.py`
  - `python -m pytest -q -p no:cacheprovider backend/tests/test_phase4_risk_cron.py backend/tests/test_phase4_telemetry_ingestion.py backend/tests/test_personalization_learning.py backend/tests/test_metrics_registry.py`
  - `python -m pytest -q -p no:cacheprovider backend/tests/test_phase4_admin_dashboard_alerts.py backend/tests/test_phase4_risk_cron.py backend/tests/test_phase4_telemetry_ingestion.py`
  - `python -m pytest -q -p no:cacheprovider backend/tests/test_phase4_student_mastery_map.py backend/tests/test_phase4_admin_dashboard_alerts.py backend/tests/test_phase4_risk_cron.py backend/tests/test_phase4_telemetry_ingestion.py`
  - `frontend> npm run lint`
  - `frontend> npm run build`
  - `frontend> node_modules\.bin\playwright.cmd test tests/e2e/admin-dashboard.spec.ts`
  - `frontend> node_modules\.bin\playwright.cmd test tests/e2e/student-mastery.spec.ts`
  - `$env:PYTHONDONTWRITEBYTECODE='1'; python -m compileall -q backend`

## Evidence Log

- [x] Phase 0 evidence captured
- [x] Phase 1 evidence captured
- [x] Phase 2 evidence captured
- [x] Phase 3 evidence captured
- [x] Phase 4 evidence captured

## Final Closure

- [x] All five phases complete
- [x] Program verification complete
- [x] `task.md` updated to reflect full completion
