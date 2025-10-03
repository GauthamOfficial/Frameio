import { test, expect } from '@playwright/test';
import { setupApiMocks, setupErrorMocks, setupNetworkErrorMocks, setupSlowApiMocks } from './utils/test-setup';

test.describe('Phase 1 Week 2 - Member 2 (Frontend Lead) Tests', () => {
  // Set timeout for all tests
  test.setTimeout(30000);

  test.beforeEach(async ({ page }) => {
    // Setup API mocks to prevent real network calls
    await setupApiMocks(page);
    
    // Mock Clerk authentication
    await page.addInitScript(() => {
      // Mock Clerk's useUser hook
      window.__CLERK_MOCK_USER__ = {
        isSignedIn: true,
        isLoaded: true,
        user: {
          id: 'test-user-id',
          emailAddresses: [{ emailAddress: 'test@example.com' }],
          firstName: 'Test',
          lastName: 'User',
          fullName: 'Test User'
        }
      };
    });
    
    // Navigate to the homepage
    await page.goto('/');
  });

  test.describe('Clerk Authentication Integration', () => {
    test('should display sign in and sign up buttons on homepage', async ({ page }) => {
      // Mock unauthenticated state
      await page.addInitScript(() => {
        window.__CLERK_MOCK_USER__ = {
          isSignedIn: false,
          isLoaded: true,
          user: null
        };
      });
      
      await page.goto('/');
      
      // Check for authentication buttons
      await expect(page.locator('button:has-text("Sign In")').first()).toBeVisible({ timeout: 10000 });
      await expect(page.locator('button:has-text("Get Started")').first()).toBeVisible({ timeout: 10000 });
    });

    test('should redirect to dashboard when authenticated', async ({ page }) => {
      // Mock authenticated state
      await page.addInitScript(() => {
        window.__CLERK_MOCK_USER__ = {
          isSignedIn: true,
          isLoaded: true,
          user: {
            id: 'test-user-id',
            emailAddresses: [{ emailAddress: 'test@example.com' }],
            firstName: 'Test',
            lastName: 'User'
          }
        };
      });
      
      await page.goto('/');
      
      // Should redirect to dashboard
      await page.waitForURL('**/dashboard', { timeout: 10000 });
      await expect(page.locator('text=Dashboard')).toBeVisible({ timeout: 10000 });
    });

    test('should show user profile button when authenticated', async ({ page }) => {
      // Mock organization context for dashboard
      await page.addInitScript(() => {
        window.localStorage.setItem('user-role', 'Admin');
        window.localStorage.setItem('user-permissions', JSON.stringify(['manage_users', 'manage_organization', 'view_billing']));
        window.localStorage.setItem('organization-id', 'org-123');
      });
      
      await page.goto('/dashboard');
      
      // Wait for the page to load completely
      await page.waitForLoadState('domcontentloaded');
      
      // Check for user profile elements in top navigation
      await expect(page.locator('text=Test User').first()).toBeVisible({ timeout: 10000 });
    });
  });

  test.describe('Role-Based UI Rendering', () => {
    test('should show role badge in navigation header', async ({ page }) => {
      // Mock organization context
      await page.addInitScript(() => {
        window.localStorage.setItem('user-role', 'Admin');
        window.localStorage.setItem('user-permissions', JSON.stringify(['manage_users', 'manage_organization']));
        window.localStorage.setItem('organization-id', 'org-123');
      });

      await page.goto('/dashboard');
      
      // Wait for the page to load completely
      await page.waitForLoadState('domcontentloaded');
      
      // Check for role badge in top navigation
      await expect(page.locator('text=Admin').first()).toBeVisible({ timeout: 10000 });
    });

    test('should show different sidebar items based on role', async ({ page }) => {
      // Test Admin role
      await page.addInitScript(() => {
        window.localStorage.setItem('user-role', 'Admin');
        window.localStorage.setItem('user-permissions', JSON.stringify(['manage_users', 'manage_organization', 'view_billing']));
        window.localStorage.setItem('organization-id', 'org-123');
      });

      await page.goto('/dashboard');
      
      // Wait for the page to load completely
      await page.waitForLoadState('domcontentloaded');
      
      // Admin should see user management in sidebar
      await expect(page.locator('text=User Management').first()).toBeVisible({ timeout: 10000 });
      await expect(page.locator('text=Organization Settings').first()).toBeVisible({ timeout: 10000 });
      await expect(page.locator('text=Billing').first()).toBeVisible({ timeout: 10000 });
    });

    test('should hide admin features for Designer role', async ({ page }) => {
      // Test Designer role
      await page.addInitScript(() => {
        window.localStorage.setItem('user-role', 'Designer');
        window.localStorage.setItem('user-permissions', JSON.stringify(['manage_designs', 'view_templates']));
        window.localStorage.setItem('organization-id', 'org-123');
      });

      await page.goto('/dashboard');
      
      // Wait for the page to load completely
      await page.waitForLoadState('domcontentloaded');
      
      // Designer should not see admin features in sidebar
      await expect(page.locator('text=User Management').first()).not.toBeVisible();
      await expect(page.locator('text=Organization Settings').first()).not.toBeVisible();
      await expect(page.locator('text=Billing').first()).not.toBeVisible();
    });
  });

  test.describe('Organization Context', () => {
    test('should load organization context on dashboard', async ({ page }) => {
      // Mock organization context
      await page.addInitScript(() => {
        window.localStorage.setItem('user-role', 'Admin');
        window.localStorage.setItem('user-permissions', JSON.stringify(['manage_users', 'manage_organization']));
        window.localStorage.setItem('organization-id', 'org-123');
      });

      await page.goto('/dashboard');
      
      // Check for organization context loading
      await expect(page.locator('text=Loading...').first()).toBeVisible({ timeout: 5000 });
    });

    test('should display organization information', async ({ page }) => {
      // Mock organization data
      await page.addInitScript(() => {
        window.localStorage.setItem('user-role', 'Admin');
        window.localStorage.setItem('user-permissions', JSON.stringify(['manage_users', 'manage_organization']));
        window.localStorage.setItem('organization-id', 'org-123');
        window.localStorage.setItem('organization-name', 'Test Organization');
      });

      await page.goto('/dashboard');
      
      // Wait for loading to complete
      await page.waitForLoadState('domcontentloaded');
      
      // Check for dashboard content (organization context is loaded)
      await expect(page.locator('text=Dashboard').first()).toBeVisible({ timeout: 10000 });
    });
  });

  test.describe('User Management UI (Admin Only)', () => {
    test('should show user management page for Admin', async ({ page }) => {
      // Mock Admin role
      await page.addInitScript(() => {
        window.localStorage.setItem('user-role', 'Admin');
        window.localStorage.setItem('user-permissions', JSON.stringify(['manage_users']));
        window.localStorage.setItem('organization-id', 'org-123');
      });

      await page.goto('/dashboard/users');
      
      // Wait for page to load
      await page.waitForLoadState('domcontentloaded');
      
      // Check for user management elements
      await expect(page.locator('text=User Management').first()).toBeVisible({ timeout: 10000 });
      await expect(page.locator('text=Organization Users').first()).toBeVisible({ timeout: 10000 });
    });

    test('should show access denied for non-Admin users', async ({ page }) => {
      // Mock Designer role
      await page.addInitScript(() => {
        window.localStorage.setItem('user-role', 'Designer');
        window.localStorage.setItem('user-permissions', JSON.stringify(['manage_designs']));
        window.localStorage.setItem('organization-id', 'org-123');
      });

      await page.goto('/dashboard/users');
      
      // Wait for page to load
      await page.waitForLoadState('domcontentloaded');
      
      // Check for access denied message
      await expect(page.locator('text=Access Denied').first()).toBeVisible({ timeout: 10000 });
      await expect(page.locator('text=You don\'t have permission to manage users').first()).toBeVisible({ timeout: 10000 });
    });

    test('should display user list with search functionality', async ({ page }) => {
      // Mock Admin role and user data
      await page.addInitScript(() => {
        window.localStorage.setItem('user-role', 'Admin');
        window.localStorage.setItem('user-permissions', JSON.stringify(['manage_users']));
        window.localStorage.setItem('organization-id', 'org-123');
      });

      await page.goto('/dashboard/users');
      
      // Wait for page to load
      await page.waitForLoadState('domcontentloaded');
      
      // Check for search input
      await expect(page.locator('input[placeholder*="Search users"]').first()).toBeVisible({ timeout: 10000 });
      
      // Check for user management content
      await expect(page.locator('text=User Management').first()).toBeVisible({ timeout: 10000 });
    });

    test('should allow role changes for Admin users', async ({ page }) => {
      // Mock Admin role
      await page.addInitScript(() => {
        window.localStorage.setItem('user-role', 'Admin');
        window.localStorage.setItem('user-permissions', JSON.stringify(['manage_users']));
        window.localStorage.setItem('organization-id', 'org-123');
      });

      await page.goto('/dashboard/users');
      
      // Wait for page to load
      await page.waitForLoadState('domcontentloaded');
      
      // Check for role change buttons (Edit buttons)
      await expect(page.locator('button:has-text("Edit")').first()).toBeVisible({ timeout: 10000 });
    });
  });

  test.describe('Dashboard Layout Enhancements', () => {
    test('should show responsive sidebar', async ({ page }) => {
      // Mock organization context
      await page.addInitScript(() => {
        window.localStorage.setItem('user-role', 'Admin');
        window.localStorage.setItem('user-permissions', JSON.stringify(['manage_users', 'manage_organization']));
        window.localStorage.setItem('organization-id', 'org-123');
      });

      await page.goto('/dashboard');
      
      // Wait for page to load
      await page.waitForLoadState('domcontentloaded');
      
      // Check for sidebar
      await expect(page.locator('.fixed.inset-y-0.left-0').first()).toBeVisible({ timeout: 10000 });
      
      // Check for mobile menu button
      await expect(page.locator('button:has-text("Menu")').first()).toBeVisible({ timeout: 10000 });
    });

    test('should show top navigation with user info', async ({ page }) => {
      // Mock organization context
      await page.addInitScript(() => {
        window.localStorage.setItem('user-role', 'Admin');
        window.localStorage.setItem('user-permissions', JSON.stringify(['manage_users', 'manage_organization']));
        window.localStorage.setItem('organization-id', 'org-123');
      });

      await page.goto('/dashboard');
      
      // Wait for page to load
      await page.waitForLoadState('domcontentloaded');
      
      // Check for top navigation
      await expect(page.locator('header').first()).toBeVisible({ timeout: 10000 });
      
      // Check for search functionality
      await expect(page.locator('input[placeholder*="Search"]').first()).toBeVisible({ timeout: 10000 });
      
      // Check for notifications
      await expect(page.locator('button:has-text("Bell")').first()).toBeVisible({ timeout: 10000 });
    });

    test('should show role-based quick actions', async ({ page }) => {
      // Mock Admin role
      await page.addInitScript(() => {
        window.localStorage.setItem('user-role', 'Admin');
        window.localStorage.setItem('user-permissions', JSON.stringify(['manage_users', 'manage_organization']));
        window.localStorage.setItem('organization-id', 'org-123');
      });

      await page.goto('/dashboard');
      
      // Wait for page to load
      await page.waitForLoadState('domcontentloaded');
      
      // Check for quick actions
      await expect(page.locator('text=Quick Actions').first()).toBeVisible({ timeout: 10000 });
      
      // Admin should see user management quick action
      await expect(page.locator('text=Manage Users').first()).toBeVisible({ timeout: 10000 });
    });
  });

  test.describe('Organization Settings (Admin Only)', () => {
    test('should show organization settings for Admin', async ({ page }) => {
      // Mock Admin role
      await page.addInitScript(() => {
        window.localStorage.setItem('user-role', 'Admin');
        window.localStorage.setItem('user-permissions', JSON.stringify(['manage_organization']));
        window.localStorage.setItem('organization-id', 'org-123');
      });

      await page.goto('/dashboard/organization');
      
      // Wait for page to load
      await page.waitForLoadState('domcontentloaded');
      
      // Check for organization settings
      await expect(page.locator('text=Organization Settings').first()).toBeVisible({ timeout: 10000 });
    });

    test('should show access denied for non-Admin users', async ({ page }) => {
      // Mock Designer role
      await page.addInitScript(() => {
        window.localStorage.setItem('user-role', 'Designer');
        window.localStorage.setItem('user-permissions', JSON.stringify(['manage_designs']));
        window.localStorage.setItem('organization-id', 'org-123');
      });

      await page.goto('/dashboard/organization');
      
      // Wait for page to load
      await page.waitForLoadState('domcontentloaded');
      
      // Check for access denied message
      await expect(page.locator('text=Access Denied').first()).toBeVisible({ timeout: 10000 });
    });
  });

  test.describe('Billing Page (Admin Only)', () => {
    test('should show billing page for Admin', async ({ page }) => {
      // Mock Admin role
      await page.addInitScript(() => {
        window.localStorage.setItem('user-role', 'Admin');
        window.localStorage.setItem('user-permissions', JSON.stringify(['view_billing']));
        window.localStorage.setItem('organization-id', 'org-123');
      });

      await page.goto('/dashboard/billing');
      
      // Wait for page to load
      await page.waitForLoadState('domcontentloaded');
      
      // Check for billing elements
      await expect(page.locator('text=Billing').first()).toBeVisible({ timeout: 10000 });
    });

    test('should show access denied for non-Admin users', async ({ page }) => {
      // Mock Designer role
      await page.addInitScript(() => {
        window.localStorage.setItem('user-role', 'Designer');
        window.localStorage.setItem('user-permissions', JSON.stringify(['manage_designs']));
        window.localStorage.setItem('organization-id', 'org-123');
      });

      await page.goto('/dashboard/billing');
      
      // Wait for page to load
      await page.waitForLoadState('domcontentloaded');
      
      // Check for access denied message
      await expect(page.locator('text=Access Denied').first()).toBeVisible({ timeout: 10000 });
    });
  });

  test.describe('API Integration', () => {
    test('should handle API errors gracefully', async ({ page }) => {
      // Setup error mocks
      await setupErrorMocks(page);

      // Mock organization context
      await page.addInitScript(() => {
        window.localStorage.setItem('user-role', 'Admin');
        window.localStorage.setItem('user-permissions', JSON.stringify(['manage_users', 'manage_organization']));
        window.localStorage.setItem('organization-id', 'org-123');
      });

      await page.goto('/dashboard');
      
      // Wait for page to load
      await page.waitForLoadState('domcontentloaded');
      
      // Check for error handling
      await expect(page.locator('text=Failed to load user data').first()).toBeVisible({ timeout: 10000 });
    });

    test('should show loading states', async ({ page }) => {
      // Setup slow API mocks
      await setupSlowApiMocks(page);

      // Mock organization context
      await page.addInitScript(() => {
        window.localStorage.setItem('user-role', 'Admin');
        window.localStorage.setItem('user-permissions', JSON.stringify(['manage_users', 'manage_organization']));
        window.localStorage.setItem('organization-id', 'org-123');
      });

      await page.goto('/dashboard');
      
      // Check for loading state
      await expect(page.locator('text=Loading...').first()).toBeVisible({ timeout: 10000 });
    });
  });

  test.describe('Responsive Design', () => {
    test('should work on mobile devices', async ({ page }) => {
      // Mock organization context
      await page.addInitScript(() => {
        window.localStorage.setItem('user-role', 'Admin');
        window.localStorage.setItem('user-permissions', JSON.stringify(['manage_users', 'manage_organization']));
        window.localStorage.setItem('organization-id', 'org-123');
      });

      await page.setViewportSize({ width: 375, height: 667 });
      await page.goto('/dashboard');
      
      // Wait for page to load
      await page.waitForLoadState('domcontentloaded');
      
      // Check for mobile menu button
      await expect(page.locator('button:has-text("Menu")').first()).toBeVisible({ timeout: 10000 });
    });

    test('should work on tablet devices', async ({ page }) => {
      // Mock organization context
      await page.addInitScript(() => {
        window.localStorage.setItem('user-role', 'Admin');
        window.localStorage.setItem('user-permissions', JSON.stringify(['manage_users', 'manage_organization']));
        window.localStorage.setItem('organization-id', 'org-123');
      });

      await page.setViewportSize({ width: 768, height: 1024 });
      await page.goto('/dashboard');
      
      // Wait for page to load
      await page.waitForLoadState('domcontentloaded');
      
      // Check for responsive layout
      await expect(page.locator('.fixed.inset-y-0.left-0').first()).toBeVisible({ timeout: 10000 });
    });
  });

  test.describe('Error Handling', () => {
    test('should handle network errors', async ({ page }) => {
      // Setup network error mocks
      await setupNetworkErrorMocks(page);

      // Mock organization context
      await page.addInitScript(() => {
        window.localStorage.setItem('user-role', 'Admin');
        window.localStorage.setItem('user-permissions', JSON.stringify(['manage_users', 'manage_organization']));
        window.localStorage.setItem('organization-id', 'org-123');
      });

      await page.goto('/dashboard');
      
      // Wait for page to load
      await page.waitForLoadState('domcontentloaded');
      
      // Check for error handling
      await expect(page.locator('text=Failed to load').first()).toBeVisible({ timeout: 10000 });
    });

    test('should handle permission errors', async ({ page }) => {
      // Mock permission error
      await page.addInitScript(() => {
        window.localStorage.setItem('user-role', 'Designer');
        window.localStorage.setItem('user-permissions', JSON.stringify(['manage_designs']));
        window.localStorage.setItem('organization-id', 'org-123');
      });

      await page.goto('/dashboard/users');
      
      // Wait for page to load
      await page.waitForLoadState('domcontentloaded');
      
      // Check for permission error
      await expect(page.locator('text=Access Denied')).toBeVisible({ timeout: 10000 });
    });
  });
});
