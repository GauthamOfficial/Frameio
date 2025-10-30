#!/usr/bin/env node

/**
 * Get Cloudflare Tunnel URL
 * This script helps get the tunnel URL for Facebook sharing
 */

const { spawn } = require('child_process');
const fs = require('fs');

async function getTunnelUrl() {
  return new Promise((resolve, reject) => {
    console.log('🔍 Looking for Cloudflare Tunnel URL...');
    
    // Start a new tunnel process to get the URL
    const cloudflared = spawn('./cloudflared.exe', ['tunnel', '--url', 'http://localhost:3000'], {
      stdio: ['pipe', 'pipe', 'pipe']
    });
    
    let output = '';
    
    cloudflared.stdout.on('data', (data) => {
      output += data.toString();
      
      // Look for the tunnel URL in the output
      const urlMatch = output.match(/https:\/\/[a-zA-Z0-9-]+\.trycloudflare\.com/);
      if (urlMatch) {
        const tunnelUrl = urlMatch[0];
        console.log('✅ Found tunnel URL:', tunnelUrl);
        
        // Kill the process
        cloudflared.kill();
        
        resolve(tunnelUrl);
      }
    });
    
    cloudflared.stderr.on('data', (data) => {
      output += data.toString();
      
      // Look for the tunnel URL in stderr too
      const urlMatch = output.match(/https:\/\/[a-zA-Z0-9-]+\.trycloudflare\.com/);
      if (urlMatch) {
        const tunnelUrl = urlMatch[0];
        console.log('✅ Found tunnel URL:', tunnelUrl);
        
        // Kill the process
        cloudflared.kill();
        
        resolve(tunnelUrl);
      }
    });
    
    cloudflared.on('close', (code) => {
      if (code !== 0 && !output.includes('trycloudflare.com')) {
        reject(new Error('Failed to get tunnel URL'));
      }
    });
    
    // Timeout after 10 seconds
    setTimeout(() => {
      cloudflared.kill();
      reject(new Error('Timeout waiting for tunnel URL'));
    }, 10000);
  });
}

async function main() {
  try {
    const tunnelUrl = await getTunnelUrl();
    console.log('\n🎉 Tunnel URL:', tunnelUrl);
    console.log('\n📱 Test your Facebook sharing with this URL!');
    console.log('🌐 Open in browser:', tunnelUrl);
    
    // Save the URL to a file for the app to read
    fs.writeFileSync('tunnel-url.txt', tunnelUrl);
    console.log('💾 URL saved to tunnel-url.txt');
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    console.log('\n💡 Make sure Cloudflare Tunnel is running:');
    console.log('   .\\cloudflared.exe tunnel --url http://localhost:3000');
  }
}

main();




