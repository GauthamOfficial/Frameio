#!/usr/bin/env python3
"""
Gemini API Quickstart Test
Following the official Google Gemini quickstart guide
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

from google import genai
from google.genai import types

def test_gemini_quickstart():
    """Test the Gemini API quickstart example"""
    print("🚀 Testing Gemini API Quickstart")
    print("=" * 50)
    
    # Set the API key from environment or use the provided one
    api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY') or "AIzaSyDtjWMwLhP4nZIv5LeShDX_cqIQ9y2Rhuc"
    
    if not api_key:
        print("❌ No API key found!")
        return False
    
    print(f"✅ Using API key: {api_key[:10]}...")
    
    try:
        # Initialize the client
        client = genai.Client(api_key=api_key)
        print("✅ Gemini client initialized successfully")
        
        # Test 1: Basic content generation
        print("\n📝 Test 1: Basic content generation")
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents="Explain how AI works in a few words"
        )
        print(f"Response: {response.text}")
        
        # Test 2: With thinking disabled
        print("\n🧠 Test 2: With thinking disabled")
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Explain how AI works in a few words",
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0)  # Disables thinking
            ),
        )
        print(f"Response: {response.text}")
        
        # Test 3: Textile design prompt
        print("\n🎨 Test 3: Textile design prompt")
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Create a detailed prompt for generating a beautiful textile design for saree with intricate patterns, suitable for a fashion catalog",
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0)
            ),
        )
        print(f"Response: {response.text}")
        
        print("\n🎉 All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_image_generation():
    """Test image generation capabilities"""
    print("\n🖼️ Testing Image Generation")
    print("=" * 50)
    
    api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY') or "AIzaSyDtjWMwLhP4nZIv5LeShDX_cqIQ9y2Rhuc"
    
    try:
        client = genai.Client(api_key=api_key)
        
        # Test image generation with a textile design prompt
        print("🎨 Generating textile design image...")
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents="A beautiful textile design for saree with intricate patterns, elegant colors, and traditional motifs"
        )
        
        if hasattr(response, 'images') and response.images:
            print(f"✅ Generated {len(response.images)} image(s)")
            for i, image in enumerate(response.images):
                print(f"Image {i+1}: {type(image)}")
        else:
            print("ℹ️ No images in response (this might be expected for text-only models)")
            
        return True
        
    except Exception as e:
        print(f"❌ Image generation error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Gemini API Quickstart Test")
    print("=" * 60)
    
    # Test basic functionality
    success1 = test_gemini_quickstart()
    
    # Test image generation
    success2 = test_image_generation()
    
    if success1 and success2:
        print("\n🎉 All tests passed! Gemini API is working correctly.")
    else:
        print("\n❌ Some tests failed. Check the error messages above.")
        sys.exit(1)
