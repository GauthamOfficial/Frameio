#!/usr/bin/env node

/**
 * API Endpoints Test Script
 * Tests all the API endpoints that the Settings page uses
 */

const API_BASE_URL = 'http://localhost:8000';
const AUTH_TOKEN = 'test_clerk_token';

async function testEndpoint(name, url, method = 'GET', data = null) {
  try {
    console.log(`\n🔍 Testing ${name}...`);
    console.log(`   URL: ${url}`);
    
    const options = {
      method,
      headers: {
        'Authorization': `Bearer ${AUTH_TOKEN}`,
        'Content-Type': 'application/json'
      }
    };
    
    if (data) {
      options.body = JSON.stringify(data);
    }
    
    const response = await fetch(url, options);
    console.log(`   Status: ${response.status}`);
    
    if (response.ok) {
      const result = await response.json();
      console.log(`   ✅ Success: ${name} is working`);
      return true;
    } else {
      const error = await response.text();
      console.log(`   ❌ Error: ${error}`);
      return false;
    }
  } catch (error) {
    console.log(`   ❌ Network Error: ${error.message}`);
    return false;
  }
}

async function runTests() {
  console.log('🧪 Testing API Endpoints for Settings Page\n');
  
  const tests = [
    {
      name: 'Health Check',
      url: `${API_BASE_URL}/health/`,
      method: 'GET'
    },
    {
      name: 'Company Profiles GET',
      url: `${API_BASE_URL}/api/company-profiles/`,
      method: 'GET'
    },
    {
      name: 'Company Profiles Status',
      url: `${API_BASE_URL}/api/company-profiles/status/`,
      method: 'GET'
    },
    {
      name: 'Company Profiles POST',
      url: `${API_BASE_URL}/api/company-profiles/`,
      method: 'POST',
      data: {
        company_name: 'Test Company API',
        email: 'test@api.com',
        whatsapp_number: '+1234567890'
      }
    }
  ];
  
  let passed = 0;
  let total = tests.length;
  
  for (const test of tests) {
    const success = await testEndpoint(test.name, test.url, test.method, test.data);
    if (success) passed++;
  }
  
  console.log(`\n📊 Test Results: ${passed}/${total} tests passed`);
  
  if (passed === total) {
    console.log('🎉 All API endpoints are working correctly!');
    console.log('\nThe Settings page should now work without errors.');
  } else {
    console.log('⚠️ Some API endpoints are not working.');
    console.log('Please check the backend server and try again.');
  }
}

// Run the tests
runTests().catch(console.error);
