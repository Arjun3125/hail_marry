# Mascot Production Release Gate

**Date:** 2026-03-30  
**Execution checklist:** [mascot_production_execution_checklist.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/mascot_production_execution_checklist.md)  
**Evidence template:** [mascot_release_gate_evidence_template.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/mascot_release_gate_evidence_template.md)  
**WhatsApp staging script:** [mascot_whatsapp_staging_manual_test_script.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/mascot_whatsapp_staging_manual_test_script.md)

## Purpose

Define the minimum engineering and operator gate required before the mascot can be considered production-ready as the central conversational control layer.

## Automated Gate

The release is blocked unless all of the following pass:

1. `python -m pytest -q -p no:cacheprovider backend/tests/test_mascot_routes.py`
2. `python -m pytest -q -p no:cacheprovider backend/tests/test_mascot_whatsapp_adapter.py`
3. `python -m pytest -q -p no:cacheprovider backend/tests/test_alerting.py`
4. `playwright test tests/e2e/mascot-assistant.spec.ts`
5. `playwright test tests/e2e/admin-dashboard.spec.ts`
6. `python -m py_compile backend/src/domains/platform/services/mascot_orchestrator.py backend/src/domains/platform/routes/mascot.py backend/src/domains/platform/services/alerting.py backend/config.py`
7. `npm run build` in `frontend`

## Required Operator Signals

Operators must be able to inspect all of the following through the mascot release-gate snapshot or admin dashboard:

- total mascot actions in the current window
- unique mascot users in the current window
- interpretation success and failure totals
- execution success and failure totals
- upload success and failure totals
- confirmation success, failure, and cancelled totals
- interpretation failure rate
- execution failure rate
- upload failure rate
- overall mascot failure rate
- active mascot-related alerts

The structured snapshot is available at:

- `GET /api/mascot/release-gate-snapshot?days=7`
- `GET /api/mascot/release-gate-evidence?days=7`
- `GET /api/mascot/staging-packet?days=7`

The admin dashboard surfaces the same data in the `Mascot Release Gate` card and now supports:

- copying a prefilled mascot evidence draft for operator sign-off
- copying a combined mascot + WhatsApp staging packet for the live device run

## Failure Thresholds

Do not ship if any of the following are true:

- mascot execution failure rate is materially above baseline in the release window
- upload failure rate is materially above baseline in the release window
- mascot-specific alerts are active and unresolved
- notebook scope, confirmation safety, or upload-follow-up regressions are open
- browser mascot flows fail on the admin or role-specific assistant surfaces

## Human Gate

The rollout is still blocked until:

- the operator fills [mascot_release_gate_evidence_template.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/mascot_release_gate_evidence_template.md)
- the mascot WhatsApp staging pass is executed using [mascot_whatsapp_staging_manual_test_script.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/mascot_whatsapp_staging_manual_test_script.md)
- no open P0 or P1 mascot regressions remain

## Exit Condition

The mascot may be considered production-ready only when:

- the automated gate passes
- the snapshot and dashboard operator signals are available
- the evidence template is complete
- the live WhatsApp mascot staging pass is signed off
