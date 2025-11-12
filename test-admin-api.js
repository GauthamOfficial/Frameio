/**
 * Direct API test for admin users endpoints
 * Run with: node test-admin-api.js
 */

const API_BASE = 'http://localhost:3000';
const DJANGO_BASE = 'http://localhost:8000';
const ADMIN_USER = 'tsg_admin';
const ADMIN_PASS = 'tsgtharsiyanshahastragautham321';

let adminCookie = null;

async function login() {
  console.log('\n=== Testing Admin Login ===');
  const response = await fetch(`${API_BASE}/api/admin/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: ADMIN_USER,
      password: ADMIN_PASS
    })
  });
  
  console.log('Login Status:', response.status);
  const data = await response.json();
  console.log('Login Response:', data);
  
  // Get cookie from response
  const setCookie = response.headers.get('set-cookie');
  if (setCookie) {
    adminCookie = setCookie.split(';')[0];
    console.log('Admin Cookie:', adminCookie);
  }
  
  return response.ok;
}

async function verifyAuth() {
  console.log('\n=== Verifying Authentication ===');
  const response = await fetch(`${API_BASE}/api/admin/verify`, {
    headers: {
      'Cookie': adminCookie || ''
    }
  });
  
  console.log('Verify Status:', response.status);
  const data = await response.json();
  console.log('Verify Response:', data);
  
  return data.authenticated;
}

async function getUsers() {
  console.log('\n=== Getting Users ===');
  const response = await fetch(`${API_BASE}/api/admin/users`, {
    headers: {
      'Cookie': adminCookie || ''
    }
  });
  
  console.log('Get Users Status:', response.status);
  const data = await response.json();
  console.log('Users Response:', JSON.stringify(data, null, 2).substring(0, 1000));
  
  return data;
}

async function testDjangoDirectly() {
  console.log('\n=== Testing Django API Directly ===');
  
  // Test GET users with admin headers
  console.log('\n1. GET /api/users/ with admin headers');
  const getResponse = await fetch(`${DJANGO_BASE}/api/users/`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'X-Admin-Request': 'true',
      'X-Admin-Username': ADMIN_USER
    }
  });
  
  console.log('Django GET Status:', getResponse.status);
  const users = await getResponse.json().catch(() => getResponse.text());
  console.log('Django GET Response:', JSON.stringify(users, null, 2).substring(0, 1000));
  
  // Get first user ID
  let userId = null;
  if (Array.isArray(users) && users.length > 0) {
    userId = users[0].id;
  } else if (users.results && users.results.length > 0) {
    userId = users.results[0].id;
  }
  
  if (userId) {
    console.log('\nFound user ID:', userId);
    
    // Test UPDATE
    console.log(`\n2. PATCH /api/users/${userId}/ with admin headers`);
    const patchResponse = await fetch(`${DJANGO_BASE}/api/users/${userId}/`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'X-Admin-Request': 'true',
        'X-Admin-Username': ADMIN_USER
      },
      body: JSON.stringify({
        first_name: 'Test',
        last_name: 'Updated'
      })
    });
    
    console.log('Django PATCH Status:', patchResponse.status);
    const patchData = await patchResponse.json().catch(() => patchResponse.text());
    console.log('Django PATCH Response:', JSON.stringify(patchData, null, 2));
    
    // Test DELETE
    console.log(`\n3. DELETE /api/users/${userId}/ with admin headers`);
    const deleteResponse = await fetch(`${DJANGO_BASE}/api/users/${userId}/`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        'X-Admin-Request': 'true',
        'X-Admin-Username': ADMIN_USER
      }
    });
    
    console.log('Django DELETE Status:', deleteResponse.status);
    const deleteData = await deleteResponse.text();
    console.log('Django DELETE Response:', deleteData || '(empty - successful 204)');
  } else {
    console.log('No users found to test with');
  }
}

async function testViaProxy(userId) {
  console.log('\n=== Testing Via Next.js Proxy ===');
  
  // Test UPDATE via proxy
  console.log(`\n1. PATCH /api/admin/users/${userId} via proxy`);
  const patchResponse = await fetch(`${API_BASE}/api/admin/users/${userId}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'Cookie': adminCookie || ''
    },
    body: JSON.stringify({
      first_name: 'Test',
      last_name: 'Proxy Updated'
    })
  });
  
  console.log('Proxy PATCH Status:', patchResponse.status);
  const patchText = await patchResponse.text();
  console.log('Proxy PATCH Response:', patchText);
  try {
    const patchData = JSON.parse(patchText);
    console.log('Parsed:', JSON.stringify(patchData, null, 2));
  } catch (e) {
    console.log('Could not parse as JSON');
  }
  
  // Test DELETE via proxy
  console.log(`\n2. DELETE /api/admin/users/${userId} via proxy`);
  const deleteResponse = await fetch(`${API_BASE}/api/admin/users/${userId}`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
      'Cookie': adminCookie || ''
    }
  });
  
  console.log('Proxy DELETE Status:', deleteResponse.status);
  const deleteText = await deleteResponse.text();
  console.log('Proxy DELETE Response:', deleteText);
  try {
    const deleteData = JSON.parse(deleteText);
    console.log('Parsed:', JSON.stringify(deleteData, null, 2));
  } catch (e) {
    console.log('Could not parse as JSON (this is ok for 204)');
  }
}

async function main() {
  try {
    console.log('Starting Admin API Tests...\n');
    console.log('Make sure both servers are running:');
    console.log('- Frontend: http://localhost:3000');
    console.log('- Backend: http://localhost:8000');
    
    // Test Django directly first (doesn't require Next.js)
    await testDjangoDirectly();
    
    // Now test via Next.js proxy
    console.log('\n' + '='.repeat(60));
    console.log('Testing Next.js Proxy (requires frontend server)');
    console.log('='.repeat(60));
    
    const loggedIn = await login();
    if (!loggedIn) {
      console.error('\n❌ Login failed! Check if frontend server is running.');
      return;
    }
    
    const authenticated = await verifyAuth();
    if (!authenticated) {
      console.error('\n❌ Authentication verification failed!');
      return;
    }
    
    const users = await getUsers();
    
    // Extract user ID
    let userId = null;
    if (Array.isArray(users) && users.length > 0) {
      userId = users[0].id;
    } else if (users.results && users.results.length > 0) {
      userId = users.results[0].id;
    }
    
    if (userId) {
      await testViaProxy(userId);
    }
    
    console.log('\n✅ Tests completed!');
    
  } catch (error) {
    console.error('\n❌ Error:', error.message);
    console.error(error.stack);
  }
}

main();

