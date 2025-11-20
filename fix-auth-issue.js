/**
 * Playwright script to diagnose and fix 403 authentication issue
 * Run with: node fix-auth-issue.js
 */

const API_BASE_URL = 'http://localhost:8000';
const TEST_TOKEN = 'test_clerk_token';

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function testBackendHealth() {
  console.log('\n🔍 Step 1: Testing backend connectivity...');
  try {
    const response = await fetch(`${API_BASE_URL}/health/`);
    const data = await response.json();
    console.log('✅ Backend is running:', data);
    return true;
  } catch (error) {
    console.error('❌ Backend is not running!');
    console.error('   Please start the backend with: cd backend && python manage.py runserver');
    return false;
  }
}

async function testDatabaseConnection() {
  console.log('\n🔍 Step 2: Testing database connection...');
  try {
    const response = await fetch(`${API_BASE_URL}/api/users/`, {
      headers: {
        'Authorization': `Bearer ${TEST_TOKEN}`,
        'Content-Type': 'application/json'
      }
    });
    
    console.log('   Status:', response.status);
    
    if (response.status === 403) {
      console.log('❌ Authentication failed (403 Forbidden)');
      console.log('   This means the backend rejected the authentication token');
      return false;
    } else if (response.status === 200) {
      const data = await response.json();
      console.log('✅ Database connection working');
      console.log('   Users in database:', data.length || 'Unknown');
      return true;
    } else {
      console.log('⚠️  Unexpected status:', response.status);
      return false;
    }
  } catch (error) {
    console.error('❌ Database connection test failed:', error.message);
    return false;
  }
}

async function checkMigrations() {
  console.log('\n🔍 Step 3: Checking if migrations are applied...');
  console.log('   Run this command in backend directory:');
  console.log('   python manage.py showmigrations');
  console.log('\n   If migrations are missing, run:');
  console.log('   python manage.py migrate');
}

async function testCompanyProfileEndpoint() {
  console.log('\n🔍 Step 4: Testing company profile endpoint...');
  
  // Test GET
  console.log('   Testing GET /api/users/company-profiles/...');
  try {
    const response = await fetch(`${API_BASE_URL}/api/users/company-profiles/`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${TEST_TOKEN}`,
        'Content-Type': 'application/json'
      }
    });
    
    console.log('   GET Status:', response.status);
    
    if (response.status === 403) {
      console.log('❌ GET request failed with 403 Forbidden');
      console.log('   Diagnosis: Authentication middleware is not accepting the token');
      return false;
    } else if (response.status === 200) {
      const data = await response.json();
      console.log('✅ GET request successful');
      console.log('   Profile data:', JSON.stringify(data, null, 2).substring(0, 200) + '...');
      return true;
    } else if (response.status === 404) {
      console.log('⚠️  No profile found (404) - this is normal for first time');
      return true;
    } else {
      console.log('⚠️  Unexpected status:', response.status);
      const text = await response.text();
      console.log('   Response:', text);
      return false;
    }
  } catch (error) {
    console.error('❌ Request failed:', error.message);
    return false;
  }
}

async function testCreateProfile() {
  console.log('\n🔍 Step 5: Testing profile creation...');
  
  try {
    const testData = {
      company_name: 'Test Company',
      email: 'test@company.com',
      whatsapp_number: '+1234567890',
      address: '123 Test Street'
    };
    
    console.log('   Attempting to create profile...');
    const response = await fetch(`${API_BASE_URL}/api/users/company-profiles/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${TEST_TOKEN}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(testData)
    });
    
    console.log('   POST Status:', response.status);
    
    if (response.status === 403) {
      console.log('❌ POST request failed with 403 Forbidden');
      return false;
    } else if (response.status === 200 || response.status === 201) {
      const data = await response.json();
      console.log('✅ Profile created successfully');
      console.log('   Profile ID:', data.id);
      return true;
    } else {
      console.log('⚠️  Unexpected status:', response.status);
      const text = await response.text();
      console.log('   Response:', text);
      return false;
    }
  } catch (error) {
    console.error('❌ Request failed:', error.message);
    return false;
  }
}

async function checkAuthenticationClasses() {
  console.log('\n🔍 Step 6: Checking authentication configuration...');
  console.log('   The backend should have these authentication classes:');
  console.log('   1. DevelopmentAuthentication (for test_clerk_token)');
  console.log('   2. SessionAuthentication');
  console.log('   3. ClerkAuthentication');
  console.log('\n   Check backend/frameio_backend/settings.py');
  console.log('   Look for DEFAULT_AUTHENTICATION_CLASSES');
}

async function provideSolution() {
  console.log('\n💡 SOLUTION:');
  console.log('=' .repeat(60));
  console.log('\nThe 403 error is caused by authentication failure.');
  console.log('Here\'s how to fix it:\n');
  
  console.log('1. ENSURE BACKEND IS RUNNING:');
  console.log('   cd backend');
  console.log('   python manage.py runserver\n');
  
  console.log('2. RUN MIGRATIONS (if not done):');
  console.log('   cd backend');
  console.log('   python manage.py migrate\n');
  
  console.log('3. CREATE A TEST USER:');
  console.log('   cd backend');
  console.log('   python manage.py shell');
  console.log('   Then run:');
  console.log('   >>> from django.contrib.auth import get_user_model');
  console.log('   >>> User = get_user_model()');
  console.log('   >>> user = User.objects.create_user(');
  console.log('   ...     email="test@example.com",');
  console.log('   ...     username="testuser",');
  console.log('   ...     password="testpass123"');
  console.log('   ... )');
  console.log('   >>> user.save()');
  console.log('   >>> exit()\n');
  
  console.log('4. RESTART BACKEND SERVER:');
  console.log('   Press Ctrl+C to stop the server');
  console.log('   python manage.py runserver\n');
  
  console.log('5. TEST AGAIN in the frontend\n');
  
  console.log('=' .repeat(60));
}

async function runDiagnostics() {
  console.log('🚀 Starting Authentication Diagnostics...');
  console.log('=' .repeat(60));
  
  const healthOk = await testBackendHealth();
  if (!healthOk) {
    await provideSolution();
    return;
  }
  
  await sleep(500);
  const dbOk = await testDatabaseConnection();
  
  await sleep(500);
  await checkMigrations();
  
  await sleep(500);
  const profileOk = await testCompanyProfileEndpoint();
  
  if (!profileOk) {
    await sleep(500);
    await checkAuthenticationClasses();
    await sleep(500);
    await provideSolution();
    return;
  }
  
  await sleep(500);
  const createOk = await testCreateProfile();
  
  console.log('\n' + '=' .repeat(60));
  console.log('📊 DIAGNOSTIC SUMMARY:');
  console.log('=' .repeat(60));
  console.log('Backend Health:', healthOk ? '✅' : '❌');
  console.log('Database Connection:', dbOk ? '✅' : '❌');
  console.log('Profile Endpoint:', profileOk ? '✅' : '❌');
  console.log('Profile Creation:', createOk ? '✅' : '❌');
  console.log('=' .repeat(60));
  
  if (healthOk && profileOk && createOk) {
    console.log('\n🎉 ALL TESTS PASSED!');
    console.log('   The backend is working correctly.');
    console.log('   If you still see 403 errors, check:');
    console.log('   1. Frontend is using the correct API URL');
    console.log('   2. CORS is properly configured');
    console.log('   3. Browser cache is cleared');
  } else {
    console.log('\n❌ SOME TESTS FAILED');
    await provideSolution();
  }
}

// Run diagnostics
runDiagnostics().catch(console.error);







