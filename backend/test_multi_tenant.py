#!/usr/bin/env python
"""
Comprehensive test cases for multi-tenant Django application.
"""
import os
import django
import json
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from organizations.models import Organization, OrganizationMember, OrganizationInvitation
from users.models import User

User = get_user_model()


class MultiTenantTestCase(APITestCase):
    """
    Test cases for multi-tenant functionality.
    """
    
    def setUp(self):
        """Set up test data."""
        # Create test users
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@test.com',
            password='testpass123'
        )
        
        # Create test organizations
        self.org1 = Organization.objects.create(
            name='Test Organization 1',
            slug='test-org-1',
            description='Test organization 1'
        )
        self.org2 = Organization.objects.create(
            name='Test Organization 2',
            slug='test-org-2',
            description='Test organization 2'
        )
        
        # Create organization memberships
        self.membership1 = OrganizationMember.objects.create(
            organization=self.org1,
            user=self.user1,
            role='owner',
            can_invite_users=True,
            can_manage_billing=True,
            can_export_data=True
        )
        
        self.membership2 = OrganizationMember.objects.create(
            organization=self.org2,
            user=self.user2,
            role='admin',
            can_invite_users=True,
            can_manage_billing=False,
            can_export_data=True
        )
        
        # Create API client
        self.client = APIClient()
    
    def test_organization_creation(self):
        """Test organization creation."""
        self.client.force_authenticate(user=self.user1)
        
        data = {
            'name': 'New Test Organization',
            'description': 'A new test organization',
            'website': 'https://test.com',
            'industry': 'Technology'
        }
        
        response = self.client.post('/api/organizations/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check if organization was created
        org = Organization.objects.get(name='New Test Organization')
        self.assertEqual(org.name, 'New Test Organization')
        
        # Check if user became owner
        membership = OrganizationMember.objects.get(
            organization=org,
            user=self.user1
        )
        self.assertEqual(membership.role, 'owner')
    
    def test_organization_list(self):
        """Test organization listing."""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.get('/api/organizations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should only see organizations where user is a member
        org_names = [org['name'] for org in response.data['results']]
        self.assertIn('Test Organization 1', org_names)
        self.assertNotIn('Test Organization 2', org_names)
    
    def test_organization_members(self):
        """Test organization members listing."""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.get(f'/api/organizations/{self.org1.id}/members/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should see the member
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['user_email'], 'user1@test.com')
    
    def test_organization_invitation(self):
        """Test organization invitation."""
        self.client.force_authenticate(user=self.user1)
        
        data = {
            'email': 'newuser@test.com',
            'role': 'designer'
        }
        
        response = self.client.post(f'/api/organizations/{self.org1.id}/invite_member/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check if invitation was created
        invitation = OrganizationInvitation.objects.get(
            organization=self.org1,
            email='newuser@test.com'
        )
        self.assertEqual(invitation.role, 'designer')
        self.assertEqual(invitation.invited_by, self.user1)
    
    def test_organization_usage(self):
        """Test organization usage statistics."""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.get(f'/api/organizations/{self.org1.id}/usage/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check usage data
        self.assertIn('ai_generations_used', response.data)
        self.assertIn('ai_generations_limit', response.data)
        self.assertIn('usage_percentage', response.data)
    
    def test_tenant_isolation(self):
        """Test that users can only access their own organization data."""
        self.client.force_authenticate(user=self.user1)
        
        # Try to access organization 2 (user1 is not a member)
        response = self.client.get(f'/api/organizations/{self.org2.id}/members/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_organization_member_permissions(self):
        """Test organization member permissions."""
        self.client.force_authenticate(user=self.user2)
        
        # user2 is admin in org2, should be able to invite
        data = {
            'email': 'newmember@test.com',
            'role': 'designer'
        }
        
        response = self.client.post(f'/api/organizations/{self.org2.id}/invite_member/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_organization_update_permissions(self):
        """Test organization update permissions."""
        self.client.force_authenticate(user=self.user1)
        
        data = {
            'name': 'Updated Organization Name',
            'description': 'Updated description'
        }
        
        response = self.client.patch(f'/api/organizations/{self.org1.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check if organization was updated
        self.org1.refresh_from_db()
        self.assertEqual(self.org1.name, 'Updated Organization Name')
    
    def test_organization_deletion(self):
        """Test organization deletion (owner only)."""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.delete(f'/api/organizations/{self.org1.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Check if organization was deleted
        self.assertFalse(Organization.objects.filter(id=self.org1.id).exists())
    
    def test_ai_usage_tracking(self):
        """Test AI usage tracking."""
        # Increment AI usage
        self.org1.increment_ai_usage()
        self.org1.refresh_from_db()
        
        self.assertEqual(self.org1.ai_generations_used, 1)
        
        # Check if can generate AI
        self.assertTrue(self.org1.can_generate_ai)
        
        # Set usage to limit
        self.org1.ai_generations_used = self.org1.ai_generations_limit
        self.org1.save()
        
        # Should not be able to generate AI
        self.assertFalse(self.org1.can_generate_ai)
    
    def test_organization_member_roles(self):
        """Test organization member roles and permissions."""
        # Test owner permissions
        self.assertTrue(self.membership1.is_owner)
        self.assertTrue(self.membership1.is_admin)
        
        # Test admin permissions
        self.assertFalse(self.membership2.is_owner)
        self.assertTrue(self.membership2.is_admin)
        
        # Test role-based permissions
        self.assertTrue(self.membership1.can_invite_users)
        self.assertTrue(self.membership1.can_manage_billing)
        self.assertTrue(self.membership1.can_export_data)
        
        self.assertTrue(self.membership2.can_invite_users)
        self.assertFalse(self.membership2.can_manage_billing)
        self.assertTrue(self.membership2.can_export_data)
    
    def test_invitation_acceptance(self):
        """Test invitation acceptance."""
        # Create invitation
        invitation = OrganizationInvitation.objects.create(
            organization=self.org1,
            email='newuser@test.com',
            role='designer',
            invited_by=self.user1,
            token='test-token',
            expires_at='2024-12-31 23:59:59'
        )
        
        # Create new user
        new_user = User.objects.create_user(
            username='newuser',
            email='newuser@test.com',
            password='testpass123'
        )
        
        # Accept invitation
        self.assertTrue(invitation.accept(new_user))
        
        # Check if membership was created
        membership = OrganizationMember.objects.get(
            organization=self.org1,
            user=new_user
        )
        self.assertEqual(membership.role, 'designer')
        self.assertTrue(membership.is_active)
        
        # Check invitation status
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, 'accepted')
    
    def test_invitation_decline(self):
        """Test invitation decline."""
        # Create invitation
        invitation = OrganizationInvitation.objects.create(
            organization=self.org1,
            email='decline@test.com',
            role='designer',
            invited_by=self.user1,
            token='test-token',
            expires_at='2024-12-31 23:59:59'
        )
        
        # Decline invitation
        self.assertTrue(invitation.decline())
        
        # Check invitation status
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, 'declined')
    
    def test_user_organizations(self):
        """Test user's organization access."""
        # Get user's organizations
        orgs = self.user1.get_organizations()
        self.assertIn(self.org1, orgs)
        self.assertNotIn(self.org2, orgs)
        
        # Check organization access
        self.assertTrue(self.user1.can_access_organization(self.org1))
        self.assertFalse(self.user1.can_access_organization(self.org2))
    
    def test_organization_subscription_plans(self):
        """Test organization subscription plans."""
        # Test free plan limits
        self.assertEqual(self.org1.subscription_plan, 'free')
        self.assertEqual(self.org1.ai_generations_limit, 10)
        
        # Test subscription status
        self.assertTrue(self.org1.is_active)
        self.assertEqual(self.org1.subscription_status, 'active')
        
        # Test usage tracking
        self.assertEqual(self.org1.ai_generations_used, 0)
        self.assertTrue(self.org1.can_generate_ai)
    
    def test_organization_serialization(self):
        """Test organization serialization."""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.get(f'/api/organizations/{self.org1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check serialized data
        data = response.data
        self.assertEqual(data['name'], 'Test Organization 1')
        self.assertEqual(data['slug'], 'test-org-1')
        self.assertIn('members_count', data)
        self.assertIn('is_owner', data)
        self.assertIn('user_role', data)
        self.assertTrue(data['is_owner'])
        self.assertEqual(data['user_role'], 'owner')


def run_tests():
    """Run all tests."""
    print("Running Multi-Tenant Test Suite...")
    print("=" * 50)
    
    # Create test suite
    from django.test.runner import DiscoverRunner
    
    runner = DiscoverRunner(verbosity=2)
    test_suite = runner.build_suite(['organizations', 'users'])
    
    # Run tests
    result = runner.run_tests(['organizations', 'users'])
    
    if result:
        print("\n" + "=" * 50)
        print("✅ All tests passed!")
    else:
        print("\n" + "=" * 50)
        print("❌ Some tests failed!")
    
    return result


if __name__ == '__main__':
    run_tests()
