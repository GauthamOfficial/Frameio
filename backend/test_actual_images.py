#!/usr/bin/env python
"""
Test actual image generation and verify URLs work
"""
import os
import sys
import django
import requests
from pathlib import Path

# Setup Django
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

# Set API key
os.environ['NANOBANANA_API_KEY'] = 'AIzaSyBBP1QGjY7lJBhjNwWMSJCIOZC1bWgSzMY'

def test_image_urls():
    """Test if generated image URLs are accessible"""
    print("🧪 Testing Image URL Accessibility...")
    
    try:
        from ai_services.nanobanana_service import NanoBananaAIService
        
        service = NanoBananaAIService()
        print(f"✅ Service initialized - API Key: {bool(service.api_key)}")
        
        # Generate poster
        result = service.generate_poster(
            image_url="https://example.com/fabric.jpg",
            offer_text="Special Deepavali Offer",
            theme="festive"
        )
        
        print(f"✅ Generation result:")
        print(f"   - Success: {result.get('success', False)}")
        print(f"   - Fallback: {result.get('fallback', False)}")
        print(f"   - Image URLs: {len(result.get('image_urls', []))}")
        
        # Test each image URL
        image_urls = result.get('image_urls', [])
        accessible_count = 0
        
        for i, url in enumerate(image_urls):
            print(f"\n📸 Testing image {i+1}: {url}")
            try:
                response = requests.head(url, timeout=10)
                if response.status_code == 200:
                    print(f"   ✅ Accessible (Status: {response.status_code})")
                    accessible_count += 1
                else:
                    print(f"   ❌ Not accessible (Status: {response.status_code})")
            except Exception as e:
                print(f"   ❌ Error accessing: {str(e)}")
        
        print(f"\n📊 Results: {accessible_count}/{len(image_urls)} images accessible")
        return accessible_count > 0
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

def test_textile_specific_images():
    """Test textile-specific image generation"""
    print("\n🧪 Testing Textile-Specific Image Generation...")
    
    try:
        from ai_services.services import NanoBananaTextileService
        
        textile_service = NanoBananaTextileService()
        print("✅ Textile service initialized")
        
        # Test different fabric types
        test_cases = [
            {
                "fabric_type": "silk",
                "festival": "deepavali",
                "theme": "elegant",
                "offer_text": "Luxury Silk Collection"
            },
            {
                "fabric_type": "cotton",
                "festival": "pongal",
                "theme": "traditional",
                "offer_text": "Cotton Comfort Wear"
            }
        ]
        
        total_accessible = 0
        total_images = 0
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📸 Test Case {i}: {test_case['fabric_type']} - {test_case['festival']}")
            
            result = textile_service.generate_textile_poster(
                image_url="https://example.com/fabric.jpg",
                offer_text=test_case['offer_text'],
                theme=test_case['theme'],
                fabric_type=test_case['fabric_type'],
                festival=test_case['festival']
            )
            
            print(f"   - Success: {result.get('success', False)}")
            print(f"   - Textile specific: {result.get('textile_specific', False)}")
            print(f"   - Fabric type: {result.get('fabric_type', 'N/A')}")
            print(f"   - Festival: {result.get('festival', 'N/A')}")
            
            # Test image URLs
            image_urls = result.get('image_urls', [])
            print(f"   - Image URLs: {len(image_urls)}")
            
            for j, url in enumerate(image_urls):
                try:
                    response = requests.head(url, timeout=5)
                    if response.status_code == 200:
                        print(f"     ✅ Image {j+1} accessible")
                        total_accessible += 1
                    else:
                        print(f"     ❌ Image {j+1} not accessible (Status: {response.status_code})")
                except Exception as e:
                    print(f"     ❌ Image {j+1} error: {str(e)}")
                
                total_images += 1
        
        print(f"\n📊 Textile Results: {total_accessible}/{total_images} images accessible")
        return total_accessible > 0
        
    except Exception as e:
        print(f"❌ Textile test failed: {str(e)}")
        return False

def test_fallback_images():
    """Test fallback image generation"""
    print("\n🧪 Testing Fallback Image Generation...")
    
    try:
        from ai_services.nanobanana_service import NanoBananaAIService
        
        # Test with no API key to force fallback
        original_key = os.environ.get('NANOBANANA_API_KEY')
        os.environ['NANOBANANA_API_KEY'] = ''
        
        service = NanoBananaAIService()
        print(f"✅ Fallback service initialized - API Key: {bool(service.api_key)}")
        
        result = service.generate_poster(
            image_url="https://example.com/fabric.jpg",
            offer_text="Fallback Test",
            theme="modern"
        )
        
        print(f"✅ Fallback result:")
        print(f"   - Success: {result.get('success', False)}")
        print(f"   - Fallback: {result.get('fallback', False)}")
        print(f"   - Image URLs: {len(result.get('image_urls', []))}")
        
        # Test fallback image URLs
        image_urls = result.get('image_urls', [])
        accessible_count = 0
        
        for i, url in enumerate(image_urls):
            print(f"\n📸 Testing fallback image {i+1}: {url}")
            try:
                response = requests.head(url, timeout=10)
                if response.status_code == 200:
                    print(f"   ✅ Accessible (Status: {response.status_code})")
                    accessible_count += 1
                else:
                    print(f"   ❌ Not accessible (Status: {response.status_code})")
            except Exception as e:
                print(f"   ❌ Error accessing: {str(e)}")
        
        # Restore API key
        if original_key:
            os.environ['NANOBANANA_API_KEY'] = original_key
        
        print(f"\n📊 Fallback Results: {accessible_count}/{len(image_urls)} images accessible")
        return accessible_count > 0
        
    except Exception as e:
        print(f"❌ Fallback test failed: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 Testing Actual Image Generation")
    print("=" * 50)
    
    tests = [
        ("Basic Image Generation", test_image_urls),
        ("Textile-Specific Generation", test_textile_specific_images),
        ("Fallback Image Generation", test_fallback_images),
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
        print("🎉 All tests passed! Image generation is working with accessible URLs!")
        return True
    else:
        print("⚠️  Some tests failed. Image generation may have issues.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

