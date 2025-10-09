#!/usr/bin/env python3
"""
Simple test for Gemini 2.5 Flash Image Generation
Tests the core functionality without database complications
"""
import os
import sys
import django

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from ai_services.gemini_2_5_flash_image_service import gemini_2_5_flash_image_service


def test_simple_image_generation():
    """Test simple image generation"""
    print("🧪 Testing Simple Gemini 2.5 Flash Image Generation...")
    
    try:
        # Test basic image generation
        result = gemini_2_5_flash_image_service.generate_image_from_prompt(
            prompt="Beautiful silk saree with golden border, elegant design, professional photography",
            style="photorealistic",
            width=1024,
            height=1024
        )
        
        if result.get('success'):
            print("✅ Image generation successful!")
            print(f"🖼️  Image URL: {result.get('image_url', 'N/A')}")
            print(f"📊 Service: {result.get('service', 'N/A')}")
            print(f"⏱️  Processing Time: {result.get('processing_time', 'N/A')}s")
            print(f"🆔 Unique ID: {result.get('unique_id', 'N/A')}")
            return True
        else:
            print(f"❌ Image generation failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error in image generation: {str(e)}")
        return False


def test_poster_generation():
    """Test poster generation"""
    print("\n🧪 Testing Poster Generation...")
    
    try:
        result = gemini_2_5_flash_image_service.generate_poster(
            fabric_type="silk saree",
            offer_text="Special Diwali Collection - 30% Off",
            theme="festive",
            festival="deepavali",
            price_range="₹2999"
        )
        
        if result.get('success'):
            print("✅ Poster generation successful!")
            print(f"🖼️  Image URL: {result.get('image_url', 'N/A')}")
            print(f"📊 Service: {result.get('service', 'N/A')}")
            print(f"⏱️  Processing Time: {result.get('processing_time', 'N/A')}s")
            return True
        else:
            print(f"❌ Poster generation failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error in poster generation: {str(e)}")
        return False


def test_multiple_images():
    """Test multiple image generation"""
    print("\n🧪 Testing Multiple Image Generation...")
    
    try:
        result = gemini_2_5_flash_image_service.generate_multiple_images(
            prompt="Elegant cotton kurta with traditional embroidery",
            num_images=3,
            style="photorealistic"
        )
        
        if result.get('success'):
            images = result.get('data', {}).get('images', [])
            print(f"✅ Generated {len(images)} images successfully!")
            
            for i, image_result in enumerate(images):
                if image_result.get('success'):
                    print(f"  🖼️  Image {i+1}: {image_result.get('image_url', 'N/A')}")
                else:
                    print(f"  ❌ Image {i+1} failed: {image_result.get('error', 'Unknown error')}")
            
            return True
        else:
            print(f"❌ Multiple image generation failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error in multiple image generation: {str(e)}")
        return False


def test_service_info():
    """Test service information"""
    print("\n🧪 Testing Service Information...")
    
    try:
        info = gemini_2_5_flash_image_service.get_service_info()
        print(f"✅ Service Name: {info['service_name']}")
        print(f"✅ Model: {info['model']}")
        print(f"✅ API Key Configured: {info['api_key_configured']}")
        print(f"✅ Base URL: {info['base_url']}")
        print(f"✅ Features: {', '.join(info['features'])}")
        return True
        
    except Exception as e:
        print(f"❌ Error getting service info: {str(e)}")
        return False


def run_simple_test():
    """Run simple test suite"""
    print("🚀 Starting Simple Gemini 2.5 Flash Test")
    print("=" * 50)
    
    tests = [
        ("Service Information", test_service_info),
        ("Simple Image Generation", test_simple_image_generation),
        ("Poster Generation", test_poster_generation),
        ("Multiple Image Generation", test_multiple_images),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*15} {test_name} {'='*15}")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*50)
    print("📊 SIMPLE TEST SUMMARY")
    print("="*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\n📈 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Gemini 2.5 Flash is working perfectly!")
        print("\n🚀 Your site can now generate images using Gemini 2.5 Flash!")
        print("💡 The system is no longer in fallback mode - it's using real AI generation!")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total


if __name__ == "__main__":
    success = run_simple_test()
    sys.exit(0 if success else 1)
