import { expect, test } from "@playwright/test";

test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
        window.localStorage.setItem("vidyaos_access_token", "test-token");
    });

    // Set demo role cookie for teacher user
    await page.context().addCookies([{
        name: 'demo_role',
        value: 'teacher',
        domain: 'localhost',
        path: '/',
    }]);

    await page.route("**/api/branding/config", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                name: "VidyaOS",
                logo_url: null,
                primary_color: "#2563eb",
                secondary_color: "#0f172a",
                accent_color: "#f59e0b",
                font_family: "Inter",
                theme_style: "modern",
            }),
        });
    });
});

test("teacher attendance page imports OCR attendance and surfaces review metadata", async ({ page }) => {
    let attendanceFetchCount = 0;
    const todayIso = new Date().toISOString().split("T")[0];

    await page.route("**/api/teacher/classes", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify([
                {
                    id: "class-1",
                    name: "Class 10 A",
                    students: [
                        { id: "student-1", name: "Aarav Patil", roll_number: "1" },
                        { id: "student-2", name: "Diya Shah", roll_number: "2" },
                    ],
                },
            ]),
        });
    });

    await page.route("**/api/teacher/attendance/class-1", async (route) => {
        attendanceFetchCount += 1;
        const body = attendanceFetchCount === 1
            ? []
            : [
                { student_id: "student-1", date: todayIso, status: "present" },
                { student_id: "student-2", date: todayIso, status: "late" },
            ];
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify(body),
        });
    });

    await page.route("**/api/teacher/attendance/csv-import**", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                success: true,
                imported: 2,
                errors: ["Row 4: student blurry row not in class"],
                ocr_review_required: true,
                ocr_warning: "Low confidence on one handwritten surname.",
                ocr_confidence: 0.79,
                ocr_unmatched_lines: 1,
            }),
        });
    });

    await page.goto("/teacher/attendance", { waitUntil: "domcontentloaded" });

    await expect(page.getByRole("heading", { name: "Mark Attendance" })).toBeVisible();
    await page.locator('input[type="file"]').setInputFiles({
        name: "attendance-sheet.jpg",
        mimeType: "image/jpeg",
        buffer: Buffer.from("fake-image-binary"),
    });

    await expect(page.getByText(/Imported 2 attendance rows/i)).toBeVisible();
    await expect(page.getByText(/OCR confidence 79%/i)).toBeVisible();
    await expect(page.getByText(/OCR review recommended/i)).toBeVisible();
    await expect(page.getByText(/Low confidence on one handwritten surname/i)).toBeVisible();
    await expect(page.getByText(/student blurry row not in class/i)).toBeVisible();
    await expect(page.getByRole("button", { name: /late/i })).toBeVisible();
});

test("teacher marks page imports OCR marks after creating an exam and surfaces review metadata", async ({ page }) => {
    await page.route("**/api/teacher/classes", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify([
                {
                    id: "class-1",
                    name: "Class 10 A",
                    students: [
                        { id: "student-1", name: "Aarav Patil", roll_number: "1" },
                        { id: "student-2", name: "Diya Shah", roll_number: "2" },
                    ],
                    subjects: [{ id: "subject-1", name: "Biology" }],
                },
            ]),
        });
    });

    await page.route("**/api/teacher/exams", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                success: true,
                exam_id: "exam-1",
                name: "Photosynthesis Unit Test",
            }),
        });
    });

    await page.route("**/api/teacher/marks/csv-import**", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                success: true,
                imported: 2,
                errors: ["Row 5: student unclear entry not in class"],
                ocr_review_required: true,
                ocr_warning: "One handwritten score needed review.",
                ocr_confidence: 0.83,
                ocr_unmatched_lines: 1,
            }),
        });
    });

    await page.goto("/teacher/marks", { waitUntil: "domcontentloaded" });

    await expect(page.getByRole("heading", { name: "Enter Assessment Marks" })).toBeVisible();
    await page.getByPlaceholder("Exam name").fill("Photosynthesis Unit Test");
    await page.locator('input[type="file"]').setInputFiles({
        name: "marks-sheet.jpg",
        mimeType: "image/jpeg",
        buffer: Buffer.from("fake-image-binary"),
    });

    await expect(page.getByText(/Imported 2 marks rows/i)).toBeVisible();
    await expect(page.getByText(/OCR confidence 83%/i)).toBeVisible();
    await expect(page.getByText(/OCR review recommended/i)).toBeVisible();
    await expect(page.getByText(/One handwritten score needed review/i)).toBeVisible();
    await expect(page.getByText(/student unclear entry not in class/i)).toBeVisible();
});

