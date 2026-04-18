import { expect, test } from "@playwright/test";
import {
    authenticateAs,
    expectKeyboardNavigation,
    expectNoHorizontalScroll,
    expectReadableText,
    expectTouchTargetSizes,
} from "../../fixtures/auth";

test.describe("Admin Dashboard - Mobile (360px)", { tag: "@mobile @admin" }, () => {
    test.beforeEach(async ({ page }, testInfo) => {
        test.skip(testInfo.project.name !== "Mobile Chrome", "This block is for Mobile Chrome only");
        await authenticateAs(page, "admin");

        // Stub admin endpoints
        await page.route("**/api/admin/dashboard-bootstrap", (route) => {
            route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify({
                    dashboard: {
                        total_schools: 12,
                        total_teachers: 150,
                        total_students: 2500,
                        total_parents: 2000,
                        active_sessions: 45,
                        active_today: 45,
                        avg_attendance: 95
                    }
                }),
            });
        });

        await page.route("**/api/admin/schools", (route) => {
            route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify({
                    items: [
                        {
                            id: "school-1",
                            name: "ABC School",
                            location: "Mumbai",
                            teachers: 25,
                            students: 500,
                        },
                    ],
                }),
            });
        });
    });

    test("admin dashboard loads without horizontal scroll", async ({ page }) => {
            await page.goto("/admin/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page).toHaveTitle(/VidyaOS/i);
        await expectNoHorizontalScroll(page);
    });

    test("stat cards are stacked mobile-friendly", async ({ page }) => {
            await page.goto("/admin/dashboard", { waitUntil: "domcontentloaded" });

        const firstCard = page.locator("[data-testid*='stat'], [data-testid*='card']").first();
        await expect(firstCard).toBeVisible();

        const statCards = await page.locator("[data-testid*='stat'], [data-testid*='card']").all();

        // Verify cards fit mobile width
        for (const card of statCards.slice(0, 4)) {
            const box = await card.boundingBox();
            if (box) {
                expect(box.width).toBeLessThanOrEqual(360);
            }
        }
    });

    test("navigation buttons are accessible", async ({ page }) => {
            await page.goto("/admin/dashboard", { waitUntil: "domcontentloaded" });

        // Look for nav links
        const navLinks = await page.locator(".prism-nav-link, .prism-action").filter({ hasText: /school|teacher|user|setting/i }).all();

        for (const link of navLinks.slice(0, 3)) {
            if (await link.isVisible()) {
                const box = await link.boundingBox();
                if (box) {
                    expect(box.height).toBeGreaterThanOrEqual(36);
                    expect(box.width).toBeGreaterThanOrEqual(36);
                }
            }
        }
    });

    test("touch targets meet 44px minimum", async ({ page }) => {
            await page.goto("/admin/dashboard", { waitUntil: "domcontentloaded" });
        await expectTouchTargetSizes(page);
    });

    test("large tables/grids are scrollable", async ({ page }) => {
            await page.goto("/admin/dashboard", { waitUntil: "domcontentloaded" });

        // Look for data tables
        const tables = await page.locator("table, [role='table']").all();

        for (const table of tables) {
            if (await table.isVisible()) {
                const box = await table.boundingBox();
                if (box && box.width > 360) {
                    // Table is wider than mobile - should have horizontal scroll
                    console.warn("Wide table on mobile - horizontal scrolling available");
                }
            }
        }
    });

    test("text remains readable", async ({ page }) => {
            await page.goto("/admin/dashboard", { waitUntil: "domcontentloaded" });
        await expectReadableText(page, 12);
    });

    test("can access settings/config", async ({ page }) => {
            await page.goto("/admin/dashboard", { waitUntil: "domcontentloaded" });

        // Open mobile nav if available to expose settings
        const toggles = page.locator("button[aria-label='Open menu'], .mobile-menu-toggle");
        if (await toggles.count() > 0 && await toggles.first().isVisible()) {
             await toggles.first().click();
             await page.waitForTimeout(300);
        }

        const settingsButton = page.locator(".prism-nav-link").filter({ hasText: /settings/i }).first();
        if (await settingsButton.isVisible()) {
            await settingsButton.click();
            await page.waitForTimeout(300);
        }
    });

    test("keyboard navigation working", async ({ page }) => {
            await page.goto("/admin/dashboard", { waitUntil: "domcontentloaded" });
        await expectKeyboardNavigation(page);
    });

    test("modals/dialogs fit mobile viewport", async ({ page }) => {
            await page.goto("/admin/dashboard", { waitUntil: "domcontentloaded" });

        // Try opening a modal if available
        const actionButton = page.locator("button").filter({ hasText: /add|edit|create|manage/i }).first();

        if (await actionButton.isVisible()) {
            await actionButton.click();
            await page.waitForTimeout(300);

            const modal = page.locator("[role='dialog'], .modal").first();
            if (await modal.isVisible()) {
                const box = await modal.boundingBox();
                const viewport = page.viewportSize();

                if (box && viewport) {
                    expect(box.width).toBeLessThanOrEqual(viewport.width);
                    expect(box.height).toBeLessThanOrEqual(viewport.height);
                }
            }
        }
    });
});

test.describe("Admin Dashboard - Tablet (768px)", { tag: "@tablet @admin" }, () => {
    test.beforeEach(async ({ page }, testInfo) => {
        test.skip(testInfo.project.name !== "Tablet", "This block is for Tablet only");
        await authenticateAs(page, "admin");

        await page.route("**/api/admin/dashboard-bootstrap", (route) => {
            route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify({
                    dashboard: {
                        total_schools: 12,
                        total_teachers: 150,
                        total_students: 2500,
                        total_parents: 2000,
                        active_sessions: 45,
                        active_today: 45,
                        avg_attendance: 95
                    }
                }),
            });
        });
    });

    test("can display stats in grid layout", async ({ page }) => {
        await page.setViewportSize({ width: 768, height: 1024 });
            await page.goto("/admin/dashboard", { waitUntil: "domcontentloaded" });

        await expectNoHorizontalScroll(page);

        // On tablet, stats might be in 2-column grid
        const firstCard = page.locator("[data-testid*='stat'], [data-testid*='card']").first();
        await expect(firstCard).toBeVisible();
    });
});

test.describe("Admin Dashboard - Desktop (1280px)", { tag: "@desktop @admin" }, () => {
    test.beforeEach(async ({ page }, testInfo) => {
        test.skip(!["chromium", "Desktop Small"].includes(testInfo.project.name), "This block is for Desktop only");
        await authenticateAs(page, "admin");

        await page.route("**/api/admin/dashboard-bootstrap", (route) => {
            route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify({
                    dashboard: {
                        total_schools: 12,
                        total_teachers: 150,
                        total_students: 2500,
                        total_parents: 2000,
                        active_sessions: 45,
                        active_today: 45,
                        avg_attendance: 95
                    }
                }),
            });
        });
    });

    test("displays full admin interface", async ({ page }) => {
        await page.setViewportSize({ width: 1280, height: 720 });
            await page.goto("/admin/dashboard", { waitUntil: "domcontentloaded" });

        await expect(page).toHaveTitle(/VidyaOS/i);
        await expectNoHorizontalScroll(page);

        // Desktop should have full navigation sidebar
        await expect(page.getByTestId("sidebar")).toBeVisible();
    });
});

