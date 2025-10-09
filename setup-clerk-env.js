#!/usr/bin/env node

/**
 * Clerk Environment Setup Script
 * This script helps you set up the correct Clerk environment variables
 * to fix the CSP (Content Security Policy) issue.
 */

const fs = require('fs');
const path = require('path');

console.log('🔧 Setting up Clerk environment variables...\n');

// Check if .env file exists in frontend directory
const frontendEnvPath = path.join(__dirname, 'frontend', '.env.local');
const rootEnvPath = path.join(__dirname, '.env');

// Environment variables template for frontend
const frontendEnvContent = `# Frameio Frontend Environment Variables
# This file contains environment variables for the Next.js frontend

# =============================================================================
# CLERK AUTHENTICATION
# =============================================================================
# Your actual Clerk keys from https://dashboard.clerk.com
# The domain should match the one in your CSP error: correct-lobster-87.clerk.accounts.dev
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_correct-lobster-87.clerk.accounts.dev
NEXT_PUBLIC_CLERK_FRONTEND_API=https://correct-lobster-87.clerk.accounts.dev

# =============================================================================
# API CONFIGURATION
# =============================================================================
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_APP_URL=http://localhost:3000

# =============================================================================
# SOCKET.IO CONFIGURATION
# =============================================================================
NEXT_PUBLIC_SOCKET_URL=http://localhost:8000
`;

// Environment variables template for root
const rootEnvContent = `# Frameio Root Environment Variables
# Copy from env.template and update with your actual values

# =============================================================================
# CLERK AUTHENTICATION
# =============================================================================
CLERK_PUBLISHABLE_KEY=pk_test_correct-lobster-87.clerk.accounts.dev
CLERK_SECRET_KEY=sk_test_your_secret_key_here
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_correct-lobster-87.clerk.accounts.dev
NEXT_PUBLIC_CLERK_FRONTEND_API=https://correct-lobster-87.clerk.accounts.dev
`;

try {
  // Create frontend .env.local file
  if (!fs.existsSync(frontendEnvPath)) {
    fs.writeFileSync(frontendEnvPath, frontendEnvContent);
    console.log('✅ Created frontend/.env.local');
  } else {
    console.log('⚠️  frontend/.env.local already exists');
  }

  // Create root .env file if it doesn't exist
  if (!fs.existsSync(rootEnvPath)) {
    fs.writeFileSync(rootEnvPath, rootEnvContent);
    console.log('✅ Created .env');
  } else {
    console.log('⚠️  .env already exists');
  }

  console.log('\n📋 Next steps:');
  console.log('1. Update the Clerk keys in both .env files with your actual keys from https://dashboard.clerk.com');
  console.log('2. Make sure the domain matches: correct-lobster-87.clerk.accounts.dev');
  console.log('3. Restart your development server');
  console.log('\n🔧 The CSP has been updated to allow the correct Clerk domain (correct-lobster-87.clerk.accounts.dev).');
  console.log('   This should fix the "Refused to load the script" error.');

} catch (error) {
  console.error('❌ Error setting up environment:', error.message);
  process.exit(1);
}
