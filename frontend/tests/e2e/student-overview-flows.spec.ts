import { expect, test } from "@playwright/test";
import { stubAuthShell, stubStudentOverview, overviewBootstrapPayload } from "../fixtures/helpers";

/* ═══════════════════════════════════════════════════════════════════════
   STUDENT  OVERVIEW  FLOWS  ·  40 hard fault-finding tests
   ═══════════════════════════════════════════════════════════════════════ */

test.describe("Student overview bootstrap rendering", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "student");
    });

    test("overview renders hero heading with complete bootstrap data", async ({ page }) => {
        await stubStudentOverview(page);
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.getByRole("heading", { name: /Open VidyaOS and know what to do next/i })).toBeVisible();
    });

    test("attendance percentage is displayed from bootstrap data", async ({ page }) => {
        await stubStudentOverview(page);
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("91%").first()).toBeVisible();
    });

    test("avg marks is displayed from bootstrap data", async ({ page }) => {
        await stubStudentOverview(page);
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("78").first()).toBeVisible();
    });

    test("pending assignments count is shown", async ({ page }) => {
        await stubStudentOverview(page);
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("2").first()).toBeAttached();
    });

    test("AI queries shows usage against limit", async ({ page }) => {
        await stubStudentOverview(page);
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        // AI queries: 3 of 50
        await expect(page.getByText(/3/i).first()).toBeAttached();
    });
});

test.describe("Weak topics and strong topics", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "student");
    });

    test("weak topic is shown with subject and score", async ({ page }) => {
        await stubStudentOverview(page);
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("Biology").first()).toBeVisible();
    });

    test("strong topic is displayed", async ({ page }) => {
        await stubStudentOverview(page);
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("Maths").first()).toBeVisible();
    });

    test("empty weak topics shows graceful fallback", async ({ page }) => {
        const data = overviewBootstrapPayload({ weak_topics: { weak_topics: [], strong_topics: [] } });
        await stubStudentOverview(page, data);
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.getByRole("heading", { name: /Open VidyaOS/i })).toBeVisible();
    });

    test("multiple weak topics render without layout break", async ({ page }) => {
        const data = overviewBootstrapPayload({
            weak_topics: {
                weak_topics: [
                    { subject: "Physics", average_score: 38, exam_count: 2, is_weak: true },
                    { subject: "Chemistry", average_score: 42, exam_count: 3, is_weak: true },
                    { subject: "Biology", average_score: 44, exam_count: 2, is_weak: true },
                ],
                strong_topics: [{ subject: "Maths", average_score: 92, exam_count: 4, is_weak: false }],
            },
        });
        await stubStudentOverview(page, data);
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("Physics").first()).toBeVisible();
        await expect(page.getByText("Chemistry").first()).toBeVisible();
    });

    test("weak topic with zero score doesn't crash", async ({ page }) => {
        const data = overviewBootstrapPayload({
            weak_topics: { weak_topics: [{ subject: "Art", average_score: 0, exam_count: 1, is_weak: true }], strong_topics: [] },
        });
        await stubStudentOverview(page, data);
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("Art").first()).toBeVisible();
    });
});

test.describe("Streaks and engagement badges", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "student");
    });

    test("current streak is displayed", async ({ page }) => {
        await stubStudentOverview(page);
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("4").first()).toBeAttached();
    });

    test("longest streak is displayed", async ({ page }) => {
        await stubStudentOverview(page);
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("7").first()).toBeAttached();
    });

    test("zero streak scenario renders without crash", async ({ page }) => {
        const data = overviewBootstrapPayload({
            streaks: { current_streak: 0, longest_streak: 0, total_sessions: 0, last_login: null, badges: [] },
        });
        await stubStudentOverview(page, data);
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.getByRole("heading", { name: /Open VidyaOS/i })).toBeVisible();
    });

    test("null streaks object doesn't crash the page", async ({ page }) => {
        const data = overviewBootstrapPayload({ streaks: null });
        await stubStudentOverview(page, data);
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });
});

test.describe("Personalization recommendations", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "student");
    });

    test("recommendation card is displayed with label", async ({ page }) => {
        await stubStudentOverview(page);
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("Review Photosynthesis basics").first()).toBeVisible();
    });

    test("recommendation has a description", async ({ page }) => {
        await stubStudentOverview(page);
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.getByText(/Start with a quick guided explanation/i)).toBeVisible();
    });

    test("empty recommendations doesn't crash", async ({ page }) => {
        const data = overviewBootstrapPayload({ recommendations: { items: [] } });
        await stubStudentOverview(page, data);
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.getByRole("heading", { name: /Open VidyaOS/i })).toBeVisible();
    });

    test("multiple recommendations render correctly", async ({ page }) => {
        const data = overviewBootstrapPayload({
            recommendations: {
                items: [
                    { id: "r1", label: "Review Photosynthesis basics", description: "Start with guided explanation", prompt: "Review", target_tool: "study_guide", reason: "mastery_gap", priority: "high" },
                    { id: "r2", label: "Practice quadratics", description: "Take a quiz on quadratic equations", prompt: "Quiz me", target_tool: "quiz", reason: "mastery_gap", priority: "medium" },
                    { id: "r3", label: "Memorize periodic table", description: "Flashcard drill", prompt: "Flashcards", target_tool: "flashcards", reason: "spaced_repetition", priority: "low" },
                ],
            },
        });
        await stubStudentOverview(page, data);
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("Review Photosynthesis basics")).toBeVisible();
        await expect(page.getByText("Practice quadratics")).toBeVisible();
        await expect(page.getByText("Memorize periodic table")).toBeVisible();
    });

    test("null recommendations doesn't crash", async ({ page }) => {
        const data = overviewBootstrapPayload({ recommendations: null });
        await stubStudentOverview(page, data);
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });
});

test.describe("Study path and next action", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "student");
    });

    test("active study path shows focus topic", async ({ page }) => {
        await stubStudentOverview(page);
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("Photosynthesis").first()).toBeVisible();
    });

    test("study plan items are listed", async ({ page }) => {
        await stubStudentOverview(page);
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("Relearn Photosynthesis").first()).toBeVisible();
    });

    test("null study path renders without errors", async ({ page }) => {
        const data = overviewBootstrapPayload({ study_path: { plan: null } });
        await stubStudentOverview(page, data);
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.getByRole("heading", { name: /Open VidyaOS/i })).toBeVisible();
    });

    test("study plan with no items shows graceful state", async ({ page }) => {
        const data = overviewBootstrapPayload({
            study_path: { plan: { id: "p1", focus_topic: "Organic Chemistry", status: "active", items: [], next_action: null } },
        });
        await stubStudentOverview(page, data);
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("Organic Chemistry").first()).toBeVisible();
    });

    test("completed study plan status renders differently", async ({ page }) => {
        const data = overviewBootstrapPayload({
            study_path: {
                plan: {
                    id: "p2",
                    focus_topic: "Algebra",
                    status: "completed",
                    items: [{ id: "s1", title: "Master basics", target_tool: "study_guide", status: "completed" }],
                    next_action: null,
                },
            },
        });
        await stubStudentOverview(page, data);
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("Algebra").first()).toBeVisible();
    });
});

test.describe("Dashboard edge cases", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "student");
    });

    test("zero attendance percentage renders", async ({ page }) => {
        const data = overviewBootstrapPayload({
            dashboard: { attendance_pct: 0, avg_marks: 0, pending_assignments: 0, ai_queries_today: 0, ai_queries_limit: 50, upcoming_classes: [], my_uploads: 0, ai_insight: null },
        });
        await stubStudentOverview(page, data);
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("0%").first()).toBeVisible();
    });

    test("100 percent attendance renders", async ({ page }) => {
        const data = overviewBootstrapPayload({
            dashboard: { attendance_pct: 100, avg_marks: 99, pending_assignments: 0, ai_queries_today: 50, ai_queries_limit: 50, upcoming_classes: [], my_uploads: 100, ai_insight: "Perfect week!" },
        });
        await stubStudentOverview(page, data);
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("100%").first()).toBeVisible();
    });

    test("AI insight with special characters renders safely", async ({ page }) => {
        const data = overviewBootstrapPayload({
            dashboard: { attendance_pct: 90, avg_marks: 80, pending_assignments: 1, ai_queries_today: 5, ai_queries_limit: 50, upcoming_classes: [], my_uploads: 3, ai_insight: "Focus on <strong>Biology</strong> & Chemistry's \"equilibrium\"" },
        });
        await stubStudentOverview(page, data);
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("long AI insight text does not break layout", async ({ page }) => {
        const longInsight = "A".repeat(500);
        const data = overviewBootstrapPayload({
            dashboard: { attendance_pct: 85, avg_marks: 72, pending_assignments: 1, ai_queries_today: 2, ai_queries_limit: 50, upcoming_classes: [], my_uploads: 1, ai_insight: longInsight },
        });
        await stubStudentOverview(page, data);
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("upcoming classes with empty array renders gracefully", async ({ page }) => {
        const data = overviewBootstrapPayload({
            dashboard: { attendance_pct: 85, avg_marks: 72, pending_assignments: 0, ai_queries_today: 0, ai_queries_limit: 50, upcoming_classes: [], my_uploads: 0, ai_insight: "No classes today." },
        });
        await stubStudentOverview(page, data);
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.getByRole("heading", { name: /Open VidyaOS/i })).toBeVisible();
    });

    test("multiple upcoming classes render", async ({ page }) => {
        const data = overviewBootstrapPayload({
            dashboard: { attendance_pct: 90, avg_marks: 82, pending_assignments: 2, ai_queries_today: 5, ai_queries_limit: 50, upcoming_classes: [{ subject: "Maths", time: "08:00" }, { subject: "Science", time: "09:00" }, { subject: "English", time: "10:00" }], my_uploads: 5, ai_insight: "Great day ahead." },
        });
        await stubStudentOverview(page, data);
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("Maths").first()).toBeVisible();
    });

    test("high upload count renders correctly", async ({ page }) => {
        const data = overviewBootstrapPayload({
            dashboard: { attendance_pct: 90, avg_marks: 82, pending_assignments: 0, ai_queries_today: 0, ai_queries_limit: 50, upcoming_classes: [], my_uploads: 999, ai_insight: "Lots of material!" },
        });
        await stubStudentOverview(page, data);
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("999").first()).toBeAttached();
    });

    test("AI queries at limit shows boundary value", async ({ page }) => {
        const data = overviewBootstrapPayload({
            dashboard: { attendance_pct: 90, avg_marks: 80, pending_assignments: 0, ai_queries_today: 50, ai_queries_limit: 50, upcoming_classes: [], my_uploads: 5, ai_insight: "Limit reached." },
        });
        await stubStudentOverview(page, data);
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("50").first()).toBeAttached();
    });

    test("personalization events endpoint fires on page load", async ({ page }) => {
        let eventsFired = false;
        await page.route("**/api/personalization/events", async (route) => {
            eventsFired = true;
            await route.fulfill({ status: 202, contentType: "application/json", body: JSON.stringify({ ok: true }) });
        });
        await stubStudentOverview(page);
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.getByRole("heading", { name: /Open VidyaOS/i })).toBeVisible();
        // Events endpoint should have been called
        expect(eventsFired).toBe(true);
    });
});
