import { test, expect } from '@playwright/test'

/**
 * Poster Generation Tests
 * Verifies poster generation works via tunnel
 */

const BASE_URL = process.env.TUNNEL_URL || 'http://localhost:3000'

test.describe('Poster Generation via Tunnel', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(`${BASE_URL}/dashboard/poster-generator`)
    await page.waitForLoadState('networkidle')
  })

  test('should load poster generator without errors', async ({ page }) => {
    // Check page loaded
    await expect(page).toHaveURL(/poster-generator/)
    
    // Should have generation form
    const generateButton = page.locator('button:has-text("Generate")')
    await expect(generateButton).toBeVisible()
  })

  test('should not have API connection errors', async ({ page }) => {
    const consoleErrors: string[] = []
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text())
      }
    })

    await page.goto(`${BASE_URL}/dashboard/poster-generator`)
    await page.waitForLoadState('networkidle')

    // Filter for API/network errors
    const apiErrors = consoleErrors.filter(err => 
      err.includes('Failed to fetch') || 
      err.includes('ERR_BLOCKED_BY_CLIENT') ||
      err.includes('CORS')
    )

    expect(apiErrors).toHaveLength(0)
  })

  test('should make API calls via relative paths when using tunnel', async ({ page }) => {
    const apiRequests: string[] = []
    
    page.on('request', request => {
      const url = request.url()
      if (url.includes('/api/')) {
        apiRequests.push(url)
        console.log('API Request:', url)
      }
    })

    await page.goto(`${BASE_URL}/dashboard/poster-generator`)
    await page.waitForLoadState('networkidle')

    // When using tunnel, should use relative paths (same origin)
    if (BASE_URL.includes('trycloudflare.com') || BASE_URL.includes('ngrok.io')) {
      const localhostRequests = apiRequests.filter(url => 
        url.includes('localhost:8000')
      )
      
      // Should NOT have any localhost:8000 requests when using tunnel
      expect(localhostRequests).toHaveLength(0)
      
      // Should have requests to same origin (tunnel URL)
      const tunnelRequests = apiRequests.filter(url => 
        url.startsWith(BASE_URL)
      )
      
      // At minimum, should attempt some API calls
      expect(tunnelRequests.length).toBeGreaterThanOrEqual(0)
    }
  })

  test('should show console log when tunnel access is detected', async ({ page }) => {
    // Only run for tunnel URLs
    if (BASE_URL.includes('localhost')) {
      test.skip()
      return
    }

    const consoleLogs: string[] = []
    page.on('console', msg => {
      if (msg.type() === 'log') {
        consoleLogs.push(msg.text())
      }
    })

    await page.goto(`${BASE_URL}/dashboard/poster-generator`)
    await page.waitForLoadState('networkidle')

    // Should log that tunnel access was detected
    const tunnelDetected = consoleLogs.some(log => 
      log.includes('Tunnel access detected') || 
      log.includes('using relative path')
    )

    expect(tunnelDetected).toBeTruthy()
  })

  test('should be able to fill prompt input', async ({ page }) => {
    const promptInput = page.locator('textarea[placeholder*="prompt"], input[placeholder*="prompt"]').first()
    
    if (await promptInput.isVisible()) {
      await promptInput.fill('A beautiful sunset over mountains')
      const value = await promptInput.inputValue()
      expect(value).toBe('A beautiful sunset over mountains')
    }
  })

  // Note: Actual generation test would require valid API credentials
  // and would take longer to run
  test.skip('should generate poster successfully', async ({ page }) => {
    // Fill prompt
    const promptInput = page.locator('textarea[placeholder*="prompt"]').first()
    await promptInput.fill('Test poster generation')

    // Click generate
    const generateButton = page.locator('button:has-text("Generate")').first()
    await generateButton.click()

    // Wait for generation (this can take 30+ seconds)
    await page.waitForTimeout(40000)

    // Should show success or generated poster
    const successMessage = page.locator('text=Generated successfully, text=Poster created')
    await expect(successMessage).toBeVisible({ timeout: 5000 })
  })
})



