# VidyaOS — Frontend

**Framework:** Next.js 16 · **UI:** React 19 · **Language:** TypeScript · **Styling:** Tailwind CSS 4  
**Last updated:** 2026-03-25

---

## Quick Start

```bash
npm install
cp .env.example .env.local        # Set NEXT_PUBLIC_API_URL
npm run dev                        # Development server at http://localhost:3000
npm run lint                       # ESLint check (0 errors expected)
npm run build                      # Production build
```

## Project Structure

```
frontend/src/
├── app/
│   ├── student/         # 16 routes — AI assistant, attendance, results, reviews, tools, etc.
│   ├── teacher/         # 11 routes — dashboard, insights, assessment generator, discover, etc.
│   ├── admin/           # 19 routes — dashboard, AI review, queue ops, webhooks, feature-flags, branding, etc.
│   ├── parent/          #  5 routes — dashboard, attendance, results, audio reports
│   ├── login/           # Google OAuth + email/password
│   ├── demo/            # Demo mode with role switching
│   ├── globals.css      # 50+ dark-mode-safe semantic CSS variables
│   ├── layout.tsx       # Root layout with ThemeProvider, BrandingProvider, PWA manifest
│   └── page.tsx         # Landing page
├── components/
│   ├── theme/
│   │   ├── ThemeToggle.tsx       # Dark/light mode toggle
│   │   └── BrandingProvider.tsx  # Global CSS variable injection for white-label branding
│   ├── GuidedTour.tsx            # Step-by-step product walkthrough
│   ├── DemoToolbar.tsx           # Demo mode role-switching toolbar
│   └── MascotWidget.tsx          # AI interview mascot
├── i18n/                # Hindi/Marathi/English translation files
└── lib/
    └── api.ts           # Centralized API client (auth, admin, student, teacher, parent, branding)
```

## Design System

All components use **CSS Custom Properties** (`var(--primary)`, `var(--bg-card)`, etc.) instead of hardcoded Tailwind colors. This enables:
- **Automatic dark mode** support via `next-themes`
- **Dynamic white-label branding** via the `BrandingProvider` context

| CSS Variable | Purpose |
|---|---|
| `--primary` | Brand primary color (overridden per tenant) |
| `--bg-card` | Card background |
| `--text-primary` | Main text color |
| `--text-muted` | Subdued text color |
| `--border` | Border color |
| `--bg-page` | Page background |

50+ variables defined in `globals.css`. No raw `text-gray-*`, `bg-white`, or `border-gray-*` in TSX files.

## Environment Variables

```env
NEXT_PUBLIC_API_URL=http://localhost:8000     # Backend API base URL
```

Typography note:
- declaring a tenant font family in branding only changes CSS variables
- custom fonts must still be loaded through `next/font` or explicit `@font-face` assets to avoid fallback-font regressions

## Key Features

- **Role-based routing** — 4 portals (student, teacher, admin, parent) with 51+ total routes
- **Dark mode** — Persistent via `next-themes` with `localStorage`
- **White-label branding** — Per-tenant logo, colors, and fonts via `BrandingProvider`
- **Feature management** — Admin dashboard to toggle 58 features with AI intensity badges and ERP module tags
- **System profiles** — Quick-apply buttons for AI Tutor, AI Helper, and Full ERP modes
- **PWA** — Installable, offline-capable via service worker
- **Real-time notifications** — WebSocket-based
- **Demo mode** — Role switching + guided walkthrough
- **Accessibility** — Skip navigation, ARIA labels, focus management
- **i18n** — Hindi, Marathi, and English support

## Admin Dashboard Routes

| Route | Purpose |
|---|---|
| `/admin/dashboard` | Executive KPIs and school overview |
| `/admin/ai-review` | AI response review with approve/flag |
| `/admin/ai-usage` | AI usage analytics |
| `/admin/billing` | Razorpay billing management |
| `/admin/branding` | White-label branding configuration |
| `/admin/classes` | Class and section management |
| `/admin/complaints` | Complaint tracking |
| `/admin/enterprise` | SSO, compliance, incidents |
| `/admin/feature-flags` | Feature toggles with AI profiles |
| `/admin/qr-cards` | Magic QR login card generation |
| `/admin/queue` | Background job queue operations |
| `/admin/reports` | Performance heatmaps and reports |
| `/admin/security` | Security settings |
| `/admin/settings` | General settings |
| `/admin/setup-wizard` | Initial tenant setup |
| `/admin/timetable` | Timetable management |
| `/admin/traces` | AI trace viewer |
| `/admin/users` | User management |
| `/admin/webhooks` | Webhook subscriptions |

## Related Docs

- [Root README](../README.md)
- [UI Design System](../documentation/system_docs/Ui%20design.md)
- [Sitemap & Wireframe](../documentation/system_docs/Sitemap%20wireframe.md)
- [Architecture](../documentation/system_docs/Architecture.md)
