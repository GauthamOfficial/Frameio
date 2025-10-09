#!/usr/bin/env python
"""
Simple test for image generation
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

# Set API key
os.environ['NANOBANANA_API_KEY'] = 'AIzaSyBBP1QGjY7lJBhjNwWMSJCIOZC1bWgSzMY'

print("🚀 Testing Image Generation...")

try:
    from ai_services.nanobanana_service import NanoBananaAIService
    print("✅ Import successful")
    
    service = NanoBananaAIService()
    print(f"✅ Service created - API Key: {bool(service.api_key)}")
    
    result = service.generate_poster(
        image_url="https://example.com/fabric.jpg",
        offer_text="Test Offer",
        theme="modern"
    )
    
    print("✅ Image generation result:")
    print(f"   - Success: {result.get('success', False)}")
    print(f"   - Fallback: {result.get('fallback', False)}")
    print(f"   - Image URLs: {len(result.get('image_urls', []))}")
    
    if result.get('image_urls'):
        print(f"   - First URL: {result['image_urls'][0]}")
    
    print("🎉 Image generation test completed successfully!")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()

