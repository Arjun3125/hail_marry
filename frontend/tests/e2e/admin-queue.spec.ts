import { expect, test } from "@playwright/test";

test("admin queue page supports cancel, dead-letter, and retry actions", async ({ page }) => {
    await page.addInitScript(() => {
        window.localStorage.setItem("vidyaos_access_token", "test-token");
    });

    const jobs = [
        {
            job_id: "job-queued",
            job_type: "text_query",
            status: "queued",
            created_at: "2026-03-06T09:00:00.000Z",
            updated_at: "2026-03-06T09:00:00.000Z",
            attempts: 0,
            max_retries: 2,
            priority: 30,
            worker_id: null,
            duration_ms: null,
            user_id: "user-1",
            user_name: "Queued Student",
            trace_id: "trace-queued",
            events: [],
        },
        {
            job_id: "job-failed",
            job_type: "audio_overview",
            status: "failed",
            created_at: "2026-03-06T09:05:00.000Z",
            updated_at: "2026-03-06T09:05:30.000Z",
            attempts: 1,
            max_retries: 2,
            priority: 35,
            worker_id: "worker-1",
            duration_ms: 2500,
            user_id: "user-2",
            user_name: "Failed Student",
            trace_id: "trace-failed",
            error: "boom",
            events: [],
        },
    ];
    const auditHistory = [
        {
            action: "ai.job.created",
            actor: "System",
            created_at: "2026-03-06T09:00:00.000Z",
            metadata: { detail: "Queued for processing" },
            job_id: "job-queued",
        },
    ];

    const counters = { cancel: 0, retry: 0, deadLetter: 0 };

    await page.route("**/api/admin/**", async (route) => {
        const request = route.request();
        const url = new URL(request.url());
        const pathname = url.pathname;

        if (pathname.endsWith("/api/admin/ai-jobs/metrics")) {
            await route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify({
                    pending_depth: jobs.filter((job) => job.status === "queued").length,
                    processing_depth: 0,
                    tracked_jobs: jobs.length,
                    completed_last_window: 4,
                    failed_last_window: jobs.filter((job) => job.status === "failed").length,
                    failure_rate_pct: 20,
                    retry_count: counters.retry,
                    stuck_jobs: 0,
                    stuck_job_ids: [],
                    dead_letter_count: jobs.filter((job) => job.status === "dead_letter").length,
                    metrics_window_seconds: 3600,
                    stuck_after_seconds: 300,
                    max_pending_jobs: 1000,
                    max_pending_jobs_per_tenant: 200,
                    by_status: {},
                    by_type: {},
                }),
            });
            return;
        }

        if (pathname.endsWith("/api/admin/ai-jobs/history")) {
            await route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify(auditHistory),
            });
            return;
        }

        if (pathname.endsWith("/api/admin/ai-jobs") && request.method() === "GET") {
            await route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify(jobs.map((job) => ({
                    ...job,
                    events: undefined,
                }))),
            });
            return;
        }

        const jobMatch = pathname.match(/\/api\/admin\/ai-jobs\/([^/]+)(?:\/(cancel|retry|dead-letter))?$/);
        if (jobMatch) {
            const [, jobId, action] = jobMatch;
            const job = jobs.find((candidate) => candidate.job_id === jobId);

            if (!job) {
                await route.fulfill({ status: 404, contentType: "application/json", body: JSON.stringify({ detail: "AI job not found" }) });
                return;
            }

            if (request.method() === "GET") {
                await route.fulfill({
                    status: 200,
                    contentType: "application/json",
                    body: JSON.stringify({
                        ...job,
                        request: { topic: "Atoms" },
                        result: job.status === "queued" ? null : { ok: true },
                        audit_history: auditHistory.filter((entry) => entry.job_id === jobId),
                    }),
                });
                return;
            }

            if (request.method() === "POST" && action === "cancel") {
                counters.cancel += 1;
                job.status = "cancelled";
                auditHistory.unshift({
                    action: "ai.job.cancelled",
                    actor: "Admin User",
                    created_at: "2026-03-06T09:10:00.000Z",
                    metadata: { detail: "Cancelled by admin" },
                    job_id: jobId,
                });
            }

            if (request.method() === "POST" && action === "dead-letter") {
                counters.deadLetter += 1;
                job.status = "dead_letter";
                auditHistory.unshift({
                    action: "ai.job.dead_lettered",
                    actor: "Admin User",
                    created_at: "2026-03-06T09:11:00.000Z",
                    metadata: { detail: "Moved to dead letter" },
                    job_id: jobId,
                });
            }

            if (request.method() === "POST" && action === "retry") {
                counters.retry += 1;
                job.status = "queued";
                job.attempts += 1;
                auditHistory.unshift({
                    action: "ai.job.retried",
                    actor: "Admin User",
                    created_at: "2026-03-06T09:12:00.000Z",
                    metadata: { detail: "Retried by admin" },
                    job_id: jobId,
                });
            }

            await route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify({ ...job }),
            });
            return;
        }

        await route.fulfill({ status: 404, contentType: "application/json", body: JSON.stringify({ detail: "Unhandled admin route" }) });
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

    await page.goto("/admin/queue");

    await expect(page.getByRole("heading", { name: "AI Queue Operations" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Persistent Audit History" })).toBeVisible();

    const queuedRow = page.locator("tr").filter({ hasText: "job-queued" });
    await queuedRow.getByRole("button", { name: /cancel/i }).click();
    await expect(queuedRow.getByText("cancelled")).toBeVisible();

    const failedRow = page.locator("tr").filter({ hasText: "job-failed" });
    await failedRow.getByRole("button", { name: /dead letter/i }).click();
    await expect(failedRow.getByText("dead_letter")).toBeVisible();

    await failedRow.getByRole("button", { name: /retry/i }).click();
    await expect(failedRow.getByText("queued")).toBeVisible();

    expect(counters.cancel).toBe(1);
    expect(counters.deadLetter).toBe(1);
    expect(counters.retry).toBe(1);
});
