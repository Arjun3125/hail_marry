import { expect, test } from "@playwright/test";

test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
        window.localStorage.setItem("vidyaos_access_token", "test-token");
    });

    // Set demo role cookie for teacher user
    await page.context().addCookies([{
        name: 'demo_role',
        value: 'teacher',
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

test("teacher assessment generator queues a job and renders the completed draft", async ({ page }) => {
    let jobPolls = 0;

    await page.route("**/api/teacher/classes", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify([
                {
                    id: "class-1",
                    name: "Class 10 A",
                    subjects: [
                        { id: "subject-1", name: "Biology" },
                        { id: "subject-2", name: "Chemistry" },
                    ],
                },
            ]),
        });
    });

    await page.route("**/api/teacher/generate-assessment", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                job_id: "assessment-job-1",
                status: "queued",
            }),
        });
    });

    await page.route("**/api/ai/jobs/assessment-job-1", async (route) => {
        jobPolls += 1;
        if (jobPolls === 1) {
            await route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify({
                    status: "running",
                    poll_after_ms: 25,
                }),
            });
            return;
        }

        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                status: "completed",
                result: {
                    assessment: "1. Define photosynthesis.\n2. Explain the role of chlorophyll.",
                },
            }),
        });
    });

    await page.goto("/teacher/generate-assessment", { waitUntil: "domcontentloaded" });

    await expect(page.getByRole("heading", { name: "Generate Assessment" })).toBeVisible();
    await page.getByPlaceholder(/Photosynthesis, Quadratic Equations/i).fill("Photosynthesis");
    await page.getByRole("button", { name: /Generate Assessment/i }).click();

    await expect(page.getByRole("heading", { name: /Generated Assessment/i })).toBeVisible();
    await expect(page.getByText("1. Define photosynthesis.")).toBeVisible();
    await expect(page.getByText("2. Explain the role of chlorophyll.")).toBeVisible();
    expect(jobPolls).toBeGreaterThanOrEqual(2);
});

