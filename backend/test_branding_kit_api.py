#!/usr/bin/env python
"""
Test script for Branding Kit API endpoints
"""
import requests
import json
import time

def test_branding_kit_api():
    """Test the branding kit API endpoints"""
    base_url = "http://127.0.0.1:8000/api/ai/branding-kit"
    
    print("🧪 Testing Branding Kit API Endpoints...")
    
    # Test service status
    print("\n📡 Testing service status...")
    try:
        response = requests.get(f"{base_url}/status/", timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Service status: {result.get('message')}")
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Status check error: {e}")
        return False
    
    # Test logo generation
    print("\n🎨 Testing logo generation...")
    try:
        data = {
            "prompt": "Modern tech startup logo with clean lines",
            "style": "modern"
        }
        response = requests.post(f"{base_url}/logo/", json=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Logo generation successful")
                logo_data = result['data']['logo']
                print(f"   Format: {logo_data['format']}")
                print(f"   Size: {logo_data['width']}x{logo_data['height']}")
            else:
                print(f"❌ Logo generation failed: {result.get('error')}")
                return False
        else:
            print(f"❌ Logo generation request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Logo generation error: {e}")
        return False
    
    # Test color palette generation
    print("\n🎨 Testing color palette generation...")
    try:
        data = {
            "prompt": "Modern tech startup",
            "num_colors": 5
        }
        response = requests.post(f"{base_url}/colors/", json=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Color palette generation successful")
                palette_data = result['data']['palette']
                print(f"   Format: {palette_data['format']}")
                print(f"   Size: {palette_data['width']}x{palette_data['height']}")
            else:
                print(f"❌ Color palette generation failed: {result.get('error')}")
                return False
        else:
            print(f"❌ Color palette generation request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Color palette generation error: {e}")
        return False
    
    # Test complete branding kit generation
    print("\n🎨 Testing complete branding kit generation...")
    try:
        data = {
            "prompt": "Modern tech startup with clean aesthetic",
            "style": "modern"
        }
        response = requests.post(f"{base_url}/generate/", json=data, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Complete branding kit generation successful")
                branding_kit = result['data']['branding_kit']
                print(f"   Logo: {branding_kit['logo']['format']} ({branding_kit['logo']['width']}x{branding_kit['logo']['height']})")
                print(f"   Palette: {branding_kit['color_palette']['format']} ({branding_kit['color_palette']['width']}x{branding_kit['color_palette']['height']})")
            else:
                print(f"❌ Complete branding kit generation failed: {result.get('error')}")
                return False
        else:
            print(f"❌ Complete branding kit generation request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Complete branding kit generation error: {e}")
        return False
    
    print("\n🎉 All API tests passed! Branding Kit API is working correctly.")
    return True

if __name__ == "__main__":
    success = test_branding_kit_api()
    exit(0 if success else 1)
