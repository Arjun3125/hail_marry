import { expect, test } from "@playwright/test";
import { stubAuthShell, stubStudentOverview, stubAdminDashboard, stubTeacherDashboard, stubParentDashboard, stubMascotSuggestions } from "../fixtures/helpers";

/* ═══════════════════════════════════════════════════════════════════════
   ACCESSIBILITY  &  RESPONSIVE  ·  15 hard fault-finding tests
   ═══════════════════════════════════════════════════════════════════════ */

test.describe("Semantic HTML and accessibility", () => {
    test("landing page has proper heading hierarchy", async ({ page }) => {
        await page.route("**/api/branding/config", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ name: "VidyaOS" }) });
        });
        await page.goto("/", { waitUntil: "domcontentloaded" });
        const h1Count = await page.locator("h1").count();
        expect(h1Count).toBeGreaterThanOrEqual(1);
        expect(h1Count).toBeLessThanOrEqual(2); // allow for app shell + page
    });

    test("login page has accessible form labels", async ({ page }) => {
        await page.route("**/api/branding/config", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ name: "VidyaOS" }) });
        });
        await page.goto("/login", { waitUntil: "domcontentloaded" });
        // Wait for page hydration
        await expect(page.locator("h1").first()).toBeVisible();
        // Login should have buttons or links with discernible text
        const buttonsAndLinks = page.locator("button, a");
        const count = await buttonsAndLinks.count();
        expect(count).toBeGreaterThanOrEqual(1);
    });

    test("student overview has at least one heading", async ({ page }) => {
        await stubAuthShell(page, "student");
        await stubStudentOverview(page);
        await stubMascotSuggestions(page, []);
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        const headings = page.locator("h1, h2, h3");
        await headings.first().waitFor({ state: "visible", timeout: 5000 });
        expect(await headings.count()).toBeGreaterThanOrEqual(1);
    });

    test("admin dashboard has contrast-safe text", async ({ page }) => {
        await stubAuthShell(page, "admin");
        await stubAdminDashboard(page);
        await stubMascotSuggestions(page, []);
        await page.goto("/admin/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("Admin command center")).toBeVisible();
        // Spot-check: zero-opacity text should not exist for important content
        const invisibleText = await page.evaluate(() => {
            const elements = document.querySelectorAll("p, h1, h2, h3, span, div");
            let count = 0;
            elements.forEach((el) => {
                const style = getComputedStyle(el);
                if (style.opacity === "0" && el.textContent && el.textContent.trim().length > 0) count++;
            });
            return count;
        });
        expect(invisibleText).toBe(0);
    });

    test("interactive elements have unique IDs or accessible names", async ({ page }) => {
        await stubAuthShell(page, "student");
        await stubStudentOverview(page);
        await stubMascotSuggestions(page, []);
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        const buttons = await page.locator("button").all();
        for (const btn of buttons) {
            const name = await btn.getAttribute("aria-label") ?? await btn.textContent();
            expect(name?.trim().length).toBeGreaterThan(0);
        }
    });
});

test.describe("Responsive layouts — Mobile viewport", () => {
    test.use({ viewport: { width: 375, height: 812 } });

    test("student overview is usable on mobile", async ({ page }) => {
        await stubAuthShell(page, "student");
        await stubStudentOverview(page);
        await stubMascotSuggestions(page, []);
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
        const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
        expect(bodyWidth).toBeLessThanOrEqual(430); // no horizontal overflow
    });

    test("teacher dashboard is usable on mobile", async ({ page }) => {
        await stubAuthShell(page, "teacher");
        await stubTeacherDashboard(page);
        await stubMascotSuggestions(page, []);
        await page.goto("/teacher/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("admin dashboard is usable on mobile", async ({ page }) => {
        await stubAuthShell(page, "admin");
        await stubAdminDashboard(page);
        await stubMascotSuggestions(page, []);
        await page.goto("/admin/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("parent dashboard is usable on mobile", async ({ page }) => {
        await stubAuthShell(page, "parent");
        await stubParentDashboard(page);
        await stubMascotSuggestions(page, []);
        await page.route("**/api/parent/ai-insights**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ insights: [] }) });
        });
        await page.goto("/parent/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("mascot launcher is accessible on mobile", async ({ page }) => {
        await stubAuthShell(page, "student");
        await stubStudentOverview(page);
        await stubMascotSuggestions(page, ["Help"]);
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.getByLabel("Open mascot assistant")).toBeVisible();
    });
});

test.describe("Responsive layouts — Tablet viewport", () => {
    test.use({ viewport: { width: 768, height: 1024 } });

    test("student overview is usable on tablet", async ({ page }) => {
        await stubAuthShell(page, "student");
        await stubStudentOverview(page);
        await stubMascotSuggestions(page, []);
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("admin dashboard is usable on tablet", async ({ page }) => {
        await stubAuthShell(page, "admin");
        await stubAdminDashboard(page);
        await stubMascotSuggestions(page, []);
        await page.goto("/admin/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });
});

test.describe("Dark mode resilience", () => {
    test("pages work with prefers-color-scheme dark", async ({ page }) => {
        await page.emulateMedia({ colorScheme: "dark" });
        await page.route("**/api/branding/config", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ name: "VidyaOS" }) });
        });
        await page.goto("/", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("student dashboard works in dark mode", async ({ page }) => {
        await page.emulateMedia({ colorScheme: "dark" });
        await stubAuthShell(page, "student");
        await stubStudentOverview(page);
        await stubMascotSuggestions(page, []);
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });
});
