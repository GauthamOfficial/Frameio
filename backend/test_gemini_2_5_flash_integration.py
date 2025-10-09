#!/usr/bin/env python3
"""
Test script for Gemini 2.5 Flash Image Generation Integration
Tests the new Gemini 2.5 Flash service with the provided API key
"""
import os
import sys
import django
import time

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from ai_services.gemini_2_5_flash_image_service import gemini_2_5_flash_image_service
from ai_services.prompt_based_image_service import PromptBasedImageService
from ai_services.nanobanana_service import NanoBananaAIService


def test_gemini_service_initialization():
    """Test Gemini 2.5 Flash service initialization"""
    print("🧪 Testing Gemini 2.5 Flash Service Initialization...")
    
    try:
        service_info = gemini_2_5_flash_image_service.get_service_info()
        print(f"✅ Service Name: {service_info['service_name']}")
        print(f"✅ Model: {service_info['model']}")
        print(f"✅ API Key Configured: {service_info['api_key_configured']}")
        print(f"✅ Base URL: {service_info['base_url']}")
        print(f"✅ Features: {', '.join(service_info['features'])}")
        
        if service_info['api_key_configured']:
            print("✅ Gemini 2.5 Flash service is properly configured")
            return True
        else:
            print("❌ Gemini 2.5 Flash service is not properly configured")
            return False
            
    except Exception as e:
        print(f"❌ Error testing service initialization: {str(e)}")
        return False


def test_gemini_image_generation():
    """Test Gemini 2.5 Flash image generation"""
    print("\n🧪 Testing Gemini 2.5 Flash Image Generation...")
    
    try:
        # Test basic image generation
        prompt = "Beautiful silk saree with golden border, elegant design, professional photography"
        style = "photorealistic"
        
        print(f"📝 Prompt: {prompt}")
        print(f"🎨 Style: {style}")
        
        result = gemini_2_5_flash_image_service.generate_image_from_prompt(
            prompt=prompt,
            style=style,
            width=1024,
            height=1024
        )
        
        if result.get('success'):
            print("✅ Image generation successful!")
            print(f"🖼️  Image URL: {result.get('image_url', 'N/A')}")
            print(f"📊 Service: {result.get('service', 'N/A')}")
            print(f"⏱️  Processing Time: {result.get('processing_time', 'N/A')}s")
            print(f"🆔 Unique ID: {result.get('unique_id', 'N/A')}")
            
            # Check metadata
            metadata = result.get('metadata', {})
            if metadata:
                print(f"🎨 Colors Detected: {metadata.get('colors_detected', [])}")
                print(f"🧵 Fabrics Detected: {metadata.get('fabrics_detected', [])}")
                print(f"🎯 Design Elements: {metadata.get('design_elements', [])}")
            
            return True
        else:
            print(f"❌ Image generation failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing image generation: {str(e)}")
        return False


def test_gemini_poster_generation():
    """Test Gemini 2.5 Flash poster generation"""
    print("\n🧪 Testing Gemini 2.5 Flash Poster Generation...")
    
    try:
        # Test poster generation
        fabric_type = "silk saree"
        offer_text = "Special Diwali Collection - 30% Off"
        theme = "festive"
        
        print(f"👗 Fabric Type: {fabric_type}")
        print(f"📢 Offer Text: {offer_text}")
        print(f"🎨 Theme: {theme}")
        
        result = gemini_2_5_flash_image_service.generate_poster(
            fabric_type=fabric_type,
            offer_text=offer_text,
            theme=theme,
            style="photorealistic"
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
        print(f"❌ Error testing poster generation: {str(e)}")
        return False


def test_multiple_image_generation():
    """Test multiple image generation"""
    print("\n🧪 Testing Multiple Image Generation...")
    
    try:
        prompt = "Elegant cotton kurta with traditional embroidery"
        num_images = 3
        
        print(f"📝 Prompt: {prompt}")
        print(f"🔢 Number of Images: {num_images}")
        
        result = gemini_2_5_flash_image_service.generate_multiple_images(
            prompt=prompt,
            num_images=num_images,
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
        print(f"❌ Error testing multiple image generation: {str(e)}")
        return False


def test_prompt_based_service_integration():
    """Test integration with prompt-based image service"""
    print("\n🧪 Testing Prompt-Based Service Integration...")
    
    try:
        service = PromptBasedImageService()
        
        prompt = "Beautiful handwoven textile with intricate patterns"
        style = "artistic"
        
        print(f"📝 Prompt: {prompt}")
        print(f"🎨 Style: {style}")
        
        result = service.generate_image_from_prompt(prompt, style)
        
        if result.get('success'):
            print("✅ Prompt-based service integration successful!")
            print(f"🖼️  Image URL: {result.get('image_url', 'N/A')}")
            print(f"📊 Service: {result.get('service', 'N/A')}")
            return True
        else:
            print(f"❌ Prompt-based service failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing prompt-based service: {str(e)}")
        return False


def test_nanobanana_service_integration():
    """Test integration with NanoBanana service (now using Gemini)"""
    print("\n🧪 Testing NanoBanana Service Integration (with Gemini)...")
    
    try:
        service = NanoBananaAIService()
        
        image_url = "https://example.com/fabric.jpg"
        offer_text = "Summer Collection - 50% Off"
        theme = "modern"
        
        print(f"🖼️  Image URL: {image_url}")
        print(f"📢 Offer Text: {offer_text}")
        print(f"🎨 Theme: {theme}")
        
        result = service.generate_poster(image_url, offer_text, theme)
        
        if result.get('success'):
            print("✅ NanoBanana service integration successful!")
            print(f"🖼️  Image URLs: {result.get('image_urls', [])}")
            print(f"📊 Service: {result.get('service', 'N/A')}")
            print(f"🆔 Generation ID: {result.get('generation_id', 'N/A')}")
            return True
        else:
            print(f"❌ NanoBanana service failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing NanoBanana service: {str(e)}")
        return False


def test_api_key_validation():
    """Test API key validation"""
    print("\n🧪 Testing API Key Validation...")
    
    try:
        from django.conf import settings
        
        gemini_key = getattr(settings, 'GEMINI_API_KEY', None)
        google_key = getattr(settings, 'GOOGLE_API_KEY', None)
        
        print(f"🔑 GEMINI_API_KEY: {'✅ Set' if gemini_key else '❌ Not set'}")
        print(f"🔑 GOOGLE_API_KEY: {'✅ Set' if google_key else '❌ Not set'}")
        
        if gemini_key:
            print(f"🔑 GEMINI_API_KEY value: {gemini_key[:10]}...")
        if google_key:
            print(f"🔑 GOOGLE_API_KEY value: {google_key[:10]}...")
        
        # Check if the expected API key is set
        expected_key = "AIzaSyDtjWMwLhP4nZIv5LeShDX_cqIQ9y2Rhuc"
        if gemini_key == expected_key or google_key == expected_key:
            print("✅ Expected API key is configured correctly")
            return True
        else:
            print("❌ Expected API key is not configured")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API key validation: {str(e)}")
        return False


def run_comprehensive_test():
    """Run comprehensive test suite"""
    print("🚀 Starting Gemini 2.5 Flash Integration Test Suite")
    print("=" * 60)
    
    tests = [
        ("API Key Validation", test_api_key_validation),
        ("Service Initialization", test_gemini_service_initialization),
        ("Image Generation", test_gemini_image_generation),
        ("Poster Generation", test_gemini_poster_generation),
        ("Multiple Image Generation", test_multiple_image_generation),
        ("Prompt-Based Service Integration", test_prompt_based_service_integration),
        ("NanoBanana Service Integration", test_nanobanana_service_integration),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
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
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\n📈 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Gemini 2.5 Flash integration is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total


if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
