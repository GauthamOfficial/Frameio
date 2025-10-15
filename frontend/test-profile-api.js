#!/usr/bin/env node

// Use built-in fetch (Node.js 18+)

console.log('🧪 Testing Profile Saving API Endpoints...\n');

const API_BASE_URL = 'http://localhost:8000';
const AUTH_TOKEN = 'test_clerk_token';

async function testAPIEndpoint() {
  try {
    console.log('🔍 Testing GET /api/company-profiles/...');
    const getResponse = await fetch(`${API_BASE_URL}/api/company-profiles/`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${AUTH_TOKEN}`,
        'Content-Type': 'application/json'
      }
    });
    
    console.log(`   Status: ${getResponse.status}`);
    if (getResponse.ok) {
      const data = await getResponse.json();
      console.log(`   ✅ Success: Found profile for ${data.user_email}`);
      console.log(`   Company: ${data.company_name}`);
      console.log(`   Email: ${data.email}`);
    } else {
      const error = await getResponse.text();
      console.log(`   ❌ Error: ${error}`);
    }
    
    console.log('\n🔍 Testing POST /api/company-profiles/...');
    const postData = {
      company_name: 'Playwright Test Company',
      whatsapp_number: '+1234567890',
      email: 'playwright@test.com',
      facebook_link: 'https://facebook.com/playwright',
      website: 'https://playwright.com',
      address: '123 Playwright Street',
      description: 'Test company created by Playwright'
    };
    
    const postResponse = await fetch(`${API_BASE_URL}/api/company-profiles/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${AUTH_TOKEN}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(postData)
    });
    
    console.log(`   Status: ${postResponse.status}`);
    if (postResponse.ok) {
      const data = await postResponse.json();
      console.log(`   ✅ Success: Profile updated`);
      console.log(`   Company: ${data.company_name}`);
      console.log(`   Email: ${data.email}`);
    } else {
      const error = await postResponse.text();
      console.log(`   ❌ Error: ${error}`);
    }
    
    console.log('\n🔍 Testing GET /api/company-profiles/status/...');
    const statusResponse = await fetch(`${API_BASE_URL}/api/company-profiles/status/`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${AUTH_TOKEN}`,
        'Content-Type': 'application/json'
      }
    });
    
    console.log(`   Status: ${statusResponse.status}`);
    if (statusResponse.ok) {
      const data = await statusResponse.json();
      console.log(`   ✅ Success: Profile status retrieved`);
      console.log(`   Has Profile: ${data.has_profile}`);
      console.log(`   Has Logo: ${data.has_logo}`);
      console.log(`   Has Contact Info: ${data.has_contact_info}`);
      console.log(`   Is Complete: ${data.is_complete}`);
      console.log(`   Completion: ${data.completion_percentage}%`);
    } else {
      const error = await statusResponse.text();
      console.log(`   ❌ Error: ${error}`);
    }
    
    console.log('\n🔍 Testing CORS preflight...');
    const corsResponse = await fetch(`${API_BASE_URL}/api/company-profiles/`, {
      method: 'OPTIONS',
      headers: {
        'Origin': 'http://localhost:3000',
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'authorization,content-type'
      }
    });
    
    console.log(`   Status: ${corsResponse.status}`);
    if (corsResponse.ok) {
      const allowOrigin = corsResponse.headers.get('access-control-allow-origin');
      const allowMethods = corsResponse.headers.get('access-control-allow-methods');
      console.log(`   ✅ CORS configured correctly`);
      console.log(`   Allow Origin: ${allowOrigin}`);
      console.log(`   Allow Methods: ${allowMethods}`);
    } else {
      console.log(`   ❌ CORS error`);
    }
    
    console.log('\n✅ All API tests completed!');
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
    process.exit(1);
  }
}

// Check if servers are running
async function checkServers() {
  console.log('🔍 Checking server status...\n');
  
  try {
    const frontendResponse = await fetch('http://localhost:3000');
    console.log('✅ Frontend server is running (http://localhost:3000)');
  } catch (error) {
    console.log('❌ Frontend server is not running. Please start it with: npm run dev');
    process.exit(1);
  }
  
  try {
    const backendResponse = await fetch('http://localhost:8000');
    console.log('✅ Backend server is running (http://localhost:8000)');
  } catch (error) {
    console.log('❌ Backend server is not running. Please start it with: python manage.py runserver 8000');
    process.exit(1);
  }
  
  console.log('');
}

async function main() {
  await checkServers();
  await testAPIEndpoint();
}

main().catch(console.error);
