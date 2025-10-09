#!/usr/bin/env python
"""
Debug image generation functionality
"""
import os
import sys
import django
from pathlib import Path

# Setup Django properly
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')

# Set API key
os.environ['NANOBANANA_API_KEY'] = 'AIzaSyBBP1QGjY7lJBhjNwWMSJCIOZC1bWgSzMY'

print("🔍 Debugging Image Generation...")

try:
    # Setup Django
    django.setup()
    print("✅ Django setup successful")
    
    # Test 1: Check service initialization
    print("\n🔧 Testing NanoBanana service initialization...")
    
    from ai_services.nanobanana_service import NanoBananaAIService
    
    service = NanoBananaAIService()
    print(f"   - Service created: ✅")
    print(f"   - Available: {service.is_available()}")
    print(f"   - API Key: {'✅ Configured' if service.api_key else '❌ Not configured'}")
    print(f"   - Use Fallback: {service.use_fallback}")
    print(f"   - Client: {'✅ Initialized' if service.client else '❌ Not initialized'}")
    
    # Test 2: Test poster generation
    print("\n📸 Testing poster generation...")
    
    result = service.generate_poster(
        image_url='https://example.com/test-fabric.jpg',
        offer_text='Special Deepavali Offer - 50% Off!',
        theme='festive'
    )
    
    print(f"   - Success: {result.get('success', False)}")
    print(f"   - Fallback: {result.get('fallback', False)}")
    print(f"   - Images: {len(result.get('image_urls', []))}")
    print(f"   - Generation ID: {result.get('generation_id', 'None')}")
    print(f"   - Cost: {result.get('cost', 0)}")
    
    if result.get('image_urls'):
        print("   - Generated URLs:")
        for i, url in enumerate(result['image_urls']):
            print(f"     {i+1}. {url}")
    else:
        print("   ❌ No image URLs generated!")
    
    # Test 3: Test different themes
    print("\n🎨 Testing different themes...")
    
    themes = ['modern', 'traditional', 'festive', 'elegant']
    for theme in themes:
        print(f"   - Testing {theme} theme...")
        theme_result = service.generate_poster(
            image_url='https://example.com/test.jpg',
            offer_text=f'Special {theme.title()} Offer',
            theme=theme
        )
        
        success = theme_result.get('success', False)
        image_count = len(theme_result.get('image_urls', []))
        fallback = theme_result.get('fallback', False)
        
        print(f"     Success: {success}")
        print(f"     Images: {image_count}")
        print(f"     Fallback: {fallback}")
        
        if theme_result.get('image_urls'):
            print(f"     First URL: {theme_result['image_urls'][0]}")
    
    # Test 4: Test caption generation
    print("\n📝 Testing caption generation...")
    
    caption_result = service.generate_caption(
        product_name='Luxury Silk Saree',
        description='Beautiful traditional silk saree with intricate designs'
    )
    
    print(f"   - Success: {caption_result.get('success', False)}")
    print(f"   - Fallback: {caption_result.get('fallback', False)}")
    print(f"   - Captions: {len(caption_result.get('captions', []))}")
    
    if caption_result.get('captions'):
        print("   - Sample captions:")
        for i, caption in enumerate(caption_result['captions'][:2]):
            print(f"     {i+1}. {caption['text']}")
    
    # Test 5: Check fallback image generation directly
    print("\n🔄 Testing fallback image generation directly...")
    
    fallback_images = service._generate_fallback_images('modern', 'Test Offer')
    print(f"   - Fallback images generated: {len(fallback_images)}")
    
    if fallback_images:
        print("   - Fallback URLs:")
        for i, url in enumerate(fallback_images):
            print(f"     {i+1}. {url}")
    
    # Test 6: Check if URLs are actually accessible
    print("\n🌐 Testing URL accessibility...")
    
    import requests
    
    if result.get('image_urls'):
        for i, url in enumerate(result['image_urls'][:2]):  # Test first 2 URLs
            try:
                print(f"   - Testing URL {i+1}: {url[:50]}...")
                response = requests.get(url, timeout=10)
                print(f"     Status: {response.status_code}")
                if response.status_code == 200:
                    print(f"     ✅ URL {i+1} is accessible")
                else:
                    print(f"     ❌ URL {i+1} returned status {response.status_code}")
            except Exception as e:
                print(f"     ❌ URL {i+1} error: {str(e)[:50]}...")
    
    print("\n🎉 Debug test completed!")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()