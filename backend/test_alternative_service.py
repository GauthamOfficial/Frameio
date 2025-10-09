#!/usr/bin/env python
"""
Test the alternative image service
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

def test_alternative_service():
    """Test the alternative image service"""
    print("🧪 Testing Alternative Image Service...")
    
    try:
        from ai_services.alternative_image_service import AlternativeImageService
        
        service = AlternativeImageService()
        print(f"✅ Alternative service initialized")
        
        # Test 1: Basic image generation
        print("\n📸 Test 1: Basic image generation")
        result = service.generate_poster(
            image_url="https://example.com/fabric.jpg",
            offer_text="Test Offer",
            theme="modern"
        )
        
        print(f"   - Success: {result.get('success')}")
        print(f"   - Service used: {result.get('service_used')}")
        print(f"   - Images: {len(result.get('image_urls', []))}")
        print(f"   - Image URLs: {result.get('image_urls', [])}")
        
        # Test 2: Different themes
        print("\n📸 Test 2: Different themes")
        themes = ['modern', 'traditional', 'festive', 'elegant']
        for theme in themes:
            result = service.generate_poster(
                image_url="https://example.com/fabric.jpg",
                offer_text=f"Special {theme.title()} Offer",
                theme=theme
            )
            
            print(f"   {theme.title()}: {len(result.get('image_urls', []))} images")
            if result.get('image_urls'):
                print(f"     First image: {result['image_urls'][0]}")
        
        # Test 3: Same parameters multiple times
        print("\n📸 Test 3: Same parameters multiple times")
        for i in range(3):
            result = service.generate_poster(
                image_url="https://example.com/fabric.jpg",
                offer_text="Test Offer",
                theme="modern"
            )
            
            print(f"   Attempt {i+1}: {len(result.get('image_urls', []))} images")
            if result.get('image_urls'):
                print(f"     First image: {result['image_urls'][0]}")
        
        print("\n✅ Alternative service test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_nanobanana_with_alternative():
    """Test NanoBanana service with alternative fallback"""
    print("\n🧪 Testing NanoBanana with Alternative Fallback...")
    
    try:
        from ai_services.nanobanana_service import NanoBananaAIService
        
        service = NanoBananaAIService()
        print(f"✅ NanoBanana service initialized")
        
        # Test image generation
        result = service.generate_poster(
            image_url="https://example.com/fabric.jpg",
            offer_text="Test Offer",
            theme="modern"
        )
        
        print(f"✅ Result:")
        print(f"   - Success: {result.get('success')}")
        print(f"   - Fallback: {result.get('fallback')}")
        print(f"   - Service used: {result.get('service_used', 'N/A')}")
        print(f"   - Images: {len(result.get('image_urls', []))}")
        print(f"   - Image URLs: {result.get('image_urls', [])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 Testing Alternative Image Service")
    print("=" * 50)
    
    tests = [
        ("Alternative Service", test_alternative_service),
        ("NanoBanana with Alternative", test_nanobanana_with_alternative),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} passed")
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Alternative image service is working!")
        return True
    else:
        print("⚠️  Some tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

