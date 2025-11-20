import { FullConfig } from '@playwright/test';

async function globalTeardown(config: FullConfig) {
  console.log('🧹 Starting global teardown for profile saving tests...');
  
  try {
    // Clean up any test data if needed
    console.log('🧽 Cleaning up test data...');
    
    // Add any cleanup logic here
    // For example, delete test profiles created during tests
    
    console.log('✅ Global teardown completed successfully');
  } catch (error) {
    console.error('❌ Global teardown failed:', error);
    // Don't throw error in teardown to avoid masking test failures
  }
}

export default globalTeardown;