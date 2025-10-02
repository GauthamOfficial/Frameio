import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright configuration specifically for AI Services testing
 * Phase 1 Week 1 Team Member 3 implementation
 */
export default defineConfig({
  testDir: './tests',
  testMatch: ['**/ai-*.spec.ts'],
  
  /* Run tests in files in parallel */
  fullyParallel: true,
  
  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,
  
  /* Retry on CI only */
  retries: process.env.CI ? 2 : 1,
  
  /* Opt out of parallel tests on CI. */
  workers: process.env.CI ? 2 : 4,
  
  /* Reporter to use */
  reporter: [
    ['html', { outputFolder: 'playwright-report/ai-services' }],
    ['json', { outputFile: 'test-results/ai-services-results.json' }],
    ['junit', { outputFile: 'test-results/ai-services-junit.xml' }]
  ],
  
  /* Shared settings for all projects */
  use: {
    /* Base URL for the frontend */
    baseURL: 'http://localhost:3000',
    
    /* Collect trace when retrying the failed test */
    trace: 'retain-on-failure',
    
    /* Screenshot on failure */
    screenshot: 'only-on-failure',
    
    /* Video recording */
    video: 'retain-on-failure',
    
    /* Performance optimizations for AI testing */
    actionTimeout: 10000, // AI operations might take longer
    navigationTimeout: 15000,
    expect: {
      timeout: 5000,
    },
    
    /* Ignore HTTPS errors for local development */
    ignoreHTTPSErrors: true,
    
    /* Extra HTTP headers */
    extraHTTPHeaders: {
      'X-Test-Suite': 'AI-Services',
      'X-Organization': 'ai-test-org'
    }
  },

  /* Configure projects for different test scenarios */
  projects: [
    {
      name: 'ai-services-desktop',
      use: { 
        ...devices['Desktop Chrome'],
        viewport: { width: 1280, height: 720 },
        launchOptions: {
          args: [
            '--disable-web-security',
            '--disable-features=VizDisplayCompositor'
          ]
        }
      },
      testMatch: ['**/ai-services.spec.ts', '**/ai-integration.spec.ts']
    },

    {
      name: 'ai-backend-api',
      use: { 
        ...devices['Desktop Chrome'],
        baseURL: 'http://localhost:8000' // Django backend
      },
      testMatch: ['**/ai-backend-api.spec.ts']
    },

    {
      name: 'ai-services-mobile',
      use: { 
        ...devices['Pixel 5'],
        launchOptions: {
          args: ['--disable-web-security']
        }
      },
      testMatch: ['**/ai-services.spec.ts']
    },

    {
      name: 'ai-services-firefox',
      use: { 
        ...devices['Desktop Firefox']
      },
      testMatch: ['**/ai-services.spec.ts']
    }
  ],

  /* Global setup and teardown */
  globalSetup: require.resolve('./tests/utils/global-setup.ts'),
  globalTeardown: require.resolve('./tests/utils/global-teardown.ts'),

  /* Run local dev servers before starting tests */
  webServer: [
    {
      command: 'npm run dev',
      url: 'http://localhost:3000',
      reuseExistingServer: !process.env.CI,
      timeout: 120000,
      env: {
        NODE_ENV: 'test',
        NEXT_PUBLIC_API_URL: 'http://localhost:8000'
      }
    },
    {
      command: 'cd ../backend && python manage.py runserver 8000',
      url: 'http://localhost:8000/api/',
      reuseExistingServer: !process.env.CI,
      timeout: 60000,
      env: {
        DJANGO_SETTINGS_MODULE: 'frameio_backend.settings',
        DEBUG: 'True'
      }
    }
  ],

  /* Test output directories */
  outputDir: 'test-results/ai-services',
  
  /* Expect configuration */
  expect: {
    /* Custom matchers timeout */
    timeout: 5000,
    
    /* Screenshot comparison threshold */
    threshold: 0.2,
    
    /* Animation handling */
    animations: 'disabled'
  }
});
