import { expect, test } from "@playwright/test";

test("landing page renders", async ({ page }) => {
    await page.goto("/", { waitUntil: "domcontentloaded" });
    await expect(page.getByRole("link", { name: /Login To Platform/i }).first()).toBeVisible();
    await expect(page.getByRole("navigation").getByText("VidyaOS", { exact: true })).toBeVisible();
});
