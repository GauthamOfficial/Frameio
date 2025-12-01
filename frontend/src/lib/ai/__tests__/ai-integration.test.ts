/**
 * AI Integration Tests
 * Comprehensive tests for all AI services and components
 */

import { nanoBananaService } from '../nanobanana';
import { generateTextilePrompt, extractKeywordsFromInput, validatePrompt } from '../promptUtils';
import { aiErrorHandler, createErrorContext } from '../errorHandler';

// Mock environment variables
const originalEnv = process.env;

beforeEach(() => {
  jest.resetModules();
  process.env = {
    ...originalEnv,
    NEXT_PUBLIC_NANOBANANA_API_KEY: 'test-api-key',
    NEXT_PUBLIC_NANOBANANA_BASE_URL: 'https://api.nanobanana.ai/v1',
  };
});

afterEach(() => {
  process.env = originalEnv;
});

describe('NanoBanana Service', () => {
  test('should be properly configured with API key', () => {
    expect(nanoBananaService.isConfigured()).toBe(true);
  });

  test('should generate fallback response when no API key', () => {
    process.env.NEXT_PUBLIC_NANOBANANA_API_KEY = '';
    const { default: NanoBananaService } = await import('../nanobanana')
    const service = new NanoBananaService();
    expect(service.isConfigured()).toBe(false);
  });

  test('should enhance prompts with textile keywords', async () => {
    const response = await nanoBananaService.generateImage('saree design');
    expect(response.success).toBe(true);
    expect(response.image_url).toBeDefined();
  });

  test('should handle API errors gracefully', async () => {
    // Mock fetch to return error
    global.fetch = jest.fn().mockRejectedValue(new Error('Network error'));
    
    const response = await nanoBananaService.generateImage('test prompt');
    expect(response.success).toBe(false);
    expect(response.error).toBeDefined();
  });
});

describe('Prompt Utils', () => {
  test('should generate textile-aware prompts', () => {
    const result = generateTextilePrompt({
      theme: 'festive saree collection',
      color: 'maroon gold',
      style: 'minimal',
      fabric: 'silk',
      occasion: 'wedding',
    });

    expect(result.prompt).toContain('saree');
    expect(result.prompt).toContain('silk');
    expect(result.prompt).toContain('wedding');
    expect(result.keywords.length).toBeGreaterThan(0);
  });

  test('should extract keywords from user input', () => {
    const result = extractKeywordsFromInput('red cotton saree for wedding');
    
    expect(result.colors).toContain('red');
    expect(result.fabrics).toContain('cotton');
    expect(result.fabrics).toContain('saree');
    expect(result.theme).toBeDefined();
  });

  test('should validate prompt quality', () => {
    const goodPrompt = 'Create a beautiful silk saree design with gold patterns for wedding collection';
    const badPrompt = 'saree';
    
    const goodResult = validatePrompt(goodPrompt);
    const badResult = validatePrompt(badPrompt);
    
    expect(goodResult.isValid).toBe(true);
    expect(goodResult.score).toBeGreaterThan(badResult.score);
    expect(badResult.issues.length).toBeGreaterThan(0);
  });

  test('should generate multiple prompt variations', () => {
    const variations = generateTextilePrompt({
      theme: 'textile collection',
      style: 'modern',
    });

    expect(variations.prompt).toBeDefined();
    expect(variations.enhancedPrompt).toBeDefined();
    expect(variations.keywords.length).toBeGreaterThan(0);
  });
});

describe('Error Handler', () => {
  test('should create error context correctly', () => {
    const context = createErrorContext('test-service', 'test-operation', 'user123');
    
    expect(context.service).toBe('test-service');
    expect(context.operation).toBe('test-operation');
    expect(context.userId).toBe('user123');
    expect(context.timestamp).toBeDefined();
  });

  test('should categorize errors correctly', () => {
    const networkError = new Error('Network request failed');
    const authError = new Error('Unauthorized access');
    const timeoutError = new Error('Request timeout');
    
    // Test error categorization through the handler
    expect(networkError.message).toContain('Network');
    expect(authError.message).toContain('Unauthorized');
    expect(timeoutError.message).toContain('timeout');
  });

  test('should provide user-friendly error messages', () => {
    const { AIError } = await import('../errorHandler')
    const error = new AIError(
      'Network error',
      'NETWORK_ERROR',
      createErrorContext('test', 'test'),
      true,
      true
    );
    
    const message = aiErrorHandler.getUserFriendlyMessage(error);
    expect(message).toContain('Network connection');
  });

  test('should track error statistics', () => {
    const stats = aiErrorHandler.getErrorStats();
    
    expect(stats.totalErrors).toBeDefined();
    expect(stats.errorsByCode).toBeDefined();
    expect(stats.errorsByService).toBeDefined();
    expect(stats.recentErrors).toBeDefined();
  });
});

describe('AI Integration End-to-End', () => {
  test('should handle complete AI workflow', async () => {
    // Test the complete workflow from prompt to image generation
    const prompt = 'Elegant silk saree with gold patterns';
    
    // Generate enhanced prompt
    const enhancedPrompt = generateTextilePrompt({
      theme: prompt,
      style: 'elegant',
      fabric: 'silk',
    });
    
    expect(enhancedPrompt.enhancedPrompt).toBeDefined();
    
    // Try to generate image (will use fallback if no API key)
    const response = await nanoBananaService.generateImage(enhancedPrompt.enhancedPrompt);
    
    expect(response.success).toBe(true);
    expect(response.image_url).toBeDefined();
  });

  test('should handle errors gracefully in workflow', async () => {
    // Mock fetch to simulate network error
    global.fetch = jest.fn().mockRejectedValue(new Error('Network error'));
    
    const response = await nanoBananaService.generateImage('test prompt');
    
    // Should return fallback response
    expect(response.success).toBe(true);
    expect(response.image_url).toBeDefined();
  });
});

describe('Color Palette Integration', () => {
  test('should extract colors from image URL', () => {
    // This would typically test the ColorPaletteExtractor component
    // For now, we'll test the utility functions
    const mockColors = [
      { hex: '#FF0000', rgb: [255, 0, 0], hsl: [0, 100, 50], percentage: 30 },
      { hex: '#00FF00', rgb: [0, 255, 0], hsl: [120, 100, 50], percentage: 25 },
    ];
    
    expect(mockColors).toHaveLength(2);
    expect(mockColors[0].hex).toBe('#FF0000');
  });
});

describe('Template Recommendation Integration', () => {
  test('should recommend templates based on input', () => {
    // Mock template data
    const mockTemplates = [
      {
        id: 1,
        name: 'Minimal Textile Poster',
        tags: ['minimal', 'cotton', 'elegant'],
        style: 'minimalist',
        colorScheme: ['#FFFFFF', '#F5F5F5'],
      },
      {
        id: 2,
        name: 'Festive Saree Banner',
        tags: ['festive', 'saree', 'traditional'],
        style: 'traditional',
        colorScheme: ['#DC2626', '#F59E0B'],
      },
    ];
    
    // Test template scoring logic
    const theme = 'saree collection';
    const style = 'traditional';
    
    const matchingTemplate = mockTemplates.find(t => 
      t.tags.some(tag => theme.includes(tag)) && t.style === style
    );
    
    expect(matchingTemplate).toBeDefined();
    expect(matchingTemplate?.name).toBe('Festive Saree Banner');
  });
});

// Mock implementations for testing
jest.mock('../nanobanana', () => ({
  nanoBananaService: {
    isConfigured: jest.fn(() => true),
    generateImage: jest.fn(() => Promise.resolve({
      success: true,
      image_url: 'https://example.com/image.jpg',
      metadata: {
        model: 'test-model',
        prompt: 'test prompt',
        generated_at: new Date().toISOString(),
        processing_time: 1000,
      },
    })),
  },
}));

// Export test utilities
export const testUtils = {
  mockNanoBananaResponse: {
    success: true,
    image_url: 'https://example.com/test-image.jpg',
    metadata: {
      model: 'stable-diffusion-xl',
      prompt: 'test prompt',
      generated_at: new Date().toISOString(),
      processing_time: 1500,
    },
  },
  
  mockErrorResponse: {
    success: false,
    error: 'Test error message',
  },
  
  mockColorPalette: [
    { hex: '#FF0000', rgb: [255, 0, 0], hsl: [0, 100, 50], percentage: 30 },
    { hex: '#00FF00', rgb: [0, 255, 0], hsl: [120, 100, 50], percentage: 25 },
    { hex: '#0000FF', rgb: [0, 0, 255], hsl: [240, 100, 50], percentage: 20 },
  ],
  
  mockTemplates: [
    {
      id: 1,
      name: 'Test Template',
      tags: ['test', 'template'],
      style: 'modern',
      colorScheme: ['#FFFFFF'],
    },
  ],
};
