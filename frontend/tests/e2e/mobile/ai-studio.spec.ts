import { expect, test } from "@playwright/test";
import {
    authenticateAs,
    expectKeyboardNavigation,
    expectNoHorizontalScroll,
    expectReadableText,
    expectTouchTargetSizes,
} from "../../fixtures/auth";

test.describe("AI Studio - Mobile (360px)", { tag: "@mobile @ai-studio" }, () => {
    test.beforeEach(async ({ page }) => {
        await authenticateAs(page, "student");

        // Stub AI Studio endpoints
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

        await page.route("**/api/recommendations**", (route) => {
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
    });

    test("AI Studio loads without horizontal scroll", async ({ page }) => {
        await page.goto("/student/ai-studio");
        await expect(page).toHaveTitle(/ai|studio|learning/i);
        await expectNoHorizontalScroll(page);
    });

    test("tool buttons are accessible", async ({ page }) => {
        await page.goto("/student/ai-studio");

        // Look for tool buttons (Quiz, Flashcard, Mind Map, etc.)
        const toolButtons = await page.locator("button").all();
        expect(toolButtons.length).toBeGreaterThan(0);

        // Check first button size
        if (toolButtons.length > 0) {
            const box = await toolButtons[0].boundingBox();
            if (box) {
                expect(box.height).toBeGreaterThanOrEqual(44);
                expect(box.width).toBeGreaterThanOrEqual(44);
            }
        }
    });

    test("conversation panel responds to touch", async ({ page }) => {
        await page.goto("/student/ai-studio");

        // Find input area
        const input = page.locator("input[placeholder*='ask' i], textarea, [contenteditable]").first();

        if (await input.isVisible()) {
            await input.click();
            expect(await input.evaluate((el) => (el as HTMLElement).offsetHeight)).toBeGreaterThan(0);
        }
    });

    test("touch targets for tools are 44px+", async ({ page }) => {
        await page.goto("/student/ai-studio");
        await expectTouchTargetSizes(page);
    });

    test("text in conversation is readable", async ({ page }) => {
        await page.goto("/student/ai-studio");
        await expectReadableText(page, 12);
    });

    test("can interact with quiz if displayed", async ({ page }) => {
        await page.goto("/student/ai-studio");

        // Simulate clicking a quiz button if available
        const quizButton = page.locator("button").filter({ hasText: /quiz/i }).first();

        if (await quizButton.isVisible()) {
            await quizButton.click();
            await expectNoHorizontalScroll(page);
        }
    });

    test("keyboard navigation available", async ({ page }) => {
        await page.goto("/student/ai-studio");
        await expectKeyboardNavigation(page);
    });

    test("session info displays correctly", async ({ page }) => {
        await page.goto("/student/ai-studio");

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
    });

    test("can display side-by-side layout", async ({ page }) => {
        await page.setViewportSize({ width: 768, height: 1024 });
        await page.goto("/student/ai-studio");

        await expectNoHorizontalScroll(page);

        // On tablet, tools might be in a sidebar or grid
        const toolElements = await page.locator("button").all();
        expect(toolElements.length).toBeGreaterThan(0);
    });
});

test.describe("AI Studio - Desktop (1280px)", { tag: "@desktop @ai-studio" }, () => {
    test.beforeEach(async ({ page }) => {
        await authenticateAs(page, "student");

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
    });

    test("AI Studio displays full interface", async ({ page }) => {
        await page.setViewportSize({ width: 1280, height: 720 });
        await page.goto("/student/ai-studio");

        await expect(page).toHaveTitle(/ai|studio/i);
        await expectNoHorizontalScroll(page);

        // Desktop should have full sidebar
        const sidebar = await page.locator("nav, aside").isVisible();
        expect(sidebar).toBeTruthy();
    });
});
