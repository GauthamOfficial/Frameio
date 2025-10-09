#!/usr/bin/env python3
"""
Simple test for Gemini AI integration
"""
import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

def test_gemini_config():
    """Test Gemini configuration"""
    print("🔑 Testing Gemini Configuration...")
    
    # Check API key
    gemini_key = getattr(settings, 'GEMINI_API_KEY', None)
    if gemini_key:
        print(f"✅ GEMINI_API_KEY is set: {gemini_key[:10]}...")
    else:
        print("❌ GEMINI_API_KEY not found")
        return False
    
    # Check Google API key
    google_key = getattr(settings, 'GOOGLE_API_KEY', None)
    if google_key:
        print(f"✅ GOOGLE_API_KEY is set: {google_key[:10]}...")
    else:
        print("❌ GOOGLE_API_KEY not found")
    
    return True

def test_gemini_service():
    """Test Gemini service"""
    print("\n🤖 Testing Gemini Service...")
    
    try:
        from ai_services.gemini_service import GeminiService
        
        service = GeminiService()
        print(f"✅ Gemini service initialized")
        print(f"   API Key: {service.api_key[:10] if service.api_key else 'None'}...")
        print(f"   Model: {service.model_name}")
        print(f"   Base URL: {service.base_url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Gemini service failed: {str(e)}")
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
        
        if result.get('success'):
            print("✅ Image generation successful")
            print(f"   Image URL: {result.get('image_url')}")
            print(f"   Service: {result.get('service')}")
        else:
            print(f"❌ Image generation failed: {result.get('error')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Image generation test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Gemini AI Simple Test")
    print("=" * 40)
    
    if test_gemini_config():
        if test_gemini_service():
            if test_image_generation():
                print("\n✅ All tests passed! Gemini AI is working.")
            else:
                print("\n❌ Image generation failed")
        else:
            print("\n❌ Gemini service failed")
    else:
        print("\n❌ Configuration failed")
    
    print("\n" + "=" * 40)
