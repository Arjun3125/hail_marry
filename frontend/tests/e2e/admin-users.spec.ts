import { expect, test } from "@playwright/test";

test("admin users page supports role updates, activation changes, and guardian bindings", async ({ page }) => {
    await page.addInitScript(() => {
        window.localStorage.setItem("vidyaos_access_token", "test-token");
    });

    const users = [
        {
            id: "student-1",
            name: "Student One",
            email: "student1@example.com",
            role: "student",
            is_active: true,
            last_login: "2026-04-06T09:00:00.000Z",
            ai_queries_30d: 12,
        },
        {
            id: "parent-1",
            name: "Parent One",
            email: "parent1@example.com",
            role: "parent",
            is_active: true,
            last_login: "2026-04-05T08:00:00.000Z",
            ai_queries_30d: 2,
        },
        {
            id: "teacher-1",
            name: "Teacher One",
            email: "teacher1@example.com",
            role: "teacher",
            is_active: true,
            last_login: "2026-04-05T07:00:00.000Z",
            ai_queries_30d: 18,
        },
    ];

    const links: Array<{
        id: string;
        parent_id: string;
        parent_name: string;
        child_id: string;
        child_name: string;
        created_at: string;
    }> = [];

    await page.route("**/api/admin/users", async (route) => {
        if (route.request().method() !== "GET") {
            await route.fallback();
            return;
        }
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify(users),
        });
    });

    await page.route("**/api/admin/parent-links", async (route) => {
        const request = route.request();

        if (request.method() === "GET") {
            await route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify(links),
            });
            return;
        }

        if (request.method() === "POST") {
            const payload = request.postDataJSON() as { parent_id: string; child_id: string };
            const parent = users.find((user) => user.id === payload.parent_id);
            const child = users.find((user) => user.id === payload.child_id);
            links.push({
                id: "link-1",
                parent_id: payload.parent_id,
                parent_name: parent?.name ?? "Unknown Parent",
                child_id: payload.child_id,
                child_name: child?.name ?? "Unknown Student",
                created_at: "2026-04-06T10:00:00.000Z",
            });
            await route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify({ success: true }),
            });
            return;
        }

        await route.fallback();
    });

    await page.route("**/api/admin/parent-links/*", async (route) => {
        if (route.request().method() !== "DELETE") {
            await route.fallback();
            return;
        }
        const id = route.request().url().split("/").pop();
        const index = links.findIndex((link) => link.id === id);
        if (index >= 0) links.splice(index, 1);
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({ success: true }),
        });
    });

    await page.route("**/api/admin/users/*/role", async (route) => {
        const payload = route.request().postDataJSON() as { role: "student" | "teacher" | "admin" | "parent" };
        const userId = route.request().url().split("/").slice(-2)[0];
        const user = users.find((candidate) => candidate.id === userId);
        if (user) user.role = payload.role;
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({ success: true }),
        });
    });

    await page.route("**/api/admin/users/*/deactivate", async (route) => {
        const userId = route.request().url().split("/").slice(-2)[0];
        const user = users.find((candidate) => candidate.id === userId);
        if (user) user.is_active = !user.is_active;
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({ success: true }),
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

    await page.goto("/admin/users");

    await expect(page.getByRole("heading", { name: "Govern the school directory without leaving the control room" })).toBeVisible();
    await expect(page.getByRole("heading", { name: /User directory/i })).toBeVisible();

    const teacherRoleSelect = page.getByLabel("Change role for Teacher One");
    await teacherRoleSelect.selectOption("admin");
    await expect(page.locator("tr").filter({ hasText: "Teacher One" }).getByText("admin", { exact: true })).toBeVisible();

    await page.getByLabel("Guardian", { exact: true }).selectOption("parent-1");
    await page.getByLabel("Student", { exact: true }).selectOption("student-1");
    await page.getByRole("button", { name: /create guardian binding/i }).click();
    await expect(page.getByText("Linked to Student One")).toBeVisible();

    await page.getByLabel("Delete link for Parent One and Student One").click();
    await expect(page.getByText("No guardian bindings yet")).toBeVisible();

    await page.getByLabel("Disable Student One").click();
    await expect(page.locator("tr").filter({ hasText: "Student One" }).getByText("Disabled", { exact: true })).toBeVisible();
});
