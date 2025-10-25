#!/usr/bin/env python3
"""
Test AI Caption Generation Service
"""
import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from ai_services.ai_caption_service import AICaptionService

def test_caption_generation():
    """Test the caption generation service"""
    print("Testing AI Caption Generation Service...")
    
    # Initialize the service
    caption_service = AICaptionService()
    
    if not caption_service.client:
        print("❌ Caption service not initialized. Check GEMINI_API_KEY.")
        return
    
    print("✅ Caption service initialized successfully")
    
    # Test prompts for textile products
    test_prompts = [
        "Beautiful silk saree for Diwali",
        "Elegant cotton kurta for summer",
        "Traditional handwoven shawl",
        "Modern printed dress for office",
        "Vintage style embroidered blouse"
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n--- Test {i}: {prompt} ---")
        
        try:
            # Generate caption for the prompt
            result = caption_service.generate_product_caption(
                product_name=prompt,
                product_type="textile",
                target_audience="fashion enthusiasts",
                caption_style="engaging",
                brand_voice="modern and elegant"
            )
            
            if result.get("status") == "success":
                caption_data = result.get("caption", {})
                print("✅ Caption generated successfully!")
                print(f"Main Text: {caption_data.get('main_text', 'N/A')}")
                print(f"Full Caption: {caption_data.get('full_caption', 'N/A')}")
                print(f"Hashtags: {caption_data.get('hashtags', [])}")
                print(f"Call to Action: {caption_data.get('call_to_action', 'N/A')}")
                print(f"Emoji: {caption_data.get('emoji', 'N/A')}")
            else:
                print(f"❌ Caption generation failed: {result.get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error generating caption: {str(e)}")
    
    print("\n" + "="*50)
    print("Caption generation test completed!")

if __name__ == "__main__":
    test_caption_generation()
