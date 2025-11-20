import { test, expect } from '@playwright/test';

test.describe('AI Services - Simple Gemini Test', () => {
  const API_BASE_URL = 'http://localhost:8000/api/ai';
  
  test('should check AI poster service status', async ({ request }) => {
    const response = await request.get(`${API_BASE_URL}/ai-poster/status/`);
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data.success).toBe(true);
    expect(data.service_available).toBe(true);
  });

  test('should generate a simple poster', async ({ request }) => {
    const testData = {
      prompt: 'Simple red circle on white background',
      aspect_ratio: '1:1'
    };
    
    console.log('🚀 Starting poster generation...');
    const startTime = Date.now();
    
    const response = await request.post(`${API_BASE_URL}/ai-poster/generate_poster/`, {
      data: testData,
      headers: {
        'Content-Type': 'application/json'
      },
      timeout: 120000 // 2 minutes timeout
    });
    
    const endTime = Date.now();
    const duration = (endTime - startTime) / 1000;
    console.log(`⏱️ Generation took ${duration.toFixed(2)} seconds`);
    
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data.success).toBe(true);
    expect(data.message).toContain('successfully');
    expect(data.image_path).toBeDefined();
    expect(data.image_url).toBeDefined();
    expect(data.filename).toBeDefined();
    
    console.log(`✅ Poster generated: ${data.filename}`);
    console.log(`📁 Image path: ${data.image_path}`);
  });
});
