import { test, expect } from '../../fixtures/auth';

test.describe('Parent Dashboard - Mobile (360px)', () => {
  test('should load parent dashboard', async ({ parentPage }) => {
    // Check viewport size
    const viewport = parentPage.viewportSize();
    expect(viewport?.width).toBe(360);

    // Should load without horizontal scroll
    const scrollWidth = await parentPage.evaluate(() => {
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

  test('should display child overview', async ({ parentPage }) => {
    // Should show child information
    await expect(parentPage.locator('text=/child|student|ward/i')).toBeVisible();

    // Should show attendance summary
    await expect(parentPage.locator('text=/attendance|present|absent/i')).toBeVisible();
  });

  test('should show attendance statistics', async ({ parentPage }) => {
    // Check for attendance metrics
    const attendanceStats = parentPage.locator('[class*="attendance"], [class*="stats"]').filter({
      hasText: /\d+%|\d+\/\d+|present|absent/i
    });

    await expect(attendanceStats.first()).toBeVisible();
  });

  test('should display marks/grades', async ({ parentPage }) => {
    // Should show academic performance
    await expect(parentPage.locator('text=/marks|grades|percentage|score/i')).toBeVisible();

    // Check for subject-wise breakdown
    const subjects = parentPage.locator('text=/math|science|english|hindi|social/i');

    if (await subjects.count() > 0) {
      await expect(subjects.first()).toBeVisible();
    }
  });

  test('should have readable performance data', async ({ parentPage }) => {
    // Check font sizes for marks/grades
    const gradeElements = parentPage.locator('[class*="grade"], [class*="mark"], [class*="score"]').filter({
      hasText: /\d+/
    });

    for (const element of await gradeElements.all()) {
      const fontSize = await element.evaluate((el) => {
        return parseFloat(getComputedStyle(el).fontSize);
      });
      expect(fontSize).toBeGreaterThanOrEqual(14); // Grades should be clearly readable
    }
  });

  test('should show recent activity or updates', async ({ parentPage }) => {
    // Look for recent activity, announcements, or updates
    const activityElements = parentPage.locator('text=/recent|latest|update|announcement|activity/i');

    if (await activityElements.count() > 0) {
      await expect(activityElements.first()).toBeVisible();
    }
  });

  test('should provide navigation to detailed views', async ({ parentPage }) => {
    // Should have links to detailed attendance/marks views
    const detailLinks = parentPage.locator('a, button').filter({
      hasText: /view|details|more|see|check/i
    });

    if (await detailLinks.count() > 0) {
      // Check touch targets
      for (const link of await detailLinks.all()) {
        const box = await link.boundingBox();
        if (box) {
          expect(box.width).toBeGreaterThanOrEqual(44);
          expect(box.height).toBeGreaterThanOrEqual(44);
        }
      }
    }
  });

  test('should handle settings/preferences access', async ({ parentPage }) => {
    // Look for settings or preferences button
    const settingsButton = parentPage.locator('a, button').filter({
      hasText: /setting|preference|notification|alert/i
    }).first();

    if (await settingsButton.isVisible()) {
      // Check it's accessible
      const box = await settingsButton.boundingBox();
      if (box) {
        expect(box.width).toBeGreaterThanOrEqual(44);
        expect(box.height).toBeGreaterThanOrEqual(44);
      }
    }
  });

  test('should display contact information if available', async ({ parentPage }) => {
    // Check for teacher contact or school contact info
    const contactInfo = parentPage.locator('text=/contact|phone|email|teacher|school/i');

    if (await contactInfo.count() > 0) {
      await expect(contactInfo.first()).toBeVisible();
    }
  });
});