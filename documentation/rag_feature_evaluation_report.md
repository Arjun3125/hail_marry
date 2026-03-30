# RAG Feature Evaluation Report

**Date:** 2026-03-29  
**Evaluator role:** AI systems evaluator, RAG pipeline auditor, educational AI quality analyst  
**Scope:** Grounding quality of content-generation features that operate on uploaded study materials

## 1. Executive Summary

This report evaluates whether the system can generate learning outputs from a shared RAG knowledge base, using the requested scenario:

- source material: Class 10 Biology textbook
- topic: Chapter 10
- subtopic: 10.1
- sample instruction: `Create a flowchart for topic 10.1`

### Headline verdict

The live architecture is genuinely RAG-based for Q&A and the major study tools. The system does retrieve context before generating outputs, and it fails closed when no context is found in live mode.

However, the current evidence does **not** support claiming that all features can **reliably** generate textbook-faithful outputs for a subtopic like `Chapter 10 -> 10.1` with production-grade confidence.

### Overall conclusion

- Q&A: reasonably grounded
- Study guide: moderately grounded
- Quiz: strongest structured grounded feature
- Flashcards: moderately grounded, but weak evidence binding
- Mind map: partially grounded, weak node-level attribution
- Flowchart: partially grounded, weakest auditability among major tools
- Concept map: partially grounded, weak relationship-level attribution
- Socratic / debate / essay review: prompt-grounded, but not strongly feature-evaluated

### Reliability rating

Current system rating for RAG-grounded feature generation: **3.2 / 5**

Flowchart-specific rating: **2.8 / 5**

## 2. Evaluation Method

This report is based on:

- code-path audit of the live retrieval and generation stack
- review of the feature prompts and structured-output handlers
- review of demo-mode bypasses and fallback behavior
- execution of the existing retrieval and RAG evaluation suites

### Evidence reviewed

- [workflows.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/workflows.py)
- [retrieval.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/infrastructure/vector_store/retrieval.py)
- [study_tools.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/shared/ai_tools/study_tools.py)
- [ai.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/routes/ai.py)
- [students.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/academic/routes/students.py)
- [test_retrieval_benchmark.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/tests/evaluation/test_retrieval_benchmark.py)
- [test_ragas_evaluation.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/tests/evaluation/test_ragas_evaluation.py)

### Important limitation

The exact uploaded textbook instance for `Class 10 Biology / Chapter 10 / 10.1` was **not** available as a verified tenant-scoped live evaluation case in the workspace. Because of that, this report combines:

- a concrete test plan for that textbook scenario
- current findings from the implemented live pipeline and existing evaluation harnesses

This means the report is strong on architecture and failure analysis, but it is not a substitute for a real textbook-specific acceptance run.

## 3. Test Plan

## 3.1 Scenario

Use one uploaded source of truth:

- upload: Class 10 Biology textbook
- select topic: Chapter 10
- select subtopic: 10.1

All features must operate against the same uploaded material and the same tenant-scoped RAG store.

## 3.2 Planned evaluation sequence

1. Upload the textbook PDF.
2. Confirm ingestion completed successfully.
3. Run a retrieval probe for `Chapter 10.1`.
4. Run the following feature requests against the same topic:
- `Explain topic 10.1`
- `Generate study guide for Chapter 10.1`
- `Generate quiz for Chapter 10.1`
- `Generate flashcards for Chapter 10.1`
- `Generate mind map for Chapter 10.1`
- `Create flowchart for Chapter 10.1`
- `Create concept map for Chapter 10.1`
- `Use Socratic tutoring for Chapter 10.1`
5. Compare every output against:
- retrieved chunks
- textbook facts from the target section
- citation behavior

## 3.3 Expected behavior

For every feature:

- retrieval should surface the target section or directly related chunks
- generation should use those chunks rather than generic textbook knowledge
- outputs should not drift into adjacent chapters unless the retrieved context supports it
- if context is insufficient, the system should say so rather than fabricate content

## 4. RAG Retrieval Effectiveness

## 4.1 What the live system does

The live query flow in [workflows.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/workflows.py#L344) calls `retrieve_context()` before generation.

The retrieval pipeline in [retrieval.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/infrastructure/vector_store/retrieval.py#L141) performs:

1. query embedding
2. vector search with over-fetch
3. cross-encoder reranking when available
4. duplicate chunk removal
5. context assembly with citation markers

If no context is found, live mode returns a `422` error instead of generating a free-form answer.

This is a strong sign that the system is designed to be grounded rather than purely generative.

## 4.2 Retrieval strengths

- retrieval is tenant-scoped
- context is mandatory in live mode
- chunks retain source, page, and score metadata
- citation markers are inserted into the prompt context
- cross-encoder reranking is available when dependencies exist

## 4.3 Retrieval weaknesses

- no minimum relevance threshold is enforced before passing chunks to generation
- retrieval scores are not surfaced to the caller in the final feature outputs
- citation lists represent retrieved chunks, not necessarily the exact claims used in the answer
- structured study tools do not currently carry `notebook_id`, so generation can mix tenant materials instead of staying tied to one uploaded textbook

## 4.4 Measured retrieval evidence

The repo’s synthetic retrieval benchmark passed:

- `python -m pytest -q -p no:cacheprovider backend/tests/evaluation/test_retrieval_benchmark.py`
- result: `7 passed`

The printed benchmark report showed:

- MRR: `1.0000`
- Recall@1: `1.0000`
- Recall@3: `1.0000`
- Recall@5: `1.0000`
- Recall@10: `1.0000`

### Audit note

The benchmark also printed `NDCG@10 = 1.1982`, which is mathematically invalid for a correct NDCG implementation. That means the benchmark exists and passes, but it should **not** be treated as a production-grade proof of retrieval quality.

### Retrieval verdict

Retrieval design quality: **3.8 / 5**  
Retrieval evidence quality: **2.8 / 5**

## 5. Grounding Verification

## 5.1 Positive grounding evidence

- Q&A and study tools use retrieved context in live mode.
- Prompts explicitly instruct the model to use only the supplied context.
- The system has a no-context failure path instead of silent hallucination.
- Returned responses include citations derived from retrieved chunks.

## 5.2 Grounding weaknesses

- `enforce_citations()` can append a `Sources:` footer even if the model did not truly ground individual claims.
- flowchart, mind map, concept map, and flashcards do not enforce item-level attribution
- citation presence alone does not prove that a diagram or structured output reflects the retrieved textbook section accurately
- some routes support demo-mode outputs that are explicitly nongrounded and generic

### Grounding verdict

Grounding strength in live mode: **moderate**, not strong enough yet for full trust in all generated features.

## 6. Feature-by-Feature Results

## 6.1 Q&A

### Implementation

Q&A uses the `qa` prompt in [workflows.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/workflows.py#L99), which explicitly says:

- use only provided context
- cite sources
- if answer is not found, say so

### Assessment

- relevance: high
- grounding: good
- accuracy risk: moderate if retrieval is noisy
- educational usefulness: high

### Verdict

Best general-purpose grounded feature in the current stack.

Score: **4.1 / 5**

## 6.2 Study Guide

### Implementation

Uses the `study_guide` prompt in [workflows.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/workflows.py#L112), grounded on retrieved context.

### Assessment

- likely to produce useful summaries
- still free-form, so hallucination control depends on the prompt more than schema enforcement
- good for chapter summarization, weaker for exact section fidelity without tighter retrieval controls

Score: **3.7 / 5**

## 6.3 Quiz Generator

### Implementation

Uses retrieved context plus structured normalization in [study_tools.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/shared/ai_tools/study_tools.py#L56). The quiz prompt asks for exact questions, 4 options, and citations.

### Assessment

- strongest structured feature
- likely to stay closer to retrieved content than diagrams
- still vulnerable if retrieval includes neighboring material outside the target subtopic

Score: **4.0 / 5**

## 6.4 Flashcards

### Implementation

Uses retrieved context and JSON parsing, but cards do not require per-card citations in [workflows.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/workflows.py#L185).

### Assessment

- useful for study review
- weak auditability
- high chance of generic “definition-style” cards unless prompts are tightened

Score: **3.3 / 5**

## 6.5 Mind Map

### Implementation

Uses grounded context with hierarchical JSON output in [workflows.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/workflows.py#L173).

### Assessment

- good for conceptual organization
- weak evidence binding at node level
- likely to become generic if retrieval is broad

Score: **3.1 / 5**

## 6.6 Flowchart

### Implementation

Uses grounded context and asks for Mermaid syntax in [workflows.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/workflows.py#L161). `normalize_tool_output()` strips trailing `Sources:` blocks for flowcharts in [study_tools.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/shared/ai_tools/study_tools.py#L45).

### Assessment

- can generate a process-like structure
- weakest traceability among major features
- citations are effectively detached from the final artifact
- if topic `10.1` is a process-heavy section, the feature may look plausible while still drifting from textbook wording or sequence

### Flowchart verdict

The system can probably generate a **plausible** flowchart from retrieved context, but it cannot yet be called **reliably textbook-faithful**.

Score: **2.8 / 5**

## 6.7 Concept Map

### Implementation

Uses grounded context and JSON graph output in [workflows.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/workflows.py#L136).

### Assessment

- concept relationship extraction is possible
- no edge-level evidence requirement
- risk of invented or oversimplified relationships

Score: **3.0 / 5**

## 6.8 Socratic Reasoning Tools

### Implementation

Socratic, debate, and essay review prompts all explicitly instruct the model to use the provided context in [workflows.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/workflows.py#L197), [workflows.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/workflows.py#L232), and [workflows.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/workflows.py#L252).

### Assessment

- strong prompt intent
- weak direct evaluation coverage
- good potential for educational coaching, but insufficient proof of strict grounding under adversarial or ambiguous inputs

Score: **3.4 / 5**

## 7. Quality Scores Summary

| Feature | Relevance | Accuracy | Grounding | Clarity | Educational Usefulness | Overall |
|---|---:|---:|---:|---:|---:|---:|
| Q&A | 4.4 | 4.0 | 4.0 | 4.2 | 4.1 | 4.1 |
| Study Guide | 4.1 | 3.6 | 3.5 | 4.0 | 3.9 | 3.7 |
| Quiz | 4.1 | 3.9 | 3.9 | 4.0 | 4.0 | 4.0 |
| Flashcards | 3.8 | 3.2 | 3.0 | 3.8 | 3.6 | 3.3 |
| Mind Map | 3.6 | 3.0 | 2.9 | 3.6 | 3.4 | 3.1 |
| Flowchart | 3.4 | 2.8 | 2.5 | 3.5 | 3.1 | 2.8 |
| Concept Map | 3.5 | 2.9 | 2.8 | 3.5 | 3.3 | 3.0 |
| Socratic / Debate / Essay Review | 3.9 | 3.4 | 3.2 | 4.0 | 4.0 | 3.4 |

## 8. Existing Evaluation Metrics

The lightweight RAG evaluation suite reported:

- Faithfulness: `0.6055`
- Answer Relevancy: `0.1121`
- Context Precision: `0.0865`
- Context Recall: `0.5102`

Source: [test_ragas_evaluation.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/tests/evaluation/test_ragas_evaluation.py)

### Interpretation

- faithfulness is moderate
- recall is acceptable
- precision is weak
- this supports the view that the system is grounded in principle, but still noisy and not sufficiently constrained for all structured features

## 9. Failure Analysis

## 9.1 Incorrect retrieval

Possible issue:

- subtopic `10.1` retrieves general Chapter 10 or adjacent biology chunks rather than the exact section

Why it happens:

- no explicit minimum relevance threshold
- no section-aware retrieval objective
- study tools do not carry `notebook_id`, so tenant-level material can mix

## 9.2 Hallucinated or generic structured outputs

Possible issue:

- diagrams and flashcards may look academically plausible but not match the textbook

Why it happens:

- prompts are generative
- structured tools do not require evidence per node, edge, or card
- citations are attached at the response level, not the element level

## 9.3 Demo-mode contamination

Possible issue:

- evaluation appears to pass, but outputs are actually generic demo responses

Why it happens:

- demo mode explicitly bypasses live retrieval in [ai.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/routes/ai.py#L50) and [students.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/academic/routes/students.py#L687)

## 9.4 Stale cache after new uploads

Possible issue:

- user uploads a textbook, then asks again and receives an older cached answer

Why it happens:

- cache keys do not include `notebook_id`
- no visible invalidation path is triggered when new material is ingested

## 9.5 Weak evaluation confidence for flowcharts and maps

Possible issue:

- flowchart and concept structures may omit key steps or invent relationships

Why it happens:

- no feature-specific acceptance suite tied to textbook ground truth
- no artifact-level grounding validator

## 10. Recommended Improvements

## 10.1 Retrieval improvements

- add a relevance threshold before generation
- expose retrieved chunk scores in audit/debug mode
- support section-aware retrieval for textbook chapter/subtopic requests
- include `notebook_id` in all study-tool generation requests

## 10.2 Prompt and feature improvements

- require per-question citations for quizzes and enforce them strictly
- require per-card citations for flashcards
- require node-level or edge-level evidence for mind maps and concept maps
- require step-level evidence for flowcharts
- add a stricter flowchart prompt that forbids adding steps not present in context

## 10.3 Validation improvements

- build a real textbook-backed golden set for Class 10 Biology
- evaluate each feature against a known chapter/subtopic answer key
- add a grounding validator that compares each structured artifact element to supporting chunks
- fail or warn when the answer contains unsupported concepts

## 10.4 Operational improvements

- invalidate AI cache after new document or URL ingestion
- make evaluation mode reject demo-mode execution
- add feature-level regression tests for:
  - chapter-specific quiz accuracy
  - flowchart step correctness
  - concept map relationship fidelity

## 11. Final Verdict

### Can the system reliably generate flowcharts from textbook RAG knowledge?

**Not reliably yet.**

It can generate flowchart-shaped outputs from retrieved context, but current evidence does not prove that those outputs consistently match the exact textbook section with strong grounding guarantees.

### Can the system reliably generate all major feature outputs from the same RAG knowledge base?

**Partially.**

The architecture supports it and live mode is genuinely grounded, but reliability varies by feature:

- reliable enough today: Q&A, Quiz
- usable but still weakly verified: Study Guide, Socratic tools
- not yet reliable enough for strict textbook-faithful evaluation: Flashcards, Mind Map, Flowchart, Concept Map

### Final determination

The system is **RAG-capable and partially grounded**, but it is **not yet strong enough to claim consistent, textbook-faithful generation for all structured learning features**, especially visual or semi-visual artifacts like flowcharts and concept maps.

