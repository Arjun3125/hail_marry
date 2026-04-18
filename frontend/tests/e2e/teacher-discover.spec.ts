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

test("teacher discover page searches sources and ingests a result", async ({ page }) => {
    let jobPolls = 0;

    await page.route("**/api/ai/discover-sources", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                results: [
                    {
                        title: "NCERT Photosynthesis Revision Notes",
                        url: "https://example.edu/photosynthesis",
                        snippet: "A concise revision guide for photosynthesis with diagrams, terminology, and checkpoint questions.",
                    },
                ],
            }),
        });
    });

    await page.route("**/api/ai/ingest-url", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                job_id: "discover-job-1",
                status: "queued",
            }),
        });
    });

    await page.route("**/api/ai/jobs/discover-job-1", async (route) => {
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
                    chunks_created: 7,
                },
            }),
        });
    });

    await page.goto("/teacher/discover", { waitUntil: "domcontentloaded" });

    await expect(page.getByRole("heading", { name: "Find relevant external sources before you add them to class knowledge" })).toBeVisible();
    await page.getByPlaceholder(/NCERT Class 10 Photosynthesis/i).fill("NCERT Photosynthesis");
    await page.getByRole("button", { name: /Search Sources/i }).click();

    await expect(page.getByRole("heading", { name: "NCERT Photosynthesis Revision Notes" })).toBeVisible();
    await page.getByRole("button", { name: /Add To Knowledge Base/i }).click();

    await expect(page.getByText(/Source indexed/i)).toBeVisible();
    await expect(page.getByText(/7 chunks added to the knowledge base/i)).toBeVisible();
    expect(jobPolls).toBeGreaterThanOrEqual(2);
});

