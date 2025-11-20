import { test, expect } from '@playwright/test'

/**
 * Tunnel Health Check Tests
 * Verifies the Cloudflare Tunnel is working and pages load correctly
 */

// Get tunnel URL from environment or use localhost as fallback
const BASE_URL = process.env.TUNNEL_URL || 'http://localhost:3000'

test.describe('Tunnel Health Checks', () => {
  test('should load dashboard without errors', async ({ page }) => {
    // Navigate to dashboard
    const response = await page.goto(`${BASE_URL}/dashboard`)
    
    // Should not get Cloudflare error
    expect(response?.status()).not.toBe(530)
    expect(response?.status()).toBeLessThan(400)
    
    // Should load the page
    await expect(page).toHaveTitle(/Dashboard/i)
    
    // Should not show Cloudflare Tunnel error
    await expect(page.locator('text=Cloudflare Tunnel error')).not.toBeVisible()
  })

  test('should load dashboard stats without API errors', async ({ page }) => {
    // Listen for console errors
    const consoleErrors: string[] = []
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text())
      }
    })

    // Navigate to dashboard
    await page.goto(`${BASE_URL}/dashboard`)
    await page.waitForLoadState('networkidle')

    // Check for ERR_BLOCKED_BY_CLIENT errors
    const blockedErrors = consoleErrors.filter(err => 
      err.includes('ERR_BLOCKED_BY_CLIENT')
    )
    expect(blockedErrors).toHaveLength(0)

    // Check for network errors
    const networkErrors = consoleErrors.filter(err => 
      err.includes('Failed to fetch') || err.includes('NetworkError')
    )
    expect(networkErrors).toHaveLength(0)
  })

  test('should make API calls via relative paths when using tunnel', async ({ page }) => {
    // Track network requests
    const apiRequests: string[] = []
    page.on('request', request => {
      const url = request.url()
      if (url.includes('/api/')) {
        apiRequests.push(url)
      }
    })

    // Navigate to dashboard
    await page.goto(`${BASE_URL}/dashboard`)
    await page.waitForLoadState('networkidle')

    // Should have made API requests
    expect(apiRequests.length).toBeGreaterThan(0)

    // When accessed via tunnel, requests should be relative (same origin)
    if (BASE_URL.includes('trycloudflare.com') || BASE_URL.includes('ngrok.io')) {
      const relativeRequests = apiRequests.filter(url => 
        url.startsWith(BASE_URL) && !url.includes('localhost')
      )
      expect(relativeRequests.length).toBeGreaterThan(0)
      
      // Should NOT have localhost in API URLs when using tunnel
      const localhostRequests = apiRequests.filter(url => 
        url.includes('localhost:8000')
      )
      expect(localhostRequests).toHaveLength(0)
    }
  })

  test('should load poster generator page', async ({ page }) => {
    const response = await page.goto(`${BASE_URL}/dashboard/poster-generator`)
    
    expect(response?.status()).toBeLessThan(400)
    await expect(page.locator('text=Generate Poster')).toBeVisible()
  })

  test('should load social media page', async ({ page }) => {
    const response = await page.goto(`${BASE_URL}/dashboard/social-media`)
    
    expect(response?.status()).toBeLessThan(400)
    // Should show the page, even if no posters yet
    await expect(page).toHaveURL(/social-media/)
  })
})

test.describe('API Integration via Tunnel', () => {
  test('should fetch posters without CORS errors', async ({ page }) => {
    const responses: any[] = []
    
    page.on('response', response => {
      if (response.url().includes('/api/ai/ai-poster/posters/')) {
        responses.push({
          status: response.status(),
          url: response.url()
        })
      }
    })

    await page.goto(`${BASE_URL}/dashboard/social-media`)
    await page.waitForLoadState('networkidle')

    // Should have attempted to fetch posters
    expect(responses.length).toBeGreaterThan(0)
    
    // Should not get CORS errors (status 0) or blocked
    const failedRequests = responses.filter(r => r.status === 0 || r.status >= 500)
    expect(failedRequests).toHaveLength(0)
  })

  test('should fetch branding kits without errors', async ({ page }) => {
    const responses: any[] = []
    
    page.on('response', response => {
      if (response.url().includes('/api/ai/branding-kit/history/')) {
        responses.push({
          status: response.status(),
          url: response.url()
        })
      }
    })

    await page.goto(`${BASE_URL}/dashboard`)
    await page.waitForLoadState('networkidle')

    // Should have attempted to fetch branding kits
    expect(responses.length).toBeGreaterThan(0)
  })
})



