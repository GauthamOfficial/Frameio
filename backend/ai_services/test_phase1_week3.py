"""
Test cases for Phase 1 Week 3 Backend Lead tasks
"""
import json
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from organizations.models import Organization, OrganizationMember
from ai_services.models import AIProvider, AIGenerationRequest
from ai_services.scheduling_models import ScheduledPost
from ai_services.social_media import SocialMediaService

User = get_user_model()


class TextilePosterEndpointTest(APITestCase):
    """Test cases for textile poster generation endpoint"""
    
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
        OrganizationMember.objects.create(
            organization=self.organization,
            user=self.user,
            role='admin'
        )
        
        # Create AI provider
        self.provider = AIProvider.objects.create(
            name='nanobanana',
            is_active=True
        )
        
        self.client.force_authenticate(user=self.user)
    
    def test_generate_poster_success(self):
        """Test successful poster generation"""
        url = '/api/ai/textile/poster/generate_poster/'
        data = {
            'product_image_url': 'https://example.com/product.jpg',
            'fabric_type': 'saree',
            'festival': 'deepavali',
            'price_range': '₹2999',
            'style': 'elegant',
            'color_scheme': 'gold and red',
            'custom_text': 'Special offer!',
            'offer_details': 'Buy 2 get 1 free'
        }
        
        response = self.client.post(
            url, 
            data, 
            format='json',
            HTTP_X_ORGANIZATION=self.organization.slug
        )
        
        # Debug: Print response details
        if response.status_code != 200:
            print(f"Response status: {response.status_code}")
            if hasattr(response, 'data'):
                print(f"Response data: {response.data}")
            else:
                print(f"Response content: {response.content}")
        
        # Should return 200 with success response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('poster_url', response.data)
        self.assertIn('caption_suggestions', response.data)
        self.assertIn('hashtags', response.data)
        self.assertIn('metadata', response.data)
    
    def test_generate_poster_missing_image(self):
        """Test poster generation with missing image URL"""
        url = '/api/ai/textile/poster/generate_poster/'
        data = {
            'fabric_type': 'saree',
            'festival': 'deepavali'
        }
        
        response = self.client.post(url, data, format='json')
        
        # Should return 400 with validation error
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('product_image_url', response.data)
    
    def test_generate_poster_invalid_data(self):
        """Test poster generation with invalid data"""
        url = '/api/ai/textile/poster/generate_poster/'
        data = {
            'product_image_url': 'not-a-url',
            'fabric_type': 'invalid_fabric'
        }
        
        response = self.client.post(url, data, format='json')
        
        # Should return 400 with validation error
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TextileCaptionEndpointTest(APITestCase):
    """Test cases for textile caption generation endpoint"""
    
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
        OrganizationMember.objects.create(
            organization=self.organization,
            user=self.user,
            role='admin'
        )
        
        self.client.force_authenticate(user=self.user)
    
    def test_generate_caption_success(self):
        """Test successful caption generation"""
        url = '/api/ai/textile/caption/generate_caption/'
        data = {
            'product_name': 'Elegant Silk Saree',
            'fabric_type': 'silk',
            'festival': 'deepavali',
            'price_range': '₹4999',
            'style': 'traditional',
            'color_scheme': 'gold and maroon',
            'custom_text': 'Perfect for celebrations',
            'offer_details': 'Free shipping on orders above ₹3000'
        }
        
        response = self.client.post(url, data, format='json')
        
        # Should return 200 with success response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('captions', response.data)
        self.assertIn('hashtags', response.data)
        self.assertIn('metadata', response.data)
    
    def test_generate_caption_missing_product_name(self):
        """Test caption generation with missing product name"""
        url = '/api/ai/textile/caption/generate_caption/'
        data = {
            'fabric_type': 'silk',
            'festival': 'deepavali'
        }
        
        response = self.client.post(url, data, format='json')
        
        # Should return 400 with validation error
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('product_name', response.data)
    
    def test_generate_caption_empty_product_name(self):
        """Test caption generation with empty product name"""
        url = '/api/ai/textile/caption/generate_caption/'
        data = {
            'product_name': '',
            'fabric_type': 'silk'
        }
        
        response = self.client.post(url, data, format='json')
        
        # Should return 400 with validation error
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('product_name', response.data)


class ScheduledPostModelTest(TestCase):
    """Test cases for ScheduledPost model"""
    
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
        OrganizationMember.objects.create(
            organization=self.organization,
            user=self.user,
            role='admin'
        )
    
    def test_create_scheduled_post(self):
        """Test creating a scheduled post"""
        scheduled_time = timezone.now() + timezone.timedelta(hours=1)
        
        post = ScheduledPost.objects.create(
            organization=self.organization,
            user=self.user,
            platform='facebook',
            asset_url='https://example.com/image.jpg',
            caption='Test post with hashtags #test #social',
            scheduled_time=scheduled_time
        )
        
        self.assertEqual(post.organization, self.organization)
        self.assertEqual(post.user, self.user)
        self.assertEqual(post.platform, 'facebook')
        self.assertEqual(post.status, 'pending')
        self.assertTrue(post.is_ready_to_post() is False)  # Not ready yet
    
    def test_mark_as_posted(self):
        """Test marking a post as posted"""
        scheduled_time = timezone.now() - timezone.timedelta(hours=1)
        
        post = ScheduledPost.objects.create(
            organization=self.organization,
            user=self.user,
            platform='instagram',
            asset_url='https://example.com/image.jpg',
            caption='Test post',
            scheduled_time=scheduled_time,
            status='scheduled'
        )
        
        post.mark_as_posted()
        
        self.assertEqual(post.status, 'posted')
        self.assertIsNotNone(post.posted_at)
    
    def test_mark_as_failed(self):
        """Test marking a post as failed"""
        post = ScheduledPost.objects.create(
            organization=self.organization,
            user=self.user,
            platform='twitter',
            asset_url='https://example.com/image.jpg',
            caption='Test post',
            scheduled_time=timezone.now() + timezone.timedelta(hours=1)
        )
        
        post.mark_as_failed('API error')
        
        self.assertEqual(post.status, 'failed')
        self.assertEqual(post.error_message, 'API error')
        self.assertEqual(post.retry_count, 1)
    
    def test_can_retry(self):
        """Test retry functionality"""
        post = ScheduledPost.objects.create(
            organization=self.organization,
            user=self.user,
            platform='linkedin',
            asset_url='https://example.com/image.jpg',
            caption='Test post',
            scheduled_time=timezone.now() + timezone.timedelta(hours=1),
            retry_count=2,
            max_retries=3
        )
        
        self.assertTrue(post.can_retry())
        
        post.retry_count = 3
        self.assertFalse(post.can_retry())
    
    def test_schedule_for_retry(self):
        """Test scheduling for retry"""
        post = ScheduledPost.objects.create(
            organization=self.organization,
            user=self.user,
            platform='tiktok',
            asset_url='https://example.com/video.mp4',
            caption='Test video',
            scheduled_time=timezone.now() + timezone.timedelta(hours=1),
            status='failed',
            retry_count=1,
            max_retries=3
        )
        
        result = post.schedule_for_retry()
        
        self.assertTrue(result)
        self.assertEqual(post.status, 'pending')
    
    def test_schedule_for_retry_max_retries_exceeded(self):
        """Test scheduling for retry when max retries exceeded"""
        post = ScheduledPost.objects.create(
            organization=self.organization,
            user=self.user,
            platform='whatsapp',
            asset_url='https://example.com/image.jpg',
            caption='Test post',
            scheduled_time=timezone.now() + timezone.timedelta(hours=1),
            status='failed',
            retry_count=3,
            max_retries=3
        )
        
        result = post.schedule_for_retry()
        
        self.assertFalse(result)
        self.assertEqual(post.status, 'failed')


class ScheduledPostEndpointTest(APITestCase):
    """Test cases for scheduled post endpoints"""
    
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
        OrganizationMember.objects.create(
            organization=self.organization,
            user=self.user,
            role='admin'
        )
        
        self.client.force_authenticate(user=self.user)
    
    def test_create_scheduled_post(self):
        """Test creating a scheduled post"""
        url = '/api/ai/schedule/'
        scheduled_time = timezone.now() + timezone.timedelta(hours=1)
        
        data = {
            'platform': 'facebook',
            'asset_url': 'https://example.com/image.jpg',
            'caption': 'Test post with hashtags #test #social',
            'scheduled_time': scheduled_time.isoformat(),
            'metadata': {'page_id': '123456'}
        }
        
        response = self.client.post(url, data, format='json')
        
        # Should return 201 with created post
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['platform'], 'facebook')
        self.assertEqual(response.data['status'], 'pending')
    
    def test_create_scheduled_post_past_time(self):
        """Test creating a scheduled post with past time"""
        url = '/api/ai/schedule/'
        past_time = timezone.now() - timezone.timedelta(hours=1)
        
        data = {
            'platform': 'instagram',
            'asset_url': 'https://example.com/image.jpg',
            'caption': 'Test post',
            'scheduled_time': past_time.isoformat()
        }
        
        response = self.client.post(url, data, format='json')
        
        # Should return 400 with validation error
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('scheduled_time', response.data)
    
    def test_create_scheduled_post_invalid_platform(self):
        """Test creating a scheduled post with invalid platform"""
        url = '/api/ai/schedule/'
        scheduled_time = timezone.now() + timezone.timedelta(hours=1)
        
        data = {
            'platform': 'invalid_platform',
            'asset_url': 'https://example.com/image.jpg',
            'caption': 'Test post',
            'scheduled_time': scheduled_time.isoformat()
        }
        
        response = self.client.post(url, data, format='json')
        
        # Should return 400 with validation error
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('platform', response.data)
    
    def test_list_scheduled_posts(self):
        """Test listing scheduled posts"""
        # Create test posts
        ScheduledPost.objects.create(
            organization=self.organization,
            user=self.user,
            platform='facebook',
            asset_url='https://example.com/image1.jpg',
            caption='Post 1',
            scheduled_time=timezone.now() + timezone.timedelta(hours=1)
        )
        
        ScheduledPost.objects.create(
            organization=self.organization,
            user=self.user,
            platform='instagram',
            asset_url='https://example.com/image2.jpg',
            caption='Post 2',
            scheduled_time=timezone.now() + timezone.timedelta(hours=2)
        )
        
        url = '/api/ai/schedule/'
        response = self.client.get(url)
        
        # Should return 200 with list of posts
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_filter_scheduled_posts_by_platform(self):
        """Test filtering scheduled posts by platform"""
        # Create test posts
        ScheduledPost.objects.create(
            organization=self.organization,
            user=self.user,
            platform='facebook',
            asset_url='https://example.com/image1.jpg',
            caption='Facebook post',
            scheduled_time=timezone.now() + timezone.timedelta(hours=1)
        )
        
        ScheduledPost.objects.create(
            organization=self.organization,
            user=self.user,
            platform='instagram',
            asset_url='https://example.com/image2.jpg',
            caption='Instagram post',
            scheduled_time=timezone.now() + timezone.timedelta(hours=2)
        )
        
        url = '/api/ai/schedule/'
        response = self.client.get(url, {'platform': 'facebook'})
        
        # Should return only Facebook posts
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['platform'], 'facebook')
    
    def test_filter_scheduled_posts_by_status(self):
        """Test filtering scheduled posts by status"""
        # Create test posts
        ScheduledPost.objects.create(
            organization=self.organization,
            user=self.user,
            platform='facebook',
            asset_url='https://example.com/image1.jpg',
            caption='Pending post',
            scheduled_time=timezone.now() + timezone.timedelta(hours=1),
            status='pending'
        )
        
        ScheduledPost.objects.create(
            organization=self.organization,
            user=self.user,
            platform='instagram',
            asset_url='https://example.com/image2.jpg',
            caption='Posted post',
            scheduled_time=timezone.now() - timezone.timedelta(hours=1),
            status='posted'
        )
        
        url = '/api/ai/schedule/'
        response = self.client.get(url, {'status': 'pending'})
        
        # Should return only pending posts
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['status'], 'pending')
    
    def test_update_scheduled_post(self):
        """Test updating a scheduled post"""
        # Create a scheduled post
        post = ScheduledPost.objects.create(
            organization=self.organization,
            user=self.user,
            platform='facebook',
            asset_url='https://example.com/image.jpg',
            caption='Original caption',
            scheduled_time=timezone.now() + timezone.timedelta(hours=1)
        )
        
        url = f'/api/ai/schedule/{post.id}/'
        new_scheduled_time = timezone.now() + timezone.timedelta(hours=2)
        
        data = {
            'caption': 'Updated caption',
            'scheduled_time': new_scheduled_time.isoformat()
        }
        
        response = self.client.patch(url, data, format='json')
        
        # Should return 200 with updated post
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['caption'], 'Updated caption')
    
    def test_cancel_scheduled_post(self):
        """Test cancelling a scheduled post"""
        # Create a scheduled post
        post = ScheduledPost.objects.create(
            organization=self.organization,
            user=self.user,
            platform='instagram',
            asset_url='https://example.com/image.jpg',
            caption='Post to cancel',
            scheduled_time=timezone.now() + timezone.timedelta(hours=1)
        )
        
        url = f'/api/ai/schedule/{post.id}/cancel/'
        response = self.client.post(url)
        
        # Should return 200 with cancelled post
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'cancelled')
    
    def test_cancel_posted_scheduled_post(self):
        """Test cancelling a posted scheduled post (should fail)"""
        # Create a posted post
        post = ScheduledPost.objects.create(
            organization=self.organization,
            user=self.user,
            platform='twitter',
            asset_url='https://example.com/image.jpg',
            caption='Posted post',
            scheduled_time=timezone.now() - timezone.timedelta(hours=1),
            status='posted'
        )
        
        url = f'/api/ai/schedule/{post.id}/cancel/'
        response = self.client.post(url)
        
        # Should return 400 with error
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_retry_failed_scheduled_post(self):
        """Test retrying a failed scheduled post"""
        # Create a failed post
        post = ScheduledPost.objects.create(
            organization=self.organization,
            user=self.user,
            platform='linkedin',
            asset_url='https://example.com/image.jpg',
            caption='Failed post',
            scheduled_time=timezone.now() + timezone.timedelta(hours=1),
            status='failed',
            retry_count=1,
            max_retries=3
        )
        
        url = f'/api/ai/schedule/{post.id}/retry/'
        response = self.client.post(url)
        
        # Should return 200 with retried post
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'pending')
    
    def test_retry_non_failed_scheduled_post(self):
        """Test retrying a non-failed scheduled post (should fail)"""
        # Create a pending post
        post = ScheduledPost.objects.create(
            organization=self.organization,
            user=self.user,
            platform='tiktok',
            asset_url='https://example.com/video.mp4',
            caption='Pending post',
            scheduled_time=timezone.now() + timezone.timedelta(hours=1),
            status='pending'
        )
        
        url = f'/api/ai/schedule/{post.id}/retry/'
        response = self.client.post(url)
        
        # Should return 400 with error
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_analytics(self):
        """Test scheduling analytics"""
        # Create test posts with different statuses
        ScheduledPost.objects.create(
            organization=self.organization,
            user=self.user,
            platform='facebook',
            asset_url='https://example.com/image1.jpg',
            caption='Posted post',
            scheduled_time=timezone.now() - timezone.timedelta(hours=1),
            status='posted'
        )
        
        ScheduledPost.objects.create(
            organization=self.organization,
            user=self.user,
            platform='instagram',
            asset_url='https://example.com/image2.jpg',
            caption='Failed post',
            scheduled_time=timezone.now() - timezone.timedelta(hours=2),
            status='failed'
        )
        
        ScheduledPost.objects.create(
            organization=self.organization,
            user=self.user,
            platform='twitter',
            asset_url='https://example.com/image3.jpg',
            caption='Pending post',
            scheduled_time=timezone.now() + timezone.timedelta(hours=1),
            status='pending'
        )
        
        url = '/api/ai/schedule/analytics/'
        response = self.client.get(url)
        
        # Should return 200 with analytics data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_posts', response.data)
        self.assertIn('posted_posts', response.data)
        self.assertIn('failed_posts', response.data)
        self.assertIn('pending_posts', response.data)
        self.assertIn('success_rate', response.data)
        self.assertIn('platform_breakdown', response.data)
        self.assertIn('status_breakdown', response.data)


class SocialMediaServiceTest(TestCase):
    """Test cases for SocialMediaService"""
    
    def setUp(self):
        """Set up test data"""
        self.social_service = SocialMediaService()
    
    def test_post_to_facebook(self):
        """Test posting to Facebook"""
        result = self.social_service.post_to_facebook(
            asset_url='https://example.com/image.jpg',
            caption='Test Facebook post'
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['platform'], 'facebook')
        self.assertIn('post_id', result)
        self.assertIn('url', result)
    
    def test_post_to_instagram(self):
        """Test posting to Instagram"""
        result = self.social_service.post_to_instagram(
            asset_url='https://example.com/image.jpg',
            caption='Test Instagram post'
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['platform'], 'instagram')
        self.assertIn('post_id', result)
        self.assertIn('url', result)
    
    def test_post_to_tiktok(self):
        """Test posting to TikTok"""
        result = self.social_service.post_to_tiktok(
            asset_url='https://example.com/video.mp4',
            caption='Test TikTok video'
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['platform'], 'tiktok')
        self.assertIn('post_id', result)
        self.assertIn('url', result)
    
    def test_post_to_whatsapp(self):
        """Test posting to WhatsApp"""
        result = self.social_service.post_to_whatsapp(
            asset_url='https://example.com/image.jpg',
            caption='Test WhatsApp message'
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['platform'], 'whatsapp')
        self.assertIn('post_id', result)
        self.assertIn('url', result)
    
    def test_post_to_twitter(self):
        """Test posting to Twitter"""
        result = self.social_service.post_to_twitter(
            asset_url='https://example.com/image.jpg',
            caption='Test Twitter post'
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['platform'], 'twitter')
        self.assertIn('post_id', result)
        self.assertIn('url', result)
    
    def test_post_to_linkedin(self):
        """Test posting to LinkedIn"""
        result = self.social_service.post_to_linkedin(
            asset_url='https://example.com/image.jpg',
            caption='Test LinkedIn post'
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['platform'], 'linkedin')
        self.assertIn('post_id', result)
        self.assertIn('url', result)
    
    def test_post_to_platform_generic(self):
        """Test generic platform posting"""
        result = self.social_service.post_to_platform(
            platform='facebook',
            asset_url='https://example.com/image.jpg',
            caption='Test post'
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['platform'], 'facebook')
    
    def test_post_to_platform_invalid(self):
        """Test posting to invalid platform"""
        result = self.social_service.post_to_platform(
            platform='invalid_platform',
            asset_url='https://example.com/image.jpg',
            caption='Test post'
        )
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_get_supported_platforms(self):
        """Test getting supported platforms"""
        platforms = self.social_service.get_supported_platforms()
        
        expected_platforms = ['facebook', 'instagram', 'tiktok', 'whatsapp', 'twitter', 'linkedin']
        self.assertEqual(set(platforms), set(expected_platforms))
    
    def test_validate_platform(self):
        """Test platform validation"""
        self.assertTrue(self.social_service.validate_platform('facebook'))
        self.assertTrue(self.social_service.validate_platform('instagram'))
        self.assertFalse(self.social_service.validate_platform('invalid_platform'))
    
    def test_get_platform_requirements(self):
        """Test getting platform requirements"""
        requirements = self.social_service.get_platform_requirements('facebook')
        
        self.assertIn('required_params', requirements)
        self.assertIn('asset_types', requirements)
        self.assertIn('max_caption_length', requirements)
        self.assertIn('max_asset_size', requirements)
        
        self.assertIn('page_id', requirements['required_params'])
        self.assertIn('access_token', requirements['required_params'])


class IntegrationTest(APITestCase):
    """Integration tests for the complete workflow"""
    
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
        OrganizationMember.objects.create(
            organization=self.organization,
            user=self.user,
            role='admin'
        )
        
        self.client.force_authenticate(user=self.user)
    
    def test_complete_textile_workflow(self):
        """Test complete textile workflow: generate poster -> generate caption -> schedule post"""
        
        # Step 1: Generate poster
        poster_url = reverse('textile-poster-new-generate-poster')
        poster_data = {
            'product_image_url': 'https://example.com/product.jpg',
            'fabric_type': 'saree',
            'festival': 'deepavali',
            'price_range': '₹2999',
            'style': 'elegant'
        }
        
        poster_response = self.client.post(poster_url, poster_data, format='json')
        self.assertEqual(poster_response.status_code, status.HTTP_200_OK)
        self.assertTrue(poster_response.data['success'])
        
        # Step 2: Generate caption
        caption_url = reverse('textile-caption-generate-caption')
        caption_data = {
            'product_name': 'Elegant Silk Saree',
            'fabric_type': 'silk',
            'festival': 'deepavali',
            'price_range': '₹2999',
            'style': 'traditional'
        }
        
        caption_response = self.client.post(caption_url, caption_data, format='json')
        self.assertEqual(caption_response.status_code, status.HTTP_200_OK)
        self.assertTrue(caption_response.data['success'])
        
        # Step 3: Schedule post
        schedule_url = '/api/ai/schedule/'
        scheduled_time = timezone.now() + timezone.timedelta(hours=1)
        
        schedule_data = {
            'platform': 'facebook',
            'asset_url': poster_response.data['poster_url'],
            'caption': caption_response.data['captions'][0] if caption_response.data['captions'] else 'Generated caption',
            'scheduled_time': scheduled_time.isoformat()
        }
        
        schedule_response = self.client.post(schedule_url, schedule_data, format='json')
        self.assertEqual(schedule_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(schedule_response.data['platform'], 'facebook')
        self.assertEqual(schedule_response.data['status'], 'pending')
    
    def test_error_handling_workflow(self):
        """Test error handling in the workflow"""
        
        # Test with invalid data
        poster_url = reverse('textile-poster-new-generate-poster')
        invalid_data = {
            'product_image_url': 'not-a-url',
            'fabric_type': 'invalid_fabric'
        }
        
        response = self.client.post(poster_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test scheduling with past time
        schedule_url = '/api/ai/schedule/'
        past_time = timezone.now() - timezone.timedelta(hours=1)
        
        schedule_data = {
            'platform': 'facebook',
            'asset_url': 'https://example.com/image.jpg',
            'caption': 'Test post',
            'scheduled_time': past_time.isoformat()
        }
        
        response = self.client.post(schedule_url, schedule_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
