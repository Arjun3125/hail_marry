# VidyaOS — Product Rating, Pricing & UX Strategy

## Product Rating: 7.5 / 10

## Current Status Notes (2026-03-25)

Several advanced AI items remain partial:
- AI grading currently returns OCR extraction + manual review; full rubric scoring is pending.
- Extended connectors (PPTX/XLSX uploads + Google Docs/Notion URL ingestion) are wired when API tokens are configured.

Recent UX upgrades now implemented:
- Role-specific landing dashboards for parent, student, and teacher.
- QR code student login with printable cards.
- Constraint-based timetable generator in admin timetable management.
- Android Play Store shell guide (TWA/Capacitor) with assetlinks template.
- Feature Management System with AI intensity classification and system profiles.
- White-Label Branding Engine with colorthief logo color extraction.

These caveats should be applied when interpreting the ratings below.

### Strengths (what sells)
| Area | Rating | Why |
|------|--------|-----|
| **Feature depth** | 9/10 | 61 features across 4 roles — comprehensive school ERP + AI platform + feature management + branding |
| **AI integration** | 8/10 | Grounded Q&A and study tools are implemented; citations and docs chatbot are wired; connectors are wired when tokens are configured |
| **Architecture** | 9/10 | Multi-tenant, role-based, plugin architecture, OpenAI-compat API, structured logging, telemetry |
| **Security** | 8/10 | CSRF, rate limiting, tenant isolation, JWT, RBAC, DPDP compliance; reCAPTCHA + refresh token blacklist enforced when configured |
| **Test coverage** | 9/10 | 382 tests across 48 files covering auth, RBAC, fees, library, AI, connectors, plugins, and more |

### Weaknesses (what needs work before scaling)
| Area | Rating | Gap |
|------|--------|-----|
| **Onboarding UX** | 7/10 | Self-service tenant onboarding + admission workflow implemented; setup wizard UI still needed |
| **Mobile experience** | 5/10 | Responsive but not mobile-optimized — no native-like interactions |
| **Localization** | 7/10 | Hindi + Marathi i18n implemented with locale files and API endpoints |
| **Parent simplicity** | 7/10 | WhatsApp notifications + weekly digests + parent portal; web UI could be simpler |
| **Admin setup complexity** | 6/10 | Self-service onboarding automates base setup; guided wizard still needed for fine-tuning |

---

## Pricing Strategy for 500-Student School

### Recommended Model: Per-Student/Year + One-Time Onboarding

| Component | Price | Revenue (500 students) |
|-----------|-------|------------------------|
| **Onboarding fee** (one-time) | ₹50,000 – ₹1,00,000 | ₹50K – ₹1L |
| **Per student/year** | ₹600 – ₹1,200/yr (₹50-100/month) | ₹3L – ₹6L/yr |
| **Total Year 1** | — | **₹3.5L – ₹7L** |
| **Total Year 2+** (no onboarding) | — | **₹3L – ₹6L/yr** |

### Tier Breakdown

| Tier | Per Student/Yr | What's Included |
|------|---------------|-----------------|
| **Basic** (₹600/yr) | ERP only: attendance, marks, timetable, assignments, parent dashboard, library | No AI features |
| **Standard** (₹900/yr) | Basic + AI study tools, spaced repetition, gamification, weakness alerts, fee management | Core AI |
| **Premium** (₹1,200/yr) | Standard + AI grading co-pilot, doubt heatmaps, YouTube ingestion, agent orchestration, priority support | Full AI |

### Onboarding Fee Justification
- Data migration from existing systems (Excel sheets, paper records)
- Initial teacher training (2-3 sessions)
- Class/subject/timetable setup
- First batch of student account creation
- Custom branding (logo, school name)

### Competitive Benchmark
| Competitor | Per Student/Yr | Notes |
|-----------|---------------|-------|
| Teachmint | ₹500-800 | Strong mobile, limited AI |
| iitms (MasterSoft) | ₹800-1,500 | Legacy ERP, no AI |
| Classplus | ₹300-600 | Focused on tuition, no ERP |
| **VidyaOS** | ₹600-1,200 | **Full ERP + genuine AI — unique positioning** |

> **Key selling point:** Schools currently pay separately for ERP (₹500+), LMS (₹300+), and often misuse ChatGPT (risk). VidyaOS replaces all three at a combined lower cost with curriculum-grounded AI.

---

## Making Onboarding & Usage More Convenient

### 🔴 Critical (implement before first school sale)

#### 1. Setup Wizard (First-Time Admin Experience) ✅ IMPLEMENTED
**Status:** `app/admin/setup-wizard/page.tsx` — Step-by-step wizard for new tenant setup including class generation and teacher/student bulk imports.

#### 2. One-Click CSV Templates ✅ IMPLEMENTED
**Status:** Integrated directly into the Setup Wizard component (`app/admin/setup-wizard/page.tsx` and `backend/routes/admin.py`) allowing quick template downloads.

#### 3. WhatsApp Integration for Parents ✅ IMPLEMENTED
**Status:** `services/whatsapp.py` with attendance alerts, weekly digests, and exam result notifications with emoji. 12 tests.

---

### 🟡 Important (implement in first 3 months)

#### 4. Role-Specific Landing Dashboard ✅ IMPLEMENTED
**Problem:** All roles see the same initial UI structure— overwhelming for parents and students.

**Solution:**
- **Parent:** Single card showing child's attendance %, latest marks, next class. Big "Listen to Report" button.
- **Student:** Streak counter front-and-center, "Continue Studying" quick-action, badge showcase.
- **Teacher:** "Today's Classes" at top, quick-mark attendance button, pending assignment count.

**Status:** Updated in `app/parent/dashboard/page.tsx`, `app/student/overview/page.tsx`, and `app/teacher/dashboard/page.tsx`.

#### 5. Hindi & Regional Language Support ✅ IMPLEMENTED
**Status:** `locales/{en,hi,mr}.json` + `services/i18n.py` + `routes/i18n.py`. English, Hindi, and Marathi translations with API endpoints for fetching translations and listing locales. 14 tests.

#### 6. QR Code Student Login ✅ IMPLEMENTED
**Problem:** Young students (Class 1-5) can't remember email/password.

**Solution:** Admin prints QR code cards for each student. Student scans QR → auto-login. Works via unique one-time tokens.

**Status:** `admin/qr-cards` UI, `/api/admin/generate-qr-tokens`, and `/api/auth/qr` endpoints.

#### 7. Demo Mode Enhancement ✅ IMPLEMENTED
**Status:** `components/GuidedTour.tsx` — Walkthrough tour for the demo mode showcasing the AI assistant, dashboards, and features.

---

### 🟢 Nice-to-Have (months 3-6)

#### 8. Mobile App Shell (Capacitor/TWA) ✅ IMPLEMENTED (Guide)
Wrap the PWA in a native Android shell for Play Store distribution. Indian schools trust "apps" more than "websites."

**Status:** `documentation/system_docs/Android shell.md` with TWA/Capacitor instructions + assetlinks template.

#### 9. Automated Report Cards ✅ IMPLEMENTED
**Status:** `services/report_card.py` — One-click PDF report card generation with school letterhead, attendance, marks per subject, computed grades, and configurable school colors. 3 tests.

#### 10. Smart Timetable Generator ✅ IMPLEMENTED
Instead of manual slot-by-slot entry, input constraints (teacher availability, subject hours/week) and auto-generate optimal timetable.

**Status:** `services/timetable_generator.py` + `app/admin/timetable/page.tsx` auto-generate panel.

---

## Priority Roadmap

| 🔴 P0 | Setup Wizard | ✅ Done | Reduces onboarding from hours to 15 mins |
| 🔴 P0 | CSV Templates with download | ✅ Done | Eliminates "what format?" support queries |
| 🔴 P0 | WhatsApp digest (API) | ✅ Done | 80% of parents won't need to login ever |
| 🟡 P1 | Role-specific dashboards | ✅ Done | Dramatically simpler first impression |
| 🟡 P1 | Hindi translations | ✅ Done | Opens rural market segment |
| 🟡 P1 | QR code student login | ✅ Done | Solves primary school adoption |
| 🟡 P1 | Guided demo tour | ✅ Done | Self-service sales demo |
| 🟢 P2 | Android Play Store shell | ✅ Done | Trust + distribution |
| 🟢 P2 | Automated report cards | ✅ Done | High-value for parent meetings |
| 🟢 P2 | Smart timetable generator | ✅ Done | Admin time-saver |
