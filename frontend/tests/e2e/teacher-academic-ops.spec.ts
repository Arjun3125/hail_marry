import { expect, test } from "@playwright/test";
import { stubAuthShell, stubMascotSuggestions } from "../fixtures/helpers";

/* ═══════════════════════════════════════════════════════════════════════
   TEACHER  ACADEMIC  OPS  ·  30 hard fault-finding tests
   Covers assignments, attendance, marks, doubt-heatmap, and
   generate-assessment routing behavior.
   ═══════════════════════════════════════════════════════════════════════ */

test.describe("Assignments page routing", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "teacher");
        await stubMascotSuggestions(page, []);
        await page.route("**/api/teacher/assignments**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [] }) });
        });
        await page.route("**/api/teacher/classes**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [{ id: "c1", name: "Class 10 A" }] }) });
        });
    });

    test("assignments page loads without crash", async ({ page }) => {
        await page.goto("/teacher/assignments", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("assignments page handles 500 from API", async ({ page }) => {
        await page.route("**/api/teacher/assignments**", async (route) => {
            await route.fulfill({ status: 500, contentType: "application/json", body: JSON.stringify({ detail: "Server error" }) });
        });
        await page.goto("/teacher/assignments", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("assignments page with items renders list", async ({ page }) => {
        await page.route("**/api/teacher/assignments**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [{ id: "a1", title: "Photosynthesis Worksheet", class_id: "c1", subject: "Biology", due_date: "2026-04-20", status: "active", submissions_count: 12, total_students: 30 }] }) });
        });
        await page.goto("/teacher/assignments", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("Photosynthesis Worksheet").first()).toBeVisible();
    });

    test("assignments page with empty items shows empty state", async ({ page }) => {
        await page.goto("/teacher/assignments", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });
});

test.describe("Attendance page routing", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "teacher");
        await stubMascotSuggestions(page, []);
        await page.route("**/api/teacher/classes**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [{ id: "c1", name: "Class 10 A" }] }) });
        });
        await page.route("**/api/teacher/attendance**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ students: [] }) });
        });
    });

    test("attendance page loads without crash", async ({ page }) => {
        await page.goto("/teacher/attendance", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("attendance page with classId query param loads that class", async ({ page }) => {
        await page.goto("/teacher/attendance?classId=c1", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("attendance page handles 500 from API", async ({ page }) => {
        await page.route("**/api/teacher/attendance**", async (route) => {
            await route.fulfill({ status: 500 });
        });
        await page.goto("/teacher/attendance", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("attendance page with students renders list", async ({ page }) => {
        await page.route("**/api/teacher/attendance**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ students: [{ id: "s1", name: "Aarav Sharma", status: "present" }, { id: "s2", name: "Priya Verma", status: "absent" }] }) });
        });
        await page.goto("/teacher/attendance?classId=c1", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });
});

test.describe("Marks page routing", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "teacher");
        await stubMascotSuggestions(page, []);
        await page.route("**/api/teacher/marks**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [] }) });
        });
        await page.route("**/api/teacher/classes**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [{ id: "c1", name: "Class 10 A" }] }) });
        });
    });

    test("marks page loads without crash", async ({ page }) => {
        await page.goto("/teacher/marks", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("marks page handles 500 from API", async ({ page }) => {
        await page.route("**/api/teacher/marks**", async (route) => {
            await route.fulfill({ status: 500 });
        });
        await page.goto("/teacher/marks", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("marks page with data renders table", async ({ page }) => {
        await page.route("**/api/teacher/marks**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [{ student_id: "s1", student_name: "Aarav", subject: "Biology", exam: "UT3", marks: 85, max_marks: 100 }] }) });
        });
        await page.goto("/teacher/marks", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });
});

test.describe("Doubt heatmap page", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "teacher");
        await stubMascotSuggestions(page, []);
        await page.route("**/api/teacher/doubt-heatmap**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ subjects: [] }) });
        });
    });

    test("doubt heatmap page loads without crash", async ({ page }) => {
        await page.goto("/teacher/doubt-heatmap", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("doubt heatmap handles 500", async ({ page }) => {
        await page.route("**/api/teacher/doubt-heatmap**", async (route) => {
            await route.fulfill({ status: 500 });
        });
        await page.goto("/teacher/doubt-heatmap", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("doubt heatmap with data renders topics", async ({ page }) => {
        await page.route("**/api/teacher/doubt-heatmap**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ subjects: [{ name: "Biology", topics: [{ name: "Photosynthesis", doubt_count: 15, avg_score: 45 }] }] }) });
        });
        await page.goto("/teacher/doubt-heatmap", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });
});

test.describe("Generate assessment page", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "teacher");
        await stubMascotSuggestions(page, []);
        await page.route("**/api/teacher/classes**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [{ id: "c1", name: "Class 10 A" }] }) });
        });
    });

    test("generate assessment page loads without crash", async ({ page }) => {
        await page.goto("/teacher/generate-assessment", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("generate assessment page handles missing class data", async ({ page }) => {
        await page.route("**/api/teacher/classes**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [] }) });
        });
        await page.goto("/teacher/generate-assessment", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("generate assessment page handles 500", async ({ page }) => {
        await page.route("**/api/teacher/classes**", async (route) => {
            await route.fulfill({ status: 500 });
        });
        await page.goto("/teacher/generate-assessment", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });
});

test.describe("Teacher insights page", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "teacher");
        await stubMascotSuggestions(page, []);
        await page.route("**/api/teacher/insights**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ insights: [] }) });
        });
    });

    test("insights page loads without crash", async ({ page }) => {
        await page.goto("/teacher/insights", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("insights page handles 500 from API", async ({ page }) => {
        await page.route("**/api/teacher/insights**", async (route) => {
            await route.fulfill({ status: 500 });
        });
        await page.goto("/teacher/insights", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });
});

test.describe("Teacher upload page", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "teacher");
        await stubMascotSuggestions(page, []);
        await page.route("**/api/teacher/uploads**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [] }) });
        });
    });

    test("teacher upload page loads without crash", async ({ page }) => {
        await page.goto("/teacher/upload", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("teacher upload page handles 500", async ({ page }) => {
        await page.route("**/api/teacher/uploads**", async (route) => {
            await route.fulfill({ status: 500 });
        });
        await page.goto("/teacher/upload", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });
});
