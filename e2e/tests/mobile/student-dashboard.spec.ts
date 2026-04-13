import { test, expect } from '../../fixtures/auth';

test.describe('Student Dashboard - Mobile (360px)', () => {
  test('should load dashboard without horizontal scroll', async ({ studentPage }: any) => {
    // Check viewport size
    const viewport = studentPage.viewportSize();
    expect(viewport?.width).toBe(360);

    // Check for horizontal scroll
    const scrollWidth = await studentPage.evaluate(() => {
      return Math.max(
        document.body.scrollWidth,
        document.body.offsetWidth,
        document.documentElement.clientWidth,
        document.documentElement.scrollWidth,
        document.documentElement.offsetWidth
      );
    });

    expect(scrollWidth).toBeLessThanOrEqual(360);
  });

  test('should have readable text sizes', async ({ studentPage }: any) => {
    // Check main heading
    const heading = studentPage.locator('h1, h2').first();
    const fontSize = await heading.evaluate((el: HTMLElement) => {
      return parseFloat(getComputedStyle(el).fontSize);
    });
    expect(fontSize).toBeGreaterThanOrEqual(16); // Minimum readable size

    // Check body text
    const bodyText = studentPage.locator('p, span, div').filter({ hasText: /.+/ }).first();
    const bodyFontSize = await bodyText.evaluate((el: HTMLElement) => {
      return parseFloat(getComputedStyle(el).fontSize);
    });
    expect(bodyFontSize).toBeGreaterThanOrEqual(14);
  });

  test('should have touch-friendly button sizes', async ({ studentPage }: any) => {
    const buttons = studentPage.locator('button, [role="button"]');

    for (const button of await buttons.all()) {
      const box = await button.boundingBox();
      if (box) {
        // Minimum touch target size: 44px
        expect(box.width).toBeGreaterThanOrEqual(44);
        expect(box.height).toBeGreaterThanOrEqual(44);
      }
    }
  });

  test('should display key dashboard elements', async ({ studentPage }: any) => {
    // Check for attendance card
    await expect(studentPage.locator('text=/attendance|present/i')).toBeVisible();

    // Check for performance/grades
    await expect(studentPage.locator('text=/performance|grade|score/i')).toBeVisible();

    // Check for recent results or assignments
    await expect(studentPage.locator('text=/assignment|homework|result/i')).toBeVisible();
  });

  test('should navigate to assignments page', async ({ studentPage }: any) => {
    // Click assignments navigation
    await studentPage.locator('a, button').filter({ hasText: /assignment/i }).first().click();

    // Should navigate to assignments page
    await expect(studentPage).toHaveURL(/.*assignments.*/);
  });

  test('should handle sidebar navigation on mobile', async ({ studentPage }: any) => {
    // Check if sidebar toggle exists (hamburger menu)
    const sidebarToggle = studentPage.locator('[aria-label*="menu"], .hamburger, .sidebar-toggle').first();

    if (await sidebarToggle.isVisible()) {
      await sidebarToggle.click();

      // Sidebar should be visible
      const sidebar = studentPage.locator('.sidebar, nav, aside').first();
      await expect(sidebar).toBeVisible();

      // Close sidebar
      await sidebarToggle.click();
    }
  });
});