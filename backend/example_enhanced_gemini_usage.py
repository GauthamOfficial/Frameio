#!/usr/bin/env python3
"""
Enhanced Gemini API Usage Examples
Demonstrates the new implementation following official API structure
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

from ai_services.gemini_service import gemini_service


def example_basic_text_generation():
    """Example: Basic text generation"""
    print("📝 Basic Text Generation Example")
    print("-" * 40)
    
    result = gemini_service.generate_content("Explain how AI works in a few words")
    
    if result['success']:
        print(f"✅ Response: {result['data']['text']}")
        print(f"📊 Model: {result['data']['model_version']}")
        print(f"🔢 Tokens: {result['data']['usage_metadata']}")
    else:
        print(f"❌ Error: {result['error']}")
    
    print()


def example_textile_poster():
    """Example: Textile poster generation"""
    print("🎨 Textile Poster Generation Example")
    print("-" * 40)
    
    result = gemini_service.generate_textile_poster(
        fabric_type="saree",
        offer_text="Special Diwali Collection - 30% Off",
        festival="Diwali",
        price_range="₹2000-₹5000",
        style="traditional"
    )
    
    if result['success']:
        print(f"✅ Poster Description: {result['data']['text'][:200]}...")
    else:
        print(f"❌ Error: {result['error']}")
    
    print()


def example_multimodal_analysis():
    """Example: Multimodal content analysis"""
    print("🖼️ Multimodal Analysis Example")
    print("-" * 40)
    
    # Create a simple test image
    img = Image.new('RGB', (200, 200), color='blue')
    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    img_data = base64.b64encode(buffer.getvalue()).decode()
    
    result = gemini_service.generate_multimodal_content(
        text_prompt="What color is this image and what could it represent?",
        image_data=img_data,
        mime_type="image/jpeg"
    )
    
    if result['success']:
        print(f"✅ Analysis: {result['data']['text']}")
    else:
        print(f"❌ Error: {result['error']}")
    
    print()


def example_chat_conversation():
    """Example: Multi-turn conversation"""
    print("💬 Chat Conversation Example")
    print("-" * 40)
    
    messages = [
        {"role": "user", "content": "Hello, I need help with textile design."},
        {"role": "model", "content": "Hello! I'd be happy to help you with textile design. What specific aspect would you like to work on?"},
        {"role": "user", "content": "Create a modern saree design concept for a wedding collection."}
    ]
    
    result = gemini_service.create_chat_conversation(messages)
    
    if result['success']:
        print(f"✅ Response: {result['data']['text'][:200]}...")
    else:
        print(f"❌ Error: {result['error']}")
    
    print()


def example_marketing_captions():
    """Example: Marketing caption generation"""
    print("📢 Marketing Captions Example")
    print("-" * 40)
    
    result = gemini_service.generate_captions(
        fabric_type="kurta",
        festival="Eid",
        price_range="₹1500-₹3000",
        num_captions=3
    )
    
    if result['success']:
        print(f"✅ Captions: {result['data']['text']}")
    else:
        print(f"❌ Error: {result['error']}")
    
    print()


def example_streaming_content():
    """Example: Streaming content generation"""
    print("🌊 Streaming Content Example")
    print("-" * 40)
    
    result = gemini_service.stream_generate_content("Write a short poem about fashion")
    
    if result['success']:
        print(f"✅ Streamed Response: {result['data']['text'][:200]}...")
    else:
        print(f"❌ Error: {result['error']}")
    
    print()


def example_generation_config():
    """Example: Using generation configuration"""
    print("⚙️ Generation Configuration Example")
    print("-" * 40)
    
    generation_config = {
        "temperature": 0.8,
        "topK": 40,
        "topP": 0.95,
        "maxOutputTokens": 512
    }
    
    result = gemini_service.generate_content(
        "Create a creative textile design description",
        generation_config=generation_config
    )
    
    if result['success']:
        print(f"✅ Creative Response: {result['data']['text'][:200]}...")
    else:
        print(f"❌ Error: {result['error']}")
    
    print()


def main():
    """Run all examples"""
    print("🚀 Enhanced Gemini API Usage Examples")
    print("=" * 50)
    print()
    
    examples = [
        example_basic_text_generation,
        example_textile_poster,
        example_multimodal_analysis,
        example_chat_conversation,
        example_marketing_captions,
        example_streaming_content,
        example_generation_config
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"❌ Example failed: {str(e)}")
            print()
    
    print("=" * 50)
    print("✅ All examples completed!")


if __name__ == "__main__":
    main()
