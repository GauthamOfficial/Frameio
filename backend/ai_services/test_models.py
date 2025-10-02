import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import timedelta
from django.utils import timezone

from .models import (
    AIProvider, AIGenerationRequest, AIUsageQuota, 
    AITemplate, AIGenerationHistory
)
from organizations.models import Organization, OrganizationMember

User = get_user_model()


class AIProviderModelTest(TestCase):
    """Test cases for AIProvider model"""
    
    def setUp(self):
        self.provider_data = {
            'name': 'nanobanana',
            'api_key': 'test_key_123',
            'api_url': 'https://api.nanobanana.com',
            'is_active': True,
            'rate_limit_per_minute': 60,
            'rate_limit_per_hour': 1000
        }
    
    def test_create_ai_provider(self):
        """Test creating an AI provider"""
        provider = AIProvider.objects.create(**self.provider_data)
        
        self.assertEqual(provider.name, 'nanobanana')
        self.assertEqual(provider.get_name_display(), 'NanoBanana')
        self.assertTrue(provider.is_active)
        self.assertEqual(provider.rate_limit_per_minute, 60)
        
    def test_ai_provider_str_representation(self):
        """Test string representation of AI provider"""
        provider = AIProvider.objects.create(**self.provider_data)
        expected_str = "NanoBanana - Active"
        self.assertEqual(str(provider), expected_str)
        
    def test_ai_provider_unique_name(self):
        """Test that provider names are unique"""
        AIProvider.objects.create(**self.provider_data)
        
        with self.assertRaises(Exception):
            AIProvider.objects.create(**self.provider_data)


class AIGenerationRequestModelTest(TestCase):
    """Test cases for AIGenerationRequest model"""
    
    def setUp(self):
        # Create test organization
        self.organization = Organization.objects.create(
            name="Test Org",
            slug="test-org",
            subscription_plan="pro"
        )
        
        # Create test user
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            clerk_id="test_clerk_123"
        )
        
        # Create organization member
        OrganizationMember.objects.create(
            organization=self.organization,
            user=self.user,
            role="admin"
        )
        
        # Create AI provider
        self.provider = AIProvider.objects.create(
            name='nanobanana',
            is_active=True
        )
        
        self.request_data = {
            'organization': self.organization,
            'user': self.user,
            'provider': self.provider,
            'generation_type': 'poster',
            'prompt': 'Create a beautiful textile design',
            'status': 'pending'
        }
    
    def test_create_ai_generation_request(self):
        """Test creating an AI generation request"""
        request = AIGenerationRequest.objects.create(**self.request_data)
        
        self.assertEqual(request.organization, self.organization)
        self.assertEqual(request.user, self.user)
        self.assertEqual(request.provider, self.provider)
        self.assertEqual(request.generation_type, 'poster')
        self.assertEqual(request.status, 'pending')
        
    def test_mark_completed(self):
        """Test marking request as completed"""
        request = AIGenerationRequest.objects.create(**self.request_data)
        
        result_data = {'test': 'data'}
        result_urls = ['http://example.com/image1.png']
        
        request.mark_completed(result_data, result_urls)
        
        self.assertEqual(request.status, 'completed')
        self.assertEqual(request.result_data, result_data)
        self.assertEqual(request.result_urls, result_urls)
        self.assertIsNotNone(request.completed_at)
        
    def test_mark_failed(self):
        """Test marking request as failed"""
        request = AIGenerationRequest.objects.create(**self.request_data)
        
        error_message = "API error occurred"
        request.mark_failed(error_message)
        
        self.assertEqual(request.status, 'failed')
        self.assertEqual(request.error_message, error_message)
        self.assertIsNotNone(request.completed_at)


class AIUsageQuotaModelTest(TestCase):
    """Test cases for AIUsageQuota model"""
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Org",
            slug="test-org"
        )
        
        self.provider = AIProvider.objects.create(
            name='nanobanana',
            is_active=True
        )
        
        self.quota_data = {
            'organization': self.organization,
            'provider': self.provider,
            'generation_type': 'poster',
            'quota_type': 'monthly',
            'max_requests': 100,
            'max_cost': 10.00,
            'reset_at': timezone.now() + timedelta(days=30)
        }
    
    def test_create_usage_quota(self):
        """Test creating usage quota"""
        quota = AIUsageQuota.objects.create(**self.quota_data)
        
        self.assertEqual(quota.organization, self.organization)
        self.assertEqual(quota.max_requests, 100)
        self.assertEqual(quota.current_requests, 0)
        self.assertFalse(quota.is_quota_exceeded())
        
    def test_increment_usage(self):
        """Test incrementing usage"""
        quota = AIUsageQuota.objects.create(**self.quota_data)
        
        quota.increment_usage(cost=1.50)
        
        self.assertEqual(quota.current_requests, 1)
        self.assertEqual(float(quota.current_cost), 1.50)
        
    def test_quota_exceeded(self):
        """Test quota exceeded detection"""
        quota = AIUsageQuota.objects.create(**self.quota_data)
        
        # Exceed request limit
        quota.current_requests = 101
        quota.save()
        self.assertTrue(quota.is_quota_exceeded())
        
        # Reset and exceed cost limit
        quota.current_requests = 50
        quota.current_cost = 11.00
        quota.save()
        self.assertTrue(quota.is_quota_exceeded())
        
    def test_reset_usage(self):
        """Test resetting usage"""
        quota = AIUsageQuota.objects.create(**self.quota_data)
        quota.current_requests = 50
        quota.current_cost = 5.00
        quota.save()
        
        quota.reset_usage()
        
        self.assertEqual(quota.current_requests, 0)
        self.assertEqual(float(quota.current_cost), 0.00)


class AITemplateModelTest(TestCase):
    """Test cases for AITemplate model"""
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Org",
            slug="test-org"
        )
        
        self.template_data = {
            'organization': self.organization,
            'name': 'Floral Design Template',
            'description': 'Beautiful floral patterns',
            'category': 'textile',
            'prompt_template': 'Create a {style} floral design with {colors}',
            'negative_prompt_template': 'no text, no watermarks',
            'default_parameters': {'width': 1024, 'height': 1024}
        }
    
    def test_create_template(self):
        """Test creating AI template"""
        template = AITemplate.objects.create(**self.template_data)
        
        self.assertEqual(template.name, 'Floral Design Template')
        self.assertEqual(template.category, 'textile')
        self.assertEqual(template.usage_count, 0)
        self.assertFalse(template.is_public)
        
    def test_increment_usage(self):
        """Test incrementing template usage"""
        template = AITemplate.objects.create(**self.template_data)
        
        template.increment_usage()
        self.assertEqual(template.usage_count, 1)
        
        template.increment_usage()
        self.assertEqual(template.usage_count, 2)
