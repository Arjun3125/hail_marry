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
});

test("student mascot page creates a notebook and opens AI Studio", async ({ page }) => {
    await page.route("**/api/mascot/suggestions**", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                suggestions: ["Create a Biology notebook", "Open AI Studio", "Generate flashcards for photosynthesis"],
            }),
        });
    });

    await page.route("**/api/mascot/message", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                reply_text: "Created notebook 'Biology Chapter 10'.",
                intent: "notebook_create",
                normalized_message: "Create notebook for Biology Chapter 10",
                actions: [
                    {
                        kind: "notebook_create",
                        status: "completed",
                        payload: { name: "Biology Chapter 10", notebook_id: "nb-1" },
                        result_summary: "Created notebook 'Biology Chapter 10'.",
                    },
                ],
                artifacts: [],
                navigation: { href: "/student/ai-studio", target: "ai_studio", notebook_id: "nb-1" },
                requires_confirmation: false,
                confirmation_id: null,
                follow_up_suggestions: ["Generate flashcards from Biology Chapter 10", "Create a flowchart for Biology Chapter 10", "Open Biology Chapter 10 in AI Studio"],
                notebook_id: "nb-1",
                trace_id: "mascot-trace-1",
            }),
        });
    });

    await page.route("**/api/notebooks", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                items: [{ id: "nb-1", name: "Biology Chapter 10", subject: "Biology", color: "#2563eb" }],
                total: 1,
            }),
        });
    });

    await page.goto("/student/assistant");
    await expect(page.getByText("Vidya Mascot")).toBeVisible();
    await expect(page.getByText("Student Copilot")).toBeVisible();
    await expect(page.getByText("Plan, learn, and build study outputs from one place.")).toBeVisible();
    await expect(page.getByText("Context: Assistant")).toBeVisible();
    await expect(page.getByRole("button", { name: "Create a Biology notebook" })).toBeVisible();

    await page.getByPlaceholder(/Tell the mascot what you want to do/i).fill("Create notebook for Biology Chapter 10");
    await page.locator("button[type='submit']").click();

    await expect(page.getByText("Created notebook 'Biology Chapter 10'.").first()).toBeVisible();
    await expect(page.getByText("notebook create")).toBeVisible();
    await expect(page.getByText("Next steps")).toBeVisible();
    await expect(page.getByText("Notebook: Biology Chapter 10")).toBeVisible();
    await page.getByRole("button", { name: /Open ai studio/i }).last().click();
    await expect(page).toHaveURL(/\/student\/ai-studio/);
});

test("student upload layout shows floating mascot launcher", async ({ page }) => {
    await page.route("**/api/student/uploads", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({ items: [] }),
        });
    });
    await page.route("**/api/mascot/suggestions**", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({ suggestions: ["Create a notebook for these uploads"] }),
        });
    });

    await page.goto("/student/upload");
    await page.getByLabel("Open mascot assistant").click();
    await expect(page.getByText("Vidya Mascot")).toBeVisible();
});

test("teacher classes layout shows floating mascot launcher", async ({ page }) => {
    await page.route("**/api/teacher/classes", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify([
                { id: "class-1", name: "Class 10 A", grade: "10", students: [], subjects: [] },
            ]),
        });
    });
    await page.route("**/api/mascot/suggestions**", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({ suggestions: ["Import student roster from image", "Review extracted student rows", "Generate a Biology assessment"] }),
        });
    });

    await page.goto("/teacher/classes");
    await page.getByLabel("Open mascot assistant").click();
    await expect(page.getByText("Vidya Mascot")).toBeVisible();
    await expect(page.getByText("Context: Student Onboarding")).toBeVisible();
    await expect(page.getByRole("button", { name: "Import student roster from image" })).toBeVisible();
});

test("admin setup wizard layout shows floating mascot launcher", async ({ page }) => {
    await page.route("**/api/mascot/suggestions**", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({ suggestions: ["Show setup progress", "Import teachers", "Import students"] }),
        });
    });

    await page.goto("/admin/setup-wizard");
    await page.getByLabel("Open mascot assistant").click();
    await expect(page.getByText("Vidya Mascot")).toBeVisible();
    await expect(page.getByText("Context: Setup Step: school")).toBeVisible();
    await expect(page.getByRole("button", { name: "Show setup progress" })).toBeVisible();
});

test("admin mascot page can navigate to setup wizard", async ({ page }) => {
    await page.route("**/api/mascot/suggestions**", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({ suggestions: ["Open setup wizard", "Review WhatsApp release gate"] }),
        });
    });
    await page.route("**/api/mascot/message", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                reply_text: "Opening onboarding.",
                intent: "navigate",
                normalized_message: "Open setup wizard",
                actions: [{ kind: "navigate", status: "completed", payload: { href: "/admin/setup-wizard" }, result_summary: "Prepared navigation to /admin/setup-wizard." }],
                artifacts: [],
                navigation: { href: "/admin/setup-wizard", target: "onboarding" },
                requires_confirmation: false,
                confirmation_id: null,
                follow_up_suggestions: ["Review WhatsApp release gate"],
                notebook_id: null,
                trace_id: "mascot-admin-1",
            }),
        });
    });

    await page.goto("/admin/assistant");
    await page.getByPlaceholder(/Tell the mascot what you want to do/i).fill("Open setup wizard");
    await page.locator("button[type='submit']").click();
    await expect(page).toHaveURL(/\/admin\/setup-wizard/);
});

test("student mascot can upload a file and ask a follow-up", async ({ page }) => {
    await page.route("**/api/mascot/suggestions**", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                suggestions: ["Summarize this upload", "Generate flashcards from this notebook"],
            }),
        });
    });
    await page.route("**/api/mascot/upload", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                reply_text: "Ingested notes.pdf into Biology. Indexed 5 chunks.\n\nHere is a summary of the uploaded notes.",
                intent: "query",
                normalized_message: "Summarize this upload",
                actions: [
                    {
                        kind: "content_ingest",
                        status: "completed",
                        payload: { document_id: "doc-1", file_name: "notes.pdf", chunks: 5 },
                        result_summary: "Ingested notes.pdf into Biology. Indexed 5 chunks.",
                    },
                    {
                        kind: "query",
                        status: "completed",
                        payload: { mode: "qa", topic: "Summarize this upload" },
                        result_summary: "Answered using qa mode.",
                    },
                ],
                artifacts: [
                    { document_id: "doc-1", file_name: "notes.pdf", chunks: 5, ocr_processed: false },
                    { tool: "qa", answer: "Here is a summary of the uploaded notes." },
                ],
                requires_confirmation: false,
                confirmation_id: null,
                follow_up_suggestions: ["Generate flashcards", "Create a flowchart"],
                notebook_id: "nb-upload",
                trace_id: "mascot-upload-1",
            }),
        });
    });

    await page.goto("/student/assistant");
    await expect(page.getByText("PDF, DOCX, PPTX, XLSX, or image")).toBeVisible();
    await page.getByLabel("Attach file to mascot").setInputFiles({
        name: "notes.pdf",
        mimeType: "application/pdf",
        buffer: Buffer.from("%PDF-1.4 test"),
    });
    await expect(page.getByText("notes.pdf")).toBeVisible();
    await expect(page.getByText("PDF • 1 KB • Ready to ingest")).toBeVisible();
    await expect(page.getByText("Ask after upload or ingest only")).toBeVisible();
    await page.getByPlaceholder(/Tell the mascot what you want to do/i).fill("Summarize this upload");
    await page.locator("button[type='submit']").click();

    await expect(page.getByText("Here is a summary of the uploaded notes.", { exact: true })).toBeVisible();
    await expect(page.getByText("Ingested notes.pdf into Biology. Indexed 5 chunks.", { exact: true })).toBeVisible();
    await expect(page.getByText("Indexed notes.pdf")).toBeVisible();
    await expect(page.getByText("5 chunks", { exact: true })).toBeVisible();
    await expect(page.getByRole("button", { name: "Generate flashcards", exact: true })).toBeVisible();
});
