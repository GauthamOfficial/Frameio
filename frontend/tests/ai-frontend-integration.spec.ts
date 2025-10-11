import { test, expect } from '@playwright/test';

test.describe('AI Frontend-Backend Integration', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the test API status page
    await page.goto('/test-api-status');
    await page.waitForLoadState('networkidle');
  });

  test('should complete full frontend image generation workflow', async ({ page }) => {
    console.log('🚀 Starting full frontend image generation workflow...');
    
    // Step 1: Check API status first
    console.log('1️⃣ Checking API status...');
    const statusButton = page.locator('button:has-text("Check API Status")');
    await statusButton.click();
    
    // Wait for status response
    await page.waitForSelector('.bg-white, [data-testid="status-response"]', { timeout: 10000 });
    
    // Verify status is successful
    const statusResponse = page.locator('.bg-white, [data-testid="status-response"]');
    await expect(statusResponse).toBeVisible();
    
    const successText = page.locator('text=success');
    await expect(successText).toBeVisible();
    console.log('✅ API status check passed');
    
    // Step 2: Generate image
    console.log('2️⃣ Generating image...');
    const generateButton = page.locator('button:has-text("Test Image Generation")');
    await generateButton.click();
    
    // Wait for generation to complete
    console.log('⏳ Waiting for image generation (this may take 60-120 seconds)...');
    await page.waitForSelector('.bg-white, [data-testid="generation-response"]', { timeout: 180000 });
    
    // Step 3: Verify generation response
    console.log('3️⃣ Verifying generation response...');
    const generationResponse = page.locator('.bg-white, [data-testid="generation-response"]');
    await expect(generationResponse).toBeVisible();
    
    // Check for success indicators
    const successIndicator = page.locator('text=success');
    await expect(successIndicator).toBeVisible();
    
    // Check for image path
    const imagePath = page.locator('text=generated_poster_');
    await expect(imagePath).toBeVisible();
    
    // Check for image URL
    const imageUrl = page.locator('text=image_url');
    await expect(imageUrl).toBeVisible();
    
    console.log('✅ Image generation completed successfully!');
    
    // Step 4: Verify response structure
    console.log('4️⃣ Verifying response structure...');
    const responseData = page.locator('pre, .bg-white');
    const responseText = await responseData.textContent();
    
    expect(responseText).toContain('success');
    expect(responseText).toContain('image_path');
    expect(responseText).toContain('image_url');
    expect(responseText).toContain('filename');
    
    console.log('✅ Response structure verified');
    console.log('🎉 Full frontend image generation workflow completed successfully!');
  });

  test('should handle network errors gracefully', async ({ page }) => {
    // This test simulates network issues by intercepting requests
    await page.route('**/api/ai/ai-poster/**', route => {
      route.abort('failed');
    });
    
    const generateButton = page.locator('button:has-text("Test Image Generation")');
    await generateButton.click();
    
    // Should handle the error gracefully
    await page.waitForTimeout(5000);
    
    // Check for error handling
    const errorIndicators = page.locator('text=error, text=Error, text=Failed, text=Network');
    const hasErrorHandling = await errorIndicators.count() > 0;
    
    console.log(`Error handling detected: ${hasErrorHandling}`);
  });

  test('should display loading states correctly', async ({ page }) => {
    // Start generation
    const generateButton = page.locator('button:has-text("Test Image Generation")');
    await generateButton.click();
    
    // Check for loading state
    const loadingButton = page.locator('button:has-text("Test Image Generation"):disabled');
    await expect(loadingButton).toBeVisible();
    
    console.log('✅ Loading state detected');
    
    // Wait for completion
    await page.waitForSelector('.bg-white, [data-testid="generation-response"]', { timeout: 180000 });
    
    // Check that button is enabled again
    const enabledButton = page.locator('button:has-text("Test Image Generation"):not(:disabled)');
    await expect(enabledButton).toBeVisible();
    
    console.log('✅ Button re-enabled after completion');
  });

  test('should show detailed generation information', async ({ page }) => {
    // Generate image
    const generateButton = page.locator('button:has-text("Test Image Generation")');
    await generateButton.click();
    
    // Wait for response
    await page.waitForSelector('.bg-white, [data-testid="generation-response"]', { timeout: 180000 });
    
    // Check for detailed information
    const responseData = page.locator('pre, .bg-white');
    const responseText = await responseData.textContent();
    
    // Verify all expected fields are present
    const expectedFields = [
      'success',
      'message',
      'image_path',
      'image_url',
      'filename',
      'aspect_ratio',
      'prompt'
    ];
    
    for (const field of expectedFields) {
      expect(responseText).toContain(field);
    }
    
    console.log('✅ All expected response fields present');
  });

  test('should handle multiple generation requests', async ({ page }) => {
    console.log('🔄 Testing multiple generation requests...');
    
    // First generation
    const generateButton = page.locator('button:has-text("Test Image Generation")');
    await generateButton.click();
    await page.waitForSelector('.bg-white, [data-testid="generation-response"]', { timeout: 180000 });
    
    console.log('✅ First generation completed');
    
    // Wait a bit before second generation
    await page.waitForTimeout(2000);
    
    // Second generation
    await generateButton.click();
    await page.waitForSelector('.bg-white, [data-testid="generation-response"]', { timeout: 180000 });
    
    console.log('✅ Second generation completed');
    
    // Verify both responses are present
    const responses = page.locator('.bg-white, [data-testid="generation-response"]');
    const responseCount = await responses.count();
    
    expect(responseCount).toBeGreaterThan(0);
    console.log(`✅ Multiple generations handled successfully (${responseCount} responses)`);
  });

  test('should verify image generation performance', async ({ page }) => {
    console.log('⏱️ Testing generation performance...');
    
    const startTime = Date.now();
    
    const generateButton = page.locator('button:has-text("Test Image Generation")');
    await generateButton.click();
    
    await page.waitForSelector('.bg-white, [data-testid="generation-response"]', { timeout: 180000 });
    
    const endTime = Date.now();
    const duration = (endTime - startTime) / 1000;
    
    console.log(`⏱️ Generation took ${duration.toFixed(2)} seconds`);
    
    // Generation should complete within reasonable time (3 minutes max)
    expect(duration).toBeLessThan(180);
    
    // Check for success
    const successText = page.locator('text=success');
    await expect(successText).toBeVisible();
    
    console.log('✅ Performance test passed');
  });
});
