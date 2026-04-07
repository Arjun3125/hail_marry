import { expect, test } from "@playwright/test";

test("parent assistant page shows supportive entry shell and mascot workspace", async ({ page }) => {
    await page.addInitScript(() => {
        window.localStorage.setItem("vidyaos_access_token", "test-token");
    });

    await page.route("**/api/mascot/suggestions**", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                suggestions: ["Show attendance summary", "Open progress report", "Summarize recent marks"],
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

    await page.goto("/parent/assistant");

    await expect(page.getByRole("heading", { name: "Parent Assistant" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Best ways to use it" })).toBeVisible();
    await expect(page.getByText("Progress summary")).toBeVisible();
    await expect(page.getByText("Supportive next steps")).toBeVisible();
    await expect(page.getByText("Vidya Mascot")).toBeVisible();
    await expect(page.getByText("Show attendance summary")).toBeVisible();
});
