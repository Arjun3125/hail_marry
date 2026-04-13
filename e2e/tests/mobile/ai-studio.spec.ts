import { test, expect } from '../../fixtures/auth';

test.describe('AI Studio - Mobile (360px)', () => {
  test('should load AI Studio interface', async ({ studentPage }: any) => {
    await studentPage.goto('/student/ai-studio');

    // Check viewport size
    const viewport = studentPage.viewportSize();
    expect(viewport?.width).toBe(360);

    // Should load without horizontal scroll
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

  test('should display AI assistant interface', async ({ studentPage }: any) => {
    await studentPage.goto('/student/ai-studio');

    // Check for input field
    await expect(studentPage.locator('input[type="text"], textarea')).toBeVisible();

    // Check for AI assistant indicator
    await expect(studentPage.locator('text=/ai|assistant|thinking/i')).toBeVisible();
  });

  test('should show intent selector', async ({ studentPage }: any) => {
    await studentPage.goto('/student/ai-studio');

    // Look for intent selector button or interface
    const intentButton = studentPage.locator('button, [role="button"]').filter({
      hasText: /what would you like|intent|study/i
    }).first();

    if (await intentButton.isVisible()) {
      await intentButton.click();

      // Should show intent options
      await expect(studentPage.locator('text=/understand|practice|review|help/i')).toBeVisible();
    }
  });

  test('should display tool cards with proper sizing', async ({ studentPage }: any) => {
    await studentPage.goto('/student/ai-studio');

    // Check for tool cards (quiz, flashcards, mindmap, etc.)
    const toolCards = studentPage.locator('[class*="tool"], [class*="card"]').filter({
      hasText: /quiz|flashcard|mind.?map|study/i
    });

    // Should have at least a few tools visible
    await expect(toolCards.first()).toBeVisible();

    // Check touch targets for tool cards
    for (const card of await toolCards.all()) {
      const box = await card.boundingBox();
      if (box) {
        expect(box.width).toBeGreaterThanOrEqual(44);
        expect(box.height).toBeGreaterThanOrEqual(44);
      }
    }
  });

  test('should handle text input and submission', async ({ studentPage }: any) => {
    await studentPage.goto('/student/ai-studio');

    const input = studentPage.locator('input[type="text"], textarea').first();

    // Type a question
    await input.fill('What is photosynthesis?');

    // Find submit button
    const submitButton = studentPage.locator('button[type="submit"], [aria-label*="send"]').first();

    if (await submitButton.isVisible()) {
      await submitButton.click();

      // Should show some response or loading state
      await expect(studentPage.locator('text=/thinking|loading|processing/i')).toBeVisible();
    }
  });

  test('should maintain readable text in tool descriptions', async ({ studentPage }: any) => {
    await studentPage.goto('/student/ai-studio');

    // Check tool descriptions
    const descriptions = studentPage.locator('p, span, div').filter({
      hasText: /generate|create|practice|learn/i
    });

    for (const desc of await descriptions.all()) {
      const fontSize = await desc.evaluate((el: HTMLElement) => {
        return parseFloat(getComputedStyle(el).fontSize);
      });
      expect(fontSize).toBeGreaterThanOrEqual(12); // Minimum readable for descriptions
    }
  });
});