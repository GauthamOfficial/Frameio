import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock

from .models import AIProvider, AIGenerationRequest
from .services import AIGenerationService, AIPromptEngineeringService, AIColorAnalysisService
from organizations.models import Organization

User = get_user_model()


class AIGenerationServiceTest(TestCase):
    """Test cases for AIGenerationService"""
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Org",
            slug="test-org"
        )
        
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            clerk_id="test_clerk_123"
        )
        
        self.provider = AIProvider.objects.create(
            name='nanobanana',
            is_active=True
        )
        
        self.request = AIGenerationRequest.objects.create(
            organization=self.organization,
            user=self.user,
            provider=self.provider,
            generation_type='poster',
            prompt='Test prompt',
            status='pending'
        )
        
        self.service = AIGenerationService()
    
    @patch('ai_services.services.AIGenerationService._process_nanobanana_request')
    def test_process_generation_request_success(self, mock_process):
        """Test successful generation request processing"""
        mock_result = {
            'data': {'test': 'data'},
            'urls': ['http://example.com/image.png'],
            'cost': 0.05
        }
        mock_process.return_value = mock_result
        
        result = self.service.process_generation_request(self.request)
        
        self.assertTrue(result)
        self.request.refresh_from_db()
        self.assertEqual(self.request.status, 'completed')
        self.assertEqual(self.request.result_data, mock_result['data'])
        self.assertEqual(self.request.result_urls, mock_result['urls'])
        
    @patch('ai_services.services.AIGenerationService._process_nanobanana_request')
    def test_process_generation_request_failure(self, mock_process):
        """Test failed generation request processing"""
        mock_process.side_effect = Exception("API Error")
        
        result = self.service.process_generation_request(self.request)
        
        self.assertFalse(result)
        self.request.refresh_from_db()
        self.assertEqual(self.request.status, 'failed')
        self.assertIn("API Error", self.request.error_message)
    
    def test_process_nanobanana_request_mock(self):
        """Test NanoBanana request processing (mock implementation)"""
        result = self.service._process_nanobanana_request(self.request)
        
        self.assertIn('data', result)
        self.assertIn('urls', result)
        self.assertIn('cost', result)
        self.assertIsInstance(result['urls'], list)
        self.assertGreater(len(result['urls']), 0)


class AIPromptEngineeringServiceTest(TestCase):
    """Test cases for AIPromptEngineeringService"""
    
    def test_enhance_textile_prompt(self):
        """Test textile prompt enhancement"""
        base_prompt = "Create a beautiful pattern"
        
        enhanced = AIPromptEngineeringService.enhance_textile_prompt(
            base_prompt=base_prompt,
            fabric_type="cotton",
            color_scheme="blue and white",
            style="modern"
        )
        
        self.assertIn(base_prompt, enhanced)
        self.assertIn("cotton", enhanced)
        self.assertIn("blue and white", enhanced)
        self.assertIn("modern", enhanced)
        self.assertIn("high quality textile design", enhanced)
    
    def test_enhance_textile_prompt_minimal(self):
        """Test textile prompt enhancement with minimal parameters"""
        base_prompt = "Simple pattern"
        
        enhanced = AIPromptEngineeringService.enhance_textile_prompt(
            base_prompt=base_prompt
        )
        
        self.assertIn(base_prompt, enhanced)
        self.assertIn("high quality textile design", enhanced)
        
    def test_generate_negative_prompt(self):
        """Test negative prompt generation"""
        negative_prompt = AIPromptEngineeringService.generate_negative_prompt('poster')
        
        self.assertIn("low quality", negative_prompt)
        self.assertIn("text", negative_prompt)
        self.assertIn("watermark", negative_prompt)
    
    def test_generate_negative_prompt_unknown_type(self):
        """Test negative prompt generation for unknown type"""
        negative_prompt = AIPromptEngineeringService.generate_negative_prompt('unknown_type')
        
        self.assertIn("low quality", negative_prompt)
        self.assertIn("blurry", negative_prompt)


class AIColorAnalysisServiceTest(TestCase):
    """Test cases for AIColorAnalysisService"""
    
    def test_extract_color_palette(self):
        """Test color palette extraction"""
        image_url = "http://example.com/image.jpg"
        
        palette = AIColorAnalysisService.extract_color_palette(image_url)
        
        self.assertIsInstance(palette, list)
        self.assertGreater(len(palette), 0)
        
        # Check first color structure
        color = palette[0]
        self.assertIn('hex', color)
        self.assertIn('rgb', color)
        self.assertIn('name', color)
        self.assertIn('percentage', color)
        
        # Validate hex format
        self.assertTrue(color['hex'].startswith('#'))
        self.assertEqual(len(color['hex']), 7)
        
        # Validate RGB format
        self.assertIsInstance(color['rgb'], list)
        self.assertEqual(len(color['rgb']), 3)
        
    def test_suggest_complementary_colors(self):
        """Test complementary color suggestions"""
        base_colors = ['#FF6B6B', '#4ECDC4']
        
        suggestions = AIColorAnalysisService.suggest_complementary_colors(base_colors)
        
        self.assertIsInstance(suggestions, list)
        self.assertGreater(len(suggestions), 0)
        
        # Check suggestion structure
        suggestion = suggestions[0]
        self.assertIn('hex', suggestion)
        self.assertIn('name', suggestion)
        self.assertIn('relationship', suggestion)
        
        # Validate relationship types
        valid_relationships = ['complementary', 'triadic', 'analogous']
        self.assertIn(suggestion['relationship'], valid_relationships)
