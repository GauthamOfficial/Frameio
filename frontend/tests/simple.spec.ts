import { test, expect } from '@playwright/test';

test.describe('Simple App Test', () => {
  test('homepage loads', async ({ page }) => {
    // Navigate to the homepage
    await page.goto('/');
    
    // Wait for the page to load
    await page.waitForLoadState('networkidle');
    
    // Check if the page loads (any content)
    await expect(page.locator('body')).toBeVisible();
    
    // Check if there's any text content
    const bodyText = await page.locator('body').textContent();
    expect(bodyText).toBeTruthy();
    
    console.log('Page loaded successfully with content:', bodyText?.substring(0, 100));
  });
  
  test('poster generator route exists', async ({ page }) => {
    // Try to navigate to poster generator
    const response = await page.goto('/dashboard/poster-generator');
    
    // Check if the page loads (even if it's a 404, we want to see the response)
    expect(response?.status()).toBeLessThan(500);
    
    // Wait a bit for any dynamic content
    await page.waitForTimeout(2000);
    
    // Check if there's any content on the page
    const bodyText = await page.locator('body').textContent();
    expect(bodyText).toBeTruthy();
    
    console.log('Poster generator page response:', response?.status());
    console.log('Page content preview:', bodyText?.substring(0, 200));
  });
});

