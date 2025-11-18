#!/usr/bin/env node

/**
 * Simple Cloudflare Tunnel Starter
 * Downloads and runs Cloudflare Tunnel for Facebook sharing
 */

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const https = require('https');

async function downloadAndStart() {
  const cloudflaredPath = path.join(process.cwd(), 'cloudflared.exe');
  
  // Check if already downloaded
  if (fs.existsSync(cloudflaredPath)) {
    console.log('✅ Cloudflare Tunnel already downloaded');
    startTunnel(cloudflaredPath);
    return;
  }
  
  console.log('📥 Downloading Cloudflare Tunnel...');
  console.log('This is a free alternative to ngrok that doesn\'t require authentication.\n');
  
  const downloadUrl = 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe';
  
  try {
    const file = fs.createWriteStream(cloudflaredPath);
    
    await new Promise((resolve, reject) => {
      https.get(downloadUrl, (response) => {
        if (response.statusCode !== 200) {
          reject(new Error(`Download failed with status: ${response.statusCode}`));
          return;
        }
        
        response.pipe(file);
        
        file.on('finish', () => {
          file.close();
          console.log('✅ Download completed!');
          resolve();
        });
        
        file.on('error', (err) => {
          fs.unlink(cloudflaredPath, () => {});
          reject(err);
        });
      }).on('error', reject);
    });
    
    console.log('🚀 Starting Cloudflare Tunnel...');
    startTunnel(cloudflaredPath);
    
  } catch (error) {
    console.error('❌ Download failed:', error.message);
    console.log('\n💡 Manual download:');
    console.log('1. Go to: https://github.com/cloudflare/cloudflared/releases');
    console.log('2. Download cloudflared-windows-amd64.exe');
    console.log('3. Rename to cloudflared.exe');
    console.log('4. Run: cloudflared.exe tunnel --url http://localhost:3000');
  }
}

function startTunnel(cloudflaredPath) {
  console.log('🌐 Creating public tunnel for Facebook sharing...');
  console.log('Press Ctrl+C to stop the tunnel.\n');
  
  const cloudflared = spawn(cloudflaredPath, ['tunnel', '--url', 'http://localhost:3000'], { 
    stdio: 'inherit',
    shell: true 
  });
  
  cloudflared.on('error', (error) => {
    console.error('❌ Failed to start Cloudflare Tunnel:', error.message);
  });
  
  // Handle graceful shutdown
  process.on('SIGINT', () => {
    console.log('\n🛑 Stopping Cloudflare Tunnel...');
    cloudflared.kill();
    process.exit(0);
  });
}

// Start the process
downloadAndStart().catch(console.error);








