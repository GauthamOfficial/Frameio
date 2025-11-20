#!/usr/bin/env node

/**
 * Phase 1 Week 2 Member 2 Test Runner
 * Comprehensive test execution and reporting for frontend features
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🚀 Phase 1 Week 2 Member 2 - Frontend Test Runner');
console.log('================================================\n');

// Test configuration
const testConfig = {
  testFile: 'tests/phase1-week2-member2.spec.ts',
  configFile: 'playwright.config.phase1-week2.ts',
  projects: [
    'phase1-week2-chromium',
    'phase1-week2-firefox', 
    'phase1-week2-webkit',
    'phase1-week2-mobile-chrome',
    'phase1-week2-mobile-safari'
  ],
  timeout: 300000 // 5 minutes
};

// Test categories and their descriptions
const testCategories = {
  'Clerk Authentication Integration': {
    description: 'Tests Clerk authentication integration, sign in/up buttons, and user profile display',
    tests: [
      'should display sign in and sign up buttons on homepage',
      'should redirect to dashboard when authenticated', 
      'should show user profile button when authenticated'
    ]
  },
  'Role-Based UI Rendering': {
    description: 'Tests role-based UI rendering, sidebar items, and permission-based access',
    tests: [
      'should show role badge in navigation header',
      'should show different sidebar items based on role',
      'should hide admin features for Designer role'
    ]
  },
  'Organization Context': {
    description: 'Tests organization context loading and display',
    tests: [
      'should load organization context on dashboard',
      'should display organization information'
    ]
  },
  'User Management UI (Admin Only)': {
    description: 'Tests user management interface for admin users',
    tests: [
      'should show user management page for Admin',
      'should show access denied for non-Admin users',
      'should display user list with search functionality',
      'should allow role changes for Admin users'
    ]
  },
  'Dashboard Layout Enhancements': {
    description: 'Tests responsive sidebar, top navigation, and quick actions',
    tests: [
      'should show responsive sidebar',
      'should show top navigation with user info',
      'should show role-based quick actions'
    ]
  },
  'Organization Settings (Admin Only)': {
    description: 'Tests organization settings access control',
    tests: [
      'should show organization settings for Admin',
      'should show access denied for non-Admin users'
    ]
  },
  'Billing Page (Admin Only)': {
    description: 'Tests billing page access control',
    tests: [
      'should show billing page for Admin',
      'should show access denied for non-Admin users'
    ]
  },
  'API Integration': {
    description: 'Tests API error handling and loading states',
    tests: [
      'should handle API errors gracefully',
      'should show loading states'
    ]
  },
  'Responsive Design': {
    description: 'Tests mobile and tablet responsiveness',
    tests: [
      'should work on mobile devices',
      'should work on tablet devices'
    ]
  },
  'Error Handling': {
    description: 'Tests network errors and permission errors',
    tests: [
      'should handle network errors',
      'should handle permission errors'
    ]
  }
};

// Function to run tests for a specific project
function runTestsForProject(project) {
  console.log(`\n🧪 Running tests for ${project}...`);
  
  try {
    const command = `npx playwright test ${testConfig.testFile} --config=${testConfig.configFile} --project=${project} --reporter=json`;
    console.log(`Command: ${command}`);
    
    const result = execSync(command, { 
      encoding: 'utf8', 
      timeout: testConfig.timeout,
      cwd: process.cwd()
    });
    
    console.log(`✅ ${project} tests completed successfully`);
    return { success: true, result };
    
  } catch (error) {
    console.log(`❌ ${project} tests failed`);
    console.log(`Error: ${error.message}`);
    return { success: false, error: error.message };
  }
}

// Function to generate test report
function generateTestReport(results) {
  const reportPath = 'test-results/phase1-week2-member2-report.md';
  
  let report = `# Phase 1 Week 2 Member 2 - Test Report\n\n`;
  report += `**Generated:** ${new Date().toISOString()}\n\n`;
  
  report += `## Test Summary\n\n`;
  
  const totalProjects = testConfig.projects.length;
  const successfulProjects = results.filter(r => r.success).length;
  const failedProjects = results.filter(r => !r.success).length;
  
  report += `- **Total Projects:** ${totalProjects}\n`;
  report += `- **Successful:** ${successfulProjects}\n`;
  report += `- **Failed:** ${failedProjects}\n`;
  report += `- **Success Rate:** ${((successfulProjects / totalProjects) * 100).toFixed(1)}%\n\n`;
  
  report += `## Test Categories\n\n`;
  
  Object.entries(testCategories).forEach(([category, info]) => {
    report += `### ${category}\n`;
    report += `**Description:** ${info.description}\n\n`;
    report += `**Tests:**\n`;
    info.tests.forEach(test => {
      report += `- ${test}\n`;
    });
    report += `\n`;
  });
  
  report += `## Project Results\n\n`;
  
  results.forEach((result, index) => {
    const project = testConfig.projects[index];
    report += `### ${project}\n`;
    report += `**Status:** ${result.success ? '✅ PASSED' : '❌ FAILED'}\n\n`;
    
    if (!result.success) {
      report += `**Error:** ${result.error}\n\n`;
    }
  });
  
  report += `## Next Steps\n\n`;
  
  if (failedProjects > 0) {
    report += `### Issues to Address:\n`;
    report += `1. Review failed test results\n`;
    report += `2. Check frontend server is running on localhost:3000\n`;
    report += `3. Verify all components are properly implemented\n`;
    report += `4. Check API mocks are working correctly\n`;
    report += `5. Ensure proper authentication mocking\n\n`;
  } else {
    report += `### All tests passed! 🎉\n`;
    report += `- Phase 1 Week 2 Member 2 implementation is complete\n`;
    report += `- All frontend features are working correctly\n`;
    report += `- Ready for Week 3 development\n\n`;
  }
  
  // Ensure directory exists
  const dir = path.dirname(reportPath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  
  fs.writeFileSync(reportPath, report);
  console.log(`\n📊 Test report generated: ${reportPath}`);
}

// Main execution
async function main() {
  console.log('Starting comprehensive test execution...\n');
  
  const results = [];
  
  // Run tests for each project
  for (const project of testConfig.projects) {
    const result = runTestsForProject(project);
    results.push({ project, ...result });
  }
  
  // Generate report
  generateTestReport(results);
  
  // Summary
  console.log('\n📋 Test Execution Summary');
  console.log('========================');
  
  const successful = results.filter(r => r.success).length;
  const failed = results.filter(r => !r.success).length;
  
  console.log(`✅ Successful: ${successful}`);
  console.log(`❌ Failed: ${failed}`);
  console.log(`📊 Success Rate: ${((successful / results.length) * 100).toFixed(1)}%`);
  
  if (failed === 0) {
    console.log('\n🎉 All Phase 1 Week 2 Member 2 tests passed!');
    console.log('✅ Frontend implementation is complete and working correctly.');
  } else {
    console.log('\n⚠️  Some tests failed. Please review the test report for details.');
  }
  
  console.log('\n📄 Check test-results/phase1-week2-member2-report.md for detailed report');
}

// Run the tests
main().catch(console.error);