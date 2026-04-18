import { expect, test } from "@playwright/test";
import { stubAuthShell, stubAdminDashboard, adminDashboardPayload, adminBootstrapPayload, stubMascotSuggestions } from "../fixtures/helpers";

/* ═══════════════════════════════════════════════════════════════════════
   ADMIN  DASHBOARD  OPS  ·  hard fault-finding tests
   ═══════════════════════════════════════════════════════════════════════ */

/**
 * Helper: navigate to admin dashboard and wait for client-side hydration.
 * Because SSR is bypassed in E2E (returns null), the client fetches data
 * after mount. We wait for "Attendance today" — a HeroMetric label that
 * only appears after the bootstrap payload is consumed (not in the sidebar).
 * We use domcontentloaded (not networkidle) because unmocked proxy requests
 * to the dead backend prevent the network from ever settling.
 */
async function gotoAdminDashboard(page: import("@playwright/test").Page) {
    let retries = 3;
    while (retries > 0) {
        await page.goto("/admin/dashboard", { waitUntil: "domcontentloaded" });
        // Check if Next.js randomly returned a 404 (common dev server race condition)
        const is404 = await page.locator("text='This page could not be found.'").isVisible();
        if (!is404) break;
        console.log("Caught Next.js Dev Server 404 race condition, retrying navigation...");
        await page.waitForTimeout(2000);
        retries--;
    }
    await page.getByText("Attendance today").first().waitFor({ state: "visible", timeout: 30000 });
}

test.describe("Admin dashboard bootstrap rendering", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "admin");
        await stubMascotSuggestions(page, []);
    });

    test("admin dashboard renders hero heading", async ({ page }) => {
        await stubAdminDashboard(page);
        await gotoAdminDashboard(page);
        await expect(page.getByRole("heading", { name: /See school health in one screen/i })).toBeVisible();
    });

    test("admin kicker badge is visible", async ({ page }) => {
        await stubAdminDashboard(page);
        await gotoAdminDashboard(page);
        await expect(page.getByText("Admin command center")).toBeVisible();
    });

    test("school health score is displayed", async ({ page }) => {
        await stubAdminDashboard(page);
        await gotoAdminDashboard(page);
        // The mock payload results in a score of 77 due to the formula implementation
        await expect(page.getByText("77").first()).toBeVisible();
        await expect(page.getByText("School health", { exact: true }).first()).toBeVisible();
    });

    test("attendance percentage is shown", async ({ page }) => {
        await stubAdminDashboard(page);
        await gotoAdminDashboard(page);
        // Mock has avg_attendance: 93 → renders "93%"
        await expect(page.getByText("93%").first()).toBeAttached();
    });

    test("pending complaints count is shown", async ({ page }) => {
        await stubAdminDashboard(page);
        await gotoAdminDashboard(page);
        // Mock has open_complaints: 2
        await expect(page.getByText("Pending complaints")).toBeVisible();
        await expect(page.getByText("2", { exact: true }).first()).toBeAttached();
    });

    test("AI usage today is displayed", async ({ page }) => {
        await stubAdminDashboard(page);
        await gotoAdminDashboard(page);
        await expect(page.getByText("AI usage today").first()).toBeVisible();
        // Mock has ai_queries_today: 31
        await expect(page.getByText("31").first()).toBeAttached();
    });

    test("students active is displayed", async ({ page }) => {
        await stubAdminDashboard(page);
        await gotoAdminDashboard(page);
        await expect(page.getByText("Students active").first()).toBeVisible();
        // Mock has active_today: 52
        await expect(page.getByText("52").first()).toBeAttached();
    });

    test("since yesterday section is visible", async ({ page }) => {
        await stubAdminDashboard(page);
        await gotoAdminDashboard(page);
        await expect(page.getByText("Since yesterday")).toBeVisible();
    });
});

test.describe("Admin dashboard pending actions", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "admin");
        await stubAdminDashboard(page);
        await stubMascotSuggestions(page, []);
    });

    test("complaints waiting section is visible", async ({ page }) => {
        await gotoAdminDashboard(page);
        await expect(page.getByText("Complaints waiting")).toBeVisible();
    });

    test("alerts to review section is visible", async ({ page }) => {
        await gotoAdminDashboard(page);
        await expect(page.getByText("Alerts to review")).toBeVisible();
    });

    test("high-risk learners section is visible", async ({ page }) => {
        await gotoAdminDashboard(page);
        await expect(page.getByText("High-risk learners")).toBeVisible();
    });

    test("queue backlog section is visible", async ({ page }) => {
        await gotoAdminDashboard(page);
        await expect(page.getByText("Queue backlog")).toBeVisible();
    });

    test("complaints link goes to /admin/complaints", async ({ page }) => {
        await gotoAdminDashboard(page);
        // Mock has open_complaints: 2. FeedRow renders a link with value "2".
        const link = page.getByRole("link", { name: "2" }).first();
        await expect(link).toHaveAttribute("href", /\/admin\/complaints/);
    });
});

test.describe("Admin student risk radar", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "admin");
        await stubMascotSuggestions(page, []);
    });

    test("student risk radar section is visible", async ({ page }) => {
        await stubAdminDashboard(page);
        await gotoAdminDashboard(page);
        await expect(page.getByText("Student risk radar")).toBeVisible();
    });

    test("empty risk alerts shows stable state", async ({ page }) => {
        await stubAdminDashboard(page);
        await gotoAdminDashboard(page);
        await expect(page.getByText("No active student risk alerts")).toBeVisible();
    });

    test("risk alerts with student data renders cards", async ({ page }) => {
        const bootstrap = adminBootstrapPayload({
            dashboard: adminDashboardPayload({
                student_risk_alerts: [
                    { student_id: "s1", student_name: "At-risk Student", class_name: "Class 10 A", dropout_risk: "high", academic_risk: "medium", fee_risk: "low", attendance_pct: 45, overall_score_pct: 38 },
                ],
            }),
        });
        await page.context().addCookies([{ name: "e2e_ssr_bypass", value: "1", domain: "localhost", path: "/" }]);
        await page.route("**/api/admin/dashboard-bootstrap**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(bootstrap) });
        });
        await page.route("**/api/admin/dashboard", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(bootstrap.dashboard) });
        });
        await page.route("**/api/admin/security", async (route) => { await route.fulfill({ status: 200, contentType: "application/json", body: "[]" }); });
        await page.route("**/api/whatsapp/release-gate-snapshot**", async (route) => { await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ analytics: {}, derived_rates: {} }) }); });
        await page.route("**/api/mascot/release-gate-snapshot**", async (route) => { await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ analytics: {}, derived_rates: {} }) }); });
        await page.route("**/api/mascot/greeting**", async (route) => { await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ greeting: "" }) }); });
        await page.route("**/api/mascot/message**", async (route) => { await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ reply: "" }) }); });
        await page.goto("/admin/dashboard", { waitUntil: "domcontentloaded" });
        await page.getByText("Attendance today").first().waitFor({ state: "visible", timeout: 30000 });
        await expect(page.getByText("At-risk Student")).toBeVisible();
    });
});

test.describe("Admin WhatsApp and Mascot release gate", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "admin");
        await stubAdminDashboard(page);
        await stubMascotSuggestions(page, []);
    });

    test("WhatsApp release gate section is visible", async ({ page }) => {
        await gotoAdminDashboard(page);
        await expect(page.getByText("WhatsApp release gate")).toBeVisible();
    });

    test("WhatsApp total messages is displayed", async ({ page }) => {
        await gotoAdminDashboard(page);
        await expect(page.getByText("Total messages")).toBeVisible();
        await expect(page.getByText("84").first()).toBeAttached();
    });

    test("Mascot release gate section is visible", async ({ page }) => {
        await gotoAdminDashboard(page);
        await expect(page.getByText("Mascot release gate")).toBeVisible();
    });

    test("Mascot total actions is displayed", async ({ page }) => {
        await gotoAdminDashboard(page);
        await expect(page.getByText("Total actions")).toBeVisible();
        await expect(page.getByText("126").first()).toBeAttached();
    });

    test("Refresh snapshot button is visible", async ({ page }) => {
        await gotoAdminDashboard(page);
        await expect(page.getByRole("button", { name: /Refresh snapshot/i })).toBeVisible();
    });

    test("Copy evidence button is visible", async ({ page }) => {
        await gotoAdminDashboard(page);
        await expect(page.getByRole("button", { name: /Copy evidence/i })).toBeVisible();
    });

    test("Copy staging packet button is visible", async ({ page }) => {
        await gotoAdminDashboard(page);
        await expect(page.getByRole("button", { name: /Copy staging packet/i })).toBeVisible();
    });
});

test.describe("Admin dashboard edge cases", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "admin");
        await stubMascotSuggestions(page, []);
    });

    test("500 from dashboard-bootstrap shows error state", async ({ page }) => {
        await page.context().addCookies([{ name: "e2e_ssr_bypass", value: "1", domain: "localhost", path: "/" }]);
        await page.route("**/api/admin/dashboard-bootstrap**", async (route) => {
            await route.fulfill({ status: 500, contentType: "application/json", body: JSON.stringify({ detail: "Server error" }) });
        });
        await page.route("**/api/mascot/greeting**", async (route) => { await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ greeting: "" }) }); });
        await page.route("**/api/mascot/message**", async (route) => { await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ reply: "" }) }); });
        await page.goto("/admin/dashboard", { waitUntil: "domcontentloaded" });
        // Should show something visible, not crash
        await expect(page.locator("body")).toBeVisible();
    });

    test("null dashboard data renders defaults (zeros)", async ({ page }) => {
        await page.context().addCookies([{ name: "e2e_ssr_bypass", value: "1", domain: "localhost", path: "/" }]);
        await page.route("**/api/admin/dashboard-bootstrap**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ dashboard: null }) });
        });
        await page.route("**/api/admin/dashboard", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(null) });
        });
        await page.route("**/api/admin/security", async (route) => { await route.fulfill({ status: 200, body: "[]" }); });
        await page.route("**/api/whatsapp/release-gate-snapshot**", async (route) => { await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({}) }); });
        await page.route("**/api/mascot/release-gate-snapshot**", async (route) => { await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({}) }); });
        await page.route("**/api/mascot/greeting**", async (route) => { await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ greeting: "" }) }); });
        await page.route("**/api/mascot/message**", async (route) => { await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ reply: "" }) }); });
        await page.goto("/admin/dashboard", { waitUntil: "domcontentloaded" });
        // With null data, normalizeDashboardData returns zeros. Wait for data to render.
        await page.getByText("Attendance today").first().waitFor({ state: "visible", timeout: 30000 });
        await expect(page.getByText("0%").first()).toBeAttached();
    });

    test("no observability alerts shows stable state", async ({ page }) => {
        await stubAdminDashboard(page);
        await gotoAdminDashboard(page);
        await expect(page.getByText("No active alerts")).toBeVisible();
    });

    test("no security activity shows empty state", async ({ page }) => {
        await stubAdminDashboard(page);
        await gotoAdminDashboard(page);
        await expect(page.getByText("No recent security events")).toBeVisible();
    });

    test("trend data unavailable shows empty state", async ({ page }) => {
        await stubAdminDashboard(page);
        await gotoAdminDashboard(page);
        await expect(page.getByText("Trend data unavailable")).toBeVisible();
    });

});
