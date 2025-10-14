'use client';

import { useState } from 'react';
import { apiClient } from '@/lib/api-client';

export default function TestAPIStatusPage() {
  const [status, setStatus] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);

  const checkAPIStatus = async () => {
    setIsLoading(true);
    try {
      // Test the AI poster service status
      const response = await apiClient.get('/api/ai/ai-poster/status/');
      setStatus(response);
    } catch (error) {
      setStatus({ error: error instanceof Error ? error.message : 'Unknown error' });
    } finally {
      setIsLoading(false);
    }
  };

  const testImageGeneration = async () => {
    setIsLoading(true);
    try {
      const response = await apiClient.post('/api/ai/ai-poster/generate_poster/', {
        prompt: 'A beautiful silk saree for festive occasions',
        aspect_ratio: '1:1'
      });
      setStatus(response);
    } catch (error) {
      setStatus({ error: error instanceof Error ? error.message : 'Unknown error' });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <h1 className="text-3xl font-bold mb-6">API Status Test</h1>
      
      <div className="grid gap-6">
        {/* API Status Check */}
        <div className="bg-blue-50 p-4 rounded-lg">
          <h2 className="text-xl font-semibold mb-3">Check AI Service Status</h2>
          <button
            onClick={checkAPIStatus}
            disabled={isLoading}
            className="bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 text-white px-4 py-2 rounded"
          >
            {isLoading ? 'Checking...' : 'Check Status'}
          </button>
        </div>

        {/* Test Image Generation */}
        <div className="bg-green-50 p-4 rounded-lg">
          <h2 className="text-xl font-semibold mb-3">Test Image Generation</h2>
          <button
            onClick={testImageGeneration}
            disabled={isLoading}
            className="bg-green-500 hover:bg-green-600 disabled:bg-gray-400 text-white px-4 py-2 rounded"
          >
            {isLoading ? 'Testing...' : 'Test Generation'}
          </button>
        </div>

        {/* Results */}
        {status && (
          <div className="bg-white border rounded-lg p-4">
            <h2 className="text-xl font-semibold mb-3">Results</h2>
            <pre className="bg-gray-100 p-3 rounded text-sm overflow-auto">
              {JSON.stringify(status, null, 2)}
            </pre>
          </div>
        )}

        {/* Instructions */}
        <div className="bg-yellow-50 p-4 rounded-lg">
          <h2 className="text-xl font-semibold mb-3">What This Test Does</h2>
          <ul className="list-disc list-inside space-y-2 text-sm">
            <li><strong>Status Check:</strong> Verifies if the AI poster service is available and configured</li>
            <li><strong>Generation Test:</strong> Attempts to generate an image to test the full workflow</li>
            <li><strong>Debug Info:</strong> Shows detailed response data for troubleshooting</li>
          </ul>
          <p className="mt-3 text-sm text-gray-600">
            If the service is not available, check that GEMINI_API_KEY is set in your backend environment.
          </p>
        </div>
      </div>
    </div>
  );
}





