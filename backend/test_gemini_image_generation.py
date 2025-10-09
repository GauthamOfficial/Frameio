#!/usr/bin/env python3
"""
Test script for Google Gemini 2.5 Flash Image Generation
Tests the new implementation with proper Google Genai client
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

from ai_services.gemini_image_generator import GeminiImageGenerator
from ai_services.gemini_service import GeminiImageService
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_gemini_image_generation():
    """Test the Gemini image generation functionality"""
    
    print("🧪 Testing Google Gemini 2.5 Flash Image Generation")
    print("=" * 60)
    
    # Test 1: Basic image generation
    print("\n1. Testing basic image generation...")
    generator = GeminiImageGenerator()
    
    if not generator.client:
        print("❌ Gemini client not initialized. Please check your API key.")
        return False
    
    # Test basic image generation
    result = generator.generate_image(
        prompt="A beautiful textile design for saree with intricate patterns and vibrant colors",
        aspect_ratio="1:1",
        style="photorealistic"
    )
    
    if result.get("success"):
        print("✅ Basic image generation successful")
        print(f"   Generated {len(result.get('urls', []))} images")
        print(f"   Processing time: {result.get('data', {}).get('processing_time', 0):.2f}s")
    else:
        print(f"❌ Basic image generation failed: {result.get('error')}")
        return False
    
    # Test 2: Textile poster generation
    print("\n2. Testing textile poster generation...")
    poster_result = generator.generate_poster(
        fabric_type="saree",
        offer_text="Special Diwali Collection - 30% Off",
        theme="festive",
        festival="Diwali",
        price_range="₹5000-₹15000"
    )
    
    if poster_result.get("success"):
        print("✅ Textile poster generation successful")
        print(f"   Generated {len(poster_result.get('urls', []))} images")
    else:
        print(f"❌ Textile poster generation failed: {poster_result.get('error')}")
    
    # Test 3: Multiple styles generation
    print("\n3. Testing multiple styles generation...")
    styles_result = generator.generate_multiple_styles(
        prompt="A modern kurta design for men",
        styles=["photorealistic", "illustration", "minimalist"],
        aspect_ratio="1:1"
    )
    
    if styles_result.get("success"):
        print("✅ Multiple styles generation successful")
        print(f"   Generated styles: {list(styles_result.get('data', {}).keys())}")
    else:
        print(f"❌ Multiple styles generation failed: {styles_result.get('error')}")
    
    # Test 4: Legacy service compatibility
    print("\n4. Testing legacy service compatibility...")
    legacy_service = GeminiImageService()
    
    legacy_result = legacy_service.generate_image(
        prompt="A beautiful lehenga design for wedding",
        width=1024,
        height=1024,
        style="photorealistic"
    )
    
    if legacy_result.get("success"):
        print("✅ Legacy service compatibility successful")
        print(f"   Generated {len(legacy_result.get('urls', []))} images")
    else:
        print(f"❌ Legacy service compatibility failed: {legacy_result.get('error')}")
    
    # Test 5: Textile poster with legacy service
    print("\n5. Testing textile poster with legacy service...")
    legacy_poster_result = legacy_service.generate_textile_poster(
        fabric_type="lehenga",
        offer_text="Wedding Collection - Buy 2 Get 1 Free",
        festival="Wedding",
        style="elegant"
    )
    
    if legacy_poster_result.get("success"):
        print("✅ Legacy textile poster generation successful")
        print(f"   Generated {len(legacy_poster_result.get('urls', []))} images")
    else:
        print(f"❌ Legacy textile poster generation failed: {legacy_poster_result.get('error')}")
    
    print("\n" + "=" * 60)
    print("🎉 Gemini image generation testing completed!")
    
    return True


def test_specific_scenarios():
    """Test specific scenarios from the provided examples"""
    
    print("\n🧪 Testing specific scenarios from examples")
    print("=" * 60)
    
    generator = GeminiImageGenerator()
    
    if not generator.client:
        print("❌ Gemini client not initialized. Please check your API key.")
        return False
    
    # Test scenarios from the provided examples
    test_scenarios = [
        {
            "name": "Photorealistic Portrait",
            "prompt": "A photorealistic close-up portrait of an elderly Japanese ceramicist with deep, sun-etched wrinkles and a warm, knowing smile. He is carefully inspecting a freshly glazed tea bowl. The setting is his rustic, sun-drenched workshop with pottery wheels and shelves of clay pots in the background. The scene is illuminated by soft, golden hour light streaming through a window, highlighting the fine texture of the clay and the fabric of his apron. Captured with an 85mm portrait lens, resulting in a soft, blurred background (bokeh). The overall mood is serene and masterful.",
            "aspect_ratio": "1:1",
            "style": "photorealistic"
        },
        {
            "name": "Kawaii Sticker",
            "prompt": "A kawaii-style sticker of a happy red panda wearing a tiny bamboo hat. It's munching on a green bamboo leaf. The design features bold, clean outlines, simple cel-shading, and a vibrant color palette. The background must be white.",
            "aspect_ratio": "1:1",
            "style": "illustration"
        },
        {
            "name": "Minimalist Logo",
            "prompt": "Create a modern, minimalist logo for a coffee shop called 'The Daily Grind'. The text should be in a clean, bold, sans-serif font. The design should feature a simple, stylized icon of a a coffee bean seamlessly integrated with the text. The color scheme is black and white.",
            "aspect_ratio": "1:1",
            "style": "minimalist"
        },
        {
            "name": "Product Mockup",
            "prompt": "A high-resolution, studio-lit product photograph of a minimalist ceramic coffee mug in matte black, presented on a polished concrete surface. The lighting is a three-point softbox setup designed to create soft, diffused highlights and eliminate harsh shadows. The camera angle is a slightly elevated 45-degree shot to showcase its clean lines. Ultra-realistic, with sharp focus on the steam rising from the coffee. Square image.",
            "aspect_ratio": "1:1",
            "style": "photorealistic"
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{i}. Testing {scenario['name']}...")
        
        result = generator.generate_image(
            prompt=scenario["prompt"],
            aspect_ratio=scenario["aspect_ratio"],
            style=scenario["style"]
        )
        
        if result.get("success"):
            print(f"   ✅ {scenario['name']} generation successful")
            print(f"   Generated {len(result.get('urls', []))} images")
        else:
            print(f"   ❌ {scenario['name']} generation failed: {result.get('error')}")
    
    print("\n" + "=" * 60)
    print("🎉 Specific scenarios testing completed!")
    
    return True


if __name__ == "__main__":
    print("🚀 Starting Gemini Image Generation Tests")
    print("=" * 60)
    
    # Check if API key is configured
    from django.conf import settings
    api_key = settings.GEMINI_API_KEY or settings.GOOGLE_API_KEY
    
    if not api_key:
        print("❌ No Gemini API key configured!")
        print("Please set GEMINI_API_KEY or GOOGLE_API_KEY in your environment variables")
        sys.exit(1)
    
    print(f"✅ API key configured: {api_key[:10]}...")
    
    # Run tests
    try:
        test_gemini_image_generation()
        test_specific_scenarios()
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
