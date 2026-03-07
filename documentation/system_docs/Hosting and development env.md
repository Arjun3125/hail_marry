# Hosting and Development Environment

**Project:** VidyaOS  
**Version:** v0.1 current implementation  
**Current Architecture Model:** Frontend, public API, dedicated AI service, worker, and optional observability stack

---

## 1. Hosting Model Today

The current repo supports two practical deployment patterns:

### Local / self-hosted development
- Next.js frontend
- FastAPI public API
- FastAPI AI service
- Redis worker
- PostgreSQL
- Redis
- Ollama available at `OLLAMA_URL`

### Containerized stack
Tracked in `docker-compose.yml`:
- `postgres`
- `redis`
- `api`
- `ai-service`
- `worker`
- `frontend`
- `nginx`

Optional observability profile:
- `prometheus`
- `loki`
- `promtail`
- `tempo`
- `grafana`

Ollama is not included in the compose stack. It must run separately and be reachable from both API-side generation workflows and the AI service.

## 2. Environment Variables That Matter Now

```env
DATABASE_URL=postgresql://user:pass@localhost:5432/vidyaos
REDIS_URL=redis://localhost:6379
JWT_SECRET=<strong-secret>
GOOGLE_CLIENT_ID=<google-client-id>
GOOGLE_CLIENT_SECRET=<google-client-secret>
OLLAMA_URL=http://localhost:11434
AI_SERVICE_URL=http://localhost:8001
AI_SERVICE_KEY=<internal-shared-secret>
APP_ENV=local
APP_CORS_ORIGINS=["http://localhost:3000"]
VidyaOS_STORAGE_ROOT=<optional shared storage root>
VidyaOS_VECTOR_STORE_DIR=<optional vector path override>
OBSERVABILITY_OTLP_ENDPOINT=http://localhost:4318/v1/traces
OBSERVABILITY_LOG_PATH=<service log file path>
STARTUP_CHECKS_STRICT=true
WORKER_HEALTH_PORT=8010
```

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
- responsibility: auth, ERP, admin APIs, queue enqueue/status, public AI routes

### AI service
- entrypoint: `backend/ai_service_app.py`
- responsibility: synchronous generation runtime

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

Compose now includes a first-class observability profile:
- Prometheus scrapes service metrics
- Loki receives logs through Promtail
- Tempo receives OpenTelemetry traces
- Grafana is provisioned with datasources for all three
- Prometheus also loads prebuilt alert rules
- Grafana also loads a prebuilt overview dashboard

This is tracked in:
- `ops/observability/prometheus.yml`
- `ops/observability/loki-config.yml`
- `ops/observability/promtail-config.yml`
- `ops/observability/tempo.yml`
- `ops/observability/grafana/provisioning/`

## 6. Current Operational Guidance

### Development
- run frontend, API, AI service, and worker directly, or use compose
- keep Ollama running separately
- use local settings for iterative work

### Production-like deployment
- deploy API and AI service as separate processes
- run worker against the same Redis and storage paths
- provide a strong `JWT_SECRET` and internal `AI_SERVICE_KEY`
- configure `APP_CORS_ORIGINS`, `NEXT_PUBLIC_API_URL`, and metrics / tracing env vars

## 7. Remaining Gaps

Still not complete:
- no built-in email / pager alert transport

This file should be treated as current deployment truth for the repository.
