import { test, expect } from '@playwright/test';

test.describe('Poster Generator', () => {
  test('poster generator page loads and AI preview works', async ({ page }) => {
    // Navigate to the poster generator page
    await page.goto('/dashboard/poster-generator');
    
    // Wait for the page to load
    await page.waitForLoadState('networkidle');
    
    // Check if the page title or heading is present
    await expect(page.locator('h1, h2, h3')).toContainText(/poster|generate|ai/i);
    
    // Check if the prompt input is present
    const promptInput = page.locator('textarea, input[type="text"]').first();
    await expect(promptInput).toBeVisible();
    
    // Enter a test prompt
    await promptInput.fill('luxury red silk saree poster, festive sale, modern layout, studio lighting');
    
    // Look for generate button
    const generateButton = page.locator('button').filter({ hasText: /generate|create|submit/i });
    await expect(generateButton).toBeVisible();
    
    // Click generate button
    await generateButton.click();
    
    // Wait for AI generation to complete (should show fallback mode)
    await page.waitForTimeout(3000);
    
    // Check if AI Generated Preview appears
    const previewSection = page.locator('[data-testid="ai-preview"], .ai-preview, .generated-poster').first();
    await expect(previewSection).toBeVisible();
    
    // Check if fallback mode indicator is present (since we're using placeholder API key)
    const fallbackIndicator = page.locator('text=Fallback Mode, text=frontend_fallback, .fallback-indicator').first();
    await expect(fallbackIndicator).toBeVisible();
    
    // Check if image is generated
    const generatedImage = page.locator('img[alt*="AI Generated"], img[alt*="poster"]').first();
    await expect(generatedImage).toBeVisible();
  });
});

