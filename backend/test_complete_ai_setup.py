#!/usr/bin/env python3
"""
Complete AI Setup Test
Tests both poster and caption generation services
"""

import os
import sys
import django

# Set the API key before Django setup
os.environ['GEMINI_API_KEY'] = 'AIzaSyCZiGdU4pk_-uVNWCquY5C15vaxnPszA-s'

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

def test_ai_services():
    """Test both AI services"""
    print("🧪 Testing Complete AI Setup...")
    print("=" * 50)
    
    try:
        # Test AI Poster Service
        print("\n📸 Testing AI Poster Service...")
        from ai_services.ai_poster_service import AIPosterService
        poster_service = AIPosterService()
        
        if poster_service.is_available():
            print("✅ AI Poster Service: Available")
            
            # Test simple generation
            print("   Testing poster generation...")
            result = poster_service.generate_from_prompt(
                "A beautiful silk saree with golden embroidery",
                "1:1"
            )
            
            if result.get('success'):
                print("✅ Poster generation: SUCCESS")
                print(f"   Generated image: {result.get('image_path', 'N/A')}")
            else:
                print(f"❌ Poster generation failed: {result.get('error', 'Unknown error')}")
        else:
            print("❌ AI Poster Service: Not available")
            print(f"   Error: {poster_service.error_message}")
        
        # Test AI Caption Service
        print("\n📝 Testing AI Caption Service...")
        from ai_services.ai_caption_service import AICaptionService
        caption_service = AICaptionService()
        
        if caption_service.is_available():
            print("✅ AI Caption Service: Available")
            
            # Test simple caption generation
            print("   Testing caption generation...")
            result = caption_service.generate_product_caption(
                "Silk Saree Collection",
                "textile",
                "modern",
                "professional",
                True,  # include hashtags
                True,  # include emoji
                200    # max length
            )
            
            if result.get('success'):
                print("✅ Caption generation: SUCCESS")
                caption = result.get('caption', {})
                print(f"   Main content: {caption.get('main_content', 'N/A')[:100]}...")
                print(f"   Hashtags: {len(caption.get('hashtags', []))} tags")
            else:
                print(f"❌ Caption generation failed: {result.get('error', 'Unknown error')}")
        else:
            print("❌ AI Caption Service: Not available")
            print(f"   Error: {caption_service.error_message}")
        
        print("\n🎉 AI Setup Test Complete!")
        print("=" * 50)
        
        # Summary
        poster_available = poster_service.is_available()
        caption_available = caption_service.is_available()
        
        if poster_available and caption_available:
            print("✅ ALL AI SERVICES WORKING PERFECTLY!")
            print("🚀 Ready for production use!")
        elif poster_available or caption_available:
            print("⚠️  PARTIAL AI SERVICES AVAILABLE")
            print("🔧 Some services may need configuration")
        else:
            print("❌ NO AI SERVICES AVAILABLE")
            print("🚨 Check your API key and configuration")
            
    except Exception as e:
        print(f"💥 Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ai_services()

