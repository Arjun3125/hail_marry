import { expect, test } from "@playwright/test";
import { authenticateAs } from "../fixtures/auth";

test("admin setup wizard supports OCR preview, edit, and confirm import for teacher rosters", async ({ page }) => {
    await authenticateAs(page, "admin");
    await page.route("**/api/admin/onboard-teachers?preview=1", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                preview_rows: [
                    {
                        name: "Priya Sharma",
                        email: "priya@school.com",
                        password: "Welcome@123",
                    },
                ],
                errors: ["One row needed manual OCR cleanup."],
                ocr_review_required: true,
                ocr_warning: "Low confidence in one handwritten email address.",
                ocr_confidence: 0.78,
                ocr_unmatched_lines: ["Priya S. / unclear email"],
            }),
        });
    });

    await page.route("**/api/admin/onboard-teachers", async (route) => {
        if (route.request().method() !== "POST") {
            await route.fallback();
            return;
        }
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                created: 1,
                ocr_review_required: false,
                ocr_warning: null,
                ocr_confidence: 0.99,
                ocr_unmatched_lines: [],
            }),
        });
    });

    await page.goto("/admin/setup-wizard");

    await expect(page.getByRole("heading", { name: /Initialize the institution graph in a controlled sequence/i })).toBeVisible();
    await page.getByRole("button", { name: /Advance Pipeline/i }).click();
    await page.getByRole("button", { name: /Advance Pipeline/i }).click();

    await expect(page.getByRole("heading", { name: /Onboard Educators/i })).toBeVisible();
    await page.locator('input[type="file"]').setInputFiles({
        name: "teacher-roster.jpg",
        mimeType: "image/jpeg",
        buffer: Buffer.from("fake-image-binary"),
    });

    await expect(page.getByText(/Extracted Dataset/i)).toBeVisible();
    await expect(page.getByText(/OCR confidence 78%/i)).toBeVisible();
    await expect(page.getByText(/Review recommended before final import/i)).toBeVisible();
    await expect(page.getByText(/One row needed manual OCR cleanup/i)).toBeVisible();
    await expect(page.locator('input[value="Priya Sharma"]').first()).toBeVisible();

    await page.locator('input[value="priya@school.com"]').first().fill("priya.sharma@school.com");
    await page.getByRole("button", { name: /Execute Import/i }).click();

    await expect(page.getByText(/Imported 1 records successfully/i)).toBeVisible();
});

test("student assignments page surfaces OCR review warnings after image submission", async ({ page }) => {
    await authenticateAs(page, "student");
    let assignmentListCalls = 0;

    await page.route("**/api/student/assignments", async (route) => {
        assignmentListCalls += 1;
        const payload = assignmentListCalls === 1
            ? [
                {
                    id: "assignment-1",
                    title: "Photosynthesis Worksheet",
                    subject: "Biology",
                    due: "2026-03-31",
                    status: "pending",
                },
            ]
            : [
                {
                    id: "assignment-1",
                    title: "Photosynthesis Worksheet",
                    subject: "Biology",
                    due: "2026-03-31",
                    status: "submitted",
                    has_submission: true,
                    submitted_at: "2026-03-29 18:40",
                },
            ];
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify(payload),
        });
    });

    await page.route("**/api/student/assignments/assignment-1/submit", async (route) => {
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

    await page.goto("/student/assignments");

    await expect(page.getByRole("heading", { name: /clear assignment ledger/i })).toBeVisible();
    await expect(page.getByText("Photosynthesis Worksheet")).toBeVisible();

    await page.locator('input[type="file"]').setInputFiles({
        name: "worksheet-photo.jpg",
        mimeType: "image/jpeg",
        buffer: Buffer.from("fake-image-binary"),
    });

    const assignmentCard = page.locator("div").filter({ hasText: "Photosynthesis Worksheet" }).first();
    await expect(page.getByText(/Clarity at 74%/i)).toBeVisible();
    await expect(page.getByText(/Please review your image/i)).toBeVisible();
    await expect(page.getByText(/Handwriting was unclear in two answer lines/i)).toBeVisible();
    await expect(assignmentCard.getByText("submitted", { exact: true })).toBeVisible();
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

    await page.goto("/teacher/classes");

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

    await page.goto("/teacher/classes");

    await expect(page.getByRole("heading", { name: /Operate class rosters and parent-facing actions from one desk/i })).toBeVisible();
    await page.locator('input[type="file"]').setInputFiles({
        name: "bad-student-roster.jpg",
        mimeType: "image/jpeg",
        buffer: Buffer.from("fake-image-binary"),
    });

    await expect(page.getByText(/No readable names found in the file/i)).toBeVisible();
    await expect(page.getByText(/Review Extracted Students/i)).toHaveCount(0);
});
