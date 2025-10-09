#!/usr/bin/env python
"""
Simple test to check image generation
"""
import os
import sys
import django
from pathlib import Path

print("🚀 Starting simple test...")

# Setup Django
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')

try:
    django.setup()
    print("✅ Django setup complete")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)

# Set API key
os.environ['NANOBANANA_API_KEY'] = 'AIzaSyBBP1QGjY7lJBhjNwWMSJCIOZC1bWgSzMY'
print("✅ API key set")

try:
    from ai_services.nanobanana_service import NanoBananaAIService
    print("✅ Import successful")
    
    service = NanoBananaAIService()
    print(f"✅ Service created - API Key: {bool(service.api_key)}")
    
    # Test generation
    result = service.generate_poster(
        image_url="https://example.com/fabric.jpg",
        offer_text="Test Offer",
        theme="modern"
    )
    
    print(f"✅ Generation result:")
    print(f"   - Success: {result.get('success')}")
    print(f"   - Fallback: {result.get('fallback')}")
    print(f"   - Images: {len(result.get('image_urls', []))}")
    
    if result.get('image_urls'):
        for i, url in enumerate(result.get('image_urls', []), 1):
            print(f"   - Image {i}: {url}")
    
    print("🎉 Test completed successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

