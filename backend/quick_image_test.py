#!/usr/bin/env python
"""
Quick test for image generation
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

# Set API key
os.environ['NANOBANANA_API_KEY'] = 'AIzaSyBBP1QGjY7lJBhjNwWMSJCIOZC1bWgSzMY'

print("🚀 Quick Image Generation Test")

try:
    from ai_services.nanobanana_service import NanoBananaAIService
    
    service = NanoBananaAIService()
    print(f"✅ Service created - API Key: {bool(service.api_key)}")
    
    # Test basic generation
    result = service.generate_poster(
        image_url="https://example.com/fabric.jpg",
        offer_text="Test Offer",
        theme="modern"
    )
    
    print(f"✅ Result:")
    print(f"   - Success: {result.get('success')}")
    print(f"   - Fallback: {result.get('fallback')}")
    print(f"   - Image URLs: {result.get('image_urls', [])}")
    print(f"   - Generation ID: {result.get('generation_id')}")
    
    # Test textile service
    from ai_services.services import NanoBananaTextileService
    textile_service = NanoBananaTextileService()
    
    textile_result = textile_service.generate_textile_poster(
        image_url="https://example.com/silk.jpg",
        offer_text="Silk Collection",
        theme="elegant",
        fabric_type="silk",
        festival="deepavali"
    )
    
    print(f"\n✅ Textile Result:")
    print(f"   - Success: {textile_result.get('success')}")
    print(f"   - Textile specific: {textile_result.get('textile_specific')}")
    print(f"   - Fabric type: {textile_result.get('fabric_type')}")
    print(f"   - Festival: {textile_result.get('festival')}")
    print(f"   - Image URLs: {textile_result.get('image_urls', [])}")
    
    print("\n🎉 Image generation test completed!")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()

