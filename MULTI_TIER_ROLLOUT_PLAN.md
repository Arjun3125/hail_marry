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

The database and core logic (`middleware/tenant.py`) already support complete tenant isolation. To support **Tier 2** and **Tier 3** white-labeling gracefully, only two minor architectural changes are required:

### A. The "Domain Resolver" Endpoint (Backend)
*   **Task:** Create an unauthenticated API endpoint: `GET /api/public/tenant-branding?domain={hostname}`.
*   **Purpose:** The frontend must ask the DB which school owns a particular domain *before* the user has logged in, so it can brand the login screen accurately.

### B. The Hostname Middleware (Frontend)
*   **Task:** Update `middleware.ts` (Next.js) or the `login/page.tsx` layout.
*   **Purpose:** Read the browser's URL (`req.headers.host`). If it is a custom domain, fetch the branding metadata from the new backend endpoint securely and inject it into the UI context before rendering the login form.

---

## 5. Conclusion

By maintaining a **Single Unified Codebase**, you eliminate the nightmare of releasing updates to 150 separate school applications. When you fix a bug in the AI RAG engine or update an attendance chart, all three tiers and all ~116,000 students receive the benefit instantly.
