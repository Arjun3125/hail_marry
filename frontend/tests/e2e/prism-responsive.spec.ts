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

    await page.route("**/api/personalization/events", async (route) => {
        await route.fulfill({
            status: 202,
            contentType: "application/json",
            body: JSON.stringify({ ok: true }),
        });
    });
}

async function expectNoHorizontalOverflow(page: Page) {
    const widths = await page.evaluate(() => ({
        innerWidth: window.innerWidth,
        scrollWidth: document.documentElement.scrollWidth,
    }));

    expect(widths.scrollWidth).toBeLessThanOrEqual(widths.innerWidth + 1);
}

test.describe("Prism representative responsive smoke", () => {
    test("landing remains stable on mobile", async ({ page }) => {
        await page.setViewportSize({ width: 390, height: 844 });
        await stubBranding(page);

        await page.goto("/", { waitUntil: "domcontentloaded" });

        await expect(page.getByRole("link", { name: /Explore demo/i })).toBeVisible();
        await expectNoHorizontalOverflow(page);
    });

    test("student AI Studio remains stable on tablet", async ({ page }) => {
        await page.setViewportSize({ width: 834, height: 1112 });
        await stubAuthenticatedShell(page);

        await page.route("**/api/notebooks", async (route) => {
            await route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify({
                    items: [
                        {
                            id: "nb-bio",
                            name: "Biology Chapter 10",
                            color: "#2563eb",
                            icon: "book",
                            created_at: "2026-03-31T08:00:00.000Z",
                            updated_at: "2026-03-31T08:00:00.000Z",
                            is_active: true,
                        },
                    ],
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
                            id: "rec-starter-1",
                            prompt: "Summarize Biology Chapter 10 and tell me the weakest concept first.",
                        },
                    ],
                }),
            });
        });

        await page.goto("/student/ai-studio", { waitUntil: "domcontentloaded" });

        await expect(page.getByRole("heading", { name: /Start with one clear intent, then open the full study desk/i })).toBeVisible();
        await expectNoHorizontalOverflow(page);
    });

    test("teacher dashboard remains stable on desktop", async ({ page }) => {
        await page.setViewportSize({ width: 1440, height: 900 });
        await stubAuthenticatedShell(page);

        await page.route("**/api/teacher/dashboard", async (route) => {
            await route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify({
                    classes: [
                        { id: "class-1", name: "Class 10 A", students: 32, avg_attendance: 92, avg_marks: 78 },
                        { id: "class-2", name: "Class 9 B", students: 28, avg_attendance: 88, avg_marks: 74 },
                    ],
                    today_classes: [
                        {
                            class_id: "class-1",
                            class_name: "Class 10 A",
                            subject: "Biology",
                            start_time: "09:00:00",
                            end_time: "09:45:00",
                        },
                    ],
                    pending_reviews: 4,
                    open_assignments: 3,
                }),
            });
        });

        await page.goto("/teacher/dashboard", { waitUntil: "domcontentloaded" });

        await expect(page.getByRole("heading", { name: /Guide the day, not the dashboard/i })).toBeVisible();
        await expectNoHorizontalOverflow(page);
    });

    test("admin dashboard remains stable on tablet", async ({ page }) => {
        await page.setViewportSize({ width: 1024, height: 1366 });
        await stubAuthenticatedShell(page);

        await page.route("**/api/admin/dashboard", async (route) => {
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
                    student_risk_summary: {
                        high_risk_students: 2,
                        medium_risk_students: 3,
                        academic_high_risk: 1,
                        fee_high_risk: 1,
                        dropout_high_risk: 1,
                    },
                    student_risk_alerts: [
                        {
                            student_id: "student-1",
                            student_name: "Aarav Kumar",
                            class_name: "Class 10",
                            dropout_risk: "high",
                            academic_risk: "high",
                            fee_risk: "medium",
                            attendance_pct: 58,
                            overall_score_pct: 39,
                        },
                    ],
                    observability_alerts: [
                        {
                            code: "queue_depth_high",
                            severity: "warning",
                            message: "Queue depth is 5 / 200 for this tenant.",
                        },
                    ],
                }),
            });
        });

        await page.route("**/api/admin/security", async (route) => {
            await route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify([]),
            });
        });

        await page.route("**/api/whatsapp/release-gate-snapshot?days=7", async (route) => {
            await route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify({
                    generated_at: "2026-03-30T03:30:00Z",
                    period_days: 7,
                    analytics: { total_messages: 84, inbound: 42, outbound: 42, unique_users: 12, avg_latency_ms: 920 },
                    release_gate_metrics: {
                        duplicate_inbound_total: 1,
                        routing_failure_total: 2,
                        visible_failure_total: 1,
                        outbound_retryable_failure_total: 1,
                        upload_ingest_failure_total: 0,
                        link_ingest_failure_total: 0,
                    },
                    derived_rates: {
                        duplicate_inbound_pct: 2.38,
                        routing_failure_pct: 4.76,
                        visible_failure_pct: 2.38,
                        outbound_retryable_failure_pct: 2.38,
                    },
                }),
            });
        });

        await page.route("**/api/mascot/release-gate-snapshot?days=7", async (route) => {
            await route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify({
                    generated_at: "2026-03-30T03:30:00Z",
                    period_days: 7,
                    analytics: { total_actions: 126, unique_users: 18 },
                    release_gate_metrics: {
                        interpretation_success_total: 120,
                        interpretation_failure_total: 2,
                        execution_success_total: 110,
                        execution_failure_total: 3,
                        confirmation_success_total: 8,
                        confirmation_failure_total: 1,
                        confirmation_cancelled_total: 2,
                        upload_success_total: 14,
                        upload_failure_total: 1,
                    },
                    derived_rates: {
                        interpretation_failure_pct: 1.64,
                        execution_failure_pct: 2.65,
                        upload_failure_pct: 6.67,
                        confirmation_failure_pct: 9.09,
                        overall_failure_pct: 2.84,
                    },
                    active_alerts: [
                        {
                            code: "mascot_failure_rate_high",
                            severity: "critical",
                            message: "Mascot upload failure rate reached 16.7% over 12 events.",
                        },
                    ],
                }),
            });
        });

        await page.goto("/admin/dashboard", { waitUntil: "domcontentloaded" });

        await expect(page.getByRole("heading", { name: /See school health in one screen before you drill down/i })).toBeVisible();
        await expectNoHorizontalOverflow(page);
    });

    test("parent dashboard remains stable on mobile", async ({ page }) => {
        await page.setViewportSize({ width: 393, height: 852 });
        await stubAuthenticatedShell(page);

        await page.route("**/api/parent/dashboard", async (route) => {
            await route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify({
                    child: {
                        id: "student-1",
                        name: "Aarav Sharma",
                        email: "aarav@example.com",
                        class: "10-A",
                    },
                    attendance_pct: 94,
                    avg_marks: 82,
                    pending_assignments: 1,
                    latest_mark: {
                        subject: "Biology",
                        exam: "Unit Test 3",
                        percentage: 84,
                        date: "2026-03-30",
                    },
                    next_class: {
                        day: 1,
                        start_time: "09:00",
                        end_time: "09:45",
                        subject: "Biology",
                    },
                }),
            });
        });

        await page.goto("/parent/dashboard", { waitUntil: "domcontentloaded" });

        await expect(page.getByRole("heading", { name: /Read your child's week in under a minute/i })).toBeVisible();
        await expectNoHorizontalOverflow(page);
    });
});

