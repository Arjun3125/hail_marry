import path from "path";

import { defineConfig, devices } from "@playwright/test";

const baseURL = process.env.BASE_URL || "http://localhost:3057";
const parsedBaseUrl = new URL(baseURL);
const devPort = parsedBaseUrl.port || (parsedBaseUrl.protocol === "https:" ? "443" : "80");
const repoRoot = path.resolve(__dirname, "..");
const backendDir = path.join(repoRoot, "backend");
const configuredWorkers = Number(process.env.PLAYWRIGHT_WORKERS);
const configuredRetries = Number(process.env.PLAYWRIGHT_RETRIES);
const workers = Number.isFinite(configuredWorkers) && configuredWorkers > 0
    ? configuredWorkers
    : (process.env.CI ? 4 : undefined);
const retries = Number.isFinite(configuredRetries) && configuredRetries >= 0
    ? configuredRetries
    : (process.env.CI ? 1 : 0);

export default defineConfig({
    timeout: 60 * 1000,
    testDir: "./tests/e2e",
    fullyParallel: true,
    forbidOnly: !!process.env.CI,
    retries,
    workers,
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
    webServer: [
        {
            command: "python run_api.py --host 127.0.0.1 --port 8000",
            cwd: backendDir,
            env: {
                ...process.env,
                DEMO_MODE: "true",
                TESTING: "1",
                APP_ENV: "test",
                DATABASE_URL: "sqlite:///./playwright_e2e.db",
                REDIS_URL: "redis://127.0.0.1:65535/0",
                REDIS_BROKER_URL: "redis://127.0.0.1:65535/0",
                REDIS_STATE_URL: "redis://127.0.0.1:65535/0",
                STARTUP_CHECKS_STRICT: "false",
                STARTUP_CHECKS_TIMEOUT_SECONDS: "2",
                WORKER_HEALTH_ENABLED: "false",
                JWT_SECRET: "playwright-demo-secret-playwright-demo-secret",
                REFRESH_SECRET_KEY: "playwright-refresh-secret-playwright-refresh-secret",
                PYTHONUNBUFFERED: "1",
            },
            url: "http://127.0.0.1:8000/health",
            reuseExistingServer: true,
            timeout: 120 * 1000,
        },
        {
            command: process.env.CI
                ? `npm run start -- --port ${devPort}`
                : `npm run dev -- --port ${devPort}`,
            env: {
                ...process.env,
                NEXT_PUBLIC_DEMO_MODE: "true",
            },
            url: baseURL,
            reuseExistingServer: !process.env.CI,
            timeout: 120 * 1000,
        },
    ],
});
