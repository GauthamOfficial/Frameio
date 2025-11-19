/**
 * Test authentication directly by checking what the server logs
 */

const API_BASE_URL = 'http://localhost:8000';

async function testWithLogging() {
  console.log('\n🔍 Testing authentication with detailed logging...\n');
  
  console.log('1. Testing without any authentication:');
  try {
    const response1 = await fetch(`${API_BASE_URL}/api/users/company-profiles/`);
    console.log(`   Status: ${response1.status}`);
    const text1 = await response1.text();
    console.log(`   Response: ${text1.substring(0, 100)}`);
  } catch (e) {
    console.log(`   Error: ${e.message}`);
  }
  
  console.log('\n2. Testing with test_clerk_token:');
  try {
    const response2 = await fetch(`${API_BASE_URL}/api/users/company-profiles/`, {
      headers: {
        'Authorization': 'Bearer test_clerk_token'
      }
    });
    console.log(`   Status: ${response2.status}`);
    const text2 = await response2.text();
    console.log(`   Response: ${text2.substring(0, 200)}`);
  } catch (e) {
    console.log(`   Error: ${e.message}`);
  }
  
  console.log('\n3. Testing with X-Dev-User-ID header:');
  try {
    const response3 = await fetch(`${API_BASE_URL}/api/users/company-profiles/`, {
      headers: {
        'Authorization': 'Bearer test_clerk_token',
        'X-Dev-User-ID': '97e36ced-7160-472d-ab5c-77cd2b4e8480'
      }
    });
    console.log(`   Status: ${response3.status}`);
    const text3 = await response3.text();
    console.log(`   Response: ${text3.substring(0, 200)}`);
  } catch (e) {
    console.log(`   Error: ${e.message}`);
  }
  
  console.log('\n📝 Check the backend server logs for authentication debugging');
  console.log('   The logs should show which authentication class is being used');
}

testWithLogging();






