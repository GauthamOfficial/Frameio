#!/usr/bin/env python
"""
Test image generation functionality specifically
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

print("🚀 Testing Image Generation...")

try:
    from django.test import Client
    from django.contrib.auth import get_user_model
    from organizations.models import Organization
    
    User = get_user_model()
    
    # Get or create test user
    user, created = User.objects.get_or_create(
        username='testuser_image',
        defaults={
            'email': 'test_image@example.com',
            'password': 'testpass123'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print("✅ Created new test user")
    else:
        print("✅ Using existing test user")
    
    # Get or create test organization
    organization, created = Organization.objects.get_or_create(
        slug='test-org-image',
        defaults={'name': 'Test Image Organization'}
    )
    if created:
        print("✅ Created new test organization")
    else:
        print("✅ Using existing test organization")
    
    # Create membership if it doesn't exist
    membership, created = user.organization_memberships.get_or_create(
        organization=organization,
        defaults={'role': 'admin', 'is_active': True}
    )
    if created:
        print("✅ Created organization membership")
    else:
        print("✅ Using existing membership")
    
    client = Client()
    client.force_login(user)
    
    print("\n📸 Testing poster generation endpoint...")
    response = client.post('/api/ai/textile/poster/generate_poster_nanobanana/', {
        'image_url': 'https://example.com/fabric.jpg',
        'offer_text': 'Special Deepavali Offer - 50% Off!',
        'theme': 'festive',
        'fabric_type': 'silk',
        'festival': 'deepavali'
    }, content_type='application/json')
    
    print(f"   - Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   - Success: {data.get('success', False)}")
        print(f"   - Fallback: {data.get('fallback', False)}")
        print(f"   - Image URLs: {len(data.get('image_urls', []))}")
        if data.get('image_urls'):
            print(f"   - First URL: {data['image_urls'][0]}")
            print(f"   - All URLs: {data['image_urls']}")
    else:
        print(f"   - Error: {response.content.decode()}")
    
    print("\n📝 Testing caption generation endpoint...")
    response = client.post('/api/ai/textile/caption/generate_caption_nanobanana/', {
        'product_name': 'Luxury Silk Saree',
        'description': 'Beautiful traditional silk saree',
        'fabric_type': 'silk',
        'price_range': '₹2999'
    }, content_type='application/json')
    
    print(f"   - Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   - Success: {data.get('success', False)}")
        print(f"   - Fallback: {data.get('fallback', False)}")
        print(f"   - Captions: {len(data.get('captions', []))}")
        if data.get('captions'):
            print(f"   - First caption: {data['captions'][0]['text'][:50]}...")
    else:
        print(f"   - Error: {response.content.decode()}")
    
    print("\n🔧 Testing NanoBanana service directly...")
    from ai_services.nanobanana_service import NanoBananaAIService
    
    service = NanoBananaAIService()
    print(f"   - Service available: {service.is_available()}")
    print(f"   - API key configured: {bool(service.api_key)}")
    print(f"   - Client initialized: {service.client is not None}")
    
    # Test direct service call
    result = service.generate_poster(
        image_url='https://example.com/test.jpg',
        offer_text='Test Offer',
        theme='modern'
    )
    
    print(f"   - Direct service success: {result.get('success', False)}")
    print(f"   - Fallback used: {result.get('fallback', False)}")
    print(f"   - Images generated: {len(result.get('image_urls', []))}")
    if result.get('image_urls'):
        print(f"   - Generated URLs: {result['image_urls']}")
    
    print("\n🎉 Image generation tests completed!")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()