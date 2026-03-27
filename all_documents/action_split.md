# Execution Split: Engineering vs Owner Actions (2026-03-12)

This page splits the backlog items you shared into:
- **Engineering/Docs work** I can implement directly in this repo.
- **Owner/Legal/Operations actions** you need to decide or execute outside the codebase.

---

## Engineering Work (Code/Docs)

### Batch 1 — Immediate unblockers (P0)
- Clickable citations: wire citation URL generation + UI click-through.
- Docs-as-AI chatbot: expose API endpoints + auth.
- Document ingestion watch: schedule/worker to run `doc_watcher` with hash detection.
- Parent weekly digest: email send pipeline (SMTP/transactional provider) + scheduler.
- API Reference / OpenAPI spec (versioned endpoint docs).
- Getting Started / Quickstart guide.
- `CONTRIBUTING.md`.
- `CHANGELOG.md`.

### Batch 2 — Product UX deliverables (P1)
- Role-specific dashboards (parent/student/teacher).
- QR code student login.
- Smart timetable generator (see `documentation/timetable_generator_spec.md`).
- Android Play Store shell (TWA/Capacitor).

### Batch 3 — Platform hardening & scale (P1/P2)
- ✅ Sentry integration (error tracking).
- ✅ GPU monitoring (dcgm exporter + Grafana panels).
- ✅ CI/CD pipeline (GitHub Actions).
- ✅ Email/SMS notifications beyond WhatsApp (SMTP/SMS alert transports).
- ✅ Interactive AI queue/position feedback + multi-service routing for GPU scaling.
- ✅ Vector DB scaling (Qdrant external store option).
- ✅ Horizontal API scaling (multi-instance deployment with nginx DNS resolve).

---

## Owner / Legal / Operations (You Do)

### Batch A — Decisions required before engineering
- Select canonical LLM (Qwen 14B vs llama3.2) and align docs vs infra.
- Define consent language per data category (DPDP requirement).
- Decide stance on “no profiling of children” (legal opinion on analytics).

### Batch B — Compliance + governance actions
- Legal sign-off on `documentation/DPDP_COMPLIANCE.md`.
- Appoint Data Protection Officer (DPO) + grievance redressal channel.
- Define data retention/expiry policy (storage limitation).
- Define 72‑hour breach notification SOP.
- Choose verification method for parental consent (<18).

### Batch C — Business / operations
- GPU procurement + failover plan.
- Internet redundancy plan for GPU tunnel.
- Positioning for ERP + AI bundle (pricing/packaging).
- Team/process setup (code review policy, hiring plan).

---

## Resolved From the Original List (No Action)
- Real-time notifications are persisted in the database.
- Extended data connectors are wired for PPTX/XLSX uploads and Google Docs/Notion URL ingestion.
- Provider abstraction is wired; AI runs as a dedicated service + worker.
- Monitoring stack (Prometheus/Grafana/Loki/Tempo) deployed; Sentry still pending.
- Password auth implemented.
- File upload validation implemented.
- Self-service onboarding implemented.
- Razorpay billing integration implemented.
