#!/usr/bin/env python3
"""
Debug script to check the actual Gemini response structure
"""
import os
import sys

# Set the API key
os.environ['GEMINI_API_KEY'] = 'AIzaSyCdASB6S3egrc3tj7tRQ5ER6S7DgNzh2ps'

# Add the current directory to Python path
sys.path.append('.')

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')

import django
django.setup()

from google import genai
from google.genai import types

def test_gemini_response():
    print("Testing Gemini response structure...")
    
    try:
        client = genai.Client(api_key='AIzaSyCdASB6S3egrc3tj7tRQ5ER6S7DgNzh2ps')
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=["Create a simple test caption for a textile product"],
            config=types.GenerateContentConfig(
                response_modalities=['TEXT'],
                temperature=0.7,
                max_output_tokens=200
            ),
        )
        
        print(f"Response type: {type(response)}")
        print(f"Response: {response}")
        print(f"Response candidates: {response.candidates}")
        
        if response.candidates:
            candidate = response.candidates[0]
            print(f"Candidate: {candidate}")
            print(f"Candidate content: {candidate.content}")
            
            if candidate.content:
                print(f"Content parts: {candidate.content.parts}")
                
                for i, part in enumerate(candidate.content.parts):
                    print(f"Part {i}: {part}")
                    print(f"Part {i} type: {type(part)}")
                    print(f"Part {i} attributes: {dir(part)}")
                    
                    if hasattr(part, 'text'):
                        print(f"Part {i} text: {part.text}")
                    else:
                        print(f"Part {i} has no text attribute")
                        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gemini_response()
