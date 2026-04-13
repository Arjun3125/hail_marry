import { expect, test } from "@playwright/test";

test("admin branding page loads config, extracts palette, and saves settings", async ({ page }) => {
    await page.addInitScript(() => {
        window.localStorage.setItem("vidyaos_access_token", "test-token");
    });

    const state = {
        savedPayload: null as null | Record<string, unknown>,
    };

    await page.route("**/api/branding/config", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                primary_color: "#2563eb",
                secondary_color: "#16a34a",
                font_family: "Inter",
                logo_url: "",
            }),
        });
    });

    await page.route("**/api/branding/extract", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                success: true,
                suggested_palette: {
                    primary: "#112233",
                    secondary: "#445566",
                },
            }),
        });
    });

    await page.route("**/api/branding/save", async (route) => {
        state.savedPayload = route.request().postDataJSON() as Record<string, unknown>;
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({ success: true }),
        });
    });

    await page.goto("/admin/branding");

    await expect(page.getByRole("heading", { name: "Tune the institution identity without affecting platform behavior" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Live Interface Preview" })).toBeVisible();

    const logoUpload = page.getByRole("button", { name: /upload organization logo/i });
    const fileChooserPromise = page.waitForEvent("filechooser");
    await logoUpload.click();
    const fileChooser = await fileChooserPromise;
    await fileChooser.setFiles({
        name: "logo.png",
        mimeType: "image/png",
        buffer: Buffer.from("fake-image"),
    });

    await expect(page.getByText("Palette extracted: primary #112233, secondary #445566.")).toBeVisible();
    await expect(page.locator('input[value="#112233"]').first()).toBeVisible();
    await expect(page.locator('input[value="#445566"]').first()).toBeVisible();

    await page.getByRole("combobox").selectOption({ value: "Poppins" });
    await page.getByRole("button", { name: /save brand settings/i }).click();

    await expect(page.getByText("Brand settings saved. Reload the app shell to see the updated identity everywhere.")).toBeVisible();
    expect(state.savedPayload).toMatchObject({
        primary_color: "#112233",
        secondary_color: "#445566",
        font_family: "Poppins",
    });
});
