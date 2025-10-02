import { chromium, FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  console.log('🚀 Starting AI Services Test Suite Setup...');
  
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  try {
    // 1. Wait for backend to be ready
    console.log('⏳ Waiting for Django backend...');
    let backendReady = false;
    let attempts = 0;
    const maxAttempts = 30;
    
    while (!backendReady && attempts < maxAttempts) {
      try {
        const response = await page.goto('http://localhost:8000/api/', { 
          waitUntil: 'networkidle',
          timeout: 5000 
        });
        if (response && response.status() === 200) {
          backendReady = true;
          console.log('✅ Django backend is ready');
        }
      } catch (error) {
        attempts++;
        console.log(`⏳ Backend not ready, attempt ${attempts}/${maxAttempts}`);
        await page.waitForTimeout(2000);
      }
    }
    
    if (!backendReady) {
      throw new Error('Django backend failed to start within timeout');
    }
    
    // 2. Wait for frontend to be ready
    console.log('⏳ Waiting for Next.js frontend...');
    let frontendReady = false;
    attempts = 0;
    
    while (!frontendReady && attempts < maxAttempts) {
      try {
        const response = await page.goto('http://localhost:3000', { 
          waitUntil: 'networkidle',
          timeout: 5000 
        });
        if (response && response.status() === 200) {
          frontendReady = true;
          console.log('✅ Next.js frontend is ready');
        }
      } catch (error) {
        attempts++;
        console.log(`⏳ Frontend not ready, attempt ${attempts}/${maxAttempts}`);
        await page.waitForTimeout(2000);
      }
    }
    
    if (!frontendReady) {
      throw new Error('Next.js frontend failed to start within timeout');
    }
    
    // 3. Setup test data in backend
    console.log('🔧 Setting up test data...');
    
    // Create test AI provider
    try {
      await page.evaluate(async () => {
        const response = await fetch('http://localhost:8000/api/ai/providers/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Organization': 'ai-test-org'
          },
          body: JSON.stringify({
            name: 'nanobanana',
            is_active: true,
            rate_limit_per_minute: 60,
            rate_limit_per_hour: 1000
          })
        });
        
        if (!response.ok && response.status !== 409) { // 409 = already exists
          throw new Error(`Failed to create test provider: ${response.status}`);
        }
      });
      console.log('✅ Test AI provider created');
    } catch (error) {
      console.log('⚠️ Test provider setup failed (may already exist):', error);
    }
    
    // 4. Verify AI services endpoints
    console.log('🔍 Verifying AI services endpoints...');
    
    const endpoints = [
      '/api/ai/providers/',
      '/api/ai/generation-requests/',
      '/api/ai/templates/',
      '/api/ai/quotas/',
      '/api/ai/analytics/dashboard/'
    ];
    
    for (const endpoint of endpoints) {
      try {
        const response = await page.goto(`http://localhost:8000${endpoint}`, {
          waitUntil: 'networkidle',
          timeout: 5000
        });
        
        if (response && (response.status() === 200 || response.status() === 400)) {
          console.log(`✅ Endpoint ${endpoint} is accessible`);
        } else {
          console.log(`⚠️ Endpoint ${endpoint} returned status: ${response?.status()}`);
        }
      } catch (error) {
        console.log(`❌ Endpoint ${endpoint} failed:`, error);
      }
    }
    
    // 5. Create test directories
    console.log('📁 Creating test output directories...');
    const fs = require('fs');
    const path = require('path');
    
    const dirs = [
      'test-results/ai-services',
      'playwright-report/ai-services',
      'test-results/screenshots',
      'test-results/videos'
    ];
    
    for (const dir of dirs) {
      try {
        fs.mkdirSync(dir, { recursive: true });
        console.log(`✅ Created directory: ${dir}`);
      } catch (error) {
        console.log(`⚠️ Directory creation failed for ${dir}:`, error);
      }
    }
    
    console.log('🎉 AI Services Test Suite Setup Complete!');
    
  } catch (error) {
    console.error('❌ Global setup failed:', error);
    throw error;
  } finally {
    await browser.close();
  }
}

export default globalSetup;
