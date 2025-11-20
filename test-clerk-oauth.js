/**
 * Test script to verify Clerk OAuth configuration
 * Run this to check if your Clerk environment variables are properly set
 */

const fs = require('fs');
const path = require('path');

console.log('🔍 Checking Clerk OAuth Configuration...\n');

// Check root .env file
const rootEnvPath = path.join(__dirname, '.env');
const frontendEnvPath = path.join(__dirname, 'frontend', '.env.local');

let hasErrors = false;

console.log('📁 Checking root .env file...');
if (fs.existsSync(rootEnvPath)) {
  const rootEnv = fs.readFileSync(rootEnvPath, 'utf8');
  
  // Check for required Clerk variables
  const requiredVars = [
    'CLERK_PUBLISHABLE_KEY',
    'CLERK_SECRET_KEY',
    'NEXT_PUBLIC_CLERK_FRONTEND_API'
  ];
  
  requiredVars.forEach(varName => {
    const regex = new RegExp(`${varName}=(.+)`);
    const match = rootEnv.match(regex);
    
    if (!match) {
      console.log(`   ❌ Missing: ${varName}`);
      hasErrors = true;
    } else {
      const value = match[1].trim();
      if (value === '' || value.includes('your_') || value.includes('_here')) {
        console.log(`   ⚠️  Not configured: ${varName}`);
        hasErrors = true;
      } else {
        console.log(`   ✅ Found: ${varName}`);
      }
    }
  });
} else {
  console.log('   ❌ .env file not found in root directory');
  hasErrors = true;
}

console.log('\n📁 Checking frontend/.env.local file...');
if (fs.existsSync(frontendEnvPath)) {
  const frontendEnv = fs.readFileSync(frontendEnvPath, 'utf8');
  
  const requiredVars = [
    'NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY',
    'CLERK_SECRET_KEY',
    'NEXT_PUBLIC_CLERK_FRONTEND_API'
  ];
  
  requiredVars.forEach(varName => {
    const regex = new RegExp(`${varName}=(.+)`);
    const match = frontendEnv.match(regex);
    
    if (!match) {
      console.log(`   ❌ Missing: ${varName}`);
      hasErrors = true;
    } else {
      const value = match[1].trim();
      if (value === '' || value.includes('your_') || value.includes('_here')) {
        console.log(`   ⚠️  Not configured: ${varName}`);
        hasErrors = true;
      } else {
        console.log(`   ✅ Found: ${varName}`);
        
        // Validate key format
        if (varName === 'NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY') {
          if (!value.startsWith('pk_test_') && !value.startsWith('pk_live_')) {
            console.log(`      ⚠️  Warning: Key should start with pk_test_ or pk_live_`);
          }
        }
        if (varName === 'CLERK_SECRET_KEY') {
          if (!value.startsWith('sk_test_') && !value.startsWith('sk_live_')) {
            console.log(`      ⚠️  Warning: Key should start with sk_test_ or sk_live_`);
          }
        }
        if (varName === 'NEXT_PUBLIC_CLERK_FRONTEND_API') {
          if (!value.includes('clerk.accounts.dev') && !value.includes('clerk.com')) {
            console.log(`      ⚠️  Warning: Should be a clerk.accounts.dev URL`);
          }
        }
      }
    }
  });
} else {
  console.log('   ⚠️  frontend/.env.local file not found');
  console.log('   ℹ️  Create this file by copying frontend/env.local.template');
  hasErrors = true;
}

console.log('\n' + '='.repeat(60));
if (hasErrors) {
  console.log('❌ Configuration Issues Found!\n');
  console.log('Next steps:');
  console.log('1. Create a Clerk account at https://clerk.com');
  console.log('2. Create a new application in Clerk dashboard');
  console.log('3. Get your API keys from the dashboard');
  console.log('4. Enable Google OAuth in Social Connections');
  console.log('5. Update your .env and frontend/.env.local files');
  console.log('6. See CLERK_GOOGLE_OAUTH_SETUP.md for detailed instructions');
  process.exit(1);
} else {
  console.log('✅ All Clerk environment variables are configured!\n');
  console.log('Next steps to enable Google OAuth:');
  console.log('1. Go to your Clerk dashboard');
  console.log('2. Navigate to User & Authentication → Social Connections');
  console.log('3. Enable Google OAuth');
  console.log('4. For development: Use Clerk\'s development keys');
  console.log('5. For production: Configure custom Google OAuth credentials');
  console.log('\nSee CLERK_GOOGLE_OAUTH_SETUP.md for detailed instructions');
  process.exit(0);
}




