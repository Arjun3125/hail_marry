# AI Engine Deep Design

**Project:** VidyaOS  
**Version:** v0.1 current implementation  
**Status:** Updated to match the repository runtime on 2026-03-06

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

Implemented now:
- PDF
- DOCX
- YouTube transcript ingestion
- URL ingestion (via discovery or direct URL)
- DuckDuckGo-powered educational source discovery

Not yet implemented:
- Google Docs connector
- PPTX connector
- OCR-heavy parsing pipeline

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

### Personalization controls
All text generation modes support:
- **Language** — response language selection
- **Response length** — short / medium / detailed
- **Expertise level** — beginner / intermediate / advanced

Applied via `_apply_language_and_style()` before prompt submission.

### Queued generation
Used in the product for:
- student study-tool generation
- audio overview
- video overview
- teacher assessment generation
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
- this is a practical observability stack, not yet a fully managed external incident pipeline with email / pager escalation

## 11. Execution Limits

Important current limits:
- FAISS is still local-file based and suited to pilot or modest single-node deployments
- queue results remain Redis TTL-based even though lifecycle state and event history are durable

## 12. Roadmap, Not Current Implementation

Still future-state:
- broader operator tooling for queue replay / pause / drain
- service-grade vector backend
- deeper trace explorer with prompt and retrieval replay

Use this document as the source of truth for the current AI runtime.
