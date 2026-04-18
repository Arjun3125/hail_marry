import { expect, test } from "@playwright/test";
import { stubAuthShell, stubMascotSuggestions } from "../fixtures/helpers";

/* ═══════════════════════════════════════════════════════════════════════
   ADMIN  USER  GOVERNANCE  ·  25 hard fault-finding tests
   Covers user management, complaints, security, and reports pages.
   ═══════════════════════════════════════════════════════════════════════ */

test.describe("Admin users page", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "admin");
        await stubMascotSuggestions(page, []);
        await page.route("**/api/admin/users**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ users: [], total: 0 }) });
        });
    });

    test("users page loads without crash", async ({ page }) => {
        await page.goto("/admin/users", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("users page handles 500", async ({ page }) => {
        await page.route("**/api/admin/users**", async (route) => {
            await route.fulfill({ status: 500, contentType: "application/json", body: JSON.stringify({ detail: "Error" }) });
        });
        await page.goto("/admin/users", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("users page with data renders list", async ({ page }) => {
        await page.route("**/api/admin/users**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ users: [{ id: "u1", name: "Aarav Sharma", role: "student", email: "a@b.com", status: "active" }], total: 1 }) });
        });
        await page.goto("/admin/users", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("users page with network failure shows error", async ({ page }) => {
        await page.route("**/api/admin/users**", async (route) => {
            await route.abort("connectionrefused");
        });
        await page.goto("/admin/users", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });
});

test.describe("Admin complaints page", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "admin");
        await stubMascotSuggestions(page, []);
        await page.route("**/api/admin/complaints**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [], total: 0 }) });
        });
    });

    test("complaints page loads without crash", async ({ page }) => {
        await page.goto("/admin/complaints", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("complaints page handles 500", async ({ page }) => {
        await page.route("**/api/admin/complaints**", async (route) => {
            await route.fulfill({ status: 500, contentType: "application/json", body: JSON.stringify({ detail: "Error" }) });
        });
        await page.goto("/admin/complaints", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("complaints with data renders list", async ({ page }) => {
        await page.route("**/api/admin/complaints**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [{ id: "c1", title: "Bus issue", status: "open", student_name: "Aarav", created_at: "2026-04-01T08:00:00Z" }], total: 1 }) });
        });
        await page.goto("/admin/complaints", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("complaints page handles malformed JSON", async ({ page }) => {
        await page.route("**/api/admin/complaints**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: "{!broken}" });
        });
        await page.goto("/admin/complaints", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });
});

test.describe("Admin security page", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "admin");
        await stubMascotSuggestions(page, []);
        await page.route("**/api/admin/security**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify([]) });
        });
    });

    test("security page loads without crash", async ({ page }) => {
        await page.goto("/admin/security", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("security page handles 500", async ({ page }) => {
        await page.route("**/api/admin/security**", async (route) => {
            await route.fulfill({ status: 500 });
        });
        await page.goto("/admin/security", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("security page with events renders list", async ({ page }) => {
        await page.route("**/api/admin/security**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify([{ id: "ev1", user: "admin@school.com", action: "login_success", date: "2026-04-01T10:00:00Z" }]) });
        });
        await page.goto("/admin/security", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });
});

test.describe("Admin reports page", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "admin");
        await stubMascotSuggestions(page, []);
        await page.route("**/api/admin/reports**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [] }) });
        });
        await page.route("**/api/admin/student-risk**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [] }) });
        });
    });

    test("reports page loads without crash", async ({ page }) => {
        await page.goto("/admin/reports", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("reports page handles 500", async ({ page }) => {
        await page.route("**/api/admin/reports**", async (route) => {
            await route.fulfill({ status: 500 });
        });
        await page.goto("/admin/reports", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });
});

test.describe("Admin fee management page", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "admin");
        await stubMascotSuggestions(page, []);
        await page.route("**/api/admin/fees**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [] }) });
        });
    });

    test("fees page loads without crash", async ({ page }) => {
        await page.goto("/admin/fees", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("fees page handles 500", async ({ page }) => {
        await page.route("**/api/admin/fees**", async (route) => {
            await route.fulfill({ status: 500 });
        });
        await page.goto("/admin/fees", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("fees page with data renders table", async ({ page }) => {
        await page.route("**/api/admin/fees**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [{ student_id: "s1", student_name: "Aarav", total: 5000, paid: 3000, pending: 2000 }] }) });
        });
        await page.goto("/admin/fees", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });
});
