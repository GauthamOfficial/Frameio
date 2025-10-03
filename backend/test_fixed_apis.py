"""
Test the fixed APIs to verify they work correctly.
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
from organizations.models import Organization, OrganizationMember, OrganizationInvitation

User = get_user_model()


class FixedAPITest(TestCase):
    """Test the fixed APIs."""
    
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
        
        # Create users
        self.admin_user = User.objects.create(
            username='admin@test.com',
            email='admin@test.com',
            first_name='Admin',
            last_name='User'
        )
        
        self.manager_user = User.objects.create(
            username='manager@test.com',
            email='manager@test.com',
            first_name='Manager',
            last_name='User'
        )
        
        # Create memberships
        self.admin_membership = OrganizationMember.objects.create(
            organization=self.org,
            user=self.admin_user,
            role='admin',
            can_invite_users=True,
            can_manage_billing=True,
            can_export_data=True
        )
        
        self.manager_membership = OrganizationMember.objects.create(
            organization=self.org,
            user=self.manager_user,
            role='manager',
            can_invite_users=True,
            can_manage_billing=False,
            can_export_data=True
        )
        
        self.client = APIClient()
    
    def test_organization_list(self):
        """Test organization list endpoint."""
        print("Testing organization list...")
        
        # Test without authentication
        response = self.client.get('/api/organizations/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        print("✅ Correctly requires authentication")
        
        # Test with authentication
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/organizations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("✅ Successfully retrieved organizations")
        
        data = response.json()
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['name'], 'Test Organization')
        print("✅ Correct organization returned")
    
    def test_organization_detail(self):
        """Test organization detail endpoint."""
        print("Testing organization detail...")
        
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f'/api/organizations/{self.org.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("✅ Successfully retrieved organization details")
        
        data = response.json()
        self.assertEqual(data['name'], 'Test Organization')
        print("✅ Correct organization details returned")
    
    def test_organization_members(self):
        """Test organization members endpoint."""
        print("Testing organization members...")
        
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f'/api/organizations/{self.org.id}/members/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("✅ Successfully retrieved organization members")
        
        data = response.json()
        self.assertEqual(len(data), 2)  # admin and manager
        print("✅ Correct number of members returned")
    
    def test_organization_invite_member(self):
        """Test organization invite member endpoint."""
        print("Testing organization invite member...")
        
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'email': 'newmember@test.com',
            'role': 'designer'
        }
        response = self.client.post(f'/api/organizations/{self.org.id}/invite_member/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        print("✅ Successfully invited member")
        
        # Check that invitation was created
        invitation = OrganizationInvitation.objects.get(email='newmember@test.com')
        self.assertEqual(invitation.organization, self.org)
        self.assertEqual(invitation.role, 'designer')
        print("✅ Invitation created correctly")
    
    def test_user_list(self):
        """Test user list endpoint."""
        print("Testing user list...")
        
        # Test without authentication
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        print("✅ Correctly requires authentication")
        
        # Test with authentication
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("✅ Successfully retrieved users")
        
        data = response.json()
        self.assertEqual(len(data['results']), 2)  # admin and manager
        print("✅ Correct number of users returned")
    
    def test_user_invite(self):
        """Test user invite endpoint."""
        print("Testing user invite...")
        
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'email': 'newuser@test.com',
            'role': 'designer',
            'message': 'Welcome!'
        }
        response = self.client.post('/api/users/invite_user/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        print("✅ Successfully invited user")
        
        # Check that invitation was created
        invitation = OrganizationInvitation.objects.get(email='newuser@test.com')
        self.assertEqual(invitation.organization, self.org)
        self.assertEqual(invitation.role, 'designer')
        print("✅ Invitation created correctly")
    
    def test_user_permissions(self):
        """Test user permissions endpoint."""
        print("Testing user permissions...")
        
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/users/permissions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("✅ Successfully retrieved user permissions")
        
        data = response.json()
        self.assertEqual(data['role'], 'admin')
        self.assertTrue(data['can_invite_users'])
        self.assertTrue(data['can_manage_billing'])
        self.assertTrue(data['can_export_data'])
        print("✅ Correct permissions returned")
    
    def run_all_tests(self):
        """Run all tests."""
        print("🚀 Testing Fixed APIs")
        print("=" * 50)
        
        self.test_organization_list()
        self.test_organization_detail()
        self.test_organization_members()
        self.test_organization_invite_member()
        self.test_user_list()
        self.test_user_invite()
        self.test_user_permissions()
        
        print("\n" + "=" * 50)
        print("✅ All API tests passed!")


def main():
    """Main test runner."""
    test = FixedAPITest()
    test.setUp()
    test.run_all_tests()


if __name__ == "__main__":
    main()
