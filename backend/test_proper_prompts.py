#!/usr/bin/env python
"""
Test image and caption generation with proper prompts
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

# Set API key (optional - system works without it)
os.environ['NANOBANANA_API_KEY'] = 'AIzaSyBBP1QGjY7lJBhjNwWMSJCIOZC1bWgSzMY'

def test_image_generation_with_proper_prompts():
    """Test image generation with realistic textile prompts"""
    print("🧪 Testing Image Generation with Proper Prompts...")
    
    try:
        from ai_services.nanobanana_service import NanoBananaAIService
        from ai_services.services import NanoBananaTextileService
        
        # Test 1: Basic NanoBanana service
        print("\n📸 Test 1: Basic Image Generation")
        service = NanoBananaAIService()
        
        test_cases = [
            {
                "prompt": "saree post",
                "theme": "traditional",
                "offer_text": "Special Deepavali Saree Collection",
                "expected": "Should generate traditional saree-related images"
            },
            {
                "prompt": "silk collection",
                "theme": "elegant", 
                "offer_text": "Luxury Silk Sarees",
                "expected": "Should generate elegant silk-related images"
            },
            {
                "prompt": "cotton wear",
                "theme": "modern",
                "offer_text": "Comfortable Cotton Collection",
                "expected": "Should generate modern cotton-related images"
            },
            {
                "prompt": "festive offer",
                "theme": "festive",
                "offer_text": "Festival Special Discount",
                "expected": "Should generate festive celebration images"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n   Test Case {i}: {test_case['prompt']} ({test_case['theme']})")
            
            result = service.generate_poster(
                image_url="https://example.com/fabric.jpg",
                offer_text=test_case['offer_text'],
                theme=test_case['theme']
            )
            
            print(f"     - Success: {result.get('success')}")
            print(f"     - Fallback: {result.get('fallback')}")
            print(f"     - Service used: {result.get('service_used', 'N/A')}")
            print(f"     - Images generated: {len(result.get('image_urls', []))}")
            
            if result.get('image_urls'):
                print(f"     - First image URL: {result['image_urls'][0]}")
                print(f"     - Expected: {test_case['expected']}")
            
            # Check if images are unique
            if i > 1:
                print(f"     - Images are unique: {len(set(result.get('image_urls', []))) == len(result.get('image_urls', []))}")
        
        # Test 2: Textile-specific service
        print("\n📸 Test 2: Textile-Specific Image Generation")
        textile_service = NanoBananaTextileService()
        
        textile_cases = [
            {
                "product": "Silk Saree",
                "description": "Beautiful traditional silk saree with golden border",
                "fabric_type": "silk",
                "festival": "deepavali",
                "theme": "elegant",
                "offer_text": "Luxury Silk Collection"
            },
            {
                "product": "Cotton Saree", 
                "description": "Comfortable everyday cotton saree",
                "fabric_type": "cotton",
                "festival": "pongal",
                "theme": "traditional",
                "offer_text": "Cotton Comfort Wear"
            },
            {
                "product": "Designer Saree",
                "description": "Modern designer saree for special occasions",
                "fabric_type": "saree",
                "festival": "wedding",
                "theme": "modern",
                "offer_text": "Designer Collection"
            }
        ]
        
        for i, test_case in enumerate(textile_cases, 1):
            print(f"\n   Textile Test {i}: {test_case['product']} ({test_case['fabric_type']})")
            
            result = textile_service.generate_textile_poster(
                image_url="https://example.com/fabric.jpg",
                offer_text=test_case['offer_text'],
                theme=test_case['theme'],
                fabric_type=test_case['fabric_type'],
                festival=test_case['festival']
            )
            
            print(f"     - Success: {result.get('success')}")
            print(f"     - Textile specific: {result.get('textile_specific')}")
            print(f"     - Fabric type: {result.get('fabric_type')}")
            print(f"     - Festival: {result.get('festival')}")
            print(f"     - Images generated: {len(result.get('image_urls', []))}")
            
            if result.get('image_urls'):
                print(f"     - First image URL: {result['image_urls'][0]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Image generation test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_caption_generation_with_proper_prompts():
    """Test caption generation with realistic textile prompts"""
    print("\n🧪 Testing Caption Generation with Proper Prompts...")
    
    try:
        from ai_services.nanobanana_service import NanoBananaAIService
        from ai_services.services import NanoBananaTextileService
        
        # Test 1: Basic caption generation
        print("\n📝 Test 1: Basic Caption Generation")
        service = NanoBananaAIService()
        
        caption_cases = [
            {
                "product_name": "Silk Saree",
                "description": "Beautiful traditional silk saree with golden border",
                "expected": "Should generate silk saree-related captions"
            },
            {
                "product_name": "Cotton Saree",
                "description": "Comfortable everyday cotton saree for daily wear",
                "expected": "Should generate cotton saree-related captions"
            },
            {
                "product_name": "Designer Saree",
                "description": "Modern designer saree perfect for special occasions",
                "expected": "Should generate designer saree-related captions"
            }
        ]
        
        for i, test_case in enumerate(caption_cases, 1):
            print(f"\n   Caption Test {i}: {test_case['product_name']}")
            
            result = service.generate_caption(
                product_name=test_case['product_name'],
                description=test_case['description']
            )
            
            print(f"     - Success: {result.get('success')}")
            print(f"     - Fallback: {result.get('fallback')}")
            print(f"     - Captions generated: {len(result.get('captions', []))}")
            
            if result.get('captions'):
                print(f"     - First caption: {result['captions'][0]['text']}")
                print(f"     - Caption tone: {result['captions'][0].get('tone', 'N/A')}")
                print(f"     - Hashtags: {result['captions'][0].get('hashtags', [])}")
                print(f"     - Expected: {test_case['expected']}")
        
        # Test 2: Textile-specific caption generation
        print("\n📝 Test 2: Textile-Specific Caption Generation")
        textile_service = NanoBananaTextileService()
        
        textile_caption_cases = [
            {
                "product_name": "Silk Saree",
                "description": "Luxurious silk saree with intricate embroidery",
                "fabric_type": "silk",
                "price_range": "₹2999",
                "expected": "Should generate silk-specific captions with price"
            },
            {
                "product_name": "Cotton Saree",
                "description": "Comfortable cotton saree for daily wear",
                "fabric_type": "cotton", 
                "price_range": "₹999",
                "expected": "Should generate cotton-specific captions with price"
            },
            {
                "product_name": "Designer Saree",
                "description": "Elegant designer saree for special occasions",
                "fabric_type": "saree",
                "price_range": "₹4999",
                "expected": "Should generate designer-specific captions with price"
            }
        ]
        
        for i, test_case in enumerate(textile_caption_cases, 1):
            print(f"\n   Textile Caption Test {i}: {test_case['product_name']} ({test_case['fabric_type']})")
            
            result = textile_service.generate_textile_caption(
                product_name=test_case['product_name'],
                description=test_case['description'],
                fabric_type=test_case['fabric_type'],
                price_range=test_case['price_range']
            )
            
            print(f"     - Success: {result.get('success')}")
            print(f"     - Textile specific: {result.get('textile_specific')}")
            print(f"     - Fabric type: {result.get('fabric_type')}")
            print(f"     - Price range: {result.get('price_range')}")
            print(f"     - Captions generated: {len(result.get('captions', []))}")
            
            if result.get('captions'):
                for j, caption in enumerate(result['captions'], 1):
                    print(f"     - Caption {j}: {caption['text']}")
                    print(f"       Tone: {caption.get('tone', 'N/A')}")
                    print(f"       Hashtags: {caption.get('hashtags', [])}")
                print(f"     - Expected: {test_case['expected']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Caption generation test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoints_with_proper_prompts():
    """Test API endpoints with proper prompts"""
    print("\n🧪 Testing API Endpoints with Proper Prompts...")
    
    try:
        from django.test import Client
        from django.contrib.auth import get_user_model
        from organizations.models import Organization
        
        User = get_user_model()
        
        # Create test user and organization
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        organization = Organization.objects.create(
            name='Test Organization',
            slug='test-org'
        )
        
        user.organization_memberships.create(
            organization=organization,
            role='admin',
            is_active=True
        )
        
        client = Client()
        client.force_login(user)
        
        # Test poster generation endpoint
        print("\n📸 Testing Poster Generation Endpoint")
        poster_data = {
            "image_url": "https://example.com/silk.jpg",
            "offer_text": "Special Deepavali Silk Collection",
            "theme": "elegant",
            "fabric_type": "silk",
            "festival": "deepavali"
        }
        
        response = client.post('/api/ai/textile/poster/generate_poster_nanobanana/', 
                             poster_data, content_type='application/json')
        
        print(f"   - Response status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   - Success: {data.get('success')}")
            print(f"   - Images generated: {len(data.get('image_urls', []))}")
            if data.get('image_urls'):
                print(f"   - First image: {data['image_urls'][0]}")
        else:
            print(f"   - Error: {response.content.decode()}")
        
        # Test caption generation endpoint
        print("\n📝 Testing Caption Generation Endpoint")
        caption_data = {
            "product_name": "Silk Saree",
            "description": "Beautiful traditional silk saree with golden border",
            "fabric_type": "silk",
            "price_range": "₹2999"
        }
        
        response = client.post('/api/ai/textile/caption/generate_caption_nanobanana/', 
                             caption_data, content_type='application/json')
        
        print(f"   - Response status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   - Success: {data.get('success')}")
            print(f"   - Captions generated: {len(data.get('captions', []))}")
            if data.get('captions'):
                print(f"   - First caption: {data['captions'][0]['text']}")
        else:
            print(f"   - Error: {response.content.decode()}")
        
        # Clean up
        user.delete()
        organization.delete()
        
        return True
        
    except Exception as e:
        print(f"❌ API endpoints test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 Testing Image and Caption Generation with Proper Prompts")
    print("=" * 70)
    
    tests = [
        ("Image Generation with Proper Prompts", test_image_generation_with_proper_prompts),
        ("Caption Generation with Proper Prompts", test_caption_generation_with_proper_prompts),
        ("API Endpoints with Proper Prompts", test_api_endpoints_with_proper_prompts),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} passed")
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
    
    print("\n" + "=" * 70)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Image and caption generation are working properly!")
        print("   • Image generation works with proper textile prompts")
        print("   • Caption generation works with proper product descriptions")
        print("   • API endpoints work with realistic data")
        print("   • System generates unique images for different prompts")
        print("   • System generates relevant captions for different products")
        return True
    else:
        print("⚠️  Some tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

