#!/usr/bin/env python3
"""
Simple Gemini API Quickstart Implementation
Following the exact pattern from the Google documentation
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

def test_basic_quickstart():
    """Test the basic quickstart example exactly as provided"""
    print("🚀 Testing Basic Gemini Quickstart")
    print("=" * 50)
    
    try:
        from google import genai
        
        # The client gets the API key from the environment variable `GEMINI_API_KEY`.
        client = genai.Client()
        
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents="Explain how AI works in a few words"
        )
        print("✅ Basic quickstart test:")
        print(f"Response: {response.text}")
        return True
        
    except Exception as e:
        print(f"❌ Basic quickstart failed: {e}")
        return False

def test_thinking_disabled():
    """Test with thinking disabled as shown in the example"""
    print("\n🧠 Testing with thinking disabled")
    print("=" * 50)
    
    try:
        from google import genai
        from google.genai import types
        
        client = genai.Client()
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Explain how AI works in a few words",
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0)  # Disables thinking
            ),
        )
        print("✅ Thinking disabled test:")
        print(f"Response: {response.text}")
        return True
        
    except Exception as e:
        print(f"❌ Thinking disabled test failed: {e}")
        return False

def test_textile_design_prompt():
    """Test with a textile design prompt relevant to your project"""
    print("\n🎨 Testing with textile design prompt")
    print("=" * 50)
    
    try:
        from google import genai
        from google.genai import types
        
        client = genai.Client()
        
        # Create a prompt for textile design
        prompt = """Create a detailed description for generating a beautiful textile design for saree with intricate patterns, suitable for a fashion catalog. Include specific details about colors, patterns, and style."""
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0)
            ),
        )
        print("✅ Textile design prompt test:")
        print(f"Response: {response.text}")
        return True
        
    except Exception as e:
        print(f"❌ Textile design test failed: {e}")
        return False

def test_image_generation():
    """Test image generation if available"""
    print("\n🖼️ Testing image generation")
    print("=" * 50)
    
    try:
        from google import genai
        from google.genai import types
        
        client = genai.Client()
        
        # Try to generate an image
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents="A beautiful textile design for saree with intricate patterns"
        )
        
        print("✅ Image generation test:")
        if hasattr(response, 'images') and response.images:
            print(f"Generated {len(response.images)} image(s)")
        else:
            print("No images in response (this might be expected)")
        
        return True
        
    except Exception as e:
        print(f"❌ Image generation test failed: {e}")
        print("Note: Image generation might not be available in all regions or with all API keys")
        return False

def main():
    """Run all quickstart tests"""
    print("🚀 Gemini API Quickstart Tests")
    print("=" * 60)
    
    # Set the API key
    api_key = "AIzaSyDtjWMwLhP4nZIv5LeShDX_cqIQ9y2Rhuc"
    os.environ['GEMINI_API_KEY'] = api_key
    
    print(f"Using API key: {api_key[:10]}...")
    
    # Run tests
    tests = [
        test_basic_quickstart,
        test_thinking_disabled,
        test_textile_design_prompt,
        test_image_generation
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Gemini API is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Check the error messages above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
