import { expect, test } from "@playwright/test";

test("landing page renders", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("link", { name: "Login" })).toBeVisible();
    await expect(page.getByRole("navigation").getByText("AIaaS", { exact: true })).toBeVisible();
});
