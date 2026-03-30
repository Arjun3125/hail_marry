# Mascot Release Gate Evidence Template

**Date:** __________  
**Tester / operator:** __________  
**Environment:** __________  
**Commit / build:** __________

## Automated Gate

| Check | Result | Notes |
| --- | --- | --- |
| `backend/tests/test_mascot_routes.py` | Pass / Fail | __________ |
| `backend/tests/test_mascot_whatsapp_adapter.py` | Pass / Fail | __________ |
| `backend/tests/test_alerting.py` | Pass / Fail | __________ |
| `frontend/tests/e2e/mascot-assistant.spec.ts` | Pass / Fail | __________ |
| `frontend/tests/e2e/admin-dashboard.spec.ts` | Pass / Fail | __________ |
| `python -m py_compile ... mascot_orchestrator/routes/alerting/config` | Pass / Fail | __________ |
| `npm run build` | Pass / Fail | __________ |

## Mascot Snapshot

- endpoint: `GET /api/mascot/release-gate-snapshot?days=7`
- prefilled draft export: `GET /api/mascot/release-gate-evidence?days=7`
- captured at: __________
- attach raw response: __________

### Key values

- total mascot actions: __________
- unique mascot users: __________
- interpretation failure %: __________
- execution failure %: __________
- upload failure %: __________
- overall failure %: __________
- active mascot alerts: __________

## Dashboard Verification

- admin dashboard `Mascot Release Gate` card visible: Pass / Fail
- admin dashboard values match API snapshot: Pass / Fail
- notes: __________

## WhatsApp Mascot Staging

- script used: [mascot_whatsapp_staging_manual_test_script.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/mascot_whatsapp_staging_manual_test_script.md)
- result: Pass / Fail
- evidence location: __________

## Sign-Off

- open P0 mascot issues: Yes / No
- open P1 mascot issues: Yes / No
- release recommendation: Approve / Block
- sign-off notes: __________
