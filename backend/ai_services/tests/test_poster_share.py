"""
Unit tests for poster share endpoint
"""
import uuid
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework import status
from ai_services.models import GeneratedPoster
from organizations.models import Organization

User = get_user_model()


class PosterShareEndpointTestCase(TestCase):
    """Test cases for poster share endpoint"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test user
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Create test organization
        self.organization = Organization.objects.create(
            name='Test Organization',
            slug='test-org'
        )
        
        # Create test poster
        self.poster = GeneratedPoster.objects.create(
            organization=self.organization,
            user=self.user,
            image_url='http://example.com/poster.png',
            image_path='posters/poster.png',
            caption='Test Poster Caption',
            full_caption='Test Poster Caption with hashtags #test #poster',
            prompt='Create a test poster',
            aspect_ratio='4:5',
            width=1080,
            height=1350,
            hashtags=['#test', '#poster', '#ai']
        )
    
    def test_get_poster_share_data_success(self):
        """Test successful retrieval of poster share data"""
        url = f'/api/ai/posters/{self.poster.id}/share/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Check required fields
        self.assertIn('id', data)
        self.assertIn('caption', data)
        self.assertIn('hashtags', data)
        self.assertIn('image_url', data)
        self.assertIn('og_title', data)
        self.assertIn('og_description', data)
        
        # Check values
        self.assertEqual(data['id'], str(self.poster.id))
        self.assertEqual(data['caption'], self.poster.caption)
        self.assertEqual(data['hashtags'], self.poster.hashtags)
        
        # Check OG fields are optimized
        self.assertLessEqual(len(data['og_title']), 60)
        self.assertLessEqual(len(data['og_description']), 200)
    
    def test_get_poster_share_data_not_found(self):
        """Test share endpoint with non-existent poster ID"""
        fake_id = uuid.uuid4()
        url = f'/api/ai/posters/{fake_id}/share/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.json()
        self.assertIn('error', data)
    
    def test_get_poster_share_data_absolute_image_url(self):
        """Test that image URL is absolute"""
        url = f'/api/ai/posters/{self.poster.id}/share/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Image URL should be absolute
        image_url = data['image_url']
        self.assertTrue(image_url.startswith(('http://', 'https://')))
    
    def test_get_poster_share_data_relative_image_url(self):
        """Test that relative image URLs are converted to absolute"""
        # Update poster with relative URL
        self.poster.image_url = '/media/posters/poster.png'
        self.poster.save()
        
        url = f'/api/ai/posters/{self.poster.id}/share/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Image URL should be absolute
        image_url = data['image_url']
        self.assertTrue(image_url.startswith(('http://', 'https://')))
    
    def test_get_poster_share_data_og_title_truncation(self):
        """Test that OG title is properly truncated"""
        # Create poster with long caption
        long_caption = 'A' * 100  # 100 characters
        self.poster.caption = long_caption
        self.poster.save()
        
        url = f'/api/ai/posters/{self.poster.id}/share/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # OG title should be truncated to max 60 chars
        self.assertLessEqual(len(data['og_title']), 60)
    
    def test_get_poster_share_data_og_description_truncation(self):
        """Test that OG description is properly truncated"""
        # Create poster with long caption and hashtags
        long_caption = 'A' * 150
        many_hashtags = ['#tag' + str(i) for i in range(20)]
        self.poster.caption = long_caption
        self.poster.hashtags = many_hashtags
        self.poster.save()
        
        url = f'/api/ai/posters/{self.poster.id}/share/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # OG description should be truncated to max 200 chars
        self.assertLessEqual(len(data['og_description']), 200)
    
    def test_get_poster_share_data_caching(self):
        """Test that share data is cached"""
        from django.core.cache import cache
        
        # Clear cache
        cache.clear()
        
        url = f'/api/ai/posters/{self.poster.id}/share/'
        
        # First request
        response1 = self.client.get(url)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # Second request should use cache
        response2 = self.client.get(url)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        
        # Responses should be identical
        self.assertEqual(response1.json(), response2.json())
    
    def test_get_poster_share_data_without_hashtags(self):
        """Test share endpoint with poster that has no hashtags"""
        self.poster.hashtags = []
        self.poster.save()
        
        url = f'/api/ai/posters/{self.poster.id}/share/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertEqual(data['hashtags'], [])
        # OG description should still work without hashtags
        self.assertIn('og_description', data)
    
    def test_get_poster_share_data_with_null_dimensions(self):
        """Test share endpoint with poster that has null dimensions"""
        self.poster.width = None
        self.poster.height = None
        self.poster.save()
        
        url = f'/api/ai/posters/{self.poster.id}/share/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Should handle null dimensions gracefully
        self.assertIn('image_width', data)
        self.assertIn('image_height', data)

