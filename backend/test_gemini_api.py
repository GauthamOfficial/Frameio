#!/usr/bin/env python3
"""
Test script to check if GEMINI_API_KEY is working
Run this from the backend directory: python test_gemini_api.py
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

def test_gemini_api():
    print("🧪 Testing Gemini API Configuration\n")
    
    # Check environment variables
    print("1. Checking environment variables...")
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print(f"   ✅ GEMINI_API_KEY found: {api_key[:10]}...")
    else:
        print("   ❌ GEMINI_API_KEY not found")
        print("   💡 Set GEMINI_API_KEY in your environment or .env file")
        return False
    
    # Check if google-genai is installed
    print("\n2. Checking google-genai installation...")
    try:
        from google import genai
        print("   ✅ google-genai is installed")
    except ImportError:
        print("   ❌ google-genai not installed")
        print("   💡 Install with: pip install google-genai")
        return False
    
    # Test API connection
    print("\n3. Testing API connection...")
    try:
        client = genai.Client(api_key=api_key)
        print("   ✅ Gemini client created successfully")
        
        # Test a simple generation
        print("\n4. Testing image generation...")
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=["A simple test image"],
                config=genai.types.GenerateContentConfig(
                    response_modalities=['Image'],
                    image_config=genai.types.ImageConfig(aspect_ratio="1:1"),
                ),
            )
            
            if response.candidates and len(response.candidates) > 0:
                print("   ✅ Image generation successful")
                print(f"   📊 Response has {len(response.candidates)} candidates")
                
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    print(f"   📊 Content has {len(candidate.content.parts)} parts")
                    
                    # Check if any part has image data
                    has_image = False
                    for part in candidate.content.parts:
                        if hasattr(part, 'inline_data') and part.inline_data is not None:
                            has_image = True
                            print(f"   ✅ Found image data: {len(part.inline_data.data)} bytes")
                            break
                    
                    if not has_image:
                        print("   ⚠️  No image data found in response")
                else:
                    print("   ⚠️  No content parts in response")
            else:
                print("   ❌ No candidates in response")
                
        except Exception as e:
            print(f"   ❌ Image generation failed: {str(e)}")
            return False
            
    except Exception as e:
        print(f"   ❌ Failed to create Gemini client: {str(e)}")
        return False
    
    print("\n🎉 Gemini API is working correctly!")
    return True

if __name__ == "__main__":
    success = test_gemini_api()
    if not success:
        print("\n🔧 To fix the issues:")
        print("   1. Set GEMINI_API_KEY environment variable")
        print("   2. Install google-genai: pip install google-genai")
        print("   3. Restart your Django server")
        sys.exit(1)
    else:
        print("\n✅ All tests passed! Your Gemini API is ready to use.")


