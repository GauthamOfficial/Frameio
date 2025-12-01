/**
 * AI Service Error Handling and Fallback System
 * Provides robust error handling, retry logic, and fallback mechanisms
 */

export interface ErrorContext {
  service: string;
  operation: string;
  timestamp: string;
  userAgent?: string;
  userId?: string;
}

export interface RetryConfig {
  maxAttempts: number;
  baseDelay: number;
  maxDelay: number;
  backoffMultiplier: number;
}

export interface FallbackConfig {
  enabled: boolean;
  fallbackService?: string;
  staticAssets?: string[];
  userNotification?: boolean;
}

export class AIError extends Error {
  public readonly code: string;
  public readonly context: ErrorContext;
  public readonly retryable: boolean;
  public readonly fallbackAvailable: boolean;

  constructor(
    message: string,
    code: string,
    context: ErrorContext,
    retryable: boolean = false,
    fallbackAvailable: boolean = false
  ) {
    super(message);
    this.name = 'AIError';
    this.code = code;
    this.context = context;
    this.retryable = retryable;
    this.fallbackAvailable = fallbackAvailable;
  }
}

export class AIErrorHandler {
  private static instance: AIErrorHandler;
  private errorLog: Array<{ error: AIError; timestamp: string }> = [];
  private retryConfig: RetryConfig = {
    maxAttempts: 3,
    baseDelay: 1000,
    maxDelay: 10000,
    backoffMultiplier: 2,
  };
  private fallbackConfig: FallbackConfig = {
    enabled: true,
    userNotification: true,
    staticAssets: [
      'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=512&h=512&fit=crop',
      'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=512&h=512&fit=crop',
      'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=512&h=512&fit=crop',
    ],
  };

  private constructor() {}

  public static getInstance(): AIErrorHandler {
    if (!AIErrorHandler.instance) {
      AIErrorHandler.instance = new AIErrorHandler();
    }
    return AIErrorHandler.instance;
  }

  /**
   * Execute operation with retry logic and fallback
   */
  public async executeWithRetry<T>(
    operation: () => Promise<T>,
    context: ErrorContext,
    fallbackOperation?: () => Promise<T>
  ): Promise<T> {
    let lastError: AIError | null = null;

    for (let attempt = 1; attempt <= this.retryConfig.maxAttempts; attempt++) {
      try {
        const result = await operation();
        return result;
      } catch (error) {
        lastError = this.createAIError(error, { ...context, attempt: attempt.toString() } as ErrorContext);
        this.logError(lastError);

        // If not retryable or last attempt, break
        if (!lastError.retryable || attempt === this.retryConfig.maxAttempts) {
          break;
        }

        // Wait before retry
        const delay = Math.min(
          this.retryConfig.baseDelay * Math.pow(this.retryConfig.backoffMultiplier, attempt - 1),
          this.retryConfig.maxDelay
        );
        await this.delay(delay);
      }
    }

    // Try fallback if available
    if (fallbackOperation && this.fallbackConfig.enabled) {
      try {
        console.log(`Attempting fallback for ${context.service}:${context.operation}`);
        return await fallbackOperation();
      } catch (fallbackError) {
        const fallbackAIError = this.createAIError(fallbackError, {
          ...context,
          service: 'fallback',
        });
        this.logError(fallbackAIError);
        throw fallbackAIError;
      }
    }

    throw lastError || new AIError(
      'Unknown error occurred',
      'UNKNOWN_ERROR',
      context,
      false,
      false
    );
  }

  /**
   * Create AIError from any error
   */
  private createAIError(error: unknown, context: ErrorContext): AIError {
    const errorCode = this.categorizeError(error);
    const retryable = this.isRetryableError(error);
    const fallbackAvailable = this.fallbackConfig.enabled;

    const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred'
    return new AIError(
      errorMessage,
      errorCode,
      context,
      retryable,
      fallbackAvailable
    );
  }

  /**
   * Categorize error type
   */
  private categorizeError(error: unknown): string {
    const errorObj = error as { name?: string; message?: string }
    if (errorObj.name === 'AIError') {
      return (error as { code: string }).code;
    }

    if (errorObj.message?.includes('network') || errorObj.message?.includes('fetch')) {
      return 'NETWORK_ERROR';
    }

    if (errorObj.message?.includes('timeout')) {
      return 'TIMEOUT_ERROR';
    }

    if (errorObj.message?.includes('unauthorized') || errorObj.message?.includes('401')) {
      return 'AUTH_ERROR';
    }

    if (errorObj.message?.includes('rate limit') || errorObj.message?.includes('429')) {
      return 'RATE_LIMIT_ERROR';
    }

    if (errorObj.message?.includes('server') || errorObj.message?.includes('5')) {
      return 'SERVER_ERROR';
    }

    if (errorObj.message?.includes('quota') || errorObj.message?.includes('limit')) {
      return 'QUOTA_ERROR';
    }

    return 'UNKNOWN_ERROR';
  }

  /**
   * Determine if error is retryable
   */
  private isRetryableError(error: unknown): boolean {
    const retryableCodes = [
      'NETWORK_ERROR',
      'TIMEOUT_ERROR',
      'SERVER_ERROR',
      'RATE_LIMIT_ERROR',
    ];

    const errorCode = this.categorizeError(error);
    return retryableCodes.includes(errorCode);
  }

  /**
   * Log error for debugging
   */
  private logError(error: AIError): void {
    this.errorLog.push({
      error,
      timestamp: new Date().toISOString(),
    });

    // Keep only last 100 errors
    if (this.errorLog.length > 100) {
      this.errorLog = this.errorLog.slice(-100);
    }

    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('AI Error:', {
        code: error.code,
        message: error.message,
        context: error.context,
        retryable: error.retryable,
        fallbackAvailable: error.fallbackAvailable,
      });
    }
  }

  /**
   * Get fallback asset
   */
  public getFallbackAsset(index: number = 0): string {
    const assets = this.fallbackConfig.staticAssets || [];
    return assets[index % assets.length];
  }

  /**
   * Get error statistics
   */
  public getErrorStats(): {
    totalErrors: number;
    errorsByCode: Record<string, number>;
    errorsByService: Record<string, number>;
    recentErrors: Array<{ error: AIError; timestamp: string }>;
  } {
    const errorsByCode: Record<string, number> = {};
    const errorsByService: Record<string, number> = {};

    this.errorLog.forEach(({ error }) => {
      errorsByCode[error.code] = (errorsByCode[error.code] || 0) + 1;
      errorsByService[error.context.service] = (errorsByService[error.context.service] || 0) + 1;
    });

    return {
      totalErrors: this.errorLog.length,
      errorsByCode,
      errorsByService,
      recentErrors: this.errorLog.slice(-10),
    };
  }

  /**
   * Clear error log
   */
  public clearErrorLog(): void {
    this.errorLog = [];
  }

  /**
   * Update retry configuration
   */
  public updateRetryConfig(config: Partial<RetryConfig>): void {
    this.retryConfig = { ...this.retryConfig, ...config };
  }

  /**
   * Update fallback configuration
   */
  public updateFallbackConfig(config: Partial<FallbackConfig>): void {
    this.fallbackConfig = { ...this.fallbackConfig, ...config };
  }

  /**
   * Utility delay function
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Get user-friendly error message
   */
  public getUserFriendlyMessage(error: AIError): string {
    const messages: Record<string, string> = {
      NETWORK_ERROR: 'Network connection issue. Please check your internet connection and try again.',
      TIMEOUT_ERROR: 'Request timed out. The service might be busy. Please try again.',
      AUTH_ERROR: 'Authentication failed. Please check your API key and try again.',
      RATE_LIMIT_ERROR: 'Too many requests. Please wait a moment and try again.',
      SERVER_ERROR: 'Server error occurred. Please try again later.',
      QUOTA_ERROR: 'API quota exceeded. Please upgrade your plan or try again later.',
      UNKNOWN_ERROR: 'An unexpected error occurred. Please try again.',
    };

    return messages[error.code] || messages.UNKNOWN_ERROR;
  }

  /**
   * Check if service is healthy
   */
  public async checkServiceHealth(serviceUrl: string): Promise<boolean> {
    try {
      const response = await fetch(serviceUrl, {
        method: 'HEAD',
        timeout: 5000,
      } as RequestInit & { timeout?: number });
      return response.ok;
    } catch {
      return false;
    }
  }
}

// Export singleton instance
export const aiErrorHandler = AIErrorHandler.getInstance();

// Export utility functions
export const withErrorHandling = async <T>(
  operation: () => Promise<T>,
  context: ErrorContext,
  fallbackOperation?: () => Promise<T>
): Promise<T> => {
  return aiErrorHandler.executeWithRetry(operation, context, fallbackOperation);
};

export const createErrorContext = (
  service: string,
  operation: string,
  userId?: string
): ErrorContext => ({
  service,
  operation,
  timestamp: new Date().toISOString(),
  userAgent: typeof window !== 'undefined' ? window.navigator.userAgent : undefined,
  userId,
});
