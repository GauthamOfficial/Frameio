"""
Comprehensive test suite for Phase 1 Week 4 backend features:
- AI poster generation
- Design export and download
- Collaboration features
- Caching functionality
"""

import pytest
import json
import uuid
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.utils import timezone
from datetime import timedelta

from organizations.models import Organization, OrganizationMember
from designs.models import Design
from poster_generation.models import PosterGenerationJob, PosterTemplate
from design_export.models import ExportJob, ExportTemplate
from collaboration.models import DesignShare, DesignComment, DesignCollaboration
from ai_services.caching import ai_cache_service, design_cache_service

User = get_user_model()


class TestAIPosterGeneration(APITestCase):
    """Test AI poster generation functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create test organization
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        
        # Create test user
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User"
        )
        
        # Add user to organization
        OrganizationMember.objects.create(
            user=self.user,
            organization=self.organization,
            role="admin",
            is_active=True
        )
        
        # Set current organization
        self.user.current_organization = self.organization
        self.user.save()
        
        # Authenticate user
        self.client.force_authenticate(user=self.user)
    
    @patch('poster_generation.services.NanoBananaPosterService.generate_poster')
    def test_generate_poster_success(self, mock_generate):
        """Test successful poster generation"""
        # Mock successful AI generation
        mock_generate.return_value = {
            'success': True,
            'generated_images': ['https://example.com/image1.png'],
            'processing_time': 15.5,
            'cost': 0.05
        }
        
        url = reverse('poster-api-generate-poster')
        data = {
            'prompt': 'A beautiful textile design',
            'width': 1024,
            'height': 1024,
            'num_images': 1
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('job_id', response.data)
        
        # Verify job was created
        job_id = response.data['job_id']
        job = PosterGenerationJob.objects.get(id=job_id)
        self.assertEqual(job.prompt, data['prompt'])
        self.assertEqual(job.status, 'completed')
    
    def test_generate_poster_invalid_data(self):
        """Test poster generation with invalid data"""
        url = reverse('poster-api-generate-poster')
        data = {
            'prompt': '',  # Empty prompt
            'width': 50,   # Invalid width
            'height': 50   # Invalid height
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('prompt', response.data)
        self.assertIn('width', response.data)
    
    def test_get_poster_templates(self):
        """Test getting poster templates"""
        # Create test template
        PosterTemplate.objects.create(
            organization=self.organization,
            name="Test Template",
            description="A test template",
            category="textile",
            prompt_template="Create a {style} textile design",
            created_by=self.user
        )
        
        url = reverse('poster-api-templates')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['templates']), 1)
    
    def test_poster_generation_analytics(self):
        """Test poster generation analytics"""
        # Create test jobs
        PosterGenerationJob.objects.create(
            organization=self.organization,
            user=self.user,
            prompt="Test prompt",
            status='completed',
            processing_time=10.5,
            cost=0.03
        )
        
        url = reverse('poster-api-analytics')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['analytics']['total_jobs'], 1)
        self.assertEqual(response.data['analytics']['completed_jobs'], 1)


class TestDesignExport(APITestCase):
    """Test design export functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create test organization
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        
        # Create test user
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User"
        )
        
        # Add user to organization
        OrganizationMember.objects.create(
            user=self.user,
            organization=self.organization,
            role="admin",
            is_active=True
        )
        
        # Set current organization
        self.user.current_organization = self.organization
        self.user.save()
        
        # Create test design
        self.design = Design.objects.create(
            organization=self.organization,
            title="Test Design",
            description="A test design",
            created_by=self.user
        )
        
        # Authenticate user
        self.client.force_authenticate(user=self.user)
    
    @patch('design_export.services.DesignExportService._export_as_images')
    def test_export_designs_success(self, mock_export):
        """Test successful design export"""
        # Mock successful export
        mock_export.return_value = {
            'success': True,
            'file_path': '/tmp/export.png',
            'download_url': 'http://example.com/download.png',
            'file_size': 1024000,
            'processing_time': 5.2
        }
        
        url = reverse('export-api-export-designs')
        data = {
            'design_ids': [str(self.design.id)],
            'export_format': 'png'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('job_id', response.data)
        
        # Verify job was created
        job_id = response.data['job_id']
        job = ExportJob.objects.get(id=job_id)
        self.assertEqual(job.export_format, 'png')
        self.assertEqual(job.status, 'completed')
    
    def test_export_designs_invalid_data(self):
        """Test design export with invalid data"""
        url = reverse('export-api-export-designs')
        data = {
            'design_ids': [],  # Empty list
            'export_format': 'invalid'  # Invalid format
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('design_ids', response.data)
        self.assertIn('export_format', response.data)
    
    def test_get_export_templates(self):
        """Test getting export templates"""
        # Create test template
        ExportTemplate.objects.create(
            organization=self.organization,
            name="Test Export Template",
            description="A test export template",
            template_type="single",
            export_format="png",
            created_by=self.user
        )
        
        url = reverse('export-api-templates')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['templates']), 1)
    
    def test_export_analytics(self):
        """Test export analytics"""
        # Create test export job
        ExportJob.objects.create(
            organization=self.organization,
            user=self.user,
            design_ids=[str(self.design.id)],
            export_format='png',
            status='completed',
            file_size=1024000,
            processing_time=5.2
        )
        
        url = reverse('export-api-analytics')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['analytics']['total_jobs'], 1)
        self.assertEqual(response.data['analytics']['completed_jobs'], 1)


class TestCollaborationFeatures(APITestCase):
    """Test collaboration functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create test organization
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        
        # Create test users
        self.user1 = User.objects.create_user(
            email="user1@example.com",
            password="testpass123",
            first_name="User",
            last_name="One"
        )
        
        self.user2 = User.objects.create_user(
            email="user2@example.com",
            password="testpass123",
            first_name="User",
            last_name="Two"
        )
        
        # Add users to organization
        OrganizationMember.objects.create(
            user=self.user1,
            organization=self.organization,
            role="admin",
            is_active=True
        )
        
        OrganizationMember.objects.create(
            user=self.user2,
            organization=self.organization,
            role="designer",
            is_active=True
        )
        
        # Set current organization
        self.user1.current_organization = self.organization
        self.user1.save()
        
        self.user2.current_organization = self.organization
        self.user2.save()
        
        # Create test design
        self.design = Design.objects.create(
            organization=self.organization,
            title="Test Design",
            description="A test design",
            created_by=self.user1
        )
        
        # Authenticate user1
        self.client.force_authenticate(user=self.user1)
    
    def test_share_design_success(self):
        """Test successful design sharing"""
        url = reverse('collaboration-api-share-design')
        data = {
            'design_id': str(self.design.id),
            'shared_with_email': self.user2.email,
            'access_level': 'edit',
            'allow_download': True,
            'allow_comments': True,
            'message': 'Please review this design'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['access_level'], 'edit')
        self.assertEqual(response.data['shared_with'], self.user2.id)
        
        # Verify share was created
        share = DesignShare.objects.get(design=self.design, shared_with=self.user2)
        self.assertEqual(share.access_level, 'edit')
        self.assertTrue(share.allow_download)
    
    def test_share_design_public(self):
        """Test public design sharing"""
        url = reverse('collaboration-api-share-design')
        data = {
            'design_id': str(self.design.id),
            'is_public': True,
            'access_level': 'view',
            'allow_download': False
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['is_public'])
        self.assertIsNotNone(response.data['share_token'])
    
    def test_add_comment_success(self):
        """Test successful comment addition"""
        url = reverse('collaboration-api-add-comment')
        data = {
            'design_id': str(self.design.id),
            'content': 'This is a great design!'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'This is a great design!')
        self.assertEqual(response.data['author'], self.user1.id)
        
        # Verify comment was created
        comment = DesignComment.objects.get(design=self.design, author=self.user1)
        self.assertEqual(comment.content, 'This is a great design!')
    
    def test_start_collaboration_success(self):
        """Test successful collaboration start"""
        url = reverse('collaboration-api-start-collaboration')
        data = {
            'design_id': str(self.design.id),
            'allow_edit': True,
            'allow_comments': True,
            'auto_save': True
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['initiator'], self.user1.id)
        self.assertEqual(response.data['status'], 'active')
        
        # Verify collaboration was created
        collaboration = DesignCollaboration.objects.get(design=self.design, initiator=self.user1)
        self.assertTrue(collaboration.allow_edit)
        self.assertTrue(collaboration.allow_comments)
    
    def test_join_collaboration_success(self):
        """Test successful collaboration join"""
        # Create collaboration
        collaboration = DesignCollaboration.objects.create(
            organization=self.organization,
            design=self.design,
            initiator=self.user1,
            allow_edit=True,
            allow_comments=True
        )
        
        # Switch to user2
        self.client.force_authenticate(user=self.user2)
        
        url = reverse('collaboration-api-join-collaboration')
        data = {
            'collaboration_id': str(collaboration.id)
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify user2 was added to collaboration
        collaboration.refresh_from_db()
        self.assertIn(self.user2, collaboration.participants.all())
    
    def test_get_activity(self):
        """Test getting design activity"""
        # Create some activity
        DesignComment.objects.create(
            organization=self.organization,
            design=self.design,
            author=self.user1,
            content="Test comment"
        )
        
        url = reverse('collaboration-api-activity')
        response = self.client.get(url, {'design_id': str(self.design.id)})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)


class TestCachingFunctionality(TestCase):
    """Test caching functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.test_prompt = "A beautiful textile design"
        self.test_parameters = {
            'width': 1024,
            'height': 1024,
            'num_images': 1
        }
        self.test_result = {
            'success': True,
            'generated_images': ['https://example.com/image1.png'],
            'processing_time': 15.5,
            'cost': 0.05
        }
    
    def test_ai_cache_set_and_get(self):
        """Test AI cache set and get operations"""
        # Test cache miss
        result = ai_cache_service.get_cached_result(self.test_prompt, self.test_parameters)
        self.assertIsNone(result)
        
        # Test cache set
        success = ai_cache_service.cache_result(
            self.test_prompt, 
            self.test_parameters, 
            self.test_result
        )
        self.assertTrue(success)
        
        # Test cache hit
        cached_result = ai_cache_service.get_cached_result(self.test_prompt, self.test_parameters)
        self.assertIsNotNone(cached_result)
        self.assertEqual(cached_result['result'], self.test_result)
    
    def test_ai_cache_invalidation(self):
        """Test AI cache invalidation"""
        # Cache a result
        ai_cache_service.cache_result(
            self.test_prompt, 
            self.test_parameters, 
            self.test_result
        )
        
        # Verify it's cached
        result = ai_cache_service.get_cached_result(self.test_prompt, self.test_parameters)
        self.assertIsNotNone(result)
        
        # Invalidate cache
        success = ai_cache_service.invalidate_cache(self.test_prompt, self.test_parameters)
        self.assertTrue(success)
        
        # Verify cache is invalidated
        result = ai_cache_service.get_cached_result(self.test_prompt, self.test_parameters)
        self.assertIsNone(result)
    
    def test_design_cache_operations(self):
        """Test design cache operations"""
        design_id = str(uuid.uuid4())
        test_data = {'title': 'Test Design', 'description': 'A test design'}
        
        # Test cache set
        success = design_cache_service.cache_design_data(design_id, test_data)
        self.assertTrue(success)
        
        # Test cache get
        cached_data = design_cache_service.get_cached_design_data(design_id)
        self.assertEqual(cached_data, test_data)
        
        # Test cache invalidation
        success = design_cache_service.invalidate_design_cache(design_id)
        self.assertTrue(success)
        
        # Verify cache is invalidated
        cached_data = design_cache_service.get_cached_design_data(design_id)
        self.assertIsNone(cached_data)
    
    def test_cache_stats(self):
        """Test cache statistics"""
        stats = ai_cache_service.get_cache_stats()
        self.assertIn('cache_enabled', stats)
        self.assertIn('cache_timeout', stats)
        self.assertIn('cache_prefix', stats)


class TestIntegration(APITestCase):
    """Integration tests for the complete workflow"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create test organization
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        
        # Create test user
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User"
        )
        
        # Add user to organization
        OrganizationMember.objects.create(
            user=self.user,
            organization=self.organization,
            role="admin",
            is_active=True
        )
        
        # Set current organization
        self.user.current_organization = self.organization
        self.user.save()
        
        # Authenticate user
        self.client.force_authenticate(user=self.user)
    
    @patch('poster_generation.services.NanoBananaPosterService.generate_poster')
    @patch('design_export.services.DesignExportService._export_as_images')
    def test_complete_workflow(self, mock_export, mock_generate):
        """Test complete workflow: generate poster -> share -> export"""
        # Mock AI generation
        mock_generate.return_value = {
            'success': True,
            'generated_images': ['https://example.com/image1.png'],
            'processing_time': 15.5,
            'cost': 0.05
        }
        
        # Mock export
        mock_export.return_value = {
            'success': True,
            'file_path': '/tmp/export.png',
            'download_url': 'http://example.com/download.png',
            'file_size': 1024000,
            'processing_time': 5.2
        }
        
        # Step 1: Generate poster
        poster_url = reverse('poster-api-generate-poster')
        poster_data = {
            'prompt': 'A beautiful textile design',
            'width': 1024,
            'height': 1024,
            'num_images': 1
        }
        
        response = self.client.post(poster_url, poster_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        job_id = response.data['job_id']
        
        # Step 2: Create design from generated poster
        design = Design.objects.create(
            organization=self.organization,
            title="Generated Design",
            description="AI generated design",
            created_by=self.user,
            ai_generated=True,
            ai_prompt=poster_data['prompt']
        )
        
        # Step 3: Share design
        share_url = reverse('collaboration-api-share-design')
        share_data = {
            'design_id': str(design.id),
            'is_public': True,
            'access_level': 'view',
            'allow_download': True
        }
        
        response = self.client.post(share_url, share_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Step 4: Export design
        export_url = reverse('export-api-export-designs')
        export_data = {
            'design_ids': [str(design.id)],
            'export_format': 'png'
        }
        
        response = self.client.post(export_url, export_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify all operations completed successfully
        self.assertTrue(Design.objects.filter(id=design.id).exists())
        self.assertTrue(DesignShare.objects.filter(design=design).exists())
        self.assertTrue(ExportJob.objects.filter(design_ids__contains=str(design.id)).exists())


# Test fixtures and utilities
@pytest.fixture
def test_organization():
    """Create a test organization"""
    return Organization.objects.create(
        name="Test Organization",
        slug="test-org"
    )


@pytest.fixture
def test_user(test_organization):
    """Create a test user"""
    user = User.objects.create_user(
        email="test@example.com",
        password="testpass123",
        first_name="Test",
        last_name="User"
    )
    
    OrganizationMember.objects.create(
        user=user,
        organization=test_organization,
        role="admin",
        is_active=True
    )
    
    user.current_organization = test_organization
    user.save()
    
    return user


@pytest.fixture
def test_design(test_organization, test_user):
    """Create a test design"""
    return Design.objects.create(
        organization=test_organization,
        title="Test Design",
        description="A test design",
        created_by=test_user
    )


# Performance tests
class TestPerformance(APITestCase):
    """Performance tests for the backend features"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create test organization
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        
        # Create test user
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User"
        )
        
        # Add user to organization
        OrganizationMember.objects.create(
            user=self.user,
            organization=self.organization,
            role="admin",
            is_active=True
        )
        
        # Set current organization
        self.user.current_organization = self.organization
        self.user.save()
        
        # Authenticate user
        self.client.force_authenticate(user=self.user)
    
    def test_poster_generation_performance(self):
        """Test poster generation performance"""
        import time
        
        url = reverse('poster-api-generate-poster')
        data = {
            'prompt': 'A beautiful textile design',
            'width': 1024,
            'height': 1024,
            'num_images': 1
        }
        
        start_time = time.time()
        response = self.client.post(url, data, format='json')
        end_time = time.time()
        
        # Should complete within reasonable time (adjust threshold as needed)
        self.assertLess(end_time - start_time, 5.0)  # 5 seconds
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_export_performance(self):
        """Test export performance"""
        import time
        
        # Create test design
        design = Design.objects.create(
            organization=self.organization,
            title="Test Design",
            description="A test design",
            created_by=self.user
        )
        
        url = reverse('export-api-export-designs')
        data = {
            'design_ids': [str(design.id)],
            'export_format': 'png'
        }
        
        start_time = time.time()
        response = self.client.post(url, data, format='json')
        end_time = time.time()
        
        # Should complete within reasonable time
        self.assertLess(end_time - start_time, 3.0)  # 3 seconds
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


if __name__ == '__main__':
    pytest.main([__file__])
