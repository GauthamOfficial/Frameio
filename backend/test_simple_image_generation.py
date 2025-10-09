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

# Set API key
os.environ['NANOBANANA_API_KEY'] = 'AIzaSyBBP1QGjY7lJBhjNwWMSJCIOZC1bWgSzMY'

print("🔍 Simple Image Generation Test...")

try:
    # Setup Django
    django.setup()
    print("✅ Django setup successful")
    
    # Test service
    from ai_services.nanobanana_service import NanoBananaAIService
    
    service = NanoBananaAIService()
    print(f"✅ Service created")
    print(f"   - Available: {service.is_available()}")
    print(f"   - API Key: {bool(service.api_key)}")
    print(f"   - Use Fallback: {service.use_fallback}")
    
    # Test image generation
    print("\n📸 Testing image generation...")
    
    result = service.generate_poster(
        image_url='https://example.com/test.jpg',
        offer_text='Special Deepavali Offer - 50% Off!',
        theme='festive'
    )
    
    print(f"✅ Success: {result.get('success', False)}")
    print(f"✅ Fallback: {result.get('fallback', False)}")
    print(f"✅ Images: {len(result.get('image_urls', []))}")
    
    if result.get('image_urls'):
        print("📸 Generated URLs:")
        for i, url in enumerate(result['image_urls']):
            print(f"   {i+1}. {url}")
    else:
        print("❌ No images generated!")
    
    # Test fallback directly
    print("\n🔄 Testing fallback directly...")
    
    fallback_images = service._generate_fallback_images('modern', 'Test Offer')
    print(f"✅ Fallback images: {len(fallback_images)}")
    
    if fallback_images:
        print("📸 Fallback URLs:")
        for i, url in enumerate(fallback_images):
            print(f"   {i+1}. {url}")
    
    print("\n🎉 Test completed!")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()

