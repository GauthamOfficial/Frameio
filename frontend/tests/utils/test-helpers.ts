import { Page } from '@playwright/test';

/**
 * Mock Clerk authentication to avoid slow auth checks in tests
 */
export async function mockClerkAuth(page: Page, isSignedIn: boolean = false) {
  await page.addInitScript((isSignedIn) => {
    // Mock Clerk's useUser hook
    window.__CLERK_MOCK_USER__ = {
      isSignedIn,
      isLoaded: true,
      user: isSignedIn ? {
        id: 'test-user-id',
        emailAddresses: [{ emailAddress: 'test@example.com' }],
        firstName: 'Test',
        lastName: 'User'
      } : null
    };

    // Override Clerk's useUser hook
    if (typeof window !== 'undefined') {
      const originalUseUser = (window as any).__CLERK_USE_USER__;
      (window as any).__CLERK_USE_USER__ = () => window.__CLERK_MOCK_USER__;
    }
  }, isSignedIn);
}

/**
 * Wait for page to be ready without waiting for Clerk auth
 */
export async function waitForPageReady(page: Page) {
  // Wait for the page to load but skip Clerk auth checks
  await page.waitForLoadState('domcontentloaded');
  
  // Wait for any loading spinners to disappear
  await page.waitForFunction(() => {
    const loadingElements = document.querySelectorAll('[data-testid="loading"], .animate-pulse');
    return loadingElements.length === 0;
  }, { timeout: 5000 }).catch(() => {
    // Ignore timeout if no loading elements found
  });
}

/**
 * Navigate to a page with optimized loading
 */
export async function navigateToPage(page: Page, path: string) {
  await page.goto(path, { 
    waitUntil: 'domcontentloaded',
    timeout: 10000 
  });
  await waitForPageReady(page);
}

/**
 * Skip authentication redirects in tests
 */
export async function skipAuthRedirects(page: Page) {
  await page.addInitScript(() => {
    // Prevent automatic redirects to dashboard
    const originalPush = window.history.pushState;
    window.history.pushState = function(state, title, url) {
      if (url && url.includes('/dashboard')) {
        console.log('Skipping redirect to dashboard in test');
        return;
      }
      return originalPush.call(this, state, title, url);
    };
  });
}

/**
 * Wait for page load with optimized timeout
 */
export async function waitForPageLoad(page: Page) {
  await page.waitForLoadState('domcontentloaded');
  // Skip waiting for network idle to save time
}

/**
 * Check if user is authenticated (mocked)
 */
export async function isAuthenticated(page: Page): Promise<boolean> {
  // Mock authentication check to avoid slow Clerk calls
  return false; // Default to not authenticated for faster tests
}

/**
 * Navigate to route with error handling
 */
export async function navigateToRoute(page: Page, route: string): Promise<boolean> {
  try {
    await page.goto(route, { waitUntil: 'domcontentloaded', timeout: 5000 });
    return true;
  } catch (error) {
    console.log(`Failed to navigate to ${route}:`, error);
    return false;
  }
}

/**
 * Take debug screenshot (only in debug mode)
 */
export async function takeDebugScreenshot(page: Page, name: string) {
  // Only take screenshots in debug mode to avoid slowing down tests
  if (process.env.DEBUG_SCREENSHOTS === 'true') {
    await page.screenshot({ path: `debug-${name}.png` });
  }
}