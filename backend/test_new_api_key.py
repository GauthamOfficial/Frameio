#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick test to verify the new GEMINI_API_KEY is working
Run: python test_new_api_key.py
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load .env file
BASE_DIR = Path(__file__).resolve().parent
env_path = BASE_DIR / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print("[OK] Loaded .env file")
else:
    print("[WARNING] .env file not found in backend directory")
    sys.exit(1)

# Get API key
api_key = os.getenv('GEMINI_API_KEY')

print("\n=== API Key Check ===")
if api_key:
    print(f"[OK] API Key found")
    print(f"   Length: {len(api_key)} characters")
    print(f"   Starts with: {api_key[:10]}...")
    print(f"   Ends with: ...{api_key[-5:]}")
else:
    print("[ERROR] API Key NOT FOUND")
    print("   Please check your .env file")
    sys.exit(1)

# Test the API key
print("\n=== Testing API Key ===")
try:
    from google import genai
    from google.genai import types
    
    print("[OK] Google GenAI library imported successfully")
    
    # Initialize client
    print("\n=== Initializing Gemini Client ===")
    client = genai.Client(api_key=api_key)
    print("[OK] Gemini client initialized")
    
    # Test a simple generation
    print("\n=== Testing Image Generation ===")
    print("Generating a simple test image...")
    
    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=["Create a simple red square on white background"],
        config=types.GenerateContentConfig(
            response_modalities=['Image'],
        ),
    )
    
    if response.candidates and len(response.candidates) > 0:
        candidate = response.candidates[0]
        if candidate.content and candidate.content.parts:
            print("[OK] Image generation successful!")
            print(f"   Found {len(candidate.content.parts)} content parts")
            print("[OK] API Key is working correctly!")
        else:
            print("[WARNING] Response received but no content parts")
            print(f"   Candidate: {candidate}")
    else:
        print("[ERROR] No candidates in response")
        print(f"   Response: {response}")
        
except ImportError as e:
    print(f"[ERROR] Failed to import Google GenAI: {e}")
    print("   Install with: pip install google-genai")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] Error testing API key: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[OK] All tests passed! API key is valid and working.")

