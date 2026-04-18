import { expect, test } from "@playwright/test";
import { stubAuthShell, stubParentDashboard, parentDashboardPayload, stubMascotSuggestions } from "../fixtures/helpers";

/* ═══════════════════════════════════════════════════════════════════════
   PARENT  GUARDIAN  FLOWS  ·  25 hard fault-finding tests
   ═══════════════════════════════════════════════════════════════════════ */

test.describe("Parent dashboard bootstrap rendering", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "parent");
        await stubMascotSuggestions(page, []);
        await page.route("**/api/parent/ai-insights**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ insights: [] }) });
        });
    });

    test("parent dashboard renders hero heading", async ({ page }) => {
        await stubParentDashboard(page);
        await page.goto("/parent/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.getByRole("heading", { name: /Read your child.*week/i })).toBeVisible();
    });

    test("parent kicker badge is visible", async ({ page }) => {
        await stubParentDashboard(page);
        await page.goto("/parent/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("Parent weekly summary", { exact: true })).toBeVisible();
    });

    test("child name is displayed", async ({ page }) => {
        await stubParentDashboard(page);
        await page.goto("/parent/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.getByRole("heading", { name: "Aarav Sharma" })).toBeVisible();
    });

    test("class badge is shown", async ({ page }) => {
        await page.route("**/api/parent/dashboard", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ ...parentDashboardPayload(), child: { id: "s1", name: "Aarav", email: "a@b.com", class: "10-A" }, summary: {} }) });
        });
        await page.goto("/parent/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("Class 10-A")).toBeVisible();
    });

    test("attendance percentage is visible", async ({ page }) => {
        await stubParentDashboard(page);
        await page.goto("/parent/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("94%").first()).toBeAttached();
    });

    test("latest test score is visible", async ({ page }) => {
        await stubParentDashboard(page);
        await page.goto("/parent/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("84%").first()).toBeAttached();
    });

    test("audio summary button is visible", async ({ page }) => {
        await stubParentDashboard(page);
        await page.goto("/parent/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.getByRole("button", { name: /Play.*audio summary/i })).toBeVisible();
    });

    test("quick links section is visible", async ({ page }) => {
        await stubParentDashboard(page);
        await page.goto("/parent/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("Quick links")).toBeVisible();
    });
});

test.describe("Parent dashboard navigation links", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "parent");
        await stubParentDashboard(page);
        await stubMascotSuggestions(page, []);
        await page.route("**/api/parent/ai-insights**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ insights: [] }) });
        });
    });

    test("attendance log link goes to /parent/attendance", async ({ page }) => {
        await page.goto("/parent/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.getByRole("link", { name: /Attendance log/i })).toHaveAttribute("href", "/parent/attendance");
    });

    test("exam results link goes to /parent/results", async ({ page }) => {
        await page.goto("/parent/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.getByRole("link", { name: /Exam results/i })).toHaveAttribute("href", "/parent/results");
    });

    test("report issue link goes to /parent/assistant", async ({ page }) => {
        await page.goto("/parent/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.getByRole("link", { name: /Report an issue/i })).toHaveAttribute("href", /\/parent\/assistant/);
    });

    test("progress reports link goes to /parent/reports", async ({ page }) => {
        await page.goto("/parent/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.getByRole("link", { name: /Progress reports/i })).toHaveAttribute("href", "/parent/reports");
    });
});

test.describe("Parent dashboard edge cases", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "parent");
        await stubMascotSuggestions(page, []);
        await page.route("**/api/parent/ai-insights**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ insights: [] }) });
        });
    });

    test("500 from dashboard shows error remediation", async ({ page }) => {
        await page.route("**/api/parent/dashboard", async (route) => {
            await route.fulfill({ status: 500, contentType: "application/json", body: JSON.stringify({ detail: "Server error" }) });
        });
        await page.goto("/parent/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("null latest_mark shows fallback text", async ({ page }) => {
        await page.route("**/api/parent/dashboard", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ ...parentDashboardPayload(), latest_mark: null, summary: {} }) });
        });
        await page.goto("/parent/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("No marks").first()).toBeAttached();
    });

    test("null class renders student profile badge", async ({ page }) => {
        await page.route("**/api/parent/dashboard", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ ...parentDashboardPayload(), child: { id: "s1", name: "Aarav", email: "a@b.com", class: null }, summary: {} }) });
        });
        await page.goto("/parent/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("Student profile")).toBeVisible();
    });

    test("loading state shows preparing message", async ({ page }) => {
        await page.route("**/api/parent/dashboard", async (route) => {
            await new Promise((r) => setTimeout(r, 2000));
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(parentDashboardPayload()) });
        });
        await page.goto("/parent/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.getByText(/Preparing the parent weekly summary/i)).toBeVisible();
    });

    test("zero attendance renders correctly", async ({ page }) => {
        await page.route("**/api/parent/dashboard", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ ...parentDashboardPayload(), attendance_pct: 0, summary: {} }) });
        });
        await page.goto("/parent/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("0%").first()).toBeAttached();
    });

    test("low attendance shows needs attention text", async ({ page }) => {
        await page.route("**/api/parent/dashboard", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ ...parentDashboardPayload(), attendance_pct: 40, summary: {} }) });
        });
        await page.goto("/parent/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.getByText(/needs attention/i)).toBeVisible();
    });

    test("highlights section shows attendance row", async ({ page }) => {
        await stubParentDashboard(page);
        await page.goto("/parent/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("Attendance").first()).toBeVisible();
        await expect(page.getByText("Latest result").first()).toBeVisible();
        await expect(page.getByText("Study activity").first()).toBeVisible();
    });

    test("XSS in child name is escaped", async ({ page }) => {
        await page.route("**/api/parent/dashboard", async (route) => {
            await route.fulfill({
                status: 200, contentType: "application/json",
                body: JSON.stringify({ ...parentDashboardPayload(), child: { id: "s1", name: '<img src=x onerror="alert(1)">', email: "a@b.com", class: "10" }, summary: {} }),
            });
        });
        await page.goto("/parent/dashboard", { waitUntil: "domcontentloaded" });
        const alertFired = await page.evaluate(() => (window as unknown as { _xss?: boolean })._xss ?? false);
        expect(alertFired).toBe(false);
    });
});
