#!/usr/bin/env python
"""
Final AI Services Test with Provided API Key
Test all AI poster and caption generation functionality
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

# Set the API key from environment or use placeholder
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("WARNING: GEMINI_API_KEY not set. Using placeholder for testing.")
    api_key = 'your_gemini_api_key_here'
os.environ['GEMINI_API_KEY'] = api_key

def test_ai_poster_generation():
    """Test AI poster generation functionality"""
    print("🎨 Testing AI Poster Generation...")
    
    try:
        from ai_services.ai_poster_service import AIPosterService
        
        service = AIPosterService()
        
        if not service.is_available():
            print("   ❌ AI Poster Service not available")
            return False
        
        print("   ✅ AI Poster Service initialized successfully")
        
        # Test text-to-image generation
        print("   🖼️ Testing text-to-image generation...")
        result = service.generate_from_prompt(
            prompt="Create a modern textile poster for a silk saree brand. Include elegant typography and deep red tones.",
            aspect_ratio="4:5"
        )
        
        if result.get('status') == 'success':
            print("   ✅ Text-to-image generation successful!")
            print(f"   📁 Generated file: {result.get('filename')}")
            print(f"   🔗 Image URL: {result.get('image_url')}")
            return True
        else:
            print(f"   ❌ Text-to-image generation failed: {result.get('message')}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing poster generation: {str(e)}")
        return False

def test_ai_caption_generation():
    """Test AI caption generation functionality"""
    print("\n📝 Testing AI Caption Generation...")
    
    try:
        from ai_services.ai_caption_service import AICaptionService
        
        service = AICaptionService()
        
        if not service.is_available():
            print("   ❌ AI Caption Service not available")
            return False
        
        print("   ✅ AI Caption Service initialized successfully")
        
        # Test product caption generation
        print("   🏷️ Testing product caption generation...")
        result = service.generate_product_caption(
            product_name="Silk Saree Collection",
            product_type="saree",
            style="modern",
            tone="professional",
            include_hashtags=True,
            include_emoji=True,
            max_length=200
        )
        
        if result.get('status') == 'success':
            print("   ✅ Product caption generation successful!")
            caption = result.get('caption', {})
            print(f"   📝 Caption: {caption.get('main_content', '')[:100]}...")
            print(f"   #️⃣ Hashtags: {caption.get('hashtags', [])}")
            return True
        else:
            print(f"   ❌ Product caption generation failed: {result.get('message')}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing caption generation: {str(e)}")
        return False

def test_social_media_caption():
    """Test social media caption generation"""
    print("\n📱 Testing Social Media Caption Generation...")
    
    try:
        from ai_services.ai_caption_service import AICaptionService
        
        service = AICaptionService()
        
        # Test social media caption generation
        result = service.generate_social_media_caption(
            content="New silk collection launch with elegant designs",
            platform="instagram",
            post_type="product_showcase",
            style="engaging",
            tone="friendly",
            include_hashtags=True,
            include_emoji=True,
            call_to_action=True
        )
        
        if result.get('status') == 'success':
            print("   ✅ Social media caption generation successful!")
            caption = result.get('caption', {})
            print(f"   📱 Caption: {caption.get('main_content', '')[:100]}...")
            print(f"   📞 CTA: {caption.get('call_to_action', '')}")
            return True
        else:
            print(f"   ❌ Social media caption generation failed: {result.get('message')}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing social media caption: {str(e)}")
        return False

def test_bulk_captions():
    """Test bulk caption generation"""
    print("\n📦 Testing Bulk Caption Generation...")
    
    try:
        from ai_services.ai_caption_service import AICaptionService
        
        service = AICaptionService()
        
        products = [
            {"name": "Silk Saree", "type": "saree"},
            {"name": "Cotton Kurta", "type": "kurta"},
            {"name": "Linen Dress", "type": "dress"}
        ]
        
        result = service.generate_bulk_captions(
            products=products,
            caption_style="consistent",
            brand_voice="professional"
        )
        
        if result.get('status') == 'success':
            print("   ✅ Bulk caption generation successful!")
            captions = result.get('captions', [])
            print(f"   📊 Generated {len(captions)} captions")
            for i, caption in enumerate(captions[:2]):
                print(f"   📝 Product {i+1}: {caption.get('caption', '')[:60]}...")
            return True
        else:
            print(f"   ❌ Bulk caption generation failed: {result.get('message')}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing bulk captions: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 Final AI Services Test")
    print("=" * 50)
    print("🔑 Using API key from environment variables")
    print("=" * 50)
    
    tests = [
        ("AI Poster Generation", test_ai_poster_generation),
        ("AI Caption Generation", test_ai_caption_generation),
        ("Social Media Caption", test_social_media_caption),
        ("Bulk Caption Generation", test_bulk_captions)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed_tests += 1
                print(f"✅ {test_name} - PASSED")
            else:
                print(f"❌ {test_name} - FAILED")
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {str(e)}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED!")
        print("\n✅ AI Services are fully functional and ready for production!")
        print("\n📋 Available Endpoints:")
        print("   • POST /api/ai-poster/generate_poster/")
        print("   • POST /api/ai-poster/edit_poster/")
        print("   • POST /api/ai-poster/composite_poster/")
        print("   • POST /api/ai-caption/product_caption/")
        print("   • POST /api/ai-caption/social_media_caption/")
        print("   • POST /api/ai-caption/image_caption/")
        print("   • POST /api/ai-caption/bulk_captions/")
        print("\n🚀 Start generating AI content for your textile platform!")
        return True
    else:
        print("❌ SOME TESTS FAILED!")
        print("🔧 Check the error messages above and fix any issues.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

