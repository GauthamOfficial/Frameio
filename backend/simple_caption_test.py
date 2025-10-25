#!/usr/bin/env python3
"""
Simple test for AI Caption Generation without Django
"""
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Set up environment variables
os.environ.setdefault('GEMINI_API_KEY', 'AIzaSyCdASB6S3egrc3tj7tRQ5ER6S7DgNzh2ps')

try:
    from google import genai
    from google.genai import types
    print("✅ Google GenAI imported successfully")
except ImportError as e:
    print(f"❌ Failed to import Google GenAI: {e}")
    sys.exit(1)

def test_gemini_connection():
    """Test basic Gemini connection and caption generation"""
    print("Testing Gemini API connection...")
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found")
        return False
    
    try:
        client = genai.Client(api_key=api_key)
        print("✅ Gemini client initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Gemini client: {e}")
        return False
    
    # Test caption generation
    test_prompts = [
        "Beautiful silk saree for Diwali",
        "Elegant cotton kurta for summer",
        "Traditional handwoven shawl"
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n--- Test {i}: {prompt} ---")
        
        try:
            # Create a detailed prompt for caption generation
            caption_prompt = f"""
            Generate an engaging social media caption for a textile product based on this description: "{prompt}"
            
            Please provide:
            1. A main caption (2-3 sentences, engaging and descriptive)
            2. A full caption (more detailed, 4-5 sentences)
            3. Relevant hashtags (5-10 hashtags)
            4. A call to action
            5. Appropriate emojis
            
            Format the response as JSON with these fields:
            - main_text: The main caption
            - full_caption: The detailed caption
            - hashtags: Array of hashtags
            - call_to_action: Call to action text
            - emoji: Relevant emojis
            """
            
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[caption_prompt],
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=1000
                )
            )
            
            if response.candidates and len(response.candidates) > 0:
                content = response.candidates[0].content.parts[0].text
                print("✅ Caption generated successfully!")
                print(f"Response: {content[:200]}...")
            else:
                print("❌ No response from Gemini")
                
        except Exception as e:
            print(f"❌ Error generating caption: {str(e)}")
    
    return True

if __name__ == "__main__":
    test_gemini_connection()
