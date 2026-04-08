import { defineConfig, devices } from "@playwright/test";

const playwrightHost = process.env.PLAYWRIGHT_HOST || "127.0.0.1";
const playwrightPort = process.env.PLAYWRIGHT_PORT || "9000";
const playwrightBaseUrl = `http://${playwrightHost}:${playwrightPort}`;
const startCommand =
    process.platform === "win32"
        ? `C:\\Windows\\System32\\cmd.exe /c npm run start -- --hostname ${playwrightHost} --port ${playwrightPort}`
        : `npm run start -- --hostname ${playwrightHost} --port ${playwrightPort}`;

export default defineConfig({
    testDir: "./tests/e2e",
    timeout: 30_000,
    retries: 1,
    workers: process.env.CI ? 2 : 4,
    use: {
        baseURL: playwrightBaseUrl,
        trace: "on-first-retry",
        serviceWorkers: "block",
    },
    webServer: {
        command: startCommand,
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
