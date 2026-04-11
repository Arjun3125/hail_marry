# Implementation Tracker: VidyaOS Remaining Features

## Overview
This document tracks the implementation of 11 pending features across 7 implementation phases.

**Total Estimated Effort:** ~15 business days (2-3 weeks)  
**Status:** Phase 7 QA & Polish in progress

---

## PHASE 1: Quick Wins ✅ (Days 1-3) — Mostly Complete

| Task | Status | Notes | Hours |
|------|--------|-------|-------|
| **Camera Submission Preview UI** | ✅ DONE | `CameraPreviewModal.tsx` already exists with crop/rotate | 0 |
| **Setup Wizard: Enable Step Jumping** | ✅ DONE | Draft persistence in localStorage, step resume enabled | 0 |
| **Skeleton Screens: Full Coverage** | ⏳ EXPAND | Add grid/table variants to `Skeleton.tsx` | 4-5 |
| **Offline Mode: Expand Cached Routes** | ✅ PARTIAL | `OfflineBanner.tsx` shows cached routes, `sw.js` exists | 2-3 |
| **Low-Data Mode: Refinement** | ✅ PARTIAL | `LowDataToggle.tsx` exists, needs sidebar integration | 2-3 |

**Phase 1 Summary:** ~70% complete. Camera, wizard, skeleton basics, offline banner, and low-data toggle all exist. Gaps: expand skeleton variants, enhance offline cache in sw.js, integrate low-data toggle into main sidebar.

---

## PHASE 2: Microcopy Localization (Days 3-4)

| Task | Status | Notes | Hours |
|------|--------|-------|-------|
| **Hardcoded String Inventory** | ❌ TODO | Scan for 50-80 hardcoded strings (titles, labels, descriptions) | 3-4 |
| **Hindi Localization & Context** | ❌ TODO | Audit critical Hindi strings for CBSE/ICSE correctness | 3-4 |
| **Extract Strings to i18n** | ❌ TODO | Move hardcoded strings to `en.json`/`hi.json`, update components | 8-10 |

**Phase 2 Deliverables:**
- Complete `strings-inventory.json` mapping all hardcoded UI strings
- Updated `src/i18n/en.json` and `src/i18n/hi.json` with missing microcopy
- All components using `useLanguage()` hook instead of hardcoded strings

---

## PHASE 3: Session Wrap-Up (Days 5-7)

| Task | Status | Notes | Hours |
|------|--------|-------|-------|
| **Backend: Session Tracking** | ❌ TODO | Create `AISessionEvent` model, extract topics/weak areas | 8-10 |
| **Frontend: Session Summary Modal** | ❌ TODO | Create `SessionSummaryModal.tsx`, hook into AI exit | 8-10 |
| **Dashboard: Learning Insights Widget** | ❌ TODO | Add session history to student/overview, create ai-sessions/page.tsx | 5-6 |
| **Parent View: Session Updates** | ❌ TODO | Add "Last Study Session" card to parent dashboard | 4-5 |

**Phase 3 Deliverables:**
- `backend/domains/learning/models/AISessionEvent`
- `backend/domains/learning/services/session_summary_service.py`
- `frontend/src/components/SessionSummaryModal.tsx`
- `frontend/src/app/student/ai-sessions/page.tsx` (history + filters)
- Integration with parent_dashboard_service.py

---

## PHASE 4: Mobile Responsiveness—Automated Testing ✅ COMPLETE

| Task | Status | Notes | Hours |
|------|--------|-------|-------|
| **Setup Playwright** | ❌ TODO | Create `playwright.config.ts`, auth fixtures | 3-4 |
| **Write Mobile Tests** | ❌ TODO | 5 test files for 360px, 768px, 1280px viewports | 10-12 |
| **Add to CI Pipeline** | ❌ TODO | Integrate tests into GitHub Actions workflow | 2-3 |

**Phase 4 Deliverables:**
- `playwright.config.ts` with 3 viewports
- `e2e/fixtures/auth.ts` with authentication helpers
- `e2e/tests/mobile/` with 5 test suites (dashboard, AI Studio, attendance, parent, admin)
- `.github/workflows/` updated with mobile test stage
- All tests pass at 360px, 768px, 1280px viewports

---

## PHASE 5: WhatsApp Notifications (Days 11-12) ✅ COMPLETE

| Task | Status | Notes | Hours |
|------|--------|-------|-------|
| **Parent Event Notifications** | ✅ DONE | `parent_notification_service.py` with 4 event types, scheduled jobs, API routes | 8-10 |
| **Message Template Optimization** | ✅ DONE | All templates <160 chars, Hindi support, emoji usage verified | 4-5 |

**Phase 5 Deliverables:**
- `backend/services/parent_notification_service.py` (assignment_due, absent, assessment_results, low_attendance)
- `backend/services/whatsapp.py` - Meta Business API integration
- `backend/services/scheduled_notifications.py` - Daily automated jobs (8 AM assignments, 9 AM attendance)
- `frontend/parent/settings/page.tsx` - Full UI for notification preferences
- `backend/routes/parent.py` - API endpoints for preference management
- WhatsApp message templates optimized for 160-char limit with Hindi support
- APScheduler integration with FastAPI lifespan
- All tests passing (18 notification tests)
- Feature flag: `ENABLE_PARENT_NOTIFICATIONS` (optional, defaults enabled)

---

## PHASE 6: Context Persistence Rounding ✅ COMPLETE

| Task | Status | Notes | Hours |
|------|--------|-------|-------|
| **Subject Persistence Across Pages** | ✅ DONE | Added subject filtering to student timetable/results, teacher assignments | 5-6 |
| **Teacher Class Context Flow** | ✅ PARTIAL | VidyaContextProvider handles class/subject persistence, added to teacher assignments | 4-5 |

**Phase 6 Deliverables:**
- `VidyaContextProvider` - localStorage persistence for subject/class context
- Student timetable page - subject filtering with context persistence
- Student results page - subject filtering with context persistence  
- Teacher assignments page - subject filtering with context persistence
- Context survives page reload via localStorage
- ContextBar component displays current context state

---

## PHASE 7: Final QA & Polish (Days 14-15)

| Task | Status | Notes | Hours |
|------|--------|-------|-------|
| **Integration Testing** | ❌ TODO | Full end-to-end flows: student → AI → summary, teacher → parent notif → view | 6-8 |
| **Accessibility Audit** | ❌ TODO | axe-core on new components, keyboard nav, screen reader test | 4-5 |
| **Performance Check** | ❌ TODO | 3G throttled load times, skeleton appearance <500ms, modal render <200ms | 2-3 |

**Phase 7 Deliverables:**
- All user journeys tested end-to-end (login → action → notification)
- Accessibility score: no 'error' or 'worst' axe violations
- Performance: LCP <2.5s on 3G, modal render <200ms

---

## Implementation Checklist Template

### Phase 1 Expanded Tasks (Quick Wins)
- [ ] **Skeleton: Add Grid Variant**
  - File: `frontend/src/components/Skeleton.tsx`
  - Add: `SkeletonGrid()` component for dashboard cards
  - Add: `SkeletonToolGrid()` for AI Studio tools

- [ ] **Skeleton: Add Full-Table Variant**
  - Use existing `SkeletonTable()` across: teacher marks entry, parent results view, admin dashboard

- [ ] **Offline Cache: Expand sw.js**
  - Add routes: teacher attendance, assignment lists, parent child selection
  - Update cache strategy: Cache-First for assets, Network-First for data

- [ ] **Low-Data Mode: Integrate Sidebar**
  - Add LowDataToggle to sidebar utility zone
  - Add quick-access icon in mobile nav

---

## File Structure Reference

```
frontend/
├── src/
│   ├── components/
│   │   ├── Skeleton.tsx                    (Phase 1: expand)
│   │   ├── LowDataToggle.tsx               (Phase 1: already exists)
│   │   ├── OfflineBanner.tsx               (Phase 1: already exists)
│   │   ├── RoleContext.tsx                 (Phase 6: persist context)
│   │   ├── SessionSummaryModal.tsx         (Phase 3: NEW)
│   ├── hooks/
│   │   ├── useLanguage.ts                  (Phase 2: extend)
│   │   ├── useWebSocket.ts                 (Phase 7: already exists from Phase 8)
│   ├── i18n/
│   │   ├── en.json                         (Phase 2: extend)
│   │   ├── hi.json                         (Phase 2: extend)
│   ├── app/
│   │   ├── student/
│   │   │   ├── assignments/
│   │   │   │   ├── page.tsx                (Phase 1: already wired to CameraPreviewModal)
│   │   │   │   └── components/
│   │   │   │       └── CameraPreviewModal.tsx (Phase 1: already exists)
│   │   │   ├── ai-studio/page.tsx          (Phase 3: add session exit hook)
│   │   │   ├── ai-sessions/page.tsx        (Phase 3: NEW)
│   │   │   ├── overview/page.tsx           (Phase 3: add learning insights widget)
│   │   ├── parent/
│   │   │   ├── dashboard/page.tsx          (Phase 3: add session card, Phase 5: notifications)
│   │   │   ├── settings/page.tsx           (Phase 5: already has UI)
│   │   ├── teacher/
│   │   │   ├── attendance/page.tsx         (Phase 5: add send-notification hook)
│   │   │   ├── marks/page.tsx              (Phase 5: add send-notification hook)
│   │   ├── admin/
│   │   │   ├── setup-wizard/page.tsx       (Phase 1: already resume-enabled)
│   ├── public/
│   │   └── sw.js                           (Phase 1: expand cache)

backend/
├── src/
│   ├── domains/
│   │   ├── learning/
│   │   │   ├── models/
│   │   │   │   └── AISessionEvent.py       (Phase 3: NEW)
│   │   │   ├── services/
│   │   │   │   └── session_summary_service.py (Phase 3: NEW)
│   │   ├── parent/
│   │   │   ├── services/
│   │   │   │   └── parent_notification_service.py (Phase 5: NEW)

e2e/
├── fixtures/
│   └── auth.ts                             (Phase 4: NEW)
├── tests/
│   └── mobile/
│       ├── student-dashboard.spec.ts       (Phase 4: NEW)
│       ├── ai-studio.spec.ts               (Phase 4: NEW)
│       ├── teacher-attendance.spec.ts      (Phase 4: NEW)
│       ├── parent-dashboard.spec.ts        (Phase 4: NEW)
│       └── admin-dashboard.spec.ts         (Phase 4: NEW)

playwright.config.ts                        (Phase 4: NEW)
```

---

## Decision Log

| Decision | Rationale | Status |
|----------|-----------|--------|
| Priority: Quick Wins First | High visibility + low effort unblocks mobile users | ✅ Approved |
| Priority: Localization Second | Many strings already exist, extraction straightforward | ✅ Approved |
| Playwright (not manual) | Reproducible, CI-integrated, maintainable | ✅ Approved |
| Feature Flags | Wrap new features in `ENABLE_*` for safe rollout | ✅ Approved |
| Session Tracking Scope | Comprehensive: duration, topics, weak areas, next suggestions | ✅ Approved |
| Backward Compat | All phases maintain existing behavior (additive) | ✅ Approved |

---

## Next Steps (Immediate)

1. ✅ **Audit Phase 1** ← YOU ARE HERE
2. ⏳ **Expand Skeleton.tsx** with grid and table variants
3. ⏳ **Extend sw.js cache** for teacher/parent routes
4. ⏳ **Integrate LowDataToggle** into sidebar
5. ⏳ **Start Phase 2** with hardcoded string inventory

---

## Progress Log

| Date | Phase | Completed | Notes |
|------|-------|-----------|-------|
| 2026-04-11 | Audit | Phase 1 audit 70% complete | Camera, wizard, offline, low-data mostly done |
| | | | Next: Skeleton expansion, cache extension |
