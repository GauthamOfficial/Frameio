import { defineConfig, devices } from '@playwright/test';

/**
 * Development Playwright configuration - Ultra fast for development
 * Only tests on Chromium with maximum performance optimizations
 */
export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: 0, // No retries for maximum speed
  workers: 4, // Maximum parallel workers
  reporter: 'list', // Simple list reporter for speed
  expect: {
    timeout: 2000, // Very fast assertions
  },
  
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'off', // No tracing for speed
    actionTimeout: 3000, // Very fast timeout
    navigationTimeout: 5000,
    ignoreHTTPSErrors: true,
    // Disable all non-essential features
    launchOptions: {
      args: [
        '--disable-images',
        '--disable-fonts',
        '--disable-javascript',
        '--disable-plugins',
        '--disable-extensions',
        '--disable-web-security',
        '--disable-features=VizDisplayCompositor',
        '--no-sandbox',
        '--disable-dev-shm-usage'
      ]
    }
  },

  // Only test on Chromium for maximum speed
  projects: [
    {
      name: 'chromium',
      use: { 
        ...devices['Desktop Chrome'],
        launchOptions: {
          args: [
            '--disable-images',
            '--disable-fonts',
            '--disable-javascript',
            '--disable-plugins',
            '--disable-extensions',
            '--disable-web-security',
            '--disable-features=VizDisplayCompositor',
            '--no-sandbox',
            '--disable-dev-shm-usage'
          ]
        }
      },
    },
  ],

  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: true, // Always reuse server
    timeout: 20000, // Faster server startup
  },
});
