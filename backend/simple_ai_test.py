#!/usr/bin/env python
"""
Simple AI Services Test - No Django Setup Required
Test AI poster and caption generation with direct API calls
"""
import os
import sys

# Set the API key from environment or use placeholder
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("WARNING: GEMINI_API_KEY not set. Using placeholder for testing.")
    api_key = 'your_gemini_api_key_here'
os.environ['GEMINI_API_KEY'] = api_key

def test_gemini_import():
    """Test if Google GenAI can be imported"""
    print("🔍 Testing Google GenAI Import...")
    
    try:
        from google import genai
        from google.genai import types
        print("   ✅ Google GenAI imported successfully")
        return True
    except ImportError as e:
        print(f"   ❌ Failed to import Google GenAI: {str(e)}")
        print("   💡 Run: pip install google-genai")
        return False

def test_gemini_client():
    """Test Gemini client initialization"""
    print("\n🤖 Testing Gemini Client...")
    
    try:
        from google import genai
        
        # Initialize client
        client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
        print("   ✅ Gemini client initialized successfully")
        
        # Test a simple text generation
        print("   🧪 Testing text generation...")
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=["Write a short product description for a silk saree."],
        )
        
        if response and response.candidates:
            print("   ✅ Text generation successful!")
            print(f"   📝 Generated: {response.candidates[0].content.parts[0].text[:100]}...")
            return True
        else:
            print("   ❌ No response from Gemini")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing Gemini client: {str(e)}")
        return False

def test_image_generation():
    """Test image generation capability"""
    print("\n🎨 Testing Image Generation...")
    
    try:
        from google import genai
        from google.genai import types
        
        client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
        
        # Test image generation
        print("   🖼️ Testing image generation...")
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=["Create a simple textile pattern"],
            config=types.GenerateContentConfig(
                response_modalities=['Image'],
                image_config=types.ImageConfig(aspect_ratio="1:1"),
            ),
        )
        
        if response and response.candidates and response.candidates[0].content.parts:
            print("   ✅ Image generation successful!")
            print("   🎨 Generated image with Gemini 2.5 Flash")
            return True
        else:
            print("   ❌ No image generated")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing image generation: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 Simple AI Services Test")
    print("=" * 50)
    print("🔑 Using API key from environment variables")
    print("=" * 50)
    
    tests = [
        ("Google GenAI Import", test_gemini_import),
        ("Gemini Client", test_gemini_client),
        ("Image Generation", test_image_generation)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed_tests += 1
                print(f"✅ {test_name} - PASSED")
            else:
                print(f"❌ {test_name} - FAILED")
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {str(e)}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED!")
        print("\n✅ AI Services are working correctly!")
        print("📋 Next steps:")
        print("   1. Run: python test_ai_poster.py")
        print("   2. Run: python test_ai_caption.py")
        print("   3. Start Django server: python manage.py runserver")
        return True
    else:
        print("❌ SOME TESTS FAILED!")
        print("🔧 Check the error messages above and fix any issues.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

