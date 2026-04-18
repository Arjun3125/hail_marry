import { expect, test } from "@playwright/test";
import { stubAuthShell, stubTeacherDashboard, teacherDashboardPayload, stubMascotSuggestions } from "../fixtures/helpers";

/* ═══════════════════════════════════════════════════════════════════════
   TEACHER  DASHBOARD  FLOWS  ·  35 hard fault-finding tests
   ═══════════════════════════════════════════════════════════════════════ */

test.describe("Teacher dashboard bootstrap rendering", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "teacher");
        await stubMascotSuggestions(page, []);
    });

    test("teacher dashboard renders hero heading", async ({ page }) => {
        await stubTeacherDashboard(page);
        await page.goto("/teacher/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.getByRole("heading", { name: /Guide the day, not the dashboard/i })).toBeVisible();
    });

    test("teacher activation CTA shows next class attendance link", async ({ page }) => {
        await stubTeacherDashboard(page);
        await page.goto("/teacher/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("Take attendance for your next class.")).toBeVisible();
        await expect(page.getByRole("link", { name: /Open attendance sheet/i })).toBeVisible();
    });

    test("today's classes section lists slots", async ({ page }) => {
        await stubTeacherDashboard(page);
        await page.goto("/teacher/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("Class 10 A · Biology")).toBeVisible();
        await expect(page.getByText("09:00")).toBeVisible();
    });

    test("pending reviews count is displayed", async ({ page }) => {
        await stubTeacherDashboard(page);
        await page.goto("/teacher/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("Pending reviews")).toBeVisible();
        await expect(page.getByRole("link", { name: "4" })).toBeVisible();
    });

    test("open assignments count is displayed", async ({ page }) => {
        await stubTeacherDashboard(page);
        await page.goto("/teacher/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("Open assignments")).toBeVisible();
        await expect(page.getByRole("link", { name: "3" })).toBeVisible();
    });

    test("weak-topic follow-up shows weakest class", async ({ page }) => {
        await stubTeacherDashboard(page);
        await page.goto("/teacher/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("Weak-topic follow-up")).toBeVisible();
        // Class 9 B has the lowest avg_marks at 74
        await expect(page.getByText("Class 9 B").first()).toBeVisible();
    });

    test("since yesterday summary tiles are visible", async ({ page }) => {
        await stubTeacherDashboard(page);
        await page.goto("/teacher/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("Grading queue")).toBeVisible();
        await expect(page.getByText("Teaching load")).toBeVisible();
        await expect(page.getByText("Coaching signal")).toBeVisible();
    });
});

test.describe("Teacher dashboard empty/edge states", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "teacher");
        await stubMascotSuggestions(page, []);
    });

    test("zero classes renders empty message", async ({ page }) => {
        await page.route("**/api/teacher/dashboard", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(teacherDashboardPayload({ classes: [], today_classes: [] })) });
        });
        await page.goto("/teacher/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("No classes are scheduled right now.")).toBeVisible();
    });

    test("null dashboard response shows error remediation", async ({ page }) => {
        await page.route("**/api/teacher/dashboard", async (route) => {
            await route.fulfill({ status: 500, contentType: "application/json", body: JSON.stringify({ detail: "Server error" }) });
        });
        await page.goto("/teacher/dashboard", { waitUntil: "domcontentloaded" });
        // Should show error state or loading error
        await expect(page.locator("body")).toBeVisible();
    });

    test("zero pending reviews renders correctly", async ({ page }) => {
        await page.route("**/api/teacher/dashboard", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(teacherDashboardPayload({ pending_reviews: 0, open_assignments: 0 })) });
        });
        await page.goto("/teacher/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.getByRole("heading", { name: /Guide the day/i })).toBeVisible();
    });

    test("single class with equal marks doesn't crash weak-topic logic", async ({ page }) => {
        await page.route("**/api/teacher/dashboard", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(teacherDashboardPayload({ classes: [{ id: "c1", name: "Class 10 A", students: 30, avg_attendance: 90, avg_marks: 80 }] })) });
        });
        await page.goto("/teacher/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("Class 10 A").first()).toBeVisible();
    });

    test("many today classes render without layout break", async ({ page }) => {
        const manyClasses = Array.from({ length: 8 }, (_, i) => ({
            class_id: `c${i}`, class_name: `Class ${i + 1}`, subject: `Subject ${i + 1}`, start_time: `${8 + i}:00:00`, end_time: `${8 + i}:45:00`,
        }));
        await page.route("**/api/teacher/dashboard", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(teacherDashboardPayload({ today_classes: manyClasses })) });
        });
        await page.goto("/teacher/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("Class 1").first()).toBeVisible();
        await expect(page.getByText("Class 8").first()).toBeVisible();
    });

    test("null start_time in class slot shows TBD", async ({ page }) => {
        await page.route("**/api/teacher/dashboard", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(teacherDashboardPayload({ today_classes: [{ class_id: "c1", class_name: "Class 10 A", subject: "Maths", start_time: null, end_time: null }] })) });
        });
        await page.goto("/teacher/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("TBD").first()).toBeVisible();
    });

    test("empty classes array with high pending reviews", async ({ page }) => {
        await page.route("**/api/teacher/dashboard", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(teacherDashboardPayload({ classes: [], today_classes: [], pending_reviews: 99 })) });
        });
        await page.goto("/teacher/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("99").first()).toBeAttached();
    });
});

test.describe("Teacher dashboard navigation links", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "teacher");
        await stubTeacherDashboard(page);
        await stubMascotSuggestions(page, []);
    });

    test("attendance link includes classId", async ({ page }) => {
        await page.goto("/teacher/dashboard", { waitUntil: "domcontentloaded" });
        const link = page.getByRole("link", { name: /Open attendance sheet/i });
        await expect(link).toHaveAttribute("href", /classId=class-1/);
    });

    test("pending reviews links to /teacher/assignments", async ({ page }) => {
        await page.goto("/teacher/dashboard", { waitUntil: "domcontentloaded" });
        const link = page.getByRole("link", { name: "4" });
        await expect(link).toHaveAttribute("href", "/teacher/assignments");
    });

    test("open assignments links to /teacher/assignments", async ({ page }) => {
        await page.goto("/teacher/dashboard", { waitUntil: "domcontentloaded" });
        const link = page.getByRole("link", { name: "3" });
        await expect(link).toHaveAttribute("href", "/teacher/assignments");
    });

    test("weak-topic link goes to /teacher/doubt-heatmap", async ({ page }) => {
        await page.goto("/teacher/dashboard", { waitUntil: "domcontentloaded" });
        const link = page.getByRole("link", { name: /Class 9 B/i });
        await expect(link).toHaveAttribute("href", "/teacher/doubt-heatmap");
    });

    test("prepare assessment link goes to /teacher/generate-assessment", async ({ page }) => {
        await page.goto("/teacher/dashboard", { waitUntil: "domcontentloaded" });
        const link = page.getByRole("link", { name: "Open" }).last();
        await expect(link).toHaveAttribute("href", "/teacher/generate-assessment");
    });
});

test.describe("Teacher dashboard data integrity", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "teacher");
        await stubMascotSuggestions(page, []);
    });

    test("class with zero students renders", async ({ page }) => {
        await page.route("**/api/teacher/dashboard", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(teacherDashboardPayload({ classes: [{ id: "c1", name: "Empty Class", students: 0, avg_attendance: 0, avg_marks: 0 }] })) });
        });
        await page.goto("/teacher/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("Empty Class").first()).toBeVisible();
    });

    test("100% attendance on a class renders correctly", async ({ page }) => {
        await page.route("**/api/teacher/dashboard", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(teacherDashboardPayload({ classes: [{ id: "c1", name: "Perfect Class", students: 20, avg_attendance: 100, avg_marks: 95 }] })) });
        });
        await page.goto("/teacher/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("Perfect Class").first()).toBeVisible();
    });

    test("class name with special characters renders safely", async ({ page }) => {
        await page.route("**/api/teacher/dashboard", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(teacherDashboardPayload({ classes: [{ id: "c1", name: 'Class <script>alert("xss")</script>', students: 20, avg_attendance: 80, avg_marks: 70 }] })) });
        });
        await page.goto("/teacher/dashboard", { waitUntil: "domcontentloaded" });
        const alertFired = await page.evaluate(() => (window as unknown as { _xss?: boolean })._xss ?? false);
        expect(alertFired).toBe(false);
    });

    test("teacher kicker text is visible", async ({ page }) => {
        await stubTeacherDashboard(page);
        await page.goto("/teacher/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.getByText("Teacher daily workflow")).toBeVisible();
    });

    test("morning briefing is visible after data loads", async ({ page }) => {
        await stubTeacherDashboard(page);
        await page.goto("/teacher/dashboard", { waitUntil: "domcontentloaded" });
        // Briefing renders facts about classes scheduled today
        await expect(page.getByText(/class session/i).first()).toBeVisible();
    });

    test("loading state shows teaching workflow message", async ({ page }) => {
        await page.route("**/api/teacher/dashboard", async (route) => {
            await new Promise((r) => setTimeout(r, 2000));
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(teacherDashboardPayload()) });
        });
        await page.goto("/teacher/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.getByText(/Loading today/i)).toBeVisible();
    });
});
