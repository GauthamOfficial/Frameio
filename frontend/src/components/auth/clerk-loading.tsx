'use client';

import { useEffect, useState, useCallback } from 'react';
import { useAuth } from '@clerk/nextjs';
import { clerkTimeoutHandler } from '@/lib/clerk-timeout-handler';

interface ClerkLoadingProps {
  children: React.ReactNode;
}

export function ClerkLoading({ children }: ClerkLoadingProps) {
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);
  const [retryCount, setRetryCount] = useState(0);
  const [errorMessage, setErrorMessage] = useState('');
  const { isLoaded } = useAuth();

  const handleRetry = useCallback(() => {
    console.log('Attempting to recover from Clerk timeout...');
    setRetryCount(clerkTimeoutHandler.getRetryCount());
    setHasError(false);
    setErrorMessage('');
    
    // Use the centralized timeout handler
    clerkTimeoutHandler['handleTimeout']();
  }, []);

  const handleManualReload = useCallback(() => {
    console.log('Manual reload triggered');
    window.location.reload();
  }, []);

  useEffect(() => {
    // Set a timeout to handle Clerk loading issues
    const timeout = setTimeout(() => {
      if (!isLoaded) {
        console.warn('Clerk loading timeout - attempting recovery');
        setHasError(true);
        setErrorMessage('Authentication service is taking longer than expected to load. This might be due to network issues or server problems.');
        handleRetry();
      }
    }, 10000); // Increased timeout to 10 seconds for better reliability

    if (isLoaded) {
      setIsLoading(false);
      setHasError(false);
      setErrorMessage('');
      clearTimeout(timeout);
    }

    return () => clearTimeout(timeout);
  }, [isLoaded, handleRetry]);

  // Handle Clerk timeout errors globally
  useEffect(() => {
    const handleClerkError = (event: ErrorEvent) => {
      if (
        event.error?.code === 'failed_to_load_clerk_js_timeout' ||
        event.message?.includes('failed_to_load_clerk_js_timeout') ||
        event.error?.name === 'ClerkRuntimeError'
      ) {
        console.warn('Clerk timeout error detected globally:', event.error);
        setHasError(true);
        setErrorMessage('Authentication service failed to load. This is usually a temporary issue.');
        handleRetry();
      }
    };

    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      if (
        event.reason?.code === 'failed_to_load_clerk_js_timeout' ||
        event.reason?.message?.includes('failed_to_load_clerk_js_timeout') ||
        event.reason?.name === 'ClerkRuntimeError'
      ) {
        console.warn('Clerk timeout promise rejection detected:', event.reason);
        setHasError(true);
        setErrorMessage('Authentication service encountered an error while loading.');
        handleRetry();
        event.preventDefault();
      }
    };

    window.addEventListener('error', handleClerkError);
    window.addEventListener('unhandledrejection', handleUnhandledRejection);

    return () => {
      window.removeEventListener('error', handleClerkError);
      window.removeEventListener('unhandledrejection', handleUnhandledRejection);
    };
  }, [handleRetry]);

  if (hasError) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center max-w-md mx-auto p-6">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Authentication Error</h2>
          <p className="text-gray-600 mb-4">
            {errorMessage || 'Authentication service is having trouble loading.'}
          </p>
          <p className="text-sm text-gray-500 mb-4">
            {retryCount > 0 ? `Retry attempt ${retryCount}/3` : 'This is usually a temporary issue.'}
          </p>
          <div className="space-y-2">
            <button
              onClick={handleRetry}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              Retry Loading
            </button>
            <button
              onClick={handleManualReload}
              className="w-full px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
            >
              Reload Page
            </button>
          </div>
          <p className="text-xs text-gray-400 mt-4">
            If the problem persists, please check your internet connection or try again later.
          </p>
        </div>
      </div>
    );
  }

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
