# Move Plan

## Status legend

- `completed`: implemented and validated
- `in_progress`: active migration area with non-breaking shims still present
- `pending`: planned, not yet executed

## Phase A — Cleanup workspace and governance docs

Status: `completed`

Steps:
- create `DEEP MIND/architecture-cleanup/` as the cleanup control center
- freeze the audit, target architecture, dependency rules, import migration notes, compatibility notes, and validation checklist
- keep cleanup planning artifacts out of runtime code paths

Exit criteria:
- architecture cleanup docs exist and are versioned
- cleanup decisions are tracked outside production modules

## Phase B — Establish non-breaking architectural scaffolding

Status: `completed`

Steps:
- create `backend/src/bootstrap/`
- create `backend/src/interfaces/http/`
- create `backend/src/interfaces/whatsapp/`
- create `backend/src/interfaces/workers/`
- create `backend/src/infrastructure/{config,db,cache,llm,vector,messaging,storage,observability}/`
- keep current imports working while the new structure is seeded

Exit criteria:
- scaffold packages exist
- runtime still imports and starts
- no feature breakage from scaffolding alone

## Phase C — Normalize startup and configuration

Status: `in_progress`

Steps:
- extract app creation and startup wiring from `backend/main.py` into `bootstrap/`
- keep `main.py` as a thin entry wrapper
- introduce root config files under `config/`
- load `APP_ENV` from the new config root
- retain temporary fallback support for legacy backend YAML settings

Already done:
- bootstrap extraction started and is active
- root `config/` environment files exist

Remaining:
- remove more legacy fallback dependence
- finish consolidating startup/config references on the new bootstrap path

Exit criteria:
- `main.py` remains thin
- runtime uses the root config system first
- legacy config files are compatibility-only

## Phase D — Import-system cleanup

Status: `in_progress`

Steps:
- keep `src.*` as the canonical backend import root during cleanup
- remove route-to-route imports
- reduce deep relative imports
- reduce path hacks and `sys.path` dependence where possible
- route interface modules through application helpers instead of peer handlers
- keep the architecture guard green after each slice

Already done:
- architecture guard script exists
- several route-to-route and service-to-route hot spots were removed

Remaining:
- audit remaining path hacks in scripts/tests/bootstrap tooling
- continue reducing compatibility-only import shims

Exit criteria:
- interface modules do not call peer route handlers
- architectural drift checks pass in CI
- import resolution is stable without ad hoc hacks

## Phase E — Route and service re-homing

Status: `in_progress`

Steps:
- move HTTP composition behind `interfaces/http/*`
- shrink route handlers into thin interface layers
- extract orchestration into `domains/*/application`
- keep domain models and business rules out of route modules

Already done:
- cleaned router composition exists for AI, academic, administrative, identity, and platform entrypoints
- major application extraction already covers:
  - AI query preparation/personalization
  - student study tools
  - student dashboard
  - teacher bulk attendance/marks paths
  - mascot suggestion/release-gate slices
  - personalization query/study-path slices
  - large parts of admin operations

Active next targets:
- remaining student route branches
- remaining teacher route branches
- remaining platform/mascot branches that still assemble responses inline

Exit criteria:
- major route families are thin orchestration boundaries only
- response assembly and transactional logic primarily live in application helpers

## Phase F — Infrastructure separation

Status: `in_progress`

Steps:
- re-home observability adapters under `infrastructure/observability`
- re-home queue/messaging adapters under `infrastructure/messaging`
- move webhook delivery behind messaging adapters
- continue separating DB/vector/cache/storage/LLM integrations from route/service modules

Already done:
- observability adapter layer started
- messaging/queue adapter layer started
- webhook delivery now goes through infrastructure messaging

Remaining:
- DB/session setup separation
- vector/OCR adapter cleanup
- cache adapter cleanup
- storage adapter cleanup
- broader LLM/provider adapter cleanup

Exit criteria:
- interface/application code stops importing provider/storage internals directly
- infrastructure concerns are routed through dedicated adapters

## Phase G — Deployment structure cleanup

Status: `in_progress`

Steps:
- make `deploy/` the canonical deployment root
- place Dockerfiles under `deploy/docker/`
- place compose manifests under `deploy/compose/`
- place nginx config under `deploy/nginx/`
- place operational scripts under `deploy/scripts/`
- keep temporary root wrappers only where backward compatibility is needed

Already done:
- canonical deployment files exist under `deploy/`
- canonical deploy scripts exist under `deploy/scripts/`

Remaining:
- reduce reliance on root compatibility deploy files
- finish documentation alignment so `deploy/` is the single source of truth

Exit criteria:
- `deploy/` is canonical
- root deployment wrappers are minimal or removable

## Phase H — Repo cleanup and compatibility reduction

Status: `pending`

Steps:
- remove leftover dead code after delegation cutovers
- reduce obsolete compatibility shims
- relocate or delete stale root artifacts
- tighten `.gitignore` for transient outputs
- remove superseded helper scripts when replacements are stable

Exit criteria:
- dead delegated code is removed
- compatibility layer is smaller and intentional
- repo root contains fewer architectural leftovers

## Final cleanup gate

The architecture-cleanup aim is fulfilled only when all of the following are true:

- major route families are reduced to thin interface layers
- orchestration primarily lives in application helpers
- infrastructure-facing code is routed through `backend/src/infrastructure/*`
- deployment/config cleanup is consolidated
- compatibility/path drift is materially reduced
- validation remains green after the remaining moves
