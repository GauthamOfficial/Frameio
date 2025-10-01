import { test, expect } from '@playwright/test';
import { mockClerkAuth, waitForPageReady, navigateToPage, skipAuthRedirects } from './utils/test-helpers';

test.describe('Basic Application Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Mock Clerk authentication to avoid slow auth checks
    await mockClerkAuth(page, false);
    await skipAuthRedirects(page);
  });

  test('homepage loads correctly', async ({ page }) => {
    await navigateToPage(page, '/');
    
    // Check if the page title is correct
    await expect(page).toHaveTitle(/Frameio/);
    
    // Check if the page loads without errors
    await expect(page.locator('body')).toBeVisible();
    
    // Check if the main content is visible
    await expect(page.locator('h1')).toBeVisible();
  });

  test('navigation works', async ({ page }) => {
    await navigateToPage(page, '/');
    
    // Check if navigation elements are present
    const navigation = page.locator('header');
    await expect(navigation).toBeVisible();
    
    // Check if logo is present
    await expect(page.locator('text=Frameio')).toBeVisible();
  });

  test('dashboard page loads', async ({ page }) => {
    // Mock as signed in user for dashboard access
    await mockClerkAuth(page, true);
    await navigateToPage(page, '/dashboard');
    
    // Check if dashboard loads
    await expect(page.locator('body')).toBeVisible();
  });
});

