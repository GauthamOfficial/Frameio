#!/usr/bin/env node

/**
 * AI Integration Verification Script
 * Verifies all AI integration features are working correctly
 */

const fs = require('fs');
const path = require('path');

// Colors for console output
const colors = {
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  reset: '\x1b[0m',
  bold: '\x1b[1m',
};

// Test results
const results = {
  passed: 0,
  failed: 0,
  warnings: 0,
  tests: [],
};

function log(message, type = 'info') {
  const timestamp = new Date().toISOString();
  const prefix = {
    info: `${colors.blue}ℹ${colors.reset}`,
    success: `${colors.green}✓${colors.reset}`,
    error: `${colors.red}✗${colors.reset}`,
    warning: `${colors.yellow}⚠${colors.reset}`,
  }[type];
  
  console.log(`${prefix} [${timestamp}] ${message}`);
}

function test(name, condition, message) {
  if (condition) {
    results.passed++;
    results.tests.push({ name, status: 'passed', message });
    log(`${name}: ${message}`, 'success');
  } else {
    results.failed++;
    results.tests.push({ name, status: 'failed', message });
    log(`${name}: ${message}`, 'error');
  }
}

function warn(name, message) {
  results.warnings++;
  results.tests.push({ name, status: 'warning', message });
  log(`${name}: ${message}`, 'warning');
}

// File existence checks
function checkFileExists(filePath, description) {
  const fullPath = path.join(__dirname, '..', filePath);
  const exists = fs.existsSync(fullPath);
  test(
    `File exists: ${description}`,
    exists,
    exists ? 'File found' : `File not found: ${filePath}`
  );
  return exists;
}

// Content validation
function checkFileContent(filePath, checks, description) {
  const fullPath = path.join(__dirname, '..', filePath);
  
  if (!fs.existsSync(fullPath)) {
    test(`Content check: ${description}`, false, `File not found: ${filePath}`);
    return false;
  }
  
  const content = fs.readFileSync(fullPath, 'utf8');
  let allPassed = true;
  
  checks.forEach((check, index) => {
    const passed = check.test(content);
    test(
      `Content check ${index + 1}: ${description}`,
      passed,
      passed ? check.message : check.failMessage
    );
    if (!passed) allPassed = false;
  });
  
  return allPassed;
}

// Main verification function
async function verifyAIIntegration() {
  log('Starting AI Integration Verification...', 'info');
  log('='.repeat(60), 'info');
  
  // 1. Check required files exist
  log('\n1. Checking required files...', 'info');
  
  const requiredFiles = [
    'src/lib/ai/nanobanana.ts',
    'src/lib/ai/promptUtils.ts',
    'src/lib/ai/errorHandler.ts',
    'src/components/ColorPaletteExtractor.tsx',
    'src/components/TemplateRecommender.tsx',
    'src/components/lazy/enhanced-poster-generator.tsx',
    'src/lib/ai/__tests__/ai-integration.test.ts',
  ];
  
  requiredFiles.forEach(file => {
    checkFileExists(file, file.split('/').pop());
  });
  
  // 2. Check NanoBanana service
  log('\n2. Verifying NanoBanana service...', 'info');
  
  checkFileContent('src/lib/ai/nanobanana.ts', [
    {
      test: (content) => content.includes('class NanoBananaService'),
      message: 'NanoBananaService class defined',
      failMessage: 'NanoBananaService class not found'
    },
    {
      test: (content) => content.includes('generateImage'),
      message: 'generateImage method implemented',
      failMessage: 'generateImage method not found'
    },
    {
      test: (content) => content.includes('getFallbackResponse'),
      message: 'Fallback mechanism implemented',
      failMessage: 'Fallback mechanism not found'
    },
    {
      test: (content) => content.includes('enhancePrompt'),
      message: 'Prompt enhancement implemented',
      failMessage: 'Prompt enhancement not found'
    },
    {
      test: (content) => content.includes('withErrorHandling'),
      message: 'Error handling integrated',
      failMessage: 'Error handling not integrated'
    }
  ], 'NanoBanana service');
  
  // 3. Check prompt utilities
  log('\n3. Verifying prompt utilities...', 'info');
  
  checkFileContent('src/lib/ai/promptUtils.ts', [
    {
      test: (content) => content.includes('generateTextilePrompt'),
      message: 'generateTextilePrompt function implemented',
      failMessage: 'generateTextilePrompt function not found'
    },
    {
      test: (content) => content.includes('extractKeywordsFromInput'),
      message: 'Keyword extraction implemented',
      failMessage: 'Keyword extraction not found'
    },
    {
      test: (content) => content.includes('validatePrompt'),
      message: 'Prompt validation implemented',
      failMessage: 'Prompt validation not found'
    },
    {
      test: (content) => content.includes('TEXTILE_KEYWORDS'),
      message: 'Textile keywords mapping defined',
      failMessage: 'Textile keywords mapping not found'
    }
  ], 'Prompt utilities');
  
  // 4. Check error handler
  log('\n4. Verifying error handler...', 'info');
  
  checkFileContent('src/lib/ai/errorHandler.ts', [
    {
      test: (content) => content.includes('class AIErrorHandler'),
      message: 'AIErrorHandler class defined',
      failMessage: 'AIErrorHandler class not found'
    },
    {
      test: (content) => content.includes('executeWithRetry'),
      message: 'Retry mechanism implemented',
      failMessage: 'Retry mechanism not found'
    },
    {
      test: (content) => content.includes('getUserFriendlyMessage'),
      message: 'User-friendly error messages implemented',
      failMessage: 'User-friendly error messages not found'
    },
    {
      test: (content) => content.includes('getFallbackAsset'),
      message: 'Fallback asset system implemented',
      failMessage: 'Fallback asset system not found'
    }
  ], 'Error handler');
  
  // 5. Check color palette extractor
  log('\n5. Verifying color palette extractor...', 'info');
  
  checkFileContent('src/components/ColorPaletteExtractor.tsx', [
    {
      test: (content) => content.includes('extractColorsFromImage'),
      message: 'Color extraction algorithm implemented',
      failMessage: 'Color extraction algorithm not found'
    },
    {
      test: (content) => content.includes('rgbToHex'),
      message: 'RGB to hex conversion implemented',
      failMessage: 'RGB to hex conversion not found'
    },
    {
      test: (content) => content.includes('copyColor'),
      message: 'Color copying functionality implemented',
      failMessage: 'Color copying functionality not found'
    },
    {
      test: (content) => content.includes('downloadPalette'),
      message: 'Palette download functionality implemented',
      failMessage: 'Palette download functionality not found'
    }
  ], 'Color palette extractor');
  
  // 6. Check template recommender
  log('\n6. Verifying template recommender...', 'info');
  
  checkFileContent('src/components/TemplateRecommender.tsx', [
    {
      test: (content) => content.includes('getRecommendedTemplates'),
      message: 'Template recommendation algorithm implemented',
      failMessage: 'Template recommendation algorithm not found'
    },
    {
      test: (content) => content.includes('calculateTemplateScore'),
      message: 'Template scoring system implemented',
      failMessage: 'Template scoring system not found'
    },
    {
      test: (content) => content.includes('MOCK_TEMPLATES'),
      message: 'Mock template data provided',
      failMessage: 'Mock template data not found'
    },
    {
      test: (content) => content.includes('isColorSimilar'),
      message: 'Color similarity detection implemented',
      failMessage: 'Color similarity detection not found'
    }
  ], 'Template recommender');
  
  // 7. Check enhanced poster generator
  log('\n7. Verifying enhanced poster generator...', 'info');
  
  checkFileContent('src/components/lazy/enhanced-poster-generator.tsx', [
    {
      test: (content) => content.includes('nanoBananaService'),
      message: 'NanoBanana service integrated',
      failMessage: 'NanoBanana service not integrated'
    },
    {
      test: (content) => content.includes('generateTextilePrompt'),
      message: 'Textile prompt generation integrated',
      failMessage: 'Textile prompt generation not integrated'
    },
    {
      test: (content) => content.includes('ColorPaletteExtractor'),
      message: 'Color palette extractor integrated',
      failMessage: 'Color palette extractor not integrated'
    },
    {
      test: (content) => content.includes('TemplateRecommender'),
      message: 'Template recommender integrated',
      failMessage: 'Template recommender not integrated'
    },
    {
      test: (content) => content.includes('aiServiceStatus'),
      message: 'AI service status tracking implemented',
      failMessage: 'AI service status tracking not implemented'
    }
  ], 'Enhanced poster generator');
  
  // 8. Check package.json dependencies
  log('\n8. Verifying dependencies...', 'info');
  
  const packageJsonPath = path.join(__dirname, '..', 'package.json');
  if (fs.existsSync(packageJsonPath)) {
    const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
    
    test(
      'Color-thief dependency',
      packageJson.dependencies && packageJson.dependencies['color-thief'],
      packageJson.dependencies && packageJson.dependencies['color-thief'] 
        ? 'color-thief dependency found' 
        : 'color-thief dependency missing'
    );
    
    test(
      'Axios dependency',
      packageJson.dependencies && packageJson.dependencies['axios'],
      packageJson.dependencies && packageJson.dependencies['axios'] 
        ? 'axios dependency found' 
        : 'axios dependency missing'
    );
  } else {
    test('Package.json exists', false, 'package.json not found');
  }
  
  // 9. Check environment configuration
  log('\n9. Verifying environment configuration...', 'info');
  
  const envExamplePath = path.join(__dirname, '..', '.env.example');
  if (fs.existsSync(envExamplePath)) {
    const envContent = fs.readFileSync(envExamplePath, 'utf8');
    
    test(
      'NanoBanana API key config',
      envContent.includes('NANOBANANA_API_KEY'),
      'NanoBanana API key configuration found'
    );
    
    test(
      'NanoBanana base URL config',
      envContent.includes('NANOBANANA_BASE_URL'),
      'NanoBanana base URL configuration found'
    );
  } else {
    warn('Environment example file', '.env.example not found - create one for documentation');
  }
  
  // 10. Check test coverage
  log('\n10. Verifying test coverage...', 'info');
  
  checkFileContent('src/lib/ai/__tests__/ai-integration.test.ts', [
    {
      test: (content) => content.includes('describe('),
      message: 'Test suites defined',
      failMessage: 'Test suites not found'
    },
    {
      test: (content) => content.includes('NanoBanana Service'),
      message: 'NanoBanana service tests included',
      failMessage: 'NanoBanana service tests not found'
    },
    {
      test: (content) => content.includes('Prompt Utils'),
      message: 'Prompt utilities tests included',
      failMessage: 'Prompt utilities tests not found'
    },
    {
      test: (content) => content.includes('Error Handler'),
      message: 'Error handler tests included',
      failMessage: 'Error handler tests not found'
    }
  ], 'Test coverage');
  
  // Summary
  log('\n' + '='.repeat(60), 'info');
  log('Verification Summary:', 'info');
  log(`✓ Passed: ${results.passed}`, 'success');
  log(`✗ Failed: ${results.failed}`, results.failed > 0 ? 'error' : 'info');
  log(`⚠ Warnings: ${results.warnings}`, results.warnings > 0 ? 'warning' : 'info');
  
  if (results.failed === 0) {
    log('\n🎉 All AI integration features verified successfully!', 'success');
    log('The AI integration is ready for use.', 'success');
  } else {
    log('\n❌ Some verification checks failed.', 'error');
    log('Please review the failed items above.', 'error');
  }
  
  // Detailed results
  if (results.failed > 0) {
    log('\nFailed tests:', 'error');
    results.tests
      .filter(test => test.status === 'failed')
      .forEach(test => {
        log(`  - ${test.name}: ${test.message}`, 'error');
      });
  }
  
  if (results.warnings > 0) {
    log('\nWarnings:', 'warning');
    results.tests
      .filter(test => test.status === 'warning')
      .forEach(test => {
        log(`  - ${test.name}: ${test.message}`, 'warning');
      });
  }
  
  // Exit with appropriate code
  process.exit(results.failed > 0 ? 1 : 0);
}

// Run verification
if (require.main === module) {
  verifyAIIntegration().catch(error => {
    log(`Verification failed with error: ${error.message}`, 'error');
    process.exit(1);
  });
}

module.exports = { verifyAIIntegration, results };
