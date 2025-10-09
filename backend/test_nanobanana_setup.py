#!/usr/bin/env python3
"""
Test NanoBanana AI setup and configuration
"""
import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

def test_environment_variables():
    """Test if environment variables are set correctly"""
    print("🔧 Testing Environment Variables...")
    
    # Check Django settings
    nanobanana_key = getattr(settings, 'NANOBANANA_API_KEY', None)
    if nanobanana_key:
        print(f"✅ NANOBANANA_API_KEY is set: {nanobanana_key[:10]}...")
    else:
        print("❌ NANOBANANA_API_KEY is not set")
        print("   Add NANOBANANA_API_KEY=your_api_key_here to your .env file")
    
    # Check environment variables
    env_key = os.getenv('NANOBANANA_API_KEY')
    if env_key:
        print(f"✅ Environment NANOBANANA_API_KEY is set: {env_key[:10]}...")
    else:
        print("❌ Environment NANOBANANA_API_KEY is not set")
        print("   Add NANOBANANA_API_KEY=your_api_key_here to your .env file")

def test_nanobanana_service():
    """Test NanoBanana service initialization"""
    print("\n🤖 Testing NanoBanana Service...")
    
    try:
        from ai_services.nanobanana_service import NanoBananaAIService
        
        service = NanoBananaAIService()
        
        if service.is_available():
            print("✅ NanoBanana service is available")
            print(f"   API Key: {service.api_key[:10]}...")
            print(f"   Base URL: {service.base_url}")
            print(f"   Use Fallback: {service.use_fallback}")
        else:
            print("❌ NanoBanana service is not available")
            print("   Check your API key configuration")
            print(f"   API Key: {service.api_key}")
            print(f"   Use Fallback: {service.use_fallback}")
            
    except Exception as e:
        print(f"❌ Failed to initialize NanoBanana service: {str(e)}")
        import traceback
        traceback.print_exc()

def test_api_connection():
    """Test API connection"""
    print("\n🌐 Testing API Connection...")
    
    try:
        import requests
        
        api_key = getattr(settings, 'NANOBANANA_API_KEY', None)
        if not api_key:
            print("❌ No API key found, skipping API test")
            return
        
        # Test API connection
        response = requests.get(
            "https://api.nanobanana.ai/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API connection successful")
            data = response.json()
            print(f"   Available models: {data.get('models', [])}")
        elif response.status_code == 401:
            print("❌ API key is invalid or expired")
            print("   Check your API key at https://app.banana.dev/")
        elif response.status_code == 403:
            print("❌ API key doesn't have required permissions")
            print("   Check your API key permissions at https://app.banana.dev/")
        else:
            print(f"❌ API connection failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            
    except requests.exceptions.ConnectionError:
        print("❌ Network connection failed")
        print("   Check your internet connection")
    except Exception as e:
        print(f"❌ API test failed: {str(e)}")

def test_image_generation():
    """Test image generation"""
    print("\n🎨 Testing Image Generation...")
    
    try:
        from ai_services.nanobanana_service import NanoBananaAIService
        
        service = NanoBananaAIService()
        
        if not service.is_available():
            print("❌ NanoBanana service is not available, skipping generation test")
            return
        
        # Test image generation
        result = service.generate_poster(
            image_url="https://example.com/fabric.jpg",
            offer_text="Special Deepavali Collection",
            theme="festive"
        )
        
        if result.get('success'):
            print("✅ Image generation successful")
            print(f"   Generated {len(result.get('image_urls', []))} images")
            print(f"   Generation ID: {result.get('generation_id')}")
            print(f"   Cost: ${result.get('cost', 0)}")
            print(f"   Fallback: {result.get('fallback', False)}")
        else:
            print(f"❌ Image generation failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Image generation test failed: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """Run all tests"""
    print("🚀 NanoBanana AI Setup Test")
    print("=" * 50)
    
    test_environment_variables()
    test_nanobanana_service()
    test_api_connection()
    test_image_generation()
    
    print("\n" + "=" * 50)
    print("✅ Tests completed!")
    print("\n📋 Next Steps:")
    print("1. If API key is missing, get one from https://app.banana.dev/")
    print("2. Add NANOBANANA_API_KEY=your_api_key_here to your .env file")
    print("3. Restart your Django server")
    print("4. Test the frontend integration")

if __name__ == "__main__":
    main()
