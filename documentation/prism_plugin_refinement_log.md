# Prism Plugin Refinement Log

This log records route-group refinement decisions using the local design
workflow repository:

- `C:\Users\naren\Work\Forks\design-plugin`

The plugin is a workflow tool, not a shipped dependency. Its documented process
is:

1. start a pass with `/design-and-refine:start [target]`
2. generate multiple variants against the live codebase
3. review them side-by-side at `/__design_lab`
4. synthesize an approved direction
5. finalize with `DESIGN_PLAN.md` while temporary lab artifacts are cleaned up

This application repo keeps the approved implementation and the route-group
decision record below. Temporary design-lab artifacts are intentionally not
committed.

## Public Route Group

- Status: implemented in app repo; retrospective decision captured
- Plugin source: `C:\Users\naren\Work\Forks\design-plugin`
- Representative routes:
  - `/`
  - `/demo`
  - `/login`
  - `/qr-login`
- Decision date: `2026-04-06`

### Accepted Direction

- Approved direction:
  - flagship immersive landing
  - curated demo role selection
  - premium but clear auth shell
- Why it won:
  - strongest first-impression upgrade
  - lets selective 3D stay concentrated on the public hero
  - keeps auth flows operationally simple
- Rejected tradeoffs:
  - no persistent WebGL outside the landing hero
  - no theatrical motion on login or QR login

### Implementation Notes

- Shared primitives touched:
  - `PrismPage`
  - `PrismPanel`
  - `PrismHeroScene`
  - shared globals/tokens in `frontend/src/app/globals.css`
- Business logic intentionally preserved:
  - auth behavior
  - route contracts
  - demo role switching

### Verification

- `npm run lint`
- `npm run build`
- Representative visual smoke:
  - `/`
  - `/demo`
  - `/login`

## Student Route Group

- Status: implemented in app repo; retrospective decision captured
- Plugin source: `C:\Users\naren\Work\Forks\design-plugin`
- Representative routes:
  - `/student/ai-studio`
  - `/student/assignments`
  - `/student/results`
  - `/student/mind-map`
  - `/student/tools`
  - `/student/upload`
  - `/student/reviews`
- Decision date: `2026-04-06`

### Accepted Direction

- Approved direction:
  - learning-product flagship treatment
  - strongest 2.5D depth on AI Studio and mind map
  - clearer academic narrative on assignments, results, and reviews
- Why it won:
  - keeps student flows feeling premium without slowing study actions
  - gives AI surfaces more depth while preserving task clarity
  - makes uploads, results, and reviews easier to scan
- Rejected tradeoffs:
  - no dense dashboard theatrics inside operational study flows
  - no data-flow rewrites just to support layout changes

### Implementation Notes

- Shared primitives touched:
  - `PrismPage`
  - `PrismPanel`
  - `PrismPageIntro`
  - `PrismSectionHeader`
  - `PrismControls`
- Business logic intentionally preserved:
  - upload and OCR flow
  - AI Studio thread and notebook behavior
  - results and trend fetch behavior
  - review creation and SM-2 completion

### Verification

- `npm run lint`
- `npm run build`
- Smoke coverage:
  - `/student/upload`
  - `/student/tools`
- Representative visual smoke:
  - `/student/ai-studio`

## Teacher Route Group

- Status: implemented in app repo; retrospective decision captured
- Plugin source: `C:\Users\naren\Work\Forks\design-plugin`
- Representative routes:
  - `/teacher/attendance`
  - `/teacher/marks`
  - `/teacher/assignments`
  - `/teacher/generate-assessment`
  - `/teacher/insights`
  - `/teacher/discover`
  - `/teacher/upload`
- Decision date: `2026-04-06`

### Accepted Direction

- Approved direction:
  - premium educator workspace
  - stronger distinction between action, insight, and generation surfaces
  - polished data-entry and content-creation framing
- Why it won:
  - preserves speed on classroom operations
  - improves hierarchy on marks, attendance, and assignments
  - gives assessment, discover, and upload surfaces a more intentional flow
- Rejected tradeoffs:
  - no decorative depth that competes with classroom tasks
  - no backend or payload changes for grading, attendance, or generation

### Implementation Notes

- Shared primitives touched:
  - `PrismPage`
  - `PrismPanel`
  - `PrismPageIntro`
  - `PrismSectionHeader`
  - `PrismControls`
- Business logic intentionally preserved:
  - attendance import and submit flow
  - marks import and submission
  - assignment list/create flow
  - AI job polling for assessment generation
  - search/ingest workflow on discover
  - document, OCR, and YouTube upload flow

### Verification

- `npm run lint`
- `npm run build`
- Targeted Playwright coverage:
  - `teacher-academic-imports.spec.ts`
  - `teacher-assignments.spec.ts`
  - `teacher-generate-assessment.spec.ts`
  - `teacher-discover.spec.ts`
  - `teacher-upload.spec.ts`

## Admin Route Group

- Status: implemented in app repo; retrospective decision captured
- Plugin source: `C:\Users\naren\Work\Forks\design-plugin`
- Representative routes:
  - `/admin/setup-wizard`
  - `/admin/reports`
  - `/admin/queue`
  - `/admin/traces`
  - `/admin/security`
  - `/admin/branding`
  - `/admin/users`
  - `/admin/timetable`
- Decision date: `2026-04-06`

### Accepted Direction

- Approved direction:
  - enterprise-grade hierarchy
  - controlled density on monitoring and governance surfaces
  - clearer command zones for setup, reporting, and operations
- Why it won:
  - makes dense operational pages easier to scan
  - keeps immersion subtle where clarity has to dominate
  - unifies reports, queue, traces, security, and configuration work
- Rejected tradeoffs:
  - no cinematic effects on monitoring pages
  - no route or admin API changes during redesign

### Implementation Notes

- Shared primitives touched:
  - `PrismPage`
  - `PrismPanel`
  - `PrismPageIntro`
  - `PrismSectionHeader`
  - `PrismControls`
  - `PrismOverlays`
- Business logic intentionally preserved:
  - setup wizard OCR preview/import
  - reports generation/export
  - queue cancel/retry/dead-letter actions
  - trace lookup and diagnostics payloads
  - security fetch behavior
  - branding extract/save flow
  - user directory role/activation/guardian linking
  - timetable generation and manual slot controls

### Verification

- `npm run lint`
- `npm run build`
- Targeted Playwright coverage:
  - `ocr-review-flows.spec.ts`
  - `admin-reports.spec.ts`
  - `admin-queue.spec.ts`
  - `admin-traces.spec.ts`
  - `admin-security.spec.ts`
  - `admin-branding.spec.ts`
  - `admin-users.spec.ts`
  - `admin-timetable.spec.ts`

## Parent Route Group

- Status: implemented in app repo; retrospective decision captured
- Plugin source: `C:\Users\naren\Work\Forks\design-plugin`
- Representative routes:
  - `/parent/dashboard`
  - `/parent/attendance`
  - `/parent/results`
  - `/parent/reports`
  - `/parent/assistant`
- Decision date: `2026-04-06`

### Accepted Direction

- Approved direction:
  - calmer, warmer, narrative-first parent experience
  - supportive cards and summary language
  - lighter density than teacher/admin surfaces
- Why it won:
  - keeps family-facing flows easier to read
  - makes progress and attendance more understandable at a glance
  - aligns the assistant with the broader parent shell
- Rejected tradeoffs:
  - no enterprise-style density
  - no mascot or narrative rewrites that alter the existing state flow

### Implementation Notes

- Shared primitives touched:
  - `PrismPage`
  - `PrismPanel`
  - `PrismPageIntro`
  - `PrismSectionHeader`
- Business logic intentionally preserved:
  - dashboard summary and audio behavior
  - attendance/results/report fetches
  - parent assistant route behavior

### Verification

- `npm run lint`
- `npm run build`
- Targeted Playwright coverage:
  - `parent-dashboard.spec.ts`
  - `parent-attendance.spec.ts`
  - `parent-results.spec.ts`
  - `parent-reports.spec.ts`
  - `parent-assistant.spec.ts`

## Remaining Phase 8 Gap

- Direct per-pass variant archives are not stored in this application repo.
- If a fresh refinement cycle is needed, run the plugin again from
  `C:\Users\naren\Work\Forks\design-plugin`, review live variants at
  `/__design_lab`, and append the new accepted direction here.
