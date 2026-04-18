import { Page } from "@playwright/test";

/* ─── Branding ─── */
export function brandingPayload() {
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

export async function stubBranding(page: Page) {
    await page.route("**/api/branding/config", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify(brandingPayload()),
        });
    });
}

/* ─── Auth shell ─── */
export async function stubAuthShell(page: Page, role: "student" | "teacher" | "admin" | "parent" = "student") {
    await page.addInitScript(({ role: r }) => {
        window.localStorage.setItem("vidyaos_access_token", `test-token-${r}`);
        ["student", "teacher", "admin", "parent"].forEach((p) => {
            window.localStorage.setItem(`${p}-tour`, "completed");
            window.localStorage.setItem(
                `${p}-onboarding`,
                JSON.stringify({
                    "profile-ready": true,
                    "upload-material": true,
                    "ask-ai": true,
                    "read-timetable": true,
                    "setup-identity": true,
                    "setup-structure": true,
                    "onboard-teachers": true,
                }),
            );
        });
        if (r === "student") {
            window.localStorage.setItem("student-ai-studio-intent", "understand_topic");
        }
    }, { role });

    await stubBranding(page);

    await page.route("**/api/auth/me", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({ role, userId: `${role}-001`, name: `Test ${role[0].toUpperCase()}${role.slice(1)}` }),
        });
    });

    await page.route("**/api/personalization/events", async (route) => {
        await route.fulfill({ status: 202, contentType: "application/json", body: JSON.stringify({ ok: true }) });
    });
}

/* ─── Student dashboard data factory ─── */
export function studentDashboardPayload(overrides: Record<string, unknown> = {}) {
    return {
        attendance_pct: 91,
        avg_marks: 78,
        pending_assignments: 2,
        ai_queries_today: 3,
        ai_queries_limit: 50,
        upcoming_classes: [{ subject: "Biology", time: "09:00" }],
        my_uploads: 4,
        ai_insight: "Focus on photosynthesis fundamentals.",
        ...overrides,
    };
}

/* ─── Student overview-bootstrap factory ─── */
export function overviewBootstrapPayload(overrides: Record<string, unknown> = {}) {
    return {
        dashboard: studentDashboardPayload(),
        weak_topics: {
            weak_topics: [{ subject: "Biology", average_score: 46, exam_count: 3, is_weak: true }],
            strong_topics: [{ subject: "Maths", average_score: 88, exam_count: 4, is_weak: false }],
        },
        streaks: {
            current_streak: 4,
            longest_streak: 7,
            total_sessions: 12,
            last_login: "2026-03-31T08:00:00.000Z",
            badges: [],
        },
        recommendations: {
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
        },
        study_path: {
            plan: {
                id: "plan-1",
                focus_topic: "Photosynthesis",
                status: "active",
                items: [
                    { id: "guide", title: "Relearn Photosynthesis", target_tool: "study_guide", status: "pending" },
                    { id: "flashcards", title: "Memorize weak concepts", target_tool: "flashcards", status: "pending" },
                    { id: "quiz", title: "Check understanding", target_tool: "quiz", status: "pending" },
                ],
                next_action: {
                    id: "guide",
                    title: "Relearn Photosynthesis",
                    target_tool: "study_guide",
                    prompt: "Explain photosynthesis simply and then quiz me.",
                    status: "pending",
                },
            },
        },
        ...overrides,
    };
}

/* ─── Teacher dashboard factory ─── */
export function teacherDashboardPayload(overrides: Record<string, unknown> = {}) {
    return {
        classes: [
            { id: "class-1", name: "Class 10 A", students: 32, avg_attendance: 92, avg_marks: 78 },
            { id: "class-2", name: "Class 9 B", students: 28, avg_attendance: 88, avg_marks: 74 },
        ],
        today_classes: [
            { class_id: "class-1", class_name: "Class 10 A", subject: "Biology", start_time: "09:00:00", end_time: "09:45:00" },
        ],
        pending_reviews: 4,
        open_assignments: 3,
        ...overrides,
    };
}

/* ─── Admin dashboard data ─── */
export function adminDashboardPayload(overrides: Record<string, unknown> = {}) {
    return {
        total_students: 120,
        total_teachers: 14,
        total_parents: 96,
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
        monthly_trends: [],
        complaint_health: { resolution_rate_pct: 88 },
        latest_milestones: {
            last_ai_query_at: "2026-03-30T08:15:00Z",
            last_complaint_at: "2026-03-30T07:45:00Z",
            last_resolved_complaint_at: "2026-03-30T08:00:00Z",
            last_attendance_marked_at: "2026-03-30T08:05:00Z",
        },
        ...overrides,
    };
}

export function adminBootstrapPayload(overrides: Record<string, unknown> = {}) {
    return {
        dashboard: adminDashboardPayload(),
        security: [],
        whatsapp_snapshot: {
            analytics: { total_messages: 84, unique_users: 12 },
            derived_rates: { visible_failure_pct: 2.38, routing_failure_pct: 4.76, duplicate_inbound_pct: 2.38, outbound_retryable_failure_pct: 2.38 },
        },
        mascot_snapshot: {
            analytics: { total_actions: 126, unique_users: 18 },
            derived_rates: { interpretation_failure_pct: 1.64, execution_failure_pct: 2.65, upload_failure_pct: 6.67, overall_failure_pct: 2.84 },
        },
        ...overrides,
    };
}

/* ─── Parent dashboard factory ─── */
export function parentDashboardPayload(overrides: Record<string, unknown> = {}) {
    return {
        child: { id: "student-1", name: "Aarav Sharma", email: "aarav@example.com", class: "10-A" },
        attendance_pct: 94,
        avg_marks: 82,
        pending_assignments: 1,
        latest_mark: { subject: "Biology", exam: "Unit Test 3", percentage: 84, date: "2026-03-30" },
        next_class: { day: 1, start_time: "09:00", end_time: "09:45", subject: "Biology" },
        ...overrides,
    };
}

/* ─── Common route stubs ─── */
export async function stubStudentOverview(page: Page, payload?: Record<string, unknown>) {
    await page.context().addCookies([{ name: "e2e_ssr_bypass", value: "1", domain: "localhost", path: "/" }]);
    const data = payload ?? overviewBootstrapPayload();
    await page.route("**/api/student/overview-bootstrap**", async (route) => {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(data) });
    });
    await page.route("**/api/student/dashboard", async (route) => {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify((data as Record<string, unknown>).dashboard ?? studentDashboardPayload()) });
    });
    await page.route("**/api/student/weak-topics", async (route) => {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify((data as Record<string, unknown>).weak_topics ?? { weak_topics: [], strong_topics: [] }) });
    });
    await page.route("**/api/student/streaks", async (route) => {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify((data as Record<string, unknown>).streaks ?? { current_streak: 0, longest_streak: 0, total_sessions: 0, badges: [] }) });
    });
    await page.route("**/api/personalization/recommendations**", async (route) => {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify((data as Record<string, unknown>).recommendations ?? { items: [] }) });
    });
    await page.route("**/api/personalization/study-path**", async (route) => {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify((data as Record<string, unknown>).study_path ?? { plan: null }) });
    });
    await page.route("**/api/mascot/greeting**", async (route) => {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ greeting: "Good morning!", suggestion: "Check your dashboard" }) });
    });
    await page.route("**/api/mascot/message**", async (route) => {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ reply: "I'm here to help!" }) });
    });
}

export async function stubAdminDashboard(page: Page) {
    await page.context().addCookies([{ name: "e2e_ssr_bypass", value: "1", domain: "localhost", path: "/" }]);
    await page.route("**/api/admin/dashboard-bootstrap**", async (route) => {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(adminBootstrapPayload()) });
    });
    await page.route("**/api/admin/dashboard", async (route) => {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(adminDashboardPayload()) });
    });
    await page.route("**/api/admin/security", async (route) => {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify([]) });
    });
    /* Mock mascot greeting/message endpoints used by MascotGreetingCard */
    await page.route("**/api/mascot/greeting**", async (route) => {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ greeting: "Good morning!", suggestion: "Check your dashboard" }) });
    });
    await page.route("**/api/mascot/message**", async (route) => {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ reply: "I'm here to help!" }) });
    });
    await page.route("**/api/whatsapp/release-gate-snapshot**", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                generated_at: "2026-03-30T03:30:00Z",
                period_days: 7,
                analytics: { total_messages: 84, inbound: 42, outbound: 42, unique_users: 12, avg_latency_ms: 920 },
                release_gate_metrics: { duplicate_inbound_total: 1, routing_failure_total: 2, visible_failure_total: 1, outbound_retryable_failure_total: 1, upload_ingest_failure_total: 0, link_ingest_failure_total: 0 },
                derived_rates: { duplicate_inbound_pct: 2.38, routing_failure_pct: 4.76, visible_failure_pct: 2.38, outbound_retryable_failure_pct: 2.38 },
            }),
        });
    });
    await page.route("**/api/mascot/release-gate-snapshot**", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                generated_at: "2026-03-30T03:30:00Z",
                period_days: 7,
                analytics: { total_actions: 126, unique_users: 18 },
                release_gate_metrics: { interpretation_success_total: 120, interpretation_failure_total: 2, execution_success_total: 110, execution_failure_total: 3, confirmation_success_total: 8, confirmation_failure_total: 1, confirmation_cancelled_total: 2, upload_success_total: 14, upload_failure_total: 1 },
                derived_rates: { interpretation_failure_pct: 1.64, execution_failure_pct: 2.65, upload_failure_pct: 6.67, confirmation_failure_pct: 9.09, overall_failure_pct: 2.84 },
                active_alerts: [],
            }),
        });
    });
}

export async function stubTeacherDashboard(page: Page) {
    await page.context().addCookies([{ name: "e2e_ssr_bypass", value: "1", domain: "localhost", path: "/" }]);
    await page.route("**/api/teacher/dashboard", async (route) => {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(teacherDashboardPayload()) });
    });
    await page.route("**/api/mascot/greeting**", async (route) => {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ greeting: "Good morning!", suggestion: "Check your dashboard" }) });
    });
    await page.route("**/api/mascot/message**", async (route) => {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ reply: "I'm here to help!" }) });
    });
}

export async function stubParentDashboard(page: Page, overrides: Record<string, unknown> = {}) {
    await page.context().addCookies([{ name: "e2e_ssr_bypass", value: "1", domain: "localhost", path: "/" }]);
    await page.route("**/api/parent/dashboard", async (route) => {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(parentDashboardPayload(overrides)) });
    });
    await page.route("**/api/parent/ai-insights**", async (route) => {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ insights: [] }) });
    });
    await page.route("**/api/mascot/greeting**", async (route) => {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ greeting: "Good morning!", suggestion: "Check your dashboard" }) });
    });
    await page.route("**/api/mascot/message**", async (route) => {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ reply: "I'm here to help!" }) });
    });
}

export async function stubStudentDashboard(page: Page, overrides: Record<string, unknown> = {}) {
    await page.context().addCookies([{ name: "e2e_ssr_bypass", value: "1", domain: "localhost", path: "/" }]);
    await page.route("**/api/student/dashboard", async (route) => {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(studentDashboardPayload(overrides)) });
    });
    await page.route("**/api/mascot/greeting**", async (route) => {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ greeting: "Good morning!", suggestion: "Check your dashboard" }) });
    });
    await page.route("**/api/mascot/message**", async (route) => {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ reply: "I'm here to help!" }) });
    });
}

export async function stubMascotSuggestions(page: Page, suggestions: string[] = ["Summarize my notes", "Create a quiz"]) {
    await page.route("**/api/mascot/suggestions**", async (route) => {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ suggestions }) });
    });
}

export async function stubNotebooks(page: Page, items: Record<string, unknown>[] = []) {
    await page.route("**/api/notebooks", async (route) => {
        if (route.request().method() === "GET") {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items, total: items.length }) });
        } else {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ id: "nb-new", name: "New Notebook" }) });
        }
    });
}

export async function stubAiHistory(page: Page, items: Record<string, unknown>[] = []) {
    await page.route("**/api/student/ai-history**", async (route) => {
        const url = new URL(route.request().url());
        const id = url.pathname.match(/\/api\/student\/ai-history\/([^/]+)$/)?.[1];
        if (id && route.request().method() === "GET") {
            const item = items.find((i) => (i as { id: string }).id === id) ?? { id, mode: "qa", query_text: "Q", response_text: "A" };
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(item) });
        } else {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items }) });
        }
    });
}
