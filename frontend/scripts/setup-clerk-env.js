#!/usr/bin/env node

/**
 * Setup Clerk Environment Variables
 * This script helps set up the required Clerk environment variables
 */

const fs = require('fs');
const path = require('path');

const ENV_FILE = path.join(__dirname, '..', '.env.local');
const ENV_TEMPLATE = path.join(__dirname, '..', '..', 'env.template');

// Default Clerk configuration from the template
const DEFAULT_CLERK_CONFIG = {
  NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: 'pk_test_c291bmQtbXVsZS0yNC5jbGVyay5hY2NvdW50cy5kZXYk',
  NEXT_PUBLIC_CLERK_FRONTEND_API: 'https://sound-mule-24.clerk.accounts.dev'
};

function readEnvFile() {
  try {
    if (fs.existsSync(ENV_FILE)) {
      const content = fs.readFileSync(ENV_FILE, 'utf8');
      const envVars = {};
      
      content.split('\n').forEach(line => {
        const trimmed = line.trim();
        if (trimmed && !trimmed.startsWith('#')) {
          const [key, ...valueParts] = trimmed.split('=');
          if (key && valueParts.length > 0) {
            envVars[key.trim()] = valueParts.join('=').trim();
          }
        }
      });
      
      return envVars;
    }
  } catch (error) {
    console.warn('Error reading .env.local file:', error.message);
  }
  
  return {};
}

function writeEnvFile(envVars) {
  try {
    const content = Object.entries(envVars)
      .map(([key, value]) => `${key}=${value}`)
      .join('\n');
    
    fs.writeFileSync(ENV_FILE, content + '\n');
    console.log('✅ Environment variables updated successfully');
  } catch (error) {
    console.error('❌ Error writing .env.local file:', error.message);
    process.exit(1);
  }
}

function setupClerkEnvironment() {
  console.log('🔧 Setting up Clerk environment variables...');
  
  const existingEnv = readEnvFile();
  const updatedEnv = { ...existingEnv };
  
  let hasChanges = false;
  
  // Check and add missing Clerk environment variables
  Object.entries(DEFAULT_CLERK_CONFIG).forEach(([key, defaultValue]) => {
    if (!updatedEnv[key]) {
      console.log(`➕ Adding missing environment variable: ${key}`);
      updatedEnv[key] = defaultValue;
      hasChanges = true;
    } else {
      console.log(`✅ Environment variable already exists: ${key}`);
    }
  });
  
  // Ensure other required variables exist
  const requiredVars = {
    NEXT_PUBLIC_API_URL: 'http://localhost:8000/api',
    NEXT_PUBLIC_APP_URL: 'http://localhost:3000',
    NEXT_PUBLIC_SOCKET_URL: 'http://localhost:8000'
  };
  
  Object.entries(requiredVars).forEach(([key, defaultValue]) => {
    if (!updatedEnv[key]) {
      console.log(`➕ Adding missing environment variable: ${key}`);
      updatedEnv[key] = defaultValue;
      hasChanges = true;
    }
  });
  
  if (hasChanges) {
    writeEnvFile(updatedEnv);
    console.log('\n🎉 Clerk environment setup complete!');
    console.log('\n📋 Environment variables configured:');
    Object.keys(updatedEnv).forEach(key => {
      if (key.includes('CLERK') || key.includes('PUBLIC')) {
        console.log(`   ${key}=${updatedEnv[key]}`);
      }
    });
  } else {
    console.log('✅ All required environment variables are already configured');
  }
  
  console.log('\n💡 Next steps:');
  console.log('   1. Restart your development server: npm run dev');
  console.log('   2. If you still see timeout errors, try clearing your browser cache');
  console.log('   3. Check the browser console for any additional error messages');
}

// Run the setup
if (require.main === module) {
  setupClerkEnvironment();
}

module.exports = { setupClerkEnvironment, readEnvFile, writeEnvFile };