import { expect, test } from "@playwright/test";

function brandingPayload() {
    return {
        name: "VidyaOS",
        logo_url: null,
        primary_color: "#2563eb",
        secondary_color: "#0f172a",
        accent_color: "#f59e0b",
        font_family: "Inter",
        theme_style: "modern",
    };
}

async function stubBranding(page: import("@playwright/test").Page) {
    await page.route("**/api/branding/config", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify(brandingPayload()),
        });
    });
}

test.describe("Prism landing runtime safeguards", () => {
    test("server HTML respects the language cookie on first paint", async ({ request }) => {
        const response = await request.get("/", {
            headers: {
                Cookie: "vidyaos-lang=hi",
            },
        });

        expect(response.ok()).toBeTruthy();
        await expect(response.text()).resolves.toContain('<html lang="hi"');
    });

    test("landing stays usable on Fast 3G with a Hindi first-paint cookie", async ({ page }) => {
        const client = await page.context().newCDPSession(page);
        await client.send("Network.enable");
        await client.send("Network.emulateNetworkConditions", {
            offline: false,
            latency: 150,
            downloadThroughput: 1.6 * 1024 * 1024 / 8,
            uploadThroughput: 750 * 1024 / 8,
            connectionType: "cellular3g",
        });

        await page.context().addCookies([
            {
                name: "vidyaos-lang",
                value: "hi",
                url: "http://127.0.0.1:9000",
            },
        ]);

        await stubBranding(page);
        await page.goto("/");

        await expect(page.locator("html")).toHaveAttribute("lang", "hi");
        await expect(page.getByRole("link", { name: /Explore demo/i })).toBeVisible();
    });

    test("landing hero honors reduced-motion preference", async ({ page }) => {
        await page.emulateMedia({ reducedMotion: "reduce" });
        await stubBranding(page);

        await page.goto("/");

        await expect(page.getByRole("link", { name: /Explore demo/i })).toBeVisible();
        await expect(page.getByTestId("prism-hero-scene")).toHaveAttribute("data-reduced-motion", "true");
    });

    test("landing hero preserves layout and messaging when WebGL is unavailable", async ({ page }) => {
        await page.addInitScript(() => {
            const originalGetContext = HTMLCanvasElement.prototype.getContext;
            Object.defineProperty(HTMLCanvasElement.prototype, "getContext", {
                configurable: true,
                value: function patchedGetContext(type: string, ...args: unknown[]) {
                    if (type === "webgl" || type === "webgl2" || type === "experimental-webgl") {
                        return null;
                    }

                    return Reflect.apply(originalGetContext, this, [type, ...args]);
                },
            });
        });

        await stubBranding(page);
        await page.goto("/");

        await expect(page.getByTestId("prism-hero-scene")).toHaveAttribute("data-webgl", "fallback");
        await expect(page.getByTestId("prism-hero-fallback")).toContainText("without WebGL");
    });

    test("landing hero disables the interactive scene on constrained connections", async ({ page }) => {
        await page.addInitScript(() => {
            Object.defineProperty(window.navigator, "connection", {
                configurable: true,
                value: {
                    effectiveType: "3g",
                    saveData: false,
                    downlink: 0.8,
                    addEventListener() { },
                    removeEventListener() { },
                },
            });
        });

        await stubBranding(page);
        await page.goto("/");

        await expect(page.getByTestId("prism-hero-scene")).toHaveAttribute("data-network", "3g");
        await expect(page.getByTestId("prism-hero-fallback")).toContainText("Reduced Network Mode");
    });
});

test.describe("Phase 2 adaptive polling safeguards", () => {
    test("admin queue backs off refresh polling on slow connections", async ({ page }) => {
        await page.addInitScript(() => {
            window.localStorage.setItem("vidyaos_access_token", "test-token");

            const capturedIntervals: number[] = [];
            const originalSetInterval = window.setInterval.bind(window);
            const browserSetInterval = originalSetInterval as unknown as (
                handler: TimerHandler,
                timeout?: number,
                ...args: unknown[]
            ) => number;

            Object.defineProperty(window.navigator, "connection", {
                configurable: true,
                value: {
                    effectiveType: "3g",
                    saveData: false,
                    downlink: 0.9,
                    addEventListener() { },
                    removeEventListener() { },
                },
            });

            Object.defineProperty(window, "__capturedIntervals", {
                configurable: true,
                value: capturedIntervals,
            });

            window.setInterval = ((handler: TimerHandler, timeout?: number, ...args: unknown[]) => {
                capturedIntervals.push(Number(timeout ?? 0));
                return browserSetInterval(handler, timeout, ...args);
            }) as unknown as typeof window.setInterval;
        });

        await stubBranding(page);

        await page.route("**/api/admin/**", async (route) => {
            const request = route.request();
            const url = new URL(request.url());
            const pathname = url.pathname;

            if (pathname.endsWith("/api/admin/ai-jobs/metrics")) {
                await route.fulfill({
                    status: 200,
                    contentType: "application/json",
                    body: JSON.stringify({
                        pending_depth: 1,
                        processing_depth: 0,
                        tracked_jobs: 1,
                        completed_last_window: 4,
                        failed_last_window: 0,
                        failure_rate_pct: 0,
                        retry_count: 0,
                        stuck_jobs: 0,
                        stuck_job_ids: [],
                        dead_letter_count: 0,
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
                    body: JSON.stringify([]),
                });
                return;
            }

            if (pathname.endsWith("/api/admin/ai-jobs") && request.method() === "GET") {
                await route.fulfill({
                    status: 200,
                    contentType: "application/json",
                    body: JSON.stringify([
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
                    ]),
                });
                return;
            }

            if (pathname.match(/\/api\/admin\/ai-jobs\/[^/]+$/)) {
                await route.fulfill({
                    status: 200,
                    contentType: "application/json",
                    body: JSON.stringify({
                        job_id: "job-queued",
                        job_type: "text_query",
                        trace_id: "trace-queued",
                        status: "queued",
                        attempts: 0,
                        max_retries: 2,
                        events: [],
                        audit_history: [],
                    }),
                });
                return;
            }

            if (pathname.endsWith("/api/admin/ocr-metrics")) {
                await route.fulfill({
                    status: 200,
                    contentType: "application/json",
                    body: JSON.stringify({ metrics: [] }),
                });
                return;
            }

            await route.fulfill({
                status: 404,
                contentType: "application/json",
                body: JSON.stringify({ detail: "Unhandled admin route" }),
            });
        });

        await page.goto("/admin/queue");

        await expect(page.getByRole("heading", { name: /Keep the AI job queue controlled before incidents spread/i })).toBeVisible();

        const intervals = await page.evaluate(() => {
            return (window as Window & { __capturedIntervals?: number[] }).__capturedIntervals || [];
        });

        expect(intervals).toContain(30000);
    });
});
