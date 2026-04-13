import { expect, test } from "@playwright/test";

test("landing page renders @smoke", async ({ page }) => {
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

    await page.goto("/");
    await expect(page.getByText("VidyaOS").first()).toBeVisible();
    await expect(page.getByRole("heading", { name: /One product for classroom work/i })).toBeVisible();
});
