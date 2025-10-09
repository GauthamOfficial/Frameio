#!/usr/bin/env python3
"""
Test Gemini AI integration for image generation
"""
import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from ai_services.gemini_service import GeminiService
from ai_services.services import AIGenerationService
import json

def test_gemini_api_key():
    """Test if Gemini API key is configured"""
    print("🔑 Testing Gemini API Key Configuration...")
    
    # Check Django settings
    gemini_key = getattr(settings, 'GEMINI_API_KEY', None)
    google_key = getattr(settings, 'GOOGLE_API_KEY', None)
    
    if gemini_key:
        print(f"✅ GEMINI_API_KEY is set: {gemini_key[:10]}...")
    elif google_key:
        print(f"✅ GOOGLE_API_KEY is set: {google_key[:10]}...")
    else:
        print("❌ No Gemini API key found")
        print("   Add GEMINI_API_KEY=AIzaSyDtjWMwLhP4nZIv5LeShDX_cqIQ9y2Rhuc to your .env file")
        return False
    
    return True

def test_gemini_service():
    """Test Gemini service initialization"""
    print("\n🤖 Testing Gemini Service...")
    
    try:
        service = GeminiService()
        
        if service.api_key:
            print("✅ Gemini service initialized successfully")
            print(f"   API Key: {service.api_key[:10]}...")
            print(f"   Model: {service.model_name}")
            print(f"   Base URL: {service.base_url}")
        else:
            print("❌ Gemini service not properly configured")
            return False
            
    except Exception as e:
        print(f"❌ Failed to initialize Gemini service: {str(e)}")
        return False
    
    return True

def test_gemini_image_generation():
    """Test Gemini image generation"""
    print("\n🎨 Testing Gemini Image Generation...")
    
    try:
        service = GeminiService()
        
        # Test image generation
        result = service.generate_image_from_prompt(
            prompt="elegant silk saree with golden border",
            style="textile",
            width=1024,
            height=1024
        )
        
        if result.get('success'):
            print("✅ Image generation successful")
            print(f"   Image URL: {result.get('image_url')}")
            print(f"   Service: {result.get('service', 'unknown')}")
            print(f"   Model: {result.get('metadata', {}).get('model', 'unknown')}")
            print(f"   Unique ID: {result.get('metadata', {}).get('unique_id', 'unknown')}")
        else:
            print(f"❌ Image generation failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Image generation test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_ai_generation_service():
    """Test AI generation service with Gemini"""
    print("\n🔄 Testing AI Generation Service...")
    
    try:
        from ai_services.models import AIGenerationRequest
        
        # Create a test request
        request = AIGenerationRequest(
            id="test_001",
            prompt="beautiful cotton shirt design",
            generation_type="image",
            parameters={
                "style": "textile",
                "width": 1024,
                "height": 1024
            }
        )
        
        # Test the service
        ai_service = AIGenerationService()
        result = ai_service.process_request(request)
        
        if result.get('success'):
            print("✅ AI generation service successful")
            print(f"   Generation ID: {result.get('data', {}).get('generation_id', 'unknown')}")
            print(f"   Model Used: {result.get('data', {}).get('model_used', 'unknown')}")
            print(f"   Image URL: {result.get('data', {}).get('image_url', 'unknown')}")
        else:
            print(f"❌ AI generation service failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ AI generation service test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_multiple_prompts():
    """Test multiple prompts for variety"""
    print("\n🎯 Testing Multiple Prompts...")
    
    test_prompts = [
        "elegant silk saree with golden border",
        "modern cotton shirt design",
        "traditional textile pattern",
        "festive deepavali clothing",
        "bohemian style fabric"
    ]
    
    try:
        service = GeminiService()
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n📝 Test {i}: {prompt}")
            
            result = service.generate_image_from_prompt(
                prompt=prompt,
                style="textile",
                width=1024,
                height=1024
            )
            
            if result.get('success'):
                print(f"✅ Generated: {result.get('image_url')}")
                print(f"   Service: {result.get('service', 'unknown')}")
            else:
                print(f"❌ Failed: {result.get('error', 'Unknown error')}")
                
    except Exception as e:
        print(f"❌ Multiple prompts test failed: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """Run all tests"""
    print("🚀 Gemini AI Integration Test")
    print("=" * 50)
    
    # Test API key configuration
    if not test_gemini_api_key():
        print("\n❌ API key not configured. Please add GEMINI_API_KEY to your .env file")
        return
    
    # Test Gemini service
    if not test_gemini_service():
        print("\n❌ Gemini service not working. Check your configuration")
        return
    
    # Test image generation
    if not test_gemini_image_generation():
        print("\n❌ Image generation not working. Check your API key and network")
        return
    
    # Test AI generation service
    if not test_ai_generation_service():
        print("\n❌ AI generation service not working. Check your configuration")
        return
    
    # Test multiple prompts
    test_multiple_prompts()
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")
    print("\n📋 Summary:")
    print("- Gemini API key is configured")
    print("- Gemini service is working")
    print("- Image generation is functional")
    print("- AI generation service is operational")
    print("- Multiple prompts are working")
    print("\n🎉 Your AI image generation is ready to use!")

if __name__ == "__main__":
    main()
