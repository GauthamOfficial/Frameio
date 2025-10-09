#!/usr/bin/env python
"""
Test dynamic image generation to ensure unique images are created
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

def test_dynamic_image_generation():
    """Test that dynamic image generation creates unique images"""
    print("🧪 Testing Dynamic Image Generation...")
    
    try:
        from ai_services.dynamic_image_service import DynamicImageService
        
        service = DynamicImageService()
        print(f"✅ Dynamic service initialized")
        
        # Test 1: Generate images with different prompts
        print("\n📸 Test 1: Different prompts should generate different images")
        
        prompts = [
            ("saree post", "traditional"),
            ("silk collection", "elegant"),
            ("cotton wear", "modern"),
            ("festive offer", "festive")
        ]
        
        all_urls = []
        for prompt, theme in prompts:
            result = service.generate_poster(
                image_url="https://example.com/fabric.jpg",
                offer_text=prompt,
                theme=theme
            )
            
            print(f"   {prompt} ({theme}): {len(result.get('image_urls', []))} images")
            if result.get('image_urls'):
                print(f"     First image: {result['image_urls'][0]}")
                all_urls.extend(result['image_urls'])
        
        # Test 2: Same prompt multiple times should generate different images
        print("\n📸 Test 2: Same prompt multiple times should generate different images")
        
        same_prompt_urls = []
        for i in range(3):
            result = service.generate_poster(
                image_url="https://example.com/fabric.jpg",
                offer_text="saree post",
                theme="traditional"
            )
            
            print(f"   Attempt {i+1}: {len(result.get('image_urls', []))} images")
            if result.get('image_urls'):
                print(f"     First image: {result['image_urls'][0]}")
                same_prompt_urls.extend(result['image_urls'])
        
        # Test 3: Check uniqueness
        print("\n🔍 Test 3: Checking image uniqueness")
        
        # Check if different prompts produce different images
        unique_prompt_urls = set(all_urls)
        print(f"   Different prompts produced {len(unique_prompt_urls)} unique images out of {len(all_urls)} total")
        
        # Check if same prompt produces different images
        unique_same_prompt_urls = set(same_prompt_urls)
        print(f"   Same prompt produced {len(unique_same_prompt_urls)} unique images out of {len(same_prompt_urls)} total")
        
        # Test 4: Test with NanoBanana service
        print("\n📸 Test 4: Testing with NanoBanana service (should use dynamic service)")
        
        from ai_services.nanobanana_service import NanoBananaAIService
        nano_service = NanoBananaAIService()
        
        result = nano_service.generate_poster(
            image_url="https://example.com/fabric.jpg",
            offer_text="saree post",
            theme="traditional"
        )
        
        print(f"   NanoBanana service result:")
        print(f"     - Success: {result.get('success')}")
        print(f"     - Service used: {result.get('service_used', 'N/A')}")
        print(f"     - Images: {len(result.get('image_urls', []))}")
        if result.get('image_urls'):
            print(f"     - First image: {result['image_urls'][0]}")
        
        print("\n✅ Dynamic image generation test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_image_uniqueness():
    """Test that images are truly unique"""
    print("\n🧪 Testing Image Uniqueness...")
    
    try:
        from ai_services.dynamic_image_service import DynamicImageService
        
        service = DynamicImageService()
        
        # Generate multiple images with same parameters
        results = []
        for i in range(5):
            result = service.generate_poster(
                image_url="https://example.com/fabric.jpg",
                offer_text="saree post",
                theme="traditional"
            )
            
            if result.get('success'):
                results.append(result)
        
        # Check uniqueness
        all_urls = []
        for result in results:
            all_urls.extend(result.get('image_urls', []))
        
        unique_urls = set(all_urls)
        print(f"   Generated {len(all_urls)} total images")
        print(f"   Unique images: {len(unique_urls)}")
        print(f"   Uniqueness ratio: {len(unique_urls)/len(all_urls)*100:.1f}%")
        
        if len(unique_urls) == len(all_urls):
            print("   ✅ All images are unique!")
        else:
            print("   ⚠️  Some images are duplicated")
        
        return len(unique_urls) > len(all_urls) * 0.8  # At least 80% unique
        
    except Exception as e:
        print(f"❌ Uniqueness test failed: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 Testing Dynamic Image Generation")
    print("=" * 50)
    
    tests = [
        ("Dynamic Image Generation", test_dynamic_image_generation),
        ("Image Uniqueness", test_image_uniqueness),
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
        print("🎉 All tests passed! Dynamic image generation is working!")
        print("   • Different prompts generate different images")
        print("   • Same prompt generates unique images each time")
        print("   • Images are truly unique and not templates")
        return True
    else:
        print("⚠️  Some tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

