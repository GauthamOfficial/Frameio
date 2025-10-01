import { test, expect } from '@playwright/test';
import { mockClerkAuth, skipAuthRedirects, waitForPageLoad } from './utils/test-helpers';

test.describe('Advanced Application Tests (Fast)', () => {
  test.beforeEach(async ({ page }) => {
    // Mock Clerk authentication to avoid slow auth checks
    await mockClerkAuth(page, false);
    await skipAuthRedirects(page);
  });

  test('application loads without JavaScript errors', async ({ page }) => {
    const errors: string[] = [];
    
    // Listen for console errors
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });
    
    // Listen for page errors
    page.on('pageerror', error => {
      errors.push(error.message);
    });
    
    await page.goto('/', { waitUntil: 'domcontentloaded' });
    await waitForPageLoad(page);
    
    // Check for JavaScript errors
    expect(errors.length).toBe(0);
  });

  test('authentication flow detection', async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded' });
    await waitForPageLoad(page);
    
    // Check for auth buttons (not authenticated)
    const signInButton = page.locator('button:has-text("Sign In"), a:has-text("Sign In")');
    const signUpButton = page.locator('button:has-text("Get Started"), a:has-text("Sign Up")');
    
    const hasSignIn = await signInButton.count() > 0;
    const hasSignUp = await signUpButton.count() > 0;
    
    expect(hasSignIn || hasSignUp).toBeTruthy();
  });

  test('mobile responsiveness', async ({ page }) => {
    // Test mobile viewport only
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/', { waitUntil: 'domcontentloaded' });
    await waitForPageLoad(page);
    
    // Check if page is still functional at mobile viewport
    await expect(page.locator('body')).toBeVisible();
  });

  test('basic performance check', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('/', { waitUntil: 'domcontentloaded' });
    await waitForPageLoad(page);
    const loadTime = Date.now() - startTime;
    
    // Basic performance check (should be under 3 seconds)
    expect(loadTime).toBeLessThan(3000);
  });
});
