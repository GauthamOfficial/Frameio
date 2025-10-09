"""
Test script for improved image generation service
Tests the enhanced NanoBanana integration with proper prompt engineering
"""
import os
import sys
import django
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from ai_services.improved_image_generation_service import ImprovedImageGenerationService
from ai_services.enhanced_nanobanana_service import EnhancedNanoBananaService
from ai_services.gemini_prompt_enhancer import GeminiPromptEnhancer
from django.conf import settings
import time


def test_improved_image_generation():
    """Test the improved image generation service"""
    print("🧪 Testing Improved Image Generation Service")
    print("=" * 60)
    
    # Initialize service
    service = ImprovedImageGenerationService()
    
    # Test prompts with different styles
    test_cases = [
        {
            'prompt': 'A beautiful red silk saree with golden border',
            'style': 'textile',
            'description': 'Textile fashion item'
        },
        {
            'prompt': 'Modern minimalist living room with clean lines',
            'style': 'modern',
            'description': 'Modern interior design'
        },
        {
            'prompt': 'Traditional Indian wedding decorations with vibrant colors',
            'style': 'festive',
            'description': 'Festive celebration theme'
        },
        {
            'prompt': 'Professional headshot of a businesswoman',
            'style': 'photorealistic',
            'description': 'Professional photography'
        },
        {
            'prompt': 'Abstract geometric pattern with blue and green colors',
            'style': 'artistic',
            'description': 'Abstract artistic design'
        }
    ]
    
    print(f"📊 Testing {len(test_cases)} different prompts and styles")
    print()
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"🔍 Test {i}: {test_case['description']}")
        print(f"   Prompt: {test_case['prompt']}")
        print(f"   Style: {test_case['style']}")
        
        try:
            start_time = time.time()
            
            # Generate image
            result = service.generate_image_from_prompt(
                prompt=test_case['prompt'],
                style=test_case['style'],
                width=1024,
                height=1024,
                num_images=3
            )
            
            processing_time = time.time() - start_time
            
            if result.get('success'):
                print(f"   ✅ Success: Generated {len(result.get('image_urls', []))} images")
                print(f"   🕒 Processing time: {processing_time:.2f}s")
                print(f"   🔧 Service used: {result.get('service', 'unknown')}")
                print(f"   📝 Enhanced prompt: {result.get('prompt_used', 'N/A')[:100]}...")
                
                # Show first image URL
                if result.get('image_urls'):
                    print(f"   🖼️  First image: {result['image_urls'][0][:80]}...")
                
                results.append({
                    'test': i,
                    'success': True,
                    'images': len(result.get('image_urls', [])),
                    'time': processing_time,
                    'service': result.get('service'),
                    'prompt_enhanced': len(result.get('prompt_used', '')) > len(test_case['prompt'])
                })
            else:
                print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
                results.append({
                    'test': i,
                    'success': False,
                    'error': result.get('error')
                })
                
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
            results.append({
                'test': i,
                'success': False,
                'error': str(e)
            })
        
        print()
    
    # Summary
    print("📈 Test Results Summary")
    print("=" * 60)
    
    successful_tests = [r for r in results if r.get('success')]
    failed_tests = [r for r in results if not r.get('success')]
    
    print(f"✅ Successful tests: {len(successful_tests)}/{len(results)}")
    print(f"❌ Failed tests: {len(failed_tests)}/{len(results)}")
    
    if successful_tests:
        avg_time = sum(r.get('time', 0) for r in successful_tests) / len(successful_tests)
        avg_images = sum(r.get('images', 0) for r in successful_tests) / len(successful_tests)
        enhanced_prompts = sum(1 for r in successful_tests if r.get('prompt_enhanced'))
        
        print(f"⏱️  Average processing time: {avg_time:.2f}s")
        print(f"🖼️  Average images generated: {avg_images:.1f}")
        print(f"🔧 Prompt enhancement rate: {enhanced_prompts}/{len(successful_tests)}")
        
        # Service usage breakdown
        services = {}
        for result in successful_tests:
            service = result.get('service', 'unknown')
            services[service] = services.get(service, 0) + 1
        
        print(f"🔧 Service usage:")
        for service, count in services.items():
            print(f"   {service}: {count} tests")
    
    if failed_tests:
        print(f"\n❌ Failed tests:")
        for result in failed_tests:
            print(f"   Test {result['test']}: {result.get('error', 'Unknown error')}")
    
    return len(successful_tests) == len(results)


def test_gemini_integration():
    """Test Gemini prompt enhancement"""
    print("\n🧠 Testing Gemini Integration")
    print("=" * 60)
    
    enhancer = GeminiPromptEnhancer()
    
    if not enhancer.is_available():
        print("❌ Gemini not available - check API key configuration")
        return False
    
    test_prompts = [
        "red dress",
        "modern kitchen",
        "textile pattern",
        "business meeting"
    ]
    
    for prompt in test_prompts:
        print(f"📝 Original: {prompt}")
        
        try:
            enhanced = enhancer.enhance_prompt_for_image_generation(prompt, "photorealistic")
            print(f"🔧 Enhanced: {enhanced[:100]}...")
            print(f"📏 Length: {len(enhanced)} characters")
            print()
        except Exception as e:
            print(f"❌ Enhancement failed: {str(e)}")
            print()
    
    return True


def test_nanobanana_service():
    """Test NanoBanana service specifically"""
    print("\n🍌 Testing NanoBanana Service")
    print("=" * 60)
    
    service = EnhancedNanoBananaService()
    
    print(f"🔑 API Key configured: {'Yes' if service.api_key else 'No'}")
    print(f"🌐 Service available: {'Yes' if service.is_available() else 'No'}")
    print(f"🔄 Using fallback: {'Yes' if service.use_fallback else 'No'}")
    
    if service.api_key:
        print(f"🔑 API Key: {service.api_key[:10]}...")
    else:
        print("🔑 API Key: Not configured")
    
    # Test prompt enhancement
    test_prompt = "A beautiful textile design with floral patterns"
    enhanced = service._enhance_prompt_locally(test_prompt, "textile")
    
    print(f"\n📝 Original prompt: {test_prompt}")
    print(f"🔧 Enhanced prompt: {enhanced[:100]}...")
    print(f"📏 Enhancement length: {len(enhanced)} characters")
    
    return True


def test_api_configuration():
    """Test API key configuration"""
    print("\n🔧 Testing API Configuration")
    print("=" * 60)
    
    api_keys = {
        'NANOBANANA_API_KEY': getattr(settings, 'NANOBANANA_API_KEY', None),
        'GEMINI_API_KEY': getattr(settings, 'GEMINI_API_KEY', None),
        'GOOGLE_API_KEY': getattr(settings, 'GOOGLE_API_KEY', None),
        'STABILITY_API_KEY': getattr(settings, 'STABILITY_API_KEY', None),
        'OPENAI_API_KEY': getattr(settings, 'OPENAI_API_KEY', None),
    }
    
    configured_keys = 0
    total_keys = len(api_keys)
    
    for key_name, key_value in api_keys.items():
        if key_value and key_value.strip():
            print(f"✅ {key_name}: Configured")
            configured_keys += 1
        else:
            print(f"❌ {key_name}: Not configured")
    
    print(f"\n📊 Configuration status: {configured_keys}/{total_keys} keys configured")
    
    if configured_keys == 0:
        print("⚠️  No API keys configured - service will use fallback mode")
    elif configured_keys < 3:
        print("⚠️  Limited API keys - some services may not be available")
    else:
        print("✅ Good API key configuration")
    
    return configured_keys > 0


def main():
    """Run all tests"""
    print("🚀 Improved Image Generation Service Test Suite")
    print("=" * 80)
    
    # Test API configuration
    config_ok = test_api_configuration()
    
    # Test NanoBanana service
    nanobanana_ok = test_nanobanana_service()
    
    # Test Gemini integration
    gemini_ok = test_gemini_integration()
    
    # Test improved image generation
    generation_ok = test_improved_image_generation()
    
    # Final summary
    print("\n🎯 Final Test Results")
    print("=" * 80)
    
    tests = [
        ("API Configuration", config_ok),
        ("NanoBanana Service", nanobanana_ok),
        ("Gemini Integration", gemini_ok),
        ("Image Generation", generation_ok)
    ]
    
    passed = sum(1 for _, ok in tests if ok)
    total = len(tests)
    
    for test_name, ok in tests:
        status = "✅ PASS" if ok else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📊 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Image generation service is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
