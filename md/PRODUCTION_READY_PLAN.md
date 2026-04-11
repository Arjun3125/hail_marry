# Production Ready Plan

Date: 2026-03-30

This plan separates what can be completed inside the codebase from what still requires live external validation.

## Goal

Move the repository from "implemented and locally verified" to "production ready except for external sign-off".

## Track A: Local Production Gate

These are automatable and should be enforced in the repo.

### A1. Unified local release gate

Required:

- backend certification suites
- OCR benchmark gate
- mascot release-gate suites
- frontend production build
- admin dashboard and mascot browser checks

Deliverables:

- one runner script
- one report artifact
- one CI workflow for manual/operator execution

### A2. Production-readiness report

Required:

- write a markdown report with pass/fail per gate
- record timestamps, durations, and exit codes
- clearly separate local gate results from external certification

### A3. Operator-visible documentation

Required:

- link the local gate runner from the audit docs
- link the generated report path
- show the remaining external-only blockers clearly

## Track B: External Certification

These cannot be completed purely in local code.

### B1. Live WhatsApp staging/device run

Required:

- real WhatsApp Cloud API credentials
- real webhook reachability
- real phone/device validation
- screenshots and evidence

Primary docs:

- [documentation/mascot_whatsapp_staging_manual_test_script.md](documentation/mascot_whatsapp_staging_manual_test_script.md)
- [documentation/mascot_whatsapp_staging_evidence_template.md](documentation/mascot_whatsapp_staging_evidence_template.md)

### B2. Final sign-off

Required:

- completed staging evidence
- no blocking `P0` or `P1`
- release recommendation recorded

## What Will Be Implemented In Code Now

1. root-level production plan
2. root-level production gate runner
3. generated markdown report output
4. manual GitHub Actions production-gate workflow
5. doc updates pointing to the automated gate

## Implemented In This Pass

- [scripts/production_readiness_gate.py](scripts/production_readiness_gate.py)
- [.github/workflows/production-readiness.yml](.github/workflows/production-readiness.yml)
- generated report target: `production_readiness_report.md`

## Exit Condition

After these codebase changes:

- local production readiness is automated and replayable
- operators have a single command/workflow to run the local gate
- the only remaining work is external staging and sign-off
