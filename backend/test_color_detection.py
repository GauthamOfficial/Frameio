#!/usr/bin/env python
"""
Test script for color detection in branding kit prompts
"""
import requests
import json

def test_color_detection():
    """Test color detection with various prompts"""
    base_url = "http://127.0.0.1:8000/api/ai/branding-kit"
    
    print("🧪 Testing Color Detection in Branding Kit Prompts...")
    
    test_prompts = [
        "Modern tech logo with blue and white colors",
        "Fashion brand logo using red and gold",
        "Eco-friendly logo with green and brown tones",
        "Luxury brand with purple and silver accents",
        "Kids brand with bright yellow and orange",
        "Professional logo with navy blue and gray",
        "Creative agency with #FF6B6B and #4ECDC4 colors",
        "Tech startup with rgb(59, 130, 246) and white"
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n📝 Test {i}: {prompt}")
        
        try:
            response = requests.post(f"{base_url}/test-colors/", json={"prompt": prompt}, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    detected = result['detected_colors']
                    print(f"✅ Detected colors: {detected['mentioned_colors']}")
                    print(f"✅ Hex colors: {detected['hex_colors']}")
                    print(f"✅ RGB colors: {detected['rgb_colors']}")
                    print(f"✅ Total detected: {detected['total_detected']}")
                else:
                    print(f"❌ Error: {result.get('error')}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
    
    print("\n🎯 Color Detection Test Complete!")

if __name__ == "__main__":
    test_color_detection()
