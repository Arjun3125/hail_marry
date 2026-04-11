import { expect, test, type Page } from "@playwright/test";

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

async function stubBranding(page: Page) {
    await page.route("**/api/branding/config", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify(brandingPayload()),
        });
    });
}

async function stubAuthenticatedShell(page: Page) {
    await page.addInitScript(() => {
        window.localStorage.setItem("vidyaos_access_token", "test-token");
        window.localStorage.setItem("student-tour", "completed");
        window.localStorage.setItem("teacher-tour", "completed");
        window.localStorage.setItem("admin-tour", "completed");
        window.localStorage.setItem("parent-tour", "completed");
    });

    await stubBranding(page);
}

async function readNavigationMetrics(page: Page) {
    return page.evaluate(() => {
        const navigation = performance.getEntriesByType("navigation")[0] as PerformanceNavigationTiming | undefined;
        const paints = performance.getEntriesByType("paint");
        const firstContentfulPaint = paints.find((entry) => entry.name === "first-contentful-paint")?.startTime ?? 0;

        if (!navigation) {
            throw new Error("Missing navigation timing entry: domContentLoaded, loadEventEnd, and responseEnd are unavailable.");
        }

        return {
            domContentLoaded: navigation.domContentLoadedEventEnd,
            loadEventEnd: navigation.loadEventEnd,
            responseEnd: navigation.responseEnd,
            firstContentfulPaint,
        };
    });
}

test.describe("Mobile performance budgets", () => {
    test("landing page stays within budget on mobile", async ({ page }) => {
        await page.setViewportSize({ width: 390, height: 844 });
        await stubBranding(page);

        await page.goto("/", { waitUntil: "load" });
        await expect(page.getByRole("link", { name: /Explore demo/i })).toBeVisible();

        const metrics = await readNavigationMetrics(page);

        expect(metrics.firstContentfulPaint).toBeGreaterThan(0);
        expect(metrics.firstContentfulPaint).toBeLessThan(1800);
        expect(metrics.domContentLoaded).toBeLessThan(2200);
        expect(metrics.responseEnd).toBeLessThan(2200);
    });

    test("student overview stays within budget on mobile", async ({ page }) => {
        await page.setViewportSize({ width: 393, height: 852 });
        await stubAuthenticatedShell(page);

        await page.route("**/api/student/overview-bootstrap", async (route) => {
            await route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify({
                    dashboard: {
                        attendance_pct: 94,
                        avg_marks: 82,
                        pending_assignments: 2,
                        ai_queries_today: 6,
                        ai_queries_limit: 50,
                        upcoming_classes: [{ subject: "Biology", time: "09:00" }],
                        my_uploads: 18,
                        ai_insight: "Biology revision is trending upward.",
                    },
                    weak_topics: {
                        weak_topics: [{ subject: "Chemistry", average_score: 54, exam_count: 3, is_weak: true }],
                        strong_topics: [{ subject: "Biology", average_score: 84, exam_count: 4, is_weak: false }],
                    },
                    streaks: {
                        current_streak: 6,
                        longest_streak: 14,
                        total_sessions: 48,
                        last_login: "2026-04-08T08:00:00.000Z",
                        badges: [],
                    },
                    recommendations: {
                        items: [
                            {
                                id: "rec-1",
                                label: "Rebuild Chemistry equilibrium",
                                description: "Target the weakest concept first.",
                                prompt: "Help me revise equilibrium and give me a short quiz.",
                            },
                        ],
                    },
                    study_path: {
                        plan: {
                            id: "plan-1",
                            focus_topic: "Chemical equilibrium",
                            status: "active",
                            items: [
                                { id: "step-1", title: "Review the core definition", status: "pending", target_tool: "assistant" },
                            ],
                            next_action: { id: "step-1", title: "Review the core definition", status: "pending", target_tool: "assistant" },
                        },
                    },
                }),
            });
        });

        await page.route("**/api/student/dashboard", async (route) => {
            await route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify({
                    attendance_pct: 94,
                    avg_marks: 82,
                    pending_assignments: 2,
                    ai_queries_today: 6,
                    ai_queries_limit: 50,
                    upcoming_classes: [{ subject: "Biology", time: "09:00" }],
                    my_uploads: 18,
                    ai_insight: "Biology revision is trending upward.",
                }),
            });
        });

        await page.route("**/api/student/weak-topics", async (route) => {
            await route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify({
                    weak_topics: [{ subject: "Chemistry", average_score: 54, exam_count: 3, is_weak: true }],
                    strong_topics: [{ subject: "Biology", average_score: 84, exam_count: 4, is_weak: false }],
                }),
            });
        });

        await page.route("**/api/student/streaks", async (route) => {
            await route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify({
                    current_streak: 6,
                    longest_streak: 14,
                    total_sessions: 48,
                    last_login: "2026-04-08T08:00:00.000Z",
                    badges: [],
                }),
            });
        });

        await page.route("**/api/personalization/recommendations**", async (route) => {
            await route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify({
                    items: [
                        {
                            id: "rec-1",
                            label: "Rebuild Chemistry equilibrium",
                            description: "Target the weakest concept first.",
                            prompt: "Help me revise equilibrium and give me a short quiz.",
                        },
                    ],
                }),
            });
        });

        await page.route("**/api/personalization/study-path**", async (route) => {
            await route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify({
                    plan: {
                        id: "plan-1",
                        focus_topic: "Chemical equilibrium",
                        status: "active",
                        items: [
                            { id: "step-1", title: "Review the core definition", status: "pending", target_tool: "assistant" },
                        ],
                        next_action: { id: "step-1", title: "Review the core definition", status: "pending", target_tool: "assistant" },
                    },
                }),
            });
        });

        await page.goto("/student/overview", { waitUntil: "load" });
        await expect(page.getByRole("heading", { name: /Your academic day, organized for action/i })).toBeVisible();

        const metrics = await readNavigationMetrics(page);

        expect(metrics.firstContentfulPaint).toBeGreaterThan(0);
        expect(metrics.firstContentfulPaint).toBeLessThan(2200);
        expect(metrics.responseEnd).toBeLessThan(2800);
        expect(metrics.loadEventEnd).toBeLessThan(4200);
    });
});
