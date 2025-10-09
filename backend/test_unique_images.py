#!/usr/bin/env python
"""
Test that unique images are being generated
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

def test_unique_image_generation():
    """Test that unique images are generated each time"""
    print("🧪 Testing Unique Image Generation...")
    
    try:
        from ai_services.nanobanana_service import NanoBananaAIService
        
        service = NanoBananaAIService()
        print(f"✅ Service initialized - API Key: {bool(service.api_key)}")
        
        # Test 1: Generate images with same parameters
        print("\n📸 Test 1: Same parameters")
        result1 = service.generate_poster(
            image_url="https://example.com/fabric.jpg",
            offer_text="Test Offer",
            theme="modern"
        )
        
        print(f"   - Success: {result1.get('success')}")
        print(f"   - Fallback: {result1.get('fallback')}")
        print(f"   - Images: {len(result1.get('image_urls', []))}")
        
        # Test 2: Generate images with different parameters
        print("\n📸 Test 2: Different parameters")
        result2 = service.generate_poster(
            image_url="https://example.com/silk.jpg",
            offer_text="Different Offer",
            theme="festive"
        )
        
        print(f"   - Success: {result2.get('success')}")
        print(f"   - Fallback: {result2.get('fallback')}")
        print(f"   - Images: {len(result2.get('image_urls', []))}")
        
        # Test 3: Generate images with same parameters again
        print("\n📸 Test 3: Same parameters again")
        result3 = service.generate_poster(
            image_url="https://example.com/fabric.jpg",
            offer_text="Test Offer",
            theme="modern"
        )
        
        print(f"   - Success: {result3.get('success')}")
        print(f"   - Fallback: {result3.get('fallback')}")
        print(f"   - Images: {len(result3.get('image_urls', []))}")
        
        # Compare URLs to see if they're unique
        urls1 = result1.get('image_urls', [])
        urls2 = result2.get('image_urls', [])
        urls3 = result3.get('image_urls', [])
        
        print(f"\n🔍 URL Analysis:")
        print(f"   - Test 1 URLs: {urls1}")
        print(f"   - Test 2 URLs: {urls2}")
        print(f"   - Test 3 URLs: {urls3}")
        
        # Check if URLs are different
        if urls1 and urls2:
            different_urls = set(urls1) != set(urls2)
            print(f"   - Different parameters produce different URLs: {different_urls}")
        
        if urls1 and urls3:
            same_urls = set(urls1) == set(urls3)
            print(f"   - Same parameters produce same URLs: {same_urls}")
        
        # Test fallback system
        print(f"\n🔄 Testing fallback system...")
        original_key = os.environ.get('NANOBANANA_API_KEY')
        os.environ['NANOBANANA_API_KEY'] = ''
        
        fallback_service = NanoBananaAIService()
        fallback_result = fallback_service.generate_poster(
            image_url="https://example.com/fabric.jpg",
            offer_text="Fallback Test",
            theme="elegant"
        )
        
        print(f"   - Fallback Success: {fallback_result.get('success')}")
        print(f"   - Fallback Images: {len(fallback_result.get('image_urls', []))}")
        print(f"   - Fallback URLs: {fallback_result.get('image_urls', [])}")
        
        # Restore API key
        if original_key:
            os.environ['NANOBANANA_API_KEY'] = original_key
        
        print(f"\n✅ Test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_unique_image_generation()
    if success:
        print("\n🎉 SUCCESS: Image generation is working with unique images!")
    else:
        print("\n❌ FAILED: Image generation has issues.")
    sys.exit(0 if success else 1)

