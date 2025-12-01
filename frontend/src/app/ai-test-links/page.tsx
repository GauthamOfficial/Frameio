'use client';

import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ExternalLink, TestTube, Image, Settings } from 'lucide-react';

export default function AITestLinksPage() {
  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-center mb-2">AI Poster Generation - Test Pages</h1>
        <p className="text-center text-gray-600">Choose a page to test the AI poster generation functionality</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Test Poster Generation */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TestTube className="h-5 w-5" />
              Test Poster Generation
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-gray-600">
              Direct API test page that generates a poster with a predefined prompt. 
              This is the simplest way to test if the backend is working.
            </p>
            <div className="space-y-2">
              <h4 className="font-semibold">What it does:</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Tests the API directly</li>
                <li>• Uses a predefined prompt</li>
                <li>• Shows raw API response</li>
                <li>• Displays generated image</li>
              </ul>
            </div>
            <Link href="/test-poster-generation">
              <Button className="w-full">
                <ExternalLink className="mr-2 h-4 w-4" />
                Go to Test Page
              </Button>
            </Link>
          </CardContent>
        </Card>

        {/* AI Poster Generator */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Image className="h-5 w-5" aria-label="AI Poster Generator icon" />
              AI Poster Generator
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-gray-600">
              Full-featured poster generator where you can enter your own prompts 
              and customize the generation settings.
            </p>
            <div className="space-y-2">
              <h4 className="font-semibold">What it does:</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Custom prompt input</li>
                <li>• Aspect ratio selection</li>
                <li>• Image download</li>
                <li>• Real-time generation</li>
              </ul>
            </div>
            <Link href="/ai-poster-generator">
              <Button className="w-full">
                <ExternalLink className="mr-2 h-4 w-4" />
                Go to Generator
              </Button>
            </Link>
          </CardContent>
        </Card>

        {/* API Status */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              API Status Check
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-gray-600">
              Check if the AI poster service is available and configured correctly.
            </p>
            <div className="space-y-2">
              <h4 className="font-semibold">What it does:</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Checks service availability</li>
                <li>• Tests API connectivity</li>
                <li>• Shows configuration status</li>
              </ul>
            </div>
            <Link href="/test-api-status">
              <Button className="w-full">
                <ExternalLink className="mr-2 h-4 w-4" />
                Check API Status
              </Button>
            </Link>
          </CardContent>
        </Card>

        {/* Simple Test */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TestTube className="h-5 w-5" />
              Simple API Test
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-gray-600">
              Direct API test that bypasses any caching issues. 
              This is the most reliable way to test the backend.
            </p>
            <div className="space-y-2">
              <h4 className="font-semibold">What it does:</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Tests API status directly</li>
                <li>• Generates a test image</li>
                <li>• Shows the actual image</li>
                <li>• Bypasses any caching issues</li>
              </ul>
            </div>
            <Link href="/simple-test">
              <Button className="w-full">
                <ExternalLink className="mr-2 h-4 w-4" />
                Run Simple Test
              </Button>
            </Link>
          </CardContent>
        </Card>

        {/* Instructions */}
        <Card>
          <CardHeader>
            <CardTitle>How to Use</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <div>
                <h4 className="font-semibold">1. Start with Test Page</h4>
                <p className="text-sm text-gray-600">
                  Use &quot;Test Poster Generation&quot; first to verify the backend is working.
                </p>
              </div>
              <div>
                <h4 className="font-semibold">2. Try the Generator</h4>
                <p className="text-sm text-gray-600">
                  Once the test works, use &quot;AI Poster Generator&quot; for custom prompts.
                </p>
              </div>
              <div>
                <h4 className="font-semibold">3. Check Status</h4>
                <p className="text-sm text-gray-600">
                  If something fails, use &quot;API Status Check&quot; to debug.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-md">
        <h3 className="font-semibold text-blue-800 mb-2">Quick Start Instructions:</h3>
        <ol className="text-sm text-blue-700 space-y-1">
          <li>1. Make sure your backend server is running: <code className="bg-blue-100 px-1 rounded">cd backend && python manage.py runserver 8000</code></li>
          <li>2. Make sure your frontend server is running: <code className="bg-blue-100 px-1 rounded">npm run dev</code></li>
          <li>3. Click &quot;Test Poster Generation&quot; to test the API</li>
          <li>4. If successful, try &quot;AI Poster Generator&quot; for custom prompts</li>
        </ol>
      </div>
    </div>
  );
}
