// Simple script to set Cloudflare Tunnel URL
// Copy and paste this into your browser console

const tunnelUrl = 'https://blah-literature-drives-hrs.trycloudflare.com';

// Set the URL in localStorage
localStorage.setItem('cloudflare-tunnel-url', tunnelUrl);

// Verify it was set
const savedUrl = localStorage.getItem('cloudflare-tunnel-url');
console.log('✅ Cloudflare Tunnel URL set:', savedUrl);

// Test the URL
fetch(tunnelUrl)
  .then(response => {
    if (response.ok) {
      console.log('✅ Tunnel URL is working!');
    } else {
      console.log('⚠️ Tunnel URL returned status:', response.status);
    }
  })
  .catch(error => {
    console.log('❌ Tunnel URL test failed:', error.message);
  });

console.log('🎉 Now refresh your app and try Facebook sharing!');





