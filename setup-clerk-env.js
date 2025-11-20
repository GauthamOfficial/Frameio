#!/usr/bin/env node

/**
 * Clerk Environment Setup Script
 * This script helps you configure Clerk authentication for the Frameio project
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

function question(prompt) {
  return new Promise((resolve) => {
    rl.question(prompt, resolve);
  });
}

async function setupClerkEnvironment() {
  console.log('🔧 Clerk Environment Setup for Frameio\n');
  
  console.log('This script will help you configure Clerk authentication.');
  console.log('You can get your Clerk keys from: https://dashboard.clerk.com\n');
  
  const publishableKey = await question('Enter your Clerk Publishable Key (pk_test_...): ');
  const secretKey = await question('Enter your Clerk Secret Key (sk_test_...): ');
  const frontendApi = await question('Enter your Clerk Frontend API URL (https://your-app.clerk.accounts.dev): ');
  
  // Create environment variables for frontend
  const frontendEnv = `# Clerk Configuration for Frontend
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=${publishableKey}
NEXT_PUBLIC_CLERK_FRONTEND_API=${frontendApi}
NEXT_PUBLIC_API_URL=http://localhost:8000
`;

  // Create environment variables for backend
  const backendEnv = `# Clerk Configuration for Backend
CLERK_PUBLISHABLE_KEY=${publishableKey}
CLERK_SECRET_KEY=${secretKey}
NEXT_PUBLIC_CLERK_FRONTEND_API=${frontendApi}
`;

  try {
    // Write frontend .env.local
    fs.writeFileSync(path.join(__dirname, 'frontend', '.env.local'), frontendEnv);
    console.log('✅ Frontend environment configured: frontend/.env.local');
    
    // Update backend .env if it exists
    const backendEnvPath = path.join(__dirname, 'backend', '.env');
    if (fs.existsSync(backendEnvPath)) {
      const existingEnv = fs.readFileSync(backendEnvPath, 'utf8');
      const updatedEnv = existingEnv + '\n' + backendEnv;
      fs.writeFileSync(backendEnvPath, updatedEnv);
      console.log('✅ Backend environment updated: backend/.env');
    } else {
      fs.writeFileSync(backendEnvPath, backendEnv);
      console.log('✅ Backend environment created: backend/.env');
    }
    
    console.log('\n🎉 Clerk environment setup complete!');
    console.log('\nNext steps:');
    console.log('1. Restart your development servers');
    console.log('2. Test the Settings page');
    console.log('3. If you still see errors, check the browser console for details');
    
  } catch (error) {
    console.error('❌ Error setting up environment:', error.message);
  }
  
  rl.close();
}

// Run the setup
setupClerkEnvironment().catch(console.error);