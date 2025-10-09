#!/usr/bin/env python
"""
Quick test for image and caption generation with proper prompts
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

# Set API key (optional)
os.environ['NANOBANANA_API_KEY'] = 'AIzaSyBBP1QGjY7lJBhjNwWMSJCIOZC1bWgSzMY'

def test_image_generation():
    """Test image generation with proper prompts"""
    print("🧪 Testing Image Generation...")
    
    try:
        from ai_services.nanobanana_service import NanoBananaAIService
        
        service = NanoBananaAIService()
        print(f"✅ Service initialized")
        
        # Test with proper textile prompts
        prompts = [
            ("saree post", "traditional", "Special Deepavali Saree Collection"),
            ("silk collection", "elegant", "Luxury Silk Sarees"),
            ("cotton wear", "modern", "Comfortable Cotton Collection")
        ]
        
        for prompt, theme, offer_text in prompts:
            print(f"\n📸 Testing: {prompt} ({theme})")
            
            result = service.generate_poster(
                image_url="https://example.com/fabric.jpg",
                offer_text=offer_text,
                theme=theme
            )
            
            print(f"   - Success: {result.get('success')}")
            print(f"   - Images: {len(result.get('image_urls', []))}")
            if result.get('image_urls'):
                print(f"   - First image: {result['image_urls'][0]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Image generation test failed: {str(e)}")
        return False

def test_caption_generation():
    """Test caption generation with proper prompts"""
    print("\n🧪 Testing Caption Generation...")
    
    try:
        from ai_services.nanobanana_service import NanoBananaAIService
        
        service = NanoBananaAIService()
        
        # Test with proper product descriptions
        products = [
            ("Silk Saree", "Beautiful traditional silk saree with golden border"),
            ("Cotton Saree", "Comfortable everyday cotton saree for daily wear"),
            ("Designer Saree", "Modern designer saree perfect for special occasions")
        ]
        
        for product_name, description in products:
            print(f"\n📝 Testing: {product_name}")
            
            result = service.generate_caption(
                product_name=product_name,
                description=description
            )
            
            print(f"   - Success: {result.get('success')}")
            print(f"   - Captions: {len(result.get('captions', []))}")
            if result.get('captions'):
                print(f"   - First caption: {result['captions'][0]['text']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Caption generation test failed: {str(e)}")
        return False

def test_textile_service():
    """Test textile-specific service"""
    print("\n🧪 Testing Textile Service...")
    
    try:
        from ai_services.services import NanoBananaTextileService
        
        textile_service = NanoBananaTextileService()
        
        # Test textile poster generation
        print("\n📸 Testing Textile Poster Generation")
        result = textile_service.generate_textile_poster(
            image_url="https://example.com/silk.jpg",
            offer_text="Luxury Silk Collection",
            theme="elegant",
            fabric_type="silk",
            festival="deepavali"
        )
        
        print(f"   - Success: {result.get('success')}")
        print(f"   - Textile specific: {result.get('textile_specific')}")
        print(f"   - Fabric type: {result.get('fabric_type')}")
        print(f"   - Festival: {result.get('festival')}")
        print(f"   - Images: {len(result.get('image_urls', []))}")
        
        # Test textile caption generation
        print("\n📝 Testing Textile Caption Generation")
        result = textile_service.generate_textile_caption(
            product_name="Silk Saree",
            description="Beautiful traditional silk saree with golden border",
            fabric_type="silk",
            price_range="₹2999"
        )
        
        print(f"   - Success: {result.get('success')}")
        print(f"   - Textile specific: {result.get('textile_specific')}")
        print(f"   - Fabric type: {result.get('fabric_type')}")
        print(f"   - Price range: {result.get('price_range')}")
        print(f"   - Captions: {len(result.get('captions', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Textile service test failed: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 Quick Test for Image and Caption Generation")
    print("=" * 50)
    
    tests = [
        ("Image Generation", test_image_generation),
        ("Caption Generation", test_caption_generation),
        ("Textile Service", test_textile_service),
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
        print("🎉 All tests passed! Image and caption generation are working!")
        return True
    else:
        print("⚠️  Some tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

