# Architecture

**Project:** AIaaS – AI Infrastructure for Educational Institutions  
**Version:** v0.1 (Pilot, Cloud-Ready Design)  
**Deployment Model:** Hybrid (Cloud Control Plane + Local AI Data Plane)

---

## 1. Architectural Philosophy

| # | Principle | Rationale |
|---|---|---|
| 1 | Multi-tenant by default | Every query, every table, every vector namespace scoped to `tenant_id` |
| 2 | Separation of concerns | ERP (deterministic) is separate from AI (probabilistic). AI never writes to ERP |
| 3 | AI as stateless inference | AI layer has no session state — makes scaling and failover simple |
| 4 | Cloud migration from day one | Control Plane on cloud VPS, Data Plane on local GPU — swap the GPU to cloud when ready |
| 5 | Horizontal scalability | AI workers can be added behind a load balancer without touching ERP |
| 6 | Provider abstraction | LLM, embedding, and vector store are abstracted behind interfaces — swap without rewrites |

---

## 2. System Topology

```
                         ┌─────────────────────┐
                         │   Web / Android UI  │
                         │   (Next.js + React)  │
                         └──────────┬──────────┘
                                    │ HTTPS
                         ┌──────────▼──────────┐
                         │   API Gateway       │
                         │  (Cloud VPS)        │
                         │  Nginx + FastAPI    │
                         └──────────┬──────────┘
                                    │
         ┌──────────────────────────┼──────────────────────────┐
         │                          │                          │
         ▼                          ▼                          ▼
┌────────────────┐        ┌────────────────┐        ┌────────────────┐
│ Auth Service   │        │ Core ERP       │        │ Usage/Billing  │
│ OAuth + JWT    │        │ PostgreSQL     │        │ Metrics        │
└────────────────┘        └────────────────┘        └────────────────┘
                                    │
                                    │ Secure Internal API
                                    ▼
         ┌────────────────────────────────────────────────┐
         │ AI Inference Node (Local GPU Server)          │
         │------------------------------------------------│
         │ Ingestion → Embedding → Vector DB → Rerank    │
         │ → LLM Inference → Structured Output           │
         └────────────────────────────────────────────────┘
```

---

## 3. Layered Architecture

### 3.1 Client Layer

**Web Application:**
- Framework: Next.js (React) with TypeScript
- Role-based dashboard: Student, Teacher, Admin views
- Session handling: JWT stored in HTTP-only cookies
- Charts: Recharts / Chart.js for analytics
- Rich text: TipTap for notes viewer

**Android (Phase 2):**
- React Native, same backend APIs
- Push notifications via Firebase Cloud Messaging

---

### 3.2 API Gateway Layer (Cloud VPS)

Responsibilities:
- TLS termination (HTTPS everywhere)
- JWT validation and extraction of `tenant_id` + `role`
- Role-based access control enforcement
- Tenant routing
- Rate limiting (Redis-backed)
- API request/response logging

**Stack:** Nginx → FastAPI (Python 3.11+) → Redis

> No business logic in the gateway. Only routing, validation, and enforcement.

---

### 3.3 Authentication & Authorization

**Authentication:**
- Google OAuth 2.0 (pilot)
- SAML SSO (enterprise, for school IT systems)
- JWT issued after successful authentication

**Authorization (RBAC):**

| Role | Permissions |
|---|---|
| Student | View own data, make AI queries (within quota) |
| Teacher | Manage assignments, upload notes, view class data |
| Admin | Full tenant control — users, AI settings, billing |
| Parent | View child's performance data (Phase 2) |

**Tenant isolation enforced at 3 levels:**
1. Database level — `WHERE tenant_id = :tenant_id` on every query
2. AI namespace level — vector DB scoped to `tenant_{id}`
3. API routing level — `tenant_id` extracted from JWT, never from client body

---

### 3.4 Core ERP Service

The deterministic, authoritative data layer. AI cannot write here.

| Module | Purpose |
|---|---|
| Student Management | Profiles, enrollment, class assignment |
| Attendance | Daily tracking with absence spike detection |
| Marks & Results | Exam entry, grading, performance trends |
| Assignments | Creation, submission, grading, AI help |
| Timetable | Weekly scheduling per class |
| Complaint Portal | Ticketing, status tracking, escalation |
| Lecture Library | YouTube embedding, transcript ingestion |

**Database:** PostgreSQL with strict `tenant_id` isolation on all tables.

---

### 3.5 AI Engine (Local GPU Server)

Runs as an independent microservice on the local GPU node.

#### Ingestion Service
- PDF parsing (PyMuPDF) + DOCX parsing (python-docx)
- YouTube transcript extraction
- Hierarchical chunking: Document → Section → Subsection → Paragraph
- Metadata tagging (subject, class, teacher, academic year)

#### Embedding Engine
- Model: `nomic-embed-text` (768-dim vectors)
- Embeddings generated async on upload
- Stored in tenant-isolated vector namespace

#### Retrieval Pipeline
```
Query → Embed → Vector Search (Top 8-12)
      → Rerank (cross-encoder)
      → Context Deduplication
      → Context Compression
```

#### LLM Inference Layer
- Model: Qwen 14B (4-bit quantized), Llama 3 8B fallback
- Structured prompting per task mode
- Citation enforcement (reject output if no citation in Q&A mode)
- Token budget management (~3800 tokens total)

#### Task Template Engine
Supports: Q&A, Study Guide, Quiz, Concept Map, Weak Topic Analysis

---

## 4. Provider Abstraction Layer

All AI components are abstracted behind interfaces for swappability:

| Component | Abstraction | Pilot Implementation | Scale Options |
|---|---|---|---|
| LLM | `BaseLLM` | Ollama (Qwen 14B) | vLLM, OpenAI, Azure, Gemini |
| Embeddings | `BaseEmbedding` | nomic-embed-text | OpenAI embeddings, Cohere |
| Vector Store | `BaseVectorStore` | FAISS (local) | Qdrant, Weaviate, Pinecone |
| Document Parser | `BaseParser` | PyMuPDF + python-docx | LlamaParse (agentic OCR) |

Configuration managed via YAML settings files per environment.

---

## 5. Event & Webhook System

Webhook events emitted on key operations for third-party integration:

| Event | Trigger |
|---|---|
| `student.enrolled` | New student added to tenant |
| `document.ingested` | Document processing complete |
| `ai.query.completed` | AI query answered |
| `exam.results.published` | Results finalized by teacher |
| `complaint.status.changed` | Complaint updated |

External systems can subscribe to these events via registered webhook URLs.

---

## 6. Scaling Strategy

| Phase | AI Infrastructure | ERP Infrastructure |
|---|---|---|
| **Phase 1 (Pilot)** | Single GPU, single vector DB, rate limiting | Single VPS, single PostgreSQL |
| **Phase 2 (Growth)** | Multiple inference workers, load balancer | Read replicas, caching layer |
| **Phase 3 (Enterprise)** | Kubernetes GPU pods, auto-scaling, distributed vector DB | Kubernetes-managed API, multi-region |

Because ERP and AI are fully separated, upgrading one doesn't require touching the other.

---

## 7. Reliability & Resilience

**Backups:**
- Daily PostgreSQL dump → offsite S3-compatible storage
- Vector DB snapshot every 24h
- Weekly restore test

**Monitoring:**
- GPU utilization + VRAM usage
- Query latency + error rates
- AI response time + token usage
- Per-tenant usage tracking

**Failover:**
- API health checks with auto-restart
- AI queue retry mechanism with timeout protection
- Secure tunnel auto-reconnect

---

## 8. Security Model

- HTTPS everywhere, TLS 1.2+
- JWT with short expiry (1h), stored in HTTP-only cookies
- Firewall-restricted AI node (no public IP)
- Rate limiting per user and per tenant
- Audit logs for all admin actions
- Data encryption at rest (LUKS or cloud-level)
- No student data used for external training

---

## 9. User Journey Map

```
Landing Page → Demo Request / Google Login
    │
    ▼ (Authentication)
Role Detection from JWT
    │
    ├── Student → Student Dashboard → AI Assistant / Attendance / Results
    ├── Teacher → Teacher Dashboard → Upload Notes / Enter Marks / View Insights
    └── Admin   → Admin Dashboard  → User Management / AI Analytics / Billing
```

---

## 10. Cloud Migration Path

The AI node can be migrated at any point:
1. Containerize with Docker
2. Deploy on Kubernetes with GPU node pools
3. Connect to managed GPU instances (A100 / L4)
4. Move vector DB to managed Qdrant / Weaviate

Because ERP and AI are decoupled, migration is **non-disruptive** to users.
