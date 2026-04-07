# Prism Immersive Redesign Contract

## Purpose

This document defines the canonical visual and implementation contract for the
full-product frontend redesign. The redesign is implemented in the application
codebase, while `C:\Users\naren\Work\Forks\design-plugin` is used as the local
design exploration workflow for generating and comparing variants before code is
finalized.

## Design Direction

- Tone: premium, clear, and operationally credible
- Density: moderate across dashboards, roomier on public surfaces
- Depth: layered 2.5D by default, selective 3D only where it materially helps
- Accessibility: readable contrast, keyboard-safe focus, reduced-motion support
- Runtime rule: no backend or route contract changes for visual work

## Canonical Visual System

### Foundations

- Fonts
  - Display: `Space Grotesk`
  - Body/UI: `Manrope`
- Theme host
  - Shared variables and surfaces live in `frontend/src/app/globals.css`
- Ambient scene
  - `PrismBackdrop` provides grid, glow, noise, and horizon layers

### Shared Primitives

- `PrismPage`
  - route-level page container
- `PrismSection`
  - page section rhythm and width control
- `PrismPanel`
  - translucent elevated panel surface
- `PrismHeroKicker`
  - compact section label / overline
- `PrismPageIntro`
  - shared route-level intro composition
- `PrismSectionHeader`
  - shared section heading pattern for overview, detail, and insight zones
- `PrismControls`
  - shared inputs, selects, search, pagination, tabs, and table shells
- `PrismOverlays`
  - shared dialog, drawer, and overlay treatments
- `PrismHeroScene`
  - selective 3D landing-page scene only

These primitives live under `frontend/src/components/prism/`.

## 3D Policy

### Allowed

- Public landing hero
- Carefully scoped showcase moments where the performance cost is justified

### Default for the rest of the product

- layered gradients
- translucency
- light fields
- perspective
- motion and staggered reveal
- hover elevation

### Not allowed

- persistent full-screen WebGL in dense dashboards
- mandatory motion with no reduced-motion fallback
- product-critical information rendered only inside decorative 3D scenes

## Route Group Guidance

### Public routes

- `/`
  - flagship cinematic presentation
  - strongest depth and visual storytelling
- `/demo`
  - spatial role-selection experience
  - guided showcase framing
- `/login`
  - premium auth shell with operational clarity
- `/qr-login`
  - same shell language as login, simpler interaction flow

### Student routes

- emphasize learning momentum, AI surfaces, and progress
- strongest in-app depth treatment after the landing page

### Teacher routes

- professional, capable, and insight-led
- immersive framing around workflows, not decoration

### Admin routes

- controlled density and stronger hierarchy
- subtle immersion only; operations stay legible first

### Parent routes

- calmer and more reassuring
- progress storytelling over dense operations

## Local Design-Plugin Workflow

Use the local plugin repository:

- `C:\Users\naren\Work\Forks\design-plugin`

Workflow intent from the plugin:

1. generate multiple real-code variants
2. compare them in the design lab
3. synthesize the preferred direction
4. carry only the approved implementation back into this repo

The plugin is a design decision engine. It is not a production dependency.

Refinement decisions and accepted route-group directions should be logged in:

- `documentation/prism_plugin_refinement_log.md`

## Current Implementation Baseline

The Prism redesign currently establishes:

- a new global immersive theme in `globals.css`
- a shared ambient application backdrop
- upgraded shared shell elements such as sidebar, buttons, skeletons, empty states, dialogs, drawers, table shells, and form controls
- standardized page intros and section headers through shared Prism primitives
- redesigned public pages:
  - landing
  - demo
  - login
  - QR login
- redesigned student routes:
  - overview
  - AI Studio
  - assignments
  - results
  - mind map
  - tools
  - upload
  - reviews
- redesigned teacher routes:
  - dashboard
  - attendance
  - marks
  - assignments
  - generate assessment
  - insights
  - discover
  - upload
- redesigned admin routes:
  - dashboard
  - setup wizard
  - reports
  - queue
  - traces
  - security
  - branding
  - users
  - timetable
- redesigned parent routes:
  - dashboard
  - attendance
  - results
  - reports
  - assistant

Because the shell and tokens are shared, the rest of the product inherits the
new visual language even before route-specific deep refinements are applied.

## Next Refinement Passes

1. Plugin-guided refinement pass
   - generate and compare route-group variants through `C:\Users\naren\Work\Forks\design-plugin`
   - record accepted directions in `documentation/prism_plugin_refinement_log.md`
2. Responsive and motion QA
   - desktop/tablet/mobile validation
   - reduced-motion validation
   - no-WebGL fallback validation on selective 3D surfaces
3. Final evidence pass
   - keep lint, build, smoke, and representative visual coverage green

## Non-Negotiables

- `npm run lint` must pass
- `npm run build` must pass
- the redesign must preserve existing route and API behavior
- reduced-motion must remain functional
- the product should feel intentionally designed, not over-animated
