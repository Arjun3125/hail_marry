# UI Design

**Project:** VidyaOS – AI Infrastructure for Educational Institutions  
**Version:** v0.1  
**Design Goal:** Institutional-Grade, Calm, Structured, Academically Aligned

---

## 1. Design Philosophy

The UI must feel:
- **Academic** — like a modern university portal
- **Structured** — clear hierarchy, consistent layout
- **Trustworthy** — calm colors, no gimmicks
- **Minimal** — every element earns its place
- **Quietly intelligent** — AI is embedded, not showy

It must NOT feel:
- ❌ Startup flashy
- ❌ Social media-like
- ❌ Gamified / animated
- ❌ Dark hacker-themed
- ❌ ChatGPT-style bubble chaos

> Education is clarity. The UI should feel like structured knowledge, not entertainment.

---

## 2. Color System

### Primary Palette

| Role | Hex | Usage |
|---|---|---|
| Primary Blue | `#2C5AA0` | CTAs, active states, links |
| Soft Blue | `#E8F0FE` | Backgrounds, hover states |
| Neutral Dark | `#1F2937` | Primary text |
| Neutral Gray | `#6B7280` | Secondary text, metadata |
| Light Gray | `#F3F4F6` | Page backgrounds, dividers |
| White | `#FFFFFF` | Card backgrounds, content areas |

Blue signals education & trust.

### Accent Colors (Indicators Only)

| Purpose | Hex | Usage |
|---|---|---|
| Success / Healthy | `#16A34A` | Good scores, present attendance |
| Warning | `#F59E0B` | Moderate performance, nearing limits |
| Error / Action Required | `#DC2626` | Failed, absent, critical alerts |

No gradients. No neon. Accents used sparingly.

---

## 3. Typography

### Font Family
**Primary:** Geist (Google Fonts)  
**Fallback:** system-ui

No decorative or serif fonts. Clean, legible, modern.

### Typography Scale

| Element | Size | Weight |
|---|---|---|
| Page Title | 24px | 600 |
| Section Title | 18px | 600 |
| Card Title | 16px | 500 |
| Body Text | 14px | 400 |
| Metadata / Labels | 12px | 400 |

**Line height:** 1.5–1.6 for all body text.

---

## 4. Layout System

- **Grid:** 12-column layout
- **Outer margin:** 24px
- **Internal padding:** 16px
- **Spacing increments:** 8px base (8, 16, 24, 32, 48)

Consistency builds trust. Use the spacing scale everywhere.

---

## 5. Navigation

### Sidebar (Desktop)
- Width: 240px
- Background: White
- Border-right: 1px `#E5E7EB`
- Active item: Soft blue background + 3px blue left accent
- Hover: Slight gray highlight
- No heavy animations

### Top Bar
- Height: 60px
- Logo (left), Notifications + Profile (right)
- Subtle shadow (not heavy)

### Mobile (Phase 2)
- Sidebar → Bottom navigation bar
- KPI cards stack vertically
- AI assistant full-width

---

## 6. Component Patterns

### Cards
- White background, 8px border radius
- Soft shadow (`0 1px 3px rgba(0,0,0,0.08)`)
- 16px padding
- No thick borders

### KPI Card
```
┌──────────────────────┐
│ Attendance            │  ← 12px label, gray
│ 92%                   │  ← 24px number, dark
│ Trend: +2% ↑          │  ← 12px metadata, green
└──────────────────────┘
```

### Buttons
| Type | Style |
|---|---|
| Primary | Blue background, white text, medium weight |
| Secondary | White background, blue border, blue text |
| Danger | Red background, white text (used rarely) |

No flashy gradients. 6px border radius. 40px height.

### Forms & Inputs
- Input height: 40px
- Subtle border (`#D1D5DB`)
- Rounded corners: 6px
- Blue focus ring (`#2C5AA0`)
- Labels above input (never placeholder-only)

### Tables
- Subtle zebra striping (alternate row: `#F9FAFB`)
- Sticky header
- Hover highlight
- Sortable column indicators
- No heavy borders

---

## 7. Charts

- Use primary blue as main color
- Light gridlines (`#F3F4F6`)
- Minimal legends
- No neon colors

Academic clarity > visual noise.

---

## 8. AI Assistant UI

The AI interface must feel **structured, not chatty**.

```
┌─────────────────────────────────────────┐
│ Ask about your notes...                  │  ← Input field
├─────────────────────────────────────────┤
│ Mode: [Q&A] [Study Guide] [Quiz]        │  ← Mode selector
├─────────────────────────────────────────┤
│                                          │
│ AI Response                              │  ← Left-aligned blocks
│ Text answer with clear paragraphs...     │
│                                          │
│ Citations:                               │
│ [Biology_Ch3_p12] [Biology_Ch3_p14]     │  ← Expandable refs
└─────────────────────────────────────────┘
```

**Rules:**
- No speech bubbles (not WhatsApp)
- Left-aligned text blocks
- Clear separation between query and response
- Citations as clickable document references

---

## 9. Icons

**Use:** Lucide or Heroicons — simple, outline style, consistent  
**Avoid:** Emoji, cartoonish icons, excessive symbols

---

## 10. Spacing & White Space

White space is part of the academic aesthetic. Avoid cramped layouts.  
Breathing room increases perceived quality and reduces cognitive load.

---

## 11. Microinteractions

**Allowed:**
- Subtle hover effects (background color change)
- Smooth fade transitions (150–200ms)
- Loading skeletons (content placeholder)

**Not allowed:**
- Bounce animations
- Slide transitions everywhere
- Over-animated dashboards
- Confetti or celebration effects

---

## 12. Accessibility

Must include:
- WCAG AA contrast ratios (4.5:1 minimum for text)
- Keyboard navigation (all interactive elements)
- Screen reader support (ARIA labels)
- Proper label associations (form elements)
- Focus states (visible focus rings)
- Skip-to-content link

Education tools must be accessible to all students.

---

## 13. Dark Mode (Accessibility Option)

While the primary design is light/institutional, dark mode is available as an **accessibility preference**.
**Current implementation defaults to dark** via `next-themes` and persists user choice.

- Background: `#111827`
- Card: `#1F2937`
- Text: `#F9FAFB`
- Accent: Same blue (`#2C5AA0`)
- Controlled via user settings toggle

### Implementation: Dark-Mode-Safe Design System

All 50 frontend pages use **semantic CSS utility classes** defined in `frontend/src/app/globals.css` instead of hardcoded Tailwind color classes. This ensures automatic dark mode support.

| Utility Class | Light Mode | Dark Mode |
|---|---|---|
| `.bg-card` | `#FFFFFF` | `#1F2937` |
| `.text-primary` | `#1F2937` | `#F9FAFB` |
| `.text-muted` | `#6B7280` | `#9CA3AF` |
| `.border-default` | `#E5E7EB` | `#374151` |
| `.bg-surface` | `#F3F4F6` | `#111827` |
| `.bg-hover` | `#F9FAFB` | `#374151` |
| `.accent-blue` | `#2C5AA0` | `#60A5FA` |

50+ semantic utilities replace all hardcoded `text-gray-*`, `bg-white`, `border-gray-*` etc. across all components and pages. No raw color values appear in TSX files.

---

## 14. White-Label Branding (Per-Tenant Theming)

Beyond the base dark/light color system, VidyaOS supports **per-tenant branding** that overrides the default palette:

### How It Works
1. Admin uploads school logo at `/admin/branding`
2. Backend `colorthief` extracts dominant color and generates secondary/accent with WCAG 2.1 contrast validation
3. Colors stored on the `Tenant` record (`primary_color`, `secondary_color`, `accent_color`)
4. Frontend `BrandingProvider` context injects CSS custom properties at the document root:
   - `--primary`, `--secondary`, `--accent`, `--font-sans`
5. All components reference these variables, so the entire UI updates instantly

### CSS Variable Hierarchy
| Priority | Source |
|---|---|
| 1 (highest) | Tenant branding overrides (`--primary` etc.) |
| 2 | Dark/light mode semantic utilities (`.bg-card`, `.text-primary`) |
| 3 (lowest) | Base Tailwind theme defaults |

This allows each school to see a fully branded portal without any code changes.

