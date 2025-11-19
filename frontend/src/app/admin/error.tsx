'use client';

import { useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { AlertTriangle, RefreshCcw } from 'lucide-react';

export default function AdminError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error('Admin error:', error);
  }, [error]);

  return (
    <div className="flex h-full items-center justify-center p-6">
      <Card className="max-w-md">
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className="rounded-full bg-red-100 p-2">
              <AlertTriangle className="h-6 w-6 text-red-600" />
            </div>
            <div>
              <CardTitle>Something went wrong!</CardTitle>
              <CardDescription>
                An error occurred while loading this page
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="rounded-md bg-gray-50 p-4">
              <p className="text-sm font-mono text-gray-700">
                {error.message || 'Unknown error'}
              </p>
            </div>
            <div className="flex gap-2">
              <Button onClick={reset} className="flex-1">
                <RefreshCcw className="mr-2 h-4 w-4" />
                Try Again
              </Button>
              <Button
                variant="outline"
                onClick={() => window.location.href = '/admin'}
                className="flex-1"
              >
                Go to Dashboard
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}







