# Mobile Responsiveness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make VidyOS fully usable on mobile for all 4 roles by adding an Assistant tab to the bottom nav on every role, fixing the Google sign-in button overflow, adding the viewport meta tag, and fixing tablet stat card grids.

**Architecture:** All 4 role layouts already use `MobileBottomNav` from `SharedUI.tsx` — just update each `mobileNav` array. CSS infrastructure (`.mobile-bottom-nav`, `.safe-bottom`, `--bottom-nav-height`) is already in `globals.css`. No new components needed.

**Tech Stack:** Next.js 14 App Router, TypeScript, Tailwind CSS v4, Lucide React icons

---

## File Map

| File | Change |
|------|--------|
| `frontend/src/app/layout.tsx` | Add viewport meta with `viewport-fit=cover` |
| `frontend/src/app/student/layout.tsx` | Replace mobileNav; add `Bot`, `ClipboardList` imports |
| `frontend/src/app/teacher/layout.tsx` | Replace mobileNav; add `Bot` import |
| `frontend/src/app/parent/layout.tsx` | Replace mobileNav; add `Bot` import |
| `frontend/src/app/admin/layout.tsx` | Replace mobileNav (all icons already imported) |
| `frontend/src/app/login/page.tsx` | Remove hardcoded `width: "320"` from GSI renderButton; wrap div in `w-full` |
| `frontend/src/app/teacher/dashboard/TeacherDashboardClient.tsx` | Add `sm:grid-cols-2` to stat card grid |
| `frontend/src/app/parent/dashboard/ParentDashboardClient.tsx` | Add `sm:grid-cols-2` to stat card grid |

---

## Task 1: Add Viewport Meta Tag

**Files:**
- Modify: `frontend/src/app/layout.tsx:77-79`

Context: `layout.tsx` already has a `<head>` block with one `<meta name="theme-color">` tag at line 78. We need to add the viewport meta. Currently there is no viewport meta, which means `env(safe-area-inset-bottom)` won't work on notched iPhones.

- [ ] **Step 1: Open the file and locate the `<head>` block**

Read `frontend/src/app/layout.tsx`. The `<head>` block is at lines 77–79:
```tsx
      <head>
        <meta name="theme-color" content="#0f172a" />
      </head>
```

- [ ] **Step 2: Add viewport meta**

Replace:
```tsx
      <head>
        <meta name="theme-color" content="#0f172a" />
      </head>
```
With:
```tsx
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
        <meta name="theme-color" content="#0f172a" />
      </head>
```

- [ ] **Step 3: Verify no TypeScript errors**

Run: `cd frontend && npx tsc --noEmit 2>&1 | head -20`
Expected: no new errors related to layout.tsx

- [ ] **Step 4: Commit**

```bash
git add frontend/src/app/layout.tsx
git commit -m "fix(mobile): add viewport meta with viewport-fit=cover"
```

---

## Task 2: Student Bottom Nav — Add Assistant Tab

**Files:**
- Modify: `frontend/src/app/student/layout.tsx`

Context: The current `mobileNav` array has 5 items: Home (`/student/overview`), Attendance, AI Studio, Ranks, Profile. Replace with: Overview, AI Studio, Assignments, Upload, Assistant. The student layout already imports `Upload` and `Wand2`. Need to add `Bot` and `ClipboardList` to the Lucide import.

- [ ] **Step 1: Add `Bot` and `ClipboardList` to the Lucide import**

The current import block starts at line 5 and includes many icons. Find the lucide-react import block and add `Bot` and `ClipboardList` to it.

Before (the import block, abbreviated — match on the closing brace line):
```tsx
    Target,
} from "lucide-react";
```
After:
```tsx
    Target,
    Bot,
    ClipboardList,
} from "lucide-react";
```

- [ ] **Step 2: Replace the `mobileNav` array**

Current array (lines 51–57):
```tsx
const mobileNav = [
    { label: "Home", href: "/student/overview", icon: LayoutDashboard },
    { label: "Attendance", href: "/student/attendance", icon: CalendarCheck },
    { label: "AI Studio", href: "/student/ai-studio", icon: Wand2 },
    { label: "Ranks", href: "/student/leaderboard", icon: Trophy },
    { label: "Profile", href: "/student/profile", icon: User },
];
```
Replace with:
```tsx
const mobileNav = [
    { label: "Overview", href: "/student/overview", icon: LayoutDashboard },
    { label: "AI Studio", href: "/student/ai-studio", icon: Wand2 },
    { label: "Assignments", href: "/student/assignments", icon: ClipboardList },
    { label: "Upload", href: "/student/upload", icon: Upload },
    { label: "Assistant", href: "/student/assistant", icon: Bot },
];
```

- [ ] **Step 3: Verify no TypeScript errors**

Run: `cd frontend && npx tsc --noEmit 2>&1 | head -20`
Expected: no new errors

- [ ] **Step 4: Commit**

```bash
git add frontend/src/app/student/layout.tsx
git commit -m "feat(mobile): add Assistant tab to student bottom nav"
```

---

## Task 3: Teacher Bottom Nav — Add Assistant Tab

**Files:**
- Modify: `frontend/src/app/teacher/layout.tsx`

Context: Current mobileNav has 5 items: My Classes, Attendance, Assessments, Insights, Profile. Replace with: Dashboard, Classes, Attendance, Upload, Assistant. `Upload` and `Users` are already imported. `Bot` is NOT imported — add it.

- [ ] **Step 1: Add `Bot` to the Lucide import**

Find the `} from "lucide-react";` closing line and add `Bot` before it:
```tsx
    User,
    Bot,
} from "lucide-react";
```

- [ ] **Step 2: Replace the `mobileNav` array**

Current array (lines 37–43):
```tsx
const mobileNav = [
    { label: "My Classes", href: "/teacher/dashboard", icon: LayoutDashboard },
    { label: "Attendance", href: "/teacher/attendance", icon: CalendarCheck },
    { label: "Assessments", href: "/teacher/generate-assessment", icon: ClipboardList },
    { label: "Insights", href: "/teacher/insights", icon: BarChart3 },
    { label: "Profile", href: "/teacher/profile", icon: User },
];
```
Replace with:
```tsx
const mobileNav = [
    { label: "Dashboard", href: "/teacher/dashboard", icon: LayoutDashboard },
    { label: "Classes", href: "/teacher/classes", icon: Users },
    { label: "Attendance", href: "/teacher/attendance", icon: CalendarCheck },
    { label: "Upload", href: "/teacher/upload", icon: Upload },
    { label: "Assistant", href: "/teacher/assistant", icon: Bot },
];
```

- [ ] **Step 3: Verify no TypeScript errors**

Run: `cd frontend && npx tsc --noEmit 2>&1 | head -20`
Expected: no new errors

- [ ] **Step 4: Commit**

```bash
git add frontend/src/app/teacher/layout.tsx
git commit -m "feat(mobile): add Assistant tab to teacher bottom nav"
```

---

## Task 4: Parent Bottom Nav — Add Assistant Tab

**Files:**
- Modify: `frontend/src/app/parent/layout.tsx`

Context: Current mobileNav has only 3 items: Dashboard, Attendance, Marks. Expand to 5: Dashboard, Attendance, Results, Reports, Assistant. `FileText` and `Award` are already imported. `Bot` is NOT imported — add it.

- [ ] **Step 1: Add `Bot` to the Lucide import**

Current imports end with:
```tsx
    Settings,
} from "lucide-react";
```
Change to:
```tsx
    Settings,
    Bot,
} from "lucide-react";
```

- [ ] **Step 2: Replace the `mobileNav` array**

Current array (lines 16–20):
```tsx
const mobileNav = [
    { label: "Dashboard", href: "/parent/dashboard", icon: LayoutDashboard },
    { label: "Attendance", href: "/parent/attendance", icon: CalendarCheck },
    { label: "Marks", href: "/parent/results", icon: Award },
];
```
Replace with:
```tsx
const mobileNav = [
    { label: "Dashboard", href: "/parent/dashboard", icon: LayoutDashboard },
    { label: "Attendance", href: "/parent/attendance", icon: CalendarCheck },
    { label: "Results", href: "/parent/results", icon: Award },
    { label: "Reports", href: "/parent/reports", icon: FileText },
    { label: "Assistant", href: "/parent/assistant", icon: Bot },
];
```

- [ ] **Step 3: Verify no TypeScript errors**

Run: `cd frontend && npx tsc --noEmit 2>&1 | head -20`
Expected: no new errors

- [ ] **Step 4: Commit**

```bash
git add frontend/src/app/parent/layout.tsx
git commit -m "feat(mobile): add Assistant tab to parent bottom nav"
```

---

## Task 5: Admin Bottom Nav — Add Assistant Tab

**Files:**
- Modify: `frontend/src/app/admin/layout.tsx`

Context: Current mobileNav has 4 items: Health, People, Traces, Settings. Replace with 5: Dashboard, Users, Classes, Queue, Assistant. All needed icons (`LayoutDashboard`, `Users`, `BookOpen`, `Activity`, `Bot`) are already imported in the admin layout.

- [ ] **Step 1: Replace the `mobileNav` array**

Current array (lines 52–57):
```tsx
const mobileNav = [
    { label: "Health", href: "/admin/dashboard", icon: LayoutDashboard },
    { label: "People", href: "/admin/users", icon: Users },
    { label: "Traces", href: "/admin/traces", icon: ScanSearch },
    { label: "Settings", href: "/admin/settings", icon: Settings },
];
```
Replace with:
```tsx
const mobileNav = [
    { label: "Dashboard", href: "/admin/dashboard", icon: LayoutDashboard },
    { label: "Users", href: "/admin/users", icon: Users },
    { label: "Classes", href: "/admin/classes", icon: BookOpen },
    { label: "Queue", href: "/admin/queue", icon: Activity },
    { label: "Assistant", href: "/admin/assistant", icon: Bot },
];
```

- [ ] **Step 2: Verify no TypeScript errors**

Run: `cd frontend && npx tsc --noEmit 2>&1 | head -20`
Expected: no new errors

- [ ] **Step 3: Commit**

```bash
git add frontend/src/app/admin/layout.tsx
git commit -m "feat(mobile): add Assistant tab to admin bottom nav"
```

---

## Task 6: Fix Google Sign-In Button Mobile Overflow

**Files:**
- Modify: `frontend/src/app/login/page.tsx:53-59,140-142`

Context: The GSI `renderButton` is called with `width: "320"` hardcoded. On 320px screens this can overflow. The containing div at line 140 is `<div className="mb-5 flex justify-center">`. Fix: remove `width` from the renderButton config so GSI uses its default responsive behavior, and wrap the button div in a `w-full flex justify-center` container.

- [ ] **Step 1: Remove the hardcoded `width` from `renderButton` config**

Current (lines 53–59):
```tsx
    window.google.accounts.id.renderButton(el, {
      theme: "outline",
      size: "large",
      width: "320",
      text: "signin_with",
      shape: "pill",
    });
```
Replace with:
```tsx
    window.google.accounts.id.renderButton(el, {
      theme: "outline",
      size: "large",
      text: "signin_with",
      shape: "pill",
    });
```

- [ ] **Step 2: Wrap the GSI div with a responsive container**

Current (line 140–142):
```tsx
              <div className="mb-5 flex justify-center">
                <div ref={initGoogle} />
              </div>
```
Replace with:
```tsx
              <div className="mb-5 flex justify-center">
                <div className="w-full max-w-xs" ref={initGoogle} />
              </div>
```

- [ ] **Step 3: Verify no TypeScript errors**

Run: `cd frontend && npx tsc --noEmit 2>&1 | head -20`
Expected: no new errors

- [ ] **Step 4: Commit**

```bash
git add frontend/src/app/login/page.tsx
git commit -m "fix(mobile): remove hardcoded GSI button width, use responsive container"
```

---

## Task 7: Teacher Dashboard — Fix Tablet Stat Grid

**Files:**
- Modify: `frontend/src/app/teacher/dashboard/TeacherDashboardClient.tsx:157`

Context: The "Since yesterday" section stat card grid at line 157 uses `md:grid-cols-3` with no intermediate `sm:` step. At 768px–1023px tablets this jumps straight from 1 column to 3 columns. Fix: add `sm:grid-cols-2` so there's a 2-column intermediate state at 640px–767px.

- [ ] **Step 1: Find the grid div**

Read `frontend/src/app/teacher/dashboard/TeacherDashboardClient.tsx` around line 157. The target line is:
```tsx
                        <div className="mt-4 grid gap-4 md:grid-cols-3">
```

- [ ] **Step 2: Add `sm:grid-cols-2`**

Replace:
```tsx
                        <div className="mt-4 grid gap-4 md:grid-cols-3">
```
With:
```tsx
                        <div className="mt-4 grid gap-4 sm:grid-cols-2 md:grid-cols-3">
```

- [ ] **Step 3: Verify no TypeScript errors**

Run: `cd frontend && npx tsc --noEmit 2>&1 | head -20`
Expected: no new errors

- [ ] **Step 4: Commit**

```bash
git add frontend/src/app/teacher/dashboard/TeacherDashboardClient.tsx
git commit -m "fix(mobile): add sm:grid-cols-2 tablet step to teacher stat grid"
```

---

## Task 8: Parent Dashboard — Fix Tablet Stat Grid

**Files:**
- Modify: `frontend/src/app/parent/dashboard/ParentDashboardClient.tsx:184`

Context: The stat card grid at line 184 uses `md:grid-cols-3` with no `sm:` step. Same issue as Task 7.

- [ ] **Step 1: Find the grid div**

Read `frontend/src/app/parent/dashboard/ParentDashboardClient.tsx` around line 184. The target line is:
```tsx
                    <div className="grid gap-4 md:grid-cols-3">
```

- [ ] **Step 2: Add `sm:grid-cols-2`**

Replace:
```tsx
                    <div className="grid gap-4 md:grid-cols-3">
```
With:
```tsx
                    <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-3">
```

- [ ] **Step 3: Verify no TypeScript errors**

Run: `cd frontend && npx tsc --noEmit 2>&1 | head -20`
Expected: no new errors

- [ ] **Step 4: Commit**

```bash
git add frontend/src/app/parent/dashboard/ParentDashboardClient.tsx
git commit -m "fix(mobile): add sm:grid-cols-2 tablet step to parent stat grid"
```

---

## Manual Test Checklist (run after all tasks)

Open Chrome DevTools → Toggle device toolbar.

| Test | Device width | Expected result |
|------|-------------|-----------------|
| Bottom nav visible | 375px, any role page | Nav bar appears at bottom with 5 tabs |
| Bottom nav hidden | 1024px+ | Nav bar not visible |
| Assistant tab active | Navigate to `/student/assistant` | Assistant tab highlighted in primary color |
| Safe area | iPhone 12 Pro (DevTools) | Nav not obscured behind home indicator |
| No horizontal scroll | 320px, login page | Page fits within viewport |
| Google button | 375px, login page | Button fills container, no horizontal overflow |
| Teacher stat grid | 700px (between sm and md) | 2-column stat cards (not 1 or 3) |
| Parent stat grid | 700px | 2-column stat cards |
| Viewport meta | Any DevTools mobile | `viewport-fit=cover` in page source head |
