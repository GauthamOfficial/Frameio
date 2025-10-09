#!/usr/bin/env python3
"""
Simple test to verify the API endpoint is working with Gemini 2.5 Flash
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

from ai_services.gemini_2_5_flash_image_service import gemini_2_5_flash_image_service


def test_gemini_service_directly():
    """Test Gemini service directly"""
    print("🧪 Testing Gemini 2.5 Flash Service Directly...")
    
    try:
        # Test the service
        result = gemini_2_5_flash_image_service.generate_poster(
            fabric_type="silk saree",
            offer_text="Special Diwali Collection - 30% Off",
            theme="elegant",
            festival="deepavali",
            price_range="₹2999"
        )
        
        if result.get('success'):
            print("✅ Gemini service working!")
            print(f"🖼️  Image URL: {result.get('image_url', 'N/A')}")
            print(f"📊 Service: {result.get('service', 'N/A')}")
            print(f"⏱️  Processing Time: {result.get('processing_time', 'N/A')}s")
            print(f"🆔 Unique ID: {result.get('unique_id', 'N/A')}")
            return True
        else:
            print(f"❌ Gemini service failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Gemini service: {str(e)}")
        return False


def test_api_endpoint_with_requests():
    """Test API endpoint using requests library"""
    print("\n🧪 Testing API Endpoint with Requests...")
    
    try:
        # Test data
        test_data = {
            'product_image_url': 'https://example.com/fabric.jpg',
            'fabric_type': 'silk saree',
            'festival': 'deepavali',
            'price_range': '₹2999',
            'style': 'elegant',
            'custom_text': 'Special Diwali Collection',
            'offer_details': '30% Off on all items'
        }
        
        # Make request to local server
        url = 'http://localhost:8000/api/ai/textile/poster/generate_poster/'
        headers = {
            'Content-Type': 'application/json',
            'X-Dev-User-ID': '1',
            'X-Dev-Org-ID': '1'
        }
        
        print(f"📡 Making request to: {url}")
        print(f"📝 Data: {test_data}")
        
        response = requests.post(url, json=test_data, headers=headers, timeout=30)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API endpoint successful!")
            print(f"🖼️  Poster URL: {data.get('poster_url', 'N/A')}")
            print(f"📊 Service: {data.get('service', 'N/A')}")
            print(f"⏱️  Processing Time: {data.get('metadata', {}).get('processing_time', 'N/A')}s")
            print(f"🆔 Unique ID: {data.get('metadata', {}).get('unique_id', 'N/A')}")
            
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
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the Django server is running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error testing API endpoint: {str(e)}")
        return False


def run_simple_api_test():
    """Run simple API test"""
    print("🚀 Starting Simple API Test")
    print("=" * 40)
    
    tests = [
        ("Gemini Service Direct", test_gemini_service_directly),
        ("API Endpoint", test_api_endpoint_with_requests),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*10} {test_name} {'='*10}")
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
    print("\n" + "="*40)
    print("📊 SIMPLE API TEST SUMMARY")
    print("="*40)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\n📈 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your site is using Gemini 2.5 Flash!")
        print("\n🚀 NO MORE FALLBACK MODE!")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total


if __name__ == "__main__":
    success = run_simple_api_test()
    sys.exit(0 if success else 1)
