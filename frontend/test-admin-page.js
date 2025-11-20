/**
 * Simple test script to verify admin page functionality
 * Run this in the browser console on localhost:3000
 */

// Test function to check admin page access
function testAdminPageAccess() {
  console.log('🧪 Testing Admin Page Access...')
  
  // Test 1: Check if admin link exists in sidebar
  const adminLink = document.querySelector('a[href="/admin"]')
  if (adminLink) {
    console.log('✅ Admin link found in sidebar')
    console.log('   Text:', adminLink.textContent)
    console.log('   Visible:', adminLink.offsetParent !== null)
  } else {
    console.log('❌ Admin link not found in sidebar')
  }
  
  // Test 2: Try to access admin page
  console.log('\n🔗 Testing direct access to /admin...')
  window.open('/admin', '_blank')
  
  // Test 3: Check user role context
  console.log('\n👤 Checking user role context...')
  const roleElement = document.querySelector('[data-testid="user-role"]')
  if (roleElement) {
    console.log('✅ User role element found:', roleElement.textContent)
  } else {
    console.log('ℹ️  User role element not found (may be in different location)')
  }
  
  // Test 4: Check for admin-specific elements
  console.log('\n🛡️ Checking for admin-specific elements...')
  const adminElements = document.querySelectorAll('[data-admin-only]')
  console.log(`Found ${adminElements.length} admin-only elements`)
  
  // Test 5: Check localStorage for role data
  console.log('\n💾 Checking localStorage for role data...')
  const userRole = localStorage.getItem('user-role')
  const orgId = localStorage.getItem('organization-id')
  console.log('User Role:', userRole)
  console.log('Organization ID:', orgId)
  
  console.log('\n✨ Admin page test completed!')
  console.log('📝 Check the new tab for admin page access results')
}

// Test function to simulate role switching
function testRoleSwitching() {
  console.log('🔄 Testing Role Switching...')
  
  const roles = ['Admin', 'Manager', 'Designer']
  const currentRole = localStorage.getItem('user-role') || 'Designer'
  const currentIndex = roles.indexOf(currentRole)
  const nextRole = roles[(currentIndex + 1) % roles.length]
  
  console.log(`Switching from ${currentRole} to ${nextRole}`)
  localStorage.setItem('user-role', nextRole)
  
  console.log('✅ Role switched! Refresh the page to see changes')
  console.log('🔄 Refreshing page in 2 seconds...')
  
  setTimeout(() => {
    window.location.reload()
  }, 2000)
}

// Test function to check admin page components
function testAdminComponents() {
  console.log('🧩 Testing Admin Components...')
  
  // Check if admin components are loaded
  const adminComponents = [
    'AdminDashboard',
    'AdminRouteProtection', 
    'AdminNavLink'
  ]
  
  adminComponents.forEach(component => {
    console.log(`Checking for ${component}...`)
    // This would need to be implemented based on how components are exposed
    console.log(`ℹ️  ${component} component check (implement based on your setup)`)
  })
}

// Main test runner
function runAdminTests() {
  console.log('🚀 Starting Admin Page Tests...')
  console.log('=' * 50)
  
  testAdminPageAccess()
  
  console.log('\n' + '=' * 50)
  console.log('💡 Additional Tests Available:')
  console.log('   - testRoleSwitching() - Test role switching')
  console.log('   - testAdminComponents() - Test admin components')
  console.log('   - runAdminTests() - Run all tests again')
}

// Auto-run tests
runAdminTests()

// Export functions for manual testing
window.testAdminPageAccess = testAdminPageAccess
window.testRoleSwitching = testRoleSwitching
window.testAdminComponents = testAdminComponents
window.runAdminTests = runAdminTests
