'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import { apiPost, getFullUrl } from '@/utils/api';

export default function TestPosterGenerationPage() {
  const [isGenerating, setIsGenerating] = useState(false);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<string | null>(null);

  const testGeneration = async () => {
    setIsGenerating(true);
    setError(null);
    setResult(null);

    try {
      console.log('🧪 Testing poster generation...');
      
      const data = await apiPost<{ success: boolean; image_url?: string; message?: string; filename?: string }>(
        '/api/ai/ai-poster/generate_poster/',
        {
          prompt: 'Beautiful silk saree for Diwali celebrations with gold accents and red colors, high-quality textile poster design',
          aspect_ratio: '4:5'
        }
      );
      console.log('✅ Generation successful:', data);
      
      setResult(data);
      setError(null);
    } catch (err) {
      console.error('❌ Generation failed:', err);
      setError(err instanceof Error ? err.message : 'Generation failed');
      setResult(null);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-center mb-2">Test Poster Generation</h1>
        <p className="text-center text-gray-600">Direct API test for Gemini 2.5 Flash image generation</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Test Controls */}
        <Card>
          <CardHeader>
            <CardTitle>Test Controls</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <h3 className="font-semibold">Test Prompt:</h3>
              <p className="text-sm text-gray-600 bg-gray-50 p-2 rounded">
                &quot;Beautiful silk saree for Diwali celebrations with gold accents and red colors, high-quality textile poster design&quot;
              </p>
            </div>

            <div className="space-y-2">
              <h3 className="font-semibold">Aspect Ratio:</h3>
              <p className="text-sm text-gray-600">4:5 (Portrait)</p>
            </div>

            <Button 
              onClick={testGeneration} 
              disabled={isGenerating}
              className="w-full"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Testing Generation...
                </>
              ) : (
                'Test Poster Generation'
              )}
            </Button>

            {error && (
              <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-md text-red-700">
                <AlertCircle className="h-4 w-4" />
                <div>
                  <p className="font-semibold">Error:</p>
                  <p className="text-sm">{error}</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Results */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              Test Results
              {result && typeof result.success === 'boolean' && result.success && <CheckCircle className="h-4 w-4 text-green-500" />}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isGenerating && (
              <div className="flex flex-col items-center justify-center h-64 bg-gray-50 rounded-md">
                <Loader2 className="h-8 w-8 animate-spin text-blue-500 mb-4" />
                <p className="text-gray-600">Testing generation...</p>
                <p className="text-sm text-gray-500 mt-2">This may take 60-120 seconds</p>
              </div>
            )}

            {(() => {
              const success = result && typeof result.success === 'boolean' ? result.success : false;
              const imageUrl = result && typeof result.image_url === 'string' ? result.image_url : null;
              const message = result && typeof result.message === 'string' ? result.message : '';
              const filename = result && typeof result.filename === 'string' ? result.filename : '';
              
              return success && imageUrl && (
                <div className="space-y-4">
                  <div className="relative">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={imageUrl.startsWith('http') ? imageUrl : getFullUrl(imageUrl)}
                      alt="Generated poster"
                      className="w-full h-auto rounded-md border"
                      onError={(e) => {
                        console.error('Image load error:', e);
                        console.error('Image URL:', imageUrl);
                        setError('Failed to load generated image. The image URL may be invalid.');
                      }}
                    />
                  </div>
                  
                  <div className="space-y-2 text-sm">
                    <div>
                      <span className="font-semibold">Success:</span> {success ? '✅ Yes' : '❌ No'}
                    </div>
                    <div>
                      <span className="font-semibold">Message:</span> {message}
                    </div>
                    <div>
                      <span className="font-semibold">Filename:</span> {filename}
                    </div>
                    <div>
                      <span className="font-semibold">Image URL:</span> 
                      <br />
                      <code className="text-xs break-all bg-gray-100 p-1 rounded">{imageUrl}</code>
                    </div>
                  </div>
                </div>
              );
            })()}

            {!isGenerating && !result && (
              <div className="flex flex-col items-center justify-center h-64 bg-gray-50 rounded-md">
                <div className="text-center">
                  <div className="text-4xl mb-4">🧪</div>
                  <p className="text-gray-600">Test results will appear here</p>
                  <p className="text-sm text-gray-500 mt-2">Click &quot;Test Poster Generation&quot; to start</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Raw Response */}
      {result && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle className="text-sm">Raw API Response</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="bg-gray-100 p-3 rounded text-xs overflow-auto max-h-64">
              {JSON.stringify(result, null, 2)}
            </pre>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
