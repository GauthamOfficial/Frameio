#!/usr/bin/env node

/**
 * Start ngrok for Facebook sharing
 * This script helps users start ngrok easily for Facebook sharing to work
 */

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

async function checkNgrokInstalled() {
  return new Promise((resolve) => {
    const ngrok = spawn('ngrok', ['version'], { stdio: 'pipe' });
    
    ngrok.on('close', (code) => {
      resolve(code === 0);
    });
    
    ngrok.on('error', () => {
      resolve(false);
    });
  });
}

async function startNgrok() {
  console.log('🚀 Starting ngrok for Facebook sharing...');
  console.log('This will create a public URL that Facebook can access.');
  console.log('Press Ctrl+C to stop ngrok when done.\n');
  
  const ngrok = spawn('ngrok', ['http', '3000'], { 
    stdio: 'inherit',
    shell: true 
  });
  
  ngrok.on('error', (error) => {
    console.error('❌ Failed to start ngrok:', error.message);
    console.log('\n💡 To install ngrok:');
    console.log('1. Download from: https://ngrok.com/download');
    console.log('2. Extract ngrok.exe to your desktop');
    console.log('3. Run: ngrok.exe http 3000');
  });
  
  // Handle graceful shutdown
  process.on('SIGINT', () => {
    console.log('\n🛑 Stopping ngrok...');
    ngrok.kill();
    process.exit(0);
  });
}

async function main() {
  console.log('🔍 Checking ngrok installation...');
  
  const isInstalled = await checkNgrokInstalled();
  
  if (!isInstalled) {
    console.log('❌ Ngrok is not installed or not in PATH');
    console.log('\n📥 To install ngrok:');
    console.log('1. Download from: https://ngrok.com/download');
    console.log('2. Extract ngrok.exe to your desktop');
    console.log('3. Add to PATH or run from desktop');
    console.log('\n🔄 Or run the PowerShell script: install-ngrok.ps1');
    return;
  }
  
  console.log('✅ Ngrok is installed');
  await startNgrok();
}

main().catch(console.error);











