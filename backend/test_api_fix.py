#!/usr/bin/env python
"""
Test script to verify the API fix
"""
import requests
import json
import os

def test_api():
    print("🧪 Testing API Fix...")
    
    # Test the API endpoint
    url = 'http://127.0.0.1:8000/api/ai/ai-poster/generate_poster/'
    data = {
        'prompt': 'Create a simple test poster with a blue background',
        'aspect_ratio': '1:1'
    }

    try:
        print("📡 Making request to API...")
        response = requests.post(url, json=data, timeout=30)
        print(f'Status Code: {response.status_code}')
        
        if response.status_code == 200:
            result = response.json()
            print('✅ API is working!')
            print(f'Success: {result.get("success")}')
            print(f'Message: {result.get("message")}')
            if result.get("image_url"):
                print(f'Image URL: {result.get("image_url")}')
            return True
        else:
            print(f'❌ API Error: {response.text}')
            return False
    except Exception as e:
        print(f'❌ Connection failed: {e}')
        return False

if __name__ == "__main__":
    test_api()
