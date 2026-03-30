# Mascot Phase 4 WhatsApp Production Plan

**Date:** 2026-03-30  
**Parent plan:** [mascot_production_upgrade_plan.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/mascot_production_upgrade_plan.md)  
**Checklist:** [mascot_production_execution_checklist.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/mascot_production_execution_checklist.md)

## Goal

Make the mascot genuinely usable as a WhatsApp-first operator for the same core learning and ingestion flows supported on the web.

## Current Baseline

Already done:

- WhatsApp requests already flow through the shared mascot orchestration layer
- mixed-language interpretation is supported
- link and media ingestion already feed the shared RAG path
- quiz, flashcard, mind map, flowchart, and concept map outputs now have compact WhatsApp formatting

Still missing:

- broader channel parity for notebook-scoped and ingestion follow-ups
- stronger WhatsApp-specific regression coverage
- live staging evidence for mascot-led WhatsApp flows

## Workstreams

### A. Structured Output Formatting

**Objective**

Make non-text tool outputs readable inside a short WhatsApp chat window.

**Implementation**

- add compact formatting for:
  - `mindmap`
  - `flowchart`
  - `concept_map`
- prefer previews over raw JSON
- cap output length and number of nodes/steps
- keep source reply useful even when artifacts are sparse

**Acceptance**

- map and diagram tools return readable previews on WhatsApp
- responses remain short enough for chat consumption

### B. WhatsApp Confirmation Loop

**Objective**

Support safe approval flows for risky mascot actions without forcing users back to the web UI.

**Implementation**

- define WhatsApp-safe confirmation reply format:
  - summary of pending action
  - clear `YES` / `CONFIRM` / `CANCEL` guidance
- map confirmation replies back to pending mascot actions
- support at least:
  - notebook archive
  - high-risk structured imports where channel support is allowed
- reject stale or unauthorized confirmations cleanly

**Acceptance**

- a risky WhatsApp request can pause for confirmation
- the follow-up confirmation executes the pending action safely
- cancellation clears the pending action

**Status**

- implemented

### C. Notebook and Ingestion Continuity

**Objective**

Make WhatsApp follow-up behavior more consistent after uploads, links, and YouTube ingestion.

**Implementation**

- persist active notebook hints across WhatsApp turns
- ensure upload/link follow-ups reuse the correct notebook scope
- improve same-turn link + question flows:
  - ingest
  - retrieve
  - answer
- ensure compact follow-up summaries mention what was indexed

**Acceptance**

- users can continue asking about newly ingested content without restating notebook context
- replies stay grounded to the newly indexed source

**Status**

- implemented for mascot-selected WhatsApp notebook scope carry-over
- further polish can still expand command-family coverage on top of this continuity layer

### D. Channel-Parity Coverage

**Objective**

Reduce drift between web mascot behavior and WhatsApp mascot behavior.

**Implementation**

- add regression tests for:
  - compact map/flowchart formatting
  - confirmation prompts and approvals
  - notebook continuity after ingestion
  - ambiguous WhatsApp commands
  - mixed-language notebook-scoped tool generation
- keep the thin WhatsApp adapter minimal and let mascot stay source-of-truth

**Acceptance**

- WhatsApp-specific flows are protected by focused automated tests

**Status**

- implemented locally for formatting, confirmation loops, notebook continuity, and two-turn scope reuse
- live external staging evidence is still pending

### E. Staging Certification

**Objective**

Collect real evidence that mascot-led WhatsApp flows work with live external infrastructure.

**Implementation**

- run staging script with real device:
  - quiz generation
  - flashcards
  - map/flowchart preview
  - link + question
  - media + question
  - confirmation flow
- capture:
  - response screenshots
  - release-gate snapshot
  - failure counts
  - latency notes

**Acceptance**

- staging evidence exists for mascot-led WhatsApp production flows

**Execution assets**

- [mascot_whatsapp_staging_manual_test_script.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/mascot_whatsapp_staging_manual_test_script.md)
- [mascot_whatsapp_staging_evidence_template.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/mascot_whatsapp_staging_evidence_template.md)

## Recommended Execution Order

1. Workstream E: live staging certification

## Immediate Next Slice

Start with Workstream E:

- run the staging/device script for mascot-led WhatsApp flows
- capture screenshots, release-gate snapshot, and latency notes
- update the checklist after verification
