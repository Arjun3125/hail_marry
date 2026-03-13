# API Reference (OpenAPI)

## Source of Truth
VidyaOS is a FastAPI service. The authoritative API spec is the OpenAPI JSON:
- `GET /openapi.json`

When `APP_DEBUG=true`, the interactive docs are available at:
- `GET /docs` (Swagger UI)
- `GET /redoc`

## Base URL
- Local dev (default): `http://localhost:8000`

## Auth Overview
- Auth tokens are issued via `/api/auth/*`.
- The API uses HTTP-only cookies by default.
- For programmatic access, a Bearer token in `Authorization: Bearer <token>` is supported by the auth stack.

## Core Route Groups

| Area | Prefix | Notes |
|---|---|---|
| Auth | `/api/auth` | Login, refresh, logout, OAuth |
| Students | `/api/student` | Dashboard, AI tools, uploads, results |
| Teachers | `/api/teacher` | Classes, uploads, assessments |
| Parents | `/api/parent` | Dashboard, digest preview |
| Admin | `/api/admin` | Governance, AI review, queue ops |
| AI (sync) | `/api/ai` | Q&A, workflows, URL ingestion |
| AI (jobs) | `/api/ai/jobs` | Queue status polling |
| Documents | `/api/documents` | Citation click-through |
| Support | `/api/support` | Docs-as-AI chatbot endpoints |
| Billing | `/api/billing` | Plans, subscriptions, payments |

## Versioning
The API is currently unversioned. The OpenAPI schema version is derived from `settings.app.version`.

## Client Generation
Use any OpenAPI tooling (e.g., `openapi-generator`, `orval`, `openapi-typescript`) against `/openapi.json` to generate typed clients.
