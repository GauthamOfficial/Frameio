#!/usr/bin/env python
"""
Test Caption Generation Fix
Test the fixed caption generation with proper error handling
"""
import os
import sys
import django
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Set the API key before Django setup
os.environ['GEMINI_API_KEY'] = 'AIzaSyCZiGdU4pk_-uVNWCquY5C15vaxnPszA-s'

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

def test_caption_generation():
    """Test caption generation with proper error handling"""
    print("🧪 Testing Caption Generation Fix...")
    
    try:
        from ai_services.ai_caption_service import AICaptionService
        
        service = AICaptionService()
        
        if not service.is_available():
            print("   ❌ AI Caption Service not available")
            return False
        
        print("   ✅ AI Caption Service initialized successfully")
        
        # Test product caption generation with proper error handling
        print("   📝 Testing product caption generation...")
        result = service.generate_product_caption(
            product_name="Silk Saree Collection",
            product_type="saree",
            style="modern",
            tone="professional",
            include_hashtags=True,
            include_emoji=True,
            max_length=200
        )
        
        if result.get('status') == 'success':
            print("   ✅ Product caption generation successful!")
            caption = result.get('caption', {})
            print(f"   📝 Caption: {caption.get('main_content', '')[:100]}...")
            print(f"   #️⃣ Hashtags: {caption.get('hashtags', [])}")
            print(f"   📊 Word count: {caption.get('word_count', 0)}")
            return True
        else:
            print(f"   ❌ Product caption generation failed: {result.get('message')}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing caption generation: {str(e)}")
        return False

def test_direct_gemini_call():
    """Test direct Gemini API call to verify the response structure"""
    print("\n🔍 Testing Direct Gemini API Call...")
    
    try:
        from google import genai
        from google.genai import types
        
        client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
        
        # Test simple text generation
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=["Write a short product description for a silk saree."],
        )
        
        print(f"   📊 Response type: {type(response)}")
        print(f"   📊 Has candidates: {hasattr(response, 'candidates')}")
        
        if response and response.candidates:
            print(f"   📊 Candidates length: {len(response.candidates)}")
            candidate = response.candidates[0]
            print(f"   📊 Has content: {hasattr(candidate, 'content')}")
            
            if candidate.content:
                print(f"   📊 Has parts: {hasattr(candidate.content, 'parts')}")
                if candidate.content.parts:
                    print(f"   📊 Parts length: {len(candidate.content.parts)}")
                    part = candidate.content.parts[0]
                    print(f"   📊 Has text: {hasattr(part, 'text')}")
                    if hasattr(part, 'text'):
                        print(f"   📝 Generated text: {part.text[:100]}...")
                        return True
        
        print("   ❌ No valid response structure found")
        return False
        
    except Exception as e:
        print(f"   ❌ Error in direct Gemini call: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 Caption Generation Fix Test")
    print("=" * 50)
    
    # Test direct API call first
    direct_success = test_direct_gemini_call()
    
    if direct_success:
        print("\n✅ Direct Gemini API call successful!")
        
        # Test caption service
        caption_success = test_caption_generation()
        
        if caption_success:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ Caption generation is working correctly!")
            return True
        else:
            print("\n❌ Caption service test failed!")
            return False
    else:
        print("\n❌ Direct Gemini API call failed!")
        print("🔧 Check your API key and network connection")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

