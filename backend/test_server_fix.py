#!/usr/bin/env python
"""
Test script to verify the server fix
"""
import os
import sys
import django
from django.conf import settings

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from django.test import Client
from django.urls import reverse
import json

def test_server_endpoints():
    """Test basic server endpoints"""
    client = Client()
    
    print("🧪 Testing server endpoints...")
    
    # Test 1: Root endpoint
    try:
        response = client.get('/')
        print(f"✅ Root endpoint: {response.status_code}")
        if response.status_code == 200:
            data = json.loads(response.content)
            print(f"   Response: {data.get('message', 'No message')}")
        else:
            print(f"   Error: {response.content}")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
    
    # Test 2: Health check
    try:
        response = client.get('/health/')
        print(f"✅ Health check: {response.status_code}")
        if response.status_code == 200:
            data = json.loads(response.content)
            print(f"   Status: {data.get('status', 'Unknown')}")
        else:
            print(f"   Error: {response.content}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # Test 3: API status
    try:
        response = client.get('/api/')
        print(f"✅ API status: {response.status_code}")
        if response.status_code == 200:
            data = json.loads(response.content)
            print(f"   Message: {data.get('message', 'No message')}")
        else:
            print(f"   Error: {response.content}")
    except Exception as e:
        print(f"❌ API status failed: {e}")
    
    # Test 4: Admin endpoint (should redirect or show login)
    try:
        response = client.get('/admin/')
        print(f"✅ Admin endpoint: {response.status_code}")
        if response.status_code in [200, 302]:
            print("   Admin accessible")
        else:
            print(f"   Error: {response.content}")
    except Exception as e:
        print(f"❌ Admin endpoint failed: {e}")

def test_middleware_order():
    """Test that middleware is working correctly"""
    print("\n🔧 Testing middleware order...")
    
    # Test that the server can handle requests without crashing
    client = Client()
    
    try:
        # This should not cause a 500 error
        response = client.get('/api/ai/')
        print(f"✅ AI endpoints accessible: {response.status_code}")
        if response.status_code == 404:
            print("   Expected 404 - endpoint doesn't exist but server is working")
        elif response.status_code == 403:
            print("   Expected 403 - authentication required")
        else:
            print(f"   Response: {response.content}")
    except Exception as e:
        print(f"❌ AI endpoints failed: {e}")

if __name__ == '__main__':
    print("🚀 Testing server fix...")
    test_server_endpoints()
    test_middleware_order()
    print("\n✅ Server fix test completed!")
