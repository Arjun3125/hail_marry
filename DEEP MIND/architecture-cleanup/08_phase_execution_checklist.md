# Phase Execution Checklist

This checklist turns the architecture cleanup plan into an execution tracker. Each phase is split into concrete steps, validation gates, and completion criteria.

## Phase A — Cleanup workspace and governance docs

Status: `completed`

- [x] Create `DEEP MIND/architecture-cleanup/`
- [x] Add audit report
- [x] Add target architecture doc
- [x] Add dependency rules doc
- [x] Add import migration notes
- [x] Add move plan
- [x] Add compatibility shim notes
- [x] Add validation checklist

Validation:
- [x] Cleanup docs exist in version control
- [x] Docs are not part of runtime imports

## Phase B — Non-breaking scaffolding

Status: `completed`

- [x] Create `backend/src/bootstrap/`
- [x] Create `backend/src/interfaces/http/`
- [x] Create `backend/src/interfaces/whatsapp/`
- [x] Create `backend/src/interfaces/workers/`
- [x] Create `backend/src/infrastructure/config/`
- [x] Create `backend/src/infrastructure/db/`
- [x] Create `backend/src/infrastructure/cache/`
- [x] Create `backend/src/infrastructure/llm/`
- [x] Create `backend/src/infrastructure/vector/`
- [x] Create `backend/src/infrastructure/messaging/`
- [x] Create `backend/src/infrastructure/storage/`
- [x] Create `backend/src/infrastructure/observability/`

Validation:
- [x] Backend still imports and starts after scaffolding

## Phase C — Startup and configuration normalization

Status: `in_progress`

- [x] Extract app factory/bootstrap wiring out of `backend/main.py`
- [x] Keep `backend/main.py` as thin entrypoint
- [x] Create root `config/base.yaml`
- [x] Create root `config/dev.yaml`
- [x] Create root `config/staging.yaml`
- [x] Create root `config/prod.yaml`
- [x] Create root `config/test.yaml`
- [x] Load new config root before legacy backend config
- [ ] Remove remaining runtime dependence on legacy config fallback
- [ ] Consolidate startup/config imports fully on bootstrap modules

Validation:
- [x] `python -c "import os; os.chdir('backend'); import main; print(main.app.title)"` works
- [ ] All runtime entrypoints read config through one normalized path

## Phase D — Import-system cleanup

Status: `in_progress`

- [x] Keep `src.*` as canonical cleanup import root
- [x] Add architecture drift guard script
- [x] Wire architecture drift guard into CI
- [x] Remove multiple route-to-route hot spots
- [x] Move more route orchestration to application helpers
- [ ] Audit and remove remaining `sys.path` hacks where safely possible
- [ ] Reduce compatibility-only import shims further
- [ ] Add stronger dependency enforcement for layer boundaries

Validation:
- [x] `python scripts/check_architecture.py` passes
- [ ] no meaningful route-to-route imports remain
- [ ] path-hack usage is materially reduced

## Phase E — Route and service re-homing

Status: `in_progress`

### Router composition
- [x] Identity router composition moved behind cleaned interface layer
- [x] Academic router composition moved behind cleaned interface layer
- [x] Administrative router composition moved behind cleaned interface layer
- [x] Platform router composition moved behind cleaned interface layer
- [x] Demo routing isolated from main platform composition
- [x] AI router composition owned by cleaned AI interface layer

### AI/application extraction
- [x] AI query preparation/personalization extracted to application layer
- [ ] Continue reducing inline orchestration in AI route handlers

### Academic/application extraction
- [x] Student study-tool generation extracted
- [x] Student queued study-tool generation extracted
- [x] Student dashboard response extracted
- [x] Student complaints workflow extracted
- [x] Teacher bulk attendance updates extracted
- [x] Teacher bulk marks updates extracted
- [x] Teacher OCR/CSV attendance import extracted
- [x] Teacher OCR/CSV marks import extracted
- [ ] Continue extracting remaining student routes
- [ ] Continue extracting remaining teacher routes

### Platform/application extraction
- [x] Mascot release-gate slice extracted
- [x] Mascot student suggestions extracted
- [x] Personalization recommendation metrics slice extracted
- [x] Personalization profile/remediation/study-path slice extracted
- [ ] Continue shrinking remaining mascot/platform route branches

### Administrative/application extraction
- [x] Teacher onboarding extracted
- [x] Student onboarding extracted
- [x] Dashboard orchestration extracted
- [x] AI review orchestration extracted
- [x] AI jobs list/detail orchestration extracted
- [x] Complaints orchestration extracted
- [x] Class/subject management extracted
- [x] Timetable CRUD extracted
- [x] Timetable generation extracted
- [x] Webhook lifecycle extracted
- [x] Parent-link lifecycle extracted
- [x] Tenant settings extracted
- [x] Reporting/billing/heatmap extracted
- [x] Security log assembly extracted
- [x] Report card and WhatsApp digest extracted
- [x] CSV export payload generation extracted
- [ ] Continue shrinking remaining admin route branches if any still assemble responses inline

Validation:
- [x] Route slices compile after each extraction
- [x] Architecture guard remains green after each extraction
- [ ] Major route families become consistently thin

## Phase F — Infrastructure separation

Status: `in_progress`

- [x] Create observability adapter package
- [x] Route admin diagnostics through observability adapter
- [x] Route admin usage snapshot through observability adapter
- [x] Create messaging queue adapter package
- [x] Route admin queue metrics through messaging adapter
- [x] Route queue lifecycle/job operations through messaging adapter
- [x] Create webhook delivery adapter
- [x] Route webhook emission through messaging adapter in admin/teacher/AI interfaces
- [ ] Separate DB/session setup into infrastructure DB package
- [ ] Separate cache concerns more fully
- [ ] Separate vector/OCR adapters more fully
- [ ] Separate storage adapters more fully
- [ ] Separate LLM/provider adapters more fully

Validation:
- [x] Infrastructure adapters compile
- [ ] Interface/application modules stop importing lower-level provider internals directly in remaining hotspots

## Phase G — Deployment cleanup

Status: `in_progress`

- [x] Create canonical Dockerfiles under `deploy/docker/`
- [x] Create canonical compose manifests under `deploy/compose/`
- [x] Create canonical nginx config under `deploy/nginx/`
- [x] Create canonical scripts under `deploy/scripts/`
- [x] Convert root demo launchers into compatibility wrappers
- [ ] Reduce root deployment file duplication further
- [ ] Finish documentation alignment to make `deploy/` the sole source of truth

Validation:
- [x] Canonical deployment assets exist under `deploy/`
- [ ] Root deployment wrappers are minimal or removable

## Phase H — Repo cleanup and compatibility reduction

Status: `in_progress`

- [x] Remove unreachable legacy heatmap body in admin route
- [x] Remove unreachable legacy billing stub in admin route
- [ ] Remove remaining dead delegated code elsewhere
- [ ] Reduce leftover compatibility clutter
- [ ] Tighten transient artifact handling further
- [ ] Reduce repo-root clutter further

Validation:
- [x] Cleanup-only removals did not break tests
- [ ] Main route modules no longer contain stale delegated bodies

## Final validation gate

These must all be true before declaring the architecture-cleanup aim fulfilled:

- [ ] backend app starts cleanly
- [ ] architecture guard passes
- [ ] major backend route families are thin
- [ ] infrastructure separation is materially real beyond the first adapters
- [ ] deployment/config normalization is substantially complete
- [ ] compatibility/path drift is materially reduced
- [ ] targeted regression packs stay green
- [ ] broader full-suite validation is run and green
