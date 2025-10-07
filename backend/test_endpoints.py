#!/usr/bin/env python
"""
Test script to verify endpoints are accessible
"""
import requests
import json

def test_endpoints():
    """Test all Phase 1 Week 3 endpoints"""
    base_url = "http://localhost:8000"
    
    print("🔍 Testing Phase 1 Week 3 Endpoints...")
    print("=" * 50)
    
    # Test basic API status
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ API Status: Server is running")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ API Status: Server returned {response.status_code}")
    except Exception as e:
        print(f"❌ API Status: Cannot connect to server - {e}")
        return
    
    # Test health check
    try:
        response = requests.get(f"{base_url}/health/")
        if response.status_code == 200:
            print("✅ Health Check: Server is healthy")
        else:
            print(f"❌ Health Check: Server returned {response.status_code}")
    except Exception as e:
        print(f"❌ Health Check: Error - {e}")
    
    # Test AI services endpoints
    ai_endpoints = [
        "/api/ai/providers/",
        "/api/ai/generation-requests/",
        "/api/ai/quotas/",
        "/api/ai/templates/",
        "/api/ai/analytics/",
    ]
    
    print("\n🔧 Testing AI Services Endpoints...")
    for endpoint in ai_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            print(f"   {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"   {endpoint}: Error - {e}")
    
    # Test textile endpoints
    print("\n🎨 Testing Textile Endpoints...")
    textile_endpoints = [
        "/api/ai/textile/poster/generate_poster/",
        "/api/ai/textile/caption/generate_caption/",
    ]
    
    for endpoint in textile_endpoints:
        try:
            # Test with OPTIONS to check if endpoint exists
            response = requests.options(f"{base_url}{endpoint}")
            print(f"   {endpoint}: {response.status_code} (OPTIONS)")
        except Exception as e:
            print(f"   {endpoint}: Error - {e}")
    
    # Test scheduling endpoints
    print("\n📅 Testing Scheduling Endpoints...")
    schedule_endpoints = [
        "/api/ai/schedule/",
        "/api/ai/schedule/analytics/",
    ]
    
    for endpoint in schedule_endpoints:
        try:
            response = requests.options(f"{base_url}{endpoint}")
            print(f"   {endpoint}: {response.status_code} (OPTIONS)")
        except Exception as e:
            print(f"   {endpoint}: Error - {e}")
    
    print("\n" + "=" * 50)
    print("📋 To test the endpoints with authentication:")
    print("1. Create a user account")
    print("2. Create an organization")
    print("3. Use the API with proper authentication headers")
    print("4. Include X-Organization header for multi-tenant support")

if __name__ == "__main__":
    test_endpoints()
