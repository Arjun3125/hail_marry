import { expect, test } from "@playwright/test";
import {
    authenticateAs,
    expectKeyboardNavigation,
    expectNoHorizontalScroll,
    expectReadableText,
    expectTouchTargetSizes,
    testResponsiveSidebar,
} from "../../fixtures/auth";

test.describe("Student Dashboard - Mobile (360px)", { tag: "@mobile @student" }, () => {
    test.beforeEach(async ({ page }, testInfo) => {
        test.skip(testInfo.project.name !== "Mobile Chrome", "This block is for Mobile Chrome only");
        await authenticateAs(page, "student");
        await page.route("**/api/student/overview-bootstrap", (route) => {
            route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify({
                    dashboard: {
                        attendance_pct: 95,
                        avg_marks: 85,
                        pending_assignments: 2,
                        ai_queries_today: 5,
                        upcoming_classes: [],
                    }
                }),
            });
        });
    });

    test("dashboard loads without horizontal scroll", async ({ page }) => {
            await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page).toHaveTitle(/VidyaOS/i);
        await expectNoHorizontalScroll(page);
    });

    test("sidebar is accessible on mobile", async ({ page }) => {
            await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        const { toggleAvailable } = await testResponsiveSidebar(page);

        if (!toggleAvailable) {
            console.warn("Sidebar toggle not found - checking direct sidebar");
        }

        // Sidebar DOM element should be attached
        await expect(page.getByTestId("sidebar")).toBeAttached();
    });

    test("cards are stacked vertically", async ({ page }) => {
            await page.goto("/student/overview", { waitUntil: "domcontentloaded" });

        // Wait for at least one card to appear (bypassing skeletons)
        const firstCard = page.locator(".vidya-command-card, .vidya-feed-row").first();
        await expect(firstCard).toBeVisible();

        const cards = await page.locator(".vidya-command-card, .vidya-feed-row").all();
        // Check that cards don't overlap horizontally (stacked vertically)
        for (let i = 0; i < Math.min(cards.length, 3); i++) {
            const card = cards[i];
            const box = await card.boundingBox();

            if (box) {
                expect(box.width).toBeLessThanOrEqual(370); // Leave some margin
            }
        }
    });

    test("touch targets are 44px minimum", async ({ page }) => {
            await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expectTouchTargetSizes(page);
    });

    test("text is readable (min 12px)", async ({ page }) => {
            await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expectReadableText(page, 12);
    });

    test("quick action buttons accessible", async ({ page }) => {
            await page.goto("/student/overview", { waitUntil: "domcontentloaded" });

        // Look for common action buttons
        const buttons = page.locator("button").first();
        expect(buttons).toBeDefined();

        const box = await buttons.boundingBox();
        if (box) {
            expect(box.height).toBeGreaterThanOrEqual(36);
            expect(box.width).toBeGreaterThanOrEqual(36);
        }
    });

    test("can navigate with keyboard", async ({ page }) => {
            await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expectKeyboardNavigation(page);
    });

    test("modals fit within viewport", async ({ page }) => {
            await page.goto("/student/overview", { waitUntil: "domcontentloaded" });

        // Find and click a modal trigger if available
        const modalTrigger = page.locator("button").first();
        if (await modalTrigger.isVisible()) {
            await modalTrigger.click();

            // Wait for potential modal
            await page.waitForTimeout(300);

            const modal = page.locator("[role='dialog'], .modal");
            if (await modal.count()) {
                const box = await modal.first().boundingBox();
                const viewport = page.viewportSize();

                if (box && viewport) {
                    expect(box.width).toBeLessThanOrEqual(viewport.width);
                    expect(box.height).toBeLessThanOrEqual(viewport.height);
                }
            }
        }
    });

    test("images are responsive", async ({ page }) => {
            await page.goto("/student/overview", { waitUntil: "domcontentloaded" });

        const images = await page.locator("img").all();
        for (const img of images.slice(0, 3)) {
            const box = await img.boundingBox();
            if (box) {
                expect(box.width).toBeLessThanOrEqual(360);
            }
        }
    });
});

test.describe("Student Dashboard - Tablet (768px)", { tag: "@tablet @student" }, () => {
    test.beforeEach(async ({ page }, testInfo) => {
        test.skip(testInfo.project.name !== "Tablet", "This block is for Tablet only");
        await authenticateAs(page, "student");
        await page.route("**/api/student/overview-bootstrap", (route) => {
            route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify({
                    dashboard: {
                        attendance_pct: 95,
                        avg_marks: 85,
                        pending_assignments: 2,
                        ai_queries_today: 5,
                        upcoming_classes: [],
                    }
                }),
            });
        });
    });

    test("dashboard loads without horizontal scroll", async ({ page }) => {
        await page.setViewportSize({ width: 768, height: 1024 });
            await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expectNoHorizontalScroll(page);
    });

    test("can display grid layout", async ({ page }) => {
        await page.setViewportSize({ width: 768, height: 1024 });
            await page.goto("/student/overview", { waitUntil: "domcontentloaded" });

        // On tablet, grid might be 2 columns
        const firstCard = page.locator(".vidya-command-card, .vidya-feed-row").first();
        await expect(firstCard).toBeVisible();
    });
});

test.describe("Student Dashboard - Desktop (1280px)", { tag: "@desktop @student" }, () => {
    test.beforeEach(async ({ page }, testInfo) => {
        test.skip(!["chromium", "Desktop Small"].includes(testInfo.project.name), "This block is for Desktop only");
        await authenticateAs(page, "student");
        await page.route("**/api/student/overview-bootstrap", (route) => {
            route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify({
                    dashboard: {
                        attendance_pct: 95,
                        avg_marks: 85,
                        pending_assignments: 2,
                        ai_queries_today: 5,
                        upcoming_classes: [],
                    }
                }),
            });
        });
    });

    test("dashboard displays full layout", async ({ page }) => {
        await page.setViewportSize({ width: 1280, height: 720 });
            await page.goto("/student/overview", { waitUntil: "domcontentloaded" });

        await expect(page).toHaveTitle(/VidyaOS/i);
        await expectNoHorizontalScroll(page);

        // On desktop, sidebar should be visible
        await expect(page.getByTestId("sidebar")).toBeVisible();
    });
});

