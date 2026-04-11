import { test as base, expect } from '@playwright/test';

type AuthFixture = {
  studentPage: any;
  teacherPage: any;
  parentPage: any;
  adminPage: any;
};

// Extend the base test with authentication fixtures
export const test = base.extend<AuthFixture>({
  // Student authentication fixture
  studentPage: async ({ browser }, use) => {
    const context = await browser.newContext({
      viewport: { width: 360, height: 640 }, // Mobile viewport
      userAgent: 'Mozilla/5.0 (Linux; Android 10; Pixel 3) AppleWebKit/537.36',
    });
    const page = await context.newPage();

    // Navigate to login page
    await page.goto('/auth/login');

    // Perform student login
    await page.fill('input[type="email"]', process.env.STUDENT_EMAIL || 'student@vidyaos.test');
    await page.fill('input[type="password"]', process.env.STUDENT_PASSWORD || 'password123');
    await page.click('button[type="submit"]');

    // Wait for navigation to dashboard
    await page.waitForURL('**/student/**', { timeout: 10000 });

    await use(page);
    await context.close();
  },

  // Teacher authentication fixture
  teacherPage: async ({ browser }, use) => {
    const context = await browser.newContext({
      viewport: { width: 768, height: 1024 }, // Tablet viewport
      userAgent: 'Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
    });
    const page = await context.newPage();

    // Navigate to login page
    await page.goto('/auth/login');

    // Perform teacher login
    await page.fill('input[type="email"]', process.env.TEACHER_EMAIL || 'teacher@vidyaos.test');
    await page.fill('input[type="password"]', process.env.TEACHER_PASSWORD || 'password123');
    await page.click('button[type="submit"]');

    // Wait for navigation to dashboard
    await page.waitForURL('**/teacher/**', { timeout: 10000 });

    await use(page);
    await context.close();
  },

  // Parent authentication fixture
  parentPage: async ({ browser }, use) => {
    const context = await browser.newContext({
      viewport: { width: 360, height: 640 }, // Mobile viewport
      userAgent: 'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36',
    });
    const page = await context.newPage();

    // Navigate to login page
    await page.goto('/auth/login');

    // Perform parent login
    await page.fill('input[type="email"]', process.env.PARENT_EMAIL || 'parent@vidyaos.test');
    await page.fill('input[type="password"]', process.env.PARENT_PASSWORD || 'password123');
    await page.click('button[type="submit"]');

    // Wait for navigation to dashboard
    await page.waitForURL('**/parent/**', { timeout: 10000 });

    await use(page);
    await context.close();
  },

  // Admin authentication fixture
  adminPage: async ({ browser }, use) => {
    const context = await browser.newContext({
      viewport: { width: 1280, height: 720 }, // Desktop small viewport
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    });
    const page = await context.newPage();

    // Navigate to login page
    await page.goto('/auth/login');

    // Perform admin login
    await page.fill('input[type="email"]', process.env.ADMIN_EMAIL || 'admin@vidyaos.test');
    await page.fill('input[type="password"]', process.env.ADMIN_PASSWORD || 'password123');
    await page.click('button[type="submit"]');

    // Wait for navigation to dashboard
    await page.waitForURL('**/admin/**', { timeout: 10000 });

    await use(page);
    await context.close();
  },
});

export { expect };