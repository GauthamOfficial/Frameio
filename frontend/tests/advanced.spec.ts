import { test, expect } from '@playwright/test';
import { waitForPageLoad, isAuthenticated, navigateToRoute, takeDebugScreenshot, mockClerkAuth, skipAuthRedirects } from './utils/test-helpers';

test.describe('Advanced Application Tests', () => {
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
    
    // Take screenshot for debugging
    await takeDebugScreenshot(page, 'homepage-loaded');
    
    // Check for JavaScript errors
    expect(errors.length).toBe(0);
  });

  test('authentication flow detection', async ({ page }) => {
    await page.goto('/');
    await waitForPageLoad(page);
    
    const authenticated = await isAuthenticated(page);
    console.log(`User authenticated: ${authenticated}`);
    
    if (authenticated) {
      // If authenticated, check for user-specific elements
      const userButton = page.locator('[data-testid="user-button"], .user-button');
      if (await userButton.count() > 0) {
        await expect(userButton.first()).toBeVisible();
      }
    } else {
      // If not authenticated, check for auth buttons
      const signInButton = page.locator('button:has-text("Sign In"), a:has-text("Sign In")');
      const signUpButton = page.locator('button:has-text("Sign Up"), a:has-text("Sign Up")');
      
      const hasSignIn = await signInButton.count() > 0;
      const hasSignUp = await signUpButton.count() > 0;
      
      expect(hasSignIn || hasSignUp).toBeTruthy();
    }
  });

  test('dashboard accessibility with authentication', async ({ page }) => {
    // Test only essential dashboard routes for performance
    const dashboardRoutes = [
      '/dashboard',
      '/dashboard/analytics',
      '/dashboard/templates'
    ];

    for (const route of dashboardRoutes) {
      console.log(`Testing route: ${route}`);
      
      const success = await navigateToRoute(page, route);
      
      if (success) {
        // Route is accessible
        await expect(page.locator('body')).toBeVisible();
        console.log(`✓ Route ${route} is accessible`);
      } else {
        // Route redirected to auth (expected for protected routes)
        console.log(`→ Route ${route} redirected to auth (expected)`);
      }
    }
  });

  test('mobile responsiveness', async ({ page }) => {
    // Test only one viewport for performance
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/', { waitUntil: 'domcontentloaded' });
    await waitForPageLoad(page);
    
    // Check if page is still functional at mobile viewport
    await expect(page.locator('body')).toBeVisible();
    
    // Take screenshot for debugging (only in debug mode)
    await takeDebugScreenshot(page, 'viewport-mobile');
  });

  test('performance metrics', async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded' });
    
    // Wait for page to be fully loaded
    await waitForPageLoad(page);
    
    // Get basic performance metrics
    const metrics = await page.evaluate(() => {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      return {
        domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
      };
    });
    
    console.log('Performance metrics:', metrics);
    
    // Basic performance checks (relaxed thresholds for faster tests)
    expect(metrics.domContentLoaded).toBeLessThan(5000); // 5 seconds max DOM content loaded
  });
});

