#!/usr/bin/env python3
"""
Simple Gemini API Test
Run this from the backend directory: python test_gemini_simple.py
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

def test_gemini_simple():
    print("🧪 Simple Gemini API Test\n")
    
    # Check API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    # Test import
    try:
        from google import genai
        from google.genai import types
        print("✅ google-genai imported successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Test client creation
    try:
        client = genai.Client(api_key=api_key)
        print("✅ Gemini client created")
    except Exception as e:
        print(f"❌ Client creation failed: {e}")
        return False
    
    # Test simple generation
    try:
        print("\n🔄 Testing simple image generation...")
        
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=["A simple red circle on white background"],
            config=types.GenerateContentConfig(
                response_modalities=['Image'],
                image_config=types.ImageConfig(aspect_ratio="1:1"),
            ),
        )
        
        print(f"✅ Generation call successful")
        print(f"📊 Response type: {type(response)}")
        print(f"📊 Has candidates: {hasattr(response, 'candidates')}")
        
        if hasattr(response, 'candidates'):
            print(f"📊 Candidates count: {len(response.candidates) if response.candidates else 0}")
            
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                print(f"📊 Candidate type: {type(candidate)}")
                print(f"📊 Has content: {hasattr(candidate, 'content')}")
                
                if hasattr(candidate, 'content') and candidate.content:
                    print(f"📊 Has parts: {hasattr(candidate.content, 'parts')}")
                    print(f"📊 Parts count: {len(candidate.content.parts) if candidate.content.parts else 0}")
                    
                    if candidate.content.parts:
                        for i, part in enumerate(candidate.content.parts):
                            print(f"📊 Part {i}: {type(part)}")
                            print(f"📊 Has inline_data: {hasattr(part, 'inline_data')}")
                            if hasattr(part, 'inline_data'):
                                print(f"📊 Inline data: {part.inline_data is not None}")
                                if part.inline_data:
                                    print(f"📊 Data size: {len(part.inline_data.data) if hasattr(part.inline_data, 'data') else 'No data'}")
                else:
                    print("❌ No content in candidate")
            else:
                print("❌ No candidates in response")
        else:
            print("❌ No candidates attribute in response")
            
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        return False
    
    print("\n🎉 Gemini API test completed!")
    return True

if __name__ == "__main__":
    success = test_gemini_simple()
    if not success:
        print("\n❌ Test failed - check your API key and configuration")
        sys.exit(1)
    else:
        print("✅ Test passed!")










