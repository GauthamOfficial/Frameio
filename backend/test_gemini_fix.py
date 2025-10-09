#!/usr/bin/env python3
"""
Test Gemini fix with proper Django setup
"""
import os
import sys
import django
from django.conf import settings

# Setup Django properly
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

def test_gemini_import():
    """Test if Gemini service can be imported"""
    print("🔧 Testing Gemini Service Import...")
    
    try:
        from ai_services.gemini_service import GeminiService
        print("✅ Gemini service imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import failed: {str(e)}")
        return False

def test_gemini_initialization():
    """Test Gemini service initialization"""
    print("\n🤖 Testing Gemini Service Initialization...")
    
    try:
        from ai_services.gemini_service import GeminiService
        
        service = GeminiService()
        print("✅ Gemini service initialized successfully")
        print(f"   API Key: {service.api_key[:10] if service.api_key else 'None'}...")
        print(f"   Model: {service.model_name}")
        return True
    except Exception as e:
        print(f"❌ Initialization failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_image_generation():
    """Test image generation"""
    print("\n🎨 Testing Image Generation...")
    
    try:
        from ai_services.gemini_service import GeminiService
        
        service = GeminiService()
        
        # Test simple image generation
        result = service.generate_image_from_prompt(
            prompt="elegant silk saree",
            style="textile"
        )
        
        print(f"   Success: {result.get('success')}")
        if result.get('success'):
            print(f"   Image URL: {result.get('image_url')}")
            print(f"   Service: {result.get('service')}")
        else:
            print(f"   Error: {result.get('error')}")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ Image generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Gemini Fix Test")
    print("=" * 30)
    
    if test_gemini_import():
        if test_gemini_initialization():
            if test_image_generation():
                print("\n✅ All tests passed! Gemini AI is working.")
            else:
                print("\n❌ Image generation failed")
        else:
            print("\n❌ Service initialization failed")
    else:
        print("\n❌ Import failed")
    
    print("\n" + "=" * 30)
