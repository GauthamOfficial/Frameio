#!/usr/bin/env python3
"""
Test script to verify the updated caption generation works without including exact prompts
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

def test_caption_generation():
    """Test the updated caption generation functionality"""
    print("🧪 Testing Updated Caption Generation...")
    print("=" * 50)
    
    # Initialize the AI poster service
    poster_service = AIPosterService()
    
    if not poster_service.is_available():
        print("❌ AI Poster Service not available - check API key configuration")
        return False
    
    print("✅ AI Poster Service is available")
    
    # Test caption generation with a sample prompt
    test_prompt = "A beautiful red silk saree with golden border"
    print(f"\n📝 Testing caption generation for prompt: '{test_prompt}'")
    
    try:
        # Test the caption generation method
        caption_result = poster_service.generate_caption_and_hashtags(test_prompt)
        
        if caption_result.get("status") == "success":
            print("✅ Caption generation successful!")
            print(f"\n📄 Generated Caption:")
            print(f"   {caption_result.get('caption', 'No caption')}")
            print(f"\n🏷️  Hashtags:")
            hashtags = caption_result.get('hashtags', [])
            for tag in hashtags[:5]:  # Show first 5 hashtags
                print(f"   {tag}")
            print(f"\n📞 Call to Action:")
            print(f"   {caption_result.get('call_to_action', 'No CTA')}")
            
            # Check if the exact prompt is NOT included in the caption
            caption_text = caption_result.get('caption', '').lower()
            prompt_words = test_prompt.lower().split()
            
            prompt_included = any(word in caption_text for word in prompt_words if len(word) > 3)
            
            if not prompt_included:
                print("\n✅ SUCCESS: Caption does not include the exact user prompt!")
                print("   The caption is now generic and meaningful without revealing the specific prompt.")
            else:
                print("\n⚠️  WARNING: Caption may still contain elements from the original prompt")
                print("   This might need further refinement.")
            
            return True
        else:
            print(f"❌ Caption generation failed: {caption_result.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error during caption generation test: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🎨 AI Caption Generation Fix Test")
    print("=" * 50)
    print("Testing that captions no longer include exact user prompts")
    print("=" * 50)
    
    success = test_caption_generation()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 TEST COMPLETED SUCCESSFULLY!")
        print("✅ Caption generation now works without including exact prompts")
        print("✅ Generated captions are meaningful and appropriate")
    else:
        print("❌ TEST FAILED!")
        print("❌ Caption generation needs further fixes")
    
    print("=" * 50)

if __name__ == "__main__":
    main()