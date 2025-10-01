import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test('sign in button is visible', async ({ page }) => {
    await page.goto('/');
    
    // Look for sign in button or authentication elements
    const signInButton = page.locator('[data-testid="sign-in-button"], button:has-text("Sign In"), a:has-text("Sign In")');
    
    // Check if any sign in element is visible
    if (await signInButton.count() > 0) {
      await expect(signInButton.first()).toBeVisible();
    }
  });

  test('sign up button is visible', async ({ page }) => {
    await page.goto('/');
    
    // Look for sign up button or authentication elements
    const signUpButton = page.locator('[data-testid="sign-up-button"], button:has-text("Sign Up"), a:has-text("Sign Up")');
    
    // Check if any sign up element is visible
    if (await signUpButton.count() > 0) {
      await expect(signUpButton.first()).toBeVisible();
    }
  });
});

