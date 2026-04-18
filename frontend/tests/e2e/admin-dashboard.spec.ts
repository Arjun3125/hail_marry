import { expect, test } from "@playwright/test";
import { stubAuthShell, stubAdminDashboard, adminBootstrapPayload, adminDashboardPayload, stubMascotSuggestions } from "../fixtures/helpers";

test("admin dashboard shows alerts and dispatches them", async ({ page }) => {
    await stubAuthShell(page, "admin");
    await stubMascotSuggestions(page, []);

    const bootstrap = adminBootstrapPayload({
        dashboard: adminDashboardPayload({
            observability_alerts: [
                {
                    code: "queue_depth_high",
                    severity: "warning",
                    message: "Queue depth is 5 / 200 for this tenant.",
                },
            ],
        }),
    });

    let dispatchCalls = 0;

    await page.context().addCookies([{ name: "e2e_ssr_bypass", value: "1", domain: "localhost", path: "/" }]);
    await page.route("**/api/admin/dashboard-bootstrap**", async (route) => {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(bootstrap) });
    });
    await page.route("**/api/admin/dashboard", async (route) => {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(bootstrap.dashboard) });
    });
    await page.route("**/api/admin/security", async (route) => {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify([]) });
    });
    await page.route("**/api/admin/observability/alerts/dispatch", async (route) => {
        dispatchCalls += 1;
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                alerts: [
                    {
                        code: "queue_depth_high",
                        severity: "warning",
                        message: "Queue depth is 5 / 200 for this tenant.",
                    },
                ],
                delivered: 1,
                skipped: 0,
            }),
        });
    });
    await page.route("**/api/whatsapp/release-gate-snapshot**", async (route) => {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ analytics: {}, derived_rates: {} }) });
    });
    await page.route("**/api/mascot/release-gate-snapshot**", async (route) => {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ analytics: {}, derived_rates: {} }) });
    });
    await page.route("**/api/mascot/greeting**", async (route) => {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ greeting: "" }) });
    });
    await page.route("**/api/mascot/message**", async (route) => {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ reply: "" }) });
    });

    await page.goto("/admin/dashboard", { waitUntil: "domcontentloaded" });
    await page.getByText("Attendance today").first().waitFor({ state: "visible", timeout: 30000 });

    await expect(page.getByText("Queue depth is 5 / 200 for this tenant.")).toBeVisible();
    await expect(page.getByRole("button", { name: /Dispatch/i })).toBeVisible();

    await page.getByRole("button", { name: /Dispatch/i }).click();
    await expect.poll(() => dispatchCalls).toBe(1);
});
