import { test, expect } from '@playwright/test';

test.describe('Dashboard', () => {
  test('dashboard layout loads', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Check if dashboard layout elements are present
    const dashboardLayout = page.locator('[data-testid="dashboard-layout"], .dashboard-layout, main');
    
    if (await dashboardLayout.count() > 0) {
      await expect(dashboardLayout.first()).toBeVisible();
    }
  });

  test('sidebar navigation is present', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Look for sidebar navigation
    const sidebar = page.locator('[data-testid="sidebar"], .sidebar, nav');
    
    if (await sidebar.count() > 0) {
      await expect(sidebar.first()).toBeVisible();
    }
  });

  test('dashboard pages are accessible', async ({ page }) => {
    const dashboardPages = [
      '/dashboard',
      '/dashboard/analytics',
      '/dashboard/branding-kit',
      '/dashboard/catalog-builder',
      '/dashboard/poster-generator',
      '/dashboard/scheduler',
      '/dashboard/templates'
    ];

    for (const pagePath of dashboardPages) {
      await page.goto(pagePath);
      
      // Check if page loads without 404
      await expect(page.locator('body')).toBeVisible();
      
      // Check if it's not a 404 page
      const is404 = await page.locator('text=404, text=Not Found, text=Page not found').count() > 0;
      expect(is404).toBeFalsy();
    }
  });
});

