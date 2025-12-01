/**
 * NanoBanana API Integration Service
 * Handles image generation using NanoBanana REST API
 */

import { createErrorContext, withErrorHandling } from './errorHandler';

export interface NanoBananaOptions {
  model?: string;
  style?: string;
  quality?: 'standard' | 'hd';
  aspect_ratio?: '1:1' | '16:9' | '9:16' | '4:3' | '3:4';
  seed?: number;
  steps?: number;
  guidance_scale?: number;
}

export interface NanoBananaResponse {
  success: boolean;
  image_url?: string;
  error?: string;
  metadata?: {
    model: string;
    prompt: string;
    generated_at: string;
    processing_time: number;
  };
}

export interface NanoBananaError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

class NanoBananaService {
  private apiKey: string;
  private baseUrl: string;
  private retryAttempts: number = 2;
  private retryDelay: number = 1000; // 1 second

  constructor() {
    // Try to get NanoBanana specific API key first, then fallback to Gemini key
    this.apiKey = process.env.NEXT_PUBLIC_NANOBANANA_API_KEY || 
                  process.env.NEXT_PUBLIC_GEMINI_API_KEY || 
                  process.env.NEXT_PUBLIC_GOOGLE_API_KEY || '';
    
    this.baseUrl = process.env.NEXT_PUBLIC_NANOBANANA_BASE_URL || 'https://api.nanobanana.ai/v1';
    
    // Validate configuration
    if (!this.apiKey || this.apiKey === 'your_api_key_here' || this.apiKey.length < 10) {
      console.warn('NanoBanana API key not configured. AI image generation will use backend fallback.');
      this.apiKey = '';
    }
    
    if (!this.baseUrl || this.baseUrl.includes('undefined') || 
        (!this.baseUrl.startsWith('http://') && !this.baseUrl.startsWith('https://'))) {
      console.warn('NanoBanana base URL not configured properly. AI image generation will use backend fallback.');
      this.baseUrl = '';
    }
    
    // Log configuration status
    if (this.isConfigured()) {
      console.log('NanoBanana service configured successfully');
    } else {
      console.log('NanoBanana service not configured, will use backend fallback');
    }
  }

  /**
   * Generate an image using NanoBanana API
   */
  async generateImage(
    prompt: string, 
    options: NanoBananaOptions = {}
  ): Promise<NanoBananaResponse> {
    // Check if service is properly configured before attempting any API calls
    if (!this.isConfigured()) {
      console.warn('NanoBanana service not configured, using fallback');
      return this.getFallbackResponse(prompt);
    }

    const requestBody = {
      prompt: this.enhancePrompt(prompt),
      model: options.model || 'stable-diffusion-xl',
      style: options.style || 'photographic',
      quality: options.quality || 'standard',
      aspect_ratio: options.aspect_ratio || '1:1',
      seed: options.seed || Math.floor(Math.random() * 1000000),
      steps: options.steps || 20,
      guidance_scale: options.guidance_scale || 7.5,
    };

    const context = createErrorContext('nanobanana', 'generateImage');
    
    return withErrorHandling(
      () => this.makeRequestWithRetry('/generate', requestBody),
      context,
      () => Promise.resolve(this.getFallbackResponse(prompt))
    );
  }

  /**
   * Make API request with retry logic
   */
  private async makeRequestWithRetry(
    endpoint: string, 
    body: Record<string, unknown>, 
    attempt: number = 1
  ): Promise<NanoBananaResponse> {
    try {
      // Double-check configuration before making any requests
      if (!this.isConfigured()) {
        console.warn('NanoBanana API not configured, skipping API call');
        return {
          success: false,
          error: 'NanoBanana API not configured. Using backend generation.',
        };
      }
      
      // Check if we're in a browser environment and have a valid base URL
      if (typeof window === 'undefined' || !this.baseUrl || this.baseUrl.includes('undefined')) {
        console.warn('NanoBanana base URL not configured, skipping API call');
        return {
          success: false,
          error: 'NanoBanana API not configured. Using backend generation.',
        };
      }

      // Validate base URL format
      if (!this.baseUrl.startsWith('http://') && !this.baseUrl.startsWith('https://')) {
        console.warn('Invalid NanoBanana base URL format, skipping API call');
        return {
          success: false,
          error: 'NanoBanana API not configured. Using backend generation.',
        };
      }

      console.log(`Attempting NanoBanana API call to: ${this.baseUrl}${endpoint}`);
      
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`,
        },
        body: JSON.stringify(body),
        // Add timeout to prevent hanging requests
        signal: AbortSignal.timeout(15000), // 15 second timeout
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      return {
        success: true,
        image_url: data.image_url || data.url,
        metadata: {
          model: body.model as string,
          prompt: body.prompt as string,
          generated_at: new Date().toISOString(),
          processing_time: data.processing_time || 0,
        },
      };
    } catch (error) {
      console.error(`NanoBanana API attempt ${attempt} failed:`, error);
      
      // Don't retry for certain types of errors
      if (error instanceof Error && (
        error.message.includes('Failed to fetch') ||
        error.message.includes('NetworkError') ||
        error.message.includes('not configured') ||
        error.message.includes('timeout') ||
        error.message.includes('NanoBanana API not configured properly') ||
        error.message.includes('AbortError') ||
        error.message.includes('TypeError')
      )) {
        // Return fallback immediately for network/configuration errors
        console.warn('NanoBanana API unavailable, using fallback');
        return {
          success: false,
          error: 'NanoBanana API not available. Using backend generation.',
        };
      }
      
      // Retry logic for other errors
      if (attempt < this.retryAttempts) {
        const delay = this.retryDelay * Math.pow(2, attempt - 1); // Exponential backoff
        console.log(`Retrying NanoBanana API call in ${delay}ms (attempt ${attempt + 1}/${this.retryAttempts})`);
        await new Promise(resolve => setTimeout(resolve, delay));
        return this.makeRequestWithRetry(endpoint, body, attempt + 1);
      }

      // Final attempt failed, return error response
      console.error('NanoBanana API failed after all retry attempts');
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
      };
    }
  }

  /**
   * Enhance prompt with textile-specific keywords
   */
  private enhancePrompt(prompt: string): string {
    const textileKeywords = [
      'high quality', 'textile design', 'fabric pattern', 'elegant',
      'professional photography', 'studio lighting', 'commercial grade'
    ];
    
    // Check if prompt already contains textile-related terms
    const hasTextileTerms = /textile|fabric|cloth|saree|cotton|silk|design|pattern/i.test(prompt);
    
    if (!hasTextileTerms) {
      return `${prompt}, ${textileKeywords.slice(0, 3).join(', ')}`;
    }
    
    return prompt;
  }

  /**
   * Get fallback response when API is not available
   */
  private getFallbackResponse(prompt: string): NanoBananaResponse {
    const errorMessage = this.isConfigured() 
      ? 'NanoBanana API temporarily unavailable. Using backend generation.'
      : 'NanoBanana API not configured. Using backend generation.';
    
    console.info('Using fallback response for image generation:', {
      prompt: prompt.substring(0, 50) + '...',
      reason: this.isConfigured() ? 'API unavailable' : 'Not configured',
      timestamp: new Date().toISOString()
    });
    
    // Instead of static images, return an error to force backend generation
    return {
      success: false,
      error: errorMessage,
      metadata: {
        model: 'fallback',
        prompt,
        generated_at: new Date().toISOString(),
        processing_time: 0,
      },
    };
  }

  /**
   * Check if the service is properly configured
   */
  isConfigured(): boolean {
    const hasValidApiKey = !!(this.apiKey && 
                              this.apiKey !== 'your_api_key_here' && 
                              this.apiKey.length > 10);
    
    const hasValidBaseUrl = !!(this.baseUrl && 
                               !this.baseUrl.includes('undefined') &&
                               (this.baseUrl.startsWith('http://') || this.baseUrl.startsWith('https://')));
    
    const isConfigured = hasValidApiKey && hasValidBaseUrl;
    
    if (!isConfigured) {
      console.warn('NanoBanana service not properly configured:', {
        hasValidApiKey,
        hasValidBaseUrl,
        apiKeyLength: this.apiKey?.length || 0,
        baseUrl: this.baseUrl
      });
    }
    
    return isConfigured;
  }

  /**
   * Get available models
   */
  async getModels(): Promise<string[]> {
    if (!this.apiKey) {
      return ['fallback'];
    }

    try {
      const response = await fetch(`${this.baseUrl}/models`, {
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data.models || ['stable-diffusion-xl'];
    } catch (error) {
      console.error('Failed to fetch models:', error);
      return ['stable-diffusion-xl'];
    }
  }

  /**
   * Get API usage statistics
   */
  async getUsage(): Promise<{ requests_remaining: number; requests_used: number }> {
    if (!this.apiKey) {
      return { requests_remaining: 0, requests_used: 0 };
    }

    try {
      const response = await fetch(`${this.baseUrl}/usage`, {
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to fetch usage:', error);
      return { requests_remaining: 0, requests_used: 0 };
    }
  }

  /**
   * Get service status and configuration info
   */
  getServiceStatus(): {
    configured: boolean;
    apiKeyConfigured: boolean;
    baseUrlConfigured: boolean;
    baseUrl: string;
    apiKeyLength: number;
    environment: string;
  } {
    return {
      configured: this.isConfigured(),
      apiKeyConfigured: !!(this.apiKey && this.apiKey !== 'your_api_key_here' && this.apiKey.length > 10),
      baseUrlConfigured: !!(this.baseUrl && !this.baseUrl.includes('undefined') && 
                           (this.baseUrl.startsWith('http://') || this.baseUrl.startsWith('https://'))),
      baseUrl: this.baseUrl,
      apiKeyLength: this.apiKey?.length || 0,
      environment: typeof window !== 'undefined' ? 'browser' : 'server'
    };
  }
}

// Create and export singleton instance
export const nanoBananaService = new NanoBananaService();

// Export the class for testing
export default NanoBananaService;
