# VidyaOS Enhancement Implementation Plan

Implement 9 feature enhancements across the full stack: new backend endpoints, services, models, and frontend components.

> [!NOTE]
> **Implementation Status (as of 2026-03-12):**
> - ✅ Enhancement 1: Bulk CSV Operations — Implemented
> - ⚠️ Enhancement 2: Real-Time Notifications — Implemented (in-memory only; not durable across multi-instance)
> - ✅ Enhancement 3: Offline-First PWA — Implemented
> - ✅ Enhancement 4: Dark Mode Persistence — Implemented (50+ semantic CSS utilities)
> - ✅ Enhancement 5: Student Progress Streak & Gamification — Implemented
> - ✅ Enhancement 6: Smart Weakness Alerts — Implemented
> - ⚠️ Enhancement 7: Parent Weekly Digest — Implemented (WhatsApp service; email digest generation exists but no send pipeline)
> - ⚠️ Enhancement 8: Teacher AI Co-Pilot for Grading — Partial (OCR-only output; full rubric scoring pending)
> - ✅ Enhancement 9: Accessibility Improvements — Implemented

## Proposed Changes

### Enhancement 1: Bulk CSV Operations for Teachers

#### [MODIFY] [teacher.py](file:///c:/Users/naren/Work/Projects/proxy_notebooklm/backend/routes/teacher.py)

Add 4 new endpoints after the existing attendance/marks sections:
- `POST /api/teacher/attendance/csv-import` — Parse CSV with columns `student_id,status`, apply to a class/date
- `GET /api/teacher/attendance/csv-export/{class_id}` — Export attendance as downloadable CSV
- `POST /api/teacher/marks/csv-import` — Parse CSV with `student_id,marks_obtained` for an exam
- `GET /api/teacher/marks/csv-export/{exam_id}` — Export marks as downloadable CSV

Uses existing `csv`, `io` imports already in the file. Reuses `_validate_student_in_class` and `_ensure_class_access`.

---

### Enhancement 2: Real-Time WebSocket Notifications

#### [NEW] [notifications.py](file:///c:/Users/naren/Work/Projects/proxy_notebooklm/backend/services/notifications.py)

In-memory notification store with `add_notification()` and `get_notifications()` functions. Thread-safe, keyed by `user_id`, auto-expires after configurable TTL.

#### [NEW] [notifications.py](file:///c:/Users/naren/Work/Projects/proxy_notebooklm/backend/routes/notifications.py)

- `WS /api/notifications/ws` — WebSocket endpoint, authenticates via token query param
- `GET /api/notifications` — REST fallback to fetch unread notifications
- `POST /api/notifications/{id}/read` — Mark as read

#### [MODIFY] [main.py](file:///c:/Users/naren/Work/Projects/proxy_notebooklm/backend/main.py)

Register the notifications router.

---

### Enhancement 3: Offline-First PWA

#### [NEW] [manifest.json](file:///c:/Users/naren/Work/Projects/proxy_notebooklm/frontend/public/manifest.json)

Standard PWA manifest with app name, theme color, icons, start URL.

#### [NEW] [sw.js](file:///c:/Users/naren/Work/Projects/proxy_notebooklm/frontend/public/sw.js)

Service worker with Cache-First for static assets, Network-First for API calls, offline fallback page.

#### [MODIFY] [layout.tsx](file:///c:/Users/naren/Work/Projects/proxy_notebooklm/frontend/src/app/layout.tsx)

Add manifest link, theme-color meta, and service worker registration script.

---

### Enhancement 4: Dark Mode Persistence

#### [MODIFY] [layout.tsx](file:///c:/Users/naren/Work/Projects/proxy_notebooklm/frontend/src/app/layout.tsx)

Change ThemeProvider `defaultTheme` from `"system"` to `"dark"` and add `storageKey="vidyaos-theme"`. The `next-themes` library automatically persists to localStorage with the storageKey prop.

---

### Enhancement 5: Student Progress Streak & Gamification

#### [NEW] [streak.py](file:///c:/Users/naren/Work/Projects/proxy_notebooklm/backend/models/streak.py)

SQLAlchemy model: `LoginStreak` with `user_id`, `current_streak`, `longest_streak`, `last_login_date`, `total_sessions`.

#### [NEW] [gamification.py](file:///c:/Users/naren/Work/Projects/proxy_notebooklm/backend/services/gamification.py)

Service with:
- `record_login(db, user)` — Updates streak logic (consecutive calendar days)
- `get_badges(db, user)` — Returns earned badges based on thresholds
- `get_streak_info(db, user)` — Returns streak data for dashboard

#### [MODIFY] [students.py](file:///c:/Users/naren/Work/Projects/proxy_notebooklm/backend/routes/students.py)

- Add `GET /api/student/streaks` endpoint
- Add streak/badge data to `student_dashboard` response

---

### Enhancement 6: Smart Weakness Alerts

#### [NEW] [weakness_alerts.py](file:///c:/Users/naren/Work/Projects/proxy_notebooklm/backend/services/weakness_alerts.py)

Service that scans `SubjectPerformance` for subjects where avg < 60%, generates actionable alert objects with recommended spaced repetition reviews.

#### [MODIFY] [students.py](file:///c:/Users/naren/Work/Projects/proxy_notebooklm/backend/routes/students.py)

Add `GET /api/student/weakness-alerts` endpoint that calls the service and returns alerts.

---

### Enhancement 7: Parent Weekly Digest Email

#### [NEW] [digest_email.py](file:///c:/Users/naren/Work/Projects/proxy_notebooklm/backend/services/digest_email.py)

Service that:
- Generates HTML digest for a parent (child's attendance, marks, AI usage)
- Provides `generate_digest_preview()` for API endpoint
- Provides `send_digest_email()` using SMTP (configurable)

#### [MODIFY] [parent.py](file:///c:/Users/naren/Work/Projects/proxy_notebooklm/backend/routes/parent.py)

Add `GET /api/parent/digest-preview` endpoint.

#### [MODIFY] [admin.py](file:///c:/Users/naren/Work/Projects/proxy_notebooklm/backend/routes/admin.py)

Add `POST /api/admin/trigger-digest` to manually trigger digest emails.

---

### Enhancement 8: Teacher AI Co-Pilot for Grading

#### [MODIFY] [teacher.py](file:///c:/Users/naren/Work/Projects/proxy_notebooklm/backend/routes/teacher.py)

Add `POST /api/teacher/ai-grade` endpoint:
- Accepts image upload of answer sheet
- Queues AI job via existing AI queue
- Returns job ID for polling/WebSocket notification

---

### Enhancement 9: Accessibility Improvements

#### [MODIFY] [layout.tsx](file:///c:/Users/naren/Work/Projects/proxy_notebooklm/frontend/src/app/layout.tsx)

- Add skip navigation link
- Add `aria-live="polite"` announcement region

#### [NEW] [ScreenReaderAnnouncer.tsx](file:///c:/Users/naren/Work/Projects/proxy_notebooklm/frontend/src/components/ScreenReaderAnnouncer.tsx)

Client component providing dynamic screen reader announcements for content updates.

---

## New Test Files

#### [NEW] [test_csv_bulk_ops.py](file:///c:/Users/naren/Work/Projects/proxy_notebooklm/backend/tests/test_csv_bulk_ops.py)

Tests for CSV import/export endpoints.

#### [NEW] [test_gamification.py](file:///c:/Users/naren/Work/Projects/proxy_notebooklm/backend/tests/test_gamification.py)

Tests for streak tracking and badge logic.

#### [NEW] [test_weakness_alerts.py](file:///c:/Users/naren/Work/Projects/proxy_notebooklm/backend/tests/test_weakness_alerts.py)

Tests for weakness alert generation threshold logic.

---

## Verification Plan

### Automated Tests
```bash
cd backend && python -m pytest tests/ -v   # 382 tests across 48 files
cd frontend && npm run lint && npm run build
```
