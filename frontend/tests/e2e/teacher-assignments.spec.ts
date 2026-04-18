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

test("teacher assignments page creates a new assignment and refreshes the board", async ({ page }) => {
    let assignments = [
        {
            id: "assignment-1",
            title: "Cell Structure Worksheet",
            subject: "Biology",
            due_date: "2026-04-10",
            submissions: 12,
        },
    ];

    await page.route("**/api/teacher/classes", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify([
                {
                    id: "class-1",
                    name: "Class 10 A",
                    subjects: [
                        { id: "subject-1", name: "Biology" },
                        { id: "subject-2", name: "Chemistry" },
                    ],
                },
            ]),
        });
    });

    await page.route("**/api/teacher/assignments", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify(assignments),
        });
    });

    await page.route("**/api/teacher/assignments", async (route) => {
        if (route.request().method() !== "POST") {
            await route.fallback();
            return;
        }
        assignments = [
            {
                id: "assignment-2",
                title: "Photosynthesis Reflection",
                subject: "Biology",
                due_date: "2026-04-12",
                submissions: 0,
            },
            ...assignments,
        ];
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({ success: true }),
        });
    });

    await page.goto("/teacher/assignments", { waitUntil: "domcontentloaded" });

    await expect(page.getByRole("heading", { name: "Manage Assignments" })).toBeVisible({ timeout: 10000 });
    await expect(page.getByText("Cell Structure Worksheet")).toBeVisible();

    await page.getByPlaceholder("Assignment title").fill("Photosynthesis Reflection");
    await page.locator("textarea").fill("Write a short explanation of photosynthesis in your own words.");
    await page.locator('input[type="date"]').fill("2026-04-12");
    await page.getByRole("button", { name: /Create Assignment/i }).click();

    await expect(page.getByText(/created successfully/i)).toBeVisible();
    await expect(page.getByRole("heading", { name: "Photosynthesis Reflection" })).toBeVisible();
    await expect(page.getByText("0 submissions")).toBeVisible();
});
