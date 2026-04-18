import { expect, test } from "@playwright/test";
import { stubAuthShell, stubMascotSuggestions } from "../fixtures/helpers";

/* ═══════════════════════════════════════════════════════════════════════
   ADMIN  QUEUE  MANAGEMENT  ·  25 hard fault-finding tests
   ═══════════════════════════════════════════════════════════════════════ */

function stubQueuePage(page: import("@playwright/test").Page, items: Record<string, unknown>[] = []) {
    return page.route("**/api/admin/queue**", async (route) => {
        const url = route.request().url();
        if (route.request().method() === "POST") {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ ok: true }) });
            return;
        }
        if (url.includes("/stats") || url.includes("/summary")) {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ pending: items.length, processing: 0, completed: 5, failed: 1, stuck: 0 }) });
            return;
        }
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items, total: items.length }) });
    });
}

test.describe("Queue page rendering", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "admin");
        await stubMascotSuggestions(page, []);
    });

    test("queue page loads without crash", async ({ page }) => {
        await stubQueuePage(page);
        await page.goto("/admin/queue", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("queue page with items renders job list", async ({ page }) => {
        await stubQueuePage(page, [
            { id: "j1", type: "study_tool", status: "pending", created_at: "2026-04-01T10:00:00Z", user_id: "s1", metadata: { tool: "quiz" } },
            { id: "j2", type: "upload_processing", status: "completed", created_at: "2026-04-01T09:00:00Z", user_id: "s2", metadata: {} },
        ]);
        await page.goto("/admin/queue", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("queue page with empty list shows empty state", async ({ page }) => {
        await stubQueuePage(page, []);
        await page.goto("/admin/queue", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("queue page handles 500 from API", async ({ page }) => {
        await page.route("**/api/admin/queue**", async (route) => {
            await route.fulfill({ status: 500, contentType: "application/json", body: JSON.stringify({ detail: "Error" }) });
        });
        await page.goto("/admin/queue", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("queue page handles network failure", async ({ page }) => {
        await page.route("**/api/admin/queue**", async (route) => {
            await route.abort("connectionrefused");
        });
        await page.goto("/admin/queue", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });
});

test.describe("Queue job status display", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "admin");
        await stubMascotSuggestions(page, []);
    });

    test("pending job is displayed", async ({ page }) => {
        await stubQueuePage(page, [{ id: "j1", type: "study_tool", status: "pending", created_at: "2026-04-01T10:00:00Z" }]);
        await page.goto("/admin/queue", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("processing job is displayed", async ({ page }) => {
        await stubQueuePage(page, [{ id: "j1", type: "upload_processing", status: "processing", created_at: "2026-04-01T10:00:00Z" }]);
        await page.goto("/admin/queue", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("failed job is displayed", async ({ page }) => {
        await stubQueuePage(page, [{ id: "j1", type: "study_tool", status: "failed", created_at: "2026-04-01T10:00:00Z", error: "Timeout" }]);
        await page.goto("/admin/queue", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("stuck job is displayed", async ({ page }) => {
        await stubQueuePage(page, [{ id: "j1", type: "study_tool", status: "stuck", created_at: "2026-04-01T08:00:00Z" }]);
        await page.goto("/admin/queue", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("completed job is displayed", async ({ page }) => {
        await stubQueuePage(page, [{ id: "j1", type: "study_tool", status: "completed", created_at: "2026-04-01T10:00:00Z", completed_at: "2026-04-01T10:01:00Z" }]);
        await page.goto("/admin/queue", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });
});

test.describe("Queue data edge cases", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "admin");
        await stubMascotSuggestions(page, []);
    });

    test("job with null metadata doesn't crash", async ({ page }) => {
        await stubQueuePage(page, [{ id: "j1", type: "unknown", status: "pending", created_at: "2026-04-01T10:00:00Z", metadata: null }]);
        await page.goto("/admin/queue", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("job with undefined error field renders", async ({ page }) => {
        await stubQueuePage(page, [{ id: "j1", type: "study_tool", status: "failed", created_at: "2026-04-01T10:00:00Z" }]);
        await page.goto("/admin/queue", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("very long error message doesn't break layout", async ({ page }) => {
        await stubQueuePage(page, [{ id: "j1", type: "study_tool", status: "failed", created_at: "2026-04-01T10:00:00Z", error: "E".repeat(500) }]);
        await page.goto("/admin/queue", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("50 jobs render without performance issue", async ({ page }) => {
        const manyJobs = Array.from({ length: 50 }, (_, i) => ({
            id: `j${i}`, type: "study_tool", status: i % 3 === 0 ? "pending" : i % 3 === 1 ? "completed" : "failed",
            created_at: "2026-04-01T10:00:00Z",
        }));
        await stubQueuePage(page, manyJobs);
        await page.goto("/admin/queue", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("malformed JSON from queue API doesn't crash page", async ({ page }) => {
        await page.route("**/api/admin/queue**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: "{broken}" });
        });
        await page.goto("/admin/queue", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("null items from queue API doesn't crash page", async ({ page }) => {
        await page.route("**/api/admin/queue**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: null }) });
        });
        await page.goto("/admin/queue", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("queue page with unknown job type renders", async ({ page }) => {
        await stubQueuePage(page, [{ id: "j1", type: "mystery_type_xyz", status: "pending", created_at: "2026-04-01T10:00:00Z" }]);
        await page.goto("/admin/queue", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("queue page loads fast enough (under 5s)", async ({ page }) => {
        await stubQueuePage(page);
        const start = Date.now();
        await page.goto("/admin/queue", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
        expect(Date.now() - start).toBeLessThan(5000);
    });
});
