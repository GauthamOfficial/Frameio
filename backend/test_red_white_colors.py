#!/usr/bin/env python
"""
Test script specifically for red and white color detection
"""
import requests
import json

def test_red_white_detection():
    """Test color detection with red and white prompts"""
    base_url = "http://127.0.0.1:8000/api/ai/branding-kit"
    
    print("🧪 Testing Red and White Color Detection...")
    
    test_prompts = [
        "Create a logo with red and white colors",
        "Brand logo using red and white palette",
        "Logo design with red and white theme",
        "Professional logo with red and white branding",
        "Modern logo with red and white color scheme"
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
                    print(f"✅ Total detected: {detected['total_detected']}")
                    
                    # Check if red and white are detected
                    if 'red' in detected['mentioned_colors'] and 'white' in detected['mentioned_colors']:
                        print("🎯 SUCCESS: Both red and white detected!")
                    else:
                        print("❌ ISSUE: Red and white not properly detected")
                else:
                    print(f"❌ Error: {result.get('error')}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
    
    print("\n🎯 Red and White Color Detection Test Complete!")

if __name__ == "__main__":
    test_red_white_detection()
