"""
Comprehensive Test Cases for NanoBanana AI Integration
Tests all Phase 1 Week 1 Member 3 deliverables
"""
import pytest
import json
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock

from organizations.models import Organization
from .models import AIProvider, AIGenerationRequest, AIUsageQuota, AITemplate
from .poster_generator import TextilePosterGenerator, FestivalKitGenerator
from .catalog_builder import TextileCatalogBuilder
from .background_matcher import BackgroundMatcher, FabricColorDetector
from .services import AIGenerationService

User = get_user_model()


class NanoBananaIntegrationTestCase(TestCase):
    """Test NanoBanana AI integration"""
    
    def setUp(self):
        """Set up test data"""
        self.organization = Organization.objects.create(
            name="Test Textile Shop",
            slug="test-textile-shop"
        )
        
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        
        self.provider = AIProvider.objects.create(
            name='nanobanana',
            api_key='test-api-key',
            api_url='https://api.banana.dev',
            is_active=True
        )
    
    @patch('ai_services.services.banana_dev.banana.run')
    def test_nanobanana_api_integration(self, mock_banana_run):
        """Test NanoBanana API integration"""
        # Mock API response
        mock_banana_run.return_value = {
            'id': 'test-generation-123',
            'modelOutputs': [{
                'image_urls': ['https://example.com/generated1.png'],
                'prompt_used': 'test prompt'
            }]
        }
        
        # Create generation request
        request = AIGenerationRequest.objects.create(
            organization=self.organization,
            user=self.user,
            provider=self.provider,
            generation_type='poster',
            prompt='Generate elegant saree poster',
            parameters={'width': 1024, 'height': 1024}
        )
        
        # Process request
        ai_service = AIGenerationService()
        success = ai_service.process_generation_request(request)
        
        # Assertions
        self.assertTrue(success)
        request.refresh_from_db()
        self.assertEqual(request.status, 'completed')
        self.assertIsNotNone(request.result_urls)
        mock_banana_run.assert_called_once()
    
    def test_ai_provider_creation(self):
        """Test AI provider model"""
        provider = AIProvider.objects.get(name='nanobanana')
        self.assertEqual(provider.name, 'nanobanana')
        self.assertTrue(provider.is_active)
        self.assertEqual(provider.api_url, 'https://api.banana.dev')


class TextilePosterGeneratorTestCase(TestCase):
    """Test Textile Poster Generator"""
    
    def setUp(self):
        """Set up test data"""
        self.organization = Organization.objects.create(
            name="Test Textile Shop",
            slug="test-textile-shop"
        )
        
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        
        self.poster_generator = TextilePosterGenerator()
    
    def test_caption_generation(self):
        """Test AI caption generation"""
        captions = self.poster_generator.generate_caption_suggestions(
            fabric_type='saree',
            festival='deepavali',
            price_range='₹2999',
            style='elegant'
        )
        
        # Assertions
        self.assertIsInstance(captions, list)
        self.assertGreater(len(captions), 0)
        
        # Check caption structure
        caption = captions[0]
        self.assertIn('text', caption)
        self.assertIn('type', caption)
        self.assertIn('tone', caption)
        self.assertIn('effectiveness_score', caption)
        
        # Check content quality
        self.assertIn('Deepavali', caption['text'])
        self.assertIn('₹2999', caption['text'])
    
    def test_festival_specific_captions(self):
        """Test festival-specific caption generation"""
        # Test Deepavali captions
        deepavali_captions = self.poster_generator.generate_caption_suggestions(
            fabric_type='saree',
            festival='deepavali'
        )
        
        # Test Pongal captions
        pongal_captions = self.poster_generator.generate_caption_suggestions(
            fabric_type='saree',
            festival='pongal'
        )
        
        # Test Wedding captions
        wedding_captions = self.poster_generator.generate_caption_suggestions(
            fabric_type='saree',
            festival='wedding'
        )
        
        # Assertions
        self.assertTrue(any('Deepavali' in cap['text'] for cap in deepavali_captions))
        self.assertTrue(any('Pongal' in cap['text'] for cap in pongal_captions))
        self.assertTrue(any('Wedding' in cap['text'] for cap in wedding_captions))
    
    @patch('ai_services.services.AIGenerationService.process_generation_request')
    def test_poster_generation_with_caption(self, mock_process):
        """Test complete poster generation with captions"""
        mock_process.return_value = True
        
        # Mock the request object
        with patch('ai_services.models.AIGenerationRequest.objects.create') as mock_create:
            mock_request = MagicMock()
            mock_request.id = 'test-id-123'
            mock_request.result_urls = ['https://example.com/poster1.png']
            mock_request.cost = 0.05
            mock_request.processing_time = 15.5
            mock_create.return_value = mock_request
            
            result = self.poster_generator.generate_poster_with_caption(
                organization=self.organization,
                user=self.user,
                fabric_type='saree',
                festival='deepavali',
                price_range='₹2999'
            )
            
            # Assertions
            self.assertTrue(result['success'])
            self.assertIn('caption_suggestions', result)
            self.assertIn('selected_caption', result)
            self.assertIn('poster_urls', result)
    
    def test_poster_prompt_creation(self):
        """Test poster prompt creation"""
        prompt = self.poster_generator.create_poster_prompt(
            fabric_type='saree',
            festival='deepavali',
            style='elegant',
            color_scheme='golden',
            caption_text='Elegant Saree Collection'
        )
        
        # Assertions
        self.assertIsInstance(prompt, str)
        self.assertIn('saree', prompt.lower())
        self.assertIn('deepavali', prompt.lower())
        self.assertIn('elegant', prompt.lower())
        self.assertIn('golden', prompt.lower())


class FestivalKitGeneratorTestCase(TestCase):
    """Test Festival Kit Generator"""
    
    def setUp(self):
        """Set up test data"""
        self.organization = Organization.objects.create(
            name="Test Textile Shop",
            slug="test-textile-shop"
        )
        
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        
        self.festival_generator = FestivalKitGenerator()
    
    def test_festival_themes_retrieval(self):
        """Test festival themes retrieval"""
        themes = self.festival_generator.get_festival_themes('deepavali')
        
        # Assertions
        self.assertIsInstance(themes, list)
        self.assertGreater(len(themes), 0)
        
        # Check theme structure
        theme = themes[0]
        self.assertIn('name', theme)
        self.assertIn('colors', theme)
        self.assertIn('elements', theme)
        self.assertIn('mood', theme)
    
    def test_festival_color_palettes(self):
        """Test festival color palette generation"""
        palettes = self.festival_generator.get_festival_color_palettes('deepavali')
        
        # Assertions
        self.assertIsInstance(palettes, list)
        self.assertGreater(len(palettes), 0)
        
        # Check palette structure
        palette = palettes[0]
        self.assertIn('name', palette)
        self.assertIn('primary', palette)
        self.assertIn('secondary', palette)
        self.assertIn('accent', palette)
        self.assertIn('background', palette)
    
    @patch('ai_services.poster_generator.TextilePosterGenerator.generate_poster_with_caption')
    def test_festival_kit_generation(self, mock_generate_poster):
        """Test complete festival kit generation"""
        # Mock poster generation
        mock_generate_poster.return_value = {
            'success': True,
            'poster_urls': ['https://example.com/poster1.png'],
            'selected_caption': 'Test Caption',
            'request_id': 'test-123',
            'cost': 0.05
        }
        
        result = self.festival_generator.generate_festival_kit(
            organization=self.organization,
            user=self.user,
            festival='deepavali',
            fabric_types=['saree', 'silk'],
            color_schemes=['golden', 'red and gold'],
            price_ranges=['₹2999', '₹4999']
        )
        
        # Assertions
        self.assertTrue(result['success'])
        self.assertEqual(result['festival'], 'deepavali')
        self.assertIn('posters', result)
        self.assertIn('themes', result)
        self.assertIn('color_palettes', result)
        self.assertGreater(len(result['posters']), 0)


class CatalogBuilderTestCase(TestCase):
    """Test Catalog Builder"""
    
    def setUp(self):
        """Set up test data"""
        self.organization = Organization.objects.create(
            name="Test Textile Shop",
            slug="test-textile-shop"
        )
        
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        
        self.catalog_builder = TextileCatalogBuilder()
        
        self.sample_products = [
            {
                'name': 'Elegant Silk Saree',
                'fabric_type': 'silk',
                'color': 'golden',
                'price': '₹4999',
                'category': 'saree',
                'features': ['handwoven', 'pure silk', 'traditional design']
            },
            {
                'name': 'Cotton Casual Wear',
                'fabric_type': 'cotton',
                'color': 'blue',
                'price': '₹1999',
                'category': 'casual',
                'features': ['comfortable', 'breathable', 'machine washable']
            }
        ]
    
    def test_product_description_generation(self):
        """Test AI product description generation"""
        result = self.catalog_builder.generate_product_description(
            organization=self.organization,
            user=self.user,
            product_info=self.sample_products[0]
        )
        
        # Assertions
        self.assertTrue(result['success'])
        self.assertIn('description', result)
        self.assertIn('variations', result)
        self.assertIsInstance(result['variations'], list)
        self.assertGreater(len(result['variations']), 0)
        
        # Check description quality
        description = result['description']
        self.assertIn('Elegant Silk Saree', description)
        self.assertIn('silk', description.lower())
    
    def test_description_variations(self):
        """Test multiple description variations"""
        variations = self.catalog_builder.create_description_variations(
            product_name='Test Saree',
            fabric_type='silk',
            color='golden',
            price='₹2999',
            features=['handwoven', 'traditional']
        )
        
        # Assertions
        self.assertIsInstance(variations, list)
        self.assertGreaterEqual(len(variations), 3)  # At least 3 variations
        
        # Check variation types
        variation_styles = [var['style'] for var in variations]
        self.assertIn('professional', variation_styles)
        self.assertIn('marketing', variation_styles)
        self.assertIn('technical', variation_styles)
        
        # Check effectiveness scores
        for variation in variations:
            self.assertIn('effectiveness_score', variation)
            self.assertGreater(variation['effectiveness_score'], 0)
    
    @patch('ai_services.services.AIGenerationService.process_generation_request')
    def test_catalog_building(self, mock_process):
        """Test complete catalog building"""
        mock_process.return_value = True
        
        with patch('ai_services.models.AIGenerationRequest.objects.create') as mock_create:
            mock_request = MagicMock()
            mock_request.id = 'catalog-123'
            mock_request.result_urls = ['https://example.com/catalog1.png']
            mock_request.cost = 0.10
            mock_request.processing_time = 25.0
            mock_create.return_value = mock_request
            
            result = self.catalog_builder.build_catalog_with_ai_descriptions(
                organization=self.organization,
                user=self.user,
                products=self.sample_products,
                catalog_style='modern',
                layout_type='grid',
                theme='professional'
            )
            
            # Assertions
            self.assertTrue(result['success'])
            self.assertIn('products', result)
            self.assertIn('catalog_urls', result)
            self.assertEqual(len(result['products']), 2)
    
    def test_catalog_templates(self):
        """Test catalog templates"""
        templates = self.catalog_builder.get_catalog_templates()
        
        # Assertions
        self.assertIsInstance(templates, list)
        self.assertGreater(len(templates), 0)
        
        # Check template structure
        template = templates[0]
        self.assertIn('id', template)
        self.assertIn('name', template)
        self.assertIn('description', template)
        self.assertIn('style', template)
        self.assertIn('layout_type', template)


class BackgroundMatcherTestCase(TestCase):
    """Test Background Matcher and Fabric Color Detection"""
    
    def setUp(self):
        """Set up test data"""
        self.organization = Organization.objects.create(
            name="Test Textile Shop",
            slug="test-textile-shop"
        )
        
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        
        self.background_matcher = BackgroundMatcher()
        self.color_detector = FabricColorDetector()
    
    @patch('ai_services.services.AIColorAnalysisService.extract_color_palette')
    def test_fabric_color_analysis(self, mock_extract_colors):
        """Test fabric color analysis"""
        # Mock color palette
        mock_extract_colors.return_value = [
            {'hex': '#FF6B6B', 'rgb': [255, 107, 107], 'name': 'Coral Red', 'percentage': 35},
            {'hex': '#4ECDC4', 'rgb': [78, 205, 196], 'name': 'Turquoise', 'percentage': 25},
            {'hex': '#45B7D1', 'rgb': [69, 183, 209], 'name': 'Sky Blue', 'percentage': 20}
        ]
        
        result = self.color_detector.analyze_fabric_colors('https://example.com/fabric.jpg')
        
        # Assertions
        self.assertTrue(result['success'])
        self.assertIn('color_palette', result)
        self.assertIn('analysis', result)
        
        analysis = result['analysis']
        self.assertIn('dominant_colors', analysis)
        self.assertIn('color_harmony', analysis)
        self.assertIn('color_temperature', analysis)
        self.assertIn('fabric_mood', analysis)
    
    def test_color_harmony_analysis(self):
        """Test color harmony analysis"""
        sample_palette = [
            {'hex': '#FF6B6B', 'rgb': [255, 107, 107], 'name': 'Red', 'percentage': 40},
            {'hex': '#FF8E53', 'rgb': [255, 142, 83], 'name': 'Orange', 'percentage': 30},
            {'hex': '#FF6B9D', 'rgb': [255, 107, 157], 'name': 'Pink', 'percentage': 30}
        ]
        
        harmony = self.color_detector.analyze_color_harmony(sample_palette)
        
        # Assertions
        self.assertIn('type', harmony)
        self.assertIn('score', harmony)
        self.assertIn('description', harmony)
        self.assertGreater(harmony['score'], 0)
    
    def test_color_temperature_analysis(self):
        """Test color temperature analysis"""
        warm_palette = [
            {'hex': '#FF6B6B', 'rgb': [255, 107, 107], 'name': 'Red', 'percentage': 50},
            {'hex': '#FFA500', 'rgb': [255, 165, 0], 'name': 'Orange', 'percentage': 50}
        ]
        
        temperature = self.color_detector.analyze_color_temperature(warm_palette)
        
        # Assertions
        self.assertIn('temperature', temperature)
        self.assertIn('score', temperature)
        self.assertEqual(temperature['temperature'], 'warm')
        self.assertGreater(temperature['score'], 0.5)
    
    def test_fabric_mood_determination(self):
        """Test fabric mood determination"""
        elegant_palette = [
            {'hex': '#000080', 'rgb': [0, 0, 128], 'name': 'Navy Blue', 'percentage': 60},
            {'hex': '#C0C0C0', 'rgb': [192, 192, 192], 'name': 'Silver', 'percentage': 40}
        ]
        
        mood = self.color_detector.determine_fabric_mood(elegant_palette)
        
        # Assertions
        self.assertIn('mood', mood)
        self.assertIn('confidence', mood)
        self.assertIn('description', mood)
        self.assertGreater(mood['confidence'], 0)
    
    def test_background_suggestions(self):
        """Test background suggestion generation"""
        mock_color_analysis = {
            'success': True,
            'color_palette': [
                {'hex': '#FF6B6B', 'rgb': [255, 107, 107], 'name': 'Red', 'percentage': 50}
            ],
            'analysis': {
                'dominant_colors': [
                    {'hex': '#FF6B6B', 'rgb': [255, 107, 107], 'name': 'Red', 'percentage': 50}
                ],
                'fabric_mood': {'mood': 'vibrant', 'confidence': 0.8},
                'color_temperature': {'temperature': 'warm', 'score': 0.7}
            }
        }
        
        suggestions = self.background_matcher.create_background_suggestions(
            color_analysis=mock_color_analysis,
            background_style='complementary',
            pattern_type='seamless',
            intensity='medium'
        )
        
        # Assertions
        self.assertIsInstance(suggestions, list)
        self.assertGreater(len(suggestions), 0)
        
        # Check suggestion structure
        suggestion = suggestions[0]
        self.assertIn('style', suggestion)
        self.assertIn('primary_color', suggestion)
        self.assertIn('matching_score', suggestion)
        self.assertIn('description', suggestion)
    
    def test_background_presets(self):
        """Test background presets"""
        presets = self.background_matcher.get_background_presets()
        
        # Assertions
        self.assertIsInstance(presets, list)
        self.assertGreater(len(presets), 0)
        
        # Check preset structure
        preset = presets[0]
        self.assertIn('id', preset)
        self.assertIn('name', preset)
        self.assertIn('description', preset)
        self.assertIn('style', preset)
        self.assertIn('best_for', preset)


class AIServiceAPITestCase(APITestCase):
    """Test AI Service API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.organization = Organization.objects.create(
            name="Test Textile Shop",
            slug="test-textile-shop"
        )
        
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Mock organization context
        self.patcher = patch('organizations.middleware.get_current_organization')
        self.mock_get_org = self.patcher.start()
        self.mock_get_org.return_value = self.organization
    
    def tearDown(self):
        """Clean up patches"""
        self.patcher.stop()
    
    def test_poster_generation_endpoint(self):
        """Test poster generation API endpoint"""
        url = reverse('textile-poster-generate-poster')
        data = {
            'fabric_type': 'saree',
            'festival': 'deepavali',
            'price_range': '₹2999',
            'style': 'elegant'
        }
        
        with patch('ai_services.poster_generator.TextilePosterGenerator.generate_poster_with_caption') as mock_generate:
            mock_generate.return_value = {
                'success': True,
                'poster_urls': ['https://example.com/poster1.png'],
                'caption_suggestions': [{'text': 'Test Caption', 'effectiveness_score': 9.0}],
                'selected_caption': 'Test Caption'
            }
            
            response = self.client.post(url, data, format='json')
            
            # Assertions
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(response.data['success'])
            self.assertIn('poster_urls', response.data)
    
    def test_caption_generation_endpoint(self):
        """Test caption generation API endpoint"""
        url = reverse('textile-poster-generate-captions')
        data = {
            'fabric_type': 'saree',
            'festival': 'deepavali',
            'price_range': '₹2999'
        }
        
        response = self.client.post(url, data, format='json')
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('caption_suggestions', response.data)
    
    def test_festival_kit_generation_endpoint(self):
        """Test festival kit generation API endpoint"""
        url = reverse('festival-kit-generate-kit')
        data = {
            'festival': 'deepavali',
            'fabric_types': ['saree', 'silk'],
            'color_schemes': ['golden', 'red and gold'],
            'price_ranges': ['₹2999', '₹4999']
        }
        
        with patch('ai_services.poster_generator.FestivalKitGenerator.generate_festival_kit') as mock_generate:
            mock_generate.return_value = {
                'success': True,
                'festival': 'deepavali',
                'posters': [],
                'themes': [],
                'color_palettes': []
            }
            
            response = self.client.post(url, data, format='json')
            
            # Assertions
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(response.data['success'])
            self.assertEqual(response.data['festival'], 'deepavali')
    
    def test_catalog_building_endpoint(self):
        """Test catalog building API endpoint"""
        url = reverse('catalog-builder-build-catalog')
        data = {
            'products': [
                {
                    'name': 'Test Saree',
                    'fabric_type': 'silk',
                    'price': '₹2999'
                }
            ],
            'catalog_style': 'modern',
            'layout_type': 'grid'
        }
        
        with patch('ai_services.catalog_builder.TextileCatalogBuilder.build_catalog_with_ai_descriptions') as mock_build:
            mock_build.return_value = {
                'success': True,
                'products': data['products'],
                'catalog_urls': ['https://example.com/catalog1.png']
            }
            
            response = self.client.post(url, data, format='json')
            
            # Assertions
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(response.data['success'])
            self.assertIn('catalog_urls', response.data)
    
    def test_background_generation_endpoint(self):
        """Test background generation API endpoint"""
        url = reverse('background-matcher-generate-background')
        data = {
            'fabric_image_url': 'https://example.com/fabric.jpg',
            'background_style': 'complementary',
            'pattern_type': 'seamless'
        }
        
        with patch('ai_services.background_matcher.BackgroundMatcher.generate_matching_background') as mock_generate:
            mock_generate.return_value = {
                'success': True,
                'background_urls': ['https://example.com/background1.png'],
                'fabric_analysis': {'success': True},
                'matching_score': 8.5
            }
            
            response = self.client.post(url, data, format='json')
            
            # Assertions
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(response.data['success'])
            self.assertIn('background_urls', response.data)
    
    def test_color_analysis_endpoint(self):
        """Test color analysis API endpoint"""
        url = reverse('background-matcher-analyze-colors')
        data = {
            'fabric_image_url': 'https://example.com/fabric.jpg'
        }
        
        with patch('ai_services.background_matcher.FabricColorDetector.analyze_fabric_colors') as mock_analyze:
            mock_analyze.return_value = {
                'success': True,
                'color_palette': [
                    {'hex': '#FF6B6B', 'name': 'Red', 'percentage': 50}
                ],
                'analysis': {
                    'dominant_colors': [],
                    'fabric_mood': {'mood': 'vibrant'}
                }
            }
            
            response = self.client.post(url, data, format='json')
            
            # Assertions
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(response.data['success'])
            self.assertIn('color_palette', response.data)


class IntegrationTestCase(TransactionTestCase):
    """Integration tests for complete workflows"""
    
    def setUp(self):
        """Set up test data"""
        self.organization = Organization.objects.create(
            name="Test Textile Shop",
            slug="test-textile-shop"
        )
        
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        
        self.provider = AIProvider.objects.create(
            name='nanobanana',
            api_key='test-api-key',
            is_active=True
        )
    
    def test_complete_poster_workflow(self):
        """Test complete poster generation workflow"""
        poster_generator = TextilePosterGenerator()
        
        # Step 1: Generate captions
        captions = poster_generator.generate_caption_suggestions(
            fabric_type='saree',
            festival='deepavali',
            price_range='₹2999'
        )
        
        self.assertGreater(len(captions), 0)
        
        # Step 2: Generate poster (mocked)
        with patch('ai_services.services.AIGenerationService.process_generation_request') as mock_process:
            mock_process.return_value = True
            
            with patch('ai_services.models.AIGenerationRequest.objects.create') as mock_create:
                mock_request = MagicMock()
                mock_request.id = 'test-123'
                mock_request.result_urls = ['https://example.com/poster.png']
                mock_request.cost = 0.05
                mock_create.return_value = mock_request
                
                result = poster_generator.generate_poster_with_caption(
                    organization=self.organization,
                    user=self.user,
                    fabric_type='saree',
                    festival='deepavali'
                )
                
                self.assertTrue(result['success'])
                self.assertIn('caption_suggestions', result)
                self.assertIn('poster_urls', result)
    
    def test_complete_catalog_workflow(self):
        """Test complete catalog building workflow"""
        catalog_builder = TextileCatalogBuilder()
        
        products = [
            {
                'name': 'Elegant Silk Saree',
                'fabric_type': 'silk',
                'color': 'golden',
                'price': '₹4999'
            }
        ]
        
        # Step 1: Generate product descriptions
        description_result = catalog_builder.generate_product_description(
            organization=self.organization,
            user=self.user,
            product_info=products[0]
        )
        
        self.assertTrue(description_result['success'])
        self.assertIn('description', description_result)
        
        # Step 2: Build complete catalog (mocked)
        with patch('ai_services.services.AIGenerationService.process_generation_request') as mock_process:
            mock_process.return_value = True
            
            with patch('ai_services.models.AIGenerationRequest.objects.create') as mock_create:
                mock_request = MagicMock()
                mock_request.id = 'catalog-123'
                mock_request.result_urls = ['https://example.com/catalog.png']
                mock_request.cost = 0.10
                mock_create.return_value = mock_request
                
                result = catalog_builder.build_catalog_with_ai_descriptions(
                    organization=self.organization,
                    user=self.user,
                    products=products
                )
                
                self.assertTrue(result['success'])
                self.assertIn('products', result)
                self.assertIn('catalog_urls', result)


if __name__ == '__main__':
    pytest.main([__file__])

