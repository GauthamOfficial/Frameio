import { test, expect } from '@playwright/test';

test.describe('AI Backend API - Gemini Image Generation', () => {
  const API_BASE_URL = 'http://localhost:8000/api/ai';
  
  test('should check AI poster service status', async ({ request }) => {
    const response = await request.get(`${API_BASE_URL}/ai-poster/status/`);
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data.success).toBe(true);
    expect(data.service_available).toBe(true);
  });

  test('should generate poster from prompt via API', async ({ request }) => {
    const testData = {
      prompt: 'Create a modern textile poster for a silk saree brand with elegant typography',
      aspect_ratio: '4:5'
    };
    
    const response = await request.post(`${API_BASE_URL}/ai-poster/generate_poster/`, {
      data: testData,
      headers: {
        'Content-Type': 'application/json'
      },
      timeout: 120000 // 2 minutes timeout for AI generation
    });
    
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data.success).toBe(true);
    expect(data.message).toContain('successfully');
    expect(data.image_path).toBeDefined();
    expect(data.image_url).toBeDefined();
    expect(data.filename).toBeDefined();
  });

  test('should handle invalid prompts gracefully', async ({ request }) => {
    const testData = {
      prompt: '', // Empty prompt
      aspect_ratio: '4:5'
    };
    
    const response = await request.post(`${API_BASE_URL}/ai-poster/generate_poster/`, {
      data: testData,
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    expect(response.status()).toBe(400);
    
    const data = await response.json();
    expect(data.success).toBe(false);
    expect(data.error).toContain('required');
  });

  test('should test different aspect ratios via API', async ({ request }) => {
    const aspectRatios = ['1:1', '16:9', '4:5'];
    
    for (const ratio of aspectRatios) {
      const testData = {
        prompt: `Test poster with ${ratio} aspect ratio`,
        aspect_ratio: ratio
      };
      
      const response = await request.post(`${API_BASE_URL}/ai-poster/generate_poster/`, {
        data: testData,
        headers: {
          'Content-Type': 'application/json'
        },
        timeout: 120000 // 2 minutes timeout for AI generation
      });
      
      expect(response.status()).toBe(200);
      
      const data = await response.json();
      expect(data.success).toBe(true);
      expect(data.aspect_ratio).toBe(ratio);
    }
  });

  test('should test multiple prompt variations via API', async ({ request }) => {
    const testPrompts = [
      'Modern textile design with geometric patterns',
      'Elegant silk saree poster with gold accents',
      'Minimalist fashion poster with clean typography',
      'Traditional Indian textile with contemporary twist'
    ];
    
    for (const prompt of testPrompts) {
      const testData = {
        prompt: prompt,
        aspect_ratio: '4:5'
      };
      
      const response = await request.post(`${API_BASE_URL}/ai-poster/generate_poster/`, {
        data: testData,
        headers: {
          'Content-Type': 'application/json'
        },
        timeout: 120000 // 2 minutes timeout for AI generation
      });
      
      expect(response.status()).toBe(200);
      
      const data = await response.json();
      expect(data.success).toBe(true);
      expect(data.prompt).toBe(prompt);
    }
  });

  test('should handle API errors gracefully', async ({ request }) => {
    // Test with malformed request
    const response = await request.post(`${API_BASE_URL}/ai-poster/generate_poster/`, {
      data: { invalid: 'data' },
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    expect(response.status()).toBe(400);
  });

  test('should test service availability under load', async ({ request }) => {
    // Test multiple concurrent requests
    const promises = [];
    
    for (let i = 0; i < 3; i++) {
      const testData = {
        prompt: `Concurrent test poster ${i}`,
        aspect_ratio: '1:1'
      };
      
      promises.push(
        request.post(`${API_BASE_URL}/ai-poster/generate_poster/`, {
          data: testData,
          headers: {
            'Content-Type': 'application/json'
          }
        })
      );
    }
    
    const responses = await Promise.all(promises);
    
    // All requests should succeed
    for (const response of responses) {
      expect(response.status()).toBe(200);
      
      const data = await response.json();
      expect(data.success).toBe(true);
    }
  });
});
