#!/usr/bin/env python3
"""
Diagnostic script to identify why the API key is failing
Run: python diagnose_api_key_issue.py
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path('.env')
if env_path.exists():
    load_dotenv(env_path)

api_key = os.getenv('GEMINI_API_KEY')

print("=" * 60)
print("GEMINI API KEY DIAGNOSTIC TOOL")
print("=" * 60)
print()

if not api_key:
    print("❌ API Key not found in environment")
    sys.exit(1)

print(f"✅ API Key found: {api_key[:15]}...{api_key[-5:]}")
print(f"   Length: {len(api_key)} characters")
print()

# Test different API endpoints and models
try:
    from google import genai
    from google.genai import types
    
    client = genai.Client(api_key=api_key)
    print("✅ Gemini client created successfully")
    print()
    
    # Test 1: Try to list available models
    print("Test 1: Checking available models...")
    try:
        models = client.models.list()
        print(f"   ✅ Can list models: {len(list(models))} models available")
    except Exception as e:
        print(f"   ❌ Cannot list models: {str(e)}")
    print()
    
    # Test 2: Try text generation (simpler than image)
    print("Test 2: Testing text generation (simpler API)...")
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=["Say hello"],
        )
        if response.candidates:
            print("   ✅ Text generation works!")
        else:
            print("   ⚠️  Text generation returned no candidates")
    except Exception as e:
        error_msg = str(e)
        print(f"   ❌ Text generation failed: {error_msg}")
        
        # Analyze the error
        if 'expired' in error_msg.lower():
            print()
            print("   🔍 DIAGNOSIS: API Key appears expired")
            print("   💡 Possible solutions:")
            print("      1. Ask supervisor to check key status in Google Cloud Console")
            print("      2. Verify key hasn't been revoked or disabled")
            print("      3. Check if key needs to be renewed (not replaced)")
        elif 'permission' in error_msg.lower() or 'denied' in error_msg.lower():
            print()
            print("   🔍 DIAGNOSIS: Permission issue")
            print("   💡 Possible solutions:")
            print("      1. Check API restrictions (IP, referrer) in Google Cloud Console")
            print("      2. Verify 'Generative Language API' is enabled for the project")
            print("      3. Check if key has proper IAM permissions")
        elif 'quota' in error_msg.lower() or 'limit' in error_msg.lower():
            print()
            print("   🔍 DIAGNOSIS: Quota/rate limit issue")
            print("   💡 Possible solutions:")
            print("      1. Check API quotas in Google Cloud Console")
            print("      2. Wait a few minutes and try again")
            print("      3. Verify billing is enabled for the project")
    print()
    
    # Test 3: Try image generation with different config
    print("Test 3: Testing image generation...")
    try:
        # Try with minimal config first
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=["A red circle"],
            config=types.GenerateContentConfig(
                response_modalities=['Image'],
            ),
        )
        if response.candidates and len(response.candidates) > 0:
            print("   ✅ Image generation works!")
        else:
            print("   ⚠️  Image generation returned no candidates")
    except Exception as e:
        error_msg = str(e)
        print(f"   ❌ Image generation failed: {error_msg}")
        
        # Provide specific guidance
        if 'expired' in error_msg.lower():
            print()
            print("   📋 DETAILED ERROR ANALYSIS:")
            print("      The API key is reporting as 'expired'")
            print()
            print("   🔧 FOR YOUR SUPERVISOR TO CHECK:")
            print("      1. Go to: https://console.cloud.google.com/apis/credentials")
            print("      2. Find the API key and check its status")
            print("      3. Verify 'Generative Language API' is enabled:")
            print("         https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com")
            print("      4. Check API restrictions:")
            print("         - IP address restrictions")
            print("         - HTTP referrer restrictions")
            print("         - Application restrictions")
            print("      5. Check if billing is enabled for the project")
            print("      6. Verify the key hasn't been disabled or deleted")
            print()
            print("   💡 WORKAROUND (if key works elsewhere):")
            print("      - Check if your IP address is allowed")
            print("      - Verify network/firewall settings")
            print("      - Try from a different network")
    
except ImportError:
    print("❌ google-genai library not installed")
    print("   Install with: pip install google-genai")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {str(e)}")
    sys.exit(1)

print()
print("=" * 60)
print("Diagnostic complete. Share the results with your supervisor.")
print("=" * 60)








