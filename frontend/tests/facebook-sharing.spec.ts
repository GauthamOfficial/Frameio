import { test, expect } from '@playwright/test'

/**
 * Facebook Sharing Tests
 * Verifies Facebook share functionality works via tunnel
 */

const BASE_URL = process.env.TUNNEL_URL || 'http://localhost:3000'

test.describe('Facebook Sharing', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to social media page
    await page.goto(`${BASE_URL}/dashboard/social-media`)
    await page.waitForLoadState('networkidle')
  })

  test('should check for public URL when sharing to Facebook', async ({ page }) => {
    // If there are no posters, skip this test
    const noPostersMessage = page.locator('text=No posters generated yet')
    if (await noPostersMessage.isVisible()) {
      test.skip()
      return
    }

    // Find a share button (assuming posters are displayed)
    const shareButtons = page.locator('[aria-label*="Share"], button:has-text("Share")')
    const count = await shareButtons.count()
    
    if (count === 0) {
      test.skip()
      return
    }

    // Listen for console warnings about localhost
    const consoleMessages: string[] = []
    page.on('console', msg => {
      consoleMessages.push(msg.text())
    })

    // Click first share button
    await shareButtons.first().click()
    
    // If using localhost, should show warning
    if (BASE_URL.includes('localhost')) {
      const warningMessages = consoleMessages.filter(msg => 
        msg.includes('localhost') || msg.includes('public URL')
      )
      expect(warningMessages.length).toBeGreaterThan(0)
    }
  })

  test('should open Facebook Share Dialog with tunnel URL', async ({ page, context }) => {
    // Skip if localhost
    if (BASE_URL.includes('localhost')) {
      test.skip()
      return
    }

    // If there are no posters, skip
    const noPostersMessage = page.locator('text=No posters generated yet')
    if (await noPostersMessage.isVisible()) {
      test.skip()
      return
    }

    // Listen for new pages (popup)
    const pagePromise = context.waitForEvent('page')

    // Find Facebook share button
    const facebookButton = page.locator('button:has-text("Facebook"), [aria-label*="Facebook"]').first()
    if (!await facebookButton.isVisible()) {
      test.skip()
      return
    }

    // Click share button
    await facebookButton.click()

    // Wait for popup
    const popup = await pagePromise
    await popup.waitForLoadState()

    // Should open Facebook sharer
    expect(popup.url()).toContain('facebook.com/sharer')
    
    // Should include tunnel URL in the share URL
    expect(popup.url()).toContain('trycloudflare.com')
  })
})

test.describe('Poster Page OG Tags', () => {
  test('should render Open Graph meta tags on poster page', async ({ page }) => {
    // This test requires a valid poster ID
    // You'll need to replace 'test-poster-id' with an actual poster ID
    const testPosterId = process.env.TEST_POSTER_ID
    
    if (!testPosterId) {
      test.skip()
      return
    }

    await page.goto(`${BASE_URL}/poster/${testPosterId}`)
    
    // Check for OG meta tags
    const ogTitle = await page.locator('meta[property="og:title"]').getAttribute('content')
    const ogImage = await page.locator('meta[property="og:image"]').getAttribute('content')
    const ogUrl = await page.locator('meta[property="og:url"]').getAttribute('content')
    
    expect(ogTitle).toBeTruthy()
    expect(ogImage).toBeTruthy()
    expect(ogUrl).toBeTruthy()
    
    // OG image should be absolute URL
    expect(ogImage).toMatch(/^https?:\/\//)
    
    // OG URL should use tunnel URL if available
    if (!BASE_URL.includes('localhost')) {
      expect(ogUrl).toContain('trycloudflare.com')
    }
  })

  test('should make poster shareable via Facebook Sharing Debugger', async ({ page }) => {
    const testPosterId = process.env.TEST_POSTER_ID
    
    if (!testPosterId || BASE_URL.includes('localhost')) {
      test.skip()
      return
    }

    const posterUrl = `${BASE_URL}/poster/${testPosterId}`
    
    // Navigate to Facebook Sharing Debugger
    await page.goto(`https://developers.facebook.com/tools/debug/`)
    
    // Find input field and enter poster URL
    const input = page.locator('input[name="q"], input[placeholder*="URL"]')
    await input.fill(posterUrl)
    
    // Click debug button
    const debugButton = page.locator('button:has-text("Debug"), button:has-text("Fetch")')
    await debugButton.click()
    
    // Wait for results
    await page.waitForTimeout(3000)
    
    // Should not show errors
    const errorText = page.locator('text=Error Parsing URL')
    await expect(errorText).not.toBeVisible()
  })
})




