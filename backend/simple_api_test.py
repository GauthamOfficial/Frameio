"""
Simple API test to identify specific errors.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from organizations.models import Organization, OrganizationMember

User = get_user_model()


class SimpleAPITest(TestCase):
    """Simple API test to identify errors."""
    
    def setUp(self):
        """Set up test data."""
        # Create organization
        self.org = Organization.objects.create(
            name='Test Organization',
            slug='test-org',
            description='Test organization',
            subscription_plan='premium',
            subscription_status='active'
        )
        
        # Create user
        self.user = User.objects.create(
            username='test@test.com',
            email='test@test.com',
            first_name='Test',
            last_name='User'
        )
        
        # Create membership
        self.membership = OrganizationMember.objects.create(
            organization=self.org,
            user=self.user,
            role='admin',
            can_invite_users=True,
            can_manage_billing=True,
            can_export_data=True
        )
        
        self.client = APIClient()
    
    def test_organization_list(self):
        """Test organization list endpoint."""
        print("Testing organization list...")
        
        # Test without authentication
        response = self.client.get('/api/organizations/')
        print(f"Status without auth: {response.status_code}")
        
        # Test with authentication
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/organizations/')
        print(f"Status with auth: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data.get('results', []))} organizations")
        else:
            print(f"Error response: {response.content.decode()}")
    
    def test_user_list(self):
        """Test user list endpoint."""
        print("Testing user list...")
        
        # Test without authentication
        response = self.client.get('/api/users/')
        print(f"Status without auth: {response.status_code}")
        
        # Test with authentication
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/users/')
        print(f"Status with auth: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data.get('results', []))} users")
        else:
            print(f"Error response: {response.content.decode()}")


def run_test():
    """Run the simple test."""
    test = SimpleAPITest()
    test.setUp()
    test.test_organization_list()
    test.test_user_list()


if __name__ == "__main__":
    run_test()
