# Product Improvement Report

## Context
Recent frontend updates addressed two separate build blockers in the Next.js app:

1. **Google Fonts fetch dependency during build** (`next/font/google` Geist), which could fail in restricted environments.
2. **App Router prerender failure** on `/teacher/attendance` due to `useSearchParams()` not being rendered under a Suspense boundary.

This report documents what happened, why the error occurred, how it was fixed, and what to improve next.

---

## Problem Statement
### Error observed during build

```text
useSearchParams() should be wrapped in a suspense boundary at page "/teacher/attendance"
```

### What this means
In the Next.js App Router, `useSearchParams()` is a client hook that depends on runtime navigation state. During static generation/prerendering, Next requires such client behavior to be isolated under a `<Suspense>` boundary. If a page component directly uses `useSearchParams()` without the required boundary, the prerender step fails.

### Why this looked confusing
The earlier build issue was network/font-related. After removing remote font fetching, the build advanced further and then failed on the attendance page. So the new failure was not a regression from font changes—it was an already-existing rendering-architecture issue revealed after the first blocker was removed.

---

## Fix Implemented
### Attendance page architecture fix

- Moved attendance UI/state/side-effects into a dedicated client component:
  - `frontend/src/app/teacher/attendance/AttendanceClient.tsx`
- Changed `frontend/src/app/teacher/attendance/page.tsx` into a wrapper that renders the client component inside `<Suspense>` with a lightweight fallback.

### Font/network hardening

- Removed `next/font/google` Geist usage from root layout.
- Switched default sans stack to system fonts in global styles to avoid external font fetch during build.

---

## Validation Results
### Build status
- `npm run build` now completes successfully.
- `/teacher/attendance` is generated without the previous `useSearchParams` prerender error.

### Non-blocking warnings still present
- Recharts warning appears during static generation (`width(-1)` / `height(-1)`), but it does **not** fail the build.

---

## Product Impact
- **Higher build reliability** in restricted CI/network environments.
- **Clearer separation of concerns** on attendance route (server wrapper + client feature component).
- **Lower operational risk**: one blocker (font fetch) no longer masks downstream rendering issues.

---

## Recommended Next Improvements
1. **Stabilize chart SSR behavior**
   - Ensure charts rendered during static generation have deterministic container sizing or client-only rendering guards.
2. **Introduce route-level build checks**
   - Add a CI step that fails on App Router anti-patterns (e.g., client hooks used outside expected boundaries).
3. **Document App Router guardrails**
   - Add a short frontend guideline: when using `useSearchParams`, `usePathname`, or similar hooks, wrap client entry points in Suspense.
4. **Improve incident notes in changelog**
   - Track “root-cause vs surfaced-cause” so sequential blockers are easier to interpret.

---

## Executive Summary
The build failure message about `useSearchParams` was a framework usage issue in the teacher attendance page, not a network/font issue. After decoupling Google Fonts from build and restructuring `/teacher/attendance` to use a Suspense-wrapped client component, the build now succeeds. The remaining chart warnings are non-blocking and should be handled in a follow-up hardening task.

---

## Part A — User Product Experience

### 1) Target audience analysis (User-facing)
- **Admins:** run school ERP, onboarding, and compliance/ops visibility.
- **Teachers:** daily classroom workflows plus AI teaching support.
- **Students:** study help, assignments, and personalized AI support.
- **Parents:** progress visibility and actionable updates.
- **Current fit:** strong breadth of role coverage, but first-run coherence and “what to do next” guidance still needs simplification for non-technical users.

### 2) Current usability assessment (User-facing)
- **Setup/onboarding:** hosted login is easy, but onboarding flow can feel fragile when backend/UI parity is imperfect.
- **Daily workflows:** rich features exist, but users can feel navigation overload.
- **Error feedback:** many backend errors are clear, but frontend messages are often too generic for end users.
- **Documentation for users:** extensive docs exist, but user journeys should be more role-task focused (e.g., “first class setup”, “first assessment”).

### 3) Product experience gap analysis (User-facing)
- Gap between feature-rich system and guided first success.
- Gap between many pages and clear day-1/day-2 workflows.
- Gap between AI power and trust UX (confidence/fallback/queue expectations).

### 4) Recommended UX improvements (User-facing)
- Role-specific first-run checklists (admin, teacher, parent, student).
- Task-first navigation (“Today’s tasks”, “Set up class”, “Assign assessment”).
- Typed user-facing error states with clear actions (“Retry now”, “Contact admin”, “Try simplified mode”).
- AI fallback UX for high load (queue estimate + status + lightweight response mode).
- User help overlays in key modules (onboarding, assessment generation, reports).

### 5) Feature suggestions by user type
- **Admins:** onboarding completion dashboard, health summary, action center.
- **Teachers:** classroom command center, misconception analytics, guided assessment lifecycle.
- **Students:** weekly learning path + confidence-aware response UI.
- **Parents:** narrative timeline + weekly action recommendations.

### 6) Ideal user journey (Hosted)
- Login to hosted website.
- See role-specific “Start here” checklist.
- Complete one high-value success task in <10 minutes.
- Continue with contextual suggestions (“Next best action”).
- Use support prompt with trace/reference IDs when errors occur.

### 7) Interface recommendations (User-facing)
- Prioritize a hosted web dashboard with progressive disclosure.
- Keep user workflows focused on outcomes, not system architecture.
- Add inline trust indicators for AI outputs (citations, confidence, source visibility).

### 8) Maturity (User-facing)
- Early product, strong pilot readiness for hosted school usage.
- Needs better first-run UX consistency and clearer fallback behavior during AI load spikes.

### 9) User roadmap

**Immediate (0–4 weeks):**
- Role-specific onboarding checklists.
- Better user-facing error remediation.
- AI queue/fallback messaging.

**Short-term (1–2 months):**
- Teacher/admin task-centered dashboards.
- Parent narrative progress improvements.

**Medium-term (2–4 months):**
- Personalization and trust UX enhancements.
- Guided module discovery by role.
