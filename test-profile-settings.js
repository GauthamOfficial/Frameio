/**
 * Complete test for profile settings feature
 */

const API_BASE_URL = 'http://localhost:8000';
const TEST_TOKEN = 'test_clerk_token';

async function testProfileSettings() {
  console.log('🧪 Testing Profile Settings Feature');
  console.log('=' .repeat(60));
  
  let allPassed = true;
  
  // Test 1: Health Check
  console.log('\n1️⃣ Health Check...');
  try {
    const response = await fetch(`${API_BASE_URL}/health/`);
    if (response.ok) {
      console.log('   ✅ Backend is running');
    } else {
      console.log('   ❌ Backend health check failed:', response.status);
      allPassed = false;
    }
  } catch (error) {
    console.log('   ❌ Cannot connect to backend:', error.message);
    console.log('   💡 Start backend with: cd backend && python manage.py runserver');
    allPassed = false;
    return;
  }
  
  // Test 2: GET Profile (Load)
  console.log('\n2️⃣ Loading Company Profile...');
  try {
    const response = await fetch(`${API_BASE_URL}/api/users/company-profiles/`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${TEST_TOKEN}`,
        'Content-Type': 'application/json'
      }
    });
    
    console.log(`   Status: ${response.status}`);
    
    if (response.status === 200) {
      const data = await response.json();
      console.log('   ✅ Profile loaded successfully');
      console.log('   Company:', data.company_name || '(not set)');
      console.log('   Email:', data.email || '(not set)');
    } else if (response.status === 404) {
      console.log('   ℹ️  No profile found (will be created on first save)');
    } else if (response.status === 403) {
      console.log('   ❌ Authentication failed (403 Forbidden)');
      console.log('   💡 Backend server needs restart!');
      console.log('   💡 Run: cd backend && python manage.py runserver');
      allPassed = false;
    } else {
      const text = await response.text();
      console.log('   ❌ Unexpected response:', text.substring(0, 200));
      allPassed = false;
    }
  } catch (error) {
    console.log('   ❌ Error:', error.message);
    allPassed = false;
  }
  
  // Test 3: POST Profile (Save)
  console.log('\n3️⃣ Saving Company Profile...');
  try {
    const testData = {
      company_name: 'Test Company',
      email: 'contact@testcompany.com',
      whatsapp_number: '+1234567890',
      address: '123 Test Street',
      description: 'A test company for testing profile settings'
    };
    
    const response = await fetch(`${API_BASE_URL}/api/users/company-profiles/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${TEST_TOKEN}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(testData)
    });
    
    console.log(`   Status: ${response.status}`);
    
    if (response.status === 200 || response.status === 201) {
      const data = await response.json();
      console.log('   ✅ Profile saved successfully');
      console.log('   Profile ID:', data.id);
      console.log('   Company:', data.company_name);
    } else if (response.status === 403) {
      console.log('   ❌ Authentication failed (403 Forbidden)');
      console.log('   💡 Backend server needs restart!');
      allPassed = false;
    } else {
      const text = await response.text();
      console.log('   ❌ Save failed:', text.substring(0, 200));
      allPassed = false;
    }
  } catch (error) {
    console.log('   ❌ Error:', error.message);
    allPassed = false;
  }
  
  // Test 4: GET Status
  console.log('\n4️⃣ Checking Profile Status...');
  try {
    const response = await fetch(`${API_BASE_URL}/api/users/company-profiles/status/`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${TEST_TOKEN}`,
        'Content-Type': 'application/json'
      }
    });
    
    console.log(`   Status: ${response.status}`);
    
    if (response.status === 200) {
      const data = await response.json();
      console.log('   ✅ Status loaded successfully');
      console.log('   Completion:', data.completion_percentage + '%');
      console.log('   Has profile:', data.has_profile);
      console.log('   Has logo:', data.has_logo);
    } else {
      console.log('   ⚠️  Could not load status');
    }
  } catch (error) {
    console.log('   ⚠️  Status check error:', error.message);
  }
  
  // Summary
  console.log('\n' + '='.repeat(60));
  if (allPassed) {
    console.log('🎉 ALL TESTS PASSED!');
    console.log('   Profile settings feature is working correctly.');
  } else {
    console.log('❌ SOME TESTS FAILED');
    console.log('\n💡 SOLUTION:');
    console.log('   1. Make sure MySQL is running');
    console.log('   2. Restart backend server:');
    console.log('      cd backend');
    console.log('      python manage.py runserver');
    console.log('   3. Run this test again');
  }
  console.log('='.repeat(60));
}

testProfileSettings().catch(console.error);








