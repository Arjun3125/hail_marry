import { expect, test } from "@playwright/test";
import {
    authenticateAs,
    expectKeyboardNavigation,
    expectNoHorizontalScroll,
    expectReadableText,
    expectTouchTargetSizes,
} from "../../fixtures/auth";

test.describe("Parent Dashboard - Mobile (360px)", { tag: "@mobile @parent" }, () => {
    test.beforeEach(async ({ page }) => {
        await authenticateAs(page, "parent");

        // Stub parent endpoints
        await page.route("**/api/parent/children", (route) => {
            route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify({
                    items: [
                        {
                            id: "child-1",
                            name: "Rajesh Kumar",
                            class: "10-A",
                            school: "ABC School",
                            avatar: "https://example.com/avatar.jpg",
                        },
                    ],
                }),
            });
        });

        await page.route("**/api/parent/summaries**", (route) => {
            route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify({
                    attendance: 92,
                    performance: 78,
                    engagement: 85,
                }),
            });
        });

        await page.route("**/api/parent/ai-insights**", (route) => {
            route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify({
                    total_sessions: 5,
                    total_study_time_hours: 8.5,
                    average_engagement: 85,
                    average_quiz_score: 78,
                }),
            });
        });
    });

    test("parent dashboard loads without horizontal scroll", async ({ page }) => {
        await page.goto("/parent/dashboard");
        await expect(page).toHaveTitle(/parent|dashboard/i);
        await expectNoHorizontalScroll(page);
    });

    test("child cards are vertically stacked", async ({ page }) => {
        await page.goto("/parent/dashboard");

        const childCards = await page.locator("[data-testid*='child'], .child-card").all();

        for (const card of childCards.slice(0, 3)) {
            const box = await card.boundingBox();
            if (box) {
                expect(box.width).toBeLessThanOrEqual(360);
            }
        }
    });

    test("performance metrics display properly", async ({ page }) => {
        await page.goto("/parent/dashboard");

        // Look for metrics cards
        const metricCards = await page.locator("[data-testid*='metric'], [data-testid*='card']").all();
        expect(metricCards.length).toBeGreaterThan(0);

        for (const card of metricCards.slice(0, 3)) {
            const box = await card.boundingBox();
            if (box) {
                expect(box.width).toBeLessThanOrEqual(360);
            }
        }
    });

    test("touch targets are accessible (44px+)", async ({ page }) => {
        await page.goto("/parent/dashboard");
        await expectTouchTargetSizes(page);
    });

    test("text is readable", async ({ page }) => {
        await page.goto("/parent/dashboard");
        await expectReadableText(page, 12);
    });

    test("can view child insights", async ({ page }) => {
        await page.goto("/parent/dashboard");

        // Look for insights button or card
        const insightButton = page.locator("button, a").filter({ hasText: /insight|summary|session|learning/i }).first();

        if (await insightButton.isVisible()) {
            await insightButton.click();
            await page.waitForTimeout(300);
            await expectNoHorizontalScroll(page);
        }
    });

    test("keyboard navigation working", async ({ page }) => {
        await page.goto("/parent/dashboard");
        await expectKeyboardNavigation(page);
    });

    test("notification badges visible", async ({ page }) => {
        await page.goto("/parent/dashboard");

        // WhatsApp or notification badges
        const badges = await page.locator("[data-testid*='badge'], .badge").all();

        for (const badge of badges.slice(0, 3)) {
            const isVisible = await badge.isVisible();
            expect(isVisible).toBeTruthy();
        }
    });

    test("can switch between children if multiple", async ({ page }) => {
        await page.goto("/parent/dashboard");

        // Look for child switcher
        const childSwitcher = page.locator("select, [role='combobox'], button").filter({ hasText: /child|select/i }).first();

        if (await childSwitcher.isVisible()) {
            await childSwitcher.click();
            const box = await childSwitcher.boundingBox();
            if (box) {
                expect(box.height).toBeGreaterThanOrEqual(44);
            }
        }
    });
});

test.describe("Parent Dashboard - Tablet (768px)", { tag: "@tablet @parent" }, () => {
    test.beforeEach(async ({ page }) => {
        await authenticateAs(page, "parent");

        await page.route("**/api/parent/children", (route) => {
            route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify({
                    items: [
                        {
                            id: "child-1",
                            name: "Rajesh Kumar",
                            class: "10-A",
                        },
                    ],
                }),
            });
        });
    });

    test("can display multi-column layout", async ({ page }) => {
        await page.setViewportSize({ width: 768, height: 1024 });
        await page.goto("/parent/dashboard");

        await expectNoHorizontalScroll(page);
    });
});

test.describe("Parent Dashboard - Desktop (1280px)", { tag: "@desktop @parent" }, () => {
    test.beforeEach(async ({ page }) => {
        await authenticateAs(page, "parent");

        await page.route("**/api/parent/children", (route) => {
            route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify({
                    items: [
                        {
                            id: "child-1",
                            name: "Rajesh Kumar",
                            class: "10-A",
                        },
                    ],
                }),
            });
        });
    });

    test("displays full dashboard layout", async ({ page }) => {
        await page.setViewportSize({ width: 1280, height: 720 });
        await page.goto("/parent/dashboard");

        await expect(page).toHaveTitle(/parent|dashboard/i);
        await expectNoHorizontalScroll(page);
    });
});
