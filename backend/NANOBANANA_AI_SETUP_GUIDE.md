# NanoBanana AI Service Setup Guide

## Overview
This guide will help you set up NanoBanana AI service for proper AI image generation according to prompts in your textile design platform.

## What You Need to Do

### 1. Get NanoBanana API Key

**Step 1: Sign up for NanoBanana**
1. Go to [https://app.banana.dev/](https://app.banana.dev/)
2. Create an account or sign in
3. Navigate to your dashboard

**Step 2: Get API Key**
1. In your dashboard, go to "API Keys" section
2. Create a new API key
3. Copy the API key (it will look like: `banana_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`)

### 2. Configure Environment Variables

**Step 1: Update your `.env` file**
```bash
# Add these lines to your .env file
NANOBANANA_API_KEY=your_actual_api_key_here
NEXT_PUBLIC_NANOBANANA_API_KEY=your_actual_api_key_here
NEXT_PUBLIC_NANOBANANA_BASE_URL=https://api.nanobanana.ai/v1
```

**Step 2: Update Django settings**
Add to your `backend/frameio_backend/settings.py`:
```python
# NanoBanana AI Configuration
NANOBANANA_API_KEY = os.getenv('NANOBANANA_API_KEY', '')
NEXT_PUBLIC_NANOBANANA_API_KEY = os.getenv('NEXT_PUBLIC_NANOBANANA_API_KEY', '')
NEXT_PUBLIC_NANOBANANA_BASE_URL = os.getenv('NEXT_PUBLIC_NANOBANANA_BASE_URL', 'https://api.nanobanana.ai/v1')
```

### 3. Update NanoBanana Service Configuration

**Step 1: Update Frontend Service** (`frontend/src/lib/ai/nanobanana.ts`)
```typescript
// Update the constructor to use proper API key
constructor() {
  this.apiKey = process.env.NEXT_PUBLIC_NANOBANANA_API_KEY || '';
  this.baseUrl = process.env.NEXT_PUBLIC_NANOBANANA_BASE_URL || 'https://api.nanobanana.ai/v1';
  
  if (!this.apiKey) {
    console.warn('NanoBanana API key not found. AI image generation will use fallback.');
  }
}
```

**Step 2: Update Backend Service** (`backend/ai_services/nanobanana_service.py`)
```python
def __init__(self):
    """Initialize the NanoBanana client"""
    self.api_key = settings.NANOBANANA_API_KEY
    self.base_url = "https://api.nanobanana.ai"
    
    if not self.api_key or self.api_key == '':
        logger.info("NANOBANANA_API_KEY not configured - using fallback mode")
        self.use_fallback = True
    else:
        try:
            import requests
            self.client = requests.Session()
            self.client.headers.update({
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            })
            logger.info("NanoBanana REST API client initialized successfully")
            self.use_fallback = False
        except Exception as e:
            logger.warning(f"Failed to initialize NanoBanana client: {str(e)} - using fallback mode")
            self.client = None
            self.use_fallback = True
```

### 4. Test NanoBanana Integration

**Step 1: Create Test Script**
Create `backend/test_nanobanana_integration.py`:
```python
#!/usr/bin/env python3
"""
Test NanoBanana AI integration
"""
import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from ai_services.nanobanana_service import NanoBananaAIService

def test_nanobanana():
    """Test NanoBanana AI service"""
    print("🧪 Testing NanoBanana AI Service...")
    
    try:
        service = NanoBananaAIService()
        
        # Test if service is available
        if service.is_available():
            print("✅ NanoBanana service is available")
            
            # Test image generation
            result = service.generate_poster(
                image_url="https://example.com/fabric.jpg",
                offer_text="Special Deepavali Collection",
                theme="festive"
            )
            
            if result.get('success'):
                print(f"✅ Generated {len(result.get('image_urls', []))} images")
                print(f"   Generation ID: {result.get('generation_id')}")
                print(f"   Cost: ${result.get('cost', 0)}")
            else:
                print(f"❌ Generation failed: {result.get('error', 'Unknown error')}")
        else:
            print("❌ NanoBanana service is not available")
            print("   Check your API key configuration")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_nanobanana()
```

**Step 2: Run the Test**
```bash
cd backend
python test_nanobanana_integration.py
```

### 5. Update Frontend Integration

**Step 1: Update Enhanced Poster Generator**
In `frontend/src/components/lazy/enhanced-poster-generator.tsx`, ensure NanoBanana is used:

```typescript
// In handleGenerateWithAI function
const aiResponse = await nanoBananaService.generateImage(
  textilePrompt.enhancedPrompt,
  {
    style: selectedStyle,
    aspect_ratio: '1:1',
    quality: 'hd'
  }
);

if (aiResponse.success && aiResponse.image_url) {
  // Use NanoBanana generated image
  setGeneratedPoster({
    url: aiResponse.image_url,
    captions: [
      `Discover our ${selectedFabric || 'textile'} collection`,
      `Perfect for ${selectedOccasion || 'any occasion'}`,
      `Style: ${selectedStyle || 'modern'} design`
    ],
    hashtags: [
      `#${selectedFabric || 'textile'}`,
      `#${selectedStyle || 'modern'}`,
      '#fashion',
      '#design',
      '#textile'
    ],
    metadata: {
      prompt: textilePrompt.enhancedPrompt,
      generated_at: new Date().toISOString(),
      ai_service: 'nanobanana'
    }
  });
  setAiServiceStatus('available');
  showSuccess("AI poster generated successfully!");
}
```

### 6. Verify Configuration

**Step 1: Check Environment Variables**
```bash
# Check if API key is set
echo $NANOBANANA_API_KEY
echo $NEXT_PUBLIC_NANOBANANA_API_KEY
```

**Step 2: Check Django Settings**
```python
# In Django shell
python manage.py shell
>>> from django.conf import settings
>>> print(settings.NANOBANANA_API_KEY)
```

**Step 3: Test API Connection**
```python
# Test API connection
import requests

api_key = "your_api_key_here"
response = requests.get(
    "https://api.nanobanana.ai/v1/models",
    headers={"Authorization": f"Bearer {api_key}"}
)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
```

### 7. Troubleshooting

**Common Issues:**

1. **API Key Not Working**
   - Verify the API key is correct
   - Check if the key has proper permissions
   - Ensure the key is not expired

2. **CORS Issues**
   - Make sure the frontend can access the API
   - Check if the base URL is correct

3. **Rate Limiting**
   - NanoBanana has rate limits
   - Implement proper error handling for rate limits

4. **Network Issues**
   - Check internet connection
   - Verify API endpoint is accessible

### 8. Production Considerations

**Step 1: Environment Variables**
- Use different API keys for development and production
- Store keys securely (use secrets management)
- Never commit API keys to version control

**Step 2: Error Handling**
- Implement proper error handling for API failures
- Add retry logic for transient failures
- Log errors for debugging

**Step 3: Monitoring**
- Monitor API usage and costs
- Set up alerts for API failures
- Track generation success rates

### 9. Expected Results

After proper setup, you should see:
- ✅ NanoBanana service is available
- ✅ Images are generated based on prompts
- ✅ Unique images for each generation
- ✅ Proper error handling and fallbacks
- ✅ Cost tracking and usage monitoring

### 10. Next Steps

1. **Test the Integration**: Run the test script to verify everything works
2. **Update Frontend**: Ensure the frontend uses NanoBanana for generation
3. **Monitor Usage**: Keep track of API usage and costs
4. **Optimize Prompts**: Fine-tune prompts for better results
5. **Add Caching**: Implement caching to reduce API calls

## Summary

To use NanoBanana AI service for image generation:

1. **Get API Key**: Sign up at [https://app.banana.dev/](https://app.banana.dev/) and get your API key
2. **Configure Environment**: Add the API key to your `.env` file
3. **Update Settings**: Configure Django and Next.js settings
4. **Test Integration**: Run the test script to verify everything works
5. **Update Frontend**: Ensure the frontend uses NanoBanana for generation

The system will then use NanoBanana for actual AI image generation according to your prompts, providing unique, high-quality images for your textile design platform.
