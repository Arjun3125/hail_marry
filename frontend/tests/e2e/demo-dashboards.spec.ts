import { test, expect } from '@playwright/test';
import * as path from 'path';

test('Verify Demo Roles Load Correctly', async ({ page }) => {
  test.setTimeout(60000); // 60 seconds
  const artifactsDir = path.resolve(process.cwd(), '..', '.gemini', 'antigravity', 'artifacts');

  // Go to Demo Gateway
  await page.goto('http://localhost:7125/demo');
  await expect(page.locator('text=Experience as a Student').first()).toBeVisible({ timeout: 15000 });
  
  // Login as Student
  await page.click('text=Experience as a Student');
  await page.waitForURL('**/student/overview');
  await expect(page.locator('text=Dashboard').first()).toBeVisible({ timeout: 10000 });
  await page.screenshot({ path: path.join(artifactsDir, 'student_dashboard.png'), fullPage: true });

  // Switch to Teacher
  await page.click('text=Switch Role');
  await page.click('text=Teacher');
  await page.waitForURL('**/teacher/dashboard');
  await expect(page.locator('text=Teacher Dashboard').first()).toBeVisible({ timeout: 10000 });
  await page.screenshot({ path: path.join(artifactsDir, 'teacher_dashboard.png'), fullPage: true });

  // Switch to Admin
  await page.click('text=Switch Role');
  await page.click('text=Admin');
  await page.waitForURL('**/admin/dashboard');
  await expect(page.locator('text=Admin Dashboard').first()).toBeVisible({ timeout: 10000 });
  await page.screenshot({ path: path.join(artifactsDir, 'admin_dashboard.png'), fullPage: true });
});
