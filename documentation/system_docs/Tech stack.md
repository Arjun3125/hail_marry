# Tech Stack

**Project:** AIaaS – AI Infrastructure for Educational Institutions  
**Version:** v0.1 (Pilot → Scale-Ready)

---

## 1. Technology Selection Philosophy

Every stack choice was evaluated against 6 criteria:

1. **Multi-tenant SaaS readiness** — Must support tenant isolation natively or easily
2. **AI ecosystem compatibility** — Must integrate smoothly with AI/ML libraries
3. **GPU-optimized inference** — Must maximize GPU utilization for local inference
4. **Cloud migration flexibility** — Must not lock us into local-only deployment
5. **Developer productivity** — Must have strong docs, community, and tooling
6. **Cost efficiency** — Must minimize operational cost during pilot

---

## 2. Frontend Stack

### 2.1 Web Application

| Layer | Technology | Rationale |
|---|---|---|
| Framework | **Next.js (React)** | SSR for SEO, file-based routing, production-ready |
| Language | **TypeScript** | Type safety prevents runtime bugs at scale |
| Styling | **Tailwind CSS** | Rapid UI dev, utility-first, consistent design |
| State | **React Query + Zustand** | Clean server state + minimal client state |
| Auth Handling | **JWT + Google OAuth** | Secure login with institutional Google accounts |
| Charts | **Recharts / Chart.js** | Student analytics, performance heatmaps |
| Rich Text | **TipTap / Slate** | Notes viewer, AI response rendering |
| Icons | **Lucide / Heroicons** | Clean, consistent outline icon set |
| i18n | **next-i18next** | Regional Indian language support (Phase 2) |

### 2.2 Android App (Phase 2)

| Layer | Technology | Rationale |
|---|---|---|
| Framework | **React Native** | Code reuse with web, shared API layer |
| Push Notifications | **Firebase Cloud Messaging** | Reliable delivery on Android |
| Auth | **Shared JWT API** | Same backend, same tokens |

---

## 3. Backend Stack (Control Plane)

### 3.1 Core API Layer

| Layer | Technology | Rationale |
|---|---|---|
| Framework | **FastAPI (Python 3.11+)** | Async support, AI ecosystem compat, OpenAPI auto-docs |
| Web Server | **Uvicorn + Gunicorn** | ASGI server with worker management |
| Reverse Proxy | **Nginx** | TLS termination, static file serving, load balancing |
| Auth | **OAuth 2.0 + JWT** | Stateless auth, short-lived tokens |
| Rate Limiting | **Redis** | In-memory throttling per user/tenant |
| Validation | **Pydantic** | Schema validation at API boundary |

**Why FastAPI over Django/Express:**
- Native async for non-blocking AI calls
- First-class Pydantic validation
- Auto-generated OpenAPI spec
- Python is the AI/ML lingua franca

### 3.2 Database Layer

| Purpose | Technology | Rationale |
|---|---|---|
| Primary DB | **PostgreSQL 15+** | Mature, supports RLS, JSON, full-text search |
| Caching | **Redis** | Rate limiting, session caching, hot query results |
| ORM | **SQLAlchemy** | Flexible, supports raw SQL when needed |
| Migrations | **Alembic** | Version-controlled schema changes |

All tables include: `tenant_id`, `created_at`, `updated_at`.  
Strict row-level isolation via application layer (with RLS planned at scale).

---

## 4. AI Stack (Data Plane)

This is the core differentiator.

### 4.1 LLM Inference

| Component | Technology | Rationale |
|---|---|---|
| Model Runner | **Ollama** | Simple local model management, HTTP API |
| Primary Model | **Qwen 14B (4-bit quantized)** | Best quality at 14B size for education domain |
| Fallback Model | **Llama 3 8B** | Lighter model when GPU is under load |
| Quantization | **4-bit or 8-bit** | Fits 14B model in 24GB VRAM |
| Context Strategy | **Sliding window + compression** | Maximizes relevant content under token budget |

Runs on: RTX 4090 (24GB VRAM), 64GB system RAM.

### 4.2 Embeddings

| Component | Technology | Rationale |
|---|---|---|
| Embedding Model | **nomic-embed-text** | 768-dim, high quality, runs locally |
| Pipeline | **Custom FastAPI microservice** | Async batch processing on upload |

Embeddings stored per tenant namespace. Generated on upload and transcript ingestion.

### 4.3 Vector Database

| Phase | Technology | Rationale |
|---|---|---|
| Pilot | **FAISS (local)** | Zero cost, fast, in-process |
| Scale | **Qdrant** | Production-grade, filtering, namespaces |
| Enterprise | **Weaviate / Pinecone** | Managed, distributed, multi-region |

Each tenant gets isolated namespace. No cross-tenant retrieval.

### 4.4 Retrieval Pipeline

| Stage | Tool |
|---|---|
| Embedding generation | nomic-embed-text |
| Top-K semantic search | FAISS / Qdrant |
| Reranking | Cross-encoder (ms-marco-MiniLM-L-2-v2) |
| Context compression | Custom summarization for lower-ranked chunks |
| Prompt building | Structured template engine |

### 4.5 Document Processing

| Task | Tool | Rationale |
|---|---|---|
| PDF parsing | **PyMuPDF (fitz)** | Fast, reliable, preserves structure |
| DOCX parsing | **python-docx** | Native Python support |
| YouTube transcripts | **YouTube Transcript API** | Free, no API key needed |
| Text cleaning | **Custom pipeline** | Header removal, noise filtering |

Hierarchical chunking: 300–600 tokens per chunk, 50–100 token overlap.

---

## 5. Infrastructure Stack

### 5.1 Cloud Control Plane

| Component | Technology | Rationale |
|---|---|---|
| VPS Provider | **DigitalOcean / Hetzner** | Cost-effective, reliable |
| OS | **Ubuntu 22.04 LTS** | Long-term support, stable |
| SSL | **Let's Encrypt (Certbot)** | Free, auto-renewing |
| Monitoring | **Uptime Kuma + Prometheus** | Health checks + metrics |
| CI/CD | **GitHub Actions** | Native GitHub integration |
| Error Tracking | **Sentry** | Real-time error monitoring |

### 5.2 Local AI Node

| Component | Specification |
|---|---|
| GPU | RTX 4090 (24GB VRAM) |
| RAM | 64GB DDR5 |
| CPU | 12–16 core |
| Storage | 2TB NVMe |
| Power Backup | UPS (30 min) |
| Firewall | UFW (only VPS IP allowed) |
| Connection | Secure tunnel (Tailscale / Cloudflare Tunnel) |

---

## 6. DevOps & Deployment

### 6.1 Containerization

| Phase | Tool |
|---|---|
| Pilot | **Docker Compose** (api, postgres, redis, ai-service) |
| Scale | **Kubernetes** (separate pods per service) |

### 6.2 CI/CD Pipeline

```
Push to main → Run tests (pytest + Playwright)
    → Lint + type check
    → Build Docker image
    → Deploy to staging
    → Manual approval → Deploy to production
```

### 6.3 Configuration Management

YAML-based settings per environment:
- `settings.yaml` — default configuration
- `settings-local.yaml` — development overrides
- `settings-docker.yaml` — Docker deployment
- `settings-production.yaml` — production deployment

---

## 7. Observability Stack

| Purpose | Tool |
|---|---|
| Logs | **Loki** |
| Metrics | **Prometheus** |
| Dashboard | **Grafana** |
| GPU Monitoring | **nvidia-smi + custom exporter** |
| AI Query Tracing | **Custom trace ID system** |
| Error Tracking | **Sentry** |

Track: query latency, AI response time, retrieval precision, token usage, per-tenant AI usage, cache hit ratio, citation accuracy.

---

## 8. Security Stack

- HTTPS only (TLS 1.2+)
- JWT with 1h expiry, HTTP-only cookies
- Rate limiting (Redis-backed)
- RBAC enforcement on every endpoint
- Firewall-restricted AI node
- Encrypted database storage
- Daily encrypted backups
- Security headers: CSP, HSTS, X-Frame-Options, X-Content-Type-Options

---

## 9. Messaging & Notifications

| Type | Tool | Rationale |
|---|---|---|
| Email | **SendGrid / Resend** | Transactional emails (results, assignments) |
| SMS | **Twilio (optional)** | Parent notifications |
| Push | **Firebase** | Android app |
| In-app | **Redis pub/sub** | Real-time alerts |

---

## 10. Testing Stack

| Type | Tool | Rationale |
|---|---|---|
| Unit Tests | **pytest** | Python standard, fast |
| E2E Tests | **Playwright** | Cross-browser, reliable |
| API Tests | **httpx + pytest** | FastAPI test client |
| Load Tests | **Locust** | GPU load simulation |

---

## 11. Cost Optimization Strategy

- Aggressive caching (Redis + precomputed chapter summaries)
- Token window optimization (context compression)
- Smaller model for low-complexity queries
- Batch embedding generation (off-peak)
- Rate limits per user (prevent GPU waste)
