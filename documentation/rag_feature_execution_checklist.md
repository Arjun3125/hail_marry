# RAG Feature Execution Checklist

**Date:** 2026-03-29  
**Source report:** [rag_feature_evaluation_report.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/rag_feature_evaluation_report.md)  
**Purpose:** Convert the RAG evaluation findings into concrete implementation work mapped to code files.

## 1. Priority Order

Execute in this order:

1. notebook-scoped grounding for all study tools
2. retrieval observability and score thresholds
3. feature-level evidence binding for structured outputs
4. cache invalidation after ingestion
5. real textbook-backed evaluation harness
6. benchmark and reporting fixes

## 2. Workstream A: Notebook-Scoped Grounding

### Problem

Structured study tools currently operate with `tenant_id` and optional `subject_id`, but not `notebook_id`. That means generated quiz, flashcards, mind map, flowchart, and concept map outputs can mix all tenant materials instead of staying tied to one uploaded textbook.

### Files

- [ai_runtime.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/platform/schemas/ai_runtime.py)
- [study_tools.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/shared/ai_tools/study_tools.py)
- [ai.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/routes/ai.py)
- [students.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/academic/routes/students.py)
- [whatsapp_tools.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/shared/ai_tools/whatsapp_tools.py)
- [agent.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/whatsapp_bot/agent.py)

### Tasks

- Add `notebook_id` to `StudyToolGenerateRequest` and `InternalStudyToolGenerateRequest`.
- Pass `notebook_id` from all web routes that generate study tools.
- Pass `notebook_id` through WhatsApp tool wrappers when the session or request context includes a scoped upload source.
- Update `execute_study_tool()` so it forwards `notebook_id` into `InternalAIQueryRequest`.
- Ensure `retrieve_context()` uses notebook filtering consistently for all study-tool generation.

### Acceptance criteria

- A quiz generated from textbook A does not pull chunks from textbook B in the same tenant.
- Flowchart, mind map, and concept map all use the same notebook-filtered retrieval path.
- Tests cover notebook-scoped study-tool generation.

## 3. Workstream B: Retrieval Observability and Thresholding

### Problem

The retrieval stack stores relevance scores, but callers do not receive enough audit detail. There is also no minimum relevance threshold, so weak nearest neighbors can still drive generation.

### Files

- [retrieval.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/infrastructure/vector_store/retrieval.py)
- [workflows.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/workflows.py)
- [ai.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/routes/ai.py)
- [whatsapp_tools.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/shared/ai_tools/whatsapp_tools.py)

### Tasks

- Add configurable minimum score thresholds after vector search and after reranking.
- Return retrieval diagnostics in debug or audit mode:
  - document id
  - source
  - page
  - reranked score
  - whether the chunk was compressed
- Include top retrieved chunks in the API response when an audit flag is enabled.
- Add an `insufficient evidence` branch when no chunk clears the threshold.

### Acceptance criteria

- Low-relevance retrieval does not silently proceed to generation.
- Audit mode shows exactly which chunks and scores were used.
- Feature outputs can be manually traced back to retrieved passages.

## 4. Workstream C: Stronger Citation and Evidence Binding

### Problem

Citations are attached at response level, but most structured features do not bind individual output elements to source evidence.

### Files

- [workflows.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/workflows.py)
- [study_tools.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/shared/ai_tools/study_tools.py)
- [students.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/academic/routes/students.py)
- [whatsapp_tools.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/shared/ai_tools/whatsapp_tools.py)

### Tasks

- Update quiz prompt and normalization to require and validate per-question citations.
- Update flashcards prompt to require per-card citations.
- Update mind map schema to allow optional citation per node.
- Update concept map schema to require citation on edges or grouped relationships.
- Update flowchart prompt so each step is paired with a citation map or sidecar metadata object.
- Stop relying on `Sources:` footer injection as the main proof of grounding.

### Acceptance criteria

- Every quiz question has a citation.
- Every flashcard has a citation.
- Diagram features include traceable evidence for each major element.
- Validation fails when a structured artifact is missing required evidence fields.

## 5. Workstream D: Flowchart-Specific Hardening

### Problem

Flowchart generation is currently the weakest major feature. It produces plausible Mermaid output, but there is no strong guardrail ensuring the steps actually match the textbook section.

### Files

- [workflows.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/workflows.py)
- [study_tools.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/shared/ai_tools/study_tools.py)
- [whatsapp_tools.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/shared/ai_tools/whatsapp_tools.py)

### Tasks

- Replace raw Mermaid-only generation with a two-part output:
  - Mermaid graph
  - structured step list with citations
- Add prompt rules:
  - do not invent steps not present in context
  - preserve order from source when the source describes a process
  - if process structure is unclear, return a grounded summary instead of a forced flowchart
- Add a validator that checks:
  - Mermaid syntax validity
  - no empty nodes
  - every major step has supporting evidence

### Acceptance criteria

- Flowchart steps can be matched to retrieved chunks.
- Unsupported processes are rejected or downgraded to text summary.
- The feature no longer depends on response-level citations alone.

## 6. Workstream E: Cache Correctness After Ingestion

### Problem

Responses are cached by tenant, mode, subject, and query, but not by notebook. There is also no visible invalidation path after new uploads are ingested.

### Files

- [cache.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/infrastructure/llm/cache.py)
- [ai.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/routes/ai.py)
- [ingestion_workflows.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/ingestion_workflows.py)
- [students.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/academic/routes/students.py)
- [whatsapp_gateway.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/platform/services/whatsapp_gateway.py)

### Tasks

- Add `notebook_id` to cache keys where applicable.
- Invalidate tenant or notebook-scoped cache after document ingestion, URL ingestion, and YouTube ingestion.
- Ensure WhatsApp media ingestion also clears relevant cache entries.
- Add tests proving that a post-upload query returns updated grounded content instead of stale cached output.

### Acceptance criteria

- Uploading a textbook changes subsequent query results immediately.
- Notebook-specific generation does not reuse cached results from another notebook.

## 7. Workstream F: Real Textbook Evaluation Harness

### Problem

Current evaluation is synthetic or token-overlap based. There is no real acceptance harness for the exact scenario: uploaded textbook -> subtopic retrieval -> feature generation quality.

### Files

- [test_ragas_evaluation.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/tests/evaluation/test_ragas_evaluation.py)
- [test_retrieval_benchmark.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/tests/evaluation/test_retrieval_benchmark.py)
- New file recommended:
  - [test_textbook_feature_grounding.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/tests/evaluation/test_textbook_feature_grounding.py)

### Tasks

- Create a curated textbook-backed fixture with:
  - source chunks
  - target questions
  - expected concepts for Chapter 10.1
  - forbidden hallucinations
- Add per-feature assertions:
  - required concepts present
  - forbidden concepts absent
  - citations reference expected pages or section chunks
- Score:
  - relevance
  - accuracy
  - grounding
  - structural completeness

### Acceptance criteria

- Every major feature is exercised against the same textbook topic.
- Flowchart and concept map have explicit textbook-based acceptance checks.
- The suite fails when generation becomes generic or hallucinatory.

## 8. Workstream G: Benchmark and Reporting Fixes

### Problem

The current retrieval benchmark reports impossible `NDCG > 1`, and the printable report tests fail on Windows `cp1252` consoles because they print emoji.

### Files

- [test_retrieval_benchmark.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/tests/evaluation/test_retrieval_benchmark.py)
- [test_ragas_evaluation.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/tests/evaluation/test_ragas_evaluation.py)

### Tasks

- Fix the NDCG implementation so the metric is bounded correctly.
- Remove or sanitize emoji from console report output in tests.
- Keep printed reports ASCII-safe for Windows shells.
- Add a regression test asserting `0.0 <= ndcg_at_k(...) <= 1.0`.

### Acceptance criteria

- Report-print tests pass without UTF-8 environment overrides.
- Retrieval benchmark metrics are numerically valid.

## 9. Workstream H: Demo-Mode Safety

### Problem

Demo mode returns nongrounded placeholder content. If evaluation runs against demo mode, results are misleading.

### Files

- [ai.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/routes/ai.py)
- [students.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/academic/routes/students.py)
- New test or helper recommended in evaluation suite

### Tasks

- Add explicit demo-mode markers in all responses returned from demo branches.
- Add guardrails so evaluation tests fail fast if demo mode is enabled.
- Add logging or headers showing live vs demo execution.

### Acceptance criteria

- No evaluation can silently pass against demo-mode outputs.
- Demo responses are clearly distinguishable from grounded live results.

## 10. Recommended First Implementation Slice

Start here:

1. add `notebook_id` to study-tool schemas and routing
2. wire notebook filtering into all study-tool generation calls
3. add cache-key support for `notebook_id`
4. add one end-to-end test proving textbook-scoped quiz and flowchart generation use the same notebook

This is the highest-leverage change because it improves grounding quality across every major feature at once.

## 11. Release Gate for RAG Feature Reliability

Do not claim reliable textbook-grounded feature generation until all of the following are true:

- study tools are notebook-scoped
- retrieval diagnostics can be inspected
- structured features carry element-level evidence
- cache is invalidated after ingestion
- textbook-backed acceptance tests pass
- flowchart and concept-map outputs are validated against expected concepts

