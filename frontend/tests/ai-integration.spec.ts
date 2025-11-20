import { test, expect } from '@playwright/test';

test.describe('AI Integration - End-to-End Gemini Testing', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should complete full poster generation workflow', async ({ page }) => {
    // Step 1: Navigate to AI poster section
    const aiPosterSection = page.locator('[data-testid="ai-poster-section"]');
    await expect(aiPosterSection).toBeVisible();
    
    // Step 2: Fill in prompt
    const promptInput = page.locator('[data-testid="poster-prompt-input"]');
    await promptInput.fill('Create a stunning textile poster for a premium silk saree brand featuring elegant typography and rich burgundy colors');
    
    // Step 3: Select aspect ratio
    const aspectRatioSelect = page.locator('[data-testid="aspect-ratio-select"]');
    await aspectRatioSelect.selectOption('4:5');
    
    // Step 4: Generate poster
    const generateButton = page.locator('[data-testid="generate-poster-button"]');
    await generateButton.click();
    
    // Step 5: Wait for loading state
    const loadingIndicator = page.locator('[data-testid="generation-loading"]');
    await expect(loadingIndicator).toBeVisible();
    
    // Step 6: Wait for completion
    await page.waitForSelector('[data-testid="generated-image"]', { timeout: 60000 });
    
    // Step 7: Verify result
    const generatedImage = page.locator('[data-testid="generated-image"]');
    await expect(generatedImage).toBeVisible();
    
    // Step 8: Check image attributes
    const imageSrc = await generatedImage.getAttribute('src');
    expect(imageSrc).toBeTruthy();
    expect(imageSrc).toContain('generated_poster_');
    
    // Step 9: Verify success message
    const successMessage = page.locator('[data-testid="generation-success"]');
    await expect(successMessage).toBeVisible();
  });

  test('should handle generation timeout gracefully', async ({ page }) => {
    // Test with a complex prompt that might timeout
    const promptInput = page.locator('[data-testid="poster-prompt-input"]');
    await promptInput.fill('Create an extremely detailed and complex textile poster with intricate patterns, multiple colors, and sophisticated typography');
    
    const generateButton = page.locator('[data-testid="generate-poster-button"]');
    await generateButton.click();
    
    // Wait for either success or timeout
    await page.waitForSelector('[data-testid="generated-image"], [data-testid="generation-timeout"]', { timeout: 120000 });
    
    // Should either succeed or show timeout message
    const hasImage = await page.locator('[data-testid="generated-image"]').isVisible();
    const hasTimeout = await page.locator('[data-testid="generation-timeout"]').isVisible();
    
    expect(hasImage || hasTimeout).toBe(true);
  });

  test('should test different prompt styles and lengths', async ({ page }) => {
    const testCases = [
      {
        prompt: 'Simple red circle',
        description: 'Simple prompt'
      },
      {
        prompt: 'Modern minimalist textile poster with clean lines and neutral colors for a contemporary fashion brand',
        description: 'Medium complexity prompt'
      },
      {
        prompt: 'Create an elaborate and sophisticated textile poster featuring intricate paisley patterns, rich jewel tones including deep emerald, royal blue, and gold accents, elegant serif typography, and a luxurious silk texture background for a high-end Indian fashion house specializing in traditional and contemporary fusion designs',
        description: 'Complex detailed prompt'
      }
    ];
    
    for (const testCase of testCases) {
      // Fill prompt
      const promptInput = page.locator('[data-testid="poster-prompt-input"]');
      await promptInput.fill(testCase.prompt);
      
      // Generate
      const generateButton = page.locator('[data-testid="generate-poster-button"]');
      await generateButton.click();
      
      // Wait for result
      await page.waitForSelector('[data-testid="generated-image"], [data-testid="generation-error"]', { timeout: 60000 });
      
      // Verify result
      const hasImage = await page.locator('[data-testid="generated-image"]').isVisible();
      const hasError = await page.locator('[data-testid="generation-error"]').isVisible();
      
      if (hasImage) {
        console.log(`✅ ${testCase.description} - Success`);
      } else if (hasError) {
        console.log(`❌ ${testCase.description} - Error`);
      }
      
      // Clear for next test
      await promptInput.clear();
    }
  });

  test('should test all aspect ratios', async ({ page }) => {
    const aspectRatios = [
      { value: '1:1', name: 'Square' },
      { value: '16:9', name: 'Widescreen' },
      { value: '4:5', name: 'Portrait' }
    ];
    
    for (const ratio of aspectRatios) {
      // Fill prompt
      const promptInput = page.locator('[data-testid="poster-prompt-input"]');
      await promptInput.fill(`Test ${ratio.name} aspect ratio poster`);
      
      // Select aspect ratio
      const aspectRatioSelect = page.locator('[data-testid="aspect-ratio-select"]');
      await aspectRatioSelect.selectOption(ratio.value);
      
      // Generate
      const generateButton = page.locator('[data-testid="generate-poster-button"]');
      await generateButton.click();
      
      // Wait for result
      await page.waitForSelector('[data-testid="generated-image"], [data-testid="generation-error"]', { timeout: 60000 });
      
      // Verify result
      const hasImage = await page.locator('[data-testid="generated-image"]').isVisible();
      expect(hasImage).toBe(true);
      
      // Clear for next test
      await promptInput.clear();
    }
  });

  test('should test error handling and recovery', async ({ page }) => {
    // Test 1: Empty prompt
    const generateButton = page.locator('[data-testid="generate-poster-button"]');
    await generateButton.click();
    
    const errorMessage = page.locator('[data-testid="generation-error"]');
    await expect(errorMessage).toBeVisible();
    
    // Test 2: Very long prompt
    const promptInput = page.locator('[data-testid="poster-prompt-input"]');
    const longPrompt = 'A'.repeat(1000); // Very long prompt
    await promptInput.fill(longPrompt);
    await generateButton.click();
    
    // Should either succeed or show appropriate error
    await page.waitForSelector('[data-testid="generated-image"], [data-testid="generation-error"]', { timeout: 60000 });
    
    // Test 3: Special characters
    await promptInput.fill('Test prompt with special characters: !@#$%^&*()_+-=[]{}|;:,.<>?');
    await generateButton.click();
    
    await page.waitForSelector('[data-testid="generated-image"], [data-testid="generation-error"]', { timeout: 60000 });
  });

  test('should verify image quality and format', async ({ page }) => {
    const promptInput = page.locator('[data-testid="poster-prompt-input"]');
    await promptInput.fill('High quality textile poster with sharp details and vibrant colors');
    
    const generateButton = page.locator('[data-testid="generate-poster-button"]');
    await generateButton.click();
    
    await page.waitForSelector('[data-testid="generated-image"]', { timeout: 60000 });
    
    const generatedImage = page.locator('[data-testid="generated-image"]');
    await expect(generatedImage).toBeVisible();
    
    // Check image properties
    const imageSrc = await generatedImage.getAttribute('src');
    expect(imageSrc).toContain('.png'); // Should be PNG format
    
    // Check image dimensions are reasonable
    const imageElement = await generatedImage.elementHandle();
    if (imageElement) {
      const boundingBox = await imageElement.boundingBox();
      expect(boundingBox?.width).toBeGreaterThan(100);
      expect(boundingBox?.height).toBeGreaterThan(100);
    }
  });
});
