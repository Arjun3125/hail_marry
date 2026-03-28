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
- `OLLAMA_URL`
- `NEXT_PUBLIC_API_URL`

Optional for alternate vector backends and observability:
- `VECTOR_BACKEND_PROVIDER`
- `QDRANT_URL`
- `OBSERVABILITY_OTLP_ENDPOINT`

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
python start-api.sh
```

### 5) Start worker

```bash
cd backend
python start-worker.sh
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
- OpenAPI: `GET http://localhost:8000/openapi.json`
- Docs when enabled: `http://localhost:8000/docs`

### 8) Run core checks before a PR

```bash
cd backend && pytest -q
cd frontend && npm run lint && npm run build
```

## Demo mode

Set `DEMO_MODE=true` to enable demo-mode helpers and seed/demo flows used by the local walkthrough experience.
