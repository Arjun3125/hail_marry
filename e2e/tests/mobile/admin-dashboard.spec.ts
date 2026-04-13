import { test, expect } from '../../fixtures/auth';

test.describe('Admin Dashboard - Mobile (360px)', () => {
  test('should load admin dashboard', async ({ adminPage }: any) => {
    // Check viewport size
    const viewport = adminPage.viewportSize();
    expect(viewport?.width).toBe(360);

    // Should load without horizontal scroll
    const scrollWidth = await adminPage.evaluate(() => {
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

  test('should display key admin metrics', async ({ adminPage }: any) => {
    // Should show system overview stats
    await expect(adminPage.locator('text=/total|active|users|schools|students|teachers/i')).toBeVisible();

    // Should show system health indicators
    const healthIndicators = adminPage.locator('[class*="status"], [class*="health"]').filter({
      hasText: /online|active|healthy|running/i
    });

    if (await healthIndicators.count() > 0) {
      await expect(healthIndicators.first()).toBeVisible();
    }
  });

  test('should show user management overview', async ({ adminPage }: any) => {
    // Should display user counts by role
    const userStats = adminPage.locator('text=/admin|teacher|student|parent/i').filter({
      hasText: /\d+/
    });

    await expect(userStats.first()).toBeVisible();
  });

  test('should provide navigation to management sections', async ({ adminPage }: any) => {
    // Should have navigation to key admin sections
    const navItems = adminPage.locator('a, button').filter({
      hasText: /user|school|system|config|report|complaint/i
    });

    await expect(navItems.first()).toBeVisible();

    // Check touch targets for navigation
    for (const item of await navItems.all()) {
      const box = await item.boundingBox();
      if (box) {
        expect(box.width).toBeGreaterThanOrEqual(44);
        expect(box.height).toBeGreaterThanOrEqual(44);
      }
    }
  });

  test('should display system alerts or notifications', async ({ adminPage }: any) => {
    // Look for system alerts, warnings, or notifications
    const alerts = adminPage.locator('[class*="alert"], [class*="notification"], [class*="warning"]').filter({
      hasText: /alert|warning|error|notice/i
    });

    // May or may not have alerts, but if present should be visible
    if (await alerts.count() > 0) {
      await expect(alerts.first()).toBeVisible();
    }
  });

  test('should show recent activity or logs', async ({ adminPage }: any) => {
    // Should display recent system activity
    const activityFeed = adminPage.locator('text=/recent|activity|log|event/i');

    if (await activityFeed.count() > 0) {
      await expect(activityFeed.first()).toBeVisible();
    }
  });

  test('should handle sidebar navigation on mobile', async ({ adminPage }: any) => {
    // Check for mobile menu toggle
    const menuToggle = adminPage.locator('[aria-label*="menu"], .hamburger, .sidebar-toggle, [class*="menu"]').first();

    if (await menuToggle.isVisible()) {
      await menuToggle.click();

      // Sidebar should be visible
      const sidebar = adminPage.locator('.sidebar, nav, aside, [class*="sidebar"]').first();
      await expect(sidebar).toBeVisible();

      // Should be able to close sidebar
      const closeButton = adminPage.locator('[aria-label*="close"], .close, [class*="close"]').first();
      if (await closeButton.isVisible()) {
        await closeButton.click();
      } else {
        // Try clicking outside or toggle again
        await menuToggle.click();
      }
    }
  });

  test('should display readable metric values', async ({ adminPage }: any) => {
    // Check font sizes for key metrics
    const metrics = adminPage.locator('[class*="metric"], [class*="stat"], [class*="count"]').filter({
      hasText: /\d+/
    });

    for (const metric of await metrics.all()) {
      const fontSize = await metric.evaluate((el: HTMLElement) => {
        return parseFloat(getComputedStyle(el).fontSize);
      });
      expect(fontSize).toBeGreaterThanOrEqual(16); // Metrics should be prominent
    }
  });

  test('should provide access to detailed reports', async ({ adminPage }: any) => {
    // Look for report generation or detailed view buttons
    const reportButtons = adminPage.locator('button, a').filter({
      hasText: /report|export|download|detail/i
    });

    if (await reportButtons.count() > 0) {
      // Check they have proper touch targets
      for (const button of await reportButtons.all()) {
        const box = await button.boundingBox();
        if (box) {
          expect(box.width).toBeGreaterThanOrEqual(44);
          expect(box.height).toBeGreaterThanOrEqual(44);
        }
      }
    }
  });
});