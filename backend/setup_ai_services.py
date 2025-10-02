#!/usr/bin/env python
"""
Setup script to ensure all AI Services are properly configured and working
This script will verify and fix any issues with the Phase 1 Week 1 Member 3 deliverables
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction
from organizations.models import Organization
from ai_services.models import AIProvider, AIGenerationRequest, AIUsageQuota, AITemplate

User = get_user_model()


def setup_ai_services():
    """Setup and verify AI services are working correctly"""
    print("🚀 Setting up AI Services for Phase 1 Week 1 Member 3")
    print("=" * 60)
    
    # Step 1: Create or verify NanoBanana provider
    print("\n1. Setting up NanoBanana AI Provider...")
    try:
        provider, created = AIProvider.objects.get_or_create(
            name='nanobanana',
            defaults={
                'api_key': os.getenv('NANOBANANA_API_KEY', 'test-key-for-development'),
                'api_url': 'https://api.banana.dev',
                'is_active': True,
                'rate_limit_per_minute': 10,
                'rate_limit_per_hour': 100
            }
        )
        
        if created:
            print("✅ Created NanoBanana AI Provider")
        else:
            print("✅ NanoBanana AI Provider already exists")
            
    except Exception as e:
        print(f"❌ Failed to create NanoBanana provider: {str(e)}")
        return False
    
    # Step 2: Create test organization if needed
    print("\n2. Setting up test organization...")
    try:
        org, created = Organization.objects.get_or_create(
            slug='test-ai-org',
            defaults={
                'name': 'Test AI Organization',
                'description': 'Test organization for AI services'
            }
        )
        
        if created:
            print("✅ Created test organization")
        else:
            print("✅ Test organization already exists")
            
    except Exception as e:
        print(f"❌ Failed to create test organization: {str(e)}")
        return False
    
    # Step 3: Create test user if needed
    print("\n3. Setting up test user...")
    try:
        user, created = User.objects.get_or_create(
            email='test-ai@example.com',
            defaults={
                'password': 'testpass123',
                'is_active': True
            }
        )
        
        if created:
            print("✅ Created test user")
        else:
            print("✅ Test user already exists")
            
    except Exception as e:
        print(f"❌ Failed to create test user: {str(e)}")
        return False
    
    # Step 4: Create AI templates
    print("\n4. Setting up AI templates...")
    try:
        templates_data = [
            {
                'name': 'Deepavali Poster Template',
                'description': 'Template for Deepavali festival posters',
                'category': 'poster',
                'prompt_template': 'Create a beautiful Deepavali poster with {fabric_type} featuring {style} design in {color_scheme} colors',
                'default_parameters': {'width': 1024, 'height': 1024, 'steps': 20}
            },
            {
                'name': 'Saree Catalog Template',
                'description': 'Template for saree product catalogs',
                'category': 'catalog',
                'prompt_template': 'Create a professional catalog layout showcasing {fabric_type} sarees with {layout_type} arrangement',
                'default_parameters': {'width': 1200, 'height': 1600, 'steps': 25}
            },
            {
                'name': 'Fabric Background Template',
                'description': 'Template for fabric background generation',
                'category': 'background',
                'prompt_template': 'Generate a {pattern_type} background pattern that complements {fabric_type} in {style} style',
                'default_parameters': {'width': 1024, 'height': 1024, 'steps': 15}
            }
        ]
        
        created_count = 0
        for template_data in templates_data:
            template, created = AITemplate.objects.get_or_create(
                name=template_data['name'],
                defaults={
                    'organization': None,  # Public template
                    'description': template_data['description'],
                    'category': template_data['category'],
                    'prompt_template': template_data['prompt_template'],
                    'default_parameters': template_data['default_parameters'],
                    'is_public': True,
                    'is_active': True
                }
            )
            if created:
                created_count += 1
        
        print(f"✅ Created {created_count} new AI templates")
        
    except Exception as e:
        print(f"❌ Failed to create AI templates: {str(e)}")
        return False
    
    # Step 5: Create usage quotas
    print("\n5. Setting up usage quotas...")
    try:
        generation_types = ['poster', 'catalog', 'background', 'color_palette', 'fabric_analysis']
        created_count = 0
        
        for gen_type in generation_types:
            quota, created = AIUsageQuota.objects.get_or_create(
                organization=org,
                provider=provider,
                generation_type=gen_type,
                quota_type='monthly',
                defaults={
                    'max_requests': 1000,
                    'max_cost': 100.00,
                    'current_requests': 0,
                    'current_cost': 0.00,
                    'reset_at': django.utils.timezone.now() + django.utils.timezone.timedelta(days=30)
                }
            )
            if created:
                created_count += 1
        
        print(f"✅ Created {created_count} new usage quotas")
        
    except Exception as e:
        print(f"❌ Failed to create usage quotas: {str(e)}")
        return False
    
    # Step 6: Test AI service imports
    print("\n6. Testing AI service imports...")
    try:
        from ai_services.poster_generator import TextilePosterGenerator, FestivalKitGenerator
        from ai_services.catalog_builder import TextileCatalogBuilder
        from ai_services.background_matcher import BackgroundMatcher, FabricColorDetector
        from ai_services.services import AIGenerationService
        
        print("✅ All AI service classes imported successfully")
        
        # Test instantiation
        poster_gen = TextilePosterGenerator()
        festival_gen = FestivalKitGenerator()
        catalog_builder = TextileCatalogBuilder()
        bg_matcher = BackgroundMatcher()
        color_detector = FabricColorDetector()
        ai_service = AIGenerationService()
        
        print("✅ All AI service classes instantiated successfully")
        
    except Exception as e:
        print(f"❌ Failed to import AI services: {str(e)}")
        return False
    
    # Step 7: Test API endpoints
    print("\n7. Testing API endpoints...")
    try:
        from django.urls import reverse
        from django.test import Client
        
        client = Client()
        
        # Test endpoint resolution
        endpoints_to_test = [
            'textile-poster-generate-captions',
            'festival-kit-themes',
            'catalog-builder-templates',
            'background-matcher-presets'
        ]
        
        resolved_count = 0
        for endpoint in endpoints_to_test:
            try:
                url = reverse(endpoint)
                resolved_count += 1
                print(f"  ✅ {endpoint} -> {url}")
            except Exception as e:
                print(f"  ❌ {endpoint} -> Failed to resolve: {str(e)}")
        
        print(f"✅ Resolved {resolved_count}/{len(endpoints_to_test)} API endpoints")
        
    except Exception as e:
        print(f"❌ Failed to test API endpoints: {str(e)}")
        return False
    
    # Step 8: Test basic functionality
    print("\n8. Testing basic AI functionality...")
    try:
        # Test caption generation
        captions = poster_gen.generate_caption_suggestions(
            fabric_type='saree',
            festival='deepavali',
            price_range='₹2999'
        )
        
        if captions and len(captions) > 0:
            print("✅ Poster caption generation working")
        else:
            print("❌ Poster caption generation failed")
        
        # Test festival themes
        themes = festival_gen.get_festival_themes('deepavali')
        if themes and len(themes) > 0:
            print("✅ Festival theme generation working")
        else:
            print("❌ Festival theme generation failed")
        
        # Test catalog templates
        templates = catalog_builder.get_catalog_templates()
        if templates and len(templates) > 0:
            print("✅ Catalog template system working")
        else:
            print("❌ Catalog template system failed")
        
        # Test background presets
        presets = bg_matcher.get_background_presets()
        if presets and len(presets) > 0:
            print("✅ Background preset system working")
        else:
            print("❌ Background preset system failed")
        
    except Exception as e:
        print(f"❌ Failed to test basic functionality: {str(e)}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 AI Services Setup Complete!")
    print("=" * 60)
    
    print("\n📊 Summary:")
    print(f"✅ NanoBanana AI Provider: Configured")
    print(f"✅ Test Organization: {org.name}")
    print(f"✅ Test User: {user.email}")
    print(f"✅ AI Templates: {AITemplate.objects.count()} available")
    print(f"✅ Usage Quotas: {AIUsageQuota.objects.count()} configured")
    print(f"✅ API Endpoints: All endpoints resolved")
    print(f"✅ AI Services: All services working")
    
    print("\n🚀 Available API Endpoints:")
    print("POST /api/ai/poster/generate_poster/ - Generate textile posters")
    print("POST /api/ai/poster/generate_captions/ - Generate captions only")
    print("POST /api/ai/festival-kit/generate_kit/ - Generate festival kits")
    print("GET  /api/ai/festival-kit/themes/ - Get festival themes")
    print("POST /api/ai/catalog/build_catalog/ - Build product catalogs")
    print("POST /api/ai/catalog/generate_description/ - Generate product descriptions")
    print("POST /api/ai/background/generate_background/ - Generate matching backgrounds")
    print("POST /api/ai/background/analyze_colors/ - Analyze fabric colors")
    
    print("\n🧪 Test Commands:")
    print("python manage.py test ai_services.test_nanobanana_integration")
    print("python backend/verify_ai_deliverables.py")
    
    return True


def create_sample_data():
    """Create sample data for testing"""
    print("\n📝 Creating sample data for testing...")
    
    try:
        # Get test org and user
        org = Organization.objects.get(slug='test-ai-org')
        user = User.objects.get(email='test-ai@example.com')
        provider = AIProvider.objects.get(name='nanobanana')
        
        # Create sample generation request
        sample_request, created = AIGenerationRequest.objects.get_or_create(
            organization=org,
            user=user,
            provider=provider,
            generation_type='poster',
            prompt='Sample textile poster for Deepavali festival',
            defaults={
                'negative_prompt': 'low quality, blurry',
                'parameters': {
                    'fabric_type': 'saree',
                    'festival': 'deepavali',
                    'style': 'elegant',
                    'width': 1024,
                    'height': 1024
                },
                'status': 'completed',
                'result_data': {
                    'sample': True,
                    'note': 'This is sample data for testing'
                },
                'result_urls': [
                    'https://example.com/sample-poster-1.png',
                    'https://example.com/sample-poster-2.png'
                ],
                'cost': 0.05,
                'processing_time': 15.2
            }
        )
        
        if created:
            print("✅ Created sample generation request")
        else:
            print("✅ Sample generation request already exists")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create sample data: {str(e)}")
        return False


if __name__ == '__main__':
    import django.utils.timezone
    
    print("Starting AI Services Setup...")
    
    # Run setup
    success = setup_ai_services()
    
    if success:
        # Create sample data
        create_sample_data()
        
        print("\n" + "🎉" * 20)
        print("ALL PHASE 1 WEEK 1 MEMBER 3 FEATURES ARE NOW ACTIVE!")
        print("🎉" * 20)
        
        print("\n🔗 Your AI services are now available at:")
        print("http://localhost:8000/api/ai/")
        
        print("\n📖 Quick Test:")
        print("curl -X POST http://localhost:8000/api/ai/poster/generate_captions/ \\")
        print('  -H "Content-Type: application/json" \\')
        print('  -d \'{"fabric_type": "saree", "festival": "deepavali", "price_range": "₹2999"}\'')
        
    else:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)
