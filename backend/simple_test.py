#!/usr/bin/env python3
"""
Simple test with minimal prompt
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

def test_simple_caption():
    print("Testing simple caption generation...")
    
    service = AICaptionService()
    
    if service.is_available():
        print("Testing with minimal prompt...")
        try:
            result = service.generate_social_media_caption(
                content="Beautiful silk saree",
                platform="instagram",
                post_type="product_showcase",
                style="engaging",
                tone="friendly",
                include_hashtags=True,
                include_emoji=True,
                call_to_action=True
            )
            
            print(f"Result: {result}")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("Service not available")

if __name__ == "__main__":
    test_simple_caption()
