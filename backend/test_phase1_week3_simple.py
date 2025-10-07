#!/usr/bin/env python
"""
Simple test script to verify Phase 1 Week 3 deliverables
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from organizations.models import Organization, OrganizationMember
from ai_services.models import AIProvider
from ai_services.scheduling_models import ScheduledPost
from ai_services.social_media import SocialMediaService
from ai_services.arcjet_service import ArcjetService
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


def test_social_media_service():
    """Test social media service functionality"""
    print("Testing Social Media Service...")
    
    service = SocialMediaService()
    
    # Test platform validation
    assert service.validate_platform('facebook') == True
    assert service.validate_platform('invalid') == False
    
    # Test supported platforms
    platforms = service.get_supported_platforms()
    assert 'facebook' in platforms
    assert 'instagram' in platforms
    assert 'tiktok' in platforms
    
    # Test posting to Facebook
    result = service.post_to_facebook(
        asset_url='https://example.com/image.jpg',
        caption='Test caption'
    )
    assert result['success'] == True
    assert result['platform'] == 'facebook'
    
    print("✅ Social Media Service tests passed")


def test_arcjet_service():
    """Test Arcjet service functionality"""
    print("Testing Arcjet Service...")
    
    # Create test organization
    org = Organization.objects.create(
        name='Test Org',
        slug='test-org'
    )
    
    service = ArcjetService()
    
    # Test usage limit check
    result = service.check_usage_limit(org, 'poster_generation')
    assert result['success'] == True
    assert 'within_limits' in result
    
    # Test usage stats
    stats = service.get_usage_stats(org)
    assert 'plan' in stats
    assert 'services' in stats
    
    print("✅ Arcjet Service tests passed")


def test_scheduled_post_model():
    """Test ScheduledPost model functionality"""
    print("Testing ScheduledPost Model...")
    
    # Create test data
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    
    org = Organization.objects.create(
        name='Test Org',
        slug='test-org'
    )
    
    OrganizationMember.objects.create(
        organization=org,
        user=user,
        role='admin'
    )
    
    # Create scheduled post
    scheduled_time = timezone.now() + timedelta(hours=1)
    post = ScheduledPost.objects.create(
        organization=org,
        user=user,
        platform='facebook',
        asset_url='https://example.com/image.jpg',
        caption='Test post',
        scheduled_time=scheduled_time
    )
    
    # Test model methods
    assert post.status == 'pending'
    assert post.can_retry() == True
    
    # Test marking as posted
    post.mark_as_posted()
    assert post.status == 'posted'
    assert post.posted_at is not None
    
    print("✅ ScheduledPost Model tests passed")


def test_textile_endpoints():
    """Test textile endpoints functionality"""
    print("Testing Textile Endpoints...")
    
    # Create test data
    user = User.objects.create_user(
        username='testuser2',
        email='test2@example.com',
        password='testpass123'
    )
    
    org = Organization.objects.create(
        name='Test Org 2',
        slug='test-org-2'
    )
    
    OrganizationMember.objects.create(
        organization=org,
        user=user,
        role='admin'
    )
    
    # Create AI provider
    provider = AIProvider.objects.create(
        name='nanobanana',
        is_active=True
    )
    
    # Test client
    client = Client()
    client.force_login(user)
    
    # Test poster generation endpoint
    url = '/api/ai/textile/poster/generate_poster/'
    data = {
        'product_image_url': 'https://example.com/product.jpg',
        'fabric_type': 'saree',
        'festival': 'deepavali',
        'price_range': '₹2999',
        'style': 'elegant'
    }
    
    response = client.post(
        url,
        data,
        content_type='application/json',
        HTTP_X_ORGANIZATION=org.slug
    )
    
    print(f"Poster endpoint response: {response.status_code}")
    if response.status_code != 200:
        print(f"Response content: {response.content}")
    
    # Test caption generation endpoint
    url = '/api/ai/textile/caption/generate_caption/'
    data = {
        'product_name': 'Test Product',
        'fabric_type': 'silk',
        'festival': 'deepavali',
        'price_range': '₹4999',
        'style': 'traditional'
    }
    
    response = client.post(
        url,
        data,
        content_type='application/json',
        HTTP_X_ORGANIZATION=org.slug
    )
    
    print(f"Caption endpoint response: {response.status_code}")
    if response.status_code != 200:
        print(f"Response content: {response.content}")
    
    print("✅ Textile Endpoints tests completed")


def test_scheduling_endpoints():
    """Test scheduling endpoints functionality"""
    print("Testing Scheduling Endpoints...")
    
    # Create test data
    user = User.objects.create_user(
        username='testuser3',
        email='test3@example.com',
        password='testpass123'
    )
    
    org = Organization.objects.create(
        name='Test Org 3',
        slug='test-org-3'
    )
    
    OrganizationMember.objects.create(
        organization=org,
        user=user,
        role='admin'
    )
    
    # Test client
    client = Client()
    client.force_login(user)
    
    # Test create scheduled post
    url = '/api/ai/schedule/'
    scheduled_time = timezone.now() + timedelta(hours=1)
    data = {
        'platform': 'facebook',
        'asset_url': 'https://example.com/image.jpg',
        'caption': 'Test scheduled post',
        'scheduled_time': scheduled_time.isoformat()
    }
    
    response = client.post(
        url,
        data,
        content_type='application/json',
        HTTP_X_ORGANIZATION=org.slug
    )
    
    print(f"Create scheduled post response: {response.status_code}")
    if response.status_code not in [200, 201]:
        print(f"Response content: {response.content}")
    
    # Test list scheduled posts
    response = client.get(
        url,
        HTTP_X_ORGANIZATION=org.slug
    )
    
    print(f"List scheduled posts response: {response.status_code}")
    if response.status_code != 200:
        print(f"Response content: {response.content}")
    
    print("✅ Scheduling Endpoints tests completed")


def main():
    """Run all tests"""
    print("🚀 Starting Phase 1 Week 3 Deliverables Testing...")
    print("=" * 60)
    
    try:
        test_social_media_service()
        test_arcjet_service()
        test_scheduled_post_model()
        test_textile_endpoints()
        test_scheduling_endpoints()
        
        print("=" * 60)
        print("🎉 All Phase 1 Week 3 tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)