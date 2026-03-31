# Student Account Operational Cost Report

Date: 2026-03-31

## Executive Summary

The current codebase is already optimized for low vendor cost by default:

- LLM: self-hosted `ollama` / `llama3.2`
- Embeddings: local `nomic-embed-text`
- Vector store: local `faiss`
- Media transcription: local `whisper-tiny`
- OCR: local CPU-based OCR stack

That default stack minimizes direct API spend, but it shifts more risk into infrastructure sizing, inference latency, and quality variance.

For production, the best cost / quality balance is a hybrid model:

- keep OCR, embeddings, and vector retrieval local or self-hosted
- use a low-cost hosted LLM for student-facing generation
- route high-volume structured tools to the cheapest model that still preserves quality

Recommended production target:

- `GPT-5.4 mini` for grounded Q&A, study guides, Socratic tutor, debate, and essay review
- `GPT-5.4 nano` for quiz, flashcards, mind map, flowchart, and concept map generation
- `text-embedding-3-small` only if you move embeddings to an API provider; otherwise keep local embeddings
- keep `faiss` or move to self-hosted `Qdrant` only when operationally necessary

Estimated cost per student for the recommended hybrid stack:

- Low usage: about `$0.47 / month`
- Average usage: about `$1.12 / month`
- Heavy usage: about `$2.44 / month`

This report treats WhatsApp pricing as an estimate because Meta pricing is geography- and conversation-category-dependent and should be replaced with your actual launch-country rate card before go-live.

## Repo-Based Cost Posture

The current repository suggests the following baseline architecture:

- [backend/config.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/config.py)
- [backend/src/infrastructure/vector_store/ingestion.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/infrastructure/vector_store/ingestion.py)
- [backend/src/interfaces/rest_api/ai/workflows.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/workflows.py)
- [backend/src/shared/ai_tools/study_tools.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/shared/ai_tools/study_tools.py)
- [backend/src/domains/platform/services/whatsapp_gateway.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/platform/services/whatsapp_gateway.py)

Implications:

- direct LLM API cost can be near zero if you stay fully self-hosted
- embedding API cost can be near zero if you keep local embeddings
- vector DB cost is negligible if you stay on local `faiss`
- OCR cost is mostly CPU time
- WhatsApp cost is external and usage-dependent

The real tradeoff is not just cost. It is cost vs:

- quality
- latency
- concurrency
- operational burden
- failure isolation

## Usage Assumptions

These scenarios are intended to estimate recurring cost for one active student account.

### Average Document Assumption

Per uploaded document:

- extracted text: `25,000` tokens
- average chunk count: `~45`
- average vector payload + metadata: `~180 KB` per document

This aligns with the codebase chunking pattern in [ingestion.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/infrastructure/vector_store/ingestion.py), where chunk sizes are relatively small and overlap is used.

### Low Usage

Per month:

- `120` Q&A requests
- `8` quiz generations
- `8` flashcard generations
- `4` mind maps
- `2` flowcharts
- `2` study guides
- `6` OCR image runs
- `4` document uploads

### Average Usage

Per month:

- `300` Q&A requests
- `24` quiz generations
- `24` flashcard generations
- `12` mind maps
- `8` flowcharts
- `8` study guides
- `20` OCR image runs
- `12` document uploads

### Heavy Usage

Per month:

- `600` Q&A requests
- `90` quiz generations
- `90` flashcard generations
- `60` mind maps
- `30` flowcharts
- `30` study guides
- `60` OCR image runs
- `30` document uploads

The heavy profile is close to the user prompt’s example daily behavior once normalized to a monthly active-student estimate.

## Recommended Model Assignment

### High-value grounded learning tasks

Use `GPT-5.4 mini` for:

- Q&A assistant
- study guide
- Socratic tutor
- debate assistant
- essay review

Reason:

- these tasks depend more on explanation quality, reasoning coherence, and better use of retrieved context

### Structured high-volume tool generation

Use `GPT-5.4 nano` for:

- quiz
- flashcards
- mind map
- flowchart
- concept map

Reason:

- these tasks are prompt-constrained, schema-constrained, and cheaper to produce at scale

### Embeddings

If hosted:

- `text-embedding-3-small`

If self-hosted:

- keep the current local embedding path unless recall quality becomes a measurable issue

### OCR / transcription

Keep local first:

- OCR: local OCR stack
- transcription: `whisper-tiny` or equivalent small local model

Only escalate hard cases to premium OCR or larger transcription models when confidence is low.

## Token and Cost Assumptions

Hosted LLM pricing assumptions used here:

- `GPT-5.4 mini`: `$0.75 / 1M input tokens`, `$4.50 / 1M output tokens`
- `GPT-5.4 nano`: `$0.20 / 1M input tokens`, `$1.25 / 1M output tokens`
- `text-embedding-3-small`: `$0.02 / 1M input tokens`

### Per-Feature Token Estimates

| Feature | Model | Input tokens | Output tokens | Estimated cost / request |
|---|---:|---:|---:|---:|
| Q&A | GPT-5.4 mini | 2,000 | 350 | `$0.003075` |
| Study guide | GPT-5.4 mini | 3,000 | 800 | `$0.005850` |
| Quiz | GPT-5.4 nano | 2,500 | 700 | `$0.001375` |
| Flashcards | GPT-5.4 nano | 2,000 | 500 | `$0.001025` |
| Mind map | GPT-5.4 nano | 2,200 | 450 | `$0.001003` |
| Flowchart | GPT-5.4 nano | 2,400 | 500 | `$0.001105` |
| Concept map | GPT-5.4 nano | 2,400 | 550 | `$0.001168` |
| Socratic tutor | GPT-5.4 mini | 2,200 | 300 | `$0.003000` |
| Debate / essay review | GPT-5.4 mini | 3,000 | 900 | `$0.006300` |

Notes:

- these are realistic budgeting estimates, not measured token logs from production traffic
- they assume retrieved context is trimmed reasonably before generation
- poor prompt hygiene or oversized retrieval contexts can easily raise these numbers by `25%+`

## Embedding Cost

### Hosted embedding estimate

Per uploaded document:

- tokens embedded: `25,000`
- price: `$0.02 / 1M`
- estimated cost: `25,000 / 1,000,000 * $0.02 = $0.0005`

Per month:

- Low usage: `4` docs -> `$0.002`
- Average usage: `12` docs -> `$0.006`
- Heavy usage: `30` docs -> `$0.015`

### Practical conclusion

Embedding cost is not a major cost driver.

If the current local embedding stack is acceptable on retrieval quality, it is cheaper to keep it local and avoid vendor dependence.

## Vector Database Cost

### Current repo-default path

The current codebase uses `faiss` by default, which makes vector storage/query cost mostly a storage and compute problem inside your own infrastructure.

Estimated storage growth:

- `~180 KB` per document
- `12` docs / month / student in the average case
- `~2.16 MB / month / student`

At `10,000` active students:

- new vector data per month: about `21.6 GB`

That is operationally manageable on local disk-backed storage or a modest self-hosted vector service.

### Managed vector DB perspective

Managed options like Pinecone and Qdrant Cloud are useful when you need:

- high query concurrency
- multi-node reliability
- operational simplicity
- hosted scaling and backup guarantees

But for this application shape, vector DB spend should stay well below LLM spend unless you significantly over-provision or move to a large managed cluster too early.

Practical estimate:

- self-hosted `faiss` / `Qdrant`: `< $0.01 / student / month`
- managed vector DB: typically only justified when ops simplicity is more important than lowest possible cost

## OCR Cost

The current repo uses local OCR and local preprocessing, so OCR is mostly a compute allocation problem.

Budget assumption:

- `~$0.0003` per OCR image equivalent in CPU / worker cost

Per month:

- Low usage: `6` images -> `$0.0018`
- Average usage: `20` images -> `$0.0060`
- Heavy usage: `60` images -> `$0.0180`

This remains small unless you switch to a premium hosted OCR API for all inputs.

Recommended policy:

- run standard OCR locally
- only escalate low-confidence cases to a premium fallback

## WhatsApp Integration Cost

This system uses the WhatsApp Cloud API transport path in:

- [whatsapp_gateway.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/platform/services/whatsapp_gateway.py)

WhatsApp cost depends on:

- country
- conversation category
- whether the message is inbound user-initiated or outbound template-driven

Because those rates vary materially by launch geography and Meta billing policy, the line below is an estimate, not a billing guarantee.

Budget assumption used in this report:

- Low usage: `$0.008 / month / student`
- Average usage: `$0.015 / month / student`
- Heavy usage: `$0.025 / month / student`

Recommendation:

- do not use WhatsApp as the primary heavy-content delivery channel
- use it for lightweight reminders, guidance, and short grounded answers
- keep richer study artifacts inside the web app

## Shared Infrastructure Cost

Assume a `10,000 active student` deployment with:

- app/API servers
- worker tier
- PostgreSQL
- Redis / queue
- object storage + backups
- metrics / logging

Practical monthly shared infrastructure budget:

- app/API + workers: `$180`
- PostgreSQL: `$100`
- Redis / queue: `$30`
- storage + backup: `$40`
- observability: `$50`
- OCR / ingestion / embedding CPU budget: `$120`

Total:

- `$520 / month`

Per active student:

- `$0.052 / month`

Rounded in scenario tables:

- `$0.05 / month / student`

## Cost Per Student

### Recommended Hybrid Production Stack

This stack means:

- hosted LLM generation
- local OCR
- local or self-hosted embeddings
- local or self-hosted vector DB
- normal app/database/storage hosting

| Scenario | LLM | Embeddings | OCR | WhatsApp | Shared infra | Total / month | Total / day |
|---|---:|---:|---:|---:|---:|---:|---:|
| Low | `$0.406` | `$0.002` | `$0.0018` | `$0.008` | `$0.050` | `$0.47` | `$0.016` |
| Average | `$1.048` | `$0.006` | `$0.0060` | `$0.015` | `$0.050` | `$1.12` | `$0.037` |
| Heavy | `$2.330` | `$0.015` | `$0.0180` | `$0.025` | `$0.050` | `$2.44` | `$0.081` |

### Current Repo-Default Self-Hosted Stack

This stack means:

- local LLM
- local embeddings
- local OCR/transcription
- local vector DB

Direct vendor cost can be very low, but true cost shifts to:

- inference nodes
- GPU or CPU capacity
- queueing latency
- operational reliability

Practical estimate at scale:

- roughly `$0.20 - $0.60 / month / student`, depending on concurrency and hardware efficiency

Important nuance:

- this is cheaper on vendor billing
- it is not automatically cheaper on total cost of ownership if you need strong concurrency, high availability, and premium answer quality

## Cost Per Request Summary

| Feature | Estimated cost |
|---|---:|
| Q&A | `$0.003075` |
| Study guide | `$0.005850` |
| Quiz | `$0.001375` |
| Flashcards | `$0.001025` |
| Mind map | `$0.001003` |
| Flowchart | `$0.001105` |
| Concept map | `$0.001168` |
| OCR image | `$0.000300` |
| Document embedding | `$0.000500` per average document |

## Best Model Choice by Task

| Task | Recommended model | Why |
|---|---|---|
| Q&A | `GPT-5.4 mini` | Better explanation depth and grounding quality |
| Study guide | `GPT-5.4 mini` | Better structure and reasoning |
| Quiz | `GPT-5.4 nano` | Structured output, high volume, lower cost |
| Flashcards | `GPT-5.4 nano` | Predictable format and low token need |
| Mind map | `GPT-5.4 nano` | Structure-heavy, not reasoning-heavy |
| Flowchart | `GPT-5.4 nano` | Constrained output format |
| Concept map | `GPT-5.4 nano` | Constrained output format |
| Socratic tutor | `GPT-5.4 mini` | Better guidance quality |
| Debate assistant | `GPT-5.4 mini` | Better argument quality |
| Essay review | `GPT-5.4 mini` | Better nuance and feedback quality |

## Cost Reduction Strategies

### 1. Keep retrieval context tight

- cap retrieved chunks aggressively
- trim duplicate or weakly relevant chunks
- summarize context before generation when possible

This lowers the biggest cost driver: input tokens.

### 2. Use cheap models for structured tools

- keep Q&A on the stronger mini model
- push quiz, flashcards, and diagram outputs to the nano model

This is the single highest-value routing decision.

### 3. Cache notebook-level repeated context

- repeated study activity often hits the same notebook and topic
- cache retrieval results or precomputed topic summaries

This cuts both latency and token spend.

### 4. Use batch generation for non-interactive artifacts

If you move some generation to asynchronous pipelines, OpenAI’s Batch API can reduce token cost materially for those tasks.

Best candidates:

- quiz
- flashcards
- study guide regeneration
- classwide content jobs

### 5. Keep embeddings and OCR local

They are already cheap locally in this codebase and do not justify premium hosted cost unless you have a measurable quality gap.

### 6. Avoid WhatsApp as the heavy artifact channel

Use WhatsApp for:

- reminder
- notification
- quick answer
- link back into app

Keep large study artifacts in the web app.

### 7. Add prompt ceilings and output ceilings

- fixed maximum answer lengths
- fixed schema sizes for tools
- avoid long chain-of-thought style outputs

### 8. Escalate quality only on failure

Use lower-cost models first and only reroute to stronger models when:

- output validation fails
- grounding score is weak
- the topic is complex or safety-sensitive

## Final Recommendation

For this application, the best production operating model is:

1. Keep the current local retrieval, OCR, and embedding stack.
2. Replace only the student-facing generation path with a hosted hybrid:
   - `GPT-5.4 mini` for explanation-heavy tasks
   - `GPT-5.4 nano` for structured study tools
3. Keep WhatsApp narrow and lightweight.
4. Stay on `faiss` or self-hosted `Qdrant` until retrieval scale or operational requirements clearly justify managed vector infrastructure.

If you follow that model, the application can realistically operate around:

- about `$0.47 / month` for low-usage students
- about `$1.12 / month` for average students
- about `$2.44 / month` for heavy-usage students

That is a strong cost position for an AI learning platform with RAG, OCR, study-tool generation, and messaging support.

## Sources

- OpenAI API pricing: https://openai.com/api/pricing/
- OpenAI pricing page: https://platform.openai.com/pricing
- OpenAI `text-embedding-3-small`: https://platform.openai.com/docs/models/text-embedding-3-small
- Qdrant Cloud pricing and billing: https://qdrant.tech/documentation/cloud-pricing-payments/
- Pinecone pricing estimator: https://www.pinecone.io/pricing/estimate/
- Pinecone cost model / RU-WU docs: https://docs.pinecone.io/guides/manage-cost/understanding-cost

## Important Caveat

This is a production cost estimate, not an invoice forecast.

The largest variables are:

- real token sizes in production
- concurrency
- WhatsApp geography/category rates
- how aggressively you cache and batch requests
- whether you remain self-hosted for inference or move more of the stack to managed APIs
