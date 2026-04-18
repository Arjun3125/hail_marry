import { expect, test } from "@playwright/test";

test("parent results page shows academic snapshot and subject breakdown", async ({ page }) => {
    await page.addInitScript(() => {
        window.localStorage.setItem("vidyaos_access_token", "test-token");
    });

    // Set demo role cookie for parent user
    await page.context().addCookies([{
        name: 'demo_role',
        value: 'parent',
        domain: 'localhost',
        path: '/',
    }]);

    await page.route("**/api/parent/results", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify([
                {
                    name: "Mathematics",
                    avg: 88,
                    exams: [
                        { name: "Unit Test 3", marks: 44, max: 50 },
                        { name: "Midterm", marks: 82, max: 100 },
                    ],
                },
                {
                    name: "Science",
                    avg: 79,
                    exams: [
                        { name: "Unit Test 3", marks: 39, max: 50 },
                    ],
                },
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

    await page.goto("/parent/results", { waitUntil: "domcontentloaded" });

    await expect(page.getByRole("heading", { name: "Read academic progress clearly before looking at raw marks" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Subject performance" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Mathematics" })).toBeVisible();
    await expect(page.getByText("Average score: 88%")).toBeVisible();
    await expect(page.getByText("44 / 50")).toBeVisible();
    await expect(page.getByText("Mathematics is currently the strongest subject with an average of 88%.")).toBeVisible();
});

