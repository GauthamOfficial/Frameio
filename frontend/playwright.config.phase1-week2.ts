import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright configuration for Phase 1 Week 2 - Member 2 (Frontend Lead) tests
 * Tests authentication, role-based UI, user management, and organization features
 */
export default defineConfig({
  testDir: './tests',
  testMatch: '**/phase1-week2-member2.spec.ts',
  
  /* Run tests in files in parallel */
  fullyParallel: true,
  
  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,
  
  /* Retry on CI only */
  retries: process.env.CI ? 2 : 0,
  
  /* Opt out of parallel tests on CI. */
  workers: process.env.CI ? 1 : 4,
  
  /* Set global timeout for all tests */
  timeout: 10000,
  
  /* Reporter to use. See https://playwright.dev/docs/test-reporters */
  reporter: [
    ['html', { outputFolder: 'playwright-report/phase1-week2' }],
    ['json', { outputFile: 'test-results/phase1-week2-results.json' }]
  ],
  
  /* Shared settings for all the projects below. See https://playwright.dev/docs/api/class-testoptions. */
  use: {
    /* Base URL to use in actions like `await page.goto('/')`. */
    baseURL: 'http://localhost:3000',
    
    /* Collect trace when retrying the failed test. See https://playwright.dev/docs/trace-viewer */
    trace: 'on-first-retry',
    
    /* Take screenshot on failure */
    screenshot: 'only-on-failure',
    
    /* Record video on failure */
    video: 'retain-on-failure',
  },

  /* Configure projects for major browsers */
  projects: [
    {
      name: 'phase1-week2-chromium',
      use: { 
        ...devices['Desktop Chrome'],
        // Mock authentication for testing
        storageState: {
          cookies: [],
          origins: [
            {
              origin: 'http://localhost:3000',
              localStorage: [
                {
                  name: 'clerk-db-jwt',
                  value: 'mock-jwt-token'
                },
                {
                  name: 'user-role',
                  value: 'Admin'
                },
                {
                  name: 'user-permissions',
                  value: JSON.stringify(['manage_users', 'manage_organization', 'view_billing'])
                },
                {
                  name: 'organization-id',
                  value: 'org-123'
                }
              ]
            }
          ]
        }
      },
    },

    {
      name: 'phase1-week2-firefox',
      use: { 
        ...devices['Desktop Firefox'],
        storageState: {
          cookies: [],
          origins: [
            {
              origin: 'http://localhost:3000',
              localStorage: [
                {
                  name: 'clerk-db-jwt',
                  value: 'mock-jwt-token'
                },
                {
                  name: 'user-role',
                  value: 'Manager'
                },
                {
                  name: 'user-permissions',
                  value: JSON.stringify(['manage_designs', 'view_analytics', 'manage_templates'])
                }
              ]
            }
          ]
        }
      },
    },

    {
      name: 'phase1-week2-webkit',
      use: { 
        ...devices['Desktop Safari'],
        storageState: {
          cookies: [],
          origins: [
            {
              origin: 'http://localhost:3000',
              localStorage: [
                {
                  name: 'clerk-db-jwt',
                  value: 'mock-jwt-token'
                },
                {
                  name: 'user-role',
                  value: 'Designer'
                },
                {
                  name: 'user-permissions',
                  value: JSON.stringify(['manage_designs', 'view_templates'])
                }
              ]
            }
          ]
        }
      },
    },

    /* Test against mobile viewports. */
    {
      name: 'phase1-week2-mobile-chrome',
      use: { 
        ...devices['Pixel 5'],
        storageState: {
          cookies: [],
          origins: [
            {
              origin: 'http://localhost:3000',
              localStorage: [
                {
                  name: 'clerk-db-jwt',
                  value: 'mock-jwt-token'
                },
                {
                  name: 'user-role',
                  value: 'Admin'
                },
                {
                  name: 'user-permissions',
                  value: JSON.stringify(['manage_users', 'manage_organization', 'view_billing'])
                }
              ]
            }
          ]
        }
      },
    },

    {
      name: 'phase1-week2-mobile-safari',
      use: { 
        ...devices['iPhone 12'],
        storageState: {
          cookies: [],
          origins: [
            {
              origin: 'http://localhost:3000',
              localStorage: [
                {
                  name: 'clerk-db-jwt',
                  value: 'mock-jwt-token'
                },
                {
                  name: 'user-role',
                  value: 'Designer'
                },
                {
                  name: 'user-permissions',
                  value: JSON.stringify(['manage_designs', 'view_templates'])
                }
              ]
            }
          ]
        }
      },
    },
  ],

  /* Run your local dev server before starting the tests */
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
});
