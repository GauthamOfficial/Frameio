#!/usr/bin/env python3
"""
Test the frontend API endpoint to ensure it's using Gemini 2.5 Flash
"""
import os
import sys
import django
import requests
import json

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from organizations.models import Organization


def test_frontend_api_endpoint():
    """Test the frontend API endpoint directly"""
    print("🧪 Testing Frontend API Endpoint...")
    
    try:
        # Create test client
        client = Client()
        
        # Create test user and organization
        User = get_user_model()
        user, _ = User.objects.get_or_create(
            email="test@example.com",
            defaults={'first_name': 'Test', 'last_name': 'User'}
        )
        
        org, _ = Organization.objects.get_or_create(
            name="Test Organization",
            defaults={'description': 'Test organization'}
        )
        
        # Login the user
        client.force_login(user)
        
        # Test data matching frontend request
        test_data = {
            'product_image_url': 'https://example.com/fabric.jpg',
            'fabric_type': 'silk saree',
            'festival': 'deepavali',
            'price_range': '₹2999',
            'style': 'elegant',
            'custom_text': 'Special Diwali Collection',
            'offer_details': '30% Off on all items'
        }
        
        print(f"📝 Test Data: {test_data}")
        
        # Make request to the frontend API endpoint
        response = client.post(
            '/api/ai/textile/poster/generate_poster/',
            data=json.dumps(test_data),
            content_type='application/json',
            HTTP_X_DEV_USER_ID=str(user.id),
            HTTP_X_DEV_ORG_ID=str(org.id)
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API endpoint successful!")
            print(f"🖼️  Poster URL: {data.get('poster_url', 'N/A')}")
            print(f"📊 Service: {data.get('service', 'N/A')}")
            print(f"⏱️  Processing Time: {data.get('metadata', {}).get('processing_time', 'N/A')}s")
            print(f"🆔 Unique ID: {data.get('metadata', {}).get('unique_id', 'N/A')}")
            print(f"🎨 Caption Suggestions: {len(data.get('caption_suggestions', []))}")
            
            # Check if it's using Gemini 2.5 Flash
            service = data.get('service', '')
            if 'gemini' in service.lower():
                print("🎉 SUCCESS: Using Gemini 2.5 Flash!")
                return True
            else:
                print(f"⚠️  Using service: {service} (not Gemini)")
                return False
        else:
            print(f"❌ API endpoint failed with status {response.status_code}")
            print(f"Response: {response.content}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API endpoint: {str(e)}")
        return False


def test_direct_poster_generator():
    """Test the poster generator directly"""
    print("\n🧪 Testing Poster Generator Directly...")
    
    try:
        from ai_services.poster_generator import TextilePosterGenerator
        from organizations.models import Organization
        from users.models import User
        
        # Create test data
        user, _ = User.objects.get_or_create(
            email="test@example.com",
            defaults={'first_name': 'Test', 'last_name': 'User'}
        )
        
        org, _ = Organization.objects.get_or_create(
            name="Test Organization",
            defaults={'description': 'Test organization'}
        )
        
        # Test poster generator
        poster_generator = TextilePosterGenerator()
        
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
            print("✅ Poster generator successful!")
            print(f"🖼️  Poster URL: {result.get('poster_url', 'N/A')}")
            print(f"📊 Service: {result.get('service', 'N/A')}")
            print(f"⏱️  Processing Time: {result.get('processing_time', 'N/A')}s")
            print(f"🆔 Request ID: {result.get('request_id', 'N/A')}")
            
            # Check if it's using Gemini 2.5 Flash
            service = result.get('service', '')
            if 'gemini' in service.lower():
                print("🎉 SUCCESS: Using Gemini 2.5 Flash!")
                return True
            else:
                print(f"⚠️  Using service: {service} (not Gemini)")
                return False
        else:
            print(f"❌ Poster generator failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing poster generator: {str(e)}")
        return False


def run_frontend_api_test():
    """Run comprehensive frontend API test"""
    print("🚀 Starting Frontend API Test")
    print("=" * 50)
    
    tests = [
        ("Direct Poster Generator", test_direct_poster_generator),
        ("Frontend API Endpoint", test_frontend_api_endpoint),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*15} {test_name} {'='*15}")
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
    print("\n" + "="*50)
    print("📊 FRONTEND API TEST SUMMARY")
    print("="*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\n📈 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Frontend API is using Gemini 2.5 Flash!")
        print("\n🚀 Your site is NO LONGER in fallback mode!")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total


if __name__ == "__main__":
    success = run_frontend_api_test()
    sys.exit(0 if success else 1)
