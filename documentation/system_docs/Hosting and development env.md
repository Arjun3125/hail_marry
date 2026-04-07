# Hosting and Development Environment

**Project:** VidyaOS  
**Version:** v0.1 current implementation  
**Current Architecture Model:** Frontend, FastAPI API, Redis worker, and optional observability stack  
**Status:** Updated to match the repository on 2026-03-28

---

## 1. Hosting Model Today

The current repo supports two practical patterns.

### Local or self-hosted development
- Next.js frontend
- FastAPI API
- Redis worker
- PostgreSQL
- Redis
- Ollama available over HTTP

### Containerized stack
Tracked in `docker-compose.yml`:
- `postgres`
- `redis`
- `api`
- `worker`
- `frontend`
- `nginx`

Optional profiles:
- observability: `prometheus`, `loki`, `promtail`, `tempo`, `grafana`, `dcgm-exporter`
- vector: `qdrant`

Important clarification:
- the repo does not currently define a separate AI-service container
- Ollama is not included in the compose stack and must run separately

## 2. Environment Variables That Matter

Core variables for the current runtime:

```env
DATABASE_URL=postgresql://user:pass@localhost:5432/vidyaos
REDIS_URL=redis://localhost:6379
JWT_SECRET=<strong-secret>
REFRESH_SECRET_KEY=<different-strong-secret>
GOOGLE_CLIENT_ID=<google-client-id>
GOOGLE_CLIENT_SECRET=<google-client-secret>
OLLAMA_URL=http://localhost:11434
APP_ENV=local
APP_CORS_ORIGINS=["http://localhost:3000"]
VidyaOS_STORAGE_ROOT=<optional storage root>
VidyaOS_VECTOR_STORE_DIR=<optional vector path override>
VECTOR_BACKEND_PROVIDER=faiss
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=
OBSERVABILITY_OTLP_ENDPOINT=http://localhost:4318/v1/traces
OBSERVABILITY_LOG_PATH=<service log file path>
AI_QUEUE_ENABLED=true
WORKER_HEALTH_PORT=8010
```

Present in config but not part of the active core execution path:

```env
AI_SERVICE_URL=http://localhost:8001
AI_SERVICE_URLS=http://localhost:8001
AI_SERVICE_KEY=<reserved/internal>
```

These values currently support admin guidance and future separation work more than the live request path.

## 3. Current Config Files

Tracked YAML configuration:
- `backend/settings.yaml`
- `backend/settings-production.yaml`

Behavior:
- YAML provides defaults
- environment variables override YAML
- `APP_ENV=production` loads `settings-production.yaml` when present

## 4. Current Deployment Units

### Public API
- entrypoint: `backend/main.py`
- responsibility: auth, ERP, admin APIs, public AI routes, queue enqueue/status, observability surfaces

### Worker
- entrypoint: `backend/ai_worker.py`
- responsibility: queued job execution
- health/readiness surface: `backend/worker_health_app.py`

### Frontend
- application in `frontend/`
- API base configured through `NEXT_PUBLIC_API_URL`

### Nginx
- optional reverse proxy for local compose use

## 5. Observability Deployment

Tracked under `ops/observability/`:
- Prometheus scrape config
- Loki config
- Promtail config
- Tempo config
- Grafana provisioning
- alert rules

## 6. Current Operational Guidance

### Development
- run frontend, API, and worker directly, or use compose
- keep Ollama running separately
- use local settings for iterative work

### Production-like deployment
- deploy API and worker as separate processes
- run both against the same Redis and storage paths
- provide strong and different `JWT_SECRET` and `REFRESH_SECRET_KEY` values
- configure `APP_CORS_ORIGINS`, `NEXT_PUBLIC_API_URL`, and observability env vars
- use `/ready` for Railway/API healthchecks instead of `/health`
- on Railway, the worker health server now defaults to the service `PORT`; override `WORKER_HEALTH_PORT` only if your platform supports a second exposed port

### Hosted demo deployment
- use `APP_ENV=development`
- set `DEMO_MODE=true`
- set `AUTO_SEED_DEMO_DATA=true` on the API service only
- keep `DATABASE_URL` and `REDIS_URL` pointed at real managed services, not `localhost`
- if you intentionally disable async queue flows for the demo with `AI_QUEUE_ENABLED=false`, API readiness will no longer require Redis

## 7. Known Gaps

- some frontend admin clients still assume `/api/...` prefixes where backend platform routes currently use `/branding`, `/features`, or `/whatsapp`
- enterprise compliance and incident pages are present, but still need API-contract cleanup
- the current docs previously overstated a dedicated AI-service topology; that is no longer the recommended deployment description for this repo

Treat this file as the current deployment truth for the repository.
