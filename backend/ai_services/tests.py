"""
Comprehensive test suite for AI Services
"""
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch
from datetime import timedelta
from django.utils import timezone

from .models import AIProvider, AIGenerationRequest, AIUsageQuota, AITemplate
from .services import AIGenerationService, AIPromptEngineeringService
from organizations.models import Organization, OrganizationMember

User = get_user_model()


class AIProviderTest(TestCase):
    """Test AIProvider model"""
    
    def test_create_provider(self):
        """Test creating AI provider"""
        provider = AIProvider.objects.create(
            name='nanobanana',
            is_active=True,
            rate_limit_per_minute=60
        )
        
        self.assertEqual(provider.get_name_display(), 'NanoBanana')
        self.assertTrue(provider.is_active)
        self.assertEqual(str(provider), "NanoBanana - Active")


class AIGenerationRequestTest(TestCase):
    """Test AIGenerationRequest model"""
    
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
    
    def test_create_request(self):
        """Test creating generation request"""
        request = AIGenerationRequest.objects.create(
            organization=self.organization,
            user=self.user,
            provider=self.provider,
            generation_type='poster',
            prompt='Test prompt',
            status='pending'
        )
        
        self.assertEqual(request.organization, self.organization)
        self.assertEqual(request.status, 'pending')
    
    def test_mark_completed(self):
        """Test marking request as completed"""
        request = AIGenerationRequest.objects.create(
            organization=self.organization,
            user=self.user,
            provider=self.provider,
            generation_type='poster',
            prompt='Test prompt'
        )
        
        result_data = {'test': 'data'}
        result_urls = ['http://example.com/image.png']
        request.mark_completed(result_data, result_urls)
        
        self.assertEqual(request.status, 'completed')
        self.assertEqual(request.result_data, result_data)
        self.assertIsNotNone(request.completed_at)


class AIUsageQuotaTest(TestCase):
    """Test AIUsageQuota model"""
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Org",
            slug="test-org"
        )
        
        self.provider = AIProvider.objects.create(
            name='nanobanana',
            is_active=True
        )
    
    def test_quota_management(self):
        """Test quota creation and management"""
        quota = AIUsageQuota.objects.create(
            organization=self.organization,
            provider=self.provider,
            generation_type='poster',
            quota_type='monthly',
            max_requests=100,
            max_cost=10.00,
            reset_at=timezone.now() + timedelta(days=30)
        )
        
        self.assertFalse(quota.is_quota_exceeded())
        
        quota.increment_usage(cost=1.50)
        self.assertEqual(quota.current_requests, 1)
        self.assertEqual(float(quota.current_cost), 1.50)


class AITemplateTest(TestCase):
    """Test AITemplate model"""
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Org",
            slug="test-org"
        )
    
    def test_create_template(self):
        """Test creating AI template"""
        template = AITemplate.objects.create(
            organization=self.organization,
            name='Floral Template',
            category='textile',
            prompt_template='Create a {style} design',
            default_parameters={'width': 1024}
        )
        
        self.assertEqual(template.name, 'Floral Template')
        self.assertEqual(template.usage_count, 0)
        
        template.increment_usage()
        self.assertEqual(template.usage_count, 1)


class AIServicesTest(TestCase):
    """Test AI service classes"""
    
    def test_prompt_enhancement(self):
        """Test prompt enhancement service"""
        enhanced = AIPromptEngineeringService.enhance_textile_prompt(
            base_prompt="Simple pattern",
            fabric_type="cotton",
            color_scheme="blue and white"
        )
        
        self.assertIn("Simple pattern", enhanced)
        self.assertIn("cotton", enhanced)
        self.assertIn("blue and white", enhanced)
        self.assertIn("high quality textile design", enhanced)
    
    def test_negative_prompt_generation(self):
        """Test negative prompt generation"""
        negative = AIPromptEngineeringService.generate_negative_prompt('poster')
        
        self.assertIn("low quality", negative)
        self.assertIn("text", negative)


class AIAPITest(APITestCase):
    """Test AI API endpoints"""
    
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
        
        OrganizationMember.objects.create(
            organization=self.organization,
            user=self.user,
            role="admin"
        )
        
        self.provider = AIProvider.objects.create(
            name='nanobanana',
            is_active=True
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_list_providers(self):
        """Test listing AI providers"""
        url = reverse('ai-provider-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    @patch('ai_services.views.get_current_organization')
    @patch('ai_services.views.AIGenerationService.process_generation_request')
    def test_create_generation_request(self, mock_process, mock_get_org):
        """Test creating generation request"""
        mock_get_org.return_value = self.organization
        mock_process.return_value = True
        
        url = reverse('ai-generation-request-list')
        data = {
            'provider': str(self.provider.pk),
            'generation_type': 'poster',
            'prompt': 'Create a design',
            'parameters': {'width': 1024}
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AIGenerationRequest.objects.count(), 1)


@pytest.mark.django_db
class TestAIIntegration:
    """Integration tests using pytest"""
    
    def setup_method(self):
        """Set up test data"""
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
    
    def test_complete_workflow(self):
        """Test complete AI generation workflow"""
        # Create request
        request = AIGenerationRequest.objects.create(
            organization=self.organization,
            user=self.user,
            provider=self.provider,
            generation_type='poster',
            prompt='Test prompt',
            status='pending'
        )
        
        # Process request
        service = AIGenerationService()
        result = service.process_generation_request(request)
        
        # Verify results
        assert result is True
        request.refresh_from_db()
        assert request.status == 'completed'
        assert len(request.result_urls) > 0