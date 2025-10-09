#!/usr/bin/env python3
"""
Test fresh generation to verify no caching
"""
import os
import sys
import django
from django.conf import settings

# Add the backend directory to Python path
sys.path.append('.')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

def test_fresh_generation():
    """Test that we get fresh content every time"""
    print("=" * 60)
    print("TESTING FRESH GENERATION (NO CACHING)")
    print("=" * 60)
    
    try:
        from ai_services.nanobanana_service import NanoBananaAIService
        
        service = NanoBananaAIService()
        
        print("Generating 3 posters to test uniqueness...")
        all_urls = []
        all_captions = []
        
        for i in range(3):
            print(f"\nGeneration {i+1}:")
            
            # Test poster generation
            result = service.generate_poster(
                image_url=f'https://example.com/test-image-{i}.jpg',
                offer_text=f'Test Offer {i}',
                theme='modern'
            )
            
            if result.get('success'):
                urls = result.get('image_urls', [])
                all_urls.extend(urls)
                print(f"   Generated {len(urls)} images")
                print(f"   First image: {urls[0][:50]}...")
            else:
                print(f"   Error: {result.get('error', 'Unknown error')}")
            
            # Test caption generation
            caption_result = service.generate_caption(
                product_name=f'Test Product {i}',
                description=f'Beautiful textile product {i}'
            )
            
            if caption_result.get('success'):
                captions = caption_result.get('captions', [])
                all_captions.extend(captions)
                print(f"   Generated {len(captions)} captions")
                print(f"   First caption: {captions[0].get('text', 'N/A')[:50]}...")
            else:
                print(f"   Caption error: {caption_result.get('error', 'Unknown error')}")
        
        # Check uniqueness
        print(f"\n" + "=" * 40)
        print("UNIQUENESS CHECK")
        print("=" * 40)
        
        unique_urls = set(all_urls)
        unique_captions = set(caption.get('text', '') for caption in all_captions)
        
        print(f"Total URLs generated: {len(all_urls)}")
        print(f"Unique URLs: {len(unique_urls)}")
        print(f"URL uniqueness: {'✓ ALL UNIQUE' if len(unique_urls) == len(all_urls) else '✗ SOME DUPLICATES'}")
        
        print(f"\nTotal captions generated: {len(all_captions)}")
        print(f"Unique captions: {len(unique_captions)}")
        print(f"Caption uniqueness: {'✓ ALL UNIQUE' if len(unique_captions) == len(all_captions) else '✗ SOME DUPLICATES'}")
        
        if len(unique_urls) == len(all_urls) and len(unique_captions) == len(all_captions):
            print("\n🎉 SUCCESS: All content is unique!")
            print("   The caching issue has been resolved.")
        else:
            print("\n⚠️  WARNING: Some content is still duplicated.")
            print("   There may still be caching issues.")
            
    except Exception as e:
        print(f"✗ Error testing fresh generation: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_fresh_generation()
