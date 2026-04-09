import { expect, test } from "@playwright/test";

test("parent reports page shows monthly snapshot and focus subjects", async ({ page }) => {
    await page.addInitScript(() => {
        window.localStorage.setItem("vidyaos_access_token", "test-token");
    });

    await page.route("**/api/parent/reports", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                child: { id: "child-1", name: "Aarav" },
                attendance_pct_30d: 91,
                weak_subjects: ["Science", "History"],
                summary: "Aarav stayed consistent overall, with extra attention needed in Science and History.",
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

    await page.goto("/parent/reports");

    await expect(page.getByRole("heading", { name: "See the month in plain academic language" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Monthly story" })).toBeVisible();
    await expect(page.getByText("Aarav stayed consistent overall, with extra attention needed in Science and History.")).toBeVisible();
    await expect(page.getByText("Science", { exact: true })).toBeVisible();
    await expect(page.getByText("History", { exact: true })).toBeVisible();
    await expect(page.getByText("Watch closely").first()).toBeVisible();
});
