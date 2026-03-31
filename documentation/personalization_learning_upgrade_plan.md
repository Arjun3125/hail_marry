Date: 2026-03-31

# Personalization and Learning Experience Upgrade Plan

## 1. Goal

Turn the current platform from:

- a grounded AI learning system with partial personalization

into:

- a genuinely personalized learning platform that adapts content, difficulty, recommendations, and workflows to each learner over time

## 2. Current State

The current system already has strong foundations:

- RAG-backed grounded study generation
- OCR and WhatsApp input coverage
- mascot orchestration
- AI history and notebook continuity
- weak-topic detection
- study-session tracking
- role-aware guidance and suggestion surfaces

But personalization is still limited because:

1. learner state is fragmented across multiple tables and UI heuristics
2. expertise and response style are mostly user-selected, not inferred
3. weak-topic logic is broad and subject-level, not concept-level
4. recommendations are mostly heuristic and session-local
5. there is no true adaptive learning loop that changes study content automatically

## 3. Target State

The upgraded system should provide:

1. persistent learner profiles
2. inferred proficiency and explanation depth
3. concept-level mastery tracking
4. adaptive quizzes and study tools
5. personalized next-step recommendations
6. recommended study paths and remediation loops
7. lower-effort UX that routes users toward the right tool automatically
8. a unified primary AI experience centered on mascot + AI Studio

## 4. Architecture Direction

### Core principle

Do not build personalization as a separate AI product.

Instead:

- layer it into the existing notebook, AI query, study-tool, mascot, dashboard, and weak-topic pipelines

### New system layers

1. **Learner Profile Layer**
   - unified student state
   - preferences
   - inferred expertise
   - study habits
   - dominant subjects/topics

2. **Mastery Layer**
   - topic-level and concept-level mastery
   - confidence score
   - evidence from quizzes, questions, reviews, and usage behavior

3. **Recommendation Layer**
   - next-best actions
   - review suggestions
   - tool recommendations
   - study path generation

4. **Adaptive Generation Layer**
   - inject learner state into prompts and tool generation
   - change difficulty and explanation style automatically

## 5. Workstreams

## Current Implementation Snapshot

The first adaptive-learning slice is now in place:

1. learner profile has a persisted backend model, recompute service, and API
2. concept-level topic mastery has a persisted backend model and migration
3. mastery seeding, quiz-result updates, review-completion updates, and repeated-AI-confusion updates are wired through the student workflow
4. weak-topic responses now include mastery-derived focus topics
5. quiz generation now accepts an adaptive quiz profile and enforces per-question difficulty tags
6. AI Studio suggestions now use a profile-aware backend recommendation endpoint instead of purely local heuristics
7. mascot suggestion chips now reuse the same personalization signals for student flows
8. student overview now exposes a profile-aware "Recommended for you" block and related entry points bias users toward mascot + AI Studio as the primary AI flow

What still remains:

1. adaptive behavior beyond quizzes
2. richer adaptive behavior across flashcards, study guides, and visual tools
3. personalization metrics and release gates

## Workstream A: Learner Profile Foundation

### Objective

Create a persistent learner profile that aggregates the signals already scattered across the system.

### Data sources to use

- AI query history
- generated content history
- notebook usage
- study sessions
- weak-topic performance
- quiz results
- review completion history
- selected language / response controls
- mascot interactions

### New backend components

1. `backend/src/domains/platform/models/learner_profile.py`
   - `tenant_id`
   - `user_id`
   - `preferred_language`
   - `inferred_expertise_level`
   - `preferred_response_length`
   - `primary_subjects`
   - `engagement_score`
   - `consistency_score`
   - `last_recomputed_at`

2. `backend/src/domains/platform/services/learner_profile_service.py`
   - recompute profile from existing signals
   - store inferred defaults
   - expose current learner context for prompts and UI

3. `backend/src/domains/platform/routes/personalization.py`
   - `GET /api/personalization/profile`
   - `POST /api/personalization/profile/recompute`

### Inference rules for v1

1. infer `preferred_language` from recent AI query settings if set repeatedly
2. infer `preferred_response_length` from repeated selection
3. infer `inferred_expertise_level` from:
   - repeated simple mode use -> `simple`
   - high performance + advanced tool use -> `advanced`
   - otherwise `standard`
4. infer `primary_subjects` from recent notebook and topic activity

### Acceptance criteria

1. each student has a persisted learner profile
2. profile recomputation is deterministic
3. profile can be consumed by AI workflows and dashboards

### Current status

In progress.

Completed in this slice:

1. learner profile model + migration
2. deterministic recompute service using AI history, study sessions, generated content, weak-topic performance, and mastery signals
3. `GET /api/personalization/profile`
4. `POST /api/personalization/profile/recompute`
5. backend tests for deterministic profile inference

## Workstream B: Concept and Topic Mastery Tracking

### Objective

Move beyond subject-level weak-topic logic into concept-level learning state.

### New backend components

1. `backend/src/domains/platform/models/topic_mastery.py`
   - `tenant_id`
   - `user_id`
   - `subject`
   - `topic`
   - `mastery_score`
   - `confidence_score`
   - `last_evidence_type`
   - `last_evidence_at`
   - `review_due_at`

2. `backend/src/domains/platform/services/mastery_tracking_service.py`
   - update mastery after:
     - quiz completion
     - flashcard review
     - AI Q&A streaks
     - review ratings
     - assignment / marks outcomes where available

### Evidence model

Use a weighted scoring model:

1. quiz correctness and difficulty
2. repeated confusion on same topic in AI chat
3. review completion rating
4. weak-topic performance
5. tool repetition without success

### Initial scoring rule

Start simple:

- mastery score: `0-100`
- confidence score: `0-1`
- below threshold -> candidate for remediation
- strong repeated correct performance -> raise confidence

### Acceptance criteria

1. topic mastery rows are updated from real activity
2. weak-topic APIs can optionally return topic-level remediation candidates
3. dashboards can show top weak topics and improving topics

### Priority emphasis

This workstream is one of the highest-value tracks because it enables:

1. adaptive quiz difficulty
2. mastery-aware recommendations
3. better routing into review, quiz, flashcards, and study-path flows

### Current status

In progress.

Completed in this slice:

1. topic mastery model + migration
2. concept extraction and topic normalization
3. academic-performance baseline seeding
4. review-completion updates
5. quiz-result updates
6. repeated-AI-confusion updates
7. mastery-aware weak-topic outputs
8. regression coverage for mastery scoring and adaptive quiz profile derivation

## Workstream C: Adaptive AI Query Personalization

### Objective

Automatically shape AI answers using learner state instead of relying only on manual controls.

### Changes

Update:

- [workflows.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/workflows.py)
- [ai.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/routes/ai.py)
- [mascot_orchestrator.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/platform/services/mascot_orchestrator.py)

### Injection logic

Before prompt generation:

1. load learner profile
2. load top mastery signals for the current topic/notebook
3. if request explicitly sets `expertise_level`, keep it
4. otherwise infer:
   - struggling learner -> `simple`
   - normal learner -> `standard`
   - strong learner -> `advanced`
5. optionally add:
   - "student is weak on X"
   - "prefer concise explanations"
   - "student benefits from guided questioning"

### Behavior targets

1. beginner receives simpler explanations automatically
2. advanced learner gets deeper reasoning automatically
3. repeated confusion on same topic biases the system toward step-by-step explanation or Socratic mode

### Acceptance criteria

1. default prompt behavior changes based on learner profile when user does not override settings
2. routes still support explicit user control
3. tests prove adaptation happens deterministically

### Current status

Complete for the main AI query path.

Completed in this slice:

1. learner profile is loaded during AI query preparation
2. topic mastery context is loaded during AI query preparation
3. default language, response length, and expertise settings adapt from learner state when the user does not explicitly override them
4. the shared AI workflow injects learner context into grounded prompts for Q&A, study guide, Socratic, debate, and essay-review modes
5. explicit user overrides are preserved even when they match default values
6. backend tests now cover both personalized-default adaptation and explicit-override preservation

## Workstream D: Adaptive Study Tool Generation

### Objective

Make study tools reflect learner state, not just topic content.

### Tool-specific upgrades

1. **Quiz**
   - assign difficulty tags intentionally
   - adapt question mix to mastery state
   - weak topics -> more recall and scaffolded questions
   - strong topics -> more synthesis/application questions
   - derive easy / medium / hard ratio from mastery score and confidence
   - raise difficulty gradually when performance is consistently strong
   - lower difficulty and add scaffolding when the learner repeatedly struggles

2. **Flashcards**
   - prioritize weak concepts
   - include misconception-correction cards
   - include confidence weighting

3. **Study Guide**
   - reorder sections:
     - basics first for weak learners
     - summary first for strong learners

4. **Mind Map / Concept Map / Flowchart**
   - simplify structure for beginners
   - preserve richer relation density for advanced users

### Required backend changes

Update:

- [study_tools.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/shared/ai_tools/study_tools.py)
- tool prompts in [workflows.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/workflows.py)

### Acceptance criteria

1. tool prompts accept learner context
2. structured outputs remain schema-valid
3. tests verify simple vs advanced behavior is different and grounded

### Priority emphasis

This workstream must explicitly deliver:

1. adaptive quiz difficulty
2. mastery-aware question selection
3. learner-aware flashcard prioritization

### Current status

In progress.

Completed in this slice:

1. study-tool pipeline accepts adaptive quiz context
2. quiz prompts require `difficulty`
3. normalization preserves difficulty tags
4. adaptive quiz profile derives difficulty mix from mastery + confidence
5. study-tool pipeline now carries learner profile + topic mastery context for non-quiz tools
6. flashcards now prioritize weak or confusing focus concepts first
7. mind maps, flowcharts, and concept maps now simplify structure for struggling learners and can deepen for advanced learners
8. study guides now reorder and adjust explanation depth for struggling vs advanced learners
9. schema normalization remains unchanged and regression-tested for adaptive tool generation

## Workstream E: Recommendation Engine

### Objective

Replace mostly heuristic next-step suggestions with learner-aware recommendations.

### New backend components

1. `backend/src/domains/platform/services/recommendation_service.py`

### Inputs

- learner profile
- topic mastery
- weak-topic alerts
- recent tools used
- recent uploads and notebooks
- incomplete reviews
- current page / route context

### Outputs

1. next best action
2. recommended tool
3. recommended topic
4. optional remediation reason

### Recommendation categories

1. review weak topic
2. generate quiz
3. create flashcards
4. revisit uploaded notebook
5. continue unfinished study sequence
6. switch to a better tool for the current task

### UI surfaces to integrate

- `student overview`
- AI Studio suggestion rail
- mascot suggestion chips
- dashboard / role panels

### Acceptance criteria

1. recommendations are route-aware and learner-aware
2. suggestions cite a reason internally
3. generic static suggestions are reduced

### Priority emphasis

This workstream must explicitly replace current heuristic suggestion behavior in the main student AI surfaces with:

1. profile-aware next-step recommendations
2. mastery-aware action ranking
3. route-aware tool recommendations

### Current status

In progress.

Completed in this slice:

1. backend recommendation builder
2. weak-topic and route-aware recommendation ranking
3. AI Studio integration with backend-backed suggestions
4. fallback to static suggestions when the service is unavailable

## Workstream F: Study Path and Remediation Engine

### Objective

Create sequential guidance rather than one-off suggestions.

### New capabilities

1. recommended study path per notebook or subject
2. remediation queue for weak topics
3. "next 3 actions" plan per student

### Flow

1. identify weak topic
2. identify prerequisite or supporting concept
3. assign:
   - simple explanation
   - flashcards
   - short quiz
   - re-check confidence

### New APIs

- `GET /api/personalization/study-path`
- `GET /api/personalization/remediation`

### Acceptance criteria

1. students can see a concrete path, not only isolated outputs
2. mascot can summarize and execute a study path

### Current status

In progress.

Completed in this slice:

1. persisted study-path plan model and migration
2. remediation candidate builder from mastery gaps
3. `GET /api/personalization/remediation`
4. `GET /api/personalization/study-path`
5. `POST /api/personalization/study-path/{plan_id}/steps/{step_id}/complete`
6. mascot can now summarize the current study path and execute the next pending step
7. student overview now surfaces the active study path and next action
8. browser E2E now verifies the personalized study-path CTA flow from student overview into mascot
9. backend tests for remediation ranking, plan persistence, mascot execution, and next-step advancement

## Workstream G: UX Simplification and Product Flow

### Objective

Reduce cognitive load so personalization is actually felt by the user.

### Problems to solve

1. too many AI entry points
2. too much mode choice for weaker users
3. recommendations are not strong enough to guide action

### UX changes

1. Treat mascot + AI Studio as the primary intelligent learning surface
2. Add "recommended for you" blocks on student overview and assistant pages
3. Add one-click actions:
   - "practice weak topic"
   - "review due flashcards"
   - "continue yesterday's topic"
4. Add adaptive entry actions:
   - if student is weak on topic -> suggest quiz + flashcards
   - if student asks repeated question -> suggest study guide or Socratic mode

### Acceptance criteria

1. fewer static suggestion lists
2. more context-aware CTA blocks
3. less need for users to decide the tool themselves

### Priority emphasis

This workstream must explicitly tighten the AI experience around mascot + AI Studio by:

1. making them the primary discovery and action surfaces
2. reducing overlapping parallel AI entry experiences where possible
3. routing upload, dashboard, and recommendation flows back into the same core AI workspace

### Current status

In progress.

Completed in this slice:

1. student overview CTAs now bias toward mascot assistant and AI Studio
2. assignment and lecture help links now point to mascot assistant
3. AI Studio remains the deeper workspace while mascot is the guided entry point
4. completed student uploads now surface direct next-step actions that open mascot with a prefilled guided follow-up prompt
5. mascot assistant now accepts prompt-prefill handoffs so upload flows can move directly into ask -> practice behavior without asking the learner to decide the next tool manually
6. the legacy `/student/ai` route now redirects into AI Studio with history and tool context preserved, reducing parallel student AI workspaces
7. AI Studio starter suggestions and hint-panel actions now use profile-aware backend recommendations, with prompt seeding into the composer instead of large static suggestion lists

## Workstream H: Analytics, Evaluation, and Safety

### Objective

Measure whether personalization helps instead of just adding complexity.

### Metrics

1. recommendation click-through
2. recommendation completion rate
3. quiz improvement after recommended remediation
4. repeat-question reduction
5. weak-topic recovery rate
6. tool effectiveness by learner segment

### New tests and evaluation

1. backend tests for learner profile inference
2. backend tests for mastery update logic
3. grounding tests with beginner vs advanced prompt variants
4. browser tests for personalized suggestions
5. evaluation report for adaptive quiz behavior

### Safety rules

1. do not silently override explicit user settings
2. personalization must never reduce grounding quality
3. learner-profile prompts must remain explainable and deterministic

### Current status

In progress.

Completed in this slice:

1. recommendation impressions now emit automatically from the personalization recommendation route with surface and tool labels
2. study-path views and step completions now emit automatically from the study-path routes
3. student clients can record high-signal personalization events such as recommendation clicks and study-path opens
4. `GET /api/personalization/metrics` now exposes an admin-facing effectiveness summary with recommendation CTR and study-path completion rates
5. quiz-result and review-completion flows now emit mastery-improvement and mastery-recovery telemetry when a guided study path exists for the same topic
6. backend tests now cover personalization metrics export, route-level telemetry summaries, and guided-improvement tracking
7. a deterministic evaluation benchmark now verifies support, balanced, and advanced learner scenarios across recommendation ranking, adaptive quiz difficulty, prompt shaping, and study-path generation
8. rollout criteria are now explicit: the benchmark must pass, personalization metrics must be observable, adaptive generation must remain schema-safe, and the main browser CTA flows must stay green

## 6. Rollout Phases

## Phase 1: Foundation

Build:

- learner profile model
- profile service
- topic mastery model
- mastery update hooks

Status:

- partially complete
- topic mastery model and first mastery hooks are done
- learner profile model and service are still pending

## Phase 2: Adaptive Generation

Build:

- prompt injection of learner context
- adaptive quiz and flashcard behavior
- mastery-aware study guide ordering
- mastery-aware quiz difficulty policy

Status:

- partially complete
- adaptive quiz difficulty foundation is done
- broader prompt injection and non-quiz adaptive tools are still pending

## Phase 3: Recommendations

Build:

- recommendation service
- student dashboard suggestions
- AI Studio suggestions
- mascot suggestions
- replacement of heuristic next-step suggestion logic

Status:

- partially complete
- AI Studio now uses backend-backed personalized suggestions
- dashboard and mascot parity are still pending

## Phase 4: Study Path UX

Build:

- remediation queue
- study path APIs
- one-click recommended actions
- mascot + AI Studio primary AI flow tightening

Status:

- partially complete
- navigation is now biased toward mascot + AI Studio
- study-path APIs and remediation sequencing are still pending

## Phase 5: Evaluation and Release Gates

Build:

- personalization regression suite
- UX/E2E coverage
- outcome metrics and dashboards

## 7. Prioritization

### Highest value first

1. learner profile foundation
2. topic mastery tracking
3. adaptive quiz difficulty
4. adaptive prompt injection
5. recommendation engine
6. mascot + AI Studio unification

### After that

1. adaptive study tools
2. study path engine
3. UX simplification

## 8. Definition of Success

The personalization system is successful when:

1. outputs adapt automatically for different learners without manual configuration
2. weak topics and topic mastery drive recommendations and study generation
3. adaptive quizzes change difficulty based on learner state
4. students receive profile-aware next-step recommendations instead of mostly heuristic suggestions
5. students see clear next steps with low friction
6. mascot + AI Studio feel like one coherent intelligent workspace
7. grounded generation quality remains strong
8. dashboards and mascot feel genuinely personalized, not generic
