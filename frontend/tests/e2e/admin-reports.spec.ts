import { expect, test } from "@playwright/test";

test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
        window.localStorage.setItem("vidyaos_access_token", "test-token");
    });

    // Set demo role cookie for admin user
    await page.context().addCookies([{
        name: 'demo_role',
        value: 'admin',
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

test("admin reports page generates a report and shows recent output metadata", async ({ page }) => {
    await page.route("**/api/admin/reports/attendance", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify([
                {
                    class_name: "Class 10 A",
                    attendance_pct: 93,
                    present: 28,
                    absent: 2,
                },
            ]),
        });
    });

    await page.goto("/admin/reports", { waitUntil: "domcontentloaded" });

    await expect(page.getByRole("heading", { name: "Generate school reports without leaving the academic workflow" })).toBeVisible();
    await page.getByRole("button", { name: "Generate" }).first().click();

    await expect(page.getByRole("heading", { name: "Attendance Report" })).toBeVisible();
    await expect(page.getByText(/Class 10 A/i)).toBeVisible();
    await expect(page.getByText(/attendance_pct/i)).toBeVisible();
    await expect(page.getByText("Rows", { exact: true })).toBeVisible();
});

