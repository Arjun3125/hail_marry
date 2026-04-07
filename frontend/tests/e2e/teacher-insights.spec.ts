import { expect, test } from "@playwright/test";

test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
        window.localStorage.setItem("vidyaos_access_token", "test-token");
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
});

test("teacher insights page renders class analytics and recommendations", async ({ page }) => {
    await page.route("**/api/teacher/insights", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                insights: [
                    {
                        class: "Class 10 A",
                        subjects: [
                            { subject: "Biology", avg_pct: 48, is_weak: true },
                            { subject: "Chemistry", avg_pct: 76, is_weak: false },
                        ],
                        weak_topics: ["Photosynthesis", "Cell Division"],
                        recommendation: "Run a short remediation block on photosynthesis before the next assessment.",
                    },
                ],
            }),
        });
    });

    await page.goto("/teacher/insights");

    await expect(page.getByRole("heading", { name: "AI Class Insights" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Class 10 A" })).toBeVisible();
    await expect(page.getByText("Biology")).toBeVisible();
    await expect(page.getByText("Photosynthesis", { exact: true })).toBeVisible();
    await expect(page.getByText(/Run a short remediation block on photosynthesis/i)).toBeVisible();
});
