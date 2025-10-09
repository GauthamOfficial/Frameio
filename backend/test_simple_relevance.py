#!/usr/bin/env python3
"""
Simple test for prompt relevance
"""
import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

def test_simple_relevance():
    """Test simple prompt relevance"""
    print("🎯 Testing Simple Prompt Relevance...")
    
    try:
        from ai_services.gemini_service import GeminiService
        
        service = GeminiService()
        
        # Test a specific prompt
        prompt = "elegant silk saree with golden border"
        print(f"📝 Testing: {prompt}")
        
        result = service.generate_image_from_prompt(
            prompt=prompt,
            style="textile",
            width=1024,
            height=1024
        )
        
        if result.get('success'):
            print(f"✅ Generated image: {result.get('image_url')}")
            print(f"   Service: {result.get('service')}")
            print(f"   Enhanced Prompt: {result.get('prompt_used', 'N/A')}")
            
            # Check if the enhanced prompt contains relevant terms
            enhanced = result.get('prompt_used', '').lower()
            relevant_terms = ['silk', 'golden', 'border', 'elegant', 'textile', 'fabric']
            found_terms = [term for term in relevant_terms if term in enhanced]
            
            print(f"   Found relevant terms: {found_terms}")
            print(f"   Relevance: {len(found_terms)}/{len(relevant_terms)} terms")
            
        else:
            print(f"❌ Generation failed: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_relevance()
