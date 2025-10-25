#!/usr/bin/env python3
"""
Test Gemini connection directly
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
    
    # Test simple generation
    print("Testing simple text generation...")
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=["Hello, how are you?"],
        config=types.GenerateContentConfig(
            response_modalities=['TEXT'],
            temperature=0.7,
            max_output_tokens=1000  # Increased token limit
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
            text = ""
            for part in candidate.content.parts:
                print(f"Part: {part}")
                if hasattr(part, 'text') and part.text:
                    text += part.text
            print(f"✅ Response received: {text[:100]}...")
        else:
            print("❌ No content in response")
    else:
        print("❌ No candidates in response")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
