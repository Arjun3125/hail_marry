import { expect, test } from "@playwright/test";

test("parent dashboard shows progress story and plays audio summary", async ({ page }) => {
    await page.addInitScript(() => {
        window.localStorage.setItem("vidyaos_access_token", "test-token");
        Object.defineProperty(window, "speechSynthesis", {
            value: {
                speak: (utterance: SpeechSynthesisUtterance) => {
                    (window as Window & { __spokenText?: string }).__spokenText = utterance.text;
                    setTimeout(() => {
                        utterance.onend?.(new Event("end") as SpeechSynthesisEvent);
                    }, 0);
                },
                cancel: () => {
                    (window as Window & { __speechCancelled?: boolean }).__speechCancelled = true;
                },
            },
            configurable: true,
        });
    });

    await page.route("**/api/parent/dashboard", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                child: {
                    id: "child-1",
                    name: "Aarav",
                    email: "aarav@example.com",
                    class: "8A",
                },
                attendance_pct: 92,
                avg_marks: 84,
                pending_assignments: 2,
                latest_mark: {
                    subject: "Mathematics",
                    exam: "Unit Test 3",
                    percentage: 88,
                    date: "2026-04-05T10:00:00.000Z",
                },
                next_class: {
                    day: 1,
                    start_time: "09:00",
                    end_time: "09:45",
                    subject: "Science",
                },
            }),
        });
    });

    await page.route("**/api/parent/audio-report", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                text: "Aarav is doing well this week with 92 percent attendance and 88 percent in Mathematics.",
            }),
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

    await page.goto("/parent/dashboard", { waitUntil: "domcontentloaded" });

    await expect(page.getByRole("heading", { name: /Read your child's week in under a minute/i })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Aarav" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Last week's highlights" })).toBeVisible();
    await expect(page.getByText("Attendance recorded this week.")).toBeVisible();
    await expect(page.getByText("Unit Test 3", { exact: true })).toBeVisible();
    await expect(page.getByText("Science")).toBeVisible();

    await page.getByRole("button", { name: "Play audio update" }).click();
    await expect.poll(async () => page.evaluate(() => (window as Window & { __spokenText?: string }).__spokenText || "")).toContain("Aarav is doing well this week");
});

