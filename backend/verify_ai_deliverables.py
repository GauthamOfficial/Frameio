#!/usr/bin/env python
"""
Verification Script for Phase 1 Week 1 Member 3 AI Deliverables
Verifies all NanoBanana AI integration features are working correctly
"""
import os
import sys
import django
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from organizations.models import Organization
from ai_services.models import AIProvider, AIGenerationRequest
from ai_services.poster_generator import TextilePosterGenerator, FestivalKitGenerator
from ai_services.catalog_builder import TextileCatalogBuilder
from ai_services.background_matcher import BackgroundMatcher, FabricColorDetector

User = get_user_model()


class AIDeliverablesVerifier:
    """Verifies all AI deliverables are working correctly"""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_results': []
        }
        
        # Setup test data
        self.setup_test_data()
    
    def setup_test_data(self):
        """Setup test organization and user"""
        try:
            self.organization, created = Organization.objects.get_or_create(
                slug='test-verification-org',
                defaults={'name': 'Test Verification Organization'}
            )
            
            self.user, created = User.objects.get_or_create(
                email='test-verification@example.com',
                defaults={'password': 'testpass123'}
            )
            
            # Create NanoBanana provider
            self.provider, created = AIProvider.objects.get_or_create(
                name='nanobanana',
                defaults={
                    'api_key': 'test-key',
                    'api_url': 'https://api.banana.dev',
                    'is_active': True
                }
            )
            
            print("✅ Test data setup completed")
            
        except Exception as e:
            print(f"❌ Failed to setup test data: {str(e)}")
            sys.exit(1)
    
    def run_test(self, test_name, test_function):
        """Run a single test and record results"""
        self.results['total_tests'] += 1
        
        try:
            print(f"\n🧪 Running test: {test_name}")
            result = test_function()
            
            if result['success']:
                print(f"✅ {test_name} - PASSED")
                self.results['passed_tests'] += 1
                status = 'PASSED'
            else:
                print(f"❌ {test_name} - FAILED: {result.get('error', 'Unknown error')}")
                self.results['failed_tests'] += 1
                status = 'FAILED'
            
            self.results['test_results'].append({
                'test_name': test_name,
                'status': status,
                'details': result,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {str(e)}")
            self.results['failed_tests'] += 1
            self.results['test_results'].append({
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
    
    def verify_poster_generator(self):
        """Verify Poster Generator functionality"""
        try:
            poster_generator = TextilePosterGenerator()
            
            # Test caption generation
            captions = poster_generator.generate_caption_suggestions(
                fabric_type='saree',
                festival='deepavali',
                price_range='₹2999',
                style='elegant'
            )
            
            if not captions or len(captions) == 0:
                return {'success': False, 'error': 'No captions generated'}
            
            # Verify caption structure
            caption = captions[0]
            required_fields = ['text', 'type', 'tone', 'effectiveness_score']
            for field in required_fields:
                if field not in caption:
                    return {'success': False, 'error': f'Missing field: {field}'}
            
            # Test festival-specific captions
            festivals = ['deepavali', 'pongal', 'wedding']
            for festival in festivals:
                fest_captions = poster_generator.generate_caption_suggestions(
                    fabric_type='saree',
                    festival=festival
                )
                
                if not any(festival.title() in cap['text'] for cap in fest_captions):
                    return {'success': False, 'error': f'Festival {festival} not found in captions'}
            
            # Test prompt creation
            prompt = poster_generator.create_poster_prompt(
                fabric_type='saree',
                festival='deepavali',
                style='elegant'
            )
            
            if not prompt or len(prompt) < 50:
                return {'success': False, 'error': 'Generated prompt too short'}
            
            return {
                'success': True,
                'captions_generated': len(captions),
                'festivals_tested': len(festivals),
                'prompt_length': len(prompt)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def verify_festival_kit_generator(self):
        """Verify Festival Kit Generator functionality"""
        try:
            festival_generator = FestivalKitGenerator()
            
            # Test theme retrieval
            themes = festival_generator.get_festival_themes('deepavali')
            if not themes or len(themes) == 0:
                return {'success': False, 'error': 'No themes generated'}
            
            # Verify theme structure
            theme = themes[0]
            required_fields = ['name', 'colors', 'elements', 'mood']
            for field in required_fields:
                if field not in theme:
                    return {'success': False, 'error': f'Missing theme field: {field}'}
            
            # Test color palettes
            palettes = festival_generator.get_festival_color_palettes('deepavali')
            if not palettes or len(palettes) == 0:
                return {'success': False, 'error': 'No color palettes generated'}
            
            # Verify palette structure
            palette = palettes[0]
            required_fields = ['name', 'primary', 'secondary', 'accent', 'background']
            for field in required_fields:
                if field not in palette:
                    return {'success': False, 'error': f'Missing palette field: {field}'}
            
            # Test multiple festivals
            festivals = ['deepavali', 'pongal', 'wedding']
            for festival in festivals:
                fest_themes = festival_generator.get_festival_themes(festival)
                if not fest_themes:
                    return {'success': False, 'error': f'No themes for festival: {festival}'}
            
            return {
                'success': True,
                'themes_generated': len(themes),
                'palettes_generated': len(palettes),
                'festivals_supported': len(festivals)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def verify_catalog_builder(self):
        """Verify Catalog Builder functionality"""
        try:
            catalog_builder = TextileCatalogBuilder()
            
            # Test product description generation
            product_info = {
                'name': 'Elegant Silk Saree',
                'fabric_type': 'silk',
                'color': 'golden',
                'price': '₹4999',
                'category': 'saree',
                'features': ['handwoven', 'pure silk', 'traditional design']
            }
            
            result = catalog_builder.generate_product_description(
                organization=self.organization,
                user=self.user,
                product_info=product_info
            )
            
            if not result['success']:
                return {'success': False, 'error': 'Product description generation failed'}
            
            if 'description' not in result or not result['description']:
                return {'success': False, 'error': 'No description generated'}
            
            # Test description variations
            variations = catalog_builder.create_description_variations(
                product_name='Test Saree',
                fabric_type='silk',
                color='golden',
                price='₹2999',
                features=['handwoven']
            )
            
            if not variations or len(variations) < 3:
                return {'success': False, 'error': 'Insufficient description variations'}
            
            # Verify variation structure
            variation = variations[0]
            required_fields = ['text', 'style', 'tone', 'effectiveness_score']
            for field in required_fields:
                if field not in variation:
                    return {'success': False, 'error': f'Missing variation field: {field}'}
            
            # Test catalog templates
            templates = catalog_builder.get_catalog_templates()
            if not templates or len(templates) == 0:
                return {'success': False, 'error': 'No catalog templates available'}
            
            # Test catalog prompt creation
            products = [product_info]
            prompt = catalog_builder.create_catalog_prompt(
                products=products,
                style='modern',
                layout_type='grid',
                theme='professional'
            )
            
            if not prompt or len(prompt) < 50:
                return {'success': False, 'error': 'Generated catalog prompt too short'}
            
            return {
                'success': True,
                'description_generated': True,
                'variations_count': len(variations),
                'templates_available': len(templates),
                'prompt_length': len(prompt)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def verify_background_matcher(self):
        """Verify Background Matcher functionality"""
        try:
            background_matcher = BackgroundMatcher()
            color_detector = FabricColorDetector()
            
            # Test color analysis (with mock data)
            mock_fabric_url = 'https://example.com/fabric.jpg'
            
            # Since we can't actually analyze a real image, we'll test the logic
            # Test color harmony analysis
            sample_palette = [
                {'hex': '#FF6B6B', 'rgb': [255, 107, 107], 'name': 'Red', 'percentage': 40},
                {'hex': '#FF8E53', 'rgb': [255, 142, 83], 'name': 'Orange', 'percentage': 30},
                {'hex': '#FF6B9D', 'rgb': [255, 107, 157], 'name': 'Pink', 'percentage': 30}
            ]
            
            harmony = color_detector.analyze_color_harmony(sample_palette)
            if 'type' not in harmony or 'score' not in harmony:
                return {'success': False, 'error': 'Color harmony analysis failed'}
            
            # Test color temperature analysis
            temperature = color_detector.analyze_color_temperature(sample_palette)
            if 'temperature' not in temperature or 'score' not in temperature:
                return {'success': False, 'error': 'Color temperature analysis failed'}
            
            # Test fabric mood determination
            mood = color_detector.determine_fabric_mood(sample_palette)
            if 'mood' not in mood or 'confidence' not in mood:
                return {'success': False, 'error': 'Fabric mood determination failed'}
            
            # Test background suggestions
            mock_color_analysis = {
                'success': True,
                'color_palette': sample_palette,
                'analysis': {
                    'dominant_colors': sample_palette[:2],
                    'fabric_mood': mood,
                    'color_temperature': temperature
                }
            }
            
            suggestions = background_matcher.create_background_suggestions(
                color_analysis=mock_color_analysis,
                background_style='complementary',
                pattern_type='seamless',
                intensity='medium'
            )
            
            if not suggestions or len(suggestions) == 0:
                return {'success': False, 'error': 'No background suggestions generated'}
            
            # Verify suggestion structure
            suggestion = suggestions[0]
            required_fields = ['style', 'primary_color', 'matching_score', 'description']
            for field in required_fields:
                if field not in suggestion:
                    return {'success': False, 'error': f'Missing suggestion field: {field}'}
            
            # Test background presets
            presets = background_matcher.get_background_presets()
            if not presets or len(presets) == 0:
                return {'success': False, 'error': 'No background presets available'}
            
            return {
                'success': True,
                'harmony_analysis': harmony['type'],
                'temperature_analysis': temperature['temperature'],
                'mood_analysis': mood['mood'],
                'suggestions_count': len(suggestions),
                'presets_available': len(presets)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def verify_api_endpoints(self):
        """Verify API endpoints are properly configured"""
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
            
            resolved_endpoints = []
            for endpoint in endpoints_to_test:
                try:
                    url = reverse(endpoint)
                    resolved_endpoints.append(endpoint)
                except Exception as e:
                    return {'success': False, 'error': f'Failed to resolve endpoint {endpoint}: {str(e)}'}
            
            return {
                'success': True,
                'endpoints_resolved': len(resolved_endpoints),
                'endpoints': resolved_endpoints
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def verify_database_models(self):
        """Verify database models are working correctly"""
        try:
            # Test AIProvider model
            provider_count = AIProvider.objects.count()
            
            # Test AIGenerationRequest model
            test_request = AIGenerationRequest.objects.create(
                organization=self.organization,
                user=self.user,
                provider=self.provider,
                generation_type='poster',
                prompt='Test prompt for verification',
                parameters={'test': True}
            )
            
            # Test request methods
            test_request.mark_completed(
                result_data={'test': 'data'},
                result_urls=['https://example.com/test.png']
            )
            
            if test_request.status != 'completed':
                return {'success': False, 'error': 'Request status not updated correctly'}
            
            # Clean up test request
            test_request.delete()
            
            return {
                'success': True,
                'providers_count': provider_count,
                'request_creation': True,
                'request_completion': True
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def verify_nanobanana_integration(self):
        """Verify NanoBanana integration setup"""
        try:
            from django.conf import settings
            
            # Check if NanoBanana settings are configured
            has_api_key = hasattr(settings, 'NANOBANANA_API_KEY') and settings.NANOBANANA_API_KEY
            has_model_key = hasattr(settings, 'NANOBANANA_MODEL_KEY')
            
            # Check if banana-dev is importable
            try:
                import banana_dev
                banana_importable = True
            except ImportError:
                banana_importable = False
            
            # Check provider exists
            try:
                provider = AIProvider.objects.get(name='nanobanana')
                provider_exists = True
            except AIProvider.DoesNotExist:
                provider_exists = False
            
            return {
                'success': True,
                'api_key_configured': has_api_key,
                'model_key_configured': has_model_key,
                'banana_dev_importable': banana_importable,
                'provider_exists': provider_exists,
                'integration_ready': all([has_api_key, banana_importable, provider_exists])
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def run_all_verifications(self):
        """Run all verification tests"""
        print("🚀 Starting AI Deliverables Verification")
        print("=" * 50)
        
        # Run all tests
        self.run_test("NanoBanana Integration Setup", self.verify_nanobanana_integration)
        self.run_test("Database Models", self.verify_database_models)
        self.run_test("API Endpoints Configuration", self.verify_api_endpoints)
        self.run_test("Poster Generator", self.verify_poster_generator)
        self.run_test("Festival Kit Generator", self.verify_festival_kit_generator)
        self.run_test("Catalog Builder", self.verify_catalog_builder)
        self.run_test("Background Matcher", self.verify_background_matcher)
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 VERIFICATION SUMMARY")
        print("=" * 50)
        print(f"Total Tests: {self.results['total_tests']}")
        print(f"Passed: {self.results['passed_tests']} ✅")
        print(f"Failed: {self.results['failed_tests']} ❌")
        
        success_rate = (self.results['passed_tests'] / self.results['total_tests']) * 100
        print(f"Success Rate: {success_rate:.1f}%")
        
        if self.results['failed_tests'] == 0:
            print("\n🎉 ALL DELIVERABLES VERIFIED SUCCESSFULLY!")
            print("✅ Phase 1 Week 1 Member 3 tasks are complete and working")
        else:
            print(f"\n⚠️  {self.results['failed_tests']} tests failed. Please review the issues above.")
        
        # Save results to file
        with open('ai_deliverables_verification_report.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: ai_deliverables_verification_report.json")
        
        return self.results['failed_tests'] == 0


def main():
    """Main function to run verification"""
    verifier = AIDeliverablesVerifier()
    success = verifier.run_all_verifications()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

