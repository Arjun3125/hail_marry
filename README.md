# AIaaS — AI Infrastructure for Indian K-12 Education

> Multi-tenant school ERP + curriculum-grounded AI study assistant, running on local GPU.

![Stack](https://img.shields.io/badge/FastAPI-Backend-009688?style=flat-square&logo=fastapi)
![Stack](https://img.shields.io/badge/Next.js_16-Frontend-000?style=flat-square&logo=next.js)
![Stack](https://img.shields.io/badge/PostgreSQL-Database-4169E1?style=flat-square&logo=postgresql)
![Stack](https://img.shields.io/badge/Ollama-LLM-blue?style=flat-square)
![Stack](https://img.shields.io/badge/FAISS-Vectors-yellow?style=flat-square)

---

## What is this?

A **school management platform** (ERP) combined with an **AI study assistant** that answers from uploaded curriculum materials — with citations. Think *Google NotebookLM, but purpose-built for Indian K-12 schools*, running locally on affordable hardware.

## Key Features

### 🎓 School ERP
- **Attendance tracking** — teacher entry, student/parent view
- **Marks & results** — exam management, grade reports
- **Assignments** — CRUD + file submission
- **Timetable engine** — admin-managed schedules
- **Lecture library** — PDF/YouTube upload with transcript ingestion
- **Complaint portal** — student submission, admin review

### 🤖 AI Study Assistant (13 Modes)
| Mode | Description |
|---|---|
| **Q&A** | Citation-grounded answers from uploaded notes |
| **Study Guide** | Structured sections with source references |
| **Quiz** | NCERT-aligned MCQ generation |
| **Concept Map** | JSON nodes + edges for topic relationships |
| **Weak Topic** | Performance-aware remediation plans |
| **Flowchart** | Mermaid.js process diagrams |
| **Mind Map** | Hierarchical topic trees |
| **Flashcards** | Front/back card pairs |
| **Socratic** | Guided hints — never gives direct answers |
| **Perturbation (Exam Prep)** | Novel variations of existing questions |
| **Debate** | Devil's advocate for critical thinking |
| **Essay Review** | Structural feedback on writing |
| **Career Simulation** | Role-play professional scenarios |

### 👩‍🏫 Teacher Tools
- **AI Assessment Generator** — generate MCQ assessments from uploaded materials
- **Doubt Heatmap** — real-time view of where students are struggling (aggregated AI queries)
- **Class Insights** — performance analytics

### 👨‍👩‍👧 Parent Portal
- **Dashboard** — attendance, marks, pending assignments at a glance
- **🔊 Audio Report** — listen to child's progress summary via browser TTS
- **Attendance & Results** — detailed views

### 📚 Student Features
- **Spaced Repetition** — SM-2 algorithm for long-term retention with self-rating
- **Multi-mode AI chat** — 8 pedagogical modes with growth-mindset prompts
- **Study Tools** — concept maps, flashcards, flowcharts, mind maps

### 🔐 Security & Multi-tenancy
- JWT in HTTP-only cookies with refresh token rotation
- Tenant isolation at DB + vector store + API layers
- CSRF protection, rate limiting (Redis-backed), output sanitization
- AI safety: citation enforcement, prompt injection defense, PII stripping

### 🏛️ Admin Governance
- KPI dashboard, AI usage analytics, quality review panel
- User management with audit logging
- Webhook system for integrations
- Security monitoring (failed logins, role changes)

---

## Architecture

```
                          ┌──────────────────────────┐
                          │   Next.js 16 Frontend    │
                          │  (Student/Teacher/Admin/  │
                          │       Parent portals)     │
                          └──────────┬───────────────┘
                                     │
                          ┌──────────▼───────────────┐
                          │    Nginx Reverse Proxy    │
                          │  (TLS, security headers)  │
                          └──────────┬───────────────┘
                                     │
                          ┌──────────▼───────────────┐
                          │   FastAPI Backend (API)   │
                          │  Auth │ Routes │ AI Core  │
                          └──┬─────┬──────┬──────────┘
                             │     │      │
                    ┌────────▼┐ ┌──▼───┐ ┌▼──────────┐
                    │PostgreSQL│ │Redis │ │  Ollama   │
                    │ (Multi-  │ │(Rate │ │  (LLM +   │
                    │  tenant) │ │limit)│ │ Embedding)│
                    └──────────┘ └──────┘ └─────┬─────┘
                                                │
                                         ┌──────▼──────┐
                                         │  FAISS      │
                                         │ Vector Store│
                                         └─────────────┘
```

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Ollama (with `llama3.2` and `nomic-embed-text`)

### Backend
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # configure DATABASE_URL, OLLAMA_URL, etc.
alembic upgrade head
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env.local  # set NEXT_PUBLIC_API_URL
npm run dev
```

### Docker (Recommended)
```bash
docker compose up -d
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 16, React 19, TypeScript, Tailwind CSS 4 |
| Backend | FastAPI, Python 3.11+, SQLAlchemy, Pydantic |
| Database | PostgreSQL 15+ (multi-tenant), Alembic migrations |
| AI/ML | Ollama (llama3.2), FAISS, sentence-transformers, cross-encoder reranking |
| Cache | Redis 7 (rate limiting, query caching) |
| Infrastructure | Docker Compose, Nginx, Let's Encrypt TLS |
| Auth | Google OAuth 2.0, JWT (HTTP-only cookies) |

---

## AI Pipeline

```
Query → Embed (nomic-embed-text) → FAISS search (top 8, tenant-scoped)
  → Cross-encoder rerank (ms-marco-MiniLM, top 5)
  → Jaccard deduplication (0.85 threshold)
  → Context compression
  → Prompt template (13 mode-specific)
  → LLM inference (Ollama, temp=0.1)
  → Output sanitization
  → Citation validation
  → Cache + Log + Webhook → Return
```

---

## Project Structure

```
proxy_notebooklm/
├── backend/
│   ├── ai/              # RAG pipeline (ingestion, retrieval, embeddings, cache, providers)
│   ├── auth/            # OAuth, JWT, dependencies
│   ├── middleware/       # CSRF, rate limiting
│   ├── models/          # 20+ SQLAlchemy models
│   ├── routes/          # API routes (ai, admin, teacher, student, parent)
│   ├── services/        # Webhooks, utilities
│   └── tests/           # Security regression tests
├── frontend/
│   └── src/app/         # Next.js app router
│       ├── admin/       # 12 admin routes
│       ├── teacher/     # 10 teacher routes
│       ├── student/     # 12 student routes
│       └── parent/      # 5 parent routes
├── docker-compose.yml
├── nginx/               # Reverse proxy config
└── documentation/       # Architecture docs, audit reports
```

---

## Documentation

| Document | Description |
|---|---|
| `documentation/structural_audit.md` | Deep technical audit (architecture, security, scaling) |
| `STAR_FEATURES_ANALYSIS.md` | Feature gap analysis vs 5 reference repos |
| `documentation/AI in Indian K-12 Learning.txt` | K-12 AI pedagogy reference |
| `raw/` | 11 detailed system design documents |

---

## Target Market

- **1.5M+ Indian K-12 schools**
- Local GPU deployment: ₹3L one-time + ₹6,500/month operational
- Serves 2-3 pilot schools on single RTX 4090

---

## License

Private — All rights reserved.
