# Architecture Cleanup Audit

## Current state

- Backend is partly domain-oriented, but route handlers still mix HTTP, orchestration, data access, provider calls, and job coordination.
- `backend/main.py` mixes bootstrap, middleware wiring, health endpoints, exception handlers, router inclusion, and demo initialization.
- Config loading is centralized in `backend/config.py`, but environment layering is still tied to legacy backend-local YAML files.
- `src.*` imports are the effective backend package root, but scripts/tests/Alembic still use `sys.path` injection.
- Demo and compatibility logic remain mixed into runtime routes and entrypoints.

## Confirmed problem areas

- route-to-route imports
- service-to-route imports
- password hashing duplicated outside identity services
- config/deploy files spread between backend root and repo root
- cleanup docs and generated operational artifacts mixed at repo root

## First cleanup wave implemented

- bootstrap package created
- root `config/` introduced with environment files
- DEEP MIND cleanup control folder created
- first route-to-route imports removed
- initial architecture guard script added

