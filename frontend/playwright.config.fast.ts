import { defineConfig, devices } from '@playwright/test';

/**
 * Fast Playwright configuration for development and CI
 * Optimized for speed over comprehensive testing
 */
export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0, // Reduced retries for speed
  workers: process.env.CI ? 2 : undefined, // More workers for parallel execution
  reporter: 'html',
  
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'retain-on-failure', // Only keep traces on failure
    actionTimeout: 5000, // Reduced timeout for faster failure detection
    navigationTimeout: 10000,
    expect: {
      timeout: 3000, // Reduced assertion timeout
    },
  },

  // Only test on Chromium for maximum speed
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 30000, // Reduced server startup timeout
  },
});
