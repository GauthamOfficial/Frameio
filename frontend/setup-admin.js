#!/usr/bin/env node

/**
 * Admin Dashboard Setup Script
 * 
 * This script helps set up the admin dashboard by:
 * 1. Creating .env.local with admin credentials
 * 2. Installing required dependencies (jose)
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('🚀 Setting up Admin Dashboard...\n');

// Step 1: Create .env.local
console.log('📝 Creating .env.local file...');
const envContent = `# Admin Authentication Credentials
ADMIN_USERNAME=tsg_admin
ADMIN_PASSWORD=tsgtharsiyanshahastragautham321

# JWT Secret for admin sessions (change this in production)
ADMIN_JWT_SECRET=your-super-secret-jwt-key-change-in-production-12345678

# Session expiry in hours
ADMIN_SESSION_EXPIRY=24
`;

const envPath = path.join(__dirname, '.env.local');

if (fs.existsSync(envPath)) {
  console.log('⚠️  .env.local already exists. Skipping...');
} else {
  fs.writeFileSync(envPath, envContent);
  console.log('✅ .env.local created successfully!');
}

// Step 2: Install dependencies
console.log('\n📦 Installing required dependencies...');
try {
  console.log('Installing jose for JWT handling...');
  execSync('npm install jose', { stdio: 'inherit' });
  console.log('✅ Dependencies installed successfully!');
} catch (error) {
  console.error('❌ Failed to install dependencies:', error.message);
  console.log('\nPlease run manually: npm install jose');
}

// Step 3: Display success message
console.log('\n✨ Admin Dashboard setup complete!\n');
console.log('📍 Access the admin dashboard at: http://localhost:3000/admin/login\n');
console.log('🔐 Login Credentials:');
console.log('   Username: tsg_admin');
console.log('   Password: tsgtharsiyanshahastragautham321\n');
console.log('⚠️  IMPORTANT: Change the ADMIN_JWT_SECRET in .env.local for production!\n');
console.log('📖 For more information, see: ADMIN_DASHBOARD_README.md\n');
console.log('🎉 Happy administrating!\n');

