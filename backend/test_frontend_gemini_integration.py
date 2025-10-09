#!/usr/bin/env python3
"""
Test script for Frontend Gemini 2.5 Flash Integration
Tests the complete flow from frontend request to Gemini 2.5 Flash generation
"""
import os
import sys
import django
import time

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from ai_services.poster_generator import TextilePosterGenerator
from ai_services.gemini_2_5_flash_image_service import gemini_2_5_flash_image_service
from organizations.models import Organization
from users.models import User


def test_gemini_poster_generation():
    """Test Gemini 2.5 Flash poster generation through the poster generator"""
    print("🧪 Testing Gemini 2.5 Flash Poster Generation...")
    
    try:
        # Create test organization and user
        org, org_created = Organization.objects.get_or_create(
            name="Test Organization",
            defaults={'description': 'Test organization for Gemini integration'}
        )
        
        user, user_created = User.objects.get_or_create(
            email="test@example.com",
            defaults={'first_name': 'Test', 'last_name': 'User'}
        )
        
        if org_created:
            print(f"✅ Created test organization: {org.name}")
        if user_created:
            print(f"✅ Created test user: {user.email}")
        
        # Initialize poster generator
        poster_generator = TextilePosterGenerator()
        
        # Test poster generation
        result = poster_generator.generate_poster_with_caption(
            organization=org,
            user=user,
            fabric_type='silk saree',
            festival='deepavali',
            price_range='₹2999',
            style='elegant',
            custom_text='Special Diwali Collection',
            offer_details='30% Off on all items'
        )
        
        if result.get('success'):
            print("✅ Poster generation successful!")
            print(f"🖼️  Poster URL: {result.get('poster_url', 'N/A')}")
            print(f"📊 Service: {result.get('service', 'N/A')}")
            print(f"⏱️  Processing Time: {result.get('processing_time', 'N/A')}s")
            print(f"💰 Cost: ₹{result.get('cost', 0)}")
            print(f"🆔 Request ID: {result.get('request_id', 'N/A')}")
            
            # Check caption suggestions
            captions = result.get('caption_suggestions', [])
            if captions:
                print(f"📝 Caption Suggestions ({len(captions)}):")
                for i, caption in enumerate(captions[:3], 1):
                    print(f"  {i}. {caption.get('text', 'N/A')}")
            
            return True
        else:
            print(f"❌ Poster generation failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing poster generation: {str(e)}")
        return False


def test_direct_gemini_service():
    """Test Gemini 2.5 Flash service directly"""
    print("\n🧪 Testing Direct Gemini 2.5 Flash Service...")
    
    try:
        # Test direct service
        result = gemini_2_5_flash_image_service.generate_poster(
            fabric_type='cotton kurta',
            offer_text='Summer Collection - 50% Off',
            theme='modern',
            festival='general',
            price_range='₹1999'
        )
        
        if result.get('success'):
            print("✅ Direct Gemini service successful!")
            print(f"🖼️  Image URL: {result.get('image_url', 'N/A')}")
            print(f"📊 Service: {result.get('service', 'N/A')}")
            print(f"⏱️  Processing Time: {result.get('processing_time', 'N/A')}s")
            return True
        else:
            print(f"❌ Direct Gemini service failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing direct Gemini service: {str(e)}")
        return False


def test_api_endpoint_simulation():
    """Test API endpoint simulation"""
    print("\n🧪 Testing API Endpoint Simulation...")
    
    try:
        from ai_services.textile_views import TextilePosterViewSet
        from rest_framework.test import APIRequestFactory
        from django.contrib.auth import get_user_model
        
        # Create test data
        factory = APIRequestFactory()
        request_data = {
            'product_image_url': 'https://example.com/fabric.jpg',
            'fabric_type': 'silk saree',
            'festival': 'deepavali',
            'price_range': '₹2999',
            'style': 'elegant',
            'custom_text': 'Special Diwali Collection',
            'offer_details': '30% Off on all items'
        }
        
        # Create request
        request = factory.post('/api/textile/poster/', request_data, format='json')
        
        # Create test user and organization
        User = get_user_model()
        user, _ = User.objects.get_or_create(
            email="test@example.com",
            defaults={'first_name': 'Test', 'last_name': 'User'}
        )
        request.user = user
        
        # Mock organization context
        from unittest.mock import patch
        with patch('ai_services.textile_views.get_current_organization') as mock_org:
            org, _ = Organization.objects.get_or_create(
                name="Test Organization",
                defaults={'description': 'Test organization'}
            )
            mock_org.return_value = org
            
            # Test the viewset
            viewset = TextilePosterViewSet()
            response = viewset.generate_poster(request)
            
            if response.status_code == 200:
                data = response.data
                if data.get('success'):
                    print("✅ API endpoint simulation successful!")
                    print(f"🖼️  Poster URL: {data.get('poster_url', 'N/A')}")
                    print(f"📊 Cache Bust: {data.get('cache_bust', 'N/A')}")
                    return True
                else:
                    print(f"❌ API endpoint failed: {data.get('error', 'Unknown error')}")
                    return False
            else:
                print(f"❌ API endpoint returned status {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Error testing API endpoint: {str(e)}")
        return False


def run_comprehensive_frontend_test():
    """Run comprehensive frontend integration test"""
    print("🚀 Starting Frontend Gemini 2.5 Flash Integration Test")
    print("=" * 70)
    
    tests = [
        ("Direct Gemini Service", test_direct_gemini_service),
        ("Poster Generator Integration", test_gemini_poster_generation),
        ("API Endpoint Simulation", test_api_endpoint_simulation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*70)
    print("📊 FRONTEND INTEGRATION TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\n📈 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All frontend integration tests passed! Gemini 2.5 Flash is ready for production use.")
        print("\n🚀 Your site can now generate images using Gemini 2.5 Flash instead of fallback mode!")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total


if __name__ == "__main__":
    success = run_comprehensive_frontend_test()
    sys.exit(0 if success else 1)
