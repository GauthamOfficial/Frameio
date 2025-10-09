"""
Comprehensive tests for AI integration with NanoBanana SDK
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.cache import cache

from ai_services.nanobanana_service import NanoBananaAIService, NanoBananaError
from ai_services.services import NanoBananaTextileService
from organizations.models import Organization
from ai_services.models import AIProvider

User = get_user_model()


class NanoBananaAIServiceTestCase(TestCase):
    """Test cases for NanoBananaAIService"""
    
    def setUp(self):
        """Set up test data"""
        self.service = NanoBananaAIService()
        self.test_image_url = "https://example.com/fabric.jpg"
        self.test_offer_text = "Special Deepavali Offer"
        self.test_theme = "festive"
        self.test_product_name = "Silk Saree"
        self.test_description = "Beautiful traditional silk saree"
    
    def tearDown(self):
        """Clean up after tests"""
        cache.clear()
    
    @patch('ai_services.nanobanana_service.NanoBananaClient')
    def test_service_initialization_with_api_key(self, mock_client_class):
        """Test service initialization with API key"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        with self.settings(NANOBANANA_API_KEY='test-api-key'):
            service = NanoBananaAIService()
            self.assertIsNotNone(service.client)
            mock_client_class.assert_called_once_with(api_key='test-api-key')
    
    @patch('ai_services.nanobanana_service.NanoBananaClient')
    def test_service_initialization_without_api_key(self, mock_client_class):
        """Test service initialization without API key"""
        with self.settings(NANOBANANA_API_KEY=''):
            service = NanoBananaAIService()
            self.assertIsNone(service.client)
            mock_client_class.assert_not_called()
    
    def test_is_available_with_client(self):
        """Test is_available method when client is available"""
        self.service.client = Mock()
        self.service.api_key = 'test-key'
        self.assertTrue(self.service.is_available())
    
    def test_is_available_without_client(self):
        """Test is_available method when client is not available"""
        self.service.client = None
        self.service.api_key = None
        self.assertFalse(self.service.is_available())
    
    @patch('ai_services.nanobanana_service.cache')
    def test_get_cached_result(self, mock_cache):
        """Test getting cached result"""
        mock_cache.get.return_value = {'cached': True, 'data': 'test'}
        result = self.service.get_cached_result('test_key')
        self.assertEqual(result['cached'], True)
        self.assertEqual(result['data'], 'test')
    
    @patch('ai_services.nanobanana_service.cache')
    def test_get_cached_result_not_found(self, mock_cache):
        """Test getting cached result when not found"""
        mock_cache.get.return_value = None
        result = self.service.get_cached_result('test_key')
        self.assertIsNone(result)
    
    def test_create_poster_prompt(self):
        """Test poster prompt creation"""
        prompt = self.service._create_poster_prompt(
            self.test_image_url, self.test_offer_text, self.test_theme
        )
        self.assertIn(self.test_offer_text, prompt)
        self.assertIn(self.test_theme, prompt)
        self.assertIn("textile poster", prompt.lower())
    
    def test_create_caption_prompt(self):
        """Test caption prompt creation"""
        prompt = self.service._create_caption_prompt(
            self.test_product_name, self.test_description
        )
        self.assertIn(self.test_product_name, prompt)
        self.assertIn(self.test_description, prompt)
        self.assertIn("social media captions", prompt.lower())
    
    def test_parse_captions(self):
        """Test caption parsing"""
        test_text = """Caption 1: Beautiful silk saree for special occasions ✨
        Caption 2: Elegant traditional wear #Fashion
        Caption 3: Premium quality silk fabric"""
        
        captions = self.service._parse_captions(test_text)
        self.assertGreater(len(captions), 0)
        self.assertIn('text', captions[0])
        self.assertIn('tone', captions[0])
        self.assertIn('effectiveness_score', captions[0])
    
    def test_determine_tone(self):
        """Test tone determination"""
        marketing_text = "Special sale offer! Get 50% off!"
        elegant_text = "Elegant luxury silk saree"
        casual_text = "Comfortable everyday wear"
        
        self.assertEqual(self.service._determine_tone(marketing_text), 'marketing')
        self.assertEqual(self.service._determine_tone(elegant_text), 'elegant')
        self.assertEqual(self.service._determine_tone(casual_text), 'casual')
    
    def test_calculate_effectiveness_score(self):
        """Test effectiveness score calculation"""
        good_caption = "Beautiful silk saree ✨ #Fashion #Style"
        score = self.service._calculate_effectiveness_score(good_caption)
        self.assertGreater(score, 5.0)
        self.assertLessEqual(score, 10.0)
    
    def test_extract_hashtags(self):
        """Test hashtag extraction"""
        text = "Beautiful saree #Fashion #Style #Textile"
        hashtags = self.service._extract_hashtags(text)
        self.assertIn('#Fashion', hashtags)
        self.assertIn('#Style', hashtags)
        self.assertIn('#Textile', hashtags)
    
    def test_get_fallback_poster_result(self):
        """Test fallback poster result"""
        result = self.service._get_fallback_poster_result(
            self.test_image_url, self.test_offer_text, self.test_theme
        )
        self.assertTrue(result['success'])
        self.assertTrue(result['fallback'])
        self.assertIn('image_urls', result)
        self.assertEqual(result['theme'], self.test_theme)
    
    def test_get_fallback_caption_result(self):
        """Test fallback caption result"""
        result = self.service._get_fallback_caption_result(
            self.test_product_name, self.test_description
        )
        self.assertTrue(result['success'])
        self.assertTrue(result['fallback'])
        self.assertIn('captions', result)
        self.assertEqual(result['product_name'], self.test_product_name)


class NanoBananaTextileServiceTestCase(TestCase):
    """Test cases for NanoBananaTextileService"""
    
    def setUp(self):
        """Set up test data"""
        self.service = NanoBananaTextileService()
        self.test_image_url = "https://example.com/fabric.jpg"
        self.test_offer_text = "Special Deepavali Offer"
        self.test_theme = "festive"
        self.test_fabric_type = "silk"
        self.test_festival = "deepavali"
    
    @patch.object(NanoBananaAIService, 'generate_poster')
    def test_generate_textile_poster(self, mock_generate_poster):
        """Test textile poster generation"""
        mock_generate_poster.return_value = {
            'success': True,
            'image_urls': ['https://example.com/poster.jpg'],
            'prompt_used': 'test prompt'
        }
        
        result = self.service.generate_textile_poster(
            image_url=self.test_image_url,
            offer_text=self.test_offer_text,
            theme=self.test_theme,
            fabric_type=self.test_fabric_type,
            festival=self.test_festival
        )
        
        self.assertTrue(result['success'])
        self.assertTrue(result['textile_specific'])
        self.assertEqual(result['fabric_type'], self.test_fabric_type)
        self.assertEqual(result['festival'], self.test_festival)
        mock_generate_poster.assert_called_once()
    
    @patch.object(NanoBananaAIService, 'generate_caption')
    def test_generate_textile_caption(self, mock_generate_caption):
        """Test textile caption generation"""
        mock_generate_caption.return_value = {
            'success': True,
            'captions': [{'text': 'Beautiful silk saree', 'tone': 'elegant'}]
        }
        
        result = self.service.generate_textile_caption(
            product_name="Silk Saree",
            description="Beautiful traditional silk saree",
            fabric_type="silk",
            price_range="₹2999"
        )
        
        self.assertTrue(result['success'])
        self.assertTrue(result['textile_specific'])
        self.assertEqual(result['fabric_type'], 'silk')
        self.assertEqual(result['price_range'], '₹2999')
        mock_generate_caption.assert_called_once()
    
    def test_enhance_theme_for_textile(self):
        """Test theme enhancement for textile"""
        enhanced_theme = self.service._enhance_theme_for_textile(
            "modern", "silk", "deepavali"
        )
        self.assertIn("modern", enhanced_theme)
        self.assertIn("silk", enhanced_theme.lower())
        self.assertIn("deepavali", enhanced_theme.lower())
    
    def test_enhance_description_for_textile(self):
        """Test description enhancement for textile"""
        enhanced_description = self.service._enhance_description_for_textile(
            "Beautiful saree", "silk", "₹2999"
        )
        self.assertIn("Beautiful saree", enhanced_description)
        self.assertIn("silk", enhanced_description.lower())
        self.assertIn("₹2999", enhanced_description)


class NanoBananaAPITestCase(APITestCase):
    """Test cases for NanoBanana API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.organization = Organization.objects.create(
            name='Test Organization',
            slug='test-org'
        )
        self.user.organization_memberships.create(
            organization=self.organization,
            role='admin',
            is_active=True
        )
        
        # Create AI provider
        self.ai_provider = AIProvider.objects.create(
            name='nanobanana',
            api_key='test-api-key',
            is_active=True
        )
        
        self.client.force_authenticate(user=self.user)
    
    def tearDown(self):
        """Clean up after tests"""
        cache.clear()
    
    @patch('ai_services.textile_views.NanoBananaTextileService')
    def test_generate_poster_nanobanana_endpoint(self, mock_service_class):
        """Test NanoBanana poster generation endpoint"""
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.generate_textile_poster.return_value = {
            'success': True,
            'image_urls': ['https://example.com/poster.jpg'],
            'prompt_used': 'test prompt',
            'generation_id': 'test_id',
            'cost': 0.05,
            'cached': False,
            'fallback': False
        }
        
        # Mock Arcjet service
        with patch('ai_services.textile_views.ArcjetService') as mock_arcjet:
            mock_arcjet_instance = Mock()
            mock_arcjet.return_value = mock_arcjet_instance
            mock_arcjet_instance.check_usage_limit.return_value = {'within_limits': True}
            mock_arcjet_instance.increment_usage.return_value = None
            
            response = self.client.post('/api/ai/textile/poster/generate_poster_nanobanana/', {
                'image_url': 'https://example.com/fabric.jpg',
                'offer_text': 'Special Offer',
                'theme': 'modern',
                'fabric_type': 'silk',
                'festival': 'deepavali'
            })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('image_urls', data)
        self.assertIn('metadata', data)
    
    @patch('ai_services.textile_views.NanoBananaTextileService')
    def test_generate_caption_nanobanana_endpoint(self, mock_service_class):
        """Test NanoBanana caption generation endpoint"""
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.generate_textile_caption.return_value = {
            'success': True,
            'captions': [
                {'text': 'Beautiful silk saree', 'tone': 'elegant', 'effectiveness_score': 8.5}
            ],
            'prompt_used': 'test prompt',
            'generation_id': 'test_id',
            'cost': 0.05,
            'cached': False,
            'fallback': False
        }
        
        # Mock Arcjet service
        with patch('ai_services.textile_views.ArcjetService') as mock_arcjet:
            mock_arcjet_instance = Mock()
            mock_arcjet.return_value = mock_arcjet_instance
            mock_arcjet_instance.check_usage_limit.return_value = {'within_limits': True}
            mock_arcjet_instance.increment_usage.return_value = None
            
            response = self.client.post('/api/ai/textile/caption/generate_caption_nanobanana/', {
                'product_name': 'Silk Saree',
                'description': 'Beautiful traditional silk saree',
                'fabric_type': 'silk',
                'price_range': '₹2999'
            })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('captions', data)
        self.assertIn('metadata', data)
    
    def test_generate_poster_nanobanana_missing_image_url(self):
        """Test poster generation with missing image URL"""
        response = self.client.post('/api/ai/textile/poster/generate_poster_nanobanana/', {
            'offer_text': 'Special Offer',
            'theme': 'modern'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('image_url is required', response.json()['error'])
    
    def test_generate_caption_nanobanana_missing_product_name(self):
        """Test caption generation with missing product name"""
        response = self.client.post('/api/ai/textile/caption/generate_caption_nanobanana/', {
            'description': 'Beautiful silk saree',
            'fabric_type': 'silk'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('product_name is required', response.json()['error'])
    
    @patch('ai_services.textile_views.ArcjetService')
    def test_usage_limit_exceeded(self, mock_arcjet):
        """Test usage limit exceeded scenario"""
        mock_arcjet_instance = Mock()
        mock_arcjet.return_value = mock_arcjet_instance
        mock_arcjet_instance.check_usage_limit.return_value = {
            'within_limits': False,
            'plan': 'basic',
            'monthly_exceeded': True,
            'daily_exceeded': False,
            'remaining_monthly': 0,
            'remaining_daily': 5
        }
        
        response = self.client.post('/api/ai/textile/poster/generate_poster_nanobanana/', {
            'image_url': 'https://example.com/fabric.jpg',
            'offer_text': 'Special Offer',
            'theme': 'modern'
        })
        
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        data = response.json()
        self.assertIn('Usage limit exceeded', data['error'])


class NanoBananaIntegrationTestCase(TestCase):
    """Integration tests for NanoBanana SDK"""
    
    def setUp(self):
        """Set up test data"""
        self.service = NanoBananaAIService()
    
    def tearDown(self):
        """Clean up after tests"""
        cache.clear()
    
    @patch('ai_services.nanobanana_service.NanoBananaClient')
    def test_poster_generation_with_mock_client(self, mock_client_class):
        """Test poster generation with mocked client"""
        # Mock the client and its response
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_image = Mock()
        mock_image.url = 'https://example.com/generated_poster.jpg'
        mock_result = Mock()
        mock_result.images = [mock_image]
        mock_client.generate_image.return_value = mock_result
        
        with self.settings(NANOBANANA_API_KEY='test-api-key'):
            service = NanoBananaAIService()
            result = service.generate_poster(
                image_url='https://example.com/fabric.jpg',
                offer_text='Special Offer',
                theme='modern'
            )
        
        self.assertTrue(result['success'])
        self.assertIn('image_urls', result)
        self.assertEqual(len(result['image_urls']), 1)
        self.assertEqual(result['image_urls'][0], 'https://example.com/generated_poster.jpg')
    
    @patch('ai_services.nanobanana_service.NanoBananaClient')
    def test_caption_generation_with_mock_client(self, mock_client_class):
        """Test caption generation with mocked client"""
        # Mock the client and its response
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_result = Mock()
        mock_result.text = """Caption 1: Beautiful silk saree for special occasions ✨ #Fashion #Style
        Caption 2: Elegant traditional wear #Luxury #Textile
        Caption 3: Premium quality silk fabric #Quality #Fashion"""
        mock_client.generate_text.return_value = mock_result
        
        with self.settings(NANOBANANA_API_KEY='test-api-key'):
            service = NanoBananaAIService()
            result = service.generate_caption(
                product_name='Silk Saree',
                description='Beautiful traditional silk saree'
            )
        
        self.assertTrue(result['success'])
        self.assertIn('captions', result)
        self.assertGreater(len(result['captions']), 0)
        self.assertIn('text', result['captions'][0])
        self.assertIn('tone', result['captions'][0])
    
    def test_fallback_mechanism(self):
        """Test fallback mechanism when API is unavailable"""
        # Test with no API key
        with self.settings(NANOBANANA_API_KEY=''):
            service = NanoBananaAIService()
            result = service.generate_poster(
                image_url='https://example.com/fabric.jpg',
                offer_text='Special Offer',
                theme='modern'
            )
        
        self.assertTrue(result['success'])
        self.assertTrue(result['fallback'])
        self.assertIn('image_urls', result)
    
    def test_caching_mechanism(self):
        """Test caching mechanism"""
        # Mock cache
        with patch('ai_services.nanobanana_service.cache') as mock_cache:
            mock_cache.get.return_value = None  # No cached result
            mock_cache.set.return_value = None
            
            # Mock client
            with patch('ai_services.nanobanana_service.NanoBananaClient'):
                service = NanoBananaAIService()
                service.client = Mock()
                service.client.generate_image.return_value = Mock(images=[Mock(url='test.jpg')])
                
                result = service.generate_poster(
                    image_url='https://example.com/fabric.jpg',
                    offer_text='Special Offer',
                    theme='modern'
                )
            
            # Verify cache was called
            mock_cache.get.assert_called_once()
            mock_cache.set.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__])

