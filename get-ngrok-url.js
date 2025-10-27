#!/usr/bin/env node

// Script to get ngrok URL and update sharing code
const https = require('https');

async function getNgrokUrl() {
  return new Promise((resolve, reject) => {
    https.get('http://localhost:4040/api/tunnels', (res) => {
      let data = '';
      res.on('data', (chunk) => {
        data += chunk;
      });
      res.on('end', () => {
        try {
          const response = JSON.parse(data);
          const tunnels = response.tunnels || [];
          const httpsTunnel = tunnels.find(t => t.proto === 'https');
          if (httpsTunnel) {
            resolve(httpsTunnel.public_url);
          } else {
            reject(new Error('No HTTPS tunnel found'));
          }
        } catch (error) {
          reject(error);
        }
      });
    }).on('error', reject);
  });
}

async function main() {
  try {
    console.log('🔍 Checking ngrok status...');
    const ngrokUrl = await getNgrokUrl();
    console.log('✅ Ngrok URL found:', ngrokUrl);
    
    console.log('\n📝 Update your sharing code with this URL:');
    console.log(`const ngrokUrl = '${ngrokUrl}';`);
    
    console.log('\n🧪 Test your poster page:');
    console.log(`${ngrokUrl}/poster/test123`);
    
    console.log('\n📊 Test with Facebook Sharing Debugger:');
    console.log('https://developers.facebook.com/tools/debug/');
    console.log(`Enter this URL: ${ngrokUrl}/poster/test123`);
    
  } catch (error) {
    console.log('❌ Error:', error.message);
    console.log('\n💡 Make sure ngrok is running:');
    console.log('ngrok http 3000');
  }
}

main();

