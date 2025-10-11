#!/usr/bin/env python3
"""
Test script to verify AI caption and hashtag generation integration
"""
import os
import sys
import django

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from ai_services.ai_poster_service import AIPosterService
from ai_services.ai_caption_service import AICaptionService

def test_caption_service():
    """Test the AI caption service directly"""
    print("🧪 Testing AI Caption Service...")
    
    caption_service = AICaptionService()
    
    if not caption_service.client:
        print("❌ Caption service not available - check GEMINI_API_KEY")
        return False
    
    # Test product caption generation
    result = caption_service.generate_product_caption(
        product_name="Beautiful Silk Saree",
        product_type="saree",
        style="modern",
        tone="friendly",
        include_hashtags=True,
        include_emoji=True
    )
    
    if result.get('status') == 'success':
        print("✅ Caption service working!")
        print(f"Caption: {result.get('caption', {}).get('main_text', 'N/A')}")
        print(f"Hashtags: {result.get('caption', {}).get('hashtags', [])}")
        return True
    else:
        print(f"❌ Caption service failed: {result.get('message', 'Unknown error')}")
        return False

def test_poster_service():
    """Test the AI poster service with caption generation"""
    print("\n🧪 Testing AI Poster Service with Caption Generation...")
    
    poster_service = AIPosterService()
    
    if not poster_service.client:
        print("❌ Poster service not available - check GEMINI_API_KEY")
        return False
    
    # Test caption generation method
    caption_result = poster_service.generate_caption_and_hashtags(
        prompt="Beautiful silk saree for Diwali celebrations with gold accents",
        image_url="http://example.com/test.jpg"
    )
    
    if caption_result.get('status') == 'success':
        print("✅ Poster service caption generation working!")
        print(f"Caption: {caption_result.get('caption', 'N/A')}")
        print(f"Hashtags: {caption_result.get('hashtags', [])}")
        print(f"Full Caption: {caption_result.get('full_caption', 'N/A')}")
        return True
    else:
        print(f"❌ Poster service caption generation failed: {caption_result.get('message', 'Unknown error')}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing AI Caption and Hashtag Integration...")
    print("=" * 50)
    
    # Test caption service
    caption_ok = test_caption_service()
    
    # Test poster service
    poster_ok = test_poster_service()
    
    print("\n" + "=" * 50)
    if caption_ok and poster_ok:
        print("🎉 All tests passed! Caption and hashtag generation is working.")
        return 0
    else:
        print("❌ Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    exit(main())
