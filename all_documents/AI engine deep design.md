# AI Engine Deep Design

**Project:** VidyaOS  
**Version:** v0.1 current implementation  
**Status:** Updated to match the repository runtime on 2026-03-25

---

## 1. Design Objectives

The current AI engine is designed to:
- provide retrieval-grounded answers from school materials
- preserve tenant isolation across retrieval, queueing, and usage tracking
- support multiple educational task modes through structured prompts
- keep ERP records authoritative and read-only from the AI layer
- expose a service boundary for public synchronous generation

## 2. Current AI Runtime Architecture

There are now two execution paths.

### Synchronous public AI path
```text
public API request
  -> AI gateway
  -> dedicated AI service
      -> embed
      -> retrieve from tenant-scoped FAISS store
      -> rerank / dedup / compress
      -> prompt template assembly
      -> apply language, response length, and expertise level personalization
      -> Ollama generation
      -> sanitize + citation validation / source fallback
  -> AIQuery log + trace events + webhook
```

### Queued heavy-work path
```text
request
  -> Redis enqueue
  -> worker claim
  -> dispatch queued workflow to dedicated AI service
  -> queue metrics + audit history + trace events
  -> result polling
```

## 3. Supported Sources

Implemented in the active ingestion pipeline:
- PDF
- DOCX
- YouTube transcript ingestion
- URL ingestion (via discovery or direct URL)
- DuckDuckGo-powered educational source discovery
- Image OCR to PDF for student uploads (image-to-PDF preprocessing)

Present in code but not yet wired into ingestion workflows:
- PPTX connector
- Excel connector
- Google Docs connector
- Notion connector

## 4. Chunking and Retrieval

### Chunking
- hierarchical chunking for parsed content
- metadata includes document, page, subject, and source details where available

### Retrieval
- query embedding with `nomic-embed-text`
- FAISS semantic search over tenant-specific vector files
- optional cross-encoder reranking when dependencies are available
- deduplication and context compression before prompting

## 5. Current Task Surface

### Text generation modes (13)
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
- Career Simulation

### Additional AI outputs
- Audio overview (podcast-style dialogue between two hosts)
- Video overview (narrated slide presentation)

### Teacher-specific AI workflows
- Assessment generation (NCERT-aligned formative assessments via RAG + LLM)
- Doubt heatmap data aggregation

### Integrated into Main Query Flow
The primary AI request pipeline now applies:
- HyDE query transform
- Knowledge graph context retrieval
- Agent orchestration workflows (via /api/ai/workflows)

### Personalization controls
- ingestion-heavy flows (document, YouTube, URL)

## 6. Model Configuration

Current default configuration comes from `backend/settings.yaml` and environment overrides.

### LLM
- provider path: Ollama over HTTP
- default model: `llama3.2`
- fallback model: configurable, default currently also `llama3.2`

### Embeddings
- model: `nomic-embed-text`
- dimension: 768

## 7. Citation Behavior

Current behavior is grounded and citation-aware, but not a universal hard-reject policy.

What happens now:
- retrieved chunks are formatted with citation markers
- responses are checked for citations
- when citations are missing but grounded sources exist, the system can append source fallback text rather than reject every response outright
- citation enrichment to clickable document URLs exists as a helper but is not applied in the main response flow

## 8. Queueing and Control Plane

Implemented now:
- Redis-backed queue
- tenant-fair scheduling
- static priority ordering by job type
- queue admission limits
- cancel / retry / dead-letter controls
- admin queue metrics and audit history

Current durability model:
- live queue state lives in Redis
- durable lifecycle state is mirrored into relational `ai_jobs` and `ai_job_events`
- queue lifecycle actions are also written to `audit_logs`

Current limitation:
- `ai_grade` jobs return OCR extraction + review_required output; automated rubric scoring is not implemented yet

## 9. Spaced Repetition Integration

Implemented now:
- SM-2 algorithm for review card scheduling
- Students create review cards tied to topics and subjects
- Quality self-rating (1=Again to 5=Perfect) adjusts interval and ease factor
- Next review date calculated from interval and ease factor
- Due and upcoming cards surfaced in student UI

## 10. Logging, Tracing, and Reviewability

Current query and job observability includes:
- structured logs
- per-job event timelines
- `trace_id` propagation across API, queue, worker, and AI service
- persistent trace events
- admin trace viewer
- alert evaluation plus webhook dispatch

Current limitation:
- observability includes email/SMS alert transports, but full pager escalation is still external

## 11. Execution Limits

Important current limits:
- FAISS is still local-file based (Qdrant is available for larger, multi-node deployments)
- queue results remain Redis TTL-based even though lifecycle state and event history are durable

## 12. Roadmap, Not Current Implementation

Still future-state:
- deeper trace explorer with prompt and retrieval replay
- automated rubric scoring for AI grading

Use this document as the source of truth for the current AI runtime.
