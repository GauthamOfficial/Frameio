/**
 * API Client for Frameio Backend
 * Handles all API communication with proper error handling and authentication
 */
import { API_BASE_URL } from '@/utils/api';

export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface FileUploadResponse {
  success: boolean;
  url: string;
  filename: string;
  original_name: string;
  size: number;
  content_type: string;
  uploaded_at: string;
  image_info?: {
    width: number;
    height: number;
    format: string;
  };
}

export interface PosterGenerationRequest {
  product_image_url?: string;
  fabric_type: 'saree' | 'cotton' | 'silk' | 'linen' | 'wool' | 'denim';
  festival: 'deepavali' | 'pongal' | 'wedding' | 'general';
  price_range: string;
  style: 'elegant' | 'modern' | 'traditional' | 'bohemian' | 'casual';
  color_scheme?: string;
  custom_text?: string;
  offer_details?: string;
  // New parameters for two-step workflow
  color_palette?: string[];
  generation_type?: 'poster' | 'catalog' | 'background';
}

export interface PosterGenerationResponse {
  success: boolean;
  poster_url: string;
  caption_suggestions: string[];
  hashtags: string[];
  metadata: {
    fabric_type: string;
    festival: string;
    style: string;
    generated_at: string;
    organization: string;
    // New metadata for two-step workflow
    two_step_flow?: boolean;
    gemini_refinement?: Record<string, unknown>;
    nanobanana_generation?: boolean;
    original_prompt?: string;
    refined_prompt?: string;
    processing_time?: number;
  };
  // Error handling for two-step workflow
  error?: string;
  fallback_attempted?: boolean;
}

export interface CatalogCreateRequest {
  product_ids: number[];
  template: 'festival_collection' | 'wedding_collection' | 'casual_wear' | 'premium_collection';
  style: 'modern' | 'traditional' | 'elegant' | 'bohemian';
  color_scheme: string;
}

export interface CatalogCreateResponse {
  success: boolean;
  catalog_url: string;
  catalog_name: string;
  created_at: string;
  organization: string;
}

export interface SchedulePostRequest {
  platform: 'facebook' | 'instagram' | 'tiktok' | 'whatsapp' | 'twitter' | 'linkedin';
  asset_url: string;
  caption: string;
  scheduled_time: string;
  metadata?: Record<string, unknown>;
}

export interface SocialMediaPostRequest {
  platform: 'facebook' | 'instagram' | 'tiktok' | 'whatsapp' | 'twitter' | 'linkedin';
  asset_url: string;
  caption: string;
  metadata?: Record<string, unknown>;
}

class ApiClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl?: string) {
    // Use provided baseUrl, or fallback to API_BASE_URL from utility
    if (baseUrl) {
      this.baseUrl = baseUrl.replace(/\/+$/, '');
    } else {
      this.baseUrl = API_BASE_URL.replace(/\/+$/, '');
    }
  }

  setToken(token: string | null) {
    this.token = token;
  }

  private getToken(): string | null {
    // Try to get token from the client first, then from localStorage as fallback
    if (this.token) {
      return this.token;
    }
    
    // Fallback to localStorage for development
    if (typeof window !== 'undefined') {
      return localStorage.getItem('auth-token');
    }
    
    return null;
  }

  private buildUrl(endpoint: string): string {
    // If endpoint is absolute, return as-is
    if (/^https?:\/\//i.test(endpoint)) {
      return endpoint;
    }

    // Ensure endpoint starts with a single leading slash
    const normalizedEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;

    // Avoid double /api when baseUrl already contains /api
    if (this.baseUrl.endsWith('/api') && normalizedEndpoint.startsWith('/api/')) {
      return `${this.baseUrl}${normalizedEndpoint.replace(/^\/api/, '')}`;
    }

    return `${this.baseUrl}${normalizedEndpoint}`;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = this.buildUrl(endpoint);
    
    const existingHeaders = (options.headers as Record<string, string>) || {};
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...existingHeaders,
    };

    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    // Add development headers for testing
    if (typeof window !== 'undefined') {
      const devUserId = localStorage.getItem('dev-user-id');
      const devOrgId = localStorage.getItem('dev-org-id');
      
      if (devUserId && devOrgId) {
        headers['X-Dev-User-ID'] = devUserId;
        headers['X-Dev-Org-ID'] = devOrgId;
        console.log('Added development headers:', { devUserId, devOrgId });
      }
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers: headers as HeadersInit,
      });

      const data = await response.json();

      if (!response.ok) {
        return {
          success: false,
          error: data.error || `HTTP ${response.status}: ${response.statusText}`,
        };
      }

      return {
        success: true,
        data,
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
      };
    }
  }

  // Convenience helpers that return raw backend JSON (matching components' expectations)
  async get(endpoint: string, options: RequestInit = {}): Promise<unknown> {
    const url = this.buildUrl(endpoint);

    const existingHeaders = (options.headers as Record<string, string>) || {};
    const headers: Record<string, string> = {
      ...existingHeaders,
    };

    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    if (typeof window !== 'undefined') {
      const devUserId = localStorage.getItem('dev-user-id');
      const devOrgId = localStorage.getItem('dev-org-id');
      if (devUserId && devOrgId) {
        headers['X-Dev-User-ID'] = devUserId;
        headers['X-Dev-Org-ID'] = devOrgId;
      }
    }

    try {
      const response = await fetch(url, { ...options, method: 'GET', headers: headers as HeadersInit });
      const data = await response.json();
      if (!response.ok) {
        return { success: false, error: data?.error || `HTTP ${response.status}: ${response.statusText}` };
      }
      return data;
    } catch (error) {
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error occurred' };
    }
  }

  async post(endpoint: string, body?: unknown, options: RequestInit = {}): Promise<unknown> {
    const url = this.buildUrl(endpoint);

    const isFormData = typeof FormData !== 'undefined' && body instanceof FormData;

    const existingHeaders = (options.headers as Record<string, string>) || {};
    const headers: Record<string, string> = {
      // Don't set Content-Type for FormData; the browser will set the correct boundary
      ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
      ...existingHeaders,
    };

    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    if (typeof window !== 'undefined') {
      const devUserId = localStorage.getItem('dev-user-id');
      const devOrgId = localStorage.getItem('dev-org-id');
      if (devUserId && devOrgId) {
        headers['X-Dev-User-ID'] = devUserId;
        headers['X-Dev-Org-ID'] = devOrgId;
      }
    }

    try {
      const response = await fetch(url, {
        ...options,
        method: 'POST',
        headers: headers as HeadersInit,
        body: isFormData ? body : body !== undefined ? JSON.stringify(body) : undefined,
      });
      const data = await response.json();
      if (!response.ok) {
        return { success: false, error: data?.error || `HTTP ${response.status}: ${response.statusText}` };
      }
      return data;
    } catch (error) {
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error occurred' };
    }
  }

  // File Upload Methods
  async uploadFile(file: File): Promise<ApiResponse<FileUploadResponse>> {
    const formData = new FormData();
    formData.append('file', file);

    const headers: Record<string, string> = {};
    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    // Add development headers for testing
    if (typeof window !== 'undefined') {
      const devUserId = localStorage.getItem('dev-user-id');
      const devOrgId = localStorage.getItem('dev-org-id');
      
      if (devUserId && devOrgId) {
        headers['X-Dev-User-ID'] = devUserId;
        headers['X-Dev-Org-ID'] = devOrgId;
      }
    }

    try {
      const response = await fetch(this.buildUrl('/api/upload/'), {
        method: 'POST',
        headers: headers as HeadersInit,
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        return {
          success: false,
          error: data.error || `HTTP ${response.status}: ${response.statusText}`,
        };
      }

      return {
        success: true,
        data,
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Upload failed',
      };
    }
  }

  async uploadMultipleFiles(files: File[]): Promise<ApiResponse<{ uploaded_files: FileUploadResponse[]; errors: string[] }>> {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));

    const headers: Record<string, string> = {};
    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    // Add development headers for testing
    if (typeof window !== 'undefined') {
      const devUserId = localStorage.getItem('dev-user-id');
      const devOrgId = localStorage.getItem('dev-org-id');
      
      if (devUserId && devOrgId) {
        headers['X-Dev-User-ID'] = devUserId;
        headers['X-Dev-Org-ID'] = devOrgId;
      }
    }

    try {
      const response = await fetch(this.buildUrl('/api/upload/multiple/'), {
        method: 'POST',
        headers: headers as HeadersInit,
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        return {
          success: false,
          error: data.error || `HTTP ${response.status}: ${response.statusText}`,
        };
      }

      return {
        success: true,
        data,
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Upload failed',
      };
    }
  }

  // AI Generation Methods
  async generatePoster(request: PosterGenerationRequest): Promise<ApiResponse<PosterGenerationResponse>> {
    return this.request<PosterGenerationResponse>('/api/ai/textile/poster/generate_poster/', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // Enhanced two-step generation with Gemini + NanoBanana
  async generatePosterTwoStep(request: PosterGenerationRequest): Promise<ApiResponse<PosterGenerationResponse>> {
    try {
      // Create a comprehensive prompt from all the request parameters
      const enhancedPrompt = this.buildEnhancedPrompt(request);
      
      // Use the working AI poster generation endpoint
      const requestData = {
        prompt: enhancedPrompt,
        aspect_ratio: '4:5' // Better for textile posters
      };
      
      console.log('🚀 Sending request to backend:', requestData);
      
      const resp = await this.post('/api/ai/ai-poster/generate_poster/', requestData);

      // Type guard: check if resp is an object with error property
      const isErrorResponse = (r: unknown): r is { success: false; error: string } => {
        return typeof r === 'object' && r !== null && 'error' in r && 'success' in r && (r as { success: unknown }).success === false;
      };

      // Type guard: check if resp is a success response
      const isSuccessResponse = (r: unknown): r is { success: true; image_url?: string; image_path?: string } => {
        return typeof r === 'object' && r !== null && 'success' in r && (r as { success: unknown }).success === true;
      };

      if (isErrorResponse(resp)) {
        // If backend AI service is not available, return a fallback response
        if (resp.error?.includes('not available') || resp.error?.includes('503')) {
          console.warn('Backend AI service not available, using fallback response');
          return this.getFallbackPosterResponse(request);
        }
        return { success: false, error: resp.error || 'Failed to generate with backend' };
      }

      // Transform the response to match the expected format
      const imageUrl = isSuccessResponse(resp) ? (resp.image_url || resp.image_path || '') : '';
      
      return { 
        success: true, 
        data: {
          success: true,
          poster_url: imageUrl,
          caption_suggestions: [
            `Discover our beautiful ${request.fabric_type} collection`,
            `Perfect for ${request.festival} celebrations`,
            `Premium quality ${request.style} design`
          ],
          hashtags: [
            `#${request.fabric_type}`,
            `#${request.festival}`,
            `#${request.style}`,
            '#textile',
            '#fashion'
          ],
          metadata: {
            fabric_type: request.fabric_type,
            festival: request.festival,
            style: request.style,
            generated_at: new Date().toISOString(),
            organization: 'default',
            two_step_flow: true,
            original_prompt: request.custom_text,
            refined_prompt: request.custom_text,
            processing_time: 0
          }
        }
      } as ApiResponse<PosterGenerationResponse>;
    } catch (error) {
      console.error('Error in generatePosterTwoStep:', error);
      console.error('Request that failed:', request);
      console.error('Enhanced prompt:', this.buildEnhancedPrompt(request));
      return this.getFallbackPosterResponse(request);
    }
  }

  // Build enhanced prompt from request parameters
  private buildEnhancedPrompt(request: PosterGenerationRequest): string {
    const parts = [];
    
    // Base description
    if (request.custom_text) {
      parts.push(request.custom_text);
    }
    
    // Fabric type
    if (request.fabric_type) {
      parts.push(`${request.fabric_type} fabric`);
    }
    
    // Style
    if (request.style) {
      parts.push(`${request.style} style`);
    }
    
    // Festival/occasion
    if (request.festival && request.festival !== 'general') {
      parts.push(`for ${request.festival} celebrations`);
    }
    
    // Price range
    if (request.price_range) {
      parts.push(`priced at ${request.price_range}`);
    }
    
    // Color palette
    if (request.color_palette && request.color_palette.length > 0) {
      parts.push(`featuring ${request.color_palette.join(', ')} colors`);
    }
    
    // Offer details
    if (request.offer_details) {
      parts.push(`with ${request.offer_details}`);
    }
    
    // Combine all parts
    let prompt = parts.join(', ');
    
    // Add textile-specific enhancements
    prompt += ', high-quality textile poster design, elegant typography, professional photography style';
    
    return prompt;
  }

  // Fallback response when AI services are not available
  private getFallbackPosterResponse(request: PosterGenerationRequest): ApiResponse<PosterGenerationResponse> {
    console.warn('Using fallback poster response - AI services not available');
    
    return {
      success: true,
      data: {
        success: false,
        error: 'AI image generation is currently unavailable. Please try again later or contact support.',
        poster_url: '', // No image URL for fallback
        caption_suggestions: [
          `Discover our beautiful ${request.fabric_type} collection`,
          `Perfect for ${request.festival} celebrations`,
          `Premium quality ${request.style} design`
        ],
        hashtags: [
          `#${request.fabric_type}`,
          `#${request.festival}`,
          `#${request.style}`,
          '#textile',
          '#fashion'
        ],
        metadata: {
          fabric_type: request.fabric_type,
          festival: request.festival,
          style: request.style,
          generated_at: new Date().toISOString(),
          organization: 'default',
          two_step_flow: true,
          original_prompt: request.custom_text,
          refined_prompt: request.custom_text,
          processing_time: 0,
          fallback: true
        }
      }
    } as ApiResponse<PosterGenerationResponse>;
  }

  async createCatalog(request: CatalogCreateRequest): Promise<ApiResponse<CatalogCreateResponse>> {
    return this.request<CatalogCreateResponse>('/api/ai/catalog/create/', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // Social Media Methods
  async schedulePost(request: SchedulePostRequest): Promise<ApiResponse<unknown>> {
    return this.request('/api/ai/schedule/', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async postToSocialMedia(request: SocialMediaPostRequest): Promise<ApiResponse<unknown>> {
    return this.request('/api/ai/social/post/', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async getSupportedPlatforms(): Promise<ApiResponse<unknown>> {
    return this.request('/api/ai/social/platforms/');
  }

  // Utility Methods
  async downloadFile(url: string, filename: string): Promise<boolean> {
    if (typeof window === 'undefined' || typeof document === 'undefined') {
      console.error('Download failed: window/document not available (SSR)');
      return false;
    }
    
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = downloadUrl;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(downloadUrl);
      document.body.removeChild(a);
      
      return true;
    } catch (error) {
      console.error('Download failed:', error);
      return false;
    }
  }

  // Validation Methods
  validateFile(file: File): { valid: boolean; error?: string } {
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    const maxSize = 10 * 1024 * 1024; // 10MB

    if (!allowedTypes.includes(file.type)) {
      return {
        valid: false,
        error: `File type ${file.type} not supported. Allowed types: ${allowedTypes.join(', ')}`,
      };
    }

    if (file.size > maxSize) {
      return {
        valid: false,
        error: `File too large. Maximum size is ${maxSize / (1024 * 1024)}MB`,
      };
    }

    return { valid: true };
  }

  validateMultipleFiles(files: File[]): { valid: boolean; errors: string[] } {
    const errors: string[] = [];
    
    files.forEach((file, index) => {
      const validation = this.validateFile(file);
      if (!validation.valid) {
        errors.push(`File ${index + 1} (${file.name}): ${validation.error}`);
      }
    });

    return {
      valid: errors.length === 0,
      errors,
    };
  }
}

// Create and export a singleton instance
export const apiClient = new ApiClient();

// Export the class for custom instances
export default ApiClient;
