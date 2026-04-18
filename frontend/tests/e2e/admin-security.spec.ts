import { expect, test } from "@playwright/test";

test("admin security page renders audit metrics and audit trail", async ({ page }) => {
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

    await page.route("**/api/admin/security", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify([
                {
                    id: "log-1",
                    user: "Admin User",
                    action: "login.failed",
                    entity_type: "auth",
                    metadata: { ip: "127.0.0.1", reason: "invalid_password" },
                    date: "2026-04-06T08:00:00.000Z",
                },
                {
                    id: "log-2",
                    user: "Security Lead",
                    action: "policy.updated",
                    entity_type: "rbac",
                    metadata: { policy: "teacher_scope" },
                    date: "2026-04-05T10:30:00.000Z",
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

    await page.goto("/admin/security", { waitUntil: "domcontentloaded" });

    await expect(page.getByRole("heading", { name: "Keep security review disciplined and actor-focused" })).toBeVisible();
    await expect(page.getByRole("heading", { name: /Audit trail/i })).toBeVisible();
    await expect(page.getByText("Security posture")).toBeVisible();
    const auditTable = page.getByRole("table");
    await expect(auditTable.getByText("login.failed", { exact: true })).toBeVisible();
    await expect(auditTable.getByText("policy.updated", { exact: true })).toBeVisible();
    await expect(page.getByText("invalid_password")).toBeVisible();
});

