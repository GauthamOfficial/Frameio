import { FullConfig } from '@playwright/test';

async function globalTeardown(config: FullConfig) {
  console.log('🧹 Starting AI Services Global Teardown...');
  
  // Clean up any temporary files or resources
  console.log('✅ Global teardown completed');
}

export default globalTeardown;
