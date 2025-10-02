#!/usr/bin/env node

/**
 * AI Services Test Runner
 * Phase 1 Week 1 Team Member 3 - Comprehensive Testing Script
 */

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

// Test configuration
const config = {
  // Test suites to run
  suites: [
    {
      name: 'AI Services Frontend',
      config: 'playwright.config.ai-services.ts',
      project: 'ai-services-desktop',
      tests: ['ai-services.spec.ts']
    },
    {
      name: 'AI Backend API',
      config: 'playwright.config.ai-services.ts',
      project: 'ai-backend-api',
      tests: ['ai-backend-api.spec.ts']
    },
    {
      name: 'AI Integration Tests',
      config: 'playwright.config.ai-services.ts',
      project: 'ai-services-desktop',
      tests: ['ai-integration.spec.ts']
    },
    {
      name: 'AI Mobile Tests',
      config: 'playwright.config.ai-services.ts',
      project: 'ai-services-mobile',
      tests: ['ai-services.spec.ts']
    }
  ],
  
  // Output directories
  outputDir: 'test-results/ai-services',
  reportDir: 'playwright-report/ai-services',
  
  // Test options
  options: {
    headed: process.argv.includes('--headed'),
    debug: process.argv.includes('--debug'),
    verbose: process.argv.includes('--verbose'),
    updateSnapshots: process.argv.includes('--update-snapshots'),
    workers: process.env.CI ? 2 : 4
  }
};

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m'
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function createDirectories() {
  const dirs = [
    config.outputDir,
    config.reportDir,
    'test-archives',
    'test-results/screenshots',
    'test-results/videos'
  ];
  
  dirs.forEach(dir => {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
      log(`📁 Created directory: ${dir}`, 'cyan');
    }
  });
}

function runCommand(command, args, options = {}) {
  return new Promise((resolve, reject) => {
    log(`🚀 Running: ${command} ${args.join(' ')}`, 'blue');
    
    const child = spawn(command, args, {
      stdio: 'inherit',
      shell: true,
      ...options
    });
    
    child.on('close', (code) => {
      if (code === 0) {
        resolve(code);
      } else {
        reject(new Error(`Command failed with exit code ${code}`));
      }
    });
    
    child.on('error', (error) => {
      reject(error);
    });
  });
}

async function checkPrerequisites() {
  log('🔍 Checking prerequisites...', 'yellow');
  
  // Check if Playwright is installed
  try {
    await runCommand('npx', ['playwright', '--version']);
    log('✅ Playwright is installed', 'green');
  } catch (error) {
    log('❌ Playwright not found. Installing...', 'red');
    await runCommand('npx', ['playwright', 'install']);
  }
  
  // Check if backend is running
  try {
    const response = await fetch('http://localhost:8000/api/');
    if (response.ok) {
      log('✅ Django backend is running', 'green');
    } else {
      throw new Error('Backend not responding');
    }
  } catch (error) {
    log('⚠️ Django backend not running. Please start it manually:', 'yellow');
    log('   cd backend && python manage.py runserver 8000', 'cyan');
  }
  
  // Check if frontend is running
  try {
    const response = await fetch('http://localhost:3000');
    if (response.ok) {
      log('✅ Next.js frontend is running', 'green');
    } else {
      throw new Error('Frontend not responding');
    }
  } catch (error) {
    log('⚠️ Next.js frontend not running. Please start it manually:', 'yellow');
    log('   npm run dev', 'cyan');
  }
}

async function runTestSuite(suite) {
  log(`\n🧪 Running test suite: ${suite.name}`, 'magenta');
  log('=' .repeat(50), 'magenta');
  
  const args = [
    'playwright', 'test',
    '--config', suite.config,
    '--project', suite.project
  ];
  
  // Add test files
  if (suite.tests && suite.tests.length > 0) {
    args.push(...suite.tests.map(test => `tests/${test}`));
  }
  
  // Add options
  if (config.options.headed) {
    args.push('--headed');
  }
  
  if (config.options.debug) {
    args.push('--debug');
  }
  
  if (config.options.verbose) {
    args.push('--reporter=line');
  }
  
  if (config.options.updateSnapshots) {
    args.push('--update-snapshots');
  }
  
  args.push('--workers', config.options.workers.toString());
  
  try {
    await runCommand('npx', args);
    log(`✅ ${suite.name} completed successfully`, 'green');
    return { name: suite.name, status: 'passed' };
  } catch (error) {
    log(`❌ ${suite.name} failed`, 'red');
    return { name: suite.name, status: 'failed', error: error.message };
  }
}

async function generateSummaryReport(results) {
  log('\n📊 Generating summary report...', 'yellow');
  
  const summary = {
    timestamp: new Date().toISOString(),
    suite: 'AI Services - Phase 1 Week 1 Team Member 3',
    environment: {
      node: process.version,
      platform: process.platform,
      ci: !!process.env.CI
    },
    configuration: config.options,
    results: results,
    statistics: {
      total: results.length,
      passed: results.filter(r => r.status === 'passed').length,
      failed: results.filter(r => r.status === 'failed').length,
      successRate: 0
    }
  };
  
  summary.statistics.successRate = 
    (summary.statistics.passed / summary.statistics.total * 100).toFixed(1);
  
  // Save summary
  const summaryPath = path.join(config.outputDir, 'test-summary.json');
  fs.writeFileSync(summaryPath, JSON.stringify(summary, null, 2));
  
  // Display summary
  log('\n🎯 Test Execution Summary', 'bright');
  log('=' .repeat(50), 'bright');
  log(`📅 Completed: ${new Date().toLocaleString()}`, 'cyan');
  log(`🧪 Total Suites: ${summary.statistics.total}`, 'cyan');
  log(`✅ Passed: ${summary.statistics.passed}`, 'green');
  log(`❌ Failed: ${summary.statistics.failed}`, 'red');
  log(`📊 Success Rate: ${summary.statistics.successRate}%`, 'cyan');
  
  // Show individual results
  log('\n📋 Individual Results:', 'yellow');
  results.forEach(result => {
    const status = result.status === 'passed' ? '✅' : '❌';
    const color = result.status === 'passed' ? 'green' : 'red';
    log(`  ${status} ${result.name}`, color);
    if (result.error) {
      log(`    Error: ${result.error}`, 'red');
    }
  });
  
  // Show artifacts
  log('\n📁 Test Artifacts:', 'yellow');
  log(`  📊 HTML Report: ${config.reportDir}/index.html`, 'cyan');
  log(`  📋 Summary: ${summaryPath}`, 'cyan');
  log(`  📸 Screenshots: test-results/screenshots/`, 'cyan');
  log(`  🎥 Videos: test-results/videos/`, 'cyan');
  
  return summary;
}

async function main() {
  try {
    log('🚀 AI Services Test Runner Starting...', 'bright');
    log('Phase 1 Week 1 Team Member 3 - Comprehensive Testing', 'cyan');
    log('=' .repeat(60), 'bright');
    
    // Setup
    createDirectories();
    await checkPrerequisites();
    
    // Run test suites
    const results = [];
    
    for (const suite of config.suites) {
      const result = await runTestSuite(suite);
      results.push(result);
      
      // Short pause between suites
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    // Generate summary
    const summary = await generateSummaryReport(results);
    
    // Final status
    const allPassed = results.every(r => r.status === 'passed');
    
    if (allPassed) {
      log('\n🎉 All AI Services tests completed successfully!', 'green');
      process.exit(0);
    } else {
      log('\n⚠️ Some AI Services tests failed. Check the reports for details.', 'yellow');
      process.exit(1);
    }
    
  } catch (error) {
    log(`\n❌ Test runner failed: ${error.message}`, 'red');
    process.exit(1);
  }
}

// Handle command line arguments
if (process.argv.includes('--help') || process.argv.includes('-h')) {
  log('AI Services Test Runner', 'bright');
  log('Usage: node scripts/test-ai-services.js [options]', 'cyan');
  log('\nOptions:', 'yellow');
  log('  --headed          Run tests in headed mode', 'cyan');
  log('  --debug           Run tests in debug mode', 'cyan');
  log('  --verbose         Verbose output', 'cyan');
  log('  --update-snapshots Update visual snapshots', 'cyan');
  log('  --help, -h        Show this help message', 'cyan');
  process.exit(0);
}

// Run the main function
main().catch(error => {
  log(`Fatal error: ${error.message}`, 'red');
  process.exit(1);
});
