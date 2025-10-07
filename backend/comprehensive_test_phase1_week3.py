#!/usr/bin/env python
"""
Comprehensive test suite for Phase 1 Week 3 deliverables
This test verifies all functionality is working correctly
"""
import os
import sys
import django
import json
from datetime import timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')

try:
    django.setup()
    print("✅ Django setup successful")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from organizations.models import Organization, OrganizationMember
from ai_services.models import AIProvider
from ai_services.scheduling_models import ScheduledPost
from ai_services.social_media import SocialMediaService
from ai_services.arcjet_service import ArcjetService

User = get_user_model()


class Phase1Week3TestSuite:
    """Comprehensive test suite for Phase 1 Week 3 deliverables"""
    
    def __init__(self):
        self.test_results = []
        self.client = Client()
        
    def log_test(self, test_name, success, message=""):
        """Log test result"""
        status_icon = "✅" if success else "❌"
        print(f"{status_icon} {test_name}: {message}")
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message
        })
    
    def test_social_media_service(self):
        """Test social media service functionality"""
        print("\n🔧 Testing Social Media Service...")
        
        try:
            service = SocialMediaService()
            
            # Test platform validation
            if service.validate_platform('facebook'):
                self.log_test("Platform Validation", True, "Facebook platform validated")
            else:
                self.log_test("Platform Validation", False, "Facebook platform validation failed")
            
            # Test supported platforms
            platforms = service.get_supported_platforms()
            if 'facebook' in platforms and 'instagram' in platforms:
                self.log_test("Supported Platforms", True, f"Found {len(platforms)} platforms")
            else:
                self.log_test("Supported Platforms", False, "Missing expected platforms")
            
            # Test Facebook posting
            result = service.post_to_facebook(
                asset_url='https://example.com/image.jpg',
                caption='Test caption'
            )
            if result['success']:
                self.log_test("Facebook Posting", True, f"Post ID: {result.get('post_id', 'N/A')}")
            else:
                self.log_test("Facebook Posting", False, f"Error: {result.get('error', 'Unknown')}")
            
            # Test Instagram posting
            result = service.post_to_instagram(
                asset_url='https://example.com/image.jpg',
                caption='Test caption'
            )
            if result['success']:
                self.log_test("Instagram Posting", True, f"Post ID: {result.get('post_id', 'N/A')}")
            else:
                self.log_test("Instagram Posting", False, f"Error: {result.get('error', 'Unknown')}")
            
            # Test generic platform posting
            result = service.post_to_platform('facebook', 'https://example.com/image.jpg', 'Test')
            if result['success']:
                self.log_test("Generic Platform Posting", True, "Generic posting works")
            else:
                self.log_test("Generic Platform Posting", False, f"Error: {result.get('error', 'Unknown')}")
                
        except Exception as e:
            self.log_test("Social Media Service", False, f"Exception: {str(e)}")
    
    def test_arcjet_service(self):
        """Test Arcjet service functionality"""
        print("\n🔧 Testing Arcjet Service...")
        
        try:
            # Create test organization
            org = Organization.objects.create(
                name='Test Arcjet Org',
                slug='test-arcjet-org'
            )
            
            service = ArcjetService()
            
            # Test usage limit check
            result = service.check_usage_limit(org, 'poster_generation')
            if result['success'] and 'within_limits' in result:
                self.log_test("Usage Limit Check", True, f"Within limits: {result['within_limits']}")
            else:
                self.log_test("Usage Limit Check", False, f"Error: {result.get('error', 'Unknown')}")
            
            # Test usage stats
            stats = service.get_usage_stats(org)
            if 'plan' in stats and 'services' in stats:
                self.log_test("Usage Stats", True, f"Plan: {stats['plan']}")
            else:
                self.log_test("Usage Stats", False, f"Error: {stats.get('error', 'Unknown')}")
            
            # Test usage increment
            if service.increment_usage(org, 'poster_generation'):
                self.log_test("Usage Increment", True, "Usage incremented successfully")
            else:
                self.log_test("Usage Increment", False, "Failed to increment usage")
                
        except Exception as e:
            self.log_test("Arcjet Service", False, f"Exception: {str(e)}")
    
    def test_scheduled_post_model(self):
        """Test ScheduledPost model functionality"""
        print("\n🔧 Testing ScheduledPost Model...")
        
        try:
            # Create test data
            user = User.objects.create_user(
                username='testuser_model',
                email='testmodel@example.com',
                password='testpass123'
            )
            
            org = Organization.objects.create(
                name='Test Model Org',
                slug='test-model-org'
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
            
            # Test model creation
            if post.id:
                self.log_test("ScheduledPost Creation", True, f"ID: {post.id}")
            else:
                self.log_test("ScheduledPost Creation", False, "Failed to create post")
            
            # Test model methods
            if post.can_retry():
                self.log_test("Can Retry Check", True, "Post can be retried")
            else:
                self.log_test("Can Retry Check", False, "Post cannot be retried")
            
            # Test marking as posted
            post.mark_as_posted()
            if post.status == 'posted' and post.posted_at:
                self.log_test("Mark as Posted", True, "Post marked as posted successfully")
            else:
                self.log_test("Mark as Posted", False, "Failed to mark as posted")
            
            # Test marking as failed
            post.mark_as_failed("Test error")
            if post.status == 'failed' and post.error_message:
                self.log_test("Mark as Failed", True, "Post marked as failed successfully")
            else:
                self.log_test("Mark as Failed", False, "Failed to mark as failed")
                
        except Exception as e:
            self.log_test("ScheduledPost Model", False, f"Exception: {str(e)}")
    
    def test_textile_endpoints(self):
        """Test textile endpoints functionality"""
        print("\n🔧 Testing Textile Endpoints...")
        
        try:
            # Create test data
            user = User.objects.create_user(
                username='testuser_endpoints',
                email='testendpoints@example.com',
                password='testpass123'
            )
            
            org = Organization.objects.create(
                name='Test Endpoints Org',
                slug='test-endpoints-org'
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
            
            # Test client setup
            self.client.force_login(user)
            
            # Test poster generation endpoint
            url = '/api/ai/textile/poster/generate_poster/'
            data = {
                'product_image_url': 'https://example.com/product.jpg',
                'fabric_type': 'saree',
                'festival': 'deepavali',
                'price_range': '₹2999',
                'style': 'elegant'
            }
            
            response = self.client.post(
                url,
                data,
                content_type='application/json',
                HTTP_X_ORGANIZATION=org.slug
            )
            
            if response.status_code == 200:
                self.log_test("Poster Generation Endpoint", True, "Endpoint responded successfully")
            else:
                self.log_test("Poster Generation Endpoint", False, f"Status: {response.status_code}, Content: {response.content.decode()[:200]}")
            
            # Test caption generation endpoint
            url = '/api/ai/textile/caption/generate_caption/'
            data = {
                'product_name': 'Test Product',
                'fabric_type': 'silk',
                'festival': 'deepavali',
                'price_range': '₹4999',
                'style': 'traditional'
            }
            
            response = self.client.post(
                url,
                data,
                content_type='application/json',
                HTTP_X_ORGANIZATION=org.slug
            )
            
            if response.status_code == 200:
                self.log_test("Caption Generation Endpoint", True, "Endpoint responded successfully")
            else:
                self.log_test("Caption Generation Endpoint", False, f"Status: {response.status_code}, Content: {response.content.decode()[:200]}")
                
        except Exception as e:
            self.log_test("Textile Endpoints", False, f"Exception: {str(e)}")
    
    def test_scheduling_endpoints(self):
        """Test scheduling endpoints functionality"""
        print("\n🔧 Testing Scheduling Endpoints...")
        
        try:
            # Create test data
            user = User.objects.create_user(
                username='testuser_scheduling',
                email='testscheduling@example.com',
                password='testpass123'
            )
            
            org = Organization.objects.create(
                name='Test Scheduling Org',
                slug='test-scheduling-org'
            )
            
            OrganizationMember.objects.create(
                organization=org,
                user=user,
                role='admin'
            )
            
            # Test client setup
            self.client.force_login(user)
            
            # Test create scheduled post
            url = '/api/ai/schedule/'
            scheduled_time = timezone.now() + timedelta(hours=1)
            data = {
                'platform': 'facebook',
                'asset_url': 'https://example.com/image.jpg',
                'caption': 'Test scheduled post',
                'scheduled_time': scheduled_time.isoformat()
            }
            
            response = self.client.post(
                url,
                data,
                content_type='application/json',
                HTTP_X_ORGANIZATION=org.slug
            )
            
            if response.status_code in [200, 201]:
                self.log_test("Create Scheduled Post", True, "Scheduled post created successfully")
            else:
                self.log_test("Create Scheduled Post", False, f"Status: {response.status_code}, Content: {response.content.decode()[:200]}")
            
            # Test list scheduled posts
            response = self.client.get(
                url,
                HTTP_X_ORGANIZATION=org.slug
            )
            
            if response.status_code == 200:
                self.log_test("List Scheduled Posts", True, "Scheduled posts listed successfully")
            else:
                self.log_test("List Scheduled Posts", False, f"Status: {response.status_code}, Content: {response.content.decode()[:200]}")
                
        except Exception as e:
            self.log_test("Scheduling Endpoints", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Comprehensive Phase 1 Week 3 Testing...")
        print("=" * 70)
        
        self.test_social_media_service()
        self.test_arcjet_service()
        self.test_scheduled_post_model()
        self.test_textile_endpoints()
        self.test_scheduling_endpoints()
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['message']}")
        
        print("\n" + "=" * 70)
        if failed_tests == 0:
            print("🎉 ALL TESTS PASSED! Phase 1 Week 3 deliverables are working correctly!")
        else:
            print("⚠️  Some tests failed. Please review the issues above.")
        
        return failed_tests == 0


def main():
    """Main test runner"""
    test_suite = Phase1Week3TestSuite()
    success = test_suite.run_all_tests()
    return success


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
