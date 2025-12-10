'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/hooks/useAuth';

interface AuthLoadingProps {
  children: React.ReactNode;
}

export function AuthLoading({ children }: AuthLoadingProps) {
  const [isLoading, setIsLoading] = useState(true);
  const { isLoaded } = useAuth();

  useEffect(() => {
    if (isLoaded) {
      setIsLoading(false);
    }
  }, [isLoaded]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-foreground">Loading Frameio...</p>
          <p className="text-sm text-muted-foreground mt-2">Please wait while we initialize your session</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}

