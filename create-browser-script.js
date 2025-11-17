#!/usr/bin/env node

/**
 * Set Cloudflare Tunnel URL in browser localStorage
 * This helps the app detect the tunnel URL immediately
 */

const fs = require('fs');

function getTunnelUrlFromFile() {
  try {
    const tunnelUrlPath = 'tunnel-url.txt';
    if (fs.existsSync(tunnelUrlPath)) {
      const tunnelUrl = fs.readFileSync(tunnelUrlPath, 'utf8').trim();
      return tunnelUrl;
    }
  } catch (error) {
    console.error('Error reading tunnel URL:', error);
  }
  return null;
}

function createBrowserScript() {
  const tunnelUrl = getTunnelUrlFromFile();
  
  if (tunnelUrl) {
    const script = `
// Set Cloudflare Tunnel URL in localStorage
localStorage.setItem('cloudflare-tunnel-url', '${tunnelUrl}');
console.log('✅ Cloudflare Tunnel URL set:', '${tunnelUrl}');
`;
    
    fs.writeFileSync('set-tunnel-url.js', script);
    console.log('✅ Browser script created: set-tunnel-url.js');
    console.log('🌐 Tunnel URL:', tunnelUrl);
    console.log('\n📋 To use this URL in your app:');
    console.log('1. Open your browser console');
    console.log('2. Copy and paste the contents of set-tunnel-url.js');
    console.log('3. Refresh your app and try Facebook sharing');
  } else {
    console.log('❌ No tunnel URL found. Make sure Cloudflare Tunnel is running.');
  }
}

createBrowserScript();







