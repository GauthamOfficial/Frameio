#!/usr/bin/env python
"""
Debug script for NanoBanana API
"""
import os
import sys
import django
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

# Set the API key
os.environ['NANOBANANA_API_KEY'] = 'AIzaSyBBP1QGjY7lJBhjNwWMSJCIOZC1bWgSzMY'

def test_requests():
    """Test if requests module works"""
    print("🧪 Testing requests module...")
    try:
        import requests
        print("✅ Requests module imported successfully")
        
        # Test a simple request
        response = requests.get('https://httpbin.org/get', timeout=10)
        print(f"✅ HTTP request successful: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Requests test failed: {str(e)}")
        return False

def test_nanobanana_api():
    """Test NanoBanana API directly"""
    print("\n🧪 Testing NanoBanana API...")
    try:
        import requests
        
        api_key = 'AIzaSyBBP1QGjY7lJBhjNwWMSJCIOZC1bWgSzMY'
        base_url = "https://api.nanobanana.ai"
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        print(f"🔑 API Key: {api_key[:10]}...")
        print(f"🌐 Base URL: {base_url}")
        
        # Test a simple request first
        print("📡 Testing API connectivity...")
        try:
            response = requests.get(f"{base_url}/", headers=headers, timeout=10)
            print(f"   - Root endpoint status: {response.status_code}")
            print(f"   - Response: {response.text[:200]}...")
        except Exception as e:
            print(f"   - Root endpoint failed: {str(e)}")
        
        # Test image style transfer (NanoBanana's actual endpoint)
        print("📸 Testing image style transfer...")
        payload = {
            "prompt": "A simple test image",
            "style": "cinematic"
        }
        
        print(f"📤 Payload: {payload}")
        
        response = requests.post(f"{base_url}/v1/images/style-transfer", json=payload, headers=headers, timeout=30)
        print(f"📥 Response status: {response.status_code}")
        print(f"📥 Response headers: {dict(response.headers)}")
        print(f"📥 Response text: {response.text[:500]}...")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API call successful!")
            print(f"   - Result keys: {list(result.keys())}")
            if 'images' in result:
                print(f"   - Images: {result['images']}")
            return True
        else:
            print(f"❌ API call failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ NanoBanana API test failed: {str(e)}")
        return False

def test_alternative_endpoints():
    """Test alternative API endpoints"""
    print("\n🧪 Testing alternative endpoints...")
    try:
        import requests
        
        api_key = 'AIzaSyBBP1QGjY7lJBhjNwWMSJCIOZC1bWgSzMY'
        
        # Try different base URLs
        base_urls = [
            "https://api.nanobananaapi.ai",
            "https://nanobananaapi.ai",
            "https://api.nanobanana.com",
            "https://nanobanana.com"
        ]
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        for base_url in base_urls:
            print(f"🌐 Testing: {base_url}")
            try:
                response = requests.get(f"{base_url}/", headers=headers, timeout=5)
                print(f"   - Status: {response.status_code}")
                if response.status_code != 404:
                    print(f"   - Response: {response.text[:100]}...")
            except Exception as e:
                print(f"   - Error: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Alternative endpoints test failed: {str(e)}")
        return False

def main():
    """Main debug function"""
    print("🔍 NanoBanana API Debug")
    print("=" * 40)
    
    tests = [
        ("Requests Module", test_requests),
        ("NanoBanana API", test_nanobanana_api),
        ("Alternative Endpoints", test_alternative_endpoints),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} passed")
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 40)
    print(f"📊 Debug Results: {passed}/{total} tests passed")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
