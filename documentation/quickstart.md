# Quickstart

This guide is split into two parts:
- **Part A - User Quickstart**
- **Part B - Developer Quickstart**

---

## Part A - User Quickstart

Use this if you are not coding and only need to access the product.

### 1) Open the website
- Go to the VidyaOS URL shared by your school or admin team.

### 2) Login
- Sign in with your provided account.
- If this is your first login, complete any onboarding prompts shown for your role.

### 3) Start with core workflows
- Teachers: class insights, assignments, AI study tools, assessment tools
- Admins: ERP setup, dashboard, queue and operations views
- Parents and students: reports, attendance, study support, notifications

### 4) AI experience expectations
- Standard AI requests are handled by the main API runtime.
- Heavy requests may be queued and completed through the worker path.
- Response quality depends on available uploaded materials and current Ollama/runtime health.

### 5) Get support
- Use in-app support/help channels.
- Share trace or request IDs with support when available.

---

## Part B - Developer Quickstart

Use this if you are building, debugging, or extending VidyaOS.

### 1) Prerequisites
- Docker and Docker Compose
- Python 3.11+
- Node.js 20+
- Ollama running locally or reachable over HTTP

### 2) Environment setup

```bash
cp .env.example .env
```

Update at minimum:
- `DATABASE_URL`
- `REDIS_URL`
- `JWT_SECRET`
- `REFRESH_SECRET_KEY`
- `APP_ENV`
- `OLLAMA_URL`
- `NEXT_PUBLIC_API_URL`

Optional for alternate vector backends and observability:
- `VECTOR_BACKEND_PROVIDER`
- `QDRANT_URL`
- `OBSERVABILITY_OTLP_ENDPOINT`
- `AI_QUEUE_ENABLED`

Present in config but not required for the current core runtime:
- `AI_SERVICE_URL`
- `AI_SERVICE_URLS`
- `AI_SERVICE_KEY`

### 3) Start dependencies

```bash
docker compose up -d postgres redis
```

### 4) Start backend API

```bash
cd backend
pip install -r requirements.txt
sh start-api.sh
```

### 5) Start worker

```bash
cd backend
sh start-worker.sh
```

### 6) Start frontend

```bash
cd frontend
npm install
npm run dev
```

### 7) Verify local stack

- App: `http://localhost:3000`
- API health: `GET http://localhost:8000/health`
- API readiness: `GET http://localhost:8000/ready`
- OpenAPI: `GET http://localhost:8000/openapi.json`
- Docs when enabled: `http://localhost:8000/docs`

### 8) Run core checks before a PR

```bash
cd backend && pytest -q
cd frontend && npm run lint && npm run build
```

## Demo mode

Set `APP_ENV=development` and `DEMO_MODE=true` to enable demo-mode helpers.
On a fresh demo database, also set `AUTO_SEED_DEMO_DATA=true` on the API
service so the canonical Class 11 CBSE showcase dataset is bootstrapped once.
For the containerized demo stack, use `deploy/compose/demo.yml`.

Hosted demo checklist:
- use real `DATABASE_URL` and `REDIS_URL` values instead of `localhost`
- keep `JWT_SECRET` and `REFRESH_SECRET_KEY` set to different strong values
- set `AI_QUEUE_ENABLED=false` only if you intentionally want to run without Redis-backed heavy jobs
