Date: 2026-03-31

# Personalization and Learning Experience Execution Checklist

## Status Legend

- `Not started`
- `In progress`
- `Complete`

## Workstream A: Learner Profile Foundation

Status: `In progress`

- [x] Add learner profile model and migration
- [x] Add learner profile service
- [x] Aggregate inputs from AI history, notebooks, sessions, weak topics, and generated artifacts
- [x] Infer preferred language
- [x] Infer preferred response length
- [x] Infer expertise level
- [x] Expose profile API endpoints
- [x] Add backend tests for deterministic profile inference

## Workstream B: Topic Mastery Tracking

Status: `In progress`

- [x] Add topic mastery model and migration
- [x] Add mastery update service
- [x] Define concept extraction / topic normalization strategy for mastery units
- [x] Update mastery from quiz completion
- [x] Update mastery from review completion
- [x] Update mastery from repeated AI confusion patterns
- [x] Update mastery from academic performance signals
- [x] Expose mastery-aware weak-topic outputs
- [x] Add backend tests for mastery scoring

## Workstream C: Adaptive AI Query Personalization

Status: `Complete`

- [x] Load learner profile during AI query preparation
- [x] Load topic mastery context during AI query preparation
- [x] Infer expertise level automatically when not explicitly set
- [x] Inject learner context into Q&A prompts
- [x] Inject learner context into study guide / Socratic / debate / essay prompts
- [x] Preserve explicit user overrides
- [x] Add tests for beginner vs advanced adaptation

## Workstream D: Adaptive Study Tool Generation

Status: `Complete`

- [x] Extend study tool pipeline to accept learner context
- [x] Make quizzes adapt difficulty and question mix
- [x] Define easy / medium / hard selection policy from mastery signals
- [x] Add mastery-aware quiz difficulty regression tests
- [x] Make flashcards prioritize weak concepts
- [x] Make study guides adapt ordering and explanation depth
- [x] Make visual tools simplify or deepen based on learner profile
- [x] Preserve schema validation and grounding checks
- [x] Add regression coverage for adaptive tool output

## Workstream E: Recommendation Engine

Status: `In progress`

- [x] Add recommendation service
- [x] Generate route-aware personalized recommendations
- [x] Generate mastery-aware recommendations
- [x] Replace current heuristic SmartSuggestions logic with service-backed recommendations
- [x] Replace generic suggestion chips where learner context is available
- [x] Integrate with student dashboard
- [x] Integrate with AI Studio suggestion surface
- [x] Integrate with mascot suggestion chips
- [x] Add backend tests for recommendation ranking and fallback behavior

## Workstream F: Study Path and Remediation Engine

Status: `Complete`

- [x] Add remediation queue design and model/state shape
- [x] Add study path API
- [x] Add weak-topic remediation generation
- [x] Add one-click "continue learning" actions
- [x] Make mascot able to summarize and execute a study path
- [x] Add tests for remediation sequencing

## Workstream G: UX Simplification

Status: `Complete`

- [x] Add personalized "recommended for you" blocks
- [x] Reduce static generic suggestion lists
- [x] Add one-click recommended actions on overview and assistant pages
- [x] Add visible study-path CTA on the overview surface
- [x] Make AI Studio and mascot primary learning surfaces
- [x] Define primary AI navigation model centered on mascot + AI Studio
- [x] Route dashboard and upload success states into mascot + AI Studio follow-up flows
- [x] Reduce overlapping parallel AI entry points where possible
- [x] Improve flow between upload -> ask -> practice -> review
- [x] Add browser E2E for personalized CTA flows

## Workstream H: Analytics and Evaluation

Status: `Complete`

- [x] Add recommendation click-through metrics
- [x] Add remediation completion metrics
- [x] Add improvement-after-recommendation metrics
- [x] Add personalization evaluation benchmark
- [x] Add dashboards / audit visibility for personalization effectiveness
- [x] Add release criteria for personalization rollout

## Recommended Execution Order

1. Workstream A
2. Workstream B
3. Workstream D
4. Workstream C
5. Workstream E
6. Workstream F
7. Workstream G
8. Workstream H

## Current Progress Snapshot

- `Complete slice`: learner profile foundation, concept-level mastery foundation, adaptive quiz profile plumbing, mastery updates from quiz results and AI confusion, profile-aware recommendations in AI Studio, mascot suggestion chips, the student dashboard, general AI-query personalization with explicit override safety, adaptive study-tool generation across quizzes, flashcards, study guides, and visual tools with schema-safe regression coverage, persisted study-path/remediation APIs, mascot study-path execution, overview-level path visibility, first-cut personalization telemetry for recommendation clicks and study-path usage, guided mastery-improvement and recovery metrics after recommended remediation, a deterministic personalization benchmark for support, balanced, and advanced learner scenarios, a direct upload -> mascot follow-up handoff for ask/practice/deepen flows, consolidation of the legacy student AI route into AI Studio so history and mode restoration no longer live in a parallel workspace, and replacement of the remaining AI Studio generic hint surfaces with personalized recommendation-backed actions and composer seeding.
- `Next best steps`: broader personalized UX flows, reduction of overlapping static entry points, and optional admin/dashboard surfacing of personalization effectiveness summaries.

## Release Gates

- [x] Learner profile inference is deterministic and tested
- [x] Topic mastery updates are stable and tested
- [x] Adaptive quiz difficulty is live and regression-tested
- [x] AI outputs adapt automatically without breaking grounding
- [x] Personalized recommendations are visible in main student surfaces
- [x] Heuristic suggestion surfaces are replaced or clearly downgraded
- [x] Mascot + AI Studio operate as the primary AI learning flow
- [x] Adaptive tool generation remains schema-valid
- [x] Browser flows for personalized UX pass
- [x] Personalization metrics are observable
- [x] Personalization benchmark passes for support, balanced, and advanced learner scenarios
