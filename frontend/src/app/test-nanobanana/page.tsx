'use client';

import { useState } from 'react';
import { nanoBananaService } from '@/lib/ai/nanobanana';
import NanoBananaTester from '@/lib/ai/test-nanobanana';

export default function TestNanoBananaPage() {
  const [testResults, setTestResults] = useState<any[]>([]);
  const [isRunning, setIsRunning] = useState(false);

  const runTests = async () => {
    setIsRunning(true);
    setTestResults([]);
    
    try {
      const results = await NanoBananaTester.runAllTests();
      setTestResults(results);
    } catch (error) {
      console.error('Test execution failed:', error);
      setTestResults([{
        testName: 'Test Execution',
        passed: false,
        message: `Failed to run tests: ${error instanceof Error ? error.message : 'Unknown error'}`,
        details: { error }
      }]);
    } finally {
      setIsRunning(false);
    }
  };

  const getServiceStatus = () => {
    return nanoBananaService.getServiceStatus();
  };

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <h1 className="text-3xl font-bold mb-6">NanoBanana Service Test</h1>
      
      <div className="grid gap-6">
        {/* Service Status */}
        <div className="bg-gray-100 p-4 rounded-lg">
          <h2 className="text-xl font-semibold mb-3">Service Status</h2>
          <pre className="bg-white p-3 rounded text-sm overflow-auto">
            {JSON.stringify(getServiceStatus(), null, 2)}
          </pre>
        </div>

        {/* Test Controls */}
        <div className="bg-blue-50 p-4 rounded-lg">
          <h2 className="text-xl font-semibold mb-3">Run Tests</h2>
          <button
            onClick={runTests}
            disabled={isRunning}
            className="bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 text-white px-4 py-2 rounded"
          >
            {isRunning ? 'Running Tests...' : 'Run All Tests'}
          </button>
        </div>

        {/* Test Results */}
        {testResults.length > 0 && (
          <div className="bg-white border rounded-lg p-4">
            <h2 className="text-xl font-semibold mb-3">Test Results</h2>
            <div className="space-y-3">
              {testResults.map((result, index) => (
                <div key={index} className={`p-3 rounded ${
                  result.passed ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'
                } border`}>
                  <div className="flex items-center gap-2 mb-2">
                    <span className={`text-lg ${result.passed ? 'text-green-600' : 'text-red-600'}`}>
                      {result.passed ? '✅' : '❌'}
                    </span>
                    <span className="font-medium">{result.testName}</span>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">{result.message}</p>
                  {result.details && (
                    <details className="text-xs">
                      <summary className="cursor-pointer text-gray-500 hover:text-gray-700">
                        Show Details
                      </summary>
                      <pre className="mt-2 bg-gray-100 p-2 rounded overflow-auto">
                        {JSON.stringify(result.details, null, 2)}
                      </pre>
                    </details>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Instructions */}
        <div className="bg-yellow-50 p-4 rounded-lg">
          <h2 className="text-xl font-semibold mb-3">What This Test Does</h2>
          <ul className="list-disc list-inside space-y-2 text-sm">
            <li><strong>Configuration Test:</strong> Verifies that the service correctly detects when it's not configured</li>
            <li><strong>Fallback Test:</strong> Tests that the service returns a fallback response instead of throwing errors</li>
            <li><strong>Error Handling Test:</strong> Ensures the service handles errors gracefully</li>
          </ul>
          <p className="mt-3 text-sm text-gray-600">
            The "Failed to fetch" error should no longer occur because the service now checks configuration 
            before making API calls and provides proper fallback responses.
          </p>
        </div>
      </div>
    </div>
  );
}










