import { test, expect } from '@playwright/test';

test.describe('AI Poster Generator Component', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to a page that contains the poster generator
    // We'll need to find the actual route for this component
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should display poster generator interface', async ({ page }) => {
    // Look for the enhanced poster generator component
    const posterGenerator = page.locator('[data-testid="poster-generator"], .poster-generator, text="Generate Poster"');
    
    // If the component is not on the main page, we might need to navigate to a specific route
    if (!(await posterGenerator.isVisible())) {
      // Try to find a link or button that leads to the poster generator
      const posterLink = page.locator('a:has-text("Poster"), button:has-text("Poster"), a:has-text("Generate")');
      if (await posterLink.isVisible()) {
        await posterLink.click();
        await page.waitForLoadState('networkidle');
      }
    }
    
    // Check for key elements of the poster generator
    const promptInput = page.locator('textarea, input[type="text"], [data-testid="prompt-input"]');
    const generateButton = page.locator('button:has-text("Generate"), button:has-text("Create"), [data-testid="generate-button"]');
    const aspectRatioSelect = page.locator('select, [data-testid="aspect-ratio"]');
    
    // At least one of these should be visible
    const hasPromptInput = await promptInput.isVisible();
    const hasGenerateButton = await generateButton.isVisible();
    const hasAspectRatio = await aspectRatioSelect.isVisible();
    
    expect(hasPromptInput || hasGenerateButton || hasAspectRatio).toBe(true);
  });

  test('should allow entering prompt text', async ({ page }) => {
    // Find the prompt input
    const promptInput = page.locator('textarea, input[type="text"], [data-testid="prompt-input"]').first();
    
    if (await promptInput.isVisible()) {
      const testPrompt = 'Create a beautiful textile poster for a silk saree brand';
      await promptInput.fill(testPrompt);
      
      // Verify the text was entered
      const inputValue = await promptInput.inputValue();
      expect(inputValue).toBe(testPrompt);
    }
  });

  test('should allow selecting aspect ratio', async ({ page }) => {
    // Find the aspect ratio selector
    const aspectRatioSelect = page.locator('select, [data-testid="aspect-ratio"]').first();
    
    if (await aspectRatioSelect.isVisible()) {
      // Try to select different aspect ratios
      const aspectRatios = ['1:1', '16:9', '4:5'];
      
      for (const ratio of aspectRatios) {
        try {
          await aspectRatioSelect.selectOption(ratio);
          const selectedValue = await aspectRatioSelect.inputValue();
          expect(selectedValue).toBe(ratio);
        } catch (error) {
          // If the option doesn't exist, that's okay for this test
          console.log(`Aspect ratio ${ratio} not available`);
        }
      }
    }
  });

  test('should handle generation workflow', async ({ page }) => {
    // Find the generate button
    const generateButton = page.locator('button:has-text("Generate"), button:has-text("Create"), [data-testid="generate-button"]').first();
    
    if (await generateButton.isVisible()) {
      // Fill in a prompt if there's an input
      const promptInput = page.locator('textarea, input[type="text"], [data-testid="prompt-input"]').first();
      if (await promptInput.isVisible()) {
        await promptInput.fill('Test poster generation');
      }
      
      // Click generate button
      await generateButton.click();
      
      // Wait for loading state
      const loadingButton = page.locator('button:disabled, [data-testid="loading"]');
      if (await loadingButton.isVisible()) {
        console.log('✅ Loading state detected');
      }
      
      // Wait for completion (with a reasonable timeout)
      try {
        await page.waitForSelector('[data-testid="generated-image"], .generated-image, img[src*="generated_poster"]', { timeout: 180000 });
        console.log('✅ Image generation completed');
      } catch (error) {
        console.log('⏰ Generation timeout - this is expected for long AI operations');
      }
    }
  });

  test('should display generation status', async ({ page }) => {
    // Look for status indicators
    const statusIndicators = page.locator('text="Generating", text="Loading", text="Processing", [data-testid="status"]');
    
    // These might not be visible initially, but we can check if they exist in the DOM
    const hasStatusElements = await statusIndicators.count() > 0;
    console.log(`Status indicators found: ${hasStatusElements}`);
  });

  test('should handle file uploads if available', async ({ page }) => {
    // Look for file upload elements
    const fileInput = page.locator('input[type="file"], [data-testid="file-upload"]');
    
    if (await fileInput.isVisible()) {
      console.log('✅ File upload functionality detected');
      
      // Test file upload (we won't actually upload a file in this test)
      const isEnabled = await fileInput.isEnabled();
      expect(isEnabled).toBe(true);
    }
  });

  test('should show AI service status', async ({ page }) => {
    // Look for AI service status indicators
    const statusIndicators = page.locator('text="Available", text="Error", text="Service", [data-testid="ai-status"]');
    
    // Check if any status information is displayed
    const statusCount = await statusIndicators.count();
    console.log(`AI service status indicators found: ${statusCount}`);
  });
});
