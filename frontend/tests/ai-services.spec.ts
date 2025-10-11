import { test, expect } from '@playwright/test';

test.describe('AI Services - Gemini Image Generation', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the main page
    await page.goto('/');
    
    // Wait for the page to load
    await page.waitForLoadState('networkidle');
  });

  test('should display AI poster generation interface', async ({ page }) => {
    // Look for AI poster generation elements
    const aiPosterSection = page.locator('[data-testid="ai-poster-section"]');
    await expect(aiPosterSection).toBeVisible();
    
    // Check for prompt input
    const promptInput = page.locator('[data-testid="poster-prompt-input"]');
    await expect(promptInput).toBeVisible();
    
    // Check for generate button
    const generateButton = page.locator('[data-testid="generate-poster-button"]');
    await expect(generateButton).toBeVisible();
  });

  test('should test Gemini API connectivity', async ({ page }) => {
    // Test API status endpoint
    const response = await page.request.get('http://localhost:8000/api/ai-poster/status/');
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data.success).toBe(true);
    expect(data.service_available).toBe(true);
  });

  test('should generate poster from text prompt', async ({ page }) => {
    // Fill in the prompt
    const promptInput = page.locator('[data-testid="poster-prompt-input"]');
    await promptInput.fill('Create a modern textile poster for a silk saree brand with elegant typography');
    
    // Select aspect ratio
    const aspectRatioSelect = page.locator('[data-testid="aspect-ratio-select"]');
    await aspectRatioSelect.selectOption('4:5');
    
    // Click generate button
    const generateButton = page.locator('[data-testid="generate-poster-button"]');
    await generateButton.click();
    
    // Wait for generation to complete
    await page.waitForSelector('[data-testid="generated-image"]', { timeout: 30000 });
    
    // Verify image is displayed
    const generatedImage = page.locator('[data-testid="generated-image"]');
    await expect(generatedImage).toBeVisible();
    
    // Check for success message
    const successMessage = page.locator('[data-testid="generation-success"]');
    await expect(successMessage).toBeVisible();
  });

  test('should handle generation errors gracefully', async ({ page }) => {
    // Test with empty prompt
    const generateButton = page.locator('[data-testid="generate-poster-button"]');
    await generateButton.click();
    
    // Should show error message
    const errorMessage = page.locator('[data-testid="generation-error"]');
    await expect(errorMessage).toBeVisible();
  });

  test('should test different aspect ratios', async ({ page }) => {
    const aspectRatios = ['1:1', '16:9', '4:5'];
    
    for (const ratio of aspectRatios) {
      // Fill prompt
      const promptInput = page.locator('[data-testid="poster-prompt-input"]');
      await promptInput.fill(`Test poster with ${ratio} aspect ratio`);
      
      // Select aspect ratio
      const aspectRatioSelect = page.locator('[data-testid="aspect-ratio-select"]');
      await aspectRatioSelect.selectOption(ratio);
      
      // Generate
      const generateButton = page.locator('[data-testid="generate-poster-button"]');
      await generateButton.click();
      
      // Wait for result
      await page.waitForSelector('[data-testid="generated-image"], [data-testid="generation-error"]', { timeout: 30000 });
      
      // Clear for next test
      await promptInput.clear();
    }
  });

  test('should test multiple prompt variations', async ({ page }) => {
    const testPrompts = [
      'Modern textile design with geometric patterns',
      'Elegant silk saree poster with gold accents',
      'Minimalist fashion poster with clean typography',
      'Traditional Indian textile with contemporary twist'
    ];
    
    for (const prompt of testPrompts) {
      // Fill prompt
      const promptInput = page.locator('[data-testid="poster-prompt-input"]');
      await promptInput.fill(prompt);
      
      // Generate
      const generateButton = page.locator('[data-testid="generate-poster-button"]');
      await generateButton.click();
      
      // Wait for result
      await page.waitForSelector('[data-testid="generated-image"], [data-testid="generation-error"]', { timeout: 30000 });
      
      // Clear for next test
      await promptInput.clear();
    }
  });
});
