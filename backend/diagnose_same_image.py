#!/usr/bin/env python
"""
Diagnose why the same image is still showing
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

# Force no API key to test fallback
os.environ['NANOBANANA_API_KEY'] = ''

def diagnose_image_generation():
    """Diagnose why same image is showing"""
    print("🔍 Diagnosing Image Generation Issue...")
    
    try:
        from ai_services.nanobanana_service import NanoBananaAIService
        
        service = NanoBananaAIService()
        print(f"✅ Service initialized")
        print(f"   - API Key: {bool(service.api_key)}")
        print(f"   - Client: {service.client is not None}")
        print(f"   - Use Fallback: {service.use_fallback}")
        print(f"   - Available: {service.is_available()}")
        
        # Test 1: Generate same prompt multiple times
        print("\n📸 Test 1: Same prompt multiple times")
        for i in range(3):
            result = service.generate_poster(
                image_url="https://example.com/fabric.jpg",
                offer_text="saree post",
                theme="traditional"
            )
            
            print(f"   Attempt {i+1}:")
            print(f"     - Success: {result.get('success')}")
            print(f"     - Fallback: {result.get('fallback')}")
            print(f"     - Service used: {result.get('service_used', 'N/A')}")
            print(f"     - Images: {len(result.get('image_urls', []))}")
            if result.get('image_urls'):
                print(f"     - First image: {result['image_urls'][0]}")
        
        # Test 2: Different prompts
        print("\n📸 Test 2: Different prompts")
        prompts = [
            ("saree post", "traditional"),
            ("silk collection", "elegant"),
            ("cotton wear", "modern")
        ]
        
        all_urls = []
        for prompt, theme in prompts:
            result = service.generate_poster(
                image_url="https://example.com/fabric.jpg",
                offer_text=prompt,
                theme=theme
            )
            
            print(f"   {prompt} ({theme}):")
            print(f"     - Success: {result.get('success')}")
            print(f"     - Images: {len(result.get('image_urls', []))}")
            if result.get('image_urls'):
                print(f"     - First image: {result['image_urls'][0]}")
                all_urls.extend(result['image_urls'])
        
        # Test 3: Check uniqueness
        print(f"\n🔍 Uniqueness Analysis:")
        print(f"   - Total URLs generated: {len(all_urls)}")
        unique_urls = set(all_urls)
        print(f"   - Unique URLs: {len(unique_urls)}")
        print(f"   - Uniqueness ratio: {len(unique_urls)/len(all_urls)*100:.1f}%")
        
        if len(unique_urls) == len(all_urls):
            print("   ✅ All images are unique!")
        else:
            print("   ❌ Some images are duplicated")
            print(f"   - Duplicated URLs: {len(all_urls) - len(unique_urls)}")
        
        # Test 4: Check cache
        print(f"\n🔍 Cache Analysis:")
        from django.core.cache import cache
        try:
            cache.clear()
            print("   - Cache cleared")
        except Exception as e:
            print(f"   - Cache clear failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Diagnosis failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_dynamic_service_directly():
    """Test dynamic service directly"""
    print("\n🧪 Testing Dynamic Service Directly...")
    
    try:
        from ai_services.dynamic_image_service import DynamicImageService
        
        service = DynamicImageService()
        print(f"✅ Dynamic service initialized")
        
        # Test with different prompts
        prompts = [
            ("saree post", "traditional"),
            ("silk collection", "elegant"),
            ("cotton wear", "modern")
        ]
        
        all_urls = []
        for prompt, theme in prompts:
            result = service.generate_poster(
                image_url="https://example.com/fabric.jpg",
                offer_text=prompt,
                theme=theme
            )
            
            print(f"   {prompt} ({theme}):")
            print(f"     - Success: {result.get('success')}")
            print(f"     - Service used: {result.get('service_used')}")
            print(f"     - Images: {len(result.get('image_urls', []))}")
            if result.get('image_urls'):
                print(f"     - First image: {result['image_urls'][0]}")
                all_urls.extend(result['image_urls'])
        
        # Check uniqueness
        unique_urls = set(all_urls)
        print(f"\n   - Total URLs: {len(all_urls)}")
        print(f"   - Unique URLs: {len(unique_urls)}")
        print(f"   - Uniqueness ratio: {len(unique_urls)/len(all_urls)*100:.1f}%")
        
        return len(unique_urls) > len(all_urls) * 0.8
        
    except Exception as e:
        print(f"❌ Dynamic service test failed: {str(e)}")
        return False

def test_alternative_service_directly():
    """Test alternative service directly"""
    print("\n🧪 Testing Alternative Service Directly...")
    
    try:
        from ai_services.alternative_image_service import AlternativeImageService
        
        service = AlternativeImageService()
        print(f"✅ Alternative service initialized")
        
        # Test with different prompts
        prompts = [
            ("saree post", "traditional"),
            ("silk collection", "elegant"),
            ("cotton wear", "modern")
        ]
        
        all_urls = []
        for prompt, theme in prompts:
            result = service.generate_poster(
                image_url="https://example.com/fabric.jpg",
                offer_text=prompt,
                theme=theme
            )
            
            print(f"   {prompt} ({theme}):")
            print(f"     - Success: {result.get('success')}")
            print(f"     - Service used: {result.get('service_used')}")
            print(f"     - Images: {len(result.get('image_urls', []))}")
            if result.get('image_urls'):
                print(f"     - First image: {result['image_urls'][0]}")
                all_urls.extend(result['image_urls'])
        
        # Check uniqueness
        unique_urls = set(all_urls)
        print(f"\n   - Total URLs: {len(all_urls)}")
        print(f"   - Unique URLs: {len(unique_urls)}")
        print(f"   - Uniqueness ratio: {len(unique_urls)/len(all_urls)*100:.1f}%")
        
        return len(unique_urls) > len(all_urls) * 0.8
        
    except Exception as e:
        print(f"❌ Alternative service test failed: {str(e)}")
        return False

def main():
    """Main diagnostic function"""
    print("🚀 Diagnosing Same Image Issue")
    print("=" * 50)
    
    tests = [
        ("Image Generation Diagnosis", diagnose_image_generation),
        ("Dynamic Service Test", test_dynamic_service_directly),
        ("Alternative Service Test", test_alternative_service_directly),
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
    print(f"📊 Diagnostic Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system should be generating unique images!")
    else:
        print("⚠️  Some tests failed. This explains why the same image is showing.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

