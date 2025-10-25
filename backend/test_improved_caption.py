#!/usr/bin/env python3
"""
Test Improved Caption Generation with Specific Prompts
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

def test_improved_caption_generation():
    """Test improved caption generation with specific prompts"""
    print("Testing Improved Caption Generation...")
    
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
    
    # Test with specific textile prompts
    test_cases = [
        {
            "prompt": "Beautiful silk saree for Diwali",
            "expected_keywords": ["silk", "saree", "diwali", "traditional", "elegant"]
        },
        {
            "prompt": "Elegant cotton kurta for summer office wear",
            "expected_keywords": ["cotton", "kurta", "summer", "office", "professional"]
        },
        {
            "prompt": "Traditional handwoven wool shawl for winter",
            "expected_keywords": ["wool", "shawl", "winter", "handwoven", "warm"]
        },
        {
            "prompt": "Embroidered party dress for wedding celebration",
            "expected_keywords": ["embroidered", "party", "wedding", "celebration", "dress"]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        prompt = test_case["prompt"]
        expected_keywords = test_case["expected_keywords"]
        
        print(f"\n--- Test {i}: {prompt} ---")
        print(f"Expected keywords: {expected_keywords}")
        
        try:
            # Create enhanced prompt for caption generation
            enhanced_content = f"""
            Create an engaging social media caption for a beautiful textile/fashion poster based on this specific description: "{prompt}"
            
            Analyze the prompt and create a caption that:
            - Captures the essence and details mentioned in the original prompt
            - Highlights the specific features, colors, materials, or style mentioned
            - Creates emotional connection with the target audience
            - Mentions the occasion, season, or purpose if specified in the prompt
            - Emphasizes the unique selling points from the original description
            - Uses relevant keywords from the prompt naturally
            - Creates desire and interest based on the specific product described
            - Be conversational and relatable to the intended use case
            - Include relevant fashion/beauty keywords that match the prompt
            - Focus on the visual appeal and craftsmanship mentioned
            - Highlight the elegance and style specific to the prompt
            - Create a sense of aspiration based on the original description
            - Include a compelling call-to-action relevant to the product type
            
            Format the response as JSON with these fields:
            - main_text: The main caption (2-3 sentences)
            - full_caption: The detailed caption (4-5 sentences)
            - hashtags: Array of relevant hashtags
            - call_to_action: Call to action text
            - emoji: Relevant emojis
            """
            
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[enhanced_content],
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=1000
                )
            )
            
            if response.candidates and len(response.candidates) > 0:
                content = response.candidates[0].content.parts[0].text
                print("✅ Caption generated successfully!")
                
                # Check if expected keywords are present in the response
                content_lower = content.lower()
                found_keywords = [kw for kw in expected_keywords if kw.lower() in content_lower]
                print(f"✅ Found keywords: {found_keywords}")
                
                if len(found_keywords) >= len(expected_keywords) * 0.6:  # At least 60% of keywords found
                    print("✅ Caption is relevant to the prompt!")
                else:
                    print("⚠️ Caption may not be fully relevant to the prompt")
                
                print(f"Response preview: {content[:300]}...")
            else:
                print("❌ No response from Gemini")
                
        except Exception as e:
            print(f"❌ Error generating caption: {str(e)}")
    
    return True

if __name__ == "__main__":
    test_improved_caption_generation()
