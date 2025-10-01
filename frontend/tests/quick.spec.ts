import { test, expect } from '@playwright/test';

test.describe('Quick Application Tests', () => {
  test('homepage loads and shows content', async ({ page }) => {
    // Navigate to homepage
    await page.goto('/', { waitUntil: 'domcontentloaded' });
    
    // Check page title
    await expect(page).toHaveTitle(/Frameio/);
    
    // Check if main content is visible
    await expect(page.locator('body')).toBeVisible();
    
    // Check if the hero section is present
    await expect(page.locator('h1')).toBeVisible();
    
    // Check if the logo is present
    await expect(page.locator('text=Frameio')).toBeVisible();
  });

  test('page has proper structure', async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded' });
    
    // Check for header
    await expect(page.locator('header')).toBeVisible();
    
    // Check for main content
    await expect(page.locator('main')).toBeVisible();
    
    // Check for footer
    await expect(page.locator('footer')).toBeVisible();
  });

  test('navigation elements are present', async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded' });
    
    // Check for navigation buttons
    await expect(page.locator('button')).toHaveCount({ min: 1 });
    
    // Check for sign in/up buttons
    const signInButton = page.locator('text=Sign In').or(page.locator('text=Login'));
    const signUpButton = page.locator('text=Get Started').or(page.locator('text=Sign Up'));
    
    await expect(signInButton.or(signUpButton)).toBeVisible();
  });
});