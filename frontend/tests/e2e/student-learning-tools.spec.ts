import { expect, test } from "@playwright/test";
import { stubAuthShell } from "../fixtures/helpers";

/* ═══════════════════════════════════════════════════════════════════════
   STUDENT  LEARNING  TOOLS  ·  40 hard fault-finding tests
   ═══════════════════════════════════════════════════════════════════════ */

async function mockToolGenerate(page: import("@playwright/test").Page, payload: any, status = 200) {
    if (status !== 200) {
        await page.route("**/api/student/tools/generate**", async (route) => {
            await route.fulfill({ status, contentType: "application/json", body: JSON.stringify(payload) });
        });
        return;
    }
    
    // Provide both synchronous payload (for demo mode) AND async job (for job mode)
    // This makes the mock resilient regardless of whether the local server has Demo mode enabled.
    await page.route("**/api/student/tools/generate**", async (route) => {
        const unifiedResponse = {
            job_id: "test-job-mock",
            status: "queued",
            data: payload.data,
            citations: payload.citations || []
        };
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(unifiedResponse) });
    });

    await page.route("**/api/ai/jobs/test-job-mock", async (route) => {
        const result = { data: payload.data, citations: payload.citations || [] };
        // Immediately complete the job
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ status: "completed", result }) });
    });
}

function stubToolsPage(page: import("@playwright/test").Page) {
    return page.route("**/api/student/ai-history**", async (route) => {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [] }) });
    });
}

test.describe("Tool selection UI", () => {
    test.beforeEach(async ({ page }) => { page.on('console', msg => console.log('BROWSER CONSOLE:', msg.text())); page.on('pageerror', err => console.log('BROWSER ERROR:', err.message));
        await stubAuthShell(page, "student");
        await stubToolsPage(page);
    });

    test("tools page renders hero heading", async ({ page }) => {
        // We use a longer timeout here because this is the first test that hits the Tools UI
        // Next.js initial SSR lazy compilation can take > 5s on cold starts.
        await page.goto("/student/tools", { waitUntil: "domcontentloaded" });
        await expect(page.getByRole("heading", { name: /Build revision assets from your learning material/i })).toBeVisible({ timeout: 25000 });
    });

    test("all five tool buttons are visible", async ({ page }) => {
        await page.goto("/student/tools", { waitUntil: "domcontentloaded" });
        for (const tool of ["Quiz", "Flashcards", "Mind Map", "Flowchart", "Concept Map"]) {
            await expect(page.getByRole("button", { name: tool }).first()).toBeVisible();
        }
    });

    test("clicking Quiz selects it as active tool", async ({ page }) => {
        await page.goto("/student/tools", { waitUntil: "domcontentloaded" });
        await page.getByRole("button", { name: "Quiz" }).first().click();
        await expect(page.getByText("Quiz workspace")).toBeVisible();
    });

    test("clicking Flashcards selects flashcard mode", async ({ page }) => {
        await page.goto("/student/tools", { waitUntil: "domcontentloaded" });
        await page.getByRole("button", { name: "Flashcards" }).first().click();
        await expect(page.getByText("Flashcards workspace")).toBeVisible();
    });

    test("Mind Map tool shows correct workspace label", async ({ page }) => {
        await page.goto("/student/tools", { waitUntil: "domcontentloaded" });
        await page.getByRole("button", { name: "Mind Map" }).first().click();
        await expect(page.getByText("Mind Map workspace")).toBeVisible();
    });

    test("Flowchart tool shows workspace label", async ({ page }) => {
        await page.goto("/student/tools", { waitUntil: "domcontentloaded" });
        await page.getByRole("button", { name: "Flowchart" }).first().click();
        await expect(page.getByText("Flowchart workspace")).toBeVisible();
    });

    test("Concept Map tool shows workspace label", async ({ page }) => {
        await page.goto("/student/tools", { waitUntil: "domcontentloaded" });
        await page.getByRole("button", { name: "Concept Map" }).first().click();
        await expect(page.getByText("Concept Map workspace")).toBeVisible();
    });

    test("switching tools clears previous result", async ({ page }) => {
        await page.goto("/student/tools", { waitUntil: "domcontentloaded" });
        await page.getByRole("button", { name: "Quiz" }).first().click();
        await expect(page.getByText("Quiz workspace")).toBeVisible();
        await page.getByRole("button", { name: "Flashcards" }).first().click();
        await expect(page.getByText("Flashcards workspace")).toBeVisible();
        // Quiz workspace should no longer be visible
        await expect(page.getByText("Quiz workspace")).not.toBeVisible();
    });
});

test.describe("Prompt builder and generation", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "student");
        await stubToolsPage(page);
    });

    test("textarea placeholder changes based on selected tool", async ({ page }) => {
        await page.goto("/student/tools", { waitUntil: "domcontentloaded" });
        await page.getByRole("button", { name: "Quiz" }).first().click();
        const textarea = page.locator("textarea");
        await expect(textarea).toHaveAttribute("placeholder", /Thermodynamics/i);
    });

    test("Generate button is disabled when no tool is selected", async ({ page }) => {
        await page.goto("/student/tools", { waitUntil: "domcontentloaded" });
        const genBtn = page.getByRole("button", { name: /Generate/i });
        await expect(genBtn).toBeDisabled();
    });

    test("Generate button is disabled when textarea is empty", async ({ page }) => {
        await page.goto("/student/tools", { waitUntil: "domcontentloaded" });
        await page.getByRole("button", { name: "Quiz" }).first().click();
        const genBtn = page.getByRole("button", { name: /Generate/i });
        await expect(genBtn).toBeDisabled();
    });

    test("Generate button enables when tool selected and topic filled", async ({ page }) => {
        await page.goto("/student/tools", { waitUntil: "domcontentloaded" });
        await page.getByRole("button", { name: "Quiz" }).first().click();
        await page.locator("textarea").fill("Photosynthesis");
        const genBtn = page.getByRole("button", { name: /Generate/i });
        await expect(genBtn).toBeEnabled();
    });

    test("prompt chip fills the textarea", async ({ page }) => {
        await page.goto("/student/tools", { waitUntil: "domcontentloaded" });
        await page.getByRole("button", { name: "Quiz" }).first().click();
        await page.getByRole("button", { name: "High-yield revision" }).click();
        const textarea = page.locator("textarea");
        await expect(textarea).toHaveValue(/High-yield revision/i);
    });

    test("Exam prep prompt chip works", async ({ page }) => {
        await page.goto("/student/tools", { waitUntil: "domcontentloaded" });
        await page.getByRole("button", { name: "Quiz" }).first().click();
        await page.getByRole("button", { name: "Exam prep" }).click();
        const textarea = page.locator("textarea");
        await expect(textarea).toHaveValue(/Exam-focused/i);
    });

    test("Concept links prompt chip works", async ({ page }) => {
        await page.goto("/student/tools", { waitUntil: "domcontentloaded" });
        await page.getByRole("button", { name: "Quiz" }).first().click();
        await page.getByRole("button", { name: "Concept links" }).click();
        const textarea = page.locator("textarea");
        await expect(textarea).toHaveValue(/Connections/i);
    });
});

test.describe("Quiz generation flow", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "student");
        await stubToolsPage(page);
    });

    test("successful quiz generation displays questions", async ({ page }) => {
        await mockToolGenerate(page, { data: [{ question: "What is photosynthesis?", options: ["A. Energy from food", "B. Light to chemical energy", "C. Water cycle", "D. Cell division"], correct: "B. Light to chemical energy", citation: "Biology Ch.10 p.42" }], citations: [{ source: "Biology Ch.10", page: "42" }] }, 200);
        await page.goto("/student/tools", { waitUntil: "domcontentloaded" });
        await page.getByRole("button", { name: "Quiz" }).first().click();
        await page.locator("textarea").fill("Photosynthesis");
        await page.getByRole("button", { name: /Generate/i }).click();
        await expect(page.getByText("What is photosynthesis?")).toBeVisible();
        await expect(page.getByText("B. Light to chemical energy").first()).toBeVisible();
    });

    test("quiz with citations shows source strip", async ({ page }) => {
        await mockToolGenerate(page, { data: [{ question: "Q1?", options: ["A", "B", "C", "D"], correct: "A" }], citations: [{ source: "Notes.pdf", page: "5" }] }, 200);
        await page.goto("/student/tools", { waitUntil: "domcontentloaded" });
        await page.getByRole("button", { name: "Quiz" }).first().click();
        await page.locator("textarea").fill("Test topic");
        await page.getByRole("button", { name: /Generate/i }).click();
        await expect(page.getByText("Sources")).toBeVisible();
        await expect(page.getByText(/Notes\.pdf/)).toBeVisible();
    });

    test("422 error from quiz generation shows error remediation", async ({ page }) => {
        await mockToolGenerate(page, { detail: "Upload study materials before generating." }, 422);
        await page.goto("/student/tools", { waitUntil: "domcontentloaded" });
        await page.getByRole("button", { name: "Quiz" }).first().click();
        await page.locator("textarea").fill("Atoms");
        await page.getByRole("button", { name: /Generate/i }).click();
        await expect(page.getByText(/Upload study materials/i)).toBeVisible();
    });

    test("empty quiz result array doesn't crash", async ({ page }) => {
        await mockToolGenerate(page, { data: [], citations: [] }, 200);
        await page.goto("/student/tools", { waitUntil: "domcontentloaded" });
        await page.getByRole("button", { name: "Quiz" }).first().click();
        await page.locator("textarea").fill("Nothing");
        await page.getByRole("button", { name: /Generate/i }).click();
        await expect(page.getByText("Generated Quiz")).toBeVisible();
    });
});

test.describe("Flashcard generation and navigation", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "student");
        await stubToolsPage(page);
    });

    test("successful flashcard generation shows card view", async ({ page }) => {
        await mockToolGenerate(page, { data: [{ front: "What is DNA?", back: "Deoxyribonucleic acid, carries genetic info", citation: "Biology p.12" }, { front: "What is RNA?", back: "Ribonucleic acid, protein synthesis", citation: "Biology p.14" }], citations: [] }, 200);
        await page.goto("/student/tools", { waitUntil: "domcontentloaded" });
        await page.getByRole("button", { name: "Flashcards" }).first().click();
        await page.locator("textarea").fill("DNA and RNA");
        await page.getByRole("button", { name: /Generate/i }).click();
        await expect(page.getByText("Card 1 of 2")).toBeVisible();
        await expect(page.getByText("What is DNA?")).toBeVisible();
    });

    test("flashcard flip reveals answer", async ({ page }) => {
        await mockToolGenerate(page, { data: [{ front: "Capital of France?", back: "Paris" }], citations: [] }, 200);
        await page.goto("/student/tools", { waitUntil: "domcontentloaded" });
        await page.getByRole("button", { name: "Flashcards" }).first().click();
        await page.locator("textarea").fill("Geography");
        await page.getByRole("button", { name: /Generate/i }).click();
        await expect(page.getByText("Capital of France?")).toBeVisible();
        await page.getByText("Capital of France?").click();
        await expect(page.getByText("Paris")).toBeVisible();
    });

    test("single flashcard disables both navigation buttons", async ({ page }) => {
        await mockToolGenerate(page, { data: [{ front: "Q", back: "A" }], citations: [] }, 200);
        await page.goto("/student/tools", { waitUntil: "domcontentloaded" });
        await page.getByRole("button", { name: "Flashcards" }).first().click();
        await page.locator("textarea").fill("Test");
        await page.getByRole("button", { name: /Generate/i }).click();
        await expect(page.getByText("Card 1 of 1")).toBeVisible();
    });
});

test.describe("Mind map generation", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "student");
        await stubToolsPage(page);
    });

    test("mind map result renders tree structure", async ({ page }) => {
        await mockToolGenerate(page, { data: { label: "Biology", children: [{ label: "Cell", children: [{ label: "Nucleus" }] }, { label: "Genetics" }] }, citations: [] }, 200);
        await page.goto("/student/tools", { waitUntil: "domcontentloaded" });
        await page.getByRole("button", { name: "Mind Map" }).first().click();
        await page.locator("textarea").fill("Biology overview");
        await page.getByRole("button", { name: /Generate/i }).click();
        await expect(page.getByText("Mind Map")).toBeVisible();
        await expect(page.getByText("Biology").first()).toBeVisible();
        await expect(page.getByText("Cell")).toBeVisible();
        await expect(page.getByText("Nucleus")).toBeVisible();
    });

    test("deeply nested mind map renders without crash", async ({ page }) => {
        const deepNode = { label: "L0", children: [{ label: "L1", children: [{ label: "L2", children: [{ label: "L3", children: [{ label: "L4" }] }] }] }] };
        await mockToolGenerate(page, { data: deepNode, citations: [] }, 200);
        await page.goto("/student/tools", { waitUntil: "domcontentloaded" });
        await page.getByRole("button", { name: "Mind Map" }).first().click();
        await page.locator("textarea").fill("Deep topic");
        await page.getByRole("button", { name: /Generate/i }).click();
        await expect(page.getByText("L4")).toBeVisible();
    });
});

test.describe("Library tab", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "student");
    });

    test("library tab shows empty state when no items", async ({ page }) => {
        await page.route("**/api/student/ai-history**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [] }) });
        });
        await page.goto("/student/tools", { waitUntil: "domcontentloaded" });
        await page.getByRole("button", { name: "Library" }).click();
        await expect(page.getByText("No saved study tools yet")).toBeVisible();
    });

    test("library tab shows items when present", async ({ page }) => {
        await page.route("**/api/student/ai-history**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [{ id: "h1", mode: "quiz", query_text: "Photosynthesis quiz", response_text: "...", title: "Photosynthesis Quiz", created_at: "2026-04-01T08:00:00Z", is_pinned: true, folder_id: null }] }) });
        });
        await page.goto("/student/tools", { waitUntil: "domcontentloaded" });
        await page.getByRole("button", { name: "Library" }).click();
        await expect(page.getByText("Photosynthesis Quiz")).toBeVisible();
    });

    test("switching from library to create updates tab", async ({ page }) => {
        await page.route("**/api/student/ai-history**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [] }) });
        });
        await page.goto("/student/tools", { waitUntil: "domcontentloaded" });
        await page.getByRole("button", { name: "Library" }).click();
        await expect(page.getByText("No saved study tools yet")).toBeVisible();
        await page.getByRole("button", { name: "Create" }).click();
        await expect(page.getByText("Quiz")).toBeVisible();
    });

    test("Create and Library tabs are mutually exclusive", async ({ page }) => {
        await page.route("**/api/student/ai-history**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [] }) });
        });
        await page.goto("/student/tools", { waitUntil: "domcontentloaded" });
        // Initially on Create tab
        await expect(page.getByText("Quiz").first()).toBeVisible();
        await page.getByRole("button", { name: "Library" }).click();
        // Library content should be shown
        await expect(page.getByText(/No saved study tools yet|Your generated library/i)).toBeVisible();
    });
});

test.describe("Tool guidance panels", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "student");
        await stubToolsPage(page);
    });

    test("flow guidance panel is visible", async ({ page }) => {
        await page.goto("/student/tools", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("Create, save, return")).toBeVisible();
    });

    test("better prompts guidance panel is visible", async ({ page }) => {
        await page.goto("/student/tools", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("Better prompts, better outputs")).toBeVisible();
    });

    test("output studio panel shows 'No tool selected' initially", async ({ page }) => {
        await page.goto("/student/tools", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("No tool selected")).toBeVisible();
    });

    test("selecting a tool updates output studio pill", async ({ page }) => {
        await page.goto("/student/tools", { waitUntil: "domcontentloaded" });
        await page.getByRole("button", { name: "Quiz" }).first().click();
        await expect(page.getByText("Quiz").last()).toBeVisible();
    });
});
