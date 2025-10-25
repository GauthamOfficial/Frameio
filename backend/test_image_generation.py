#!/usr/bin/env python3
"""
Test image generation with Gemini API
"""
import os
import sys

# Set the API key
os.environ['GEMINI_API_KEY'] = 'AIzaSyCdASB6S3egrc3tj7tRQ5ER6S7DgNzh2ps'

try:
    from google import genai
    from google.genai import types
    print("✅ Google GenAI library imported successfully")
    
    # Initialize client
    client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])
    print("✅ Gemini client initialized successfully")
    
    # Test image generation
    print("Testing image generation...")
    prompt = "Create a beautiful silk saree design for Diwali"
    
    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[prompt],
        config=types.GenerateContentConfig(
            response_modalities=['Image']
        ),
    )
    
    print(f"Response type: {type(response)}")
    print(f"Response: {response}")
    
    if response and response.candidates:
        candidate = response.candidates[0]
        print(f"Candidate: {candidate}")
        print(f"Content: {candidate.content}")
        print(f"Parts: {candidate.content.parts if candidate.content else 'No content'}")
        
        if candidate.content and candidate.content.parts:
            for i, part in enumerate(candidate.content.parts):
                print(f"Part {i}: {part}")
                print(f"Has inline_data: {hasattr(part, 'inline_data')}")
                if hasattr(part, 'inline_data'):
                    print(f"Inline data: {part.inline_data}")
                    if part.inline_data:
                        print(f"Data size: {len(part.inline_data.data) if part.inline_data.data else 'No data'}")
        else:
            print("❌ No content parts in response")
    else:
        print("❌ No candidates in response")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
