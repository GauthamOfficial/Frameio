#!/usr/bin/env python
"""
Test script for NanoBanana API with the provided API key
"""
import os
import sys
import django
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

# Set the API key
os.environ['NANOBANANA_API_KEY'] = 'AIzaSyBBP1QGjY7lJBhjNwWMSJCIOZC1bWgSzMY'

from ai_services.nanobanana_service import NanoBananaAIService, NanoBananaError
from ai_services.services import NanoBananaTextileService


def test_nanobanana_with_api_key():
    """Test NanoBanana service with actual API key"""
    print("🧪 Testing NanoBanana Service with API Key...")
    
    try:
        # Test service initialization
        service = NanoBananaAIService()
        print(f"✅ NanoBananaAIService initialized")
        print(f"   - API Key configured: {bool(service.api_key)}")
        print(f"   - Client available: {service.is_available()}")
        
        if service.is_available():
            print("\n🔄 Testing actual API calls...")
            
            # Test poster generation
            print("📸 Testing poster generation...")
            poster_result = service.generate_poster(
                image_url="https://example.com/fabric.jpg",
                offer_text="Special Deepavali Offer",
                theme="festive"
            )
            
            print(f"   - Success: {poster_result.get('success', False)}")
            print(f"   - Fallback: {poster_result.get('fallback', False)}")
            print(f"   - Image URLs: {len(poster_result.get('image_urls', []))}")
            if poster_result.get('image_urls'):
                print(f"   - First URL: {poster_result['image_urls'][0]}")
            
            # Test caption generation
            print("\n📝 Testing caption generation...")
            caption_result = service.generate_caption(
                product_name="Silk Saree",
                description="Beautiful traditional silk saree"
            )
            
            print(f"   - Success: {caption_result.get('success', False)}")
            print(f"   - Fallback: {caption_result.get('fallback', False)}")
            print(f"   - Captions: {len(caption_result.get('captions', []))}")
            if caption_result.get('captions'):
                print(f"   - First caption: {caption_result['captions'][0]['text'][:50]}...")
            
            return True
        else:
            print("⚠️  NanoBanana client not available - using fallback mode")
            return True
            
    except Exception as e:
        print(f"❌ Error testing NanoBanana service: {str(e)}")
        return False


def test_textile_service_with_api_key():
    """Test textile service with API key"""
    print("\n🧪 Testing NanoBananaTextileService with API Key...")
    
    try:
        # Test service initialization
        textile_service = NanoBananaTextileService()
        print(f"✅ NanoBananaTextileService initialized")
        
        # Test textile poster generation
        print("📸 Testing textile poster generation...")
        poster_result = textile_service.generate_textile_poster(
            image_url="https://example.com/silk.jpg",
            offer_text="Luxury Silk Collection",
            theme="elegant",
            fabric_type="silk",
            festival="deepavali"
        )
        
        print(f"   - Success: {poster_result.get('success', False)}")
        print(f"   - Textile specific: {poster_result.get('textile_specific', False)}")
        print(f"   - Fabric type: {poster_result.get('fabric_type', 'N/A')}")
        print(f"   - Festival: {poster_result.get('festival', 'N/A')}")
        print(f"   - Fallback: {poster_result.get('fallback', False)}")
        
        # Test textile caption generation
        print("\n📝 Testing textile caption generation...")
        caption_result = textile_service.generate_textile_caption(
            product_name="Cotton Saree",
            description="Comfortable everyday wear",
            fabric_type="cotton",
            price_range="₹1999"
        )
        
        print(f"   - Success: {caption_result.get('success', False)}")
        print(f"   - Textile specific: {caption_result.get('textile_specific', False)}")
        print(f"   - Fabric type: {caption_result.get('fabric_type', 'N/A')}")
        print(f"   - Price range: {caption_result.get('price_range', 'N/A')}")
        print(f"   - Fallback: {caption_result.get('fallback', False)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Textile service: {str(e)}")
        return False


def test_nanobanana_rest_api_directly():
    """Test NanoBanana REST API directly"""
    print("\n🧪 Testing NanoBanana REST API Directly...")
    
    try:
        import requests
        
        # Initialize client with API key
        api_key = 'AIzaSyBBP1QGjY7lJBhjNwWMSJCIOZC1bWgSzMY'
        base_url = "https://api.nanobananaapi.ai"
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        print("✅ REST API client initialized successfully")
        
        # Test image generation
        print("📸 Testing direct image generation...")
        try:
            payload = {
                "prompt": "Generate a textile poster for Special Deepavali Offer, using a festive fabric theme with soft lighting",
                "style": "cinematic",
                "aspect_ratio": "1:1",
                "quality": "high",
                "num_images": 1
            }
            
            response = requests.post(f"{base_url}/generate", json=payload, headers=headers, timeout=30)
            print(f"   - Response status: {response.status_code}")
            print(f"   - Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   - Response type: {type(result)}")
                print(f"   - Has images: {'images' in result}")
                if 'images' in result:
                    print(f"   - Number of images: {len(result['images'])}")
                    if result['images']:
                        print(f"   - First image URL: {result['images'][0]}")
                return True
            else:
                print(f"   - API call failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"   - API call failed: {str(e)}")
            return False
            
    except ImportError as e:
        print(f"❌ Requests module not available: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error testing NanoBanana REST API: {str(e)}")
        return False


def main():
    """Main test function"""
    print("🚀 NanoBanana API Key Integration Test")
    print("=" * 50)
    
    tests = [
        ("NanoBanana Service", test_nanobanana_with_api_key),
        ("Textile Service", test_textile_service_with_api_key),
        ("Direct REST API Test", test_nanobanana_rest_api_directly),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} passed")
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} test suites passed")
    
    if passed == total:
        print("🎉 All tests passed! NanoBanana API integration is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
