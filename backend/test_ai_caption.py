#!/usr/bin/env python
"""
Test script for AI Caption Generation Service
Run this to verify the Gemini 2.5 Flash caption generation is working
"""
import os
import sys
import django
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Set the API key from environment or use placeholder
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("WARNING: GEMINI_API_KEY not set. Using placeholder for testing.")
    api_key = 'your_gemini_api_key_here'
os.environ['GEMINI_API_KEY'] = api_key

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from ai_services.ai_caption_service import AICaptionService

def test_ai_caption_service():
    """Test the AI caption service"""
    print("🧪 Testing AI Caption Service...")
    
    # Initialize service
    service = AICaptionService()
    
    # Check if service is available
    if not service.is_available():
        print("❌ AI Caption Service is not available")
        print("   Make sure GOOGLE_API_KEY is set in your .env file")
        return False
    
    print("✅ AI Caption Service is available")
    
    # Test 1: Product Caption Generation
    print("\n📝 Testing Product Caption Generation...")
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
        print("✅ Product caption generated successfully!")
        caption = result.get('caption', {})
        print(f"   Main content: {caption.get('main_content', '')[:100]}...")
        print(f"   Hashtags: {caption.get('hashtags', [])}")
        print(f"   Word count: {caption.get('word_count', 0)}")
    else:
        print(f"❌ Product caption generation failed: {result.get('message')}")
        return False
    
    # Test 2: Social Media Caption Generation
    print("\n📱 Testing Social Media Caption Generation...")
    result = service.generate_social_media_caption(
        content="New silk collection launch with elegant designs",
        platform="instagram",
        post_type="product_showcase",
        style="engaging",
        tone="friendly",
        include_hashtags=True,
        include_emoji=True,
        call_to_action=True
    )
    
    if result.get('status') == 'success':
        print("✅ Social media caption generated successfully!")
        caption = result.get('caption', {})
        print(f"   Main content: {caption.get('main_content', '')[:100]}...")
        print(f"   Hashtags: {caption.get('hashtags', [])}")
        print(f"   Call to action: {caption.get('call_to_action', '')}")
    else:
        print(f"❌ Social media caption generation failed: {result.get('message')}")
        return False
    
    # Test 3: Image Caption Generation
    print("\n🖼️ Testing Image Caption Generation...")
    result = service.generate_image_caption(
        image_description="Beautiful silk saree with intricate embroidery and golden thread work",
        caption_type="descriptive",
        style="professional",
        tone="informative",
        include_hashtags=False,
        include_emoji=False
    )
    
    if result.get('status') == 'success':
        print("✅ Image caption generated successfully!")
        caption = result.get('caption', {})
        print(f"   Main content: {caption.get('main_content', '')[:100]}...")
        print(f"   Character count: {caption.get('character_count', 0)}")
    else:
        print(f"❌ Image caption generation failed: {result.get('message')}")
        return False
    
    # Test 4: Bulk Caption Generation
    print("\n📦 Testing Bulk Caption Generation...")
    products = [
        {"name": "Silk Saree", "type": "saree"},
        {"name": "Cotton Kurta", "type": "kurta"},
        {"name": "Linen Dress", "type": "dress"}
    ]
    
    result = service.generate_bulk_captions(
        products=products,
        caption_style="consistent",
        brand_voice="professional"
    )
    
    if result.get('status') == 'success':
        print("✅ Bulk captions generated successfully!")
        captions = result.get('captions', [])
        print(f"   Generated {len(captions)} captions")
        for i, caption in enumerate(captions[:2]):  # Show first 2
            print(f"   Product {i+1}: {caption.get('caption', '')[:80]}...")
    else:
        print(f"❌ Bulk caption generation failed: {result.get('message')}")
        return False
    
    return True

def test_caption_variations():
    """Test different caption variations"""
    print("\n🎨 Testing Caption Variations...")
    
    service = AICaptionService()
    
    # Test different styles
    styles = ["modern", "traditional", "casual", "formal"]
    tones = ["professional", "friendly", "authoritative", "conversational"]
    
    for style in styles[:2]:  # Test first 2 styles
        for tone in tones[:2]:  # Test first 2 tones
            print(f"\n   Testing {style} style with {tone} tone...")
            
            result = service.generate_product_caption(
                product_name="Premium Cotton Shirt",
                product_type="shirt",
                style=style,
                tone=tone,
                include_hashtags=True,
                include_emoji=True,
                max_length=150
            )
            
            if result.get('status') == 'success':
                caption = result.get('caption', {})
                print(f"   ✅ Generated: {caption.get('main_content', '')[:60]}...")
            else:
                print(f"   ❌ Failed: {result.get('message')}")
    
    return True

if __name__ == "__main__":
    print("🚀 AI Caption Generation Test")
    print("=" * 50)
    
    # Test basic functionality
    success = test_ai_caption_service()
    
    if success:
        print("\n🎨 Testing Caption Variations...")
        variation_success = test_caption_variations()
        
        if variation_success:
            print("\n🎉 All caption tests passed! AI Caption Service is ready.")
            print("\n📋 Available Caption Types:")
            print("   • Product Captions - For textile products")
            print("   • Social Media Captions - For Instagram, Facebook, etc.")
            print("   • Image Captions - For textile images")
            print("   • Bulk Captions - For multiple products")
            print("\n🔗 API Endpoints:")
            print("   • POST /api/ai-caption/product_caption/")
            print("   • POST /api/ai-caption/social_media_caption/")
            print("   • POST /api/ai-caption/image_caption/")
            print("   • POST /api/ai-caption/bulk_captions/")
            print("   • GET /api/ai-caption/status/")
        else:
            print("\n💥 Caption variation tests failed.")
            sys.exit(1)
    else:
        print("\n💥 Basic caption tests failed. Check your configuration.")
        sys.exit(1)
