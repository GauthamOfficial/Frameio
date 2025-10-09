#!/usr/bin/env python3
"""
Test script to verify AI poster generation is working correctly
and generating fresh content instead of static images.
"""

import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from ai_services.textile_views import TextilePosterViewSet
from ai_services.models import AIGenerationRequest, AIProvider
from organizations.models import Organization
from django.contrib.auth.models import User
import json

def test_poster_generation():
    """Test that poster generation creates fresh content"""
    print("🧪 Testing AI Poster Generation...")
    
    try:
        # Create test data
        viewset = TextilePosterViewSet()
        
        # Mock request data
        request_data = {
            'product_image_url': 'https://example.com/test-image.jpg',
            'fabric_type': 'silk',
            'festival': 'deepavali',
            'price_range': '₹2999',
            'style': 'elegant',
            'custom_text': 'Test AI generation',
            'offer_details': 'Special offer'
        }
        
        print(f"📝 Request data: {json.dumps(request_data, indent=2)}")
        
        # Test the generation process
        result = viewset.poster_generator.generate_poster_with_caption(
            organization=None,  # Will be mocked
            user=None,  # Will be mocked
            fabric_image_url=request_data['product_image_url'],
            fabric_type=request_data['fabric_type'],
            festival=request_data['festival'],
            price_range=request_data['price_range'],
            style=request_data['style'],
            custom_text=request_data['custom_text'],
            offer_details=request_data['offer_details']
        )
        
        print(f"✅ Generation result: {json.dumps(result, indent=2)}")
        
        # Check if result contains fresh content indicators
        if result.get('success'):
            print("✅ Poster generation successful!")
            
            # Check for unique identifiers
            if 'request_id' in result:
                print(f"✅ Generated unique request ID: {result['request_id']}")
            
            # Check for fresh URLs (not static images)
            poster_urls = result.get('poster_urls', [])
            if poster_urls:
                print(f"✅ Generated {len(poster_urls)} poster URLs")
                for i, url in enumerate(poster_urls):
                    print(f"   📸 Poster {i+1}: {url}")
                    
                # Check if URLs contain unique identifiers
                unique_indicators = ['random=', 'timestamp=', 'gen_', 'unique']
                has_unique_content = any(indicator in str(poster_urls) for indicator in unique_indicators)
                
                if has_unique_content:
                    print("✅ URLs contain unique identifiers - fresh content generated!")
                else:
                    print("⚠️  URLs may be static - check for unique content")
            else:
                print("⚠️  No poster URLs generated")
                
            # Check captions
            captions = result.get('caption_suggestions', [])
            if captions:
                print(f"✅ Generated {len(captions)} caption suggestions:")
                for i, caption in enumerate(captions):
                    print(f"   📝 Caption {i+1}: {caption}")
            else:
                print("⚠️  No caption suggestions generated")
                
        else:
            print(f"❌ Poster generation failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

def test_caption_generation():
    """Test caption generation"""
    print("\n🧪 Testing Caption Generation...")
    
    try:
        viewset = TextilePosterViewSet()
        
        captions = viewset.poster_generator.generate_caption_suggestions(
            fabric_type='silk',
            festival='deepavali',
            price_range='₹2999',
            style='elegant',
            custom_text='Test caption generation'
        )
        
        print(f"✅ Generated {len(captions)} captions:")
        for i, caption in enumerate(captions):
            print(f"   📝 Caption {i+1}: {caption.get('text', 'N/A')}")
            print(f"      Type: {caption.get('type', 'N/A')}")
            print(f"      Tone: {caption.get('tone', 'N/A')}")
            print(f"      Score: {caption.get('effectiveness_score', 'N/A')}")
            
    except Exception as e:
        print(f"❌ Caption test failed: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting AI Poster Generation Tests...")
    test_poster_generation()
    test_caption_generation()
    print("\n✅ Tests completed!")
