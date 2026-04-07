import { defineConfig, devices } from "@playwright/test";

const playwrightHost = process.env.PLAYWRIGHT_HOST || "127.0.0.1";
const playwrightPort = process.env.PLAYWRIGHT_PORT || "9000";
const playwrightBaseUrl = `http://${playwrightHost}:${playwrightPort}`;

export default defineConfig({
    testDir: "./tests/e2e",
    timeout: 30_000,
    retries: 1,
    use: {
        baseURL: playwrightBaseUrl,
        trace: "on-first-retry",
        serviceWorkers: "block",
    },
    webServer: {
        command: `npm run start -- --hostname ${playwrightHost} --port ${playwrightPort}`,
        url: playwrightBaseUrl,
        reuseExistingServer: true,
        timeout: 120_000,
    },
    projects: [
        {
            name: "chromium",
            use: { ...devices["Desktop Chrome"] },
        },
    ],
});
