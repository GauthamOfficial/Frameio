#!/usr/bin/env node

const { execSync } = require('child_process');
const path = require('path');

console.log('🧪 Running Profile Saving Tests with Playwright...\n');

try {
  // Check if Playwright is installed
  console.log('📦 Checking Playwright installation...');
  try {
    execSync('npx playwright --version', { stdio: 'pipe' });
    console.log('✅ Playwright is installed');
  } catch (error) {
    console.log('❌ Playwright not found. Installing...');
    execSync('npm install @playwright/test', { stdio: 'inherit' });
    execSync('npx playwright install', { stdio: 'inherit' });
    console.log('✅ Playwright installed successfully');
  }

  // Run the profile saving tests
  console.log('\n🚀 Running profile saving tests...');
  console.log('📋 Test Configuration:');
  console.log('   - Frontend: http://localhost:3000');
  console.log('   - Backend: http://localhost:8000');
  console.log('   - Test File: profile-saving.spec.ts');
  console.log('   - Config: playwright.config.profile-saving.ts\n');

  const testCommand = 'npx playwright test --config=playwright.config.profile-saving.ts --reporter=html,json';
  
  console.log(`🔧 Executing: ${testCommand}\n`);
  
  execSync(testCommand, { 
    stdio: 'inherit',
    cwd: path.resolve(__dirname)
  });
  
  console.log('\n✅ Profile saving tests completed successfully!');
  console.log('📊 Check the test-results directory for detailed reports');
  
} catch (error) {
  console.error('\n❌ Test execution failed:', error.message);
  process.exit(1);
}

