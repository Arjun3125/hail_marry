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

test("teacher upload page handles document OCR intake and YouTube ingestion", async ({ page }) => {
    let docPolls = 0;
    let youtubePolls = 0;

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

    await page.route("**/api/teacher/upload", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                success: true,
                job_id: "doc-job-1",
                ocr_processed: true,
                ocr_review_required: true,
                ocr_warning: "Low confidence in one handwritten note.",
                ocr_confidence: 0.81,
            }),
        });
    });

    await page.route("**/api/teacher/youtube", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                success: true,
                job_id: "youtube-job-1",
            }),
        });
    });

    await page.route("**/api/ai/jobs/doc-job-1", async (route) => {
        docPolls += 1;
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify(
                docPolls === 1
                    ? { status: "running", poll_after_ms: 25 }
                    : { status: "completed", result: { chunks: 6 } },
            ),
        });
    });

    await page.route("**/api/ai/jobs/youtube-job-1", async (route) => {
        youtubePolls += 1;
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify(
                youtubePolls === 1
                    ? { status: "running", poll_after_ms: 25 }
                    : { status: "completed", result: { chunks: 12 } },
            ),
        });
    });

    await page.goto("/teacher/upload", { waitUntil: "domcontentloaded" });

    await expect(page.getByRole("heading", { name: "Bring class materials into one controlled intake flow" })).toBeVisible();

    await page.locator('input[type="file"]').setInputFiles({
        name: "photosynthesis-note.jpg",
        mimeType: "image/jpeg",
        buffer: Buffer.from("fake-image"),
    });

    await expect(page.getByText("photosynthesis-note.jpg")).toBeVisible();
    await expect(page.getByText(/OCR completed/i)).toBeVisible();
    await expect(page.getByText(/OCR review recommended/i)).toBeVisible();
    await expect(page.getByText(/OCR confidence 81%/i)).toBeVisible();

    await page.getByPlaceholder("Lecture title").fill("Cell Division Lecture");
    await page.getByPlaceholder("Paste YouTube URL...").fill("https://youtube.com/watch?v=test");
    await page.getByRole("button", { name: /Ingest Lecture/i }).click();

    await expect(page.getByText("Cell Division Lecture")).toBeVisible();
    await expect(page.getByText(/Transcript ingested \(12 chunks\)/i)).toBeVisible();

    expect(docPolls).toBeGreaterThanOrEqual(2);
    expect(youtubePolls).toBeGreaterThanOrEqual(2);
});

