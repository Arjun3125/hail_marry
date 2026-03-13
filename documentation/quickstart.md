# Quickstart (Local Development)

## 1) Prerequisites
- Docker + Docker Compose
- Python 3.11+
- Node.js 20+
- Ollama running locally (`ollama serve`)

## 2) Environment Setup
```bash
cp .env.example .env
```
Update:
- `DATABASE_URL`
- `REDIS_URL`
- `OLLAMA_URL`
- `AI_SERVICE_URL` / `AI_SERVICE_KEY` (if using AI service)

## 3) Start Dependencies
```bash
docker compose up -d postgres redis
```

## 4) Backend API
```bash
cd backend
pip install -r requirements.txt
python start-api.sh
```

## 5) AI Service + Worker
```bash
cd backend
python start-ai-service.sh
python start-worker.sh
```

## 6) Frontend
```bash
cd frontend
npm install
npm run dev
```

## 7) Verify
- App: `http://localhost:3000`
- API health: `GET http://localhost:8000/health`
- OpenAPI: `GET http://localhost:8000/openapi.json`
- Docs (when `APP_DEBUG=true`): `http://localhost:8000/docs`

## Demo Mode
Set `DEMO_MODE=true` to auto-seed demo data at startup.
