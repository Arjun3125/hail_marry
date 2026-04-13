import { defineConfig, devices } from "@playwright/test";

const baseURL = process.env.BASE_URL || "http://localhost:3057";
const parsedBaseUrl = new URL(baseURL);
const devPort = parsedBaseUrl.port || (parsedBaseUrl.protocol === "https:" ? "443" : "80");

export default defineConfig({
    timeout: 60 * 1000,
    testDir: "./tests/e2e",
    fullyParallel: true,
    forbidOnly: !!process.env.CI,
    retries: process.env.CI ? 2 : 0,
    workers: process.env.CI ? 1 : undefined,
    reporter: [
        ["html"],
        ["junit", { outputFile: "test-results/junit.xml" }],
        ["github"],
    ],
    use: {
        baseURL,
        trace: "on-first-retry",
        screenshot: "only-on-failure",
        video: "retain-on-failure",
    },
    projects: [
        {
            name: "chromium",
            use: { ...devices["Desktop Chrome"] },
        },
        {
            name: "Mobile Chrome",
            use: {
                ...devices["Pixel 5"],
                viewport: { width: 360, height: 640 },
            },
        },
        {
            name: "Tablet",
            use: {
                ...devices.iPad,
                viewport: { width: 768, height: 1024 },
            },
        },
        {
            name: "Desktop Small",
            use: {
                ...devices["Desktop Chrome"],
                viewport: { width: 1280, height: 720 },
            },
        },
    ],
    webServer: {
        command: `npm run dev -- --port ${devPort}`,
        url: baseURL,
        reuseExistingServer: !process.env.CI,
        timeout: 120 * 1000,
    },
});
