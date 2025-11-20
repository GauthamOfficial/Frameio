#!/usr/bin/env python
"""Quick test script to verify the backend API is accessible."""
import requests

print("Testing backend API endpoint...")
print("=" * 50)

try:
    # Test the company profiles endpoint
    url = "http://localhost:8000/api/users/company-profiles/"
    response = requests.get(url, timeout=5)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Body: {response.text[:500]}")
    
    if response.status_code == 200:
        print("\n✅ SUCCESS! Endpoint is accessible")
    else:
        print(f"\n❌ ERROR: Got {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("❌ ERROR: Could not connect to backend. Is it running?")
except Exception as e:
    print(f"❌ ERROR: {e}")



