#!/usr/bin/env node

/**
 * Start Cloudflare Tunnel for Facebook sharing
 * Free alternative to ngrok that doesn't require authentication
 */

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

async function checkCloudflaredInstalled() {
  return new Promise((resolve) => {
    // Check if cloudflared.exe exists in current directory
    const fs = require('fs');
    const path = require('path');
    const cloudflaredPath = path.join(process.cwd(), 'cloudflared.exe');
    
    if (fs.existsSync(cloudflaredPath)) {
      resolve(true);
    } else {
      resolve(false);
    }
  });
}

async function downloadCloudflared() {
  console.log('📥 Downloading Cloudflare Tunnel...');
  console.log('This is a free alternative to ngrok that doesn\'t require authentication.');
  
  const downloadUrl = 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe';
  const outputPath = path.join(process.cwd(), 'cloudflared.exe');
  
  try {
    const https = require('https');
    const fs = require('fs');
    
    console.log('⏳ Downloading from:', downloadUrl);
    console.log('📍 Saving to:', outputPath);
    
    const file = fs.createWriteStream(outputPath);
    
    return new Promise((resolve, reject) => {
      https.get(downloadUrl, (response) => {
        if (response.statusCode !== 200) {
          reject(new Error(`Download failed with status: ${response.statusCode}`));
          return;
        }
        
        response.pipe(file);
        
        file.on('finish', () => {
          file.close();
          console.log('✅ Cloudflare Tunnel downloaded successfully!');
          console.log('📍 Location:', outputPath);
          resolve();
        });
        
        file.on('error', (err) => {
          fs.unlink(outputPath, () => {}); // Delete the file on error
          reject(err);
        });
      }).on('error', (err) => {
        reject(err);
      });
    });
  } catch (error) {
    console.error('❌ Download failed:', error.message);
    throw error;
  }
}

async function startCloudflared(cloudflaredPath) {
  console.log('🚀 Starting Cloudflare Tunnel...');
  console.log('This will create a public URL that Facebook can access.');
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

async function main() {
  console.log('🔍 Checking Cloudflare Tunnel installation...');
  
  const isInstalled = await checkCloudflaredInstalled();
  
  if (!isInstalled) {
    console.log('❌ Cloudflare Tunnel is not installed');
    console.log('\n📥 Downloading Cloudflare Tunnel (free alternative to ngrok)...');
    
    try {
      await downloadCloudflared();
      console.log('\n🚀 Starting Cloudflare Tunnel...');
      await startCloudflared(path.join(process.cwd(), 'cloudflared.exe'));
    } catch (error) {
      console.error('❌ Failed to download or start Cloudflare Tunnel:', error.message);
      console.log('\n💡 Manual download:');
      console.log('1. Go to: https://github.com/cloudflare/cloudflared/releases');
      console.log('2. Download cloudflared-windows-amd64.exe');
      console.log('3. Rename to cloudflared.exe');
      console.log('4. Run: cloudflared.exe tunnel --url http://localhost:3000');
    }
  } else {
    console.log('✅ Cloudflare Tunnel is installed');
    await startCloudflared(path.join(process.cwd(), 'cloudflared.exe'));
  }
}

main().catch(console.error);
