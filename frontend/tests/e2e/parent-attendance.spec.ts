import { expect, test } from "@playwright/test";

test("parent attendance page shows attendance story and recent records", async ({ page }) => {
    await page.addInitScript(() => {
        window.localStorage.setItem("vidyaos_access_token", "test-token");
    });

    await page.route("**/api/parent/attendance", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify([
                { date: "2026-04-04", day: "Friday", status: "present" },
                { date: "2026-04-03", day: "Thursday", status: "absent" },
                { date: "2026-04-02", day: "Wednesday", status: "late" },
            ]),
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

    await page.goto("/parent/attendance");

    await expect(page.getByRole("heading", { name: "See the attendance story without operational noise" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Recent record" })).toBeVisible();
    await expect(page.getByText("2026-04-04")).toBeVisible();
    await expect(page.getByText("Friday")).toBeVisible();
    await expect(page.getByText("present", { exact: true })).toBeVisible();
    await expect(page.getByText("There is 1 recorded absence in the current list, so this week may need a short follow-up conversation.")).toBeVisible();
});
