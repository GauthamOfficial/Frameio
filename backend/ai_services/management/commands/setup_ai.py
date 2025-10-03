"""
Django management command to setup AI services
Usage: python manage.py setup_ai
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from organizations.models import Organization
from ai_services.models import AIProvider, AITemplate, AIUsageQuota
import os

User = get_user_model()


class Command(BaseCommand):
    help = 'Setup AI services for Phase 1 Week 1 Member 3 deliverables'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreate all data',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Setting up AI Services...')
        )

        try:
            with transaction.atomic():
                # Setup NanoBanana provider
                provider, created = AIProvider.objects.get_or_create(
                    name='nanobanana',
                    defaults={
                        'api_key': os.getenv('NANOBANANA_API_KEY', 'test-key'),
                        'api_url': 'https://api.banana.dev',
                        'is_active': True,
                        'rate_limit_per_minute': 10,
                        'rate_limit_per_hour': 100
                    }
                )
                
                if created:
                    self.stdout.write('✅ Created NanoBanana provider')
                else:
                    self.stdout.write('✅ NanoBanana provider exists')

                # Setup test organization
                org, created = Organization.objects.get_or_create(
                    slug='test-ai-org',
                    defaults={
                        'name': 'Test AI Organization',
                        'description': 'Test organization for AI services'
                    }
                )
                
                if created:
                    self.stdout.write('✅ Created test organization')
                else:
                    self.stdout.write('✅ Test organization exists')

                # Create AI templates
                templates_data = [
                    {
                        'name': 'Deepavali Poster Template',
                        'description': 'Template for Deepavali festival posters',
                        'category': 'poster',
                        'prompt_template': 'Create a beautiful Deepavali poster with {fabric_type} featuring {style} design',
                    },
                    {
                        'name': 'Saree Catalog Template',
                        'description': 'Template for saree product catalogs',
                        'category': 'catalog',
                        'prompt_template': 'Create a professional catalog layout showcasing {fabric_type} sarees',
                    }
                ]

                created_templates = 0
                for template_data in templates_data:
                    template, created = AITemplate.objects.get_or_create(
                        name=template_data['name'],
                        defaults={
                            'organization': None,
                            'description': template_data['description'],
                            'category': template_data['category'],
                            'prompt_template': template_data['prompt_template'],
                            'is_public': True,
                            'is_active': True
                        }
                    )
                    if created:
                        created_templates += 1

                self.stdout.write(f'✅ Created {created_templates} templates')

                # Test imports
                try:
                    from ai_services.poster_generator import TextilePosterGenerator
                    from ai_services.catalog_builder import TextileCatalogBuilder
                    from ai_services.background_matcher import BackgroundMatcher
                    
                    # Test instantiation
                    poster_gen = TextilePosterGenerator()
                    catalog_builder = TextileCatalogBuilder()
                    bg_matcher = BackgroundMatcher()
                    
                    self.stdout.write('✅ All AI services imported successfully')
                    
                    # Test basic functionality
                    captions = poster_gen.generate_caption_suggestions(
                        fabric_type='saree',
                        festival='deepavali',
                        price_range='₹2999'
                    )
                    
                    if captions:
                        self.stdout.write('✅ Caption generation working')
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Import test failed: {str(e)}')
                    )

                self.stdout.write(
                    self.style.SUCCESS('\n🎉 AI Services setup complete!')
                )
                
                self.stdout.write('\n📊 Available endpoints:')
                self.stdout.write('POST /api/ai/poster/generate_captions/')
                self.stdout.write('GET  /api/ai/festival-kit/themes/')
                self.stdout.write('GET  /api/ai/catalog/templates/')
                self.stdout.write('GET  /api/ai/background/presets/')
                
                self.stdout.write('\n🧪 Test with:')
                self.stdout.write('python backend/test_ai_endpoints.py')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Setup failed: {str(e)}')
            )
            raise

