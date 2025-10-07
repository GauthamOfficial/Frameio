import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch
import json

from .models import AIProvider, AIGenerationRequest, AIUsageQuota, AITemplate
from organizations.models import Organization, OrganizationMember
from test_utils import TenantAPITestCase

User = get_user_model()


class AIProviderAPITest(APITestCase):
    """Test cases for AI Provider API endpoints"""
    
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
            is_active=True,
            rate_limit_per_minute=60
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_list_providers(self):
        """Test listing AI providers"""
        url = reverse('ai-provider-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'nanobanana')
    
    def test_list_providers_only_active(self):
        """Test that only active providers are listed"""
        # Create inactive provider
        AIProvider.objects.create(
            name='openai',
            is_active=False
        )
        
        url = reverse('ai-provider-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Only active provider
        
    def test_retrieve_provider(self):
        """Test retrieving specific provider"""
        url = reverse('ai-provider-detail', kwargs={'pk': self.provider.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'nanobanana')
        self.assertTrue(response.data['is_active'])


class AIGenerationRequestAPITest(APITestCase):
    """Test cases for AI Generation Request API endpoints"""
    
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
        
        # Mock organization context
        self.patcher = patch('ai_services.views.get_current_organization')
        self.mock_get_org = self.patcher.start()
        self.mock_get_org.return_value = self.organization
    
    def tearDown(self):
        self.patcher.stop()
    
    @patch('ai_services.views.AIGenerationService.process_generation_request')
    def test_create_generation_request(self, mock_process):
        """Test creating AI generation request"""
        mock_process.return_value = True
        
        url = reverse('ai-generation-request-list')
        data = {
            'provider': str(self.provider.pk),
            'generation_type': 'poster',
            'prompt': 'Create a beautiful textile design',
            'parameters': {'width': 1024, 'height': 1024}
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AIGenerationRequest.objects.count(), 1)
        
        request = AIGenerationRequest.objects.first()
        self.assertEqual(request.organization, self.organization)
        self.assertEqual(request.user, self.user)
        self.assertEqual(request.prompt, 'Create a beautiful textile design')
    
    def test_create_generation_request_invalid_prompt(self):
        """Test creating request with invalid prompt"""
        url = reverse('ai-generation-request-list')
        data = {
            'provider': str(self.provider.pk),
            'generation_type': 'poster',
            'prompt': '',  # Empty prompt
            'parameters': {}
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('prompt', response.data)
    
    def test_list_generation_requests(self):
        """Test listing generation requests"""
        # Create test request
        AIGenerationRequest.objects.create(
            organization=self.organization,
            user=self.user,
            provider=self.provider,
            generation_type='poster',
            prompt='Test prompt',
            status='completed'
        )
        
        url = reverse('ai-generation-request-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_filter_by_generation_type(self):
        """Test filtering requests by generation type"""
        # Create requests with different types
        AIGenerationRequest.objects.create(
            organization=self.organization,
            user=self.user,
            provider=self.provider,
            generation_type='poster',
            prompt='Poster prompt'
        )
        
        AIGenerationRequest.objects.create(
            organization=self.organization,
            user=self.user,
            provider=self.provider,
            generation_type='catalog',
            prompt='Catalog prompt'
        )
        
        url = reverse('ai-generation-request-list')
        response = self.client.get(url, {'generation_type': 'poster'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['generation_type'], 'poster')


class AITemplateAPITest(APITestCase):
    """Test cases for AI Template API endpoints"""
    
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
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Mock organization context
        self.patcher = patch('ai_services.views.get_current_organization')
        self.mock_get_org = self.patcher.start()
        self.mock_get_org.return_value = self.organization
    
    def tearDown(self):
        self.patcher.stop()
    
    def test_create_template(self):
        """Test creating AI template"""
        url = reverse('ai-template-list')
        data = {
            'name': 'Floral Template',
            'description': 'Beautiful floral patterns',
            'category': 'textile',
            'prompt_template': 'Create a {style} floral design',
            'negative_prompt_template': 'no text',
            'default_parameters': {'width': 1024}
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AITemplate.objects.count(), 1)
        
        template = AITemplate.objects.first()
        self.assertEqual(template.organization, self.organization)
        self.assertEqual(template.name, 'Floral Template')
    
    def test_list_templates_includes_public(self):
        """Test that template list includes public templates"""
        # Create organization template
        org_template = AITemplate.objects.create(
            organization=self.organization,
            name='Org Template',
            category='textile',
            prompt_template='Org prompt'
        )
        
        # Create public template
        public_template = AITemplate.objects.create(
            organization=None,
            name='Public Template',
            category='textile',
            prompt_template='Public prompt',
            is_public=True,
            is_active=True
        )
        
        url = reverse('ai-template-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_filter_templates_by_category(self):
        """Test filtering templates by category"""
        AITemplate.objects.create(
            organization=self.organization,
            name='Textile Template',
            category='textile',
            prompt_template='Textile prompt'
        )
        
        AITemplate.objects.create(
            organization=self.organization,
            name='Poster Template',
            category='poster',
            prompt_template='Poster prompt'
        )
        
        url = reverse('ai-template-list')
        response = self.client.get(url, {'category': 'textile'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['category'], 'textile')


class AIAnalyticsAPITest(TenantAPITestCase):
    """Test cases for AI Analytics API endpoints"""
    
    def setUp(self):
        super().setUp()
        
        self.provider = AIProvider.objects.create(
            name='nanobanana',
            is_active=True
        )
    
    def test_analytics_dashboard(self):
        """Test analytics dashboard endpoint"""
        # Create test data
        AIGenerationRequest.objects.create(
            organization=self.organization,
            user=self.user,
            provider=self.provider,
            generation_type='poster',
            prompt='Test prompt',
            status='completed',
            processing_time=2.5,
            cost=0.05
        )
        
        AIGenerationRequest.objects.create(
            organization=self.organization,
            user=self.user,
            provider=self.provider,
            generation_type='poster',
            prompt='Test prompt 2',
            status='failed'
        )
        
        url = reverse('ai-analytics-dashboard')
        response = self.client.get(url)
        
        # Debug: Print response details if test fails
        if response.status_code != status.HTTP_200_OK:
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.content}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data
        self.assertEqual(data['total_requests'], 2)
        self.assertEqual(data['successful_requests'], 1)
        self.assertEqual(data['failed_requests'], 1)
        self.assertEqual(data['success_rate'], 50.0)
        self.assertEqual(data['average_processing_time'], 2.5)
        self.assertEqual(float(data['total_cost']), 0.05)
    
    def test_analytics_dashboard_with_date_filter(self):
        """Test analytics dashboard with date filter"""
        url = reverse('ai-analytics-dashboard')
        response = self.client.get(url, {'days': 7})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return empty analytics for new organization
        self.assertEqual(response.data['total_requests'], 0)
