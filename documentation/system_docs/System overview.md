# System Overview

**Project Name:** AIaaS – AI Infrastructure for Educational Institutions  
**Version:** v0.1 (Pilot Architecture)  
**Deployment Model:** Hybrid (Cloud ERP + Local AI Compute Node)  
**Target Stage:** 2–3 Pilot Schools  

---

## 1. Project Vision

AIaaS is a verticalized, multi-tenant AI infrastructure layer that gives schools the power of **NotebookLM-level document intelligence** — grounded answers from their own curriculum materials, citation-enforced, and completely private.

> **Strategic Identity:**  
> AIaaS is not an ERP with AI features.  
> It is an **institutional AI governance platform** with ERP as the interface shell.

---

## 2. Structural Pillars

These are the 5 non-negotiable principles that define every engineering and design decision:

| # | Pillar | Meaning |
|---|---|---|
| 1 | **Multi-Tenant by Default** | Every school is fully isolated — data, AI, billing. No cross-tenant leakage, ever. |
| 2 | **AI as Augmentation, Not Authority** | AI reads ERP data but never writes to it. Academic records remain deterministic and authoritative. |
| 3 | **Citation-First Intelligence** | Every AI answer must cite its source document and page. Ungrounded answers are rejected. |
| 4 | **Cloud-Ready from Day One** | Architecture separates control plane (cloud) and data plane (GPU) so scaling requires no rewrite. |
| 5 | **Security is a Constraint, Not a Feature** | Tenant isolation, RBAC, audit logging, and encrypted storage are built into every layer from pilot. |

---

## 3. Core System Components

AIaaS combines three major systems:

### 3.1 Institutional ERP (Deterministic Data Layer)
Handles the structured, authoritative operations a school needs daily:
- **Student Management** — profiles, enrollment, class assignment
- **Attendance Tracking** — daily records with absence spike detection
- **Marks & Results** — exam entry, grading, performance trends
- **Assignment Tracker** — creation, submission, feedback loop
- **Timetable Engine** — weekly scheduling per class
- **Complaint Portal** — ticketing with status tracking and escalation
- **Lecture Library** — YouTube embedding, metadata tagging, transcript ingestion

### 3.2 AI Intelligence Engine (Probabilistic Layer)
Provides document-grounded AI capabilities that sit on top of curriculum materials:
- **Document Ingestion** — PDF, DOCX, YouTube transcript parsing
- **Hierarchical Chunking** — Document → Section → Subsection → Paragraph
- **Embedding Generation** — 768-dim vectors via local model (nomic-embed-text)
- **Semantic Retrieval** — Top-K vector search with optional reranking
- **LLM Inference** — Quantized 14B model, structured prompting, citation enforcement
- **Task Modes** — Q&A, Study Guide, Quiz Generation, Concept Map, Weak Topic Analysis

### 3.3 Admin Governance Dashboard
The control center for institutional oversight:
- Real-time KPI monitoring (active users, AI queries, attendance)
- AI usage analytics and cost tracking
- AI quality review (sample responses, flagged answers)
- User management and role control
- Security monitoring and audit logs

---

## 4. Core Operational Flows

### Student AI Query Flow
```
Student submits question
    → API validates JWT + tenant
    → Request routed to AI microservice
    → Retrieval from tenant vector DB
    → Reranking + context assembly
    → LLM inference with structured prompt
    → Citation injection
    → Response returned to student
    → Usage logged for billing
```

### Weak Topic Intelligence Flow
```
Low Algebra Score detected from ERP marks
    → Fetch Algebra notes from vector DB
    → Generate Focused Study Guide
    → Generate Targeted Quiz
    → Deliver personalized remediation to student
```

### Document Ingestion Flow
```
Teacher uploads PDF or pastes YouTube URL
    → Text extraction + cleaning
    → Hierarchical segmentation
    → Metadata attachment (subject, class, teacher)
    → Embedding generation (async)
    → Storage in tenant-isolated vector namespace
```

---

## 5. Multi-Tenant Model

Each school (tenant) gets:

| Resource | Isolation Method |
|---|---|
| Database records | `tenant_id` column on all tables + WHERE clause enforcement |
| AI vectors | Separate vector namespace (`tenant_{id}`) |
| Usage tracking | Independent query counting + daily limits |
| Configuration | Configurable AI credits, plan tier, max students |

**Hard rule:** No cross-tenant data mixing. Not in the database, not in the vector store, not in the API response.

---

## 6. Revenue Model

Tier-based pricing for pilot:

| Tier | Features |
|---|---|
| **Basic** | ERP only (attendance, marks, timetable) |
| **Pro** | AI Q&A + Study Guide + Quiz generation |
| **Advanced** | AI analytics + weak topic intelligence + concept maps |
| **Enterprise** | Custom models + SLA + dedicated support |

Optional: Usage-based AI credit system for per-query billing.

---

## 7. Key Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Power outage (local GPU) | UPS + auto-restart service |
| Hardware failure | Daily backup + offsite copy |
| Latency spike | Request queueing + rate limiting |
| GPU overload | Tenant-level daily query caps |
| Data breach | Strict isolation + firewall + audit logging |

---

## 8. Long-Term Moat

The architecture enables capabilities that compound over time:
- **Multi-year student learning memory** — performance history across academic years
- **Performance-based adaptive tutoring** — AI that learns what each student struggles with
- **Institutional knowledge graph** — connected concepts across curriculum
- **Proprietary evaluation benchmarks** — AI accuracy metrics per subject
- **Cross-school anonymized benchmarking** — opt-in comparison across institutions

---

## 9. Strategic Position

> *A citation-grounded, multi-tenant, performance-aware educational reasoning layer.*

This transitions AIaaS from tool → infrastructure layer. The long-term value lies not in the chatbot, but in the data accumulation and personalization loops that no competitor can replicate overnight.
