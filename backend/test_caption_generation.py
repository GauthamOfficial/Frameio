#!/usr/bin/env python
"""Test script to verify caption generation is working"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from ai_services.ai_poster_service import AIPosterService
from django.contrib.auth import get_user_model

User = get_user_model()

def test_caption_generation():
    print("=" * 80)
    print("TESTING CAPTION GENERATION")
    print("=" * 80)
    
    # Initialize the service
    service = AIPosterService()
    
    # Check caption service
    print(f"\n1. Caption Service Status:")
    print(f"   - Client initialized: {service.caption_service.client is not None}")
    print(f"   - API key exists: {bool(service.caption_service.api_key)}")
    
    # Test caption generation
    print(f"\n2. Testing Caption Generation:")
    test_prompt = "A beautiful white party frock with elegant details, perfect for special occasions"
    
    try:
        result = service.generate_caption_and_hashtags(
            prompt=test_prompt,
            image_url="http://localhost:8000/media/test.png",
            user=None
        )
        
        print(f"\n3. Caption Generation Result:")
        print(f"   - Status: {result.get('status')}")
        print(f"   - Caption exists: {bool(result.get('caption'))}")
        print(f"   - Full caption exists: {bool(result.get('full_caption'))}")
        print(f"   - Hashtags count: {len(result.get('hashtags', []))}")
        
        if result.get('status') == 'success':
            print(f"\n4. Generated Content:")
            print(f"   - Caption (first 100 chars): {result.get('caption', '')[:100]}...")
            print(f"   - Hashtags (first 5): {result.get('hashtags', [])[:5]}")
            print(f"\n✅ Caption generation is WORKING!")
        else:
            print(f"\n❌ Caption generation FAILED!")
            print(f"   - Error: {result.get('message')}")
            
    except Exception as e:
        print(f"\n❌ Exception occurred: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    test_caption_generation()


