<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **proxy_notebooklm** (10952 symbols, 29535 relationships, 300 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## When Debugging

1. `gitnexus_query({query: "<error or symptom>"})` — find execution flows related to the issue
2. `gitnexus_context({name: "<suspect function>"})` — see all callers, callees, and process participation
3. `READ gitnexus://repo/proxy_notebooklm/process/{processName}` — trace the full execution flow step by step
4. For regressions: `gitnexus_detect_changes({scope: "compare", base_ref: "main"})` — see what your branch changed

## When Refactoring

- **Renaming**: MUST use `gitnexus_rename({symbol_name: "old", new_name: "new", dry_run: true})` first. Review the preview — graph edits are safe, text_search edits need manual review. Then run with `dry_run: false`.
- **Extracting/Splitting**: MUST run `gitnexus_context({name: "target"})` to see all incoming/outgoing refs, then `gitnexus_impact({target: "target", direction: "upstream"})` to find all external callers before moving code.
- After any refactor: run `gitnexus_detect_changes({scope: "all"})` to verify only expected files changed.

## Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.

## Tools Quick Reference

| Tool | When to use | Command |
|------|-------------|---------|
| `query` | Find code by concept | `gitnexus_query({query: "auth validation"})` |
| `context` | 360-degree view of one symbol | `gitnexus_context({name: "validateUser"})` |
| `impact` | Blast radius before editing | `gitnexus_impact({target: "X", direction: "upstream"})` |
| `detect_changes` | Pre-commit scope check | `gitnexus_detect_changes({scope: "staged"})` |
| `rename` | Safe multi-file rename | `gitnexus_rename({symbol_name: "old", new_name: "new", dry_run: true})` |
| `cypher` | Custom graph queries | `gitnexus_cypher({query: "MATCH ..."})` |

## Impact Risk Levels

| Depth | Meaning | Action |
|-------|---------|--------|
| d=1 | WILL BREAK — direct callers/importers | MUST update these |
| d=2 | LIKELY AFFECTED — indirect deps | Should test |
| d=3 | MAY NEED TESTING — transitive | Test if critical path |

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/proxy_notebooklm/context` | Codebase overview, check index freshness |
| `gitnexus://repo/proxy_notebooklm/clusters` | All functional areas |
| `gitnexus://repo/proxy_notebooklm/processes` | All execution flows |
| `gitnexus://repo/proxy_notebooklm/process/{name}` | Step-by-step execution trace |

## Self-Check Before Finishing

Before completing any code modification task, verify:
1. `gitnexus_impact` was run for all modified symbols
2. No HIGH/CRITICAL risk warnings were ignored
3. `gitnexus_detect_changes()` confirms changes match expected scope
4. All d=1 (WILL BREAK) dependents were updated

## Keeping the Index Fresh

After committing code changes, the GitNexus index becomes stale. Re-run analyze to update it:

```bash
npx gitnexus analyze
```

If the index previously included embeddings, preserve them by adding `--embeddings`:

```bash
npx gitnexus analyze --embeddings
```

To check whether embeddings exist, inspect `.gitnexus/meta.json` — the `stats.embeddings` field shows the count (0 means no embeddings). **Running analyze without `--embeddings` will delete any previously generated embeddings.**

> Claude Code users: A PostToolUse hook handles this automatically after `git commit` and `git merge`.

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->

---

# VidyaOS — Project Context

## Stack

| Layer | Tech |
|-------|------|
| Frontend | Next.js 14 (App Router), TypeScript, Tailwind CSS v4 |
| Backend | FastAPI, SQLAlchemy, LangGraph, Python 3.11 |
| AI | LangGraph StateGraph, Anthropic Claude, WhatsApp via WAHA |
| DB | PostgreSQL (prod), SQLite (tests) |
| Mascot | Blue Owl agent — primary product surface for all 4 roles |

## Commands

```bash
# Backend tests
cd backend && python -m pytest tests/ -v

# Backend (single file)
cd backend && python -m pytest tests/test_mascot_routes.py -v

# Frontend type check
cd frontend && npx tsc --noEmit

# GitNexus index (run after committing)
gitnexus analyze

# GitNexus UI
gitnexus serve   # → http://localhost:4747
```

## Architecture

```
backend/src/domains/
  mascot/          ← Owl agent: context assemblers, LangGraph, chat route, greeting endpoint
  academic/        ← Attendance, marks, assignments, timetable
  identity/        ← Users, roles, tenants, auth
  administrative/  ← Fees, incidents, announcements
  platform/        ← AI jobs queue, release gate

frontend/src/
  app/{student,teacher,parent,admin}/   ← Role-scoped layouts + dashboards + assistant pages
  components/mascot/                     ← MascotShell, MascotLauncher, MascotGreetingCard
  components/prism/                      ← Design system (PrismPage, PrismPanel, PrismSection)
  lib/api.ts                             ← All API calls in one place
```

## Roles

4 roles: `student`, `teacher`, `parent`, `admin`. All use the Mascot. Role is auth-derived server-side (`current_user.role`), never passed from client.

## Key Gotchas

- `MascotConversationTurn.student_id` stores user ID for ALL roles (not just students) — column name is legacy.
- Tailwind CSS v4: use CSS variables (`--text-primary`, `--bg-card`, `--border`) not hardcoded colors.
- `apiFetch` returns `Promise<unknown>` — all api.ts callers cast the result.
- `persist_and_format_node` in `mascot_agent.py` is the canonical turn save — don't add a second save in the route.
- WhatsApp tools live in `whatsapp_tools.py` — `WHATSAPP_TOOL_REGISTRY` dict, each spec has `.roles: frozenset` and `.required_params: tuple`.
- LangGraph node order: `load_context → tool_dispatch → extract_signals → generate_response → persist_and_format`.

---

# Skills & Plugins — When to Use What

## Trigger Map (use proactively, without being asked)

| Situation | Invoke |
|-----------|--------|
| User describes a new feature or change | `superpowers:brainstorming` **before any code** |
| Writing an implementation plan | `superpowers:writing-plans` |
| Executing a plan task-by-task | `superpowers:subagent-driven-development` |
| Debugging a failing test or runtime error | `superpowers:systematic-debugging` + `gitnexus-debugging` skill |
| Any frontend UI / component work | `superpowers:frontend-design` |
| Finishing a feature (all tasks done) | `superpowers:finishing-a-development-branch` |
| Before declaring a task complete | `superpowers:verification-before-completion` |
| Writing new backend logic | `superpowers:test-driven-development` |
| Exploring unfamiliar code | `gitnexus-exploring` skill |
| Before editing any function/class | `gitnexus-impact-analysis` skill |
| Renaming or extracting code | `gitnexus-refactoring` skill |
| Reviewing a PR | `gitnexus-pr-review` skill |
| Improving this CLAUDE.md | `claude-md-improver` skill |

## Installed Plugin Commands

| Command | When |
|---------|------|
| `/feature-dev` | Full feature cycle: explore → architect → implement → review |
| `/code-review` | Review any diff or PR |
| `/commit` | Structured commit with message guidance |
| `/commit-push-pr` | Commit + push + open PR in one flow |

## Superpowers Skill Names (for `Skill` tool)

```
superpowers:brainstorming
superpowers:writing-plans
superpowers:subagent-driven-development
superpowers:executing-plans
superpowers:systematic-debugging
superpowers:frontend-design          ← plugin: frontend-design
superpowers:finishing-a-development-branch
superpowers:verification-before-completion
superpowers:test-driven-development
superpowers:using-git-worktrees
superpowers:requesting-code-review
superpowers:dispatching-parallel-agents
```

## GitNexus Skill Names (for `Skill` tool)

```
gitnexus-exploring
gitnexus-impact-analysis
gitnexus-debugging
gitnexus-refactoring
gitnexus-pr-review
gitnexus-guide
gitnexus-cli
```
