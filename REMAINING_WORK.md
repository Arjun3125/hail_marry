# Remaining Work

Date: 2026-03-30

This file lists the work that is still open after the current local implementation, test, and documentation passes.

## Executive Status

- Core platform implementation: complete
- Local backend verification: complete
- Local browser verification: complete for the implemented regression slices
- Mascot local implementation: complete
- Local production-readiness gate automation: complete
- Remaining work: production certification and live-environment validation

## Highest-Priority Remaining Work

### 1. Live WhatsApp staging and device certification

This is the main unresolved blocker.

Still required:

- run a real staging pass against live WhatsApp Cloud API credentials
- verify webhook reachability from the real Meta/WhatsApp side
- test on a real phone/device
- capture screenshots and evidence
- record pass/fail outcomes for:
  - notebook continuity
  - mixed-language commands
  - structured output formatting
  - upload/link ingestion plus follow-up
  - confirmation loops
  - parent/role scoping
  - retry and duplicate-message safety

Primary docs:

- [documentation/mascot_whatsapp_staging_manual_test_script.md](documentation/mascot_whatsapp_staging_manual_test_script.md)
- [documentation/mascot_whatsapp_staging_evidence_template.md](documentation/mascot_whatsapp_staging_evidence_template.md)
- [documentation/mascot_release_gate.md](documentation/mascot_release_gate.md)

Available operator tooling:

- `GET /api/mascot/release-gate-snapshot?days=7`
- `GET /api/mascot/release-gate-evidence?days=7`
- `GET /api/mascot/staging-packet?days=7`
- admin dashboard `Mascot Release Gate` card

### 2. Final mascot production sign-off

After the live WhatsApp run is complete:

- attach the evidence
- confirm no open `P0` or `P1` mascot issues remain
- record release recommendation
- mark the mascot release gate complete in docs

Primary docs:

- [documentation/mascot_release_gate_evidence_template.md](documentation/mascot_release_gate_evidence_template.md)
- [documentation/mascot_production_execution_checklist.md](documentation/mascot_production_execution_checklist.md)

## Broader System Production Gaps

These are the remaining non-mascot gaps called out by the full audit.

### 3. Live external system certification beyond mascot

Still required:

- real WhatsApp Business API staging validation for the broader WhatsApp channel
- real provider/runtime observation under live conditions
- confirmation that production/staging credentials, webhook paths, and delivery behavior are stable

Primary docs:

- [documentation/full_system_audit_report.md](documentation/full_system_audit_report.md)
- [documentation/production_certification_execution_checklist.md](documentation/production_certification_execution_checklist.md)

### 4. OCR accuracy improvement on hard inputs

OCR is implemented and benchmarked, but accuracy still needs improvement on difficult categories.

Still recommended:

- improve handwriting recognition
- improve classroom-board extraction
- improve difficult multilingual image accuracy
- keep tuning against the benchmark corpus

Primary docs:

- [documentation/ocr_system_audit_report.md](documentation/ocr_system_audit_report.md)
- [documentation/ocr_benchmark_report.md](documentation/ocr_benchmark_report.md)
- [documentation/ocr_universal_input_execution_checklist.md](documentation/ocr_universal_input_execution_checklist.md)

### 5. Broader browser E2E coverage

Current browser coverage is meaningful, but not exhaustive.

Still recommended:

- expand failure-path coverage
- expand broader full-product UI regression coverage
- keep CI smoke/full split healthy

Primary docs:

- [documentation/detailed_test_suite_blueprint.md](documentation/detailed_test_suite_blueprint.md)

### 6. Large-media throughput validation

Media transcription and ingestion are implemented, but still need stronger live-scale validation.

Still recommended:

- validate larger audio/video throughput in staging
- confirm queue behavior under heavier media ingestion load
- measure real latency and failure rates under staging traffic

Primary docs:

- [documentation/whatsapp_media_ingestion_report.md](documentation/whatsapp_media_ingestion_report.md)
- [documentation/production_certification_execution_checklist.md](documentation/production_certification_execution_checklist.md)

## Practical Next Actions

Do these in order:

1. Run the local automated gate with `python scripts/production_readiness_gate.py` or use `.github/workflows/production-readiness.yml`.
2. Review the generated `production_readiness_report.md`.
3. Run the real WhatsApp mascot staging flow using [documentation/mascot_whatsapp_staging_manual_test_script.md](documentation/mascot_whatsapp_staging_manual_test_script.md).
4. Export and attach the packet from `GET /api/mascot/staging-packet?days=7` or copy it from the admin dashboard.
5. Fill [documentation/mascot_whatsapp_staging_evidence_template.md](documentation/mascot_whatsapp_staging_evidence_template.md).
6. Record final mascot sign-off in [documentation/mascot_production_execution_checklist.md](documentation/mascot_production_execution_checklist.md).
7. Then close the broader production-certification items still open in [documentation/full_system_audit_report.md](documentation/full_system_audit_report.md).

## Bottom Line

There is no major local implementation gap left on the mascot track.

What remains is mostly:

- live external validation
- evidence capture
- final production sign-off
- ongoing quality improvement on OCR and broader staging/performance coverage
