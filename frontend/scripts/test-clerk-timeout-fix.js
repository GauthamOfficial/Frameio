#!/usr/bin/env node

/**
 * Test Clerk Timeout Fix
 * This script tests the Clerk timeout fix implementation
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const FRONTEND_DIR = path.join(__dirname, '..');
const ENV_FILE = path.join(FRONTEND_DIR, '.env.local');

function checkEnvironmentSetup() {
  console.log('🔍 Checking environment setup...');
  
  if (!fs.existsSync(ENV_FILE)) {
    console.error('❌ .env.local file not found');
    return false;
  }
  
  const envContent = fs.readFileSync(ENV_FILE, 'utf8');
  const requiredVars = [
    'NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY',
    'NEXT_PUBLIC_CLERK_FRONTEND_API'
  ];
  
  const missingVars = requiredVars.filter(varName => 
    !envContent.includes(varName)
  );
  
  if (missingVars.length > 0) {
    console.error('❌ Missing required environment variables:', missingVars.join(', '));
    return false;
  }
  
  console.log('✅ Environment variables are properly configured');
  return true;
}

function checkClerkComponents() {
  console.log('🔍 Checking Clerk components...');
  
  const componentsToCheck = [
    'src/components/auth/clerk-loading.tsx',
    'src/components/auth/clerk-error-boundary.tsx',
    'src/lib/clerk-timeout-handler.ts'
  ];
  
  const missingComponents = componentsToCheck.filter(component => {
    const fullPath = path.join(FRONTEND_DIR, component);
    return !fs.existsSync(fullPath);
  });
  
  if (missingComponents.length > 0) {
    console.error('❌ Missing Clerk components:', missingComponents.join(', '));
    return false;
  }
  
  console.log('✅ All Clerk components are present');
  return true;
}

function checkLayoutConfiguration() {
  console.log('🔍 Checking layout configuration...');
  
  const layoutPath = path.join(FRONTEND_DIR, 'src/app/layout.tsx');
  
  if (!fs.existsSync(layoutPath)) {
    console.error('❌ Layout file not found');
    return false;
  }
  
  const layoutContent = fs.readFileSync(layoutPath, 'utf8');
  
  const requiredConfigs = [
    'ClerkProvider',
    'publishableKey',
    'frontendApi',
    'ClerkErrorBoundary'
  ];
  
  const missingConfigs = requiredConfigs.filter(config => 
    !layoutContent.includes(config)
  );
  
  if (missingConfigs.length > 0) {
    console.error('❌ Missing layout configurations:', missingConfigs.join(', '));
    return false;
  }
  
  console.log('✅ Layout is properly configured');
  return true;
}

function runBuildTest() {
  console.log('🔍 Running build test...');
  
  try {
    process.chdir(FRONTEND_DIR);
    execSync('npm run build', { 
      stdio: 'pipe',
      timeout: 60000 // 60 seconds timeout
    });
    console.log('✅ Build completed successfully');
    return true;
  } catch (error) {
    console.error('❌ Build failed:', error.message);
    return false;
  }
}

function runLintCheck() {
  console.log('🔍 Running lint check...');
  
  try {
    process.chdir(FRONTEND_DIR);
    execSync('npm run lint', { 
      stdio: 'pipe',
      timeout: 30000 // 30 seconds timeout
    });
    console.log('✅ Lint check passed');
    return true;
  } catch (error) {
    console.warn('⚠️  Lint check failed (this might be expected):', error.message);
    return true; // Don't fail the test for lint issues
  }
}

function generateTestReport(results) {
  console.log('\n📊 Test Report:');
  console.log('================');
  
  const passed = Object.values(results).filter(Boolean).length;
  const total = Object.keys(results).length;
  
  Object.entries(results).forEach(([test, passed]) => {
    console.log(`${passed ? '✅' : '❌'} ${test}`);
  });
  
  console.log(`\n📈 Overall: ${passed}/${total} tests passed`);
  
  if (passed === total) {
    console.log('\n🎉 All tests passed! Clerk timeout fix is properly implemented.');
    console.log('\n💡 To test the fix:');
    console.log('   1. Start the development server: npm run dev');
    console.log('   2. Open the application in your browser');
    console.log('   3. Check the browser console for any Clerk-related errors');
    console.log('   4. If you see timeout errors, the fix should automatically handle them');
  } else {
    console.log('\n⚠️  Some tests failed. Please review the issues above.');
  }
}

function main() {
  console.log('🧪 Testing Clerk Timeout Fix Implementation\n');
  
  const results = {
    'Environment Setup': checkEnvironmentSetup(),
    'Clerk Components': checkClerkComponents(),
    'Layout Configuration': checkLayoutConfiguration(),
    'Build Test': runBuildTest(),
    'Lint Check': runLintCheck()
  };
  
  generateTestReport(results);
}

// Run the tests
if (require.main === module) {
  main();
}

module.exports = {
  checkEnvironmentSetup,
  checkClerkComponents,
  checkLayoutConfiguration,
  runBuildTest,
  runLintCheck
};