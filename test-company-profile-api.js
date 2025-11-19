/**
 * Test script to verify company profile API is working
 * Run this to test if the 403 error is fixed
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

console.log('🧪 Testing Company Profile API...\n');

// Test with test_clerk_token
fetch(`${API_BASE_URL}/api/users/company-profiles/`, {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer test_clerk_token',
    'Content-Type': 'application/json',
  },
})
  .then(response => {
    console.log(`Status: ${response.status} ${response.statusText}`);
    
    if (response.status === 200) {
      console.log('✅ SUCCESS! Company profile API is working\n');
      return response.json();
    } else if (response.status === 403) {
      console.log('❌ FAILED! Still getting 403 Forbidden\n');
      console.log('Troubleshooting steps:');
      console.log('1. Make sure you restarted the backend server');
      console.log('2. Check backend logs for authentication errors');
      console.log('3. Make sure at least one user exists in the database');
      console.log('4. Run: cd backend && python manage.py createsuperuser');
      throw new Error('403 Forbidden');
    } else {
      console.log(`❌ FAILED! Unexpected status: ${response.status}\n`);
      throw new Error(`HTTP ${response.status}`);
    }
  })
  .then(data => {
    console.log('Response data:');
    console.log(JSON.stringify(data, null, 2));
    console.log('\n✅ All tests passed! The fix is working correctly.');
  })
  .catch(error => {
    if (error.message !== '403 Forbidden' && error.code === 'ECONNREFUSED') {
      console.error('\n❌ ERROR: Cannot connect to backend server');
      console.error('Make sure the backend is running:');
      console.error('  cd backend');
      console.error('  python manage.py runserver');
    } else if (error.message !== '403 Forbidden') {
      console.error('\n❌ ERROR:', error.message);
    }
    process.exit(1);
  });


