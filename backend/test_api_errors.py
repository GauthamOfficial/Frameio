"""
Test backend APIs to identify and fix errors.
"""
import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from organizations.models import Organization, OrganizationMember, OrganizationInvitation

User = get_user_model()


class APIErrorTester(TestCase):
    """Test backend APIs to identify errors."""
    
    def setUp(self):
        """Set up test data."""
        # Create test organization
        self.organization = Organization.objects.create(
            name='Test Organization',
            slug='test-org',
            description='Test organization',
            subscription_plan='premium',
            subscription_status='active'
        )
        
        # Create test users
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
        
        self.designer_user = User.objects.create(
            username='designer@test.com',
            email='designer@test.com',
            first_name='Designer',
            last_name='User'
        )
        
        # Create organization memberships
        self.admin_membership = OrganizationMember.objects.create(
            organization=self.organization,
            user=self.admin_user,
            role='admin',
            can_invite_users=True,
            can_manage_billing=True,
            can_export_data=True
        )
        
        self.manager_membership = OrganizationMember.objects.create(
            organization=self.organization,
            user=self.manager_user,
            role='manager',
            can_invite_users=True,
            can_manage_billing=False,
            can_export_data=True
        )
        
        self.designer_membership = OrganizationMember.objects.create(
            organization=self.organization,
            user=self.designer_user,
            role='designer',
            can_invite_users=False,
            can_manage_billing=False,
            can_export_data=False
        )
        
        self.client = APIClient()
    
    def test_organization_apis_without_auth(self):
        """Test organization APIs without authentication."""
        print("\n🏢 Testing Organization APIs without authentication...")
        
        # Test list organizations
        response = self.client.get('/api/organizations/')
        print(f"  GET /api/organizations/ - Status: {response.status_code}")
        if response.status_code == 403:
            print("    ✅ Correctly requires authentication")
        else:
            print(f"    ❌ Unexpected status: {response.status_code}")
            print(f"    Response: {response.content.decode()}")
        
        # Test create organization
        data = {
            'name': 'New Organization',
            'description': 'Test organization',
            'website': 'https://test.com',
            'industry': 'Technology'
        }
        response = self.client.post('/api/organizations/', data, format='json')
        print(f"  POST /api/organizations/ - Status: {response.status_code}")
        if response.status_code == 403:
            print("    ✅ Correctly requires authentication")
        else:
            print(f"    ❌ Unexpected status: {response.status_code}")
            print(f"    Response: {response.content.decode()}")
    
    def test_user_apis_without_auth(self):
        """Test user APIs without authentication."""
        print("\n👥 Testing User APIs without authentication...")
        
        # Test list users
        response = self.client.get('/api/users/')
        print(f"  GET /api/users/ - Status: {response.status_code}")
        if response.status_code == 403:
            print("    ✅ Correctly requires authentication")
        else:
            print(f"    ❌ Unexpected status: {response.status_code}")
            print(f"    Response: {response.content.decode()}")
        
        # Test invite user
        data = {
            'email': 'newuser@test.com',
            'role': 'designer',
            'message': 'Welcome!'
        }
        response = self.client.post('/api/users/invite_user/', data, format='json')
        print(f"  POST /api/users/invite_user/ - Status: {response.status_code}")
        if response.status_code == 403:
            print("    ✅ Correctly requires authentication")
        else:
            print(f"    ❌ Unexpected status: {response.status_code}")
            print(f"    Response: {response.content.decode()}")
    
    def test_organization_apis_with_auth(self):
        """Test organization APIs with authentication."""
        print("\n🔐 Testing Organization APIs with authentication...")
        
        # Authenticate as admin user
        self.client.force_authenticate(user=self.admin_user)
        
        # Test list organizations
        response = self.client.get('/api/organizations/')
        print(f"  GET /api/organizations/ - Status: {response.status_code}")
        if response.status_code == 200:
            print("    ✅ Successfully retrieved organizations")
            data = response.json()
            print(f"    📊 Found {len(data.get('results', []))} organizations")
        else:
            print(f"    ❌ Unexpected status: {response.status_code}")
            print(f"    Response: {response.content.decode()}")
        
        # Test get organization details
        response = self.client.get(f'/api/organizations/{self.organization.id}/')
        print(f"  GET /api/organizations/{self.organization.id}/ - Status: {response.status_code}")
        if response.status_code == 200:
            print("    ✅ Successfully retrieved organization details")
        else:
            print(f"    ❌ Unexpected status: {response.status_code}")
            print(f"    Response: {response.content.decode()}")
        
        # Test update organization
        data = {
            'name': 'Updated Organization',
            'description': 'Updated description'
        }
        response = self.client.patch(f'/api/organizations/{self.organization.id}/', data, format='json')
        print(f"  PATCH /api/organizations/{self.organization.id}/ - Status: {response.status_code}")
        if response.status_code == 200:
            print("    ✅ Successfully updated organization")
        else:
            print(f"    ❌ Unexpected status: {response.status_code}")
            print(f"    Response: {response.content.decode()}")
    
    def test_user_apis_with_auth(self):
        """Test user APIs with authentication."""
        print("\n🔐 Testing User APIs with authentication...")
        
        # Authenticate as admin user
        self.client.force_authenticate(user=self.admin_user)
        
        # Test list users
        response = self.client.get('/api/users/')
        print(f"  GET /api/users/ - Status: {response.status_code}")
        if response.status_code == 200:
            print("    ✅ Successfully retrieved users")
            data = response.json()
            print(f"    📊 Found {len(data.get('results', []))} users")
        else:
            print(f"    ❌ Unexpected status: {response.status_code}")
            print(f"    Response: {response.content.decode()}")
        
        # Test invite user
        data = {
            'email': 'newuser@test.com',
            'role': 'designer',
            'message': 'Welcome to our organization!'
        }
        response = self.client.post('/api/users/invite_user/', data, format='json')
        print(f"  POST /api/users/invite_user/ - Status: {response.status_code}")
        if response.status_code == 201:
            print("    ✅ Successfully invited user")
        else:
            print(f"    ❌ Unexpected status: {response.status_code}")
            print(f"    Response: {response.content.decode()}")
        
        # Test get user permissions
        response = self.client.get('/api/users/permissions/')
        print(f"  GET /api/users/permissions/ - Status: {response.status_code}")
        if response.status_code == 200:
            print("    ✅ Successfully retrieved user permissions")
            data = response.json()
            print(f"    📊 User role: {data.get('role')}")
        else:
            print(f"    ❌ Unexpected status: {response.status_code}")
            print(f"    Response: {response.content.decode()}")
    
    def test_organization_member_apis(self):
        """Test organization member APIs."""
        print("\n👥 Testing Organization Member APIs...")
        
        # Authenticate as admin user
        self.client.force_authenticate(user=self.admin_user)
        
        # Test get organization members
        response = self.client.get(f'/api/organizations/{self.organization.id}/members/')
        print(f"  GET /api/organizations/{self.organization.id}/members/ - Status: {response.status_code}")
        if response.status_code == 200:
            print("    ✅ Successfully retrieved organization members")
            data = response.json()
            print(f"    📊 Found {len(data)} members")
        else:
            print(f"    ❌ Unexpected status: {response.status_code}")
            print(f"    Response: {response.content.decode()}")
        
        # Test invite member
        data = {
            'email': 'newmember@test.com',
            'role': 'designer'
        }
        response = self.client.post(f'/api/organizations/{self.organization.id}/invite_member/', data, format='json')
        print(f"  POST /api/organizations/{self.organization.id}/invite_member/ - Status: {response.status_code}")
        if response.status_code == 201:
            print("    ✅ Successfully invited member")
        else:
            print(f"    ❌ Unexpected status: {response.status_code}")
            print(f"    Response: {response.content.decode()}")
    
    def test_role_based_access(self):
        """Test role-based access control."""
        print("\n🔒 Testing Role-Based Access Control...")
        
        # Test admin access
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/users/')
        print(f"  Admin access to /api/users/ - Status: {response.status_code}")
        if response.status_code == 200:
            print("    ✅ Admin can access user management")
        else:
            print(f"    ❌ Admin access denied: {response.status_code}")
        
        # Test designer access (should be denied)
        self.client.force_authenticate(user=self.designer_user)
        response = self.client.get('/api/users/')
        print(f"  Designer access to /api/users/ - Status: {response.status_code}")
        if response.status_code == 403:
            print("    ✅ Designer correctly denied access to user management")
        else:
            print(f"    ❌ Designer should be denied access: {response.status_code}")
    
    def run_all_tests(self):
        """Run all API tests."""
        print("🚀 Starting Backend API Error Testing")
        print("=" * 60)
        
        self.test_organization_apis_without_auth()
        self.test_user_apis_without_auth()
        self.test_organization_apis_with_auth()
        self.test_user_apis_with_auth()
        self.test_organization_member_apis()
        self.test_role_based_access()
        
        print("\n" + "=" * 60)
        print("✅ Backend API testing completed!")


def main():
    """Main test runner."""
    tester = APIErrorTester()
    tester.setUp()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
