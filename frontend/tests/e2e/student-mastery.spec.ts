import { expect, test } from "@playwright/test";

test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
        window.localStorage.setItem("vidyaos_access_token", "test-token");
    });

    // Set demo role cookie for student user
    await page.context().addCookies([{
        name: 'demo_role',
        value: 'student',
        domain: 'localhost',
        path: '/',
    }]);

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
});

test("student mastery map renders live sub-topic signal", async ({ page }) => {
    await page.route("**/api/student/mastery", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                summary: {
                    attendance_pct: 83.5,
                    absent_streak: 1,
                    overall_score_pct: 66,
                    exam_readiness_pct: 71,
                    current_streak_days: 9,
                    total_reviews_completed: 14,
                    last_review_at: "2026-04-05T08:00:00.000Z",
                    strongest_subject: "Biology",
                    weakest_subject: "Chemistry",
                    highest_risk: "medium",
                    dropout_risk: "low",
                    academic_risk: "medium",
                    fee_risk: "low",
                },
                subject_mastery: [
                    { subject: "Biology", score: 44, fullMark: 100 },
                    { subject: "Chemistry", score: 81, fullMark: 100 },
                ],
                focus_topics: [
                    {
                        topic: "Photosynthesis",
                        subject: "Biology",
                        mastery_score: 44,
                        confidence_score: 0.61,
                        review_due_at: "2026-04-06T08:00:00.000Z",
                        last_evidence_type: "quiz_completed",
                        last_evidence_score: 44,
                        updated_at: "2026-04-06T07:00:00.000Z",
                        concepts: [
                            { concept: "chlorophyll", mastery_score: 39, confidence_score: 0.57 },
                            { concept: "stomata", mastery_score: 52, confidence_score: 0.6 },
                        ],
                    },
                    {
                        topic: "Chemical Bonding",
                        subject: "Chemistry",
                        mastery_score: 81,
                        confidence_score: 0.72,
                        review_due_at: "2026-04-10T08:00:00.000Z",
                        last_evidence_type: "review_completed",
                        last_evidence_score: 5,
                        updated_at: "2026-04-06T08:00:00.000Z",
                        concepts: [{ concept: "ionic", mastery_score: 76, confidence_score: 0.7 }],
                    },
                ],
                insights: {
                    tracked_topics: 2,
                    low_mastery_topics: 1,
                    due_reviews: 1,
                    strongest_topic: "Chemical Bonding",
                    weakest_topic: "Photosynthesis",
                },
                recommended_actions: ["Photosynthesis"],
            }),
        });
    });

    await page.goto("/student/mastery", { waitUntil: "domcontentloaded" });

    await expect(page.getByRole("heading", { name: /real mastery signal/i })).toBeVisible();
    await expect(page.getByRole("heading", { name: /subject mastery radar/i })).toBeVisible();
    await expect(page.getByRole("heading", { name: /sub-topic focus matrix/i })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Photosynthesis" })).toBeVisible();
    await expect(page.getByText("chlorophyll")).toBeVisible();
    await expect(page.getByText("Confidence 57%")).toBeVisible();
    await expect(page.getByText("Needs attention").first()).toBeVisible();
});

