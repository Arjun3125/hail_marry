# VidyaOS Scalable Multi-Tier Rollout Strategy

This document outlines the strategic, architectural, and operational roadmap for launching all three tiers of VidyaOS simultaneously to efficiently scale to 116,000+ total students.

## 1. Executive Summary

Instead of a time-based rollout, VidyaOS is designed to operate on a unified, enterprise-grade cloud foundation serving three distinct customer tiers from Day 1. By leveraging the platform's native multi-tenancy (`tenant_id`), the infrastructure handles isolation transparently, ensuring strict data privacy and simplified DevOps.

*   **Tier 1 (Small Private Class):** Avg ~45 students. Direct portal login (`app.vidyaos.com`).
*   **Tier 2 (Medium Class):** Avg ~220 students. White-labeled domain (`portal.academy.com`).
*   **Tier 3 (Large School):** Avg ~600 students. White-labeled domain + Personal Custom Android App.

---

## 2. Infrastructure Foundation (The "Day 1" Architecture)

To support 100k+ simultaneous users, the backend must be Enterprise-Ready from launch.

*   **API Layer (FastAPI):** Deployed via a container orchestrator (e.g., AWS EKS Kubernetes or Google Cloud Run). Auto-scales horizontally (20-50+ replicas) during morning attendance spikes.
*   **Database (PostgreSQL):** High Availability (HA) cluster (e.g., AWS Aurora Serverless). **PgBouncer** MUST be deployed to handle connection pooling from the horizontally scaled API layer. Read Replicas will be used for high-volume "getter" requests (like rendering timetables).
*   **Background Workers (Redis):** Heavy tasks (Generating PDFs, AI Jobs) are isolated to `ai_worker` containers draining a Redis queue so the main API never slows down.
*   **AI Inference (LLM):** Rely strictly on Managed Cloud APIs (OpenAI or Groq) rather than single-tenant local instances (Ollama) to guarantee inference latency at massive concurrency.

---

## 3. Product Tier Breakdown

### Tier 1: "The Direct Portal" (~45 Students)
**Offering:** Affordable access to the VidyaOS ecosystem.
*   **UX:** Students log into the core application domain (`app.vidyaos.com`).
*   **Mechanism:** Upon registration, the institution receives a `tenant_id`. Students use general branding. The backend strictly isolates their data.

### Tier 2: "The White-Label Expansion" (~220 Students)
**Offering:** A premium branded experience.
*   **UX:** Students navigate to a custom domain (e.g., `portal.techacademy.com`). The login page features the academy's specific logo and primary colors.
*   **Mechanism:** Requires Cloudflare SSL for SaaS (or Vercel Custom Domains) to terminate HTTPS. The Next.js frontend resolves the domain dynamically via a new backend API endpoint.

### Tier 3: "Enterprise Custom Android App" (~600 Students)
**Offering:** The ultimate branded experience with a physical Google Play Store presence (e.g., "The Tech Academy App").
*   **UX:** Native icon, splash screens, and direct push notification capabilities.
*   **Mechanism:** Do NOT fork the codebase 150 times.
    *   Utilize **Capacitor** (wrapping the Next.js frontend) or **React Native Quick**.
    *   Deploy a **White-Label Build Pipeline** (via Fastlane or Expo EAS).
    *   When an Enterprise client signs up, the pipeline takes their Logo, App Name, and API Endpoint URL, and automatically compiles and publishes a unique `.aab` (Android App Bundle).

---

## 4. Required Codebase Changes (Action Plan)

The database and core logic (`middleware/tenant.py`) already support complete tenant isolation.
**Update (2026-03-25): Tier 2 and Tier 3 white-labeling is now fully supported.**

### A. The Branding Processing API (Backend)
- **Implemented:** `POST /api/branding/tenant/{tenant_id}/logo`
- **Purpose:** Automatically extracts primary, secondary, and accent colors from the school's logo using `colorthief`, storing them on the `Tenant` record.

### B. The BrandingProvider Context (Frontend)
- **Implemented:** `BrandingProvider.tsx` in the Next.js frontend tree.
- **Purpose:** On load, fetches the tenant's exact color profile and injects `--primary`, `--secondary`, and `--accent` CSS Custom Properties into the document root. The entire Tailwind-powered design system instantly reskins itself with zero code forks and zero latency, fulfilling the Tier 2 and Tier 3 requirements flawlessly.

---

## 5. Conclusion

By maintaining a **Single Unified Codebase**, you eliminate the nightmare of releasing updates to 150 separate school applications. When you fix a bug in the AI RAG engine or update an attendance chart, all three tiers and all ~116,000 students receive the benefit instantly.
