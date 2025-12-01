/**
 * Clerk Timeout Handler
 * Comprehensive utility to handle Clerk loading timeout issues
 */

export class ClerkTimeoutHandler {
  private static instance: ClerkTimeoutHandler;
  private retryCount = 0;
  private maxRetries = 3;
  private timeoutDuration = 8000; // 8 seconds

  private constructor() {
    this.setupGlobalErrorHandlers();
  }

  public static getInstance(): ClerkTimeoutHandler {
    if (!ClerkTimeoutHandler.instance) {
      ClerkTimeoutHandler.instance = new ClerkTimeoutHandler();
    }
    return ClerkTimeoutHandler.instance;
  }

  private setupGlobalErrorHandlers(): void {
    if (typeof window === 'undefined') return;

    // Handle Clerk timeout errors
    const handleClerkError = (event: ErrorEvent) => {
      if (this.isClerkTimeoutError(event.error)) {
        console.warn('Clerk timeout error detected:', event.error);
        this.handleTimeout();
      }
    };

    // Handle unhandled promise rejections
    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      if (this.isClerkTimeoutError(event.reason)) {
        console.warn('Clerk timeout promise rejection detected:', event.reason);
        this.handleTimeout();
        event.preventDefault();
      }
    };

    window.addEventListener('error', handleClerkError);
    window.addEventListener('unhandledrejection', handleUnhandledRejection);
  }

  private isClerkTimeoutError(error: unknown): boolean {
    const errorObj = error as { code?: string; message?: string; name?: string; stack?: string }
    return (
      errorObj.code === 'failed_to_load_clerk_js_timeout' ||
      Boolean(errorObj.message?.includes('failed_to_load_clerk_js_timeout')) ||
      errorObj.name === 'ClerkRuntimeError' ||
      Boolean(errorObj.stack?.includes('clerk'))
    );
  }

  private async clearCaches(): Promise<void> {
    try {
      // Clear browser cache
      if ('caches' in window) {
        const cacheNames = await caches.keys();
        await Promise.all(
          cacheNames.map(name => {
            if (name.includes('clerk') || name.includes('chunk')) {
              return caches.delete(name);
            }
          })
        );
      }

      // Clear service worker
      if ('serviceWorker' in navigator) {
        const registrations = await navigator.serviceWorker.getRegistrations();
        await Promise.all(
          registrations.map(registration => registration.unregister())
        );
      }

      // Clear localStorage items related to Clerk
      const keysToRemove = [];
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && (key.includes('clerk') || key.includes('__clerk'))) {
          keysToRemove.push(key);
        }
      }
      keysToRemove.forEach(key => localStorage.removeItem(key));

      // Clear sessionStorage items related to Clerk
      const sessionKeysToRemove = [];
      for (let i = 0; i < sessionStorage.length; i++) {
        const key = sessionStorage.key(i);
        if (key && (key.includes('clerk') || key.includes('__clerk'))) {
          sessionKeysToRemove.push(key);
        }
      }
      sessionKeysToRemove.forEach(key => sessionStorage.removeItem(key));

    } catch (error) {
      console.warn('Error clearing caches:', error);
    }
  }

  private async handleTimeout(): Promise<void> {
    if (this.retryCount >= this.maxRetries) {
      console.error('Max retry attempts reached for Clerk timeout');
      // Show a user-friendly error message instead of infinite retries
      this.showFallbackError();
      return;
    }

    this.retryCount++;
    console.log(`Clerk timeout recovery attempt ${this.retryCount}/${this.maxRetries}`);

    try {
      await this.clearCaches();
      
      // For the first retry, try to reload the Clerk script
      if (this.retryCount === 1) {
        await this.reloadClerkScript();
      } else {
        // For subsequent retries, reload the page
        setTimeout(() => {
          window.location.reload();
        }, 1000);
      }
    } catch (error) {
      console.error('Error during Clerk timeout recovery:', error);
      // If recovery fails, show fallback error
      this.showFallbackError();
    }
  }

  private async reloadClerkScript(): Promise<void> {
    try {
      // Remove existing Clerk script tags
      const existingScripts = document.querySelectorAll('script[src*="clerk"]');
      existingScripts.forEach(script => script.remove());

      // Clear any Clerk-related modules from the module cache
      if (typeof window !== 'undefined' && (window as Window & { __webpack_require__?: { cache?: Record<string, unknown> } }).__webpack_require__) {
        const webpackRequire = (window as unknown as Window & { __webpack_require__: { cache?: Record<string, unknown> } }).__webpack_require__;
        const cache = webpackRequire.cache;
        if (cache) {
          Object.keys(cache).forEach(key => {
            if (key.includes('clerk')) {
              delete cache[key];
            }
          });
        }
      }

      // Wait a moment before reloading
      setTimeout(() => {
        window.location.reload();
      }, 2000);
    } catch (error) {
      console.error('Error reloading Clerk script:', error);
      setTimeout(() => {
        window.location.reload();
      }, 1000);
    }
  }

  private showFallbackError(): void {
    // Create a fallback error message
    const errorDiv = document.createElement('div');
    errorDiv.innerHTML = `
      <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 9999; display: flex; align-items: center; justify-content: center;">
        <div style="background: white; padding: 2rem; border-radius: 8px; max-width: 400px; text-align: center;">
          <h2 style="color: #dc2626; margin-bottom: 1rem;">Authentication Service Unavailable</h2>
          <p style="color: #374151; margin-bottom: 1rem;">We're experiencing issues with our authentication service. Please try refreshing the page.</p>
          <button onclick="window.location.reload()" style="background: #3b82f6; color: white; padding: 0.5rem 1rem; border: none; border-radius: 4px; cursor: pointer;">
            Refresh Page
          </button>
        </div>
      </div>
    `;
    document.body.appendChild(errorDiv);
  }

  public resetRetryCount(): void {
    this.retryCount = 0;
  }

  public getRetryCount(): number {
    return this.retryCount;
  }

  public setMaxRetries(maxRetries: number): void {
    this.maxRetries = maxRetries;
  }

  public setTimeoutDuration(duration: number): void {
    this.timeoutDuration = duration;
  }
}

// Export singleton instance
export const clerkTimeoutHandler = ClerkTimeoutHandler.getInstance();

// Export utility functions
export const handleClerkTimeout = () => {
  clerkTimeoutHandler['handleTimeout']();
};

export const resetClerkTimeout = () => {
  clerkTimeoutHandler.resetRetryCount();
};