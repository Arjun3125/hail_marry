import { test, expect } from '../../fixtures/auth';

test.describe('Teacher Attendance - Mobile (360px)', () => {
  test('should load attendance interface', async ({ teacherPage }: any) => {
    await teacherPage.goto('/teacher/attendance');

    // Check viewport size
    const viewport = teacherPage.viewportSize();
    expect(viewport?.width).toBe(360);

    // Should load without horizontal scroll
    const scrollWidth = await teacherPage.evaluate(() => {
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

  test('should display class selection', async ({ teacherPage }: any) => {
    await teacherPage.goto('/teacher/attendance');

    // Should show class selector or current class
    await expect(teacherPage.locator('select, [role="combobox"]').or(
      teacherPage.locator('text=/class|grade|section/i')
    )).toBeVisible();
  });

  test('should show student list with attendance controls', async ({ teacherPage }: any) => {
    await teacherPage.goto('/teacher/attendance');

    // Should display students
    const students = teacherPage.locator('[class*="student"], tr, [class*="row"]').filter({
      hasText: /[A-Za-z]/
    });

    await expect(students.first()).toBeVisible();

    // Should have attendance controls (present/absent/late)
    const attendanceControls = teacherPage.locator('input[type="radio"], button').filter({
      hasText: /present|absent|late/i
    });

    await expect(attendanceControls.first()).toBeVisible();
  });

  test('should have touch-friendly attendance toggles', async ({ teacherPage }: any) => {
    await teacherPage.goto('/teacher/attendance');

    // Check radio buttons or toggle buttons
    const toggles = teacherPage.locator('input[type="radio"], input[type="checkbox"], button').filter({
      hasText: /present|absent|late/i
    });

    for (const toggle of await toggles.all()) {
      const box = await toggle.boundingBox();
      if (box) {
        // Radio buttons need larger touch targets
        expect(box.width).toBeGreaterThanOrEqual(44);
        expect(box.height).toBeGreaterThanOrEqual(44);
      }
    }
  });

  test('should display student names clearly', async ({ teacherPage }: any) => {
    await teacherPage.goto('/teacher/attendance');

    // Check student name text size
    const studentNames = teacherPage.locator('[class*="name"], td:first-child, [class*="student"]').filter({
      hasText: /[A-Za-z]{2,}/
    });

    for (const name of await studentNames.all()) {
      const fontSize = await name.evaluate((el: HTMLElement) => {
        return parseFloat(getComputedStyle(el).fontSize);
      });
      expect(fontSize).toBeGreaterThanOrEqual(14); // Names should be readable
    }
  });

  test('should show attendance summary', async ({ teacherPage }: any) => {
    await teacherPage.goto('/teacher/attendance');

    // Should show summary stats
    await expect(teacherPage.locator('text=/present|absent|total|marked/i')).toBeVisible();
  });

  test('should handle save/submit attendance', async ({ teacherPage }: any) => {
    await teacherPage.goto('/teacher/attendance');

    // Look for save/submit button
    const saveButton = teacherPage.locator('button').filter({
      hasText: /save|submit|mark|update/i
    }).first();

    if (await saveButton.isVisible()) {
      // Check button is properly sized
      const box = await saveButton.boundingBox();
      if (box) {
        expect(box.width).toBeGreaterThanOrEqual(44);
        expect(box.height).toBeGreaterThanOrEqual(44);
      }
    }
  });

  test('should navigate between dates/classes', async ({ teacherPage }: any) => {
    await teacherPage.goto('/teacher/attendance');

    // Check for date navigation
    const dateControls = teacherPage.locator('button, input[type="date"]').filter({
      hasText: /today|yesterday|date/i
    });

    if (await dateControls.count() > 0) {
      // Should have proper touch targets
      for (const control of await dateControls.all()) {
        const box = await control.boundingBox();
        if (box) {
          expect(box.width).toBeGreaterThanOrEqual(44);
          expect(box.height).toBeGreaterThanOrEqual(44);
        }
      }
    }
  });
});