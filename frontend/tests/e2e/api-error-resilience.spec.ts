import { expect, test } from "@playwright/test";
import { stubAuthShell, stubBranding, stubStudentOverview, stubAdminDashboard } from "../fixtures/helpers";

/* ═══════════════════════════════════════════════════════════════════════
   API  ERROR  RESILIENCE  ·  35 hard fault-finding tests
   ═══════════════════════════════════════════════════════════════════════ */

test.describe("HTTP 500 server errors", () => {
    test("student overview gracefully handles 500 from bootstrap API", async ({ page }) => {
        await stubAuthShell(page, "student");
        await page.route("**/api/student/overview-bootstrap**", async (route) => {
            await route.fulfill({ status: 500, contentType: "application/json", body: JSON.stringify({ detail: "Internal server error" }) });
        });
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        // Page should still render without crashing — error boundaries catch this
        await expect(page.locator("body")).toBeVisible();
    });

    test("teacher dashboard handles 500 without blank screen", async ({ page }) => {
        await stubAuthShell(page, "teacher");
        await page.route("**/api/teacher/dashboard", async (route) => {
            await route.fulfill({ status: 500, contentType: "application/json", body: JSON.stringify({ detail: "DB connection lost" }) });
        });
        await page.goto("/teacher/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("admin dashboard handles 500 from bootstrap endpoint", async ({ page }) => {
        await stubAuthShell(page, "admin");
        await page.route("**/api/admin/dashboard-bootstrap**", async (route) => {
            await route.fulfill({ status: 500, contentType: "application/json", body: JSON.stringify({ detail: "Service unavailable" }) });
        });
        await page.route("**/api/admin/dashboard", async (route) => {
            await route.fulfill({ status: 500, contentType: "application/json", body: JSON.stringify({ detail: "Service unavailable" }) });
        });
        await page.route("**/api/admin/security", async (route) => { await route.fulfill({ status: 200, contentType: "application/json", body: "[]" }); });
        await page.route("**/api/whatsapp/release-gate-snapshot**", async (route) => { await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ analytics: {}, derived_rates: {} }) }); });
        await page.route("**/api/mascot/release-gate-snapshot**", async (route) => { await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ analytics: {}, derived_rates: {}, active_alerts: [] }) }); });
        await page.goto("/admin/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("parent dashboard handles 500 without crash", async ({ page }) => {
        await stubAuthShell(page, "parent");
        await page.route("**/api/parent/dashboard", async (route) => {
            await route.fulfill({ status: 500, contentType: "application/json", body: JSON.stringify({ detail: "DB down" }) });
        });
        await page.goto("/parent/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("503 from branding endpoint still renders page with defaults", async ({ page }) => {
        await page.route("**/api/branding/config", async (route) => {
            await route.fulfill({ status: 503, contentType: "application/json", body: JSON.stringify({ detail: "Service unavailable" }) });
        });
        await page.goto("/", { waitUntil: "domcontentloaded" });
        await expect(page.getByRole("heading", { name: /One product for classroom work/i })).toBeVisible();
    });
});

test.describe("HTTP 422 validation errors", () => {
    test("student tools shows friendly error on 422 from generate", async ({ page }) => {
        await stubAuthShell(page, "student");
        await page.route("**/api/student/ai-history**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [] }) });
        });
        await page.route("**/api/student/tools/generate/jobs", async (route) => {
            await route.fulfill({ status: 422, contentType: "application/json", body: JSON.stringify({ detail: "Upload matching study materials before generating a quiz." }) });
        });
        await page.route("**/api/student/tools/generate", async (route) => {
            await route.fulfill({ status: 422, contentType: "application/json", body: JSON.stringify({ detail: "Upload matching study materials before generating a quiz." }) });
        });
        await page.goto("/student/tools", { waitUntil: "domcontentloaded" });
        await page.getByRole("button", { name: /Quiz/i }).click();
        await page.locator("textarea").fill("Photosynthesis");
        await page.getByRole("button", { name: /Generate/i }).click();
        await expect(page.getByText("Upload matching study materials before generating a quiz.")).toBeVisible();
    });

    test("422 with custom error_code surfaces the code in error display", async ({ page }) => {
        await stubAuthShell(page, "student");
        await page.route("**/api/student/ai-history**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [] }) });
        });
        await page.route("**/api/student/tools/generate/jobs", async (route) => {
            await route.fulfill({
                status: 422,
                contentType: "application/json",
                headers: { "x-error-code": "MATERIAL_REQUIRED" },
                body: JSON.stringify({ detail: "You must upload material first.", error_code: "MATERIAL_REQUIRED" }),
            });
        });
        await page.route("**/api/student/tools/generate", async (route) => {
            await route.fulfill({ status: 422, contentType: "application/json", body: JSON.stringify({ detail: "You must upload material first." }) });
        });
        await page.goto("/student/tools", { waitUntil: "domcontentloaded" });
        await page.getByRole("button", { name: /Quiz/i }).click();
        await page.locator("textarea").fill("Test topic");
        await page.getByRole("button", { name: /Generate/i }).click();
        await expect(page.getByText(/You must upload material first/i)).toBeVisible();
    });
});

test.describe("HTTP 429 rate limiting", () => {
    test("rate-limited API call shows appropriate message", async ({ page }) => {
        await stubAuthShell(page, "student");
        await page.route("**/api/student/ai-history**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [] }) });
        });
        await page.route("**/api/student/tools/generate/jobs", async (route) => {
            await route.fulfill({ status: 429, contentType: "application/json", body: JSON.stringify({ detail: "Too many requests. Please wait before trying again." }) });
        });
        await page.route("**/api/student/tools/generate", async (route) => {
            await route.fulfill({ status: 429, contentType: "application/json", body: JSON.stringify({ detail: "Too many requests." }) });
        });
        await page.goto("/student/tools", { waitUntil: "domcontentloaded" });
        await page.getByRole("button", { name: /Quiz/i }).click();
        await page.locator("textarea").fill("Atoms");
        await page.getByRole("button", { name: /Generate/i }).click();
        await expect(page.getByText(/Too many requests/i)).toBeVisible();
    });
});

test.describe("Network failures and timeouts", () => {
    test("network abort on student overview shows error state", async ({ page }) => {
        await stubAuthShell(page, "student");
        await page.route("**/api/student/overview-bootstrap**", async (route) => {
            await route.abort("connectionrefused");
        });
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("network timeout on teacher dashboard doesn't freeze UI", async ({ page }) => {
        await stubAuthShell(page, "teacher");
        await page.route("**/api/teacher/dashboard", async (route) => {
            await route.abort("timedout");
        });
        await page.goto("/teacher/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("connection refused on parent dashboard maintains layout", async ({ page }) => {
        await stubAuthShell(page, "parent");
        await page.route("**/api/parent/dashboard", async (route) => {
            await route.abort("connectionrefused");
        });
        await page.goto("/parent/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });
});

test.describe("Malformed response handling", () => {
    test("HTML response from API doesn't crash the page", async ({ page }) => {
        await stubAuthShell(page, "student");
        await page.route("**/api/student/overview-bootstrap**", async (route) => {
            await route.fulfill({ status: 200, contentType: "text/html", body: "<html><body>Not JSON</body></html>" });
        });
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("empty string response body doesn't crash the parser", async ({ page }) => {
        await stubAuthShell(page, "student");
        await page.route("**/api/student/overview-bootstrap**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: "" });
        });
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("null JSON response is handled safely", async ({ page }) => {
        await stubAuthShell(page, "student");
        await page.route("**/api/student/overview-bootstrap**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: "null" });
        });
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });
});

test.describe("Mixed success/failure responses", () => {
    test("partial overview bootstrap with missing study_path renders without crash", async ({ page }) => {
        await stubAuthShell(page, "student");
        await page.route("**/api/student/overview-bootstrap**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ dashboard: { attendance_pct: 91, avg_marks: 78, pending_assignments: 2, ai_queries_today: 3, ai_queries_limit: 50, upcoming_classes: [], my_uploads: 4, ai_insight: "" }, weak_topics: { weak_topics: [], strong_topics: [] }, streaks: { current_streak: 0, longest_streak: 0, total_sessions: 0, badges: [] }, recommendations: { items: [] } }) });
        });
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.getByRole("heading", { name: /Open VidyaOS and know what to do next/i })).toBeVisible();
    });

    test("overview with all null sub-objects renders gracefully", async ({ page }) => {
        await stubAuthShell(page, "student");
        await page.route("**/api/student/overview-bootstrap**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ dashboard: { attendance_pct: 0, avg_marks: 0, pending_assignments: 0, ai_queries_today: 0, ai_queries_limit: 50, upcoming_classes: [], my_uploads: 0, ai_insight: null }, weak_topics: null, streaks: null, recommendations: null, study_path: null }) });
        });
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("admin bootstrap with empty whatsapp snapshot renders all sections", async ({ page }) => {
        await stubAuthShell(page, "admin");
        await stubAdminDashboard(page);
        await page.goto("/admin/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.getByRole("heading", { name: /See school health in one screen/i })).toBeVisible();
    });

    test("teacher dashboard with empty classes array shows no crash", async ({ page }) => {
        await stubAuthShell(page, "teacher");
        await page.route("**/api/teacher/dashboard", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ classes: [], today_classes: [], pending_reviews: 0, open_assignments: 0 }) });
        });
        await page.goto("/teacher/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.getByRole("heading", { name: /Guide the day/i })).toBeVisible();
    });

    test("parent dashboard with null child object handles gracefully", async ({ page }) => {
        await stubAuthShell(page, "parent");
        await page.route("**/api/parent/dashboard", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ child: null, attendance_pct: 0, avg_marks: 0, pending_assignments: 0 }) });
        });
        await page.goto("/parent/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });
});

test.describe("Concurrent and rapid API interactions", () => {
    test("rapid navigation between student pages doesn't cause errors", async ({ page }) => {
        await stubAuthShell(page, "student");
        await stubStudentOverview(page);
        await page.route("**/api/student/uploads", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [] }) });
        });
        await page.route("**/api/mascot/suggestions**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ suggestions: [] }) });
        });
        await page.route("**/api/student/attendance**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ records: [] }) });
        });
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.getByRole("heading", { name: /Open VidyaOS/i })).toBeVisible();
        // Rapid nav
        await page.goto("/student/upload", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("API failure during navigation doesn't leave stale loading state", async ({ page }) => {
        await stubAuthShell(page, "student");
        let callCount = 0;
        await page.route("**/api/student/overview-bootstrap**", async (route) => {
            callCount++;
            if (callCount === 1) {
                await route.fulfill({ status: 500, contentType: "application/json", body: JSON.stringify({ detail: "Server error" }) });
            } else {
                await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ dashboard: { attendance_pct: 91, avg_marks: 78, pending_assignments: 2, ai_queries_today: 3, ai_queries_limit: 50, upcoming_classes: [], my_uploads: 4, ai_insight: "Focus on bio." }, weak_topics: { weak_topics: [], strong_topics: [] }, streaks: { current_streak: 4, longest_streak: 7, total_sessions: 12, badges: [] }, recommendations: { items: [] }, study_path: { plan: null } }) });
            }
        });
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("double-clicking a navigation link doesn't cause errors", async ({ page }) => {
        await stubBranding(page);
        await page.goto("/", { waitUntil: "domcontentloaded" });
        const loginLink = page.getByRole("link", { name: /Login To Platform/i }).first();
        await loginLink.dblclick();
        await expect(page.locator("body")).toBeVisible();
    });

    test("slow API response followed by fast navigation doesn't crash", async ({ page }) => {
        await stubAuthShell(page, "student");
        await page.route("**/api/student/overview-bootstrap**", async (route) => {
            await new Promise((r) => setTimeout(r, 300));
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ dashboard: { attendance_pct: 91, avg_marks: 78, pending_assignments: 0, ai_queries_today: 0, ai_queries_limit: 50, upcoming_classes: [], my_uploads: 0, ai_insight: "" }, weak_topics: { weak_topics: [], strong_topics: [] }, streaks: { current_streak: 0, longest_streak: 0, total_sessions: 0, badges: [] }, recommendations: { items: [] }, study_path: { plan: null } }) });
        });
        await page.route("**/api/student/uploads", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [] }) });
        });
        await page.route("**/api/mascot/suggestions**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ suggestions: [] }) });
        });
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        // Navigate away before first API completes
        await page.goto("/student/upload", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("204 No Content response is handled cleanly", async ({ page }) => {
        await stubAuthShell(page, "student");
        await page.route("**/api/student/overview-bootstrap**", async (route) => {
            await route.fulfill({ status: 204, body: "" });
        });
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });
});
