import { expect, test } from "@playwright/test";

test("admin traces page loads diagnostics summary and trace timeline", async ({ page }) => {
    await page.addInitScript(() => {
        window.localStorage.setItem("vidyaos_access_token", "test-token");
    });

    await page.route("**/api/admin/observability/traceability**", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                generated_at: "2026-03-06T10:00:00.000Z",
                period_days: 7,
                total_errors: 12,
                grouped_errors: [
                    {
                        error_code: "QUEUE_TIMEOUT",
                        title: "Queue handler timeout",
                        subsystem: "worker",
                        severity: "high",
                        count: 5,
                        latest_at: "2026-03-06T09:45:00.000Z",
                    },
                ],
                subsystem_totals: [
                    { subsystem: "worker", count: 7 },
                    { subsystem: "api", count: 5 },
                ],
                recent_errors: [
                    {
                        created_at: "2026-03-06T09:50:00.000Z",
                        error_code: "QUEUE_TIMEOUT",
                        subsystem: "worker",
                        severity: "high",
                        detail: "Worker exceeded execution window",
                        path: "/api/admin/ai-jobs/retry",
                        method: "POST",
                        status_code: 500,
                        trace_id: "trace-001",
                    },
                ],
            }),
        });
    });

    await page.route("**/api/admin/observability/traces/trace-001", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                trace_id: "trace-001",
                events: [
                    {
                        created_at: "2026-03-06T09:50:01.000Z",
                        action: "queue.retry.started",
                        entity_type: "ai_job",
                        metadata: { job_id: "job-1", attempt: 2 },
                    },
                    {
                        created_at: "2026-03-06T09:50:04.000Z",
                        action: "worker.timeout",
                        entity_type: "worker",
                        metadata: { worker_id: "worker-7", duration_ms: 30000 },
                    },
                ],
            }),
        });
    });

    await page.route("**/api/branding/config", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                name: "VidyaOS",
                logo_url: null,
                primary_color: "#2563eb",
                secondary_color: "#0f172a",
                accent_color: "#f59e0b",
                font_family: "Inter",
                theme_style: "modern",
            }),
        });
    });

    await page.goto("/admin/traces");

    await expect(page.getByRole("heading", { name: "Read trace failures before they become repeated incidents" })).toBeVisible();
    await expect(page.getByRole("heading", { name: /Trace diagnostics/i })).toBeVisible();
    await expect(page.getByText(/QUEUE_TIMEOUT/i).first()).toBeVisible();
    await expect(page.getByText("Worker exceeded execution window")).toBeVisible();

    await page.getByPlaceholder("Paste a trace id").fill("trace-001");
    await page.getByRole("button", { name: /load trace/i }).click();

    await expect(page.getByRole("heading", { name: /Trace timeline/i })).toBeVisible();
    await expect(page.getByText("queue.retry.started")).toBeVisible();
    await expect(page.getByText("worker.timeout")).toBeVisible();
    await expect(page.getByText("trace-001").first()).toBeVisible();
});
