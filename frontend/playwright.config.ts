import { defineConfig, devices } from '@playwright/test';

/**
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  testDir: './tests',
  /* Run tests in files in parallel */
  fullyParallel: true,
  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,
  /* Retry on CI only */
  retries: process.env.CI ? 1 : 0, // Reduced retries for speed
  /* Opt out of parallel tests on CI. */
  workers: process.env.CI ? 2 : undefined, // More workers for parallel execution
  /* Reporter to use. See https://playwright.dev/docs/test-reporters */
  reporter: 'html',
  expect: {
    timeout: 3000, // Reduced assertion timeout
  },
  /* Shared settings for all the projects below. See https://playwright.dev/docs/api/class-testoptions. */
  use: {
    /* Base URL to use in actions like `await page.goto('/')`. */
    baseURL: 'http://localhost:3000',

    /* Collect trace when retrying the failed test. See https://playwright.dev/docs/trace-viewer */
    trace: 'retain-on-failure', // Only keep traces on failure
    
    /* Performance optimizations */
    actionTimeout: 5000, // Reduced timeout for faster failure detection
    navigationTimeout: 10000, // Reduced navigation timeout
    
    /* Disable images and fonts for faster loading */
    ignoreHTTPSErrors: true,
  },

  /* Configure projects for major browsers - Only essential browsers for faster testing */
  projects: [
    {
      name: 'chromium',
      use: { 
        ...devices['Desktop Chrome'],
        // Disable images and fonts for faster loading
        launchOptions: {
          args: ['--disable-images', '--disable-fonts']
        }
      },
    },

    // Only test one mobile browser for performance
    {
      name: 'Mobile Chrome',
      use: { 
        ...devices['Pixel 5'],
        launchOptions: {
          args: ['--disable-images', '--disable-fonts']
        }
      },
    },
  ],

  /* Run your local dev server before starting the tests */
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 30000, // Reduced server startup timeout
  },
});

