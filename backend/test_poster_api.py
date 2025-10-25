#!/usr/bin/env python3
"""
Test the poster generation API to see what's being returned
"""
import requests
import json
import time

def test_poster_api():
    url = "http://localhost:8000/api/ai/ai-poster/generate_poster/"
    
    payload = {
        "prompt": "Beautiful silk saree for Diwali",
        "aspect_ratio": "4:5"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print("Testing poster generation API...")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        print("Sending request...")
        response = requests.post(url, json=payload, headers=headers, timeout=300)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API Response received!")
            print(f"Success: {data.get('success')}")
            print(f"Image URL: {data.get('image_url')}")
            print(f"Caption: {data.get('caption', 'NOT_FOUND')}")
            print(f"Full Caption: {data.get('full_caption', 'NOT_FOUND')}")
            print(f"Hashtags: {data.get('hashtags', 'NOT_FOUND')}")
            print(f"Emoji: {data.get('emoji', 'NOT_FOUND')}")
            print(f"Call to Action: {data.get('call_to_action', 'NOT_FOUND')}")
            
            if data.get('caption') or data.get('full_caption'):
                print("✅ Caption data is present!")
            else:
                print("❌ No caption data found!")
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_poster_api()
