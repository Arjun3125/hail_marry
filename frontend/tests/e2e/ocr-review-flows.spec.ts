import { expect, test } from "@playwright/test";
import { authenticateAs } from "../fixtures/auth";

test("admin setup wizard completes setup flow successfully", async ({ page }) => {
    await authenticateAs(page, "admin");

    await page.goto("/admin/setup-wizard", { waitUntil: "domcontentloaded" });

    await expect(page.getByRole("heading", { name: /Set up the institution in five focused steps/i })).toBeVisible();
    await page.getByRole("button", { name: /Next step/i }).click();

    await expect(page.getByRole("heading", { name: /Define the grade and section shape/i })).toBeVisible();
    await page.getByRole("button", { name: /Next step/i }).click();

    await expect(page.getByRole("heading", { name: /Map subjects to accountable teachers/i })).toBeVisible();
    await page.getByRole("button", { name: /Next step/i }).click();

    await expect(page.getByRole("heading", { name: /Choose whether this environment starts/i })).toBeVisible();
    await page.getByRole("button", { name: /Next step/i }).click();

    await expect(page.getByRole("heading", { name: /Pick the first operational task/i })).toBeVisible();
    await page.getByRole("link", { name: /Continue to first action/i }).click();

    // After clicking continue, we should end up on the first action page (default /admin/dashboard)
    await expect(page).toHaveURL(/.*\/admin\/dashboard/);
});

test("student assignments page surfaces OCR review warnings after image submission", async ({ page }) => {
    await authenticateAs(page, "student");
    await page.route("**/api/student/assignments/*/submit", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                ocr_review_required: true,
                ocr_warning: "Handwriting was unclear in two answer lines.",
                ocr_confidence: 0.74,
            }),
        });
    });

    await page.goto("/student/assignments", { waitUntil: "domcontentloaded" });

    await expect(page.getByRole("heading", { name: /clear assignment ledger/i })).toBeVisible();
    await expect(page.getByRole("button", { name: /SUBMIT WORK/i }).first()).toBeVisible();

    await page.getByRole("button", { name: /SUBMIT WORK/i }).first().click();
    await page.getByRole("button", { name: /^File Upload/i }).click();

    await page.locator('label:has-text("Choose file from phone or laptop") input[type="file"]').setInputFiles({
        name: "worksheet-photo.jpg",
        mimeType: "image/jpeg",
        buffer: Buffer.from("fake-image-binary"),
    });

    await expect(page.getByText(/^Work submitted for /i)).toBeVisible();
    await expect(page.getByText(/File uploaded and linked to this assignment/i)).toBeVisible();
    await expect(page.getByText(/OCR scanning alert/i)).toBeVisible();
    await expect(page.getByText(/Clarity at 74%/i)).toBeVisible();
    await expect(page.getByText(/Handwriting was unclear in two answer lines/i)).toBeVisible();
});

test("teacher classes page supports OCR preview, edit, and confirm import for student rosters", async ({ page }) => {
    await authenticateAs(page, "teacher");
    await page.route("**/api/teacher/classes", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify([
                {
                    id: "class-1",
                    name: "Class 10 A",
                    grade: "10",
                    students: [{ id: "student-1", name: "Existing Student", email: "existing@school.com", roll_number: "1" }],
                    subjects: [{ id: "subject-1", name: "Biology" }],
                },
            ]),
        });
    });

    await page.route("**/api/teacher/onboard/students?preview=1", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                preview_rows: [
                    {
                        name: "Aarav Patil",
                        email: "aarav@school.com",
                        password: "Student123!",
                    },
                ],
                errors: ["One OCR row had an ambiguous surname."],
                ocr_review_required: true,
                ocr_warning: "Low confidence in one handwritten email address.",
                ocr_confidence: 0.81,
                ocr_unmatched_lines: ["Aarav P. / unclear email"],
            }),
        });
    });

    await page.route("**/api/teacher/onboard/students", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                created_count: 1,
                message: "Successfully onboarded 1 students.",
                ocr_review_required: false,
                ocr_warning: null,
                ocr_confidence: 0.99,
                ocr_unmatched_lines: [],
            }),
        });
    });

    await page.goto("/teacher/classes", { waitUntil: "domcontentloaded" });

    await expect(page.getByRole("heading", { name: /Operate class rosters and parent-facing actions from one desk/i })).toBeVisible();
    await page.locator('input[type="file"]').setInputFiles({
        name: "student-roster.jpg",
        mimeType: "image/jpeg",
        buffer: Buffer.from("fake-image-binary"),
    });

    await expect(page.getByText(/Review Extracted Students/i)).toBeVisible();
    await expect(page.getByText(/OCR confidence 81%/i)).toBeVisible();
    await expect(page.getByText(/Review recommended before final import/i)).toBeVisible();
    await expect(page.getByText(/One OCR row had an ambiguous surname/i)).toBeVisible();

    await page.locator('input[value="aarav@school.com"]').first().fill("aarav.patil@school.com");
    await page.getByRole("button", { name: /Confirm Import/i }).click();

    await expect(page.getByText(/Successfully onboarded 1 students/i)).toBeVisible();
    await expect(page.getByText("Imported 1 student.")).toBeVisible();
});

test("teacher classes page surfaces OCR preview failures before any import happens", async ({ page }) => {
    await authenticateAs(page, "teacher");
    await page.route("**/api/teacher/classes", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify([
                {
                    id: "class-1",
                    name: "Class 9 B",
                    grade: "9",
                    students: [],
                    subjects: [{ id: "subject-1", name: "History" }],
                },
            ]),
        });
    });

    await page.route("**/api/teacher/onboard/students?preview=1", async (route) => {
        await route.fulfill({
            status: 400,
            contentType: "application/json",
            body: JSON.stringify({
                detail: "No readable names found in the file",
            }),
        });
    });

    await page.goto("/teacher/classes", { waitUntil: "domcontentloaded" });

    await expect(page.getByRole("heading", { name: /Operate class rosters and parent-facing actions from one desk/i })).toBeVisible();
    await page.locator('input[type="file"]').setInputFiles({
        name: "bad-student-roster.jpg",
        mimeType: "image/jpeg",
        buffer: Buffer.from("fake-image-binary"),
    });

    await expect(page.getByText(/No readable names found in the file/i)).toBeVisible();
    await expect(page.getByText(/Review Extracted Students/i)).toHaveCount(0);
});

