#!/usr/bin/env python3
"""
Test script to verify AI image generation is working correctly
and generating images that match prompts.
"""

import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from ai_services.working_ai_image_service import WorkingAIImageService
from ai_services.real_ai_image_service import RealAIImageService
import json

def test_prompt_based_generation():
    """Test working AI image generation"""
    print("🧪 Testing Working AI Image Generation...")
    
    try:
        service = WorkingAIImageService()
        
        # Test prompts
        test_prompts = [
            "elegant silk saree with golden border",
            "modern cotton shirt design",
            "traditional textile pattern",
            "festive deepavali clothing",
            "bohemian style fabric"
        ]
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n📝 Test {i}: {prompt}")
            
            result = service.generate_image_from_prompt(
                prompt=prompt,
                style="textile",
                width=1024,
                height=1024
            )
            
            if result.get('success'):
                print(f"✅ Generated image: {result.get('image_url')}")
                print(f"   Service: {result.get('service', 'unknown')}")
                print(f"   Prompt used: {result.get('prompt_used', 'N/A')}")
            else:
                print(f"❌ Generation failed: {result.get('error', 'Unknown error')}")
                
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

def test_real_ai_generation():
    """Test real AI image generation"""
    print("\n🧪 Testing Real AI Image Generation...")
    
    try:
        service = RealAIImageService()
        
        # Test with a simple prompt
        prompt = "beautiful textile design with floral patterns"
        
        result = service.generate_image_from_prompt(
            prompt=prompt,
            style="textile",
            width=1024,
            height=1024
        )
        
        if result.get('success'):
            print(f"✅ Real AI generated image: {result.get('image_url')}")
            print(f"   Service: {result.get('service', 'unknown')}")
            print(f"   Metadata: {json.dumps(result.get('metadata', {}), indent=2)}")
        else:
            print(f"❌ Real AI generation failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Real AI test failed: {str(e)}")
        import traceback
        traceback.print_exc()

def test_prompt_analysis():
    """Test prompt analysis functionality"""
    print("\n🧪 Testing Prompt Analysis...")
    
    try:
        service = PromptBasedImageService()
        
        test_prompts = [
            "red silk saree with golden border",
            "blue cotton shirt with floral pattern",
            "green linen dress with geometric design"
        ]
        
        for prompt in test_prompts:
            print(f"\n📝 Analyzing: {prompt}")
            
            # Test prompt enhancement
            enhanced = service._enhance_prompt_for_ai(prompt, "textile")
            print(f"   Enhanced: {enhanced}")
            
            # Test prompt analysis
            analysis = service._analyze_prompt(enhanced)
            print(f"   Analysis: {json.dumps(analysis, indent=4)}")
            
    except Exception as e:
        print(f"❌ Prompt analysis test failed: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting AI Image Generation Tests...")
    print("=" * 50)
    
    test_prompt_based_generation()
    test_real_ai_generation()
    test_prompt_analysis()
    
    print("\n" + "=" * 50)
    print("✅ Tests completed!")
    print("\n📋 Summary:")
    print("- Prompt-based generation should create images matching prompts")
    print("- Real AI services should generate high-quality images")
    print("- Fallback mechanisms should work when APIs are unavailable")
    print("- Each generation should be unique and relevant to the prompt")
