import { chromium, FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  console.log('🚀 Starting global setup for profile saving tests...');
  
  // Start browser for setup
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  try {
    // Check if frontend is accessible
    console.log('📱 Checking frontend accessibility...');
    await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });
    console.log('✅ Frontend is accessible');
    
    // Check if backend is accessible
    console.log('🔧 Checking backend accessibility...');
    const backendResponse = await page.request.get('http://localhost:8000/');
    if (backendResponse.ok()) {
      console.log('✅ Backend is accessible');
    } else {
      throw new Error('Backend is not accessible');
    }
    
    // Test API endpoints
    console.log('🔌 Testing API endpoints...');
    const apiResponse = await page.request.get('http://localhost:8000/api/company-profiles/', {
      headers: {
        'Authorization': 'Bearer test_jwt_token'
      }
    });
    
    if (apiResponse.ok()) {
      console.log('✅ API endpoints are working');
    } else {
      console.log('⚠️ API endpoints may have authentication issues');
    }
    
  } catch (error) {
    console.error('❌ Global setup failed:', error);
    throw error;
  } finally {
    await browser.close();
  }
  
  console.log('✅ Global setup completed successfully');
}

export default globalSetup;