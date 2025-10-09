#!/usr/bin/env python
"""
HTTP test for image generation endpoints
"""
import requests
import json
import time

print("🚀 Testing Image Generation via HTTP...")

# Wait for server to start
time.sleep(3)

base_url = "http://localhost:8000"

# Test data
poster_data = {
    "image_url": "https://example.com/fabric.jpg",
    "offer_text": "Special Deepavali Offer",
    "theme": "festive",
    "fabric_type": "silk",
    "festival": "deepavali"
}

caption_data = {
    "product_name": "Silk Saree",
    "description": "Beautiful traditional silk saree",
    "fabric_type": "silk",
    "price_range": "₹2999"
}

try:
    # Test poster generation
    print("\n📸 Testing poster generation...")
    response = requests.post(
        f"{base_url}/api/ai/textile/poster/generate_poster_nanobanana/",
        json=poster_data,
        headers={'Content-Type': 'application/json'},
        timeout=30
    )
    
    print(f"   - Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   - Success: {data.get('success', False)}")
        print(f"   - Fallback: {data.get('fallback', False)}")
        print(f"   - Image URLs: {len(data.get('image_urls', []))}")
        if data.get('image_urls'):
            print(f"   - First URL: {data['image_urls'][0]}")
    else:
        print(f"   - Error: {response.text}")
    
    # Test caption generation
    print("\n📝 Testing caption generation...")
    response = requests.post(
        f"{base_url}/api/ai/textile/caption/generate_caption_nanobanana/",
        json=caption_data,
        headers={'Content-Type': 'application/json'},
        timeout=30
    )
    
    print(f"   - Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   - Success: {data.get('success', False)}")
        print(f"   - Fallback: {data.get('fallback', False)}")
        print(f"   - Captions: {len(data.get('captions', []))}")
        if data.get('captions'):
            print(f"   - First caption: {data['captions'][0]['text'][:50]}...")
    else:
        print(f"   - Error: {response.text}")
    
    print("\n🎉 HTTP tests completed!")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()

