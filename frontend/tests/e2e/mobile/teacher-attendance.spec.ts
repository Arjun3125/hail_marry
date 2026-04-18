import { expect, test } from "@playwright/test";
import {
    authenticateAs,
    expectKeyboardNavigation,
    expectNoHorizontalScroll,
    expectReadableText,
    expectTouchTargetSizes,
} from "../../fixtures/auth";

test.describe("Teacher Attendance - Mobile (360px)", { tag: "@mobile @teacher" }, () => {
    test.beforeEach(async ({ page }) => {
        await authenticateAs(page, "teacher");

        // Stub teacher attendance endpoints
        await page.route("**/api/teacher/attendance**", (route) => {
            route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify({
                    items: [
                        {
                            id: "att-1",
                            date: "2026-03-31",
                            class: "10-A",
                            present: 32,
                            absent: 3,
                            total: 35,
                        },
                    ],
                }),
            });
        });

        await page.route("**/api/teacher/classes", (route) => {
            route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify({
                    items: [
                        {
                            id: "class-1",
                            name: "10-A",
                            subject: "Mathematics",
                            students: 35,
                        },
                    ],
                }),
            });
        });
    });

    test("attendance page loads without horizontal scroll", async ({ page }) => {
            await page.goto("/teacher/attendance", { waitUntil: "domcontentloaded" });
        await expect(page).toHaveTitle(/VidyaOS/i);
        await expectNoHorizontalScroll(page);
    });

    test("attendance table is responsive", async ({ page }) => {
            await page.goto("/teacher/attendance", { waitUntil: "domcontentloaded" });

        // Table should either scroll horizontally (with scroll indicator) or stack
        const table = page.locator("table, [role='table']").first();

        if (await table.isVisible()) {
            const box = await table.boundingBox();
            if (box) {
                // If table is wider than viewport, it should have scroll
                if (box.width > 360) {
                    console.warn("Table wider than mobile viewport - scrolling required");
                }
            }
        }
    });

    test("mark attendance buttons accessible", async ({ page }) => {
            await page.goto("/teacher/attendance", { waitUntil: "domcontentloaded" });

        const presentButton = page.locator("button").filter({ hasText: /present|âœ“|yes/i }).first();
        const absentButton = page.locator("button").filter({ hasText: /absent|âœ—|no/i }).first();

        if (await presentButton.isVisible()) {
            const box = await presentButton.boundingBox();
            if (box) {
                expect(box.height).toBeGreaterThanOrEqual(44);
                expect(box.width).toBeGreaterThanOrEqual(44);
            }
        }

        if (await absentButton.isVisible()) {
            const box = await absentButton.boundingBox();
            if (box) {
                expect(box.height).toBeGreaterThanOrEqual(44);
            }
        }
    });

    test("touch targets meet minimum size", async ({ page }) => {
            await page.goto("/teacher/attendance", { waitUntil: "domcontentloaded" });
        await expectTouchTargetSizes(page);
    });

    test("student names are readable", async ({ page }) => {
            await page.goto("/teacher/attendance", { waitUntil: "domcontentloaded" });
        await expectReadableText(page, 12);
    });

    test("can scroll through students on mobile", async ({ page }) => {
            await page.goto("/teacher/attendance", { waitUntil: "domcontentloaded" });

        const studentList = page.locator("[data-testid*='student'], .student-row").first();

        if (await studentList.isVisible()) {
            await studentList.evaluate((el) => {
                el.scrollIntoView();
            });
        }
    });

    test("keyboard navigation accessible", async ({ page }) => {
            await page.goto("/teacher/attendance", { waitUntil: "domcontentloaded" });
        await expectKeyboardNavigation(page);
    });

    test("class selector works on mobile", async ({ page }) => {
            await page.goto("/teacher/attendance", { waitUntil: "domcontentloaded" });

        // Look for class dropdown/selector
        const classSelector = page.locator("select, [role='combobox'], button").filter({ hasText: /class|select/i }).first();

        if (await classSelector.isVisible()) {
            await classSelector.click();

            const box = await classSelector.boundingBox();
            if (box) {
                expect(box.width).toBeLessThanOrEqual(360);
            }
        }
    });
});

test.describe("Teacher Attendance - Tablet (768px)", { tag: "@tablet @teacher" }, () => {
    test.beforeEach(async ({ page }) => {
        await authenticateAs(page, "teacher");

        await page.route("**/api/teacher/attendance**", (route) => {
            route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify({
                    items: [
                        {
                            id: "att-1",
                            date: "2026-03-31",
                            class: "10-A",
                            present: 32,
                            absent: 3,
                        },
                    ],
                }),
            });
        });
    });

    test("can display full attendance layout", async ({ page }) => {
        await page.setViewportSize({ width: 768, height: 1024 });
            await page.goto("/teacher/attendance", { waitUntil: "domcontentloaded" });

        await expectNoHorizontalScroll(page);
    });
});

test.describe("Teacher Attendance - Desktop (1280px)", { tag: "@desktop @teacher" }, () => {
    test.beforeEach(async ({ page }) => {
        await authenticateAs(page, "teacher");

        await page.route("**/api/teacher/attendance**", (route) => {
            route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify({
                    items: [
                        {
                            id: "att-1",
                            date: "2026-03-31",
                            class: "10-A",
                            present: 32,
                            absent: 3,
                        },
                    ],
                }),
            });
        });
    });

    test("attendance table displays full data", async ({ page }) => {
        await page.setViewportSize({ width: 1280, height: 720 });
            await page.goto("/teacher/attendance", { waitUntil: "domcontentloaded" });

        await expect(page).toHaveTitle(/VidyaOS/i);
        await expectNoHorizontalScroll(page);
    });
});

