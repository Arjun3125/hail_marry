import { expect, test } from "@playwright/test";

test("admin timetable page supports generation and manual slot changes", async ({ page }) => {
    await page.addInitScript(() => {
        window.localStorage.setItem("vidyaos_access_token", "test-token");
    });

    const classes = [
        {
            id: "class-1",
            name: "Grade 8 A",
            grade: "8",
            subjects: [
                { id: "math", name: "Mathematics" },
                { id: "science", name: "Science" },
            ],
        },
    ];
    const users = [
        { id: "teacher-1", name: "Teacher One", role: "teacher", is_active: true },
        { id: "admin-1", name: "Admin One", role: "admin", is_active: true },
    ];
    let slots = [
        {
            id: "slot-1",
            class_id: "class-1",
            subject_id: "math",
            subject: "Mathematics",
            teacher_id: "teacher-1",
            teacher: "Teacher One",
            day_of_week: 0,
            start_time: "09:00",
            end_time: "09:45",
        },
    ];

    await page.route("**/api/admin/classes", async (route) => {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(classes) });
    });

    await page.route("**/api/admin/users", async (route) => {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(users) });
    });

    await page.route("**/api/admin/timetable/class-1", async (route) => {
        if (route.request().method() === "GET") {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(slots) });
            return;
        }
        await route.fallback();
    });

    await page.route("**/api/admin/timetable", async (route) => {
        if (route.request().method() === "POST") {
            const payload = route.request().postDataJSON() as {
                class_id: string;
                subject_id: string;
                teacher_id: string;
                day_of_week: number;
                start_time: string;
                end_time: string;
            };
            slots = [
                ...slots,
                {
                    id: "slot-2",
                    class_id: payload.class_id,
                    subject_id: payload.subject_id,
                    subject: payload.subject_id === "science" ? "Science" : "Mathematics",
                    teacher_id: payload.teacher_id,
                    teacher: payload.teacher_id === "teacher-1" ? "Teacher One" : "Admin One",
                    day_of_week: payload.day_of_week,
                    start_time: payload.start_time,
                    end_time: payload.end_time,
                },
            ];
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ success: true }) });
            return;
        }
        await route.fallback();
    });

    await page.route("**/api/admin/timetable/slot-1", async (route) => {
        if (route.request().method() === "DELETE") {
            slots = slots.filter((slot) => slot.id !== "slot-1");
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ success: true }) });
            return;
        }
        await route.fallback();
    });

    await page.route("**/api/admin/timetable/generate", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                success: true,
                class_balance_score: 0.91,
                assignments: [
                    {
                        class_id: "class-1",
                        subject_id: "math",
                        teacher_id: "teacher-1",
                        day: 0,
                        period: 1,
                        start_time: "09:00",
                        end_time: "09:45",
                    },
                ],
                applied: false,
            }),
        });
    });

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

    await page.goto("/admin/timetable");

    await expect(page.getByRole("heading", { name: "Keep the school timetable editable and generation-safe" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Class Timetable" })).toBeVisible();
    const timetableTable = page.getByRole("table");
    await expect(timetableTable.getByText("Mathematics")).toBeVisible();

    await page.getByLabel("Subject").selectOption("science");
    await page.getByLabel("Teacher", { exact: true }).selectOption("admin-1");
    await page.getByLabel("Start time").fill("10:00");
    await page.getByLabel("End time").fill("10:45");
    await page.getByRole("button", { name: /add slot/i }).click();
    await expect(timetableTable.getByText("Science")).toBeVisible();

    await timetableTable.getByRole("button", { name: /^delete$/i }).first().click();
    await expect(timetableTable.getByText("Mathematics")).toHaveCount(0);

    await page.getByRole("button", { name: /generate timetable/i }).click();
    await expect(page.getByText("Generated 1 slots.")).toBeVisible();
    await expect(page.getByText("Class balance score: 0.91")).toBeVisible();
});
