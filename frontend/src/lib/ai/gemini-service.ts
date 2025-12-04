/**
 * Gemini AI Service for Textile Poster and Caption Generation
 * Replaces NanoBanana with our new backend AI services
 */
import { AIErrorHandler, createErrorContext } from './errorHandler';
import { API_BASE_URL } from '@/utils/api';

export interface GeminiImageResponse {
  success: boolean;
  image_path?: string;
  image_url?: string;
  filename?: string;
  error?: string;
}

export interface GeminiCaptionResponse {
  success: boolean;
  caption?: {
    main_content: string;
    hashtags: string[];
    call_to_action: string;
    word_count: number;
    character_count: number;
    has_emoji: boolean;
  };
  error?: string;
}

export class GeminiService {
  private baseUrl: string;
  private errorHandler: AIErrorHandler;

  constructor() {
    this.baseUrl = API_BASE_URL.endsWith('/api') ? API_BASE_URL : `${API_BASE_URL}/api`;
    this.errorHandler = AIErrorHandler.getInstance();
  }

  /**
   * Generate AI poster from text prompt
   */
  async generatePoster(
    prompt: string,
    aspectRatio: '1:1' | '16:9' | '4:5' = '1:1'
  ): Promise<GeminiImageResponse> {
    return this.errorHandler.executeWithRetry(async () => {
      const response = await fetch(`${this.baseUrl}/ai-poster/generate_poster/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt,
          aspect_ratio: aspectRatio
        }),
        signal: AbortSignal.timeout(30000), // 30 second timeout for image generation
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      if (!data.success) {
        throw new Error(data.error || 'Failed to generate poster');
      }

      return {
        success: true,
        image_path: data.image_path,
        image_url: data.image_url,
        filename: data.filename
      };
    }, createErrorContext('gemini', 'generatePoster'));
  }

  /**
   * Generate AI poster by editing an uploaded image
   */
  async editPoster(
    prompt: string,
    imageFile: File,
    aspectRatio: '1:1' | '16:9' | '4:5' = '1:1'
  ): Promise<GeminiImageResponse> {
    return this.errorHandler.executeWithRetry(async () => {
      const formData = new FormData();
      formData.append('prompt', prompt);
      formData.append('image', imageFile);
      formData.append('aspect_ratio', aspectRatio);

      const response = await fetch(`${this.baseUrl}/ai-poster/edit_poster/`, {
        method: 'POST',
        body: formData,
        signal: AbortSignal.timeout(30000), // 30 second timeout
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      if (!data.success) {
        throw new Error(data.error || 'Failed to edit poster');
      }

      return {
        success: true,
        image_path: data.image_path,
        image_url: data.image_url,
        filename: data.filename
      };
    }, createErrorContext('gemini', 'editPoster'));
  }

  /**
   * Generate AI poster by combining multiple images
   */
  async compositePoster(
    prompt: string,
    imageFiles: File[],
    aspectRatio: '1:1' | '16:9' | '4:5' = '16:9'
  ): Promise<GeminiImageResponse> {
    return this.errorHandler.executeWithRetry(async () => {
      const formData = new FormData();
      formData.append('prompt', prompt);
      formData.append('aspect_ratio', aspectRatio);
      
      // Add all image files
      imageFiles.forEach(file => {
        formData.append('images', file);
      });

      const response = await fetch(`${this.baseUrl}/ai-poster/composite_poster/`, {
        method: 'POST',
        body: formData,
        signal: AbortSignal.timeout(45000), // 45 second timeout for composite
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      if (!data.success) {
        throw new Error(data.error || 'Failed to generate composite poster');
      }

      return {
        success: true,
        image_path: data.image_path,
        image_url: data.image_url,
        filename: data.filename
      };
    }, createErrorContext('gemini', 'compositePoster'));
  }

  /**
   * Generate product caption
   */
  async generateProductCaption(
    productName: string,
    productType: string = 'textile',
    style: 'modern' | 'traditional' | 'casual' | 'formal' = 'modern',
    tone: 'professional' | 'friendly' | 'authoritative' | 'conversational' = 'professional',
    includeHashtags: boolean = true,
    includeEmoji: boolean = true,
    maxLength: number = 200
  ): Promise<GeminiCaptionResponse> {
    return this.errorHandler.executeWithRetry(async () => {
      const response = await fetch(`${this.baseUrl}/ai-caption/product_caption/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          product_name: productName,
          product_type: productType,
          style,
          tone,
          include_hashtags: includeHashtags,
          include_emoji: includeEmoji,
          max_length: maxLength
        }),
        signal: AbortSignal.timeout(15000), // 15 second timeout
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      if (!data.success) {
        throw new Error(data.error || 'Failed to generate caption');
      }

      return {
        success: true,
        caption: data.caption
      };
    }, createErrorContext('gemini', 'generateProductCaption'));
  }

  /**
   * Generate social media caption
   */
  async generateSocialMediaCaption(
    content: string,
    platform: 'instagram' | 'facebook' | 'twitter' | 'linkedin' = 'instagram',
    postType: 'product_showcase' | 'behind_scenes' | 'educational' | 'promotional' = 'product_showcase',
    style: 'engaging' | 'professional' | 'casual' | 'creative' = 'engaging',
    tone: 'friendly' | 'authoritative' | 'inspirational' | 'conversational' = 'friendly',
    includeHashtags: boolean = true,
    includeEmoji: boolean = true,
    callToAction: boolean = true
  ): Promise<GeminiCaptionResponse> {
    return this.errorHandler.executeWithRetry(async () => {
      const response = await fetch(`${this.baseUrl}/ai-caption/social_media_caption/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content,
          platform,
          post_type: postType,
          style,
          tone,
          include_hashtags: includeHashtags,
          include_emoji: includeEmoji,
          call_to_action: callToAction
        }),
        signal: AbortSignal.timeout(15000), // 15 second timeout
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      if (!data.success) {
        throw new Error(data.error || 'Failed to generate social media caption');
      }

      return {
        success: true,
        caption: data.caption
      };
    }, createErrorContext('gemini', 'generateSocialMediaCaption'));
  }

  /**
   * Generate image caption
   */
  async generateImageCaption(
    imageDescription: string,
    captionType: 'descriptive' | 'marketing' | 'educational' | 'artistic' = 'descriptive',
    style: 'professional' | 'creative' | 'technical' | 'casual' = 'professional',
    tone: 'informative' | 'persuasive' | 'educational' | 'artistic' = 'informative',
    includeHashtags: boolean = false,
    includeEmoji: boolean = false
  ): Promise<GeminiCaptionResponse> {
    return this.errorHandler.executeWithRetry(async () => {
      const response = await fetch(`${this.baseUrl}/ai-caption/image_caption/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          image_description: imageDescription,
          caption_type: captionType,
          style,
          tone,
          include_hashtags: includeHashtags,
          include_emoji: includeEmoji
        }),
        signal: AbortSignal.timeout(15000), // 15 second timeout
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      if (!data.success) {
        throw new Error(data.error || 'Failed to generate image caption');
      }

      return {
        success: true,
        caption: data.caption
      };
    }, createErrorContext('gemini', 'generateImageCaption'));
  }

  /**
   * Generate bulk captions for multiple products
   */
  async generateBulkCaptions(
    products: Array<{name: string, type: string}>,
    captionStyle: 'consistent' | 'varied' | 'seasonal' = 'consistent',
    brandVoice: 'professional' | 'friendly' | 'authoritative' | 'conversational' = 'professional'
  ): Promise<{success: boolean, captions?: Array<Record<string, unknown>>, error?: string}> {
    return this.errorHandler.executeWithRetry(async () => {
      const response = await fetch(`${this.baseUrl}/ai-caption/bulk_captions/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          products,
          caption_style: captionStyle,
          brand_voice: brandVoice
        }),
        signal: AbortSignal.timeout(30000), // 30 second timeout
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      if (!data.success) {
        throw new Error(data.error || 'Failed to generate bulk captions');
      }

      return {
        success: true,
        captions: data.captions
      };
    }, createErrorContext('gemini', 'generateBulkCaptions'));
  }

  /**
   * Check if AI services are available
   */
  async checkServiceStatus(): Promise<{available: boolean, message: string}> {
    try {
      const response = await fetch(`${this.baseUrl}/ai-poster/status/`);
      const data = await response.json();
      
      return {
        available: data.service_available || false,
        message: data.message || 'AI services status unknown'
      };
    } catch {
      return {
        available: false,
        message: 'Failed to check AI services status'
      };
    }
  }

  /**
   * Check if the service is properly configured
   */
  isConfigured(): boolean {
    return !!(this.baseUrl && !this.baseUrl.includes('undefined'));
  }
}

// Export singleton instance
export const geminiService = new GeminiService();

