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

    await page.route("**/api/personalization/events", async (route) => {
        await route.fulfill({
            status: 202,
            contentType: "application/json",
            body: JSON.stringify({ ok: true }),
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

    await page.route("**/api/mascot/suggestions**", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                suggestions: [
                    "Summarize my latest upload",
                    "Create a quiz from this material",
                ],
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

    await expect(page.getByRole("paragraph").filter({ hasText: /^photosynthesis-note\.jpg$/ })).toBeVisible();
    await expect(page.getByText(/OCR completed/i)).toBeVisible();
    await expect(page.getByText(/OCR review recommended/i)).toBeVisible();
    await expect(page.getByText(/OCR confidence 82%/i)).toBeVisible();
    await expect(page.getByText(/Low confidence in two handwritten lines/i)).toBeVisible();
    await expect(page.getByRole("heading", { name: /Your upload is ready/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /Ask and understand/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /Practice immediately/i })).toBeVisible();
    await page.getByRole("link", { name: /Ask and understand/i }).click();
    await expect(page).toHaveURL(/\/student\/assistant\?prompt=/);
    await expect(page.getByPlaceholder("Tell the mascot what you want to do...")).toHaveValue(
        'Summarize my latest upload "photosynthesis-note.jpg" and tell me the best next study step.',
    );
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

test("student overview shows the personalized study path and routes into mascot", async ({ page }) => {
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
                    items: [
                        { id: "guide", title: "Relearn Photosynthesis", target_tool: "study_guide", status: "pending" },
                        { id: "flashcards", title: "Memorize weak concepts", target_tool: "flashcards", status: "pending" },
                        { id: "quiz", title: "Check understanding", target_tool: "quiz", status: "pending" },
                    ],
                    next_action: {
                        id: "guide",
                        title: "Relearn Photosynthesis",
                        target_tool: "study_guide",
                        status: "pending",
                    },
                },
            }),
        });
    });

    await page.goto("/student/overview");

    await expect(page.getByRole("heading", { name: "Continue learning path" })).toBeVisible();
    await expect(page.getByText("Focus topic: Photosynthesis")).toBeVisible();
    await expect(page.getByText("Relearn Photosynthesis").first()).toBeVisible();
    await expect(page.getByText("Step 1")).toBeVisible();
    await page.getByRole("link", { name: /Open mascot/i }).click();
    await expect(page).toHaveURL(/\/student\/assistant/);
});

test("legacy student AI route redirects into AI Studio and restores history context", async ({ page }) => {
    await page.route("**/api/notebooks", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                items: [
                    {
                        id: "nb-1",
                        name: "Biology",
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

    await page.route("**/api/student/ai-history/legacy-1", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                id: "legacy-1",
                mode: "qa",
                query_text: "Explain photosynthesis",
                response_text: "Photosynthesis converts light energy into chemical energy.",
            }),
        });
    });

    await page.route("**/api/personalization/recommendations**", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                items: [
                    { id: "rec-legacy-1", prompt: "Quiz me on photosynthesis" },
                ],
            }),
        });
    });

    await page.goto("/student/ai?history=legacy-1&mode=quiz");

    await expect(page).toHaveURL(/\/student\/ai-studio\?.*(history=legacy-1.*tool=quiz|tool=quiz.*history=legacy-1)/);
    await expect(page.locator(".tool-rail").getByText("AI Studio")).toBeVisible();
    await expect(page.getByRole("paragraph").filter({ hasText: /^Explain photosynthesis$/ })).toBeVisible();
    await expect(page.getByText("Photosynthesis converts light energy into chemical energy.")).toBeVisible();
});

test("AI Studio context hints use personalized recommendations and seed the composer", async ({ page }) => {
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
        const url = new URL(route.request().url());
        const surface = url.searchParams.get("current_surface");
        if (surface === "ai_studio_context_panel") {
            await route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify({
                    items: [
                        {
                            id: "rec-context-1",
                            label: "Relearn photosynthesis basics",
                            description: "Start with a guided explanation before practicing.",
                            prompt: "Explain photosynthesis simply and then quiz me.",
                            target_tool: "study_guide",
                            priority: "high",
                        },
                    ],
                }),
            });
            return;
        }

        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                items: [
                    {
                        id: "rec-starter-1",
                        prompt: "Summarize my Biology Chapter 10 notebook and tell me the weakest concept first.",
                    },
                ],
            }),
        });
    });

    await page.goto("/student/ai-studio");

    await page.getByRole("button", { name: /Hints/i }).click();
    await expect(page.getByText("Relearn photosynthesis basics")).toBeVisible();
    await page.getByRole("button", { name: /Relearn photosynthesis basics/i }).click();
    await expect(page).toHaveURL(/\/student\/ai-studio\?.*tool=study_guide.*prompt=/);
    await expect(page.getByPlaceholder(/Enter a topic for a comprehensive study guide/i)).toHaveValue(
        "Explain photosynthesis simply and then quiz me.",
    );
});
