# VidyaOS — Frontend

**Framework:** Next.js 16 · **UI:** React 19 · **Language:** TypeScript · **Styling:** Tailwind CSS 4  
**Last updated:** 2026-03-11

---

## Quick Start

```bash
npm install
npm run dev          # Development server at http://localhost:3000
npm run lint         # ESLint check (0 errors expected)
npm run build        # Production build (50 pages)
```

## Project Structure

```
frontend/src/app/
├── student/         # 12 routes — AI assistant, attendance, results, reviews, etc.
├── teacher/         # 10 routes — dashboard, insights, assessment generator, etc.
├── admin/           # 12 routes — dashboard, AI review, queue ops, webhooks, etc.
├── parent/          # 5 routes — dashboard, attendance, results, audio reports
├── login/           # Google OAuth + email/password
├── demo/            # Demo mode with role switching
├── globals.css      # 50+ dark-mode-safe semantic CSS utilities
├── layout.tsx       # Root layout with ThemeProvider, PWA manifest, skip nav
└── page.tsx         # Landing page
```

## Design System

All components use **semantic CSS utility classes** instead of hardcoded Tailwind colors. This ensures automatic dark mode support.

| Utility Class | Light | Dark |
|---|---|---|
| `.bg-card` | `#FFFFFF` | `#1F2937` |
| `.text-primary` | `#1F2937` | `#F9FAFB` |
| `.text-muted` | `#6B7280` | `#9CA3AF` |
| `.border-default` | `#E5E7EB` | `#374151` |
| `.bg-surface` | `#F3F4F6` | `#111827` |

50+ utilities defined in `globals.css`. No raw `text-gray-*`, `bg-white`, or `border-gray-*` in TSX files.

## Environment Variables

```env
NEXT_PUBLIC_API_URL=http://localhost:8000     # Backend API base URL
```

## Key Features

- **Role-based routing** — 4 portals (student, teacher, admin, parent)
- **Dark mode** — Persistent via `next-themes` with `localStorage`
- **PWA** — Installable, offline-capable via service worker
- **Real-time notifications** — WebSocket-based
- **Demo mode** — Role switching + guided walkthrough
- **Accessibility** — Skip navigation, ARIA labels, focus management

## Related Docs

- [UI Design System](../documentation/system_docs/Ui%20design.md)
- [Sitemap & Wireframe](../documentation/system_docs/Sitemap%20wireframe.md)
- [Architecture](../documentation/system_docs/Architecture.md)
