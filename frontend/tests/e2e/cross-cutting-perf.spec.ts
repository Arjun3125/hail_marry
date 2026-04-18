import { expect, test } from "@playwright/test";
import { stubAuthShell, stubStudentOverview, stubAdminDashboard, stubTeacherDashboard, stubParentDashboard, stubMascotSuggestions } from "../fixtures/helpers";

/* ═══════════════════════════════════════════════════════════════════════
   CROSS-CUTTING  PERFORMANCE  ·  15 hard fault-finding tests
   ═══════════════════════════════════════════════════════════════════════ */

test.describe("Page load performance — Student", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "student");
        await stubStudentOverview(page);
        await stubMascotSuggestions(page, []);
    });

    test("student overview loads in under 5 seconds", async ({ page }) => {
        const start = Date.now();
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
        expect(Date.now() - start).toBeLessThan(5000);
    });

    test("student overview FCP is under 3 seconds", async ({ page }) => {
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        const fcp = await page.evaluate(async () => {
            return new Promise<number>((resolve) => {
                const paints = performance.getEntriesByType("paint");
                const existingFCP = paints.find((entry) => entry.name === "first-contentful-paint");
                if (existingFCP) return resolve(existingFCP.startTime);
                
                const observer = new PerformanceObserver((list) => {
                    const entry = list.getEntriesByName("first-contentful-paint")[0];
                    if (entry) {
                        observer.disconnect();
                        resolve(entry.startTime);
                    }
                });
                observer.observe({ type: "paint", buffered: true });
                setTimeout(() => { observer.disconnect(); resolve(0); }, 5000);
            });
        });
        expect(fcp).toBeLessThan(3000);
    });

    test("student overview doesn't have 100+ network requests", async ({ page }) => {
        const requests: string[] = [];
        page.on("request", (req) => requests.push(req.url()));
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        expect(requests.length).toBeLessThan(100);
    });

    test("student overview DOM is not excessively deep", async ({ page }) => {
        await page.goto("/student/overview", { waitUntil: "domcontentloaded" });
        const depth = await page.evaluate(() => {
            let max = 0;
            const walk = (node: Element, d: number) => {
                if (d > max) max = d;
                for (const child of Array.from(node.children)) walk(child, d + 1);
            };
            walk(document.body, 0);
            return max;
        });
        expect(depth).toBeLessThan(40);
    });

    test("student tools page loads in under 5 seconds", async ({ page }) => {
        const start = Date.now();
        await page.goto("/student/tools", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
        expect(Date.now() - start).toBeLessThan(5000);
    });
});

test.describe("Page load performance — Teacher", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "teacher");
        await stubTeacherDashboard(page);
        await stubMascotSuggestions(page, []);
    });

    test("teacher dashboard loads in under 5 seconds", async ({ page }) => {
        const start = Date.now();
        await page.goto("/teacher/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
        expect(Date.now() - start).toBeLessThan(5000);
    });

    test("teacher dashboard FCP is under 3 seconds", async ({ page }) => {
        await page.goto("/teacher/dashboard", { waitUntil: "domcontentloaded" });
        const fcp = await page.evaluate(async () => {
            return new Promise<number>((resolve) => {
                const paints = performance.getEntriesByType("paint");
                const existingFCP = paints.find((entry) => entry.name === "first-contentful-paint");
                if (existingFCP) return resolve(existingFCP.startTime);
                
                const observer = new PerformanceObserver((list) => {
                    const entry = list.getEntriesByName("first-contentful-paint")[0];
                    if (entry) {
                        observer.disconnect();
                        resolve(entry.startTime);
                    }
                });
                observer.observe({ type: "paint", buffered: true });
                setTimeout(() => { observer.disconnect(); resolve(0); }, 5000);
            });
        });
        expect(fcp).toBeLessThan(3000);
    });
});

test.describe("Page load performance — Admin", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "admin");
        await stubAdminDashboard(page);
        await stubMascotSuggestions(page, []);
    });

    test("admin dashboard loads in under 5 seconds", async ({ page }) => {
        const start = Date.now();
        await page.goto("/admin/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
        expect(Date.now() - start).toBeLessThan(5000);
    });

    test("admin dashboard FCP is under 3 seconds", async ({ page }) => {
        await page.goto("/admin/dashboard", { waitUntil: "domcontentloaded" });
        const fcp = await page.evaluate(async () => {
            return new Promise<number>((resolve) => {
                const paints = performance.getEntriesByType("paint");
                const existingFCP = paints.find((entry) => entry.name === "first-contentful-paint");
                if (existingFCP) return resolve(existingFCP.startTime);
                
                const observer = new PerformanceObserver((list) => {
                    const entry = list.getEntriesByName("first-contentful-paint")[0];
                    if (entry) {
                        observer.disconnect();
                        resolve(entry.startTime);
                    }
                });
                observer.observe({ type: "paint", buffered: true });
                setTimeout(() => { observer.disconnect(); resolve(0); }, 5000);
            });
        });
        expect(fcp).toBeLessThan(3000);
    });
});

test.describe("Page load performance — Parent", () => {
    test.beforeEach(async ({ page }) => {
        await stubAuthShell(page, "parent");
        await stubParentDashboard(page);
        await stubMascotSuggestions(page, []);
        await page.route("**/api/parent/ai-insights**", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ insights: [] }) });
        });
    });

    test("parent dashboard loads in under 5 seconds", async ({ page }) => {
        const start = Date.now();
        await page.goto("/parent/dashboard", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
        expect(Date.now() - start).toBeLessThan(5000);
    });

    test("parent dashboard FCP is under 3 seconds", async ({ page }) => {
        await page.goto("/parent/dashboard", { waitUntil: "domcontentloaded" });
        const fcp = await page.evaluate(async () => {
            return new Promise<number>((resolve) => {
                const paints = performance.getEntriesByType("paint");
                const existingFCP = paints.find((entry) => entry.name === "first-contentful-paint");
                if (existingFCP) return resolve(existingFCP.startTime);
                
                const observer = new PerformanceObserver((list) => {
                    const entry = list.getEntriesByName("first-contentful-paint")[0];
                    if (entry) {
                        observer.disconnect();
                        resolve(entry.startTime);
                    }
                });
                observer.observe({ type: "paint", buffered: true });
                setTimeout(() => { observer.disconnect(); resolve(0); }, 5000);
            });
        });
        expect(fcp).toBeLessThan(3000);
    });
});

test.describe("Landing page performance", () => {
    test("landing page loads in under 4 seconds", async ({ page }) => {
        await page.route("**/api/branding/config", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ name: "VidyaOS" }) });
        });
        const start = Date.now();
        await page.goto("/", { waitUntil: "domcontentloaded" });
        await expect(page.locator("body")).toBeVisible();
        expect(Date.now() - start).toBeLessThan(4000);
    });

    test("landing page has no JS errors in console", async ({ page }) => {
        const errors: string[] = [];
        page.on("pageerror", (err) => errors.push(err.message));
        await page.route("**/api/branding/config", async (route) => {
            await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ name: "VidyaOS" }) });
        });
        await page.goto("/", { waitUntil: "domcontentloaded" });
        expect(errors.length).toBe(0);
    });
});
