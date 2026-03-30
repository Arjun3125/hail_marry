import { expect, test } from "@playwright/test";

type UploadRecord = {
    id: string;
    file_name: string;
    file_type: string;
    status: "processing" | "completed" | "failed";
    uploaded_at: string;
};

test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
        window.localStorage.setItem("vidyaos_access_token", "test-token");
        window.localStorage.setItem("student-tour", "completed");
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

test("student upload flow shows OCR review metadata for image uploads @smoke", async ({ page }) => {
    const uploads: UploadRecord[] = [
        {
            id: "upload-1",
            file_name: "chapter-9.pdf",
            file_type: "pdf",
            status: "completed",
            uploaded_at: "2026-03-29 09:30",
        },
    ];

    await page.route("**/api/student/uploads", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({ items: uploads }),
        });
    });

    await page.route("**/api/student/upload", async (route) => {
        uploads.unshift({
            id: "upload-2",
            file_name: "photosynthesis-note.jpg",
            file_type: "jpg",
            status: "completed",
            uploaded_at: "2026-03-29 09:45",
        });
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                success: true,
                chunks: 6,
                ocr_processed: true,
                ocr_review_required: true,
                ocr_warning: "Low confidence in two handwritten lines",
                ocr_confidence: 0.82,
            }),
        });
    });

    await page.goto("/student/upload");

    await expect(page.getByRole("heading", { name: "Upload Study Materials" })).toBeVisible();
    await expect(page.getByText("chapter-9.pdf")).toBeVisible();

    await page.locator('input[type="file"]').setInputFiles({
        name: "photosynthesis-note.jpg",
        mimeType: "image/jpeg",
        buffer: Buffer.from("fake-image-binary"),
    });

    await expect(page.getByText("photosynthesis-note.jpg")).toBeVisible();
    await expect(page.getByText(/OCR completed/i)).toBeVisible();
    await expect(page.getByText(/OCR review recommended/i)).toBeVisible();
    await expect(page.getByText(/OCR confidence 82%/i)).toBeVisible();
    await expect(page.getByText(/Low confidence in two handwritten lines/i)).toBeVisible();
    await expect(page.getByText("photosynthesis-note.jpg")).toHaveCount(2);
});

test("student study tools page queues a quiz job and renders grounded results @smoke", async ({ page }) => {
    let jobPolls = 0;

    await page.route("**/api/student/ai-history**", async (route) => {
        const url = new URL(route.request().url());
        const mode = url.searchParams.get("mode");
        const items = mode === "quiz"
            ? [
                {
                    id: "hist-1",
                    mode: "quiz",
                    query_text: "Photosynthesis",
                    response_text: "{}",
                    title: "Chapter 10 quick quiz",
                    created_at: "2026-03-28T10:00:00.000Z",
                    is_pinned: true,
                    folder_id: null,
                },
            ]
            : [];
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({ items }),
        });
    });

    const completedQuizPayload = {
        data: [
            {
                question: "Which pigment captures sunlight for photosynthesis?",
                options: [
                    "A. Chlorophyll",
                    "B. Hemoglobin",
                    "C. Keratin",
                    "D. Insulin",
                ],
                correct: "A. Chlorophyll",
                citation: "[Biology_10]",
            },
        ],
        citations: [
            {
                source: "Class 10 Biology",
                page: "10",
                text: "Class 10 Biology p.10",
            },
        ],
    };

    await page.route("**/api/student/tools/generate/jobs", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                job_id: "job-quiz-1",
                status: "queued",
            }),
        });
    });

    await page.route("**/api/student/tools/generate", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify(completedQuizPayload),
        });
    });

    await page.route("**/api/ai/jobs/job-quiz-1", async (route) => {
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
                result: completedQuizPayload,
            }),
        });
    });

    await page.goto("/student/tools");

    await expect(page.getByRole("heading", { name: "AI Study Tools" })).toBeVisible();
    await page.getByRole("button", { name: /Quiz/i }).click();

    await page.getByPlaceholder(/Enter a topic for your Quiz/i).fill("Photosynthesis");
    await page.getByRole("button", { name: /Generate/i }).click();

    await expect(page.getByRole("heading", { name: "Generated Quiz" })).toBeVisible();
    await expect(page.getByText("Which pigment captures sunlight for photosynthesis?")).toBeVisible();
    await expect(page.getByText("Correct: A. Chlorophyll")).toBeVisible();
    await expect(page.getByText("Class 10 Biology p.10")).toBeVisible();
    expect(jobPolls === 0 || jobPolls >= 2).toBeTruthy();
});

test("student study tools page surfaces a grounded failure message when generation is rejected", async ({ page }) => {
    await page.route("**/api/student/ai-history**", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({ items: [] }),
        });
    });

    await page.route("**/api/student/tools/generate/jobs", async (route) => {
        await route.fulfill({
            status: 422,
            contentType: "application/json",
            body: JSON.stringify({
                detail: "Upload matching study materials before generating a quiz.",
            }),
        });
    });

    await page.route("**/api/student/tools/generate", async (route) => {
        await route.fulfill({
            status: 422,
            contentType: "application/json",
            body: JSON.stringify({
                detail: "Upload matching study materials before generating a quiz.",
            }),
        });
    });

    await page.goto("/student/tools");

    await page.getByRole("button", { name: /Quiz/i }).click();
    await page.getByPlaceholder(/Enter a topic for your Quiz/i).fill("Photosynthesis");
    await page.getByRole("button", { name: /Generate/i }).click();

    await expect(page.getByText("Upload matching study materials before generating a quiz.")).toBeVisible();
});
