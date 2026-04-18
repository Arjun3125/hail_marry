import { expect, test } from "@playwright/test";
import type { Page } from "@playwright/test";
import {
    authenticateAs,
    expectKeyboardNavigation,
    expectNoHorizontalScroll,
    expectReadableText,
    expectTouchTargetSizes,
} from "../../fixtures/auth";

async function openAiStudio(page: Page) {
    await page.goto("/student/ai-studio", { waitUntil: "domcontentloaded" });
    await expect(page.getByRole("heading", { name: /Start with one clear intent, then open the full study desk/i })).toBeVisible({ timeout: 10000 });
}

async function stubAiStudioData(page: Page) {
    await page.route("**/api/notebooks", (route) => {
        route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                items: [
                    {
                        id: "nb-1",
                        name: "Biology Chapter 10",
                        color: "#2563eb",
                        icon: "book",
                        created_at: "2026-03-31T08:00:00Z",
                        is_active: true,
                    },
                ],
            }),
        });
    });

    await page.route("**/api/personalization/recommendations**", (route) => {
        route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                items: [
                    {
                        id: "rec-1",
                        prompt: "Explain photosynthesis",
                    },
                ],
            }),
        });
    });
}

test.describe("AI Studio - Mobile (360px)", { tag: "@mobile @ai-studio" }, () => {
    test.beforeEach(async ({ page }) => {
        await authenticateAs(page, "student");
        await stubAiStudioData(page);
    });

    test("AI Studio loads without horizontal scroll", async ({ page }) => {
        await openAiStudio(page);
        await expect(page).toHaveTitle(/VidyaOS/i);
        await expectNoHorizontalScroll(page);
    });

    test("tool buttons are accessible", async ({ page }) => {
        await openAiStudio(page);

        // Look for tool buttons (Quiz, Flashcard, Mind Map, etc.)
        const toolButtons = await page.locator("button").all();
        expect(toolButtons.length).toBeGreaterThan(0);

        // Check first button size
        if (toolButtons.length > 0) {
            const box = await toolButtons[0].boundingBox();
            if (box) {
                expect(Math.round(box.height)).toBeGreaterThanOrEqual(44);
                expect(Math.round(box.width)).toBeGreaterThanOrEqual(44);
            }
        }
    });

    test("conversation panel responds to touch", async ({ page }) => {
        await openAiStudio(page);

        // Find input area
        const input = page.locator("input[placeholder*='ask' i], textarea, [contenteditable]").first();

        if (await input.isVisible()) {
            await input.click();
            await expect(input).toBeFocused();
            expect(await input.evaluate((el) => (el as HTMLElement).offsetHeight)).toBeGreaterThan(0);
        }
    });

    test("touch targets for tools are 44px+", async ({ page }) => {
        await openAiStudio(page);
        await expectTouchTargetSizes(page);
    });

    test("text in conversation is readable", async ({ page }) => {
        await openAiStudio(page);
        await expectReadableText(page, 12);
    });

    test("can interact with quiz if displayed", async ({ page }) => {
        await openAiStudio(page);

        // Simulate clicking a quiz button if available
        const quizButton = page.locator("button").filter({ hasText: /quiz/i }).first();

        if (await quizButton.isVisible()) {
            await quizButton.evaluate((el) => {
                (el as HTMLButtonElement).click();
            });
            await expectNoHorizontalScroll(page);
        }
    });

    test("keyboard navigation available", async ({ page }) => {
        await openAiStudio(page);
        await expectKeyboardNavigation(page);
    });

    test("session info displays correctly", async ({ page }) => {
        await openAiStudio(page);

        // Look for session duration, topic info
        const sessionInfo = page.locator("[data-testid*='session'], .session-info").first();

        if (await sessionInfo.isVisible()) {
            const box = await sessionInfo.boundingBox();
            if (box) {
                expect(box.width).toBeLessThanOrEqual(360);
            }
        }
    });
});

test.describe("AI Studio - Tablet (768px)", { tag: "@tablet @ai-studio" }, () => {
    test.beforeEach(async ({ page }) => {
        await authenticateAs(page, "student");
        await stubAiStudioData(page);
    });

    test("can display side-by-side layout", async ({ page }) => {
        await page.setViewportSize({ width: 768, height: 1024 });
        await openAiStudio(page);

        await expectNoHorizontalScroll(page);

        // On tablet, tools might be in a sidebar or grid
        const toolElements = await page.locator("button").all();
        expect(toolElements.length).toBeGreaterThan(0);
    });
});

test.describe("AI Studio - Desktop (1280px)", { tag: "@desktop @ai-studio" }, () => {
    test.beforeEach(async ({ page }) => {
        await authenticateAs(page, "student");
        await stubAiStudioData(page);
    });

    test("AI Studio displays full interface", async ({ page }) => {
        await page.setViewportSize({ width: 1280, height: 720 });
        await openAiStudio(page);

        await expect(page).toHaveTitle(/VidyaOS/i);
        await expectNoHorizontalScroll(page);

        // Desktop sidebar has class lg:flex; mobile drawer has class lg:hidden and comes first in DOM.
        // Use :not(.prism-drawer) to skip the mobile drawer and target the persistent desktop aside.
        await expect(page.locator("aside:not(.prism-drawer)").first()).toBeVisible({ timeout: 10000 });
    });
});

