'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2, Download, RefreshCw, AlertCircle, CheckCircle } from 'lucide-react';
import { useUser, useAuth } from '@clerk/nextjs';

interface GenerationResult {
  success: boolean;
  message?: string;
  image_path?: string;
  image_url?: string;
  filename?: string;
  error?: string;
}

export default function AIPosterGeneratorPage() {
  // Authentication
  const { user } = useUser();
  const { getToken } = useAuth();
  
  const [prompt, setPrompt] = useState('');
  const [aspectRatio, setAspectRatio] = useState('4:5');
  const [isGenerating, setIsGenerating] = useState(false);
  const [result, setResult] = useState<GenerationResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const generatePoster = async () => {
    if (!prompt.trim()) {
      setError('Please enter a prompt');
      return;
    }

    setIsGenerating(true);
    setError(null);
    setResult(null);

    try {
      console.log('🚀 Starting poster generation...');
      console.log('Prompt:', prompt);
      console.log('Aspect Ratio:', aspectRatio);
      console.log('User authenticated:', !!user);

      // Get authentication token
      const token = await getToken();
      const authHeaders = token ? { 'Authorization': `Bearer ${token}` } : {};

      const response = await fetch('http://localhost:8000/api/ai/ai-poster/generate_poster/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...authHeaders
        },
        body: JSON.stringify({
          prompt: prompt,
          aspect_ratio: aspectRatio
        })
      });

      console.log('Response status:', response.status);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP ${response.status}`);
      }

      const data = await response.json();
      console.log('Generation result:', data);

      if (data.success) {
        setResult(data);
        setError(null);
        console.log('✅ Poster generated successfully!');
        console.log('Image URL:', data.image_url);
        console.log('Image Path:', data.image_path);
        console.log('Full Image URL:', data.image_url.startsWith('http') ? data.image_url : `http://localhost:8000${data.image_url}`);
      } else {
        throw new Error(data.error || 'Generation failed');
      }
    } catch (err) {
      console.error('❌ Generation failed:', err);
      setError(err instanceof Error ? err.message : 'Generation failed');
      setResult(null);
    } finally {
      setIsGenerating(false);
    }
  };

  const downloadImage = () => {
    if (result?.image_url) {
      const link = document.createElement('a');
      link.href = result.image_url;
      link.download = result.filename || 'generated-poster.png';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  return (
    <div className="container mx-auto p-6 max-w-6xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-center mb-2">AI Poster Generator</h1>
        <p className="text-center text-gray-600">Generate beautiful textile posters using Gemini 2.5 Flash</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <span>Generate Poster</span>
              {isGenerating && <Loader2 className="h-4 w-4 animate-spin" />}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="prompt">Describe your poster</Label>
              <Input
                id="prompt"
                placeholder="e.g., Beautiful silk saree for Diwali celebrations with gold accents"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                disabled={isGenerating}
                className="mt-1"
              />
            </div>

            <div>
              <Label htmlFor="aspect-ratio">Aspect Ratio</Label>
              <select
                id="aspect-ratio"
                value={aspectRatio}
                onChange={(e) => setAspectRatio(e.target.value)}
                disabled={isGenerating}
                className="mt-1 w-full p-2 border border-gray-300 rounded-md"
              >
                <option value="1:1">Square (1:1)</option>
                <option value="4:5">Portrait (4:5)</option>
                <option value="16:9">Widescreen (16:9)</option>
              </select>
            </div>

            <Button 
              onClick={generatePoster} 
              disabled={isGenerating || !prompt.trim()}
              className="w-full"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Generate Poster
                </>
              )}
            </Button>

            {error && (
              <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-md text-red-700">
                <AlertCircle className="h-4 w-4" />
                <span className="text-sm">{error}</span>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Result Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              Generated Poster
              {result?.success && <CheckCircle className="h-4 w-4 text-green-500" />}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isGenerating && (
              <div className="flex flex-col items-center justify-center h-64 bg-gray-50 rounded-md">
                <Loader2 className="h-8 w-8 animate-spin text-blue-500 mb-4" />
                <p className="text-gray-600">Generating your poster...</p>
                <p className="text-sm text-gray-500 mt-2">This may take 60-120 seconds</p>
              </div>
            )}

            {result?.success && result.image_url && (
              <div className="space-y-4">
                <div className="relative">
                  <img
                    src={result.image_url.startsWith('http') ? result.image_url : `http://localhost:8000${result.image_url}`}
                    alt="Generated poster"
                    className="w-full h-auto rounded-md border"
                    onError={(e) => {
                      console.error('Image load error:', e);
                      console.error('Image URL:', result.image_url);
                      setError('Failed to load generated image. Please try again.');
                    }}
                  />
                </div>
                
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <span>Filename:</span>
                    <span className="font-mono">{result.filename}</span>
                  </div>
                  
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <span>Path:</span>
                    <span className="font-mono text-xs break-all">{result.image_path}</span>
                  </div>
                </div>

                <Button onClick={downloadImage} className="w-full">
                  <Download className="mr-2 h-4 w-4" />
                  Download Image
                </Button>
              </div>
            )}

            {!isGenerating && !result && (
              <div className="flex flex-col items-center justify-center h-64 bg-gray-50 rounded-md">
                <div className="text-center">
                  <div className="text-4xl mb-4">🎨</div>
                  <p className="text-gray-600">Your generated poster will appear here</p>
                  <p className="text-sm text-gray-500 mt-2">Enter a prompt and click Generate Poster</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

    </div>
  );
}
