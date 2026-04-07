# Prism Execution Checklist

This checklist is the operational companion to
`documentation/prism_immersive_redesign_contract.md`.

It formalizes the staged rollout for the full-product immersive redesign and
anchors each route-group pass to the local design workflow repository:

- `C:\Users\naren\Work\Forks\design-plugin`

The design-plugin is used for variant generation and decision support. The
approved implementation is committed only in this application repo.

## Overall Status

- Implementation status: complete
- Shared Prism system rollout status: complete
- Automated QA status: complete
- Checklist status: not fully closed

Done when:

- the current implementation, QA, and retrospective documentation remain green
- and either:
  - a fresh design-plugin cycle is run and recorded for the route groups, or
  - the team accepts the existing retrospective refinement log as sufficient closure for Phase 8

Remaining strict-process gaps:

- fresh `design-plugin` variant generation and `/__design_lab` review evidence
- explicit fresh-cycle direction lock from that new run
- route-level manual visual QA remains stricter than the representative automated responsive and visual smoke already captured

## Phase 0: Guardrails

- [x] Confirm shared shell is authoritative:
  - `frontend/src/app/globals.css`
  - `frontend/src/app/layout.tsx`
  - `frontend/src/components/prism/PrismPage.tsx`
- [x] Keep backend/API contracts frozen during UI work
- [x] Keep route contracts frozen during UI work
- [x] Maintain one visual contract:
  - `documentation/prism_immersive_redesign_contract.md`
- [x] Require `npm run lint` after each route-group pass
- [x] Require `npm run build` after each route-group pass

## Phase 1: Foundation System

- [x] Finalize tokens for:
  - color
  - radius
  - shadow
  - spacing
  - typography
- [x] Finalize shared primitives:
  - page shell
  - section shell
  - panels
  - buttons
  - empty states
  - skeletons
- [x] Establish selective 3D policy
- [x] Add ambient backdrop and public hero scene
- [x] Finish shared table/form/dialog primitives

## Phase 2: Public Funnel

- [x] `/`
- [x] `/demo`
- [x] `/login`
- [x] `/qr-login`

Checklist:

- [x] Hero hierarchy is strong
- [x] CTA path is clear
- [x] Demo role cards feel curated
- [x] Login and QR login align with the same visual language
- [x] Empty and loading states are polished
- [x] Mobile layouts remain clean
- [x] Auth flow behavior is preserved

## Phase 3: Student Experience

Priority routes:

- [x] `/student/ai-studio`
- [x] `/student/overview`
- [x] `/student/assignments`
- [x] `/student/results`
- [x] `/student/mind-map`
- [x] `/student/tools`
- [x] `/student/upload`
- [x] `/student/reviews`

Per-route checklist:

- [x] Strong learning-oriented top section
- [x] Clear zone separation:
  - overview
  - action
  - insight
  - detail
- [x] Replace ad hoc local surfaces with Prism panels where appropriate
- [x] Improve cards, filters, forms, and empty states
- [x] Preserve data flow and actions
- [ ] Validate mobile behavior
- [x] Re-run lint/build

### Phase 3A: Student AI Studio

- [x] Add route-level Prism top section
- [x] Reframe workspace as a deep-work shell
- [x] Redesign tool rail to match Prism
- [x] Redesign notebook selector to match Prism
- [x] Redesign context panel to match Prism
- [x] Redesign center thread/composer surface to match Prism
- [ ] Visual QA on desktop/tablet/mobile
- [x] Re-run lint/build

### Phase 3B: Student Assignments

- [x] Add route-level Prism top section
- [x] Reframe the page around action, submission, and outcomes
- [x] Upgrade status filters to match Prism
- [x] Redesign assignment cards and grade presentation
- [x] Improve OCR warning presentation
- [x] Preserve upload and helper actions
- [ ] Visual QA on desktop/tablet/mobile
- [x] Re-run lint/build

### Phase 3C: Student Results

- [x] Add route-level Prism top section
- [x] Reframe the page around academic narrative and outcome clarity
- [x] Upgrade summary metrics to match Prism
- [x] Separate trend analysis from subject breakdown
- [x] Improve empty/error/loading states
- [x] Preserve result and trend fetch behavior
- [ ] Visual QA on desktop/tablet/mobile
- [x] Re-run lint/build

### Phase 3D: Student Mind Map

- [x] Add route-level Prism top section
- [x] Reframe the page around spatial learning and concept navigation
- [x] Upgrade generation controls to match Prism
- [x] Elevate the canvas into a dedicated workspace surface
- [x] Improve loading and error handling
- [x] Preserve generation, pan, and zoom behavior
- [ ] Visual QA on desktop/tablet/mobile
- [x] Re-run lint/build

### Phase 3E: Student Tools

- [x] Add route-level Prism top section
- [x] Reframe the page around creation, saved assets, and output review
- [x] Upgrade tool selection cards to match Prism
- [x] Redesign the prompt builder and output workspace
- [x] Improve library presentation and empty states
- [x] Preserve generation, polling, and library reuse behavior
- [ ] Visual QA on desktop/tablet/mobile
- [x] Re-run lint/build

### Phase 3F: Student Upload

- [x] Add route-level Prism top section
- [x] Reframe the page around intake, processing, and next actions
- [x] Upgrade the dropzone and OCR framing to match Prism
- [x] Redesign upload activity and uploaded-file surfaces
- [x] Improve empty/error states and post-upload transitions
- [x] Preserve file upload, OCR, refresh, and study handoff behavior
- [ ] Visual QA on desktop/tablet/mobile
- [x] Re-run lint/build

### Phase 3G: Student Reviews

- [x] Add route-level Prism top section
- [x] Reframe the page around due reviews, upcoming reviews, and topic creation
- [x] Upgrade review metrics and due-card hierarchy to match Prism
- [x] Improve empty/error/loading states
- [x] Preserve review creation and SM-2 completion behavior
- [ ] Visual QA on desktop/tablet/mobile
- [x] Re-run lint/build

## Phase 4: Teacher Experience

- [x] `/teacher/dashboard`
- [x] `/teacher/attendance`
- [x] `/teacher/marks`
- [x] `/teacher/assignments`
- [x] `/teacher/generate-assessment`
- [x] `/teacher/insights`
- [x] `/teacher/discover`
- [x] `/teacher/upload`

Checklist:

- [x] Workflow speed remains intact
- [x] Data-entry hierarchy improves
- [x] Insight surfaces gain clearer emphasis
- [x] Shared table/filter/action styling is consistent
- [x] No workflow regression

## Phase 5: Admin Experience

- [x] `/admin/dashboard`
- [x] `/admin/setup-wizard`
- [x] `/admin/reports`
- [x] `/admin/queue`
- [x] `/admin/traces`
- [x] `/admin/security`
- [x] `/admin/branding`
- [x] `/admin/users`
- [x] `/admin/timetable`

Checklist:

- [x] Density is more scannable
- [x] Monitoring screens have explicit priority zones
- [x] Setup wizard feels guided rather than form-heavy
- [x] Governance/configuration stays subtle and controlled
- [x] No operational regression

## Phase 6: Parent Experience

- [x] `/parent/dashboard`
- [x] `/parent/attendance`
- [x] `/parent/results`
- [x] `/parent/reports`
- [x] `/parent/assistant`

Checklist:

- [x] Progress storytelling is clearer
- [x] Cards feel supportive, not technical
- [x] Assistant surface matches the system
- [x] No routing or state regression

## Phase 7: Cross-Cutting States

- [x] empty states
- [x] error states
- [x] skeletons
- [x] toasts
- [x] dialogs
- [x] drawers
- [x] tabs
- [x] filters
- [x] search bars
- [x] pagination
- [x] standardize table styling across personas
- [x] standardize form field styling across personas
- [x] standardize intros and section headers across personas

## Phase 8: Plugin-Guided Refinement

For each route group:

- [ ] Use `C:\Users\naren\Work\Forks\design-plugin`
- [ ] Generate multiple variations
- [ ] Review in design lab
- [ ] Choose one direction
- [x] Record accepted direction in repo docs
- [ ] Avoid committing temporary plugin artifacts

## Phase 9: QA and Performance

- [x] `npm run lint`
- [x] `npm run build`
- [x] Verify desktop/tablet/mobile layouts
- [x] Verify reduced-motion behavior
- [x] Verify no-WebGL fallback for selective 3D surfaces
- [x] Verify no broken navigation
- [x] Verify key role flows still work
- [x] Update targeted Playwright coverage

Automated QA completed:

- [x] Runtime safeguards:
  - landing reduced-motion behavior
  - landing no-WebGL fallback
- [x] Behavioral smoke:
  - `/`
  - `/student/upload`
  - `/student/tools`
- [x] Targeted teacher workflow regression:
  - `/teacher/attendance`
  - `/teacher/marks`
  - `/teacher/assignments`
  - `/teacher/generate-assessment`
  - `/teacher/insights`
  - `/teacher/discover`
  - `/teacher/upload`
- [x] Targeted admin workflow regression:
  - `/admin/setup-wizard`
  - `/admin/reports`
  - `/admin/queue`
  - `/admin/traces`
  - `/admin/security`
  - `/admin/branding`
  - `/admin/users`
  - `/admin/timetable`
- [x] Targeted parent workflow regression:
  - `/parent/dashboard`
  - `/parent/attendance`
  - `/parent/results`
  - `/parent/reports`
  - `/parent/assistant`
- [x] Representative visual smoke:
  - `/`
  - `/demo`
  - `/login`
  - `/student/ai-studio`
  - `/teacher/dashboard`
  - `/admin/dashboard`
  - `/parent/dashboard`
- [x] Representative responsive smoke:
  - mobile:
    - `/`
    - `/parent/dashboard`
  - tablet:
    - `/student/ai-studio`
    - `/admin/dashboard`
  - desktop:
    - `/teacher/dashboard`
