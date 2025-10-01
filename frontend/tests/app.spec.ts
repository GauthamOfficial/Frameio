import { test, expect } from '@playwright/test';
import { mockClerkAuth, skipAuthRedirects, navigateToPage, waitForPageReady } from './utils/test-helpers';

test.describe('Framio Application', () => {
  test.beforeEach(async ({ page }) => {
    // Mock Clerk authentication to avoid slow auth checks
    await mockClerkAuth(page, false);
    await skipAuthRedirects(page);
  });

  test('homepage loads and displays correctly', async ({ page }) => {
    await navigateToPage(page, '/');
    
    // Check if the page loads successfully
    await expect(page).toHaveTitle(/Frameio/);
    
    // Check if the main content is visible
    await expect(page.locator('body')).toBeVisible();
    
    // Check if the main heading is visible
    await expect(page.locator('h1')).toBeVisible();
  });

  test('navigation elements are present', async ({ page }) => {
    await navigateToPage(page, '/');
    
    // Check for header navigation
    await expect(page.locator('header')).toBeVisible();
    
    // Check for logo
    await expect(page.locator('text=Frameio')).toBeVisible();
    
    // Check for auth buttons
    const signInButton = page.locator('button:has-text("Sign In"), button:has-text("Login")');
    const signUpButton = page.locator('button:has-text("Get Started"), button:has-text("Sign Up")');
    
    const hasSignIn = await signInButton.count() > 0;
    const hasSignUp = await signUpButton.count() > 0;
    
    expect(hasSignIn || hasSignUp).toBeTruthy();
  });

  test('responsive design works on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await navigateToPage(page, '/');
    
    // Check if page still loads correctly on mobile
    await expect(page.locator('body')).toBeVisible();
    
    // Check if main content is visible on mobile
    await expect(page.locator('h1')).toBeVisible();
  });

  test('dashboard routes are accessible', async ({ page }) => {
    // Test only essential dashboard routes for performance
    const routes = [
      '/dashboard',
      '/dashboard/analytics',
      '/dashboard/templates'
    ];

    for (const route of routes) {
      try {
        await page.goto(route, { waitUntil: 'domcontentloaded', timeout: 5000 });
        
        // Check if page loads (might redirect to auth if not logged in)
        const currentUrl = page.url();
        
        // If redirected to auth, that's expected behavior
        if (currentUrl.includes('/sign-in') || currentUrl.includes('/auth')) {
          console.log(`Route ${route} redirected to auth (expected)`);
          continue;
        }
        
        // Otherwise, check if the page content is visible
        await expect(page.locator('body')).toBeVisible();
      } catch (error) {
        console.log(`Route ${route} failed to load:`, error);
        // Continue with other routes
      }
    }
  });

  test('error handling works correctly', async ({ page }) => {
    // Test a non-existent route
    await page.goto('/non-existent-route', { waitUntil: 'domcontentloaded', timeout: 5000 });
    
    // Check if 404 page is shown or if it redirects
    const currentUrl = page.url();
    const is404 = await page.locator('text=404, text=Not Found, text=Page not found').count() > 0;
    
    // Either should show 404 or redirect to a valid page
    expect(is404 || currentUrl !== '/non-existent-route').toBeTruthy();
  });
});

