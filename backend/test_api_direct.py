#!/usr/bin/env python
"""
Test the API endpoint directly
"""
import requests
import json

def test_api():
    url = 'http://127.0.0.1:8000/api/ai/ai-poster/generate_poster/'
    data = {
        'prompt': 'Create a simple blue square',
        'aspect_ratio': '1:1'
    }
    
    try:
        print("📡 Testing API endpoint...")
        response = requests.post(url, json=data, timeout=60)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API Success!")
            print(f"Success: {result.get('success')}")
            print(f"Message: {result.get('message')}")
            print(f"Image URL: {result.get('image_url')}")
        else:
            print(f"❌ API Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    test_api()
