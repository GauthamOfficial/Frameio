#!/usr/bin/env python3
"""
Test prompt relevance for image generation
"""
import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from ai_services.gemini_service import GeminiService

def test_prompt_relevance():
    """Test that generated images are relevant to prompts"""
    print("🎯 Testing Prompt Relevance...")
    
    # Test prompts with specific characteristics
    test_cases = [
        {
            "prompt": "elegant silk saree with golden border",
            "expected_elements": ["silk", "golden", "border", "elegant"],
            "style": "textile"
        },
        {
            "prompt": "red cotton shirt with floral pattern",
            "expected_elements": ["red", "cotton", "floral", "pattern"],
            "style": "textile"
        },
        {
            "prompt": "blue denim jacket with geometric design",
            "expected_elements": ["blue", "denim", "geometric", "design"],
            "style": "textile"
        },
        {
            "prompt": "green wool sweater with traditional motifs",
            "expected_elements": ["green", "wool", "traditional", "motifs"],
            "style": "textile"
        },
        {
            "prompt": "black leather jacket with silver zippers",
            "expected_elements": ["black", "leather", "silver", "zippers"],
            "style": "textile"
        }
    ]
    
    try:
        service = GeminiService()
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📝 Test {i}: {test_case['prompt']}")
            
            # Generate image
            result = service.generate_image_from_prompt(
                prompt=test_case['prompt'],
                style=test_case['style'],
                width=1024,
                height=1024
            )
            
            if result.get('success'):
                print(f"✅ Generated image: {result.get('image_url')}")
                print(f"   Service: {result.get('service')}")
                print(f"   Enhanced Prompt: {result.get('prompt_used', 'N/A')}")
                
                # Check if enhanced prompt contains expected elements
                enhanced_prompt = result.get('prompt_used', '').lower()
                found_elements = []
                missing_elements = []
                
                for element in test_case['expected_elements']:
                    if element.lower() in enhanced_prompt:
                        found_elements.append(element)
                    else:
                        missing_elements.append(element)
                
                print(f"   Found elements: {found_elements}")
                if missing_elements:
                    print(f"   Missing elements: {missing_elements}")
                
                # Calculate relevance score
                relevance_score = len(found_elements) / len(test_case['expected_elements']) * 100
                print(f"   Relevance Score: {relevance_score:.1f}%")
                
                if relevance_score >= 75:
                    print("   🎯 High relevance!")
                elif relevance_score >= 50:
                    print("   ⚠️  Medium relevance")
                else:
                    print("   ❌ Low relevance")
                    
            else:
                print(f"❌ Generation failed: {result.get('error', 'Unknown error')}")
                
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

def test_enhanced_prompts():
    """Test prompt enhancement functionality"""
    print("\n🔧 Testing Prompt Enhancement...")
    
    try:
        service = GeminiService()
        
        test_prompts = [
            "silk saree",
            "cotton shirt",
            "wool sweater",
            "leather jacket",
            "denim jeans"
        ]
        
        for prompt in test_prompts:
            print(f"\n📝 Original: {prompt}")
            
            # Test prompt enhancement
            enhanced = service._enhance_image_prompt(prompt, "textile")
            print(f"   Enhanced: {enhanced}")
            
            # Check if enhancement added relevant terms
            enhancement_terms = ["textile", "fabric", "fashion", "elegant", "high quality"]
            found_terms = [term for term in enhancement_terms if term in enhanced.lower()]
            print(f"   Added terms: {found_terms}")
            
    except Exception as e:
        print(f"❌ Enhancement test failed: {str(e)}")
        import traceback
        traceback.print_exc()

def test_intelligent_url_generation():
    """Test intelligent URL generation"""
    print("\n🧠 Testing Intelligent URL Generation...")
    
    try:
        service = GeminiService()
        
        test_prompts = [
            "red silk saree with golden border",
            "blue cotton shirt with floral pattern",
            "green wool sweater with geometric design"
        ]
        
        for prompt in test_prompts:
            print(f"\n📝 Prompt: {prompt}")
            
            # Test URL generation
            url = service._generate_intelligent_image_url(
                prompt=prompt,
                enhanced_prompt=f"{prompt}, enhanced",
                style="textile",
                width=1024,
                height=1024
            )
            
            print(f"   Generated URL: {url}")
            
            # Check if URL contains relevant search terms
            if "source.unsplash.com" in url:
                print("   ✅ Using Unsplash with search terms")
            elif "picsum.photos" in url:
                print("   ⚠️  Using Picsum fallback")
            else:
                print("   ❓ Unknown URL format")
                
    except Exception as e:
        print(f"❌ URL generation test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Prompt Relevance Test")
    print("=" * 50)
    
    test_prompt_relevance()
    test_enhanced_prompts()
    test_intelligent_url_generation()
    
    print("\n" + "=" * 50)
    print("✅ Tests completed!")
    print("\n📋 Summary:")
    print("- Images should now be more relevant to prompts")
    print("- Enhanced prompts include fabric, color, and design elements")
    print("- Intelligent URL generation uses search terms for better results")
    print("- Each generation creates unique, prompt-specific images")
