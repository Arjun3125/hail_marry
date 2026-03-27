# Quickstart

This guide is now split into two parts so teams can onboard faster depending on role.

- **Part A — User Quickstart**: for school staff/teachers/students using the hosted website.
- **Part B — Developer Quickstart**: for engineers running VidyaOS locally or contributing code.

---

## Part A — User Quickstart (Hosted Website)

Use this if you are **not coding**, and only need to access the product.

### 1) Open the website
- Go to the VidyaOS URL shared by your school/admin team.

### 2) Login
- Sign in with your provided account (email/mobile/SSO as configured).
- If this is your first login, complete profile and role onboarding prompts.

### 3) Start with core workflows
- **Teachers**: class insights, assignment flows, AI study/assessment tools.
- **Admins**: ERP setup, onboarding checklist, dashboard + operations view.
- **Parents/Students**: reports, attendance, study support, and notifications.

### 4) AI experience expectations
- AI is served through a **centralized Ollama-backed AI service** managed by platform operators.
- During high load, requests may queue; retry or simplified responses may be shown depending on platform policy.

### 5) Get support
- Use in-app support/help channels.
- Share trace/request IDs with support for faster resolution.

---

## Part B — Developer Quickstart (Local Development)

Use this if you are building, debugging, or extending VidyaOS.

### 1) Prerequisites
- Docker + Docker Compose
- Python 3.11+
- Node.js 20+
- Ollama running (`ollama serve`) **or** centralized endpoints configured via `OLLAMA_BASE_URLS`

### 2) Environment setup
```bash
cp .env.example .env
```
Update at minimum:
- `DATABASE_URL`
- `REDIS_URL`
- `OLLAMA_URL` (legacy single endpoint)
- `OLLAMA_BASE_URLS` (preferred multi-endpoint centralized setup)
- `AI_SERVICE_URL` / `AI_SERVICE_KEY` (if using dedicated AI service)

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

### 5) Start AI service + worker
```bash
cd backend
python start-api.sh
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
- Docs (when `APP_DEBUG=true`): `http://localhost:8000/docs`

### 8) Run core checks before PR
```bash
cd backend && pytest -q
cd frontend && npm run lint && npm run build
```

## Demo mode
Set `DEMO_MODE=true` to auto-seed demo data at startup.
