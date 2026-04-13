# AI Engine Deep Design

**Project:** VidyaOS  
**Version:** v0.1 current implementation  
**Status:** Updated to match the repository runtime on 2026-04-12

---

## 1. Design Objectives

The current AI engine is designed to:
- provide retrieval-grounded answers from school materials
- preserve tenant isolation across retrieval, queueing, and usage tracking
- support multiple educational task modes through structured prompts
- keep ERP records authoritative and read-only from the AI layer
- support both synchronous requests and queued heavy workloads

## 2. Current AI Runtime Architecture

There are two execution paths.

### Synchronous public AI path

```text
public API request
  -> ai/routes/ai.py
  -> ai_gateway.py
  -> workflows.py
      -> embed
      -> retrieve from tenant-scoped vector store
      -> rerank, dedup, compress
      -> prompt assembly
      -> apply language, response length, and expertise-level controls
      -> Ollama generation
      -> sanitize plus citation handling
  -> AIQuery log plus trace events plus optional webhook
```

### Queued heavy-work path

```text
request
  -> Redis enqueue
  -> worker claim
  -> ai_queue.py
  -> ai_gateway.py
  -> workflows.py or ingestion workflow
  -> queue metrics plus audit history plus trace events
  -> result polling
```

Important clarification:
- the current repo does not route either path through a standalone AI-service process

## 3. Supported Sources

Implemented in the active ingestion and retrieval surface:
- PDF
- DOCX
- YouTube transcript ingestion
- URL ingestion
- DuckDuckGo-powered discovery search
- image-to-PDF preprocessing for student uploads

Present in code with partial wiring or dependency requirements:
- PPTX handling
- XLSX handling
- Google Docs ingestion
- Notion ingestion

## 4. Chunking and Retrieval

### Chunking
- parsed content is chunked into retrieval-friendly slices
- metadata can include document, page, subject, and source details

### Retrieval
- query embedding through the internal embedding layer
- FAISS semantic search by default
- optional Qdrant backend
- optional cross-encoder reranking when dependencies are available
- deduplication and context compression before prompting

## 5. Current Task Surface

### Text generation modes (12)
- Q&A
- Study Guide
- Quiz
- Concept Map
- Weak Topic
- Flowchart
- Mind Map
- Flashcards
- Socratic
- Perturbation
- Debate
- Essay Review

### Additional AI outputs
- Audio overview
- Video overview

### Teacher-specific AI workflows
- assessment generation
- doubt heatmap aggregation

### Additional orchestration
- HyDE query transform
- knowledge graph context retrieval
- workflow orchestration through `/api/ai/workflows`

## 6. Model Configuration

### LLM
- primary runtime: Ollama over HTTP
- model selection is config-driven

### Embeddings
- current embedding path targets `nomic-embed-text`

## 7. Citation Behavior

Current behavior is grounded and citation-aware, but not a universal hard-block policy.

What happens now:
- retrieved chunks are formatted with citation markers
- responses are checked for citation presence
- when citations are missing but grounded sources exist, the system can append source fallback text
- citation enrichment to clickable document URLs is applied in the main API response flow

## 8. Queueing and Control Plane

Implemented now:
- Redis-backed queue
- tenant-fair scheduling
- static priority ordering by job type
- queue admission limits
- cancel, retry, and dead-letter controls
- admin queue metrics and audit history

Current durability model:
- live queue state lives in Redis
- durable lifecycle state is mirrored into relational `ai_jobs` and `ai_job_events`
- queue lifecycle actions are written to `audit_logs`

## 9. Notebook Integration

Implemented now:
- `notebook_id` is logged on AI query history when provided
- generated quiz/flashcard/mindmap-like outputs can be persisted per notebook
- notebook CRUD and generated-content APIs exist

Known limitation:
- notebook-aware retrieval filtering is only partially wired in the current core RAG path

## 10. Logging, Tracing, and Reviewability

Current observability includes:
- structured logs
- per-job event timelines
- `trace_id` propagation across API and worker flows
- persistent trace events
- admin trace viewer
- alert evaluation and dispatch

## 11. Current Limitations

- FAISS remains the default local-file vector path
- queue results remain Redis-TTL-backed even though lifecycle state is mirrored durably
- `ai_grade` remains narrower than the broader grading vision
- the OpenAI-compatible API has a different provider/auth path than the core RAG pipeline

Use this document as the source of truth for the current AI runtime in the repository.
