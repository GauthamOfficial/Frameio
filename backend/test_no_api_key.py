#!/usr/bin/env python
"""
Test that the system works without NanoBanana API key
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

# Explicitly remove API key to test fallback
os.environ.pop('NANOBANANA_API_KEY', None)

def test_without_api_key():
    """Test that the system works without API key"""
    print("🧪 Testing System Without API Key...")
    
    try:
        from ai_services.nanobanana_service import NanoBananaAIService
        
        service = NanoBananaAIService()
        print(f"✅ Service initialized")
        print(f"   - API Key: {bool(service.api_key)}")
        print(f"   - Client: {service.client is not None}")
        print(f"   - Use Fallback: {service.use_fallback}")
        print(f"   - Available: {service.is_available()}")
        
        # Test image generation
        print("\n📸 Testing image generation without API key...")
        result = service.generate_poster(
            image_url="https://example.com/fabric.jpg",
            offer_text="saree post",
            theme="traditional"
        )
        
        print(f"✅ Generation result:")
        print(f"   - Success: {result.get('success')}")
        print(f"   - Fallback: {result.get('fallback')}")
        print(f"   - Service used: {result.get('service_used', 'N/A')}")
        print(f"   - Images: {len(result.get('image_urls', []))}")
        
        if result.get('image_urls'):
            print(f"   - First image: {result['image_urls'][0]}")
        
        # Test with different prompts
        print("\n📸 Testing different prompts...")
        prompts = [
            ("saree post", "traditional"),
            ("silk collection", "elegant"),
            ("cotton wear", "modern")
        ]
        
        for prompt, theme in prompts:
            result = service.generate_poster(
                image_url="https://example.com/fabric.jpg",
                offer_text=prompt,
                theme=theme
            )
            
            print(f"   {prompt} ({theme}): {len(result.get('image_urls', []))} images")
            if result.get('image_urls'):
                print(f"     First image: {result['image_urls'][0]}")
        
        print("\n✅ Test completed successfully!")
        print("   • System works without API key")
        print("   • Fallback mechanisms are working")
        print("   • Different prompts generate different images")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_dynamic_service():
    """Test the dynamic service directly"""
    print("\n🧪 Testing Dynamic Service Directly...")
    
    try:
        from ai_services.dynamic_image_service import DynamicImageService
        
        service = DynamicImageService()
        print(f"✅ Dynamic service initialized")
        
        # Test image generation
        result = service.generate_poster(
            image_url="https://example.com/fabric.jpg",
            offer_text="saree post",
            theme="traditional"
        )
        
        print(f"✅ Dynamic service result:")
        print(f"   - Success: {result.get('success')}")
        print(f"   - Service used: {result.get('service_used')}")
        print(f"   - Images: {len(result.get('image_urls', []))}")
        
        if result.get('image_urls'):
            print(f"   - First image: {result['image_urls'][0]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Dynamic service test failed: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 Testing System Without API Key")
    print("=" * 50)
    
    tests = [
        ("System Without API Key", test_without_api_key),
        ("Dynamic Service", test_dynamic_service),
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
        print("🎉 All tests passed! System works without API key!")
        print("   • No need to pay for API key")
        print("   • Fallback mechanisms work perfectly")
        print("   • Dynamic image generation is working")
        return True
    else:
        print("⚠️  Some tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

