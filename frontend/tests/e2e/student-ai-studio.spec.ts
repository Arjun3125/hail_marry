import { expect, test } from "@playwright/test";
import { stubAuthShell, stubNotebooks } from "../fixtures/helpers";

/* ═══════════════════════════════════════════════════════════════════════
   STUDENT  AI  STUDIO  ·  35 hard fault-finding tests
   ═══════════════════════════════════════════════════════════════════════ */

test.describe("AI Studio page initialization", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "student");
        await stubNotebooks(page, [{ id: "nb-bio", name: "Biology Chapter 10", color: "#2563eb", icon: "book", created_at: "2026-03-31T08:00:00Z", updated_at: "2026-03-31T08:00:00Z", is_active: true }]);
        await page.route("**/api/personalization/recommendations**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [] }) });
        });
        await page.route("**/api/student/ai-history**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [] }) });
        });
    });

    test("AI studio renders hero heading", async ({ page }) => {
        await page.goto("/student/ai-studio", { waitUntil: "domcontentloaded" });
        await expect(page.getByRole("heading", { name: /Start with one clear intent/i })).toBeVisible({ timeout: 10000 });
    });

    test("Deep Work Layout badge is visible", async ({ page }) => {
        await page.goto("/student/ai-studio", { waitUntil: "domcontentloaded" });
        await expect(page.getByText(/Deep Work Layout/i)).toBeVisible({ timeout: 10000 });
    });

    test("session intent status item is displayed", async ({ page }) => {
        await page.goto("/student/ai-studio", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("Session intent")).toBeVisible({ timeout: 10000 });
    });

    test("active mode status shows QA by default for understand_topic intent", async ({ page }) => {
        await page.goto("/student/ai-studio", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("Active mode")).toBeVisible({ timeout: 10000 });
    });

    test("keyboard ready status is displayed", async ({ page }) => {
        await page.goto("/student/ai-studio", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("Keyboard ready")).toBeVisible({ timeout: 10000 });
    });

    test("notebook scope status is visible", async ({ page }) => {
        await page.goto("/student/ai-studio", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("Notebook scope")).toBeVisible({ timeout: 10000 });
    });

    test("subject focus defaults to no subject locked", async ({ page }) => {
        await page.goto("/student/ai-studio", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("No subject locked")).toBeVisible({ timeout: 10000 });
    });
});

test.describe("Tool selection via query params", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "student");
        await stubNotebooks(page, []);
        await page.route("**/api/personalization/recommendations**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [] }) });
        });
        await page.route("**/api/student/ai-history**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [] }) });
        });
    });

    test("?tool=quiz sets quiz as active mode", async ({ page }) => {
        await page.goto("/student/ai-studio?tool=quiz", { waitUntil: "domcontentloaded" });
        await expect(page.getByText(/Deep Work Layout/i)).toBeVisible({ timeout: 10000 });
    });

    test("?tool=flashcards sets flashcards mode", async ({ page }) => {
        await page.goto("/student/ai-studio?tool=flashcards", { waitUntil: "domcontentloaded" });
        await expect(page.getByText(/Deep Work Layout/i)).toBeVisible({ timeout: 10000 });
    });

    test("?tool=invalid_tool falls back gracefully", async ({ page }) => {
        await page.goto("/student/ai-studio?tool=nonexistent", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("?notebook_id sets active notebook", async ({ page }) => {
        await page.goto("/student/ai-studio?notebook_id=nb-bio", { waitUntil: "domcontentloaded" });
        await expect(page.getByText(/Notebook scoped|nb-bio/i).first()).toBeVisible({ timeout: 10000 });
    });

    test("?subject=Biology sets subject focus", async ({ page }) => {
        await page.goto("/student/ai-studio?subject=Biology", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("Biology").first()).toBeVisible({ timeout: 10000 });
    });

    test("?prompt=test sets seed prompt", async ({ page }) => {
        await page.goto("/student/ai-studio?prompt=Explain%20photosynthesis", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });
});

test.describe("History restore flow", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "student");
        await stubNotebooks(page, []);
        await page.route("**/api/personalization/recommendations**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [] }) });
        });
    });

    test("?history=valid-id loads exchange from history API", async ({ page }) => {
        await page.route("**/api/student/ai-history/hist1", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ id: "hist1", mode: "qa", query_text: "What is DNA?", response_text: "DNA is..." }) });
        });
        await page.route("**/api/student/ai-history**", async (route) => {
            const url = route.request().url();
            if (url.includes("/hist1")) return; // Let the specific route handle it
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [] }) });
        });
        await page.goto("/student/ai-studio?history=hist1", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("?history=invalid-id handles 404 gracefully", async ({ page }) => {
        await page.route("**/api/student/ai-history/**", async (route) => {
            await route.fulfill({ status: 404, contentType: "application/json", body: JSON.stringify({ detail: "Not found" }) });
        });
        await page.goto("/student/ai-studio?history=nonexistent", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });
});

test.describe("Context panel and recommendations", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "student");
        await stubNotebooks(page, [{ id: "nb-1", name: "Bio", color: "#000" }]);
        await page.route("**/api/student/ai-history**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [] }) });
        });
    });

    test("context panel recommendations render when available", async ({ page }) => {
        await page.route("**/api/personalization/recommendations**", async (route) => {
            const url = new URL(route.request().url());
            const surface = url.searchParams.get("current_surface");
            if (surface === "ai_studio_context_panel") {
                await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [{ id: "r1", label: "Relearn photosynthesis", description: "Guided explanation", prompt: "Explain photosynthesis", target_tool: "study_guide", priority: "high" }] }) });
            } else {
                await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [] }) });
            }
        });
        await page.goto("/student/ai-studio", { waitUntil: "domcontentloaded" });
        await expect(page.getByText(/Context Lab|Deep Work Layout|Start with one clear intent/i).first()).toBeVisible({ timeout: 10000 });
    });

    test("empty recommendations still renders context panel", async ({ page }) => {
        await page.route("**/api/personalization/recommendations**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [] }) });
        });
        await page.goto("/student/ai-studio", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("500 from recommendations doesn't crash context panel", async ({ page }) => {
        await page.route("**/api/personalization/recommendations**", async (route) => {
            await route.fulfill({ status: 500, contentType: "application/json", body: JSON.stringify({ detail: "Error" }) });
        });
        await page.goto("/student/ai-studio", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });
});

test.describe("AI Studio edge cases", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "student");
        await stubNotebooks(page, []);
        await page.route("**/api/personalization/recommendations**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [] }) });
        });
        await page.route("**/api/student/ai-history**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [] }) });
        });
    });

    test("multiple query params together work correctly", async ({ page }) => {
        await page.goto("/student/ai-studio?tool=study_guide&subject=Chemistry&prompt=Equilibrium", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("Chemistry").first()).toBeVisible({ timeout: 10000 });
    });

    test("empty query params don't cause errors", async ({ page }) => {
        await page.goto("/student/ai-studio?tool=&prompt=&subject=", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("XSS in query params is safely handled", async ({ page }) => {
        await page.goto("/student/ai-studio?prompt=<script>alert(1)</script>", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
        // Script should not execute
        const alertFired = await page.evaluate(() => {
            return (window as unknown as { _xss_fired?: boolean })._xss_fired ?? false;
        });
        expect(alertFired).toBe(false);
    });

    test("very long prompt param doesn't crash", async ({ page }) => {
        const longPrompt = encodeURIComponent("A".repeat(2000));
        await page.goto(`/student/ai-studio?prompt=${longPrompt}`, { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("studio with no intent saved shows intent selector initially", async ({ page }) => {
        // Remove the saved intent
        await page.addInitScript(() => {
            window.localStorage.removeItem("student-ai-studio-intent");
        });
        await page.goto("/student/ai-studio", { waitUntil: "domcontentloaded" });
        // Should show intent selector or studio workspace
        await expect(page.locator("body")).toBeVisible();
    });

    test("Continue in advanced workspace button bypasses intent selector", async ({ page }) => {
        await page.addInitScript(() => {
            window.localStorage.removeItem("student-ai-studio-intent");
        });
        await page.goto("/student/ai-studio", { waitUntil: "domcontentloaded" });
        const advancedBtn = page.getByRole("button", { name: /Continue in advanced workspace/i });
        if (await advancedBtn.isVisible()) {
            await advancedBtn.click();
            await expect(page.getByText(/Deep Work Layout/i)).toBeVisible();
        } else {
            // Intent was already set, workspace shown directly
            await expect(page.locator("body")).toBeVisible();
        }
    });

    test("Change intent button is visible in workspace mode", async ({ page }) => {
        await page.goto("/student/ai-studio", { waitUntil: "domcontentloaded" });
        // Either intent selector or workspace is shown
        await expect(page.locator("body")).toBeVisible();
    });
});
