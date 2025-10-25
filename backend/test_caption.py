#!/usr/bin/env python3
"""
Test script to check the AI caption service directly
"""
import os
import sys

# Set the API key
os.environ['GEMINI_API_KEY'] = 'AIzaSyCdASB6S3egrc3tj7tRQ5ER6S7DgNzh2ps'

# Add the current directory to Python path
sys.path.append('.')

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')

import django
django.setup()

from ai_services.ai_caption_service import AICaptionService

def test_caption_service():
    print("Testing AI Caption Service...")
    
    service = AICaptionService()
    print(f"Service available: {service.is_available()}")
    print(f"Client available: {service.client is not None}")
    print(f"API key available: {bool(service.api_key)}")
    
    if service.is_available():
        print("\nTesting caption generation...")
        try:
            result = service.generate_social_media_caption(
                content="Create an engaging social media caption for a beautiful textile/fashion poster",
                platform="instagram",
                post_type="product_showcase",
                style="engaging",
                tone="friendly",
                include_hashtags=True,
                include_emoji=True,
                call_to_action=True
            )
            
            print(f"Caption generation result: {result}")
            
            if result.get('status') == 'success':
                caption_data = result.get('caption', {})
                print(f"✅ Caption generated successfully!")
                print(f"Main text: {caption_data.get('main_text', 'N/A')}")
                print(f"Full caption: {caption_data.get('full_caption', 'N/A')}")
                print(f"Hashtags: {caption_data.get('hashtags', 'N/A')}")
                print(f"Emoji: {caption_data.get('emoji', 'N/A')}")
                print(f"Call to action: {caption_data.get('call_to_action', 'N/A')}")
            else:
                print(f"❌ Caption generation failed: {result.get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error during caption generation: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ Caption service is not available")

if __name__ == "__main__":
    test_caption_service()
