# Validation Checklist

## Always-run checks after each cleanup slice

- [x] touched Python modules compile
- [x] `python scripts/check_architecture.py` passes
- [x] backend app imports and starts
- [x] the targeted regression pack for the touched slice passes

## Backend runtime checks

- [ ] health endpoint checked after larger bootstrap/config moves
- [ ] readiness endpoint checked after larger bootstrap/config moves
- [ ] telemetry and middleware wiring confirmed after startup changes
- [x] AI routes still resolve
- [x] mascot routes still resolve
- [x] admin routes still resolve in targeted regression packs
- [x] academic routes still resolve in targeted regression packs

## Infrastructure checks

- [ ] WhatsApp gateway/adapter regression pack passes after relevant messaging moves
- [ ] queue lifecycle and metrics remain green after messaging adapter moves
- [ ] observability/admin diagnostics endpoints remain green after adapter moves

## Frontend and deployment checks

- [ ] frontend build passes after frontend-affecting cleanup slices
- [ ] canonical deploy assets under `deploy/` remain aligned with documented entrypoints

## Final architecture-cleanup validation

- [ ] backend startup is green
- [ ] architecture guard is green
- [ ] targeted regression packs are green
- [ ] broader backend suite is green
- [ ] frontend build is green
- [ ] remaining major route files are thin enough to satisfy the target layering
