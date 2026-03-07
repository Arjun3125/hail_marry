import { expect, test } from "@playwright/test";

test("admin dashboard shows alerts and dispatches them", async ({ page }) => {
    await page.addInitScript(() => {
        window.localStorage.setItem("vidyaos_access_token", "test-token");
    });

    let dispatchCalls = 0;

    await page.route("**/api/admin/**", async (route) => {
        const request = route.request();
        const url = new URL(request.url());
        const pathname = url.pathname;

        if (pathname.endsWith("/api/admin/dashboard")) {
            await route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify({
                    total_students: 120,
                    total_teachers: 14,
                    active_today: 52,
                    ai_queries_today: 31,
                    avg_attendance: 93,
                    avg_performance: 81,
                    open_complaints: 2,
                    queue_pending_depth: 5,
                    queue_processing_depth: 2,
                    queue_failure_rate_pct: 12,
                    queue_stuck_jobs: 1,
                    observability_alerts: [
                        {
                            code: "queue_depth_high",
                            severity: "warning",
                            message: "Queue depth is 5 / 200 for this tenant.",
                        },
                    ],
                }),
            });
            return;
        }

        if (pathname.endsWith("/api/admin/security")) {
            await route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify([]),
            });
            return;
        }

        if (pathname.endsWith("/api/admin/observability/alerts/dispatch")) {
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
            return;
        }

        await route.fulfill({ status: 404, contentType: "application/json", body: JSON.stringify({ detail: "Unhandled admin route" }) });
    });

    await page.goto("/admin/dashboard");

    await expect(page.getByRole("heading", { name: "Admin Dashboard" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Queue Health" })).toBeVisible();
    await expect(page.getByText("Queue depth is 5 / 200 for this tenant.")).toBeVisible();
    await expect(page.getByRole("link", { name: "Open Trace Viewer" })).toBeVisible();

    await page.getByRole("button", { name: "Dispatch Alerts" }).click();
    await expect.poll(() => dispatchCalls).toBe(1);
});
