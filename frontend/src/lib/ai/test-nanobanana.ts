/**
 * Test utility for NanoBanana service fallback mechanism
 * This can be imported and used in components for testing
 */

import { nanoBananaService } from './nanobanana';

export interface TestResult {
  testName: string;
  passed: boolean;
  message: string;
  details?: Record<string, unknown>;
}

export class NanoBananaTester {
  /**
   * Test the service configuration
   */
  static testConfiguration(): TestResult {
    const status = nanoBananaService.getServiceStatus();
    const isConfigured = nanoBananaService.isConfigured();
    
    return {
      testName: 'Configuration Test',
      passed: !isConfigured, // Should not be configured in test environment
      message: isConfigured 
        ? 'Service is configured (unexpected in test environment)'
        : 'Service is not configured (expected for fallback testing)',
      details: status
    };
  }

  /**
   * Test the fallback mechanism
   */
  static async testFallback(): Promise<TestResult> {
    try {
      const result = await nanoBananaService.generateImage('test prompt for fallback', {
        style: 'modern',
        aspect_ratio: '1:1'
      });
      
      const fallbackWorking = !!(!result.success && 
                              result.error && 
                              result.error.includes('backend generation'));
      
      return {
        testName: 'Fallback Mechanism Test',
        passed: fallbackWorking,
        message: fallbackWorking 
          ? 'Fallback mechanism working correctly'
          : 'Fallback mechanism not working as expected',
        details: result as unknown as Record<string, unknown>
      };
    } catch (error) {
      return {
        testName: 'Fallback Mechanism Test',
        passed: false,
        message: `Error during fallback test: ${error instanceof Error ? error.message : 'Unknown error'}`,
        details: { error }
      };
    }
  }

  /**
   * Test error handling
   */
  static async testErrorHandling(): Promise<TestResult> {
    try {
      // Test with invalid configuration
      const result = await nanoBananaService.generateImage('test prompt', {
        style: 'invalid-style',
        aspect_ratio: 'invalid-ratio' as '1:1'
      });
      
      // Should return fallback response, not throw error
      return {
        testName: 'Error Handling Test',
        passed: !result.success,
        message: result.success 
          ? 'Unexpected success with invalid configuration'
          : 'Error handling working correctly',
        details: result as unknown as Record<string, unknown>
      };
    } catch (error) {
      return {
        testName: 'Error Handling Test',
        passed: false,
        message: `Unexpected error thrown: ${error instanceof Error ? error.message : 'Unknown error'}`,
        details: { error }
      };
    }
  }

  /**
   * Run all tests
   */
  static async runAllTests(): Promise<TestResult[]> {
    console.log('🧪 Running NanoBanana Service Tests\n');
    
    const results: TestResult[] = [];
    
    // Test 1: Configuration
    const configTest = this.testConfiguration();
    results.push(configTest);
    console.log(`${configTest.passed ? '✅' : '❌'} ${configTest.testName}: ${configTest.message}`);
    
    // Test 2: Fallback mechanism
    const fallbackTest = await this.testFallback();
    results.push(fallbackTest);
    console.log(`${fallbackTest.passed ? '✅' : '❌'} ${fallbackTest.testName}: ${fallbackTest.message}`);
    
    // Test 3: Error handling
    const errorTest = await this.testErrorHandling();
    results.push(errorTest);
    console.log(`${errorTest.passed ? '✅' : '❌'} ${errorTest.testName}: ${errorTest.message}`);
    
    // Summary
    const passedTests = results.filter(r => r.passed).length;
    const totalTests = results.length;
    
    console.log(`\n📊 Test Summary: ${passedTests}/${totalTests} tests passed`);
    
    if (passedTests === totalTests) {
      console.log('🎉 All tests passed! NanoBanana service is working correctly.');
    } else {
      console.log('⚠️  Some tests failed. Check the details above.');
    }
    
    return results;
  }
}

// Export for use in components
export default NanoBananaTester;










