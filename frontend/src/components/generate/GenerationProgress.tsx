'use client';

import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Loader2 } from 'lucide-react';

interface GenerationProgressProps {
  jobId?: string;
  progress?: number;
  status?: string;
  message?: string;
}

export function GenerationProgress({ 
  jobId, 
  progress = 0, 
  status = 'generating',
  message 
}: GenerationProgressProps) {
  if (!jobId && status !== 'generating') {
    return null;
  }

  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-center gap-3">
          <Loader2 className="h-5 w-5 animate-spin text-primary" />
          <div className="flex-1">
            <p className="text-sm font-medium">
              {message || 'Generating your poster...'}
            </p>
            {progress > 0 && (
              <div className="mt-2">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-primary h-2 rounded-full transition-all duration-300"
                    style={{ width: `${progress}%` }}
                  />
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  {progress}% complete
                </p>
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

