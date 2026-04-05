import { expect, test } from "@playwright/test";

test("Verify demo role entry points load current dashboards", async ({ page }) => {
    await page.goto("/demo");
    await expect(page.getByRole("heading", { name: /Explore as/i })).toBeVisible();

    await page.getByRole("button", { name: /Student/i }).first().click();
    await page.waitForURL("**/student/overview");
    await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();

    await page.goto("/demo");
    await page.getByRole("button", { name: /Teacher/i }).first().click();
    await page.waitForURL("**/teacher/dashboard");
    await expect(page.getByText(/Educator Console/i)).toBeVisible();

    await page.goto("/demo");
    await page.getByRole("button", { name: /Admin/i }).first().click();
    await page.waitForURL("**/admin/dashboard");
    await expect(page.getByRole("heading", { name: /Admin Dashboard/i })).toBeVisible();
});
