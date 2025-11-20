#!/usr/bin/env python3
"""
Quick test to verify the GEMINI_API_KEY is working
Run: python test_api_key.py
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path('.env')
if env_path.exists():
    load_dotenv(env_path)
    print("✅ Loaded .env file")
else:
    print("⚠️  .env file not found in current directory")

# Get API key
api_key = os.getenv('GEMINI_API_KEY')

print("\n=== API Key Check ===")
if api_key:
    print(f"✅ API Key found")
    print(f"   Length: {len(api_key)} characters")
    print(f"   Starts with: {api_key[:10]}...")
    print(f"   Ends with: ...{api_key[-5:]}")
else:
    print("❌ API Key NOT FOUND")
    print("   Please check your .env file")
    sys.exit(1)

# Test the API key
print("\n=== Testing API Key ===")
try:
    from google import genai
    from google.genai import types
    
    print("✅ google-genai library is installed")
    
    # Create client
    client = genai.Client(api_key=api_key)
    print("✅ Gemini client created")
    
    # Test a simple API call
    print("🔄 Testing API call...")
    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=["A simple red circle"],
        config=types.GenerateContentConfig(
            response_modalities=['Image'],
            image_config=types.ImageConfig(aspect_ratio="1:1"),
        ),
    )
    
    if response.candidates and len(response.candidates) > 0:
        print("✅ API Key is VALID and working!")
        print("   The key can successfully generate images")
        return_code = 0
    else:
        print("❌ API call returned no candidates")
        return_code = 1
        
except ImportError:
    print("❌ google-genai library not installed")
    print("   Install with: pip install google-genai")
    return_code = 1
except Exception as e:
    error_msg = str(e)
    print(f"❌ API Key test FAILED: {error_msg}")
    
    if 'expired' in error_msg.lower() or 'invalid' in error_msg.lower():
        print("\n💡 The API key appears to be expired or invalid.")
        print("   Please:")
        print("   1. Go to https://aistudio.google.com/app/apikey")
        print("   2. Create a new API key or renew the existing one")
        print("   3. Update GEMINI_API_KEY in backend/.env")
        print("   4. Restart the backend server")
    elif 'api key' in error_msg.lower():
        print("\n💡 There's an issue with the API key.")
        print("   Please check:")
        print("   1. The key is correct in backend/.env")
        print("   2. The backend server has been restarted")
        print("   3. The key has proper permissions in Google AI Studio")
    
    return_code = 1

sys.exit(return_code)







