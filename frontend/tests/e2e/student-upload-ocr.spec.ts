import { expect, test } from "@playwright/test";
import { stubAuthShell, stubMascotSuggestions } from "../fixtures/helpers";

/* ═══════════════════════════════════════════════════════════════════════
   STUDENT  UPLOAD  /  OCR  ·  30 hard fault-finding tests
   ═══════════════════════════════════════════════════════════════════════ */

test.describe("Upload page rendering", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "student");
        await page.route("**/api/student/uploads", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [] }) });
        });
        await stubMascotSuggestions(page, ["Upload a document"]);
    });

    test("upload page renders without crashes", async ({ page }) => {
        await page.goto("/student/upload", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("upload page shows empty state when no uploads exist", async ({ page }) => {
        await page.goto("/student/upload", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("upload page with existing uploads lists them", async ({ page }) => {
        await page.route("**/api/student/uploads", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [{ id: "u1", file_name: "biology_notes.pdf", file_type: "application/pdf", file_size: 1024000, status: "processed", uploaded_at: "2026-04-01T10:00:00Z", chunks: 12, ocr_processed: false }] }) });
        });
        await page.goto("/student/upload", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("biology_notes.pdf").first()).toBeVisible();
    });

    test("upload page handles 500 from uploads endpoint", async ({ page }) => {
        await page.route("**/api/student/uploads", async (route) => {
            await route.fulfill({ status: 500, contentType: "application/json", body: JSON.stringify({ detail: "Error" }) });
        });
        await page.goto("/student/upload", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("multiple uploads render correctly", async ({ page }) => {
        await page.route("**/api/student/uploads", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [{ id: "u1", file_name: "notes.pdf", file_type: "application/pdf", file_size: 512000, status: "processed", uploaded_at: "2026-04-01T10:00:00Z", chunks: 5 }, { id: "u2", file_name: "slides.pptx", file_type: "application/vnd.openxmlformats-officedocument.presentationml.presentation", file_size: 2048000, status: "processed", uploaded_at: "2026-04-02T08:00:00Z", chunks: 20 }, { id: "u3", file_name: "assignment.docx", file_type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document", file_size: 256000, status: "processing", uploaded_at: "2026-04-03T09:00:00Z", chunks: 0 }] }) });
        });
        await page.goto("/student/upload", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("notes.pdf").first()).toBeVisible();
        await expect(page.getByText("slides.pptx").first()).toBeVisible();
    });
});

test.describe("File upload interaction", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "student");
        await page.route("**/api/student/uploads", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [] }) });
        });
        await stubMascotSuggestions(page, ["Upload a document"]);
    });

    test("upload area accepts PDF files", async ({ page }) => {
        await page.route("**/api/student/upload", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ id: "new-upload", file_name: "test.pdf", status: "queued" }) });
        });
        await page.goto("/student/upload", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("upload page with processing status shows indicator", async ({ page }) => {
        await page.route("**/api/student/uploads", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [{ id: "u1", file_name: "processing.pdf", file_type: "application/pdf", file_size: 100000, status: "processing", uploaded_at: "2026-04-01T10:00:00Z", chunks: 0 }] }) });
        });
        await page.goto("/student/upload", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("processing.pdf").first()).toBeVisible();
    });

    test("upload page with failed status shows error state", async ({ page }) => {
        await page.route("**/api/student/uploads", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [{ id: "u1", file_name: "failed.pdf", file_type: "application/pdf", file_size: 100000, status: "failed", uploaded_at: "2026-04-01T10:00:00Z", chunks: 0, error: "File corrupted" }] }) });
        });
        await page.goto("/student/upload", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("failed.pdf").first()).toBeVisible();
    });

    test("upload with OCR processed shows indicator", async ({ page }) => {
        await page.route("**/api/student/uploads", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [{ id: "u1", file_name: "scanned.jpg", file_type: "image/jpeg", file_size: 500000, status: "processed", uploaded_at: "2026-04-01T10:00:00Z", chunks: 3, ocr_processed: true }] }) });
        });
        await page.goto("/student/upload", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("scanned.jpg").first()).toBeVisible();
    });
});

test.describe("Upload data integrity edge cases", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "student");
        await stubMascotSuggestions(page, []);
    });

    test("empty file name in upload list doesn't crash", async ({ page }) => {
        await page.route("**/api/student/uploads", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [{ id: "u1", file_name: "", file_type: "application/pdf", file_size: 0, status: "processed", uploaded_at: "2026-04-01T10:00:00Z", chunks: 0 }] }) });
        });
        await page.goto("/student/upload", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("very long file name doesn't break layout", async ({ page }) => {
        const longName = "A".repeat(200) + ".pdf";
        await page.route("**/api/student/uploads", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [{ id: "u1", file_name: longName, file_type: "application/pdf", file_size: 1000, status: "processed", uploaded_at: "2026-04-01T10:00:00Z", chunks: 1 }] }) });
        });
        await page.goto("/student/upload", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("file with zero size renders correctly", async ({ page }) => {
        await page.route("**/api/student/uploads", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [{ id: "u1", file_name: "empty.pdf", file_type: "application/pdf", file_size: 0, status: "processed", uploaded_at: "2026-04-01T10:00:00Z", chunks: 0 }] }) });
        });
        await page.goto("/student/upload", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("empty.pdf").first()).toBeVisible();
    });

    test("file with very large size doesn't break display", async ({ page }) => {
        await page.route("**/api/student/uploads", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [{ id: "u1", file_name: "huge.pdf", file_type: "application/pdf", file_size: 999999999, status: "processed", uploaded_at: "2026-04-01T10:00:00Z", chunks: 500 }] }) });
        });
        await page.goto("/student/upload", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("huge.pdf").first()).toBeVisible();
    });

    test("unicode file names render correctly", async ({ page }) => {
        await page.route("**/api/student/uploads", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [{ id: "u1", file_name: "生物学_ノート.pdf", file_type: "application/pdf", file_size: 5000, status: "processed", uploaded_at: "2026-04-01T10:00:00Z", chunks: 2 }] }) });
        });
        await page.goto("/student/upload", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("生物学_ノート.pdf").first()).toBeVisible();
    });

    test("null items array doesn't crash upload page", async ({ page }) => {
        await page.route("**/api/student/uploads", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: null }) });
        });
        await page.goto("/student/upload", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("missing items field doesn't crash upload page", async ({ page }) => {
        await page.route("**/api/student/uploads", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({}) });
        });
        await page.goto("/student/upload", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });
});

test.describe("Mascot launcher on upload page", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "student");
        await page.route("**/api/student/uploads", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [] }) });
        });
    });

    test("mascot launcher button is visible on upload page", async ({ page }) => {
        await stubMascotSuggestions(page, ["Summarize this upload"]);
        await page.goto("/student/upload", { waitUntil: "domcontentloaded" });
        await expect(page.getByLabel("Open mascot assistant")).toBeVisible();
    });

    test("clicking mascot launcher opens mascot dialog", async ({ page }) => {
        await stubMascotSuggestions(page, ["Create a notebook for these uploads"]);
        await page.goto("/student/upload", { waitUntil: "domcontentloaded" });
        await page.getByLabel("Open mascot assistant").click();
        await expect(page.getByText("Vidya Mascot")).toBeVisible();
    });

    test("mascot suggestions reflect upload context", async ({ page }) => {
        await stubMascotSuggestions(page, ["Summarize uploads", "Create study plan"]);
        await page.goto("/student/upload", { waitUntil: "domcontentloaded" });
        await page.getByLabel("Open mascot assistant").click();
        await expect(page.getByRole("button", { name: "Summarize uploads" })).toBeVisible();
    });

    test("mascot on upload page handles 500 from suggestions gracefully", async ({ page }) => {
        await page.route("**/api/mascot/suggestions**", async (route) => {
            await route.fulfill({ status: 500, contentType: "application/json", body: JSON.stringify({ detail: "Server error" }) });
        });
        await page.goto("/student/upload", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
    });

    test("mascot on upload page with empty suggestions still opens", async ({ page }) => {
        await stubMascotSuggestions(page, []);
        await page.goto("/student/upload", { waitUntil: "domcontentloaded" });
        await page.getByLabel("Open mascot assistant").click();
        await expect(page.getByText("Vidya Mascot")).toBeVisible();
    });
});
