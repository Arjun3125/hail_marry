# Mobile Responsiveness Design Spec

**Date:** 2026-04-15

---

## Goal

Make VidyOS fully usable on mobile (320px–767px) and tablet (768px–1023px) for all four user roles: student, teacher, parent, admin.

---

## Section 1: Architecture & Files

### New Files

- `frontend/src/components/nav/BottomNavConfig.ts` — role-to-tabs mapping (pure config, no JSX)
- `frontend/src/components/nav/BottomNav.tsx` — mobile bottom navigation bar component

### Modified Files

| File | Change |
|------|--------|
| `frontend/src/app/layout.tsx` | Add viewport meta with `viewport-fit=cover`; render `<BottomNav />` inside body |
| `frontend/src/app/globals.css` | Add `--bottom-nav-height: 4.5rem` CSS variable; add `pb-[var(--bottom-nav-height)]` utility |
| `frontend/src/app/login/page.tsx` | Google button container: `w-full max-w-sm`; `data-width="auto"` on GSI div |
| `frontend/src/app/teacher/dashboard/TeacherDashboardClient.tsx` | Add `sm:grid-cols-2` on stat card grid |
| `frontend/src/app/parent/dashboard/ParentDashboardClient.tsx` | Add `sm:grid-cols-2` on stat card grid |
| `frontend/src/app/admin/dashboard/AdminDashboardClient.tsx` | Add `sm:grid-cols-2` on stat card grid |
| `frontend/src/app/student/ai-studio/page.tsx` | Add `max-w-screen-xl mx-auto w-full` to top wrapper |

---

## Section 2: BottomNav Component Behavior

### Config Type

```ts
// BottomNavConfig.ts
import { LucideIcon } from "lucide-react";

export type NavTab = {
  label: string;
  path: string;
  icon: LucideIcon;
};

export type BottomNavConfig = Record<"student" | "teacher" | "parent" | "admin", NavTab[]>;
```

### Tab Lists

**Student** (role prefix: `/student`):
| Label | Path | Icon |
|-------|------|------|
| Overview | `/student/overview` | `LayoutDashboard` |
| AI Studio | `/student/ai-studio` | `Sparkles` |
| Assignments | `/student/assignments` | `ClipboardList` |
| Upload | `/student/upload` | `Upload` |
| Assistant | `/student/assistant` | `Bot` |

**Teacher** (role prefix: `/teacher`):
| Label | Path | Icon |
|-------|------|------|
| Dashboard | `/teacher/dashboard` | `LayoutDashboard` |
| Classes | `/teacher/classes` | `BookOpen` |
| Attendance | `/teacher/attendance` | `UserCheck` |
| Upload | `/teacher/upload` | `Upload` |
| Assistant | `/teacher/assistant` | `Bot` |

**Parent** (role prefix: `/parent`):
| Label | Path | Icon |
|-------|------|------|
| Dashboard | `/parent/dashboard` | `LayoutDashboard` |
| Attendance | `/parent/attendance` | `UserCheck` |
| Results | `/parent/results` | `BarChart2` |
| Reports | `/parent/reports` | `FileText` |
| Assistant | `/parent/assistant` | `Bot` |

**Admin** (role prefix: `/admin`):
| Label | Path | Icon |
|-------|------|------|
| Dashboard | `/admin/dashboard` | `LayoutDashboard` |
| Users | `/admin/users` | `Users` |
| Classes | `/admin/classes` | `BookOpen` |
| Queue | `/admin/queue` | `ListOrdered` |
| Assistant | `/admin/assistant` | `Bot` |

### Component Behavior

- **Visibility:** `fixed bottom-0 left-0 right-0 lg:hidden` — visible below 1024px, hidden at desktop
- **Role detection:** derive from `usePathname()` — first segment (e.g. `/student/...` → `student`)
- **Active state:** `pathname.startsWith(tab.path)` — highlight with `text-[var(--primary)]`, inactive `text-[var(--text-muted)]`
- **Safe area:** `pb-[env(safe-area-inset-bottom)]` on the nav container for notched phones
- **Height:** `h-[var(--bottom-nav-height)]` (4.5rem) so page content can pad-bottom to avoid overlap
- **Background:** `bg-[var(--bg-surface)] border-t border-[var(--border)]`
- **Coexistence with sidebar:** BottomNav is mobile-only (`lg:hidden`); desktop sidebar is desktop-only (`hidden lg:flex` or similar). No conflict.
- **Content padding:** `layout.tsx` wraps `<main>` with `pb-[var(--bottom-nav-height)] lg:pb-0` so content doesn't hide behind nav

### Role-Unknown Fallback

If pathname doesn't match any known role prefix, render nothing (`return null`).

---

## Section 3: Other Mobile Fixes

### 3a. Viewport Meta (`layout.tsx`)

Add to `<head>`:
```html
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
```
`viewport-fit=cover` enables `env(safe-area-inset-*)` CSS variables on notched iPhones.

### 3b. Google Sign-In Button (`login/page.tsx`)

- Wrap the GSI button div with `<div className="w-full max-w-sm">`
- Add `data-width="auto"` attribute to the `<div data-type="standard" ...>` element so the GSI library respects container width instead of using its default fixed width

### 3c. Tablet Grid Breakpoints

Three dashboard clients have stat card grids that jump from `grid-cols-1` to `grid-cols-3` or `grid-cols-4` with no intermediate step. Fix: add `sm:grid-cols-2` to bridge the 768px–1023px gap.

Files:
- `TeacherDashboardClient.tsx` — stat card grid
- `ParentDashboardClient.tsx` — stat card grid
- `AdminDashboardClient.tsx` — stat card grid

### 3d. Content Width

Add `max-w-screen-xl mx-auto w-full px-4` to the top-level wrapper in `frontend/src/app/student/ai-studio/page.tsx` so content is horizontally bounded and has breathing room at mobile widths.

---

## Section 4: Testing

All changes are CSS/layout only (no logic changes). Manual test checklist:

| Test | Device | Pass Criteria |
|------|--------|---------------|
| Bottom nav visible | 375px width | Nav bar appears at bottom |
| Bottom nav hidden | 1024px+ | Nav bar not visible |
| Active tab highlight | Navigate between tabs | Active tab shows primary color |
| Safe area respected | iPhone notch (DevTools) | Content not hidden behind home indicator |
| No horizontal scroll | 320px width | Page fits within viewport |
| Google button | 375px login page | Button fills container, no overflow |
| Tablet stat grid | 768px–1023px | 2-column grid visible (not 1 or 3) |
| AI Studio content | 375px | px-4 padding, no edge-to-edge text |
| Content not hidden | 375px, any role page | Scrollable content not obscured by bottom nav |

No automated visual regression tests in scope.

---

## Constraints

- Use existing CSS variables (`--bg-surface`, `--border`, `--primary`, `--text-muted`) — no new color definitions
- No changes to desktop layout
- No new npm packages
- Bottom nav must not conflict with existing sidebar drawer on tablet/desktop
