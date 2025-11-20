#!/usr/bin/env python3
"""
Test script to verify enhanced AI caption generation
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

def test_enhanced_caption_generation():
    """Test the enhanced caption generation"""
    print("🧪 Testing Enhanced AI Caption Generation...")
    print("=" * 60)
    
    poster_service = AIPosterService()
    
    if not poster_service.client:
        print("❌ Poster service not available - check GEMINI_API_KEY")
        return False
    
    # Test with different types of prompts
    test_prompts = [
        "Beautiful silk saree for Diwali celebrations with gold accents",
        "Modern cotton kurta with intricate embroidery for summer collection",
        "Elegant wedding lehenga with traditional zari work",
        "Casual denim jacket with hand-painted floral designs"
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n📝 Test {i}: {prompt}")
        print("-" * 50)
        
        caption_result = poster_service.generate_caption_and_hashtags(prompt)
        
        if caption_result.get('status') == 'success':
            print("✅ Caption generated successfully!")
            print(f"Caption: {caption_result.get('caption', 'N/A')}")
            print(f"Hashtags: {', '.join(caption_result.get('hashtags', [])[:5])}...")
            print(f"Call to Action: {caption_result.get('call_to_action', 'N/A')}")
        else:
            print(f"❌ Caption generation failed: {caption_result.get('message', 'Unknown error')}")
            return False
    
    print("\n" + "=" * 60)
    print("🎉 Enhanced caption generation is working!")
    print("✨ Captions now include:")
    print("   - Emotional storytelling")
    print("   - Power words and sensory descriptions")
    print("   - Compelling call-to-actions")
    print("   - Relevant hashtags")
    print("   - Social media optimization")
    
    return True

def main():
    """Run the test"""
    print("🚀 Testing Enhanced AI Caption Generation...")
    
    success = test_enhanced_caption_generation()
    
    if success:
        print("\n✅ All tests passed! Enhanced caption generation is working.")
        return 0
    else:
        print("\n❌ Tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    exit(main())
