import { expect, test } from "@playwright/test";

test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
        window.localStorage.setItem("vidyaos_access_token", "test-token");
        window.localStorage.setItem("student-tour", "completed");
        window.localStorage.setItem("teacher-tour", "completed");
        window.localStorage.setItem("admin-tour", "completed");
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

    await page.route("**/api/demo/profiles", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                demo_mode: true,
                profiles: [
                    {
                        role: "student",
                        persona: "Naren, Class 11 Science",
                        email: null,
                        landing_path: "/student/overview",
                        feature_showcase: ["AI assistant"],
                        walkthrough: [],
                    },
                    {
                        role: "teacher",
                        persona: "Mr. Sharma, Science Faculty",
                        email: null,
                        landing_path: "/teacher/dashboard",
                        feature_showcase: ["Assessment generation"],
                        walkthrough: [],
                    },
                    {
                        role: "admin",
                        persona: "School Operations Lead",
                        email: null,
                        landing_path: "/admin/dashboard",
                        feature_showcase: ["Institution monitoring"],
                        walkthrough: [],
                    },
                    {
                        role: "parent",
                        persona: "Mrs. Sharma, Parent",
                        email: null,
                        landing_path: "/parent/dashboard",
                        feature_showcase: ["Progress narrative"],
                        walkthrough: [],
                    },
                ],
                notes: [],
            }),
        });
    });

    await page.route("**/api/demo/switch-role", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({ ok: true }),
        });
    });

    await page.route("**/api/auth/demo-login", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({ access_token: "demo-token" }),
        });
    });

    await page.route("**/api/student/dashboard", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                attendance_pct: 91,
                avg_marks: 78,
                pending_assignments: 2,
                ai_queries_today: 3,
                ai_queries_limit: 50,
                upcoming_classes: [{ subject: "Biology", time: "09:00" }],
                my_uploads: 4,
                ai_insight: "Focus on photosynthesis fundamentals.",
            }),
        });
    });

    await page.route("**/api/student/weak-topics", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                weak_topics: [{ subject: "Biology", average_score: 46, exam_count: 3, is_weak: true }],
                strong_topics: [{ subject: "Maths", average_score: 88, exam_count: 4, is_weak: false }],
            }),
        });
    });

    await page.route("**/api/student/streaks", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                current_streak: 4,
                longest_streak: 7,
                total_sessions: 12,
                last_login: "2026-03-31T08:00:00.000Z",
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
                        label: "Review Photosynthesis basics",
                        description: "Start with a quick guided explanation before practicing.",
                        prompt: "Explain photosynthesis simply and then quiz me.",
                        target_tool: "study_guide",
                        reason: "mastery_gap",
                        priority: "high",
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
                    focus_topic: "Photosynthesis",
                    status: "active",
                    items: [],
                    next_action: null,
                },
            }),
        });
    });

    await page.route("**/api/teacher/dashboard", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                classes: [
                    { id: "class-1", name: "Class 10 A", students: 32, avg_attendance: 92, avg_marks: 78 },
                ],
                today_classes: [
                    { class_id: "class-1", class_name: "Class 10 A", subject: "Biology", start_time: "09:00:00", end_time: "09:45:00" },
                ],
                pending_reviews: 4,
                open_assignments: 3,
            }),
        });
    });

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
                student_risk_alerts: [],
                observability_alerts: [],
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
                active_alerts: [],
            }),
        });
    });
});

test("Verify demo role entry points load current dashboards", async ({ page }) => {
    await page.goto("/demo");
    await expect(page.getByRole("heading", { name: /Enter the product as a real/i })).toBeVisible();

    await page.getByRole("button", { name: /Student/i }).first().click();
    await page.waitForURL("**/student/overview");
    await expect(page.getByRole("heading", { name: /Your academic day, organized for action/i })).toBeVisible();

    await page.goto("/demo");
    await page.getByRole("button", { name: /Teacher/i }).first().click();
    await page.waitForURL("**/teacher/dashboard");
    await expect(page.getByRole("heading", { name: /Run the school day from one teaching desk/i })).toBeVisible();

    await page.goto("/demo");
    await page.getByRole("button", { name: /Admin/i }).first().click();
    await page.waitForURL("**/admin/dashboard");
    await expect(page.getByRole("heading", { name: /Run school health from a calm academic control surface/i })).toBeVisible();
});
