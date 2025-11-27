'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function SimpleTestPage() {
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const testAPI = async () => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      console.log('🧪 Testing API directly...');
      
      // Test 1: Status check
      console.log('1️⃣ Testing status endpoint...');
      const statusResponse = await fetch('http://localhost:8000/api/ai/ai-poster/status/', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!statusResponse.ok) {
        throw new Error(`Status check failed: ${statusResponse.status}`);
      }

      const statusData = await statusResponse.json();
      console.log('✅ Status check passed:', statusData);

      // Test 2: Generate image
      console.log('2️⃣ Testing image generation...');
      const generateResponse = await fetch('http://localhost:8000/api/ai/ai-poster/generate_poster/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: 'Simple test image for debugging',
          aspect_ratio: '1:1'
        })
      });

      if (!generateResponse.ok) {
        const errorText = await generateResponse.text();
        throw new Error(`Generation failed: ${generateResponse.status} - ${errorText}`);
      }

      const generateData = await generateResponse.json();
      console.log('✅ Generation successful:', generateData);

      setResult({
        status: statusData,
        generation: generateData,
        imageUrl: generateData.image_url.startsWith('http') ? generateData.image_url : `http://localhost:8000${generateData.image_url}`
      });

    } catch (err) {
      console.error('❌ Test failed:', err);
      setError(err instanceof Error ? err.message : 'Test failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-center mb-2">Simple API Test</h1>
        <p className="text-center text-gray-600">Direct API test to verify everything is working</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Test Controls</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button 
              onClick={testAPI} 
              disabled={isLoading}
              className="w-full"
            >
              {isLoading ? 'Testing...' : 'Test API Directly'}
            </Button>

            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-md text-red-700">
                <strong>Error:</strong> {error}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Test Results</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading && (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
                <p>Testing API...</p>
              </div>
            )}

            {result && (
              <div className="space-y-4">
                <div>
                  <h3 className="font-semibold mb-2">Status Check:</h3>
                  <div className="bg-green-50 p-2 rounded text-sm">
                    ✅ {result.status.message}
                  </div>
                </div>

                <div>
                  <h3 className="font-semibold mb-2">Generation Result:</h3>
                  <div className="bg-blue-50 p-2 rounded text-sm">
                    ✅ {result.generation.message}
                  </div>
                </div>

                {result.imageUrl && (
                  <div>
                    <h3 className="font-semibold mb-2">Generated Image:</h3>
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={result.imageUrl as string}
                      alt="Generated test image"
                      className="w-full h-auto rounded border"
                      onError={(e) => {
                        console.error('Image load error:', e);
                      }}
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      URL: {result.imageUrl}
                    </p>
                  </div>
                )}
              </div>
            )}

            {!isLoading && !result && (
              <div className="text-center py-8 text-gray-500">
                Click &quot;Test API Directly&quot; to start
              </div>
            )}
          </CardContent>
        </Card>
      </div>

    </div>
  );
}
