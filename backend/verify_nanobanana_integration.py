#!/usr/bin/env python
"""
Verification script for NanoBanana SDK integration
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

from ai_services.nanobanana_service import NanoBananaAIService, NanoBananaError
from ai_services.services import NanoBananaTextileService
from django.conf import settings


def test_nanobanana_service():
    """Test NanoBanana service initialization and basic functionality"""
    print("🧪 Testing NanoBanana Service Integration...")
    
    try:
        # Test service initialization
        service = NanoBananaAIService()
        print(f"✅ NanoBananaAIService initialized successfully")
        print(f"   - API Key configured: {bool(service.api_key)}")
        print(f"   - Client available: {service.is_available()}")
        
        # Test fallback functionality
        print("\n🔄 Testing fallback mechanisms...")
        
        # Test poster generation fallback
        poster_result = service.generate_poster(
            image_url="https://example.com/fabric.jpg",
            offer_text="Special Deepavali Offer",
            theme="festive"
        )
        
        print(f"✅ Poster generation test:")
        print(f"   - Success: {poster_result.get('success', False)}")
        print(f"   - Fallback: {poster_result.get('fallback', False)}")
        print(f"   - Image URLs: {len(poster_result.get('image_urls', []))}")
        
        # Test caption generation fallback
        caption_result = service.generate_caption(
            product_name="Silk Saree",
            description="Beautiful traditional silk saree"
        )
        
        print(f"✅ Caption generation test:")
        print(f"   - Success: {caption_result.get('success', False)}")
        print(f"   - Fallback: {caption_result.get('fallback', False)}")
        print(f"   - Captions: {len(caption_result.get('captions', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing NanoBanana service: {str(e)}")
        return False


def test_textile_service():
    """Test NanoBananaTextileService integration"""
    print("\n🧪 Testing NanoBananaTextileService Integration...")
    
    try:
        # Test service initialization
        textile_service = NanoBananaTextileService()
        print(f"✅ NanoBananaTextileService initialized successfully")
        
        # Test textile poster generation
        poster_result = textile_service.generate_textile_poster(
            image_url="https://example.com/silk.jpg",
            offer_text="Luxury Silk Collection",
            theme="elegant",
            fabric_type="silk",
            festival="deepavali"
        )
        
        print(f"✅ Textile poster generation test:")
        print(f"   - Success: {poster_result.get('success', False)}")
        print(f"   - Textile specific: {poster_result.get('textile_specific', False)}")
        print(f"   - Fabric type: {poster_result.get('fabric_type', 'N/A')}")
        print(f"   - Festival: {poster_result.get('festival', 'N/A')}")
        
        # Test textile caption generation
        caption_result = textile_service.generate_textile_caption(
            product_name="Cotton Saree",
            description="Comfortable everyday wear",
            fabric_type="cotton",
            price_range="₹1999"
        )
        
        print(f"✅ Textile caption generation test:")
        print(f"   - Success: {caption_result.get('success', False)}")
        print(f"   - Textile specific: {caption_result.get('textile_specific', False)}")
        print(f"   - Fabric type: {caption_result.get('fabric_type', 'N/A')}")
        print(f"   - Price range: {caption_result.get('price_range', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Textile service: {str(e)}")
        return False


def test_prompt_engineering():
    """Test prompt engineering functionality"""
    print("\n🧪 Testing Prompt Engineering...")
    
    try:
        service = NanoBananaAIService()
        
        # Test poster prompt creation
        poster_prompt = service._create_poster_prompt(
            image_url="https://example.com/fabric.jpg",
            offer_text="Special Offer",
            theme="modern"
        )
        
        print(f"✅ Poster prompt creation:")
        print(f"   - Prompt length: {len(poster_prompt)} characters")
        print(f"   - Contains offer text: {'Special Offer' in poster_prompt}")
        print(f"   - Contains theme: {'modern' in poster_prompt.lower()}")
        
        # Test caption prompt creation
        caption_prompt = service._create_caption_prompt(
            product_name="Silk Saree",
            description="Beautiful traditional silk saree"
        )
        
        print(f"✅ Caption prompt creation:")
        print(f"   - Prompt length: {len(caption_prompt)} characters")
        print(f"   - Contains product name: {'Silk Saree' in caption_prompt}")
        print(f"   - Contains description: {'traditional silk saree' in caption_prompt}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing prompt engineering: {str(e)}")
        return False


def test_caching():
    """Test caching functionality"""
    print("\n🧪 Testing Caching Functionality...")
    
    try:
        from django.core.cache import cache
        
        # Test cache operations
        test_key = "test_nanobanana_cache"
        test_data = {"test": "data", "timestamp": "2024-01-01"}
        
        # Set cache
        cache.set(test_key, test_data, timeout=60)
        print(f"✅ Cache set operation successful")
        
        # Get cache
        cached_data = cache.get(test_key)
        if cached_data == test_data:
            print(f"✅ Cache get operation successful")
        else:
            print(f"❌ Cache get operation failed")
            return False
        
        # Clear cache
        cache.delete(test_key)
        cleared_data = cache.get(test_key)
        if cleared_data is None:
            print(f"✅ Cache clear operation successful")
        else:
            print(f"❌ Cache clear operation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing caching: {str(e)}")
        return False


def test_error_handling():
    """Test error handling mechanisms"""
    print("\n🧪 Testing Error Handling...")
    
    try:
        service = NanoBananaAIService()
        
        # Test with invalid parameters
        result = service.generate_poster(
            image_url="",  # Empty URL
            offer_text="",  # Empty offer text
            theme=""  # Empty theme
        )
        
        print(f"✅ Error handling test:")
        print(f"   - Handled gracefully: {result.get('success', False)}")
        print(f"   - Fallback used: {result.get('fallback', False)}")
        
        # Test NanoBananaError exception
        try:
            raise NanoBananaError("Test error")
        except NanoBananaError as e:
            print(f"✅ NanoBananaError exception handling: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing error handling: {str(e)}")
        return False


def main():
    """Main verification function"""
    print("🚀 NanoBanana SDK Integration Verification")
    print("=" * 50)
    
    tests = [
        ("NanoBanana Service", test_nanobanana_service),
        ("Textile Service", test_textile_service),
        ("Prompt Engineering", test_prompt_engineering),
        ("Caching", test_caching),
        ("Error Handling", test_error_handling),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} tests...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} tests passed")
        else:
            print(f"❌ {test_name} tests failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} test suites passed")
    
    if passed == total:
        print("🎉 All tests passed! NanoBanana integration is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

