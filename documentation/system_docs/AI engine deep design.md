# AI Engine Deep Design

**Project:** AIaaS – AI Infrastructure for Educational Institutions  
**Version:** v0.1 (Pilot → Cloud-Scale Ready)  
**Deployment:** Local GPU (Pilot) → Distributed GPU Cluster (Scale)

---

## 1. Design Objectives

The AI Engine must:

1. Provide **NotebookLM-level** grounded document intelligence
2. Operate in **strict multi-tenant isolation**
3. Enforce **citation-first outputs** — no ungrounded claims
4. Optimize **GPU utilization** for cost efficiency
5. Remain **cloud-migration ready** from day one
6. **Never modify** authoritative ERP records
7. Support **provider abstraction** for LLM/embedding swapping

> AI is augmentation layer only. It reads, retrieves, and reasons. It does not write to ERP.

---

## 2. AI System Architecture

```
User Query
    │
    ▼
Query Router (task mode detection)
    │
    ▼
Embedding Layer (nomic-embed-text, 768-dim)
    │
    ▼
Vector Search (Top 8–12, namespace-isolated)
    │
    ▼
Reranker (cross-encoder, optional)
    │
    ▼
Context Builder (dedup + compression)
    │
    ▼
Prompt Template Engine (per task mode)
    │
    ▼
LLM Inference (Qwen 14B, 4-bit quantized)
    │
    ▼
Response Formatter + Citation Injector
    │
    ▼
Output Sanitization + Logging
```

---

## 3. Multi-Tenant Isolation

Each tenant has:
- Unique `tenant_id`
- Isolated vector namespace: `tenant_{tenant_id}`
- Independent document index
- Independent usage tracking

**Hard constraint:** No cross-namespace retrieval permitted.

---

## 4. Document Ingestion Pipeline

### 4.1 Supported Sources

| Source | Parser | Status |
|---|---|---|
| PDF notes | PyMuPDF (fitz) | ✅ Pilot |
| DOCX files | python-docx | ✅ Pilot |
| YouTube transcripts | YouTube Transcript API | ✅ Pilot |
| Text uploads | Direct text ingestion | ✅ Pilot |
| Google Docs | API connector | 🔮 Phase 2 |
| PPTX slides | python-pptx | 🔮 Phase 2 |

### 4.2 Preprocessing Pipeline

```
Raw Document
    → Text Extraction
    → Cleaning (remove headers, noise, boilerplate)
    → Hierarchical Segmentation
    → Metadata Attachment
    → Chunk Storage + Embedding Generation
```

### 4.3 Hierarchical Chunking Strategy

**Flat chunking is insufficient.** Instead:

Document → Section → Subsection → Paragraph

Each chunk stores:
- `tenant_id`, `document_id`, `chunk_id`
- `page_number`, `section_title`
- `subject`, `class_id`, `teacher_id`
- `academic_year`

**Chunk size:** 300–600 tokens  
**Overlap:** 50–100 tokens

---

## 5. Embedding Engine

**Model:** nomic-embed-text (768-dim, local)

```
Chunk → Embedding Model → 768-dim Vector → Vector DB
```

Embeddings generated:
- On document upload (async background job)
- On transcript ingestion
- Batch processing for bulk imports

Stored in tenant namespace.

---

## 6. Retrieval Pipeline

### 6.1 Query Flow
```
Student Query → Query Embedding → Vector Search (Top 8–12)
```

### 6.2 Reranking (Recommended)
- Cross-encoder model: `cross-encoder/ms-marco-MiniLM-L-2-v2`
- Scores semantic relevance of retrieved chunks
- Select top 5–8 chunks post-rerank
- Significantly improves answer quality

### 6.3 Context Deduplication
Remove: redundant chunks, near-identical overlaps, cross-page repetition

### 6.4 Context Compression
If context exceeds LLM token limit:
- Summarize lower-ranked chunks
- Keep highest semantic weight chunks raw
- Goal: maintain relevance under token budget

### 6.5 Query Transform (Advanced)
- **HyDE** (Hypothetical Document Embedding): generate hypothetical answer, embed it, search against that
- **Sub-question decomposition**: break complex queries into atomic sub-questions
- Configurable via settings YAML

---

## 7. Prompt Template Engine

AI must NOT operate in free-form mode. All responses pass through structured templates.

### Task Modes

| Mode | Description | Output Format |
|---|---|---|
| Q&A | Grounded question answering | Text + citations |
| Study Guide | Structured topic summary | Sections + citations |
| Quiz | Question generation | JSON (questions, options, correct answer) |
| Concept Map | Graph structure | JSON (nodes, edges) |
| Weak Topic | Performance-based insight | Text + targeted recommendations |

### Example Q&A Template

```
You are an academic assistant for {subject}.
Answer ONLY using the provided context.
Cite using [Document_Page] format.
If the answer is not in the context, say: "Not found in provided materials."
Do not speculate or make up information.
```

---

## 8. LLM Inference Layer

### 8.1 Model Selection

| Priority | Model | VRAM | Speed |
|---|---|---|---|
| Primary | Qwen 14B (4-bit quantized) | ~12GB | Moderate |
| Fallback | Llama 3 8B (4-bit) | ~6GB | Fast |

### 8.2 Token Budget

| Component | Tokens |
|---|---|
| Query | ~200 |
| Context | ~3000 |
| Output | ~600 |
| **Total** | **~3800** |

Strict caps enforced. Over-budget requests → context trimmed automatically.

### 8.3 GPU Utilization Strategy
- Queue-based request handling (Redis queue)
- Max concurrency limit (configurable)
- Timeout protection (30s default)
- Batch embedding generation (off-peak hours)

---

## 9. Citation Enforcement Layer

Post-processing step on every Q&A response:

1. Detect claim spans in the response
2. Attach citation markers from source chunks
3. Validate citation presence
4. **Reject output if no citation** (for Q&A mode)

Example output:
```
Photosynthesis occurs in chloroplasts. [Bio_Ch3_p12]
Light reactions happen in the thylakoid membrane. [Bio_Ch3_p14]
```

---

## 10. Structured Output Engine

### Quiz Mode
```json
{
  "questions": [
    {
      "question": "What organelle is responsible for photosynthesis?",
      "options": ["Mitochondria", "Chloroplast", "Nucleus", "Ribosome"],
      "correct": "B",
      "citation": "Bio_Ch3_p12"
    }
  ]
}
```

### Concept Map Mode
```json
{
  "nodes": [
    {"id": "1", "label": "Photosynthesis"},
    {"id": "2", "label": "Chloroplast"},
    {"id": "3", "label": "Light Reactions"}
  ],
  "edges": [
    {"from": "1", "to": "2", "label": "occurs in"},
    {"from": "1", "to": "3", "label": "includes"}
  ]
}
```

---

## 11. Weak Topic Intelligence

Uses ERP data (marks, subject performance, attendance) to personalize:

```
Low Algebra Score (from ERP)
    → Fetch Algebra documents (from vector DB)
    → Generate Focused Study Guide
    → Generate Targeted Quiz
    → Deliver to student dashboard
```

This is the key differentiator over generic NotebookLM or ChatGPT.

---

## 12. Caching Strategy

| Cache Target | TTL | Backend |
|---|---|---|
| Embeddings | Permanent (until doc update) | Disk |
| Top 20 frequent queries per subject | 24h | Redis |
| Study guides per chapter | 7 days | Redis |
| Quiz templates | 7 days | Redis |

---

## 13. Rate Limiting

Per student:
- X queries per day (plan-dependent)
- Burst limit: 5 per minute
- Token usage tracking per query

Prevents GPU overload and abuse.

---

## 14. AI Query Tracing

Every AI query gets a `trace_id` that links:
- Query text
- Embedding vector
- Retrieved chunks (with scores)
- Reranked results
- Final prompt sent to LLM
- Raw LLM response
- Post-processed response
- Citations injected
- Response time + token usage

Admins can view traces via the AI Quality Review panel.

---

## 15. Configuration (YAML-based)

```yaml
rag:
  similarity_top_k: 8
  rerank:
    enabled: true
    model: cross-encoder/ms-marco-MiniLM-L-2-v2
    top_n: 5

llm:
  mode: ollama
  model: qwen:14b
  max_new_tokens: 600
  context_window: 3900
  temperature: 0.1

embedding:
  mode: local
  model: nomic-embed-text
  embed_dim: 768

vectorstore:
  database: faiss
  # Scale: qdrant
```

Override per environment via `settings-{env}.yaml`.

---

## 16. Failure Handling

| Scenario | Action |
|---|---|
| No relevant chunks found | Return controlled fallback: "Not found in materials" |
| GPU overload | Queue request, notify user of wait time |
| Timeout (>30s) | Retry once, then return error |
| Hallucination detected | Reject output, log for review |
| Embedding service down | Queue documents, retry when available |

**Never return an ungrounded answer silently.**

---

## 17. Scaling Path

| Phase | Infrastructure |
|---|---|
| Pilot | Single GPU, single vector DB |
| Growth | Multiple inference workers, load balancer |
| Enterprise | Kubernetes GPU pods, auto-scaling, distributed vector DB, model specialization per subject |
