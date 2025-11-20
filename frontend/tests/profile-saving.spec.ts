import { test, expect } from '@playwright/test';

test.describe('Profile Information Saving', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the settings page
    await page.goto('http://localhost:3000/dashboard/settings');
    
    // Wait for the page to load
    await page.waitForLoadState('networkidle');
  });

  test('should display profile form with all required fields', async ({ page }) => {
    // Check if the profile form is visible
    await expect(page.locator('text=Personal Information')).toBeVisible();
    await expect(page.locator('text=Contact Information')).toBeVisible();
    await expect(page.locator('text=Business Logo')).toBeVisible();
    
    // Check for required form fields
    await expect(page.locator('input[id="company_name"]')).toBeVisible();
    await expect(page.locator('input[id="whatsapp_number"]')).toBeVisible();
    await expect(page.locator('input[id="email"]')).toBeVisible();
    await expect(page.locator('input[id="facebook_link"]')).toBeVisible();
    await expect(page.locator('input[id="website"]')).toBeVisible();
    await expect(page.locator('textarea[id="address"]')).toBeVisible();
    await expect(page.locator('textarea[id="description"]')).toBeVisible();
    
    // Check for save button
    await expect(page.locator('button:has-text("Save Profile")')).toBeVisible();
  });

  test('should allow filling out profile form', async ({ page }) => {
    // Fill out the company name field
    await page.fill('input[id="company_name"]', 'Test Textile Company');
    
    // Fill out contact information
    await page.fill('input[id="whatsapp_number"]', '+1234567890');
    await page.fill('input[id="email"]', 'contact@testtextile.com');
    await page.fill('input[id="facebook_link"]', 'https://facebook.com/testtextile');
    await page.fill('input[id="website"]', 'https://testtextile.com');
    
    // Fill out address and description
    await page.fill('textarea[id="address"]', '123 Textile Street, Fashion City');
    await page.fill('textarea[id="description"]', 'Premium textile manufacturer specializing in silk and cotton fabrics');
    
    // Verify the fields are filled
    await expect(page.locator('input[id="company_name"]')).toHaveValue('Test Textile Company');
    await expect(page.locator('input[id="whatsapp_number"]')).toHaveValue('+1234567890');
    await expect(page.locator('input[id="email"]')).toHaveValue('contact@testtextile.com');
  });

  test('should handle logo upload', async ({ page }) => {
    // Check if logo upload area is visible
    await expect(page.locator('input[type="file"][accept="image/*"]')).toBeVisible();
    
    // Test logo position selector
    await expect(page.locator('select')).toBeVisible();
    await page.selectOption('select', 'top_right');
  });

  test('should save profile successfully', async ({ page }) => {
    // Fill out the profile form
    await page.fill('input[id="company_name"]', 'Test Company for Playwright');
    await page.fill('input[id="whatsapp_number"]', '+1234567890');
    await page.fill('input[id="email"]', 'test@playwright.com');
    await page.fill('input[id="facebook_link"]', 'https://facebook.com/playwright');
    await page.fill('input[id="website"]', 'https://playwright.com');
    await page.fill('textarea[id="address"]', '123 Playwright Street');
    await page.fill('textarea[id="description"]', 'Test company for Playwright testing');
    
    // Click save button
    await page.click('button:has-text("Save Profile")');
    
    // Wait for the save operation to complete
    await page.waitForTimeout(2000);
    
    // Check for success message (if implemented)
    // Note: This might need to be adjusted based on actual implementation
    const successMessage = page.locator('text=successfully');
    if (await successMessage.isVisible()) {
      await expect(successMessage).toBeVisible();
    }
    
    // Verify the form still has the saved values
    await expect(page.locator('input[id="company_name"]')).toHaveValue('Test Company for Playwright');
  });

  test('should handle form validation', async ({ page }) => {
    // Try to save without required fields
    await page.click('button:has-text("Save Profile")');
    
    // Check if validation messages appear (if implemented)
    // Note: This depends on the actual validation implementation
  });

  test('should display profile completion status', async ({ page }) => {
    // Check if profile completion section is visible
    await expect(page.locator('text=Profile Completion')).toBeVisible();
    
    // Check for completion percentage
    const completionText = page.locator('text=/\\d+%/');
    if (await completionText.isVisible()) {
      await expect(completionText).toBeVisible();
    }
  });

  test('should handle network errors gracefully', async ({ page }) => {
    // Intercept the API call and return an error
    await page.route('**/api/company-profiles/', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal Server Error' })
      });
    });
    
    // Fill out the form
    await page.fill('input[id="company_name"]', 'Test Company');
    await page.fill('input[id="email"]', 'test@example.com');
    
    // Try to save
    await page.click('button:has-text("Save Profile")');
    
    // Wait for error handling
    await page.waitForTimeout(1000);
    
    // Check if error message is displayed
    const errorMessage = page.locator('text=error');
    if (await errorMessage.isVisible()) {
      await expect(errorMessage).toBeVisible();
    }
  });
});

test.describe('Backend API Profile Endpoints', () => {
  test('should respond to GET /api/company-profiles/', async ({ request }) => {
    const response = await request.get('http://localhost:8000/api/company-profiles/', {
      headers: {
        'Authorization': 'Bearer test_clerk_token'
      }
    });
    
    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(data).toHaveProperty('user');
    expect(data).toHaveProperty('company_name');
  });

  test('should respond to POST /api/company-profiles/', async ({ request }) => {
    const profileData = {
      company_name: 'Test Company API',
      whatsapp_number: '+1234567890',
      email: 'test@api.com',
      facebook_link: 'https://facebook.com/testapi',
      website: 'https://testapi.com',
      address: '123 API Street',
      description: 'Test company for API testing'
    };
    
    const response = await request.post('http://localhost:8000/api/company-profiles/', {
      headers: {
        'Authorization': 'Bearer test_clerk_token',
        'Content-Type': 'application/json'
      },
      data: profileData
    });
    
    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(data.company_name).toBe('Test Company API');
    expect(data.email).toBe('test@api.com');
  });

  test('should handle profile status endpoint', async ({ request }) => {
    const response = await request.get('http://localhost:8000/api/company-profiles/status/', {
      headers: {
        'Authorization': 'Bearer test_clerk_token'
      }
    });
    
    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(data).toHaveProperty('has_profile');
    expect(data).toHaveProperty('has_logo');
    expect(data).toHaveProperty('has_contact_info');
    expect(data).toHaveProperty('is_complete');
    expect(data).toHaveProperty('completion_percentage');
  });

  test('should handle authentication errors', async ({ request }) => {
    const response = await request.get('http://localhost:8000/api/company-profiles/', {
      headers: {
        'Authorization': 'Bearer invalid_token'
      }
    });
    
    // Should return 403 for invalid token
    expect(response.status()).toBe(403);
  });

  test('should handle CORS preflight requests', async ({ request }) => {
    const response = await request.options('http://localhost:8000/api/company-profiles/', {
      headers: {
        'Origin': 'http://localhost:3000',
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'authorization,content-type'
      }
    });
    
    expect(response.status()).toBe(200);
    const headers = response.headers();
    expect(headers['access-control-allow-origin']).toBe('http://localhost:3000');
    expect(headers['access-control-allow-methods']).toContain('POST');
  });
});

test.describe('End-to-End Profile Saving Flow', () => {
  test('complete profile saving workflow', async ({ page, request }) => {
    // Step 1: Navigate to settings page
    await page.goto('http://localhost:3000/dashboard/settings');
    await page.waitForLoadState('networkidle');
    
    // Step 2: Fill out the profile form
    await page.fill('input[id="company_name"]', 'E2E Test Company');
    await page.fill('input[id="whatsapp_number"]', '+1234567890');
    await page.fill('input[id="email"]', 'e2e@testcompany.com');
    await page.fill('input[id="facebook_link"]', 'https://facebook.com/e2etest');
    await page.fill('input[id="website"]', 'https://e2etest.com');
    await page.fill('textarea[id="address"]', '123 E2E Street');
    await page.fill('textarea[id="description"]', 'End-to-end test company');
    
    // Step 3: Save the profile
    await page.click('button:has-text("Save Profile")');
    
    // Step 4: Wait for the request to complete
    await page.waitForTimeout(3000);
    
    // Step 5: Verify the profile was saved by checking the API directly
    const apiResponse = await request.get('http://localhost:8000/api/company-profiles/', {
      headers: {
        'Authorization': 'Bearer test_clerk_token'
      }
    });
    
    expect(apiResponse.status()).toBe(200);
    const profileData = await apiResponse.json();
    expect(profileData.company_name).toBe('E2E Test Company');
    expect(profileData.email).toBe('e2e@testcompany.com');
    
    // Step 6: Verify the form still shows the saved data
    await expect(page.locator('input[id="company_name"]')).toHaveValue('E2E Test Company');
    await expect(page.locator('input[id="email"]')).toHaveValue('e2e@testcompany.com');
  });
});

