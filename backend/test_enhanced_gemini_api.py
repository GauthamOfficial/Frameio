#!/usr/bin/env python3
"""
Enhanced Gemini API Test Suite
Tests the new implementation following official Gemini API structure
"""
import os
import sys
import django
import base64
from io import BytesIO
from PIL import Image

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from ai_services.gemini_service import GeminiService


def test_basic_content_generation():
    """Test basic content generation following official API structure"""
    print("🧪 Testing Basic Content Generation...")
    
    service = GeminiService()
    
    # Test simple text generation
    result = service.generate_content("Explain how AI works in a few words")
    
    if result['success']:
        print("✅ Basic content generation: PASSED")
        print(f"Response: {result['data']['text'][:100]}...")
        return True
    else:
        print(f"❌ Basic content generation: FAILED - {result['error']}")
        return False


def test_multimodal_content():
    """Test multimodal content generation with image"""
    print("\n🧪 Testing Multimodal Content Generation...")
    
    service = GeminiService()
    
    # Create a simple test image
    img = Image.new('RGB', (100, 100), color='red')
    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    img_data = base64.b64encode(buffer.getvalue()).decode()
    
    result = service.generate_multimodal_content(
        text_prompt="What color is this image?",
        image_data=img_data,
        mime_type="image/jpeg"
    )
    
    if result['success']:
        print("✅ Multimodal content generation: PASSED")
        print(f"Response: {result['data']['text'][:100]}...")
        return True
    else:
        print(f"❌ Multimodal content generation: FAILED - {result['error']}")
        return False


def test_chat_conversation():
    """Test multi-turn conversation"""
    print("\n🧪 Testing Chat Conversation...")
    
    service = GeminiService()
    
    messages = [
        {"role": "user", "content": "Hello."},
        {"role": "model", "content": "Hello! How can I help you today?"},
        {"role": "user", "content": "Please write a four-line poem about the ocean."}
    ]
    
    result = service.create_chat_conversation(messages)
    
    if result['success']:
        print("✅ Chat conversation: PASSED")
        print(f"Response: {result['data']['text'][:100]}...")
        return True
    else:
        print(f"❌ Chat conversation: FAILED - {result['error']}")
        return False


def test_textile_poster_generation():
    """Test textile poster generation"""
    print("\n🧪 Testing Textile Poster Generation...")
    
    service = GeminiService()
    
    result = service.generate_textile_poster(
        fabric_type="saree",
        offer_text="Special Diwali Collection - 30% Off",
        festival="Diwali",
        price_range="₹2000-₹5000",
        style="traditional"
    )
    
    if result['success']:
        print("✅ Textile poster generation: PASSED")
        print(f"Response: {result['data']['text'][:200]}...")
        return True
    else:
        print(f"❌ Textile poster generation: FAILED - {result['error']}")
        return False


def test_caption_generation():
    """Test marketing caption generation"""
    print("\n🧪 Testing Caption Generation...")
    
    service = GeminiService()
    
    result = service.generate_captions(
        fabric_type="kurta",
        festival="Eid",
        price_range="₹1500-₹3000",
        num_captions=3
    )
    
    if result['success']:
        print("✅ Caption generation: PASSED")
        print(f"Response: {result['data']['text'][:200]}...")
        return True
    else:
        print(f"❌ Caption generation: FAILED - {result['error']}")
        return False


def test_streaming_content():
    """Test streaming content generation"""
    print("\n🧪 Testing Streaming Content Generation...")
    
    service = GeminiService()
    
    result = service.stream_generate_content("Write a short story about a robot")
    
    if result['success']:
        print("✅ Streaming content generation: PASSED")
        print(f"Response: {result['data']['text'][:100]}...")
        return True
    else:
        print(f"❌ Streaming content generation: FAILED - {result['error']}")
        return False


def test_generation_config():
    """Test with generation configuration"""
    print("\n🧪 Testing Generation Configuration...")
    
    service = GeminiService()
    
    generation_config = {
        "temperature": 0.7,
        "topK": 40,
        "topP": 0.95,
        "maxOutputTokens": 1024
    }
    
    result = service.generate_content(
        "Create a creative textile design description",
        generation_config=generation_config
    )
    
    if result['success']:
        print("✅ Generation configuration: PASSED")
        print(f"Response: {result['data']['text'][:100]}...")
        return True
    else:
        print(f"❌ Generation configuration: FAILED - {result['error']}")
        return False


def main():
    """Run all tests"""
    print("🚀 Enhanced Gemini API Test Suite")
    print("=" * 50)
    
    tests = [
        test_basic_content_generation,
        test_multimodal_content,
        test_chat_conversation,
        test_textile_poster_generation,
        test_caption_generation,
        test_streaming_content,
        test_generation_config
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Enhanced Gemini API is working correctly.")
    else:
        print(f"⚠️  {total - passed} tests failed. Check the implementation.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
