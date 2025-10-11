import { chromium, FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  console.log('🚀 Starting AI Services Global Setup...');
  
  // Start browser for setup tasks
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  try {
    // Test backend connectivity with retry logic
    console.log('🔍 Testing backend connectivity...');
    let backendResponse;
    let retries = 3;
    
    while (retries > 0) {
      try {
        backendResponse = await page.request.get('http://localhost:8000/api/ai/ai-poster/status/');
        if (backendResponse.status() === 200) {
          break;
        }
      } catch (error) {
        console.log(`⏳ Backend not ready, retrying... (${retries} attempts left)`);
        retries--;
        if (retries > 0) {
          await new Promise(resolve => setTimeout(resolve, 2000)); // Wait 2 seconds
        }
      }
    }
    
    if (backendResponse && backendResponse.status() === 200) {
      const data = await backendResponse.json();
      console.log(`✅ Backend API is available: ${data.service_available ? 'Service Ready' : 'Service Not Ready'}`);
    } else {
      console.log(`❌ Backend API not responding: ${backendResponse?.status() || 'Connection failed'}`);
    }
    
    // Test frontend connectivity
    console.log('🔍 Testing frontend connectivity...');
    const frontendResponse = await page.goto('http://localhost:3000');
    
    if (frontendResponse?.status() === 200) {
      console.log('✅ Frontend is available');
    } else {
      console.log(`❌ Frontend not responding: ${frontendResponse?.status()}`);
    }
    
    console.log('✅ Global setup completed');
    
  } catch (error) {
    console.error('❌ Global setup failed:', error);
    throw error;
  } finally {
    await browser.close();
  }
}

export default globalSetup;
