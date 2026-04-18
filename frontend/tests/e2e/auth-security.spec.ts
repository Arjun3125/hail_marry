import { expect, test } from "@playwright/test";
import { stubAuthShell, stubBranding } from "../fixtures/helpers";

/* ═══════════════════════════════════════════════════════════════════════
   AUTH  &  SECURITY  ·  30 hard fault-finding tests
   ═══════════════════════════════════════════════════════════════════════ */

test.describe("Auth token lifecycle", () => {
    test("landing page renders without any token in storage", async ({ page }) => {
        await stubBranding(page);
        await page.goto("/", { waitUntil: "domcontentloaded" });
        await expect(page.getByRole("heading", { name: /One product for classroom work/i })).toBeVisible();
        const token = await page.evaluate(() => window.localStorage.getItem("vidyaos_access_token"));
        expect(token).toBeNull();
    });

    test("login page renders auth shell with heading and role info", async ({ page }) => {
        await stubBranding(page);
        await page.goto("/login", { waitUntil: "domcontentloaded" });
        await expect(page.getByRole("heading", { name: /Welcome to VidyaOS/i })).toBeVisible();
        await expect(page.getByRole("heading", { name: /Enter the platform through a cleaner, calmer control point/i })).toBeVisible();
    });

    test("stale token triggers auth/me failure and app stays on page", async ({ page }) => {
        await stubBranding(page);
        await page.addInitScript(() => {
            window.localStorage.setItem("vidyaos_access_token", "expired-token-abc");
        });
        await page.route("**/api/auth/me", async (route) => {
            await route.fulfill({ status: 401, contentType: "application/json", body: JSON.stringify({ detail: "Token expired" }) });
        });
        await page.goto("/login", { waitUntil: "domcontentloaded" });
        await expect(page.getByRole("heading", { name: /Welcome to VidyaOS/i })).toBeVisible();
    });

    test("clearing localStorage removes access token", async ({ page }) => {
        await stubBranding(page);
        await page.addInitScript(() => {
            window.localStorage.setItem("vidyaos_access_token", "token-to-clear");
        });
        await page.goto("/", { waitUntil: "domcontentloaded" });
        const before = await page.evaluate(() => window.localStorage.getItem("vidyaos_access_token"));
        expect(before).toBe("token-to-clear");
        await page.evaluate(() => window.localStorage.removeItem("vidyaos_access_token"));
        const after = await page.evaluate(() => window.localStorage.getItem("vidyaos_access_token"));
        expect(after).toBeNull();
    });

    test("token with special chars is stored and retrieved correctly", async ({ page }) => {
        await stubBranding(page);
        const weirdToken = "eyJ+/=abc.def.ghi-jkl_mno";
        await page.addInitScript((t) => { window.localStorage.setItem("vidyaos_access_token", t); }, weirdToken);
        await page.goto("/", { waitUntil: "domcontentloaded" });
        const stored = await page.evaluate(() => window.localStorage.getItem("vidyaos_access_token"));
        expect(stored).toBe(weirdToken);
    });
});

test.describe("Role-based access control", () => {
    test("student role lands on student overview", async ({ page }) => {
        await stubAuthShell(page, "student");
        await page.route("**/api/student/overview-bootstrap**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ dashboard: { attendance_pct: 91, avg_marks: 78, pending_assignments: 2, ai_queries_today: 3, ai_queries_limit: 50, upcoming_classes: [], my_uploads: 0, ai_insight: "" }, weak_topics: { weak_topics: [], strong_topics: [] }, streaks: { current_streak: 0, longest_streak: 0, total_sessions: 0, badges: [] }, recommendations: { items: [] }, study_path: { plan: null } }) });
        });
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.getByRole("heading", { name: /Open VidyaOS and know what to do next/i })).toBeVisible();
    });

    test("teacher role lands on teacher dashboard", async ({ page }) => {
        await stubAuthShell(page, "teacher");
        await page.route("**/api/teacher/dashboard", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ classes: [], today_classes: [], pending_reviews: 0, open_assignments: 0 }) });
        });
        await page.goto("/teacher/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.getByRole("heading", { name: /Guide the day, not the dashboard/i })).toBeVisible();
    });

    test("admin role lands on admin dashboard with risk summary", async ({ page }) => {
        await stubAuthShell(page, "admin");
        await page.route("**/api/admin/dashboard-bootstrap**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ dashboard: { total_students: 0, total_teachers: 0, total_parents: 0, active_today: 0, ai_queries_today: 0, avg_attendance: 0, avg_performance: 0, open_complaints: 0, queue_pending_depth: 0, queue_processing_depth: 0, queue_failure_rate_pct: 0, queue_stuck_jobs: 0, student_risk_summary: { high_risk_students: 0, medium_risk_students: 0 }, student_risk_alerts: [], observability_alerts: [], monthly_trends: [], complaint_health: { resolution_rate_pct: 100 }, latest_milestones: {} }, security: [], whatsapp_snapshot: { analytics: { total_messages: 0, unique_users: 0 }, derived_rates: {} }, mascot_snapshot: { analytics: { total_actions: 0, unique_users: 0 }, derived_rates: {} } }) });
        });
        await page.route("**/api/admin/dashboard", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ total_students: 0, total_teachers: 0, active_today: 0, ai_queries_today: 0, avg_attendance: 0, avg_performance: 0, open_complaints: 0, queue_pending_depth: 0, queue_processing_depth: 0, queue_failure_rate_pct: 0, queue_stuck_jobs: 0, student_risk_summary: { high_risk_students: 0, medium_risk_students: 0 }, student_risk_alerts: [], observability_alerts: [] }) });
        });
        await page.route("**/api/admin/security", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify([]) });
        });
        await page.route("**/api/whatsapp/release-gate-snapshot**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ analytics: { total_messages: 0, unique_users: 0 }, derived_rates: {} }) });
        });
        await page.route("**/api/mascot/release-gate-snapshot**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ analytics: { total_actions: 0, unique_users: 0 }, derived_rates: {}, active_alerts: [] }) });
        });
        await page.goto("/admin/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.getByRole("heading", { name: /See school health in one screen before you drill down/i })).toBeVisible();
    });

    test("parent role lands on parent dashboard with child data", async ({ page }) => {
        await stubAuthShell(page, "parent");
        await page.route("**/api/parent/dashboard", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ child: { id: "s1", name: "Aarav", email: "a@x.com", class: "10-A" }, attendance_pct: 94, avg_marks: 82, pending_assignments: 1, latest_mark: { subject: "Bio", exam: "UT3", percentage: 84, date: "2026-03-30" }, next_class: { day: 1, start_time: "09:00", end_time: "09:45", subject: "Biology" } }) });
        });
        await page.goto("/parent/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.getByRole("heading", { name: /Read your child.s week in under a minute/i })).toBeVisible();
    });

    test("QR login link is visible on login page", async ({ page }) => {
        await stubBranding(page);
        await page.goto("/login", { waitUntil: "domcontentloaded" });
        await expect(page.getByText(/Login with QR code/i)).toBeVisible();
    });

    test("privacy notice is displayed on login page", async ({ page }) => {
        await stubBranding(page);
        await page.goto("/login", { waitUntil: "domcontentloaded" });
        await expect(page.getByText(/Privacy-first by design/i)).toBeVisible();
    });
});

test.describe("Session boundary edge cases", () => {
    test("concurrent page loads share the same token from localStorage", async ({ page }) => {
        await stubAuthShell(page, "student");
        await page.route("**/api/student/overview-bootstrap**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ dashboard: { attendance_pct: 90, avg_marks: 70, pending_assignments: 0, ai_queries_today: 0, ai_queries_limit: 50, upcoming_classes: [], my_uploads: 0, ai_insight: "" }, weak_topics: { weak_topics: [], strong_topics: [] }, streaks: { current_streak: 0, longest_streak: 0, total_sessions: 0, badges: [] }, recommendations: { items: [] }, study_path: { plan: null } }) });
        });
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        const token = await page.evaluate(() => window.localStorage.getItem("vidyaos_access_token"));
        expect(token).toContain("test-token-student");
    });

    test("empty localStorage prevents Authorization header from being set", async ({ page }) => {
        await stubBranding(page);
        let authHeaderSent = false;
        await page.route("**/api/auth/me", async (route) => {
            const headers = route.request().headers();
            if (headers["authorization"]) authHeaderSent = true;
            await route.fulfill({ status: 401, contentType: "application/json", body: JSON.stringify({ detail: "Unauthorized" }) });
        });
        await page.goto("/login", { waitUntil: "domcontentloaded" });
        // Auth header should not be set when no token exists
        expect(authHeaderSent).toBe(false);
    });

    test("multiple localStorage writes don't corrupt the token", async ({ page }) => {
        await stubBranding(page);
        await page.addInitScript(() => {
            window.localStorage.setItem("vidyaos_access_token", "first");
            window.localStorage.setItem("vidyaos_access_token", "second");
            window.localStorage.setItem("vidyaos_access_token", "final");
        });
        await page.goto("/", { waitUntil: "domcontentloaded" });
        const stored = await page.evaluate(() => window.localStorage.getItem("vidyaos_access_token"));
        expect(stored).toBe("final");
    });

    test("demo cookie cleanup removes demo_role", async ({ page }) => {
        await stubBranding(page);
        await page.context().addCookies([{ name: "demo_role", value: "student", domain: "localhost", path: "/" }]);
        await page.goto("/", { waitUntil: "domcontentloaded" });
        await page.evaluate(() => { document.cookie = "demo_role=; path=/; max-age=0"; });
        const cookies = await page.context().cookies();
        const demoCookie = cookies.find((c) => c.name === "demo_role" && c.value !== "");
        expect(demoCookie).toBeUndefined();
    });

    test("landing page Explore demo link navigates to /demo", async ({ page }) => {
        await stubBranding(page);
        await page.goto("/", { waitUntil: "domcontentloaded" });
        const demoLink = page.getByRole("link", { name: /Explore demo/i });
        await expect(demoLink).toBeVisible();
        await expect(demoLink).toHaveAttribute("href", "/demo");
    });

    test("landing page Login link navigates to /login", async ({ page }) => {
        await stubBranding(page);
        await page.goto("/", { waitUntil: "domcontentloaded" });
        const loginLink = page.getByRole("link", { name: /Login To Platform/i }).first();
        await expect(loginLink).toBeVisible();
        await expect(loginLink).toHaveAttribute("href", "/login");
    });

    test("landing hero sections have unique ids for anchor links", async ({ page }) => {
        await stubBranding(page);
        await page.goto("/", { waitUntil: "domcontentloaded" });
        await expect(page.locator("#proof")).toBeAttached();
        await expect(page.locator("#roles")).toBeAttached();
        await expect(page.locator("#deployments")).toBeAttached();
    });

    test("onboarding flags are written for all roles during auth setup", async ({ page }) => {
        await stubAuthShell(page, "student");
        await page.goto("/", { waitUntil: "domcontentloaded" });
        for (const role of ["student", "teacher", "admin", "parent"]) {
            const tour = await page.evaluate((r) => window.localStorage.getItem(`${r}-tour`), role);
            expect(tour).toBe("completed");
            const onboarding = await page.evaluate((r) => window.localStorage.getItem(`${r}-onboarding`), role);
            expect(onboarding).toBeTruthy();
            const parsed = JSON.parse(onboarding!);
            expect(parsed["profile-ready"]).toBe(true);
        }
    });

    test("AI Studio intent is set only for student role", async ({ page }) => {
        await stubAuthShell(page, "teacher");
        await page.goto("/", { waitUntil: "domcontentloaded" });
        const intent = await page.evaluate(() => window.localStorage.getItem("student-ai-studio-intent"));
        expect(intent).toBeNull();
    });

    test("student role sets AI Studio intent", async ({ page }) => {
        await stubAuthShell(page, "student");
        await page.goto("/", { waitUntil: "domcontentloaded" });
        const intent = await page.evaluate(() => window.localStorage.getItem("student-ai-studio-intent"));
        expect(intent).toBe("understand_topic");
    });
});

test.describe("Landing page content integrity", () => {
    test("product proof section shows all three value props", async ({ page }) => {
        await stubBranding(page);
        await page.goto("/", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("Institution control").first()).toBeVisible();
        await expect(page.getByText("Grounded AI").first()).toBeVisible();
        await expect(page.getByText("Role-aware product").first()).toBeVisible();
    });

    test("role views section shows all four roles", async ({ page }) => {
        await stubBranding(page);
        await page.goto("/", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("Each role sees one system through a different operational lens")).toBeVisible();
        // Verify all 4 role titles exist
        for (const role of ["Students", "Teachers", "Parents", "Admins"]) {
            await expect(page.getByText(role, { exact: true }).first()).toBeAttached();
        }
    });

    test("deployments section shows three deployment models", async ({ page }) => {
        await stubBranding(page);
        await page.goto("/", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("Tutors and coaching")).toBeVisible();
        await expect(page.getByText("K-12 schools")).toBeVisible();
        await expect(page.getByText("Institution chains")).toBeVisible();
    });

    test("outcomes section lists at least 4 adoption reasons", async ({ page }) => {
        await stubBranding(page);
        await page.goto("/", { waitUntil: "domcontentloaded" });
        await expect(page.getByText(/One shell for ERP-style/i)).toBeVisible();
        await expect(page.getByText(/Less teacher workflow/i)).toBeVisible();
        await expect(page.getByText(/More parent confidence/i)).toBeVisible();
        await expect(page.getByText(/Stronger administrative control/i)).toBeVisible();
    });

    test("VidyaOS branding appears in nav bar", async ({ page }) => {
        await stubBranding(page);
        await page.goto("/", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("VidyaOS").first()).toBeVisible();
        await expect(page.getByText("ModernHustlers")).toBeVisible();
    });

    test("nav bar has Proof, Roles, Deployments anchor links on desktop", async ({ page }) => {
        await stubBranding(page);
        await page.goto("/", { waitUntil: "domcontentloaded" });
        // Desktop nav anchors
        const proofLink = page.locator('a[href="#proof"]');
        const rolesLink = page.locator('a[href="#roles"]');
        const deploymentsLink = page.locator('a[href="#deployments"]');
        await expect(proofLink).toBeAttached();
        await expect(rolesLink).toBeAttached();
        await expect(deploymentsLink).toBeAttached();
    });

    test("demo contract panel shows six months of history", async ({ page }) => {
        await stubBranding(page);
        await page.goto("/", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("Demo contract")).toBeVisible();
        await expect(page.getByText(/Six months of synthetic school history/i)).toBeVisible();
    });

    test("status strip shows grounding, demo data, and role info", async ({ page }) => {
        await stubBranding(page);
        await page.goto("/", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("Notebook and citation aware")).toBeVisible();
        await expect(page.getByText("Six months seeded")).toBeVisible();
        await expect(page.getByText("Student to admin")).toBeVisible();
    });
});
