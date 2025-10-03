"""
Comprehensive tests for organization management APIs and tenant isolation.
"""
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch
from django.utils import timezone
from datetime import timedelta

from organizations.models import Organization, OrganizationMember, OrganizationInvitation
from users.models import User, UserProfile
from designs.models import Design, DesignTemplate, DesignCatalog


class OrganizationManagementTestCase(APITestCase):
    """
    Test cases for organization management functionality.
    """
    
    def setUp(self):
        """Set up test data."""
        # Create organizations
        self.org1 = Organization.objects.create(
            name='Organization 1',
            slug='org1',
            description='First organization',
            subscription_plan='premium',
            subscription_status='active'
        )
        self.org2 = Organization.objects.create(
            name='Organization 2',
            slug='org2',
            description='Second organization',
            subscription_plan='basic',
            subscription_status='active'
        )
        
        # Create users
        self.owner_user = User.objects.create(
            username='owner@test.com',
            email='owner@test.com',
            first_name='Owner',
            last_name='User'
        )
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
        self.owner_membership = OrganizationMember.objects.create(
            organization=self.org1,
            user=self.owner_user,
            role='owner',
            can_invite_users=True,
            can_manage_billing=True,
            can_export_data=True
        )
        self.admin_membership = OrganizationMember.objects.create(
            organization=self.org1,
            user=self.admin_user,
            role='admin',
            can_invite_users=True,
            can_manage_billing=True,
            can_export_data=True
        )
        self.manager_membership = OrganizationMember.objects.create(
            organization=self.org1,
            user=self.manager_user,
            role='manager',
            can_invite_users=True,
            can_manage_billing=False,
            can_export_data=True
        )
        self.designer_membership = OrganizationMember.objects.create(
            organization=self.org1,
            user=self.designer_user,
            role='designer',
            can_invite_users=False,
            can_manage_billing=False,
            can_export_data=False
        )
    
    def test_create_organization(self):
        """Test creating a new organization."""
        new_user = User.objects.create(
            username='newuser@test.com',
            email='newuser@test.com',
            first_name='New',
            last_name='User'
        )
        
        self.client.force_authenticate(user=new_user)
        
        data = {
            'name': 'New Organization',
            'description': 'A new organization',
            'website': 'https://neworg.com',
            'industry': 'Technology'
        }
        
        response = self.client.post('/api/organizations/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that organization was created
        org = Organization.objects.get(name='New Organization')
        self.assertEqual(org.description, 'A new organization')
        
        # Check that creator became owner
        membership = OrganizationMember.objects.get(
            organization=org,
            user=new_user
        )
        self.assertEqual(membership.role, 'owner')
    
    def test_list_organizations(self):
        """Test listing organizations for a user."""
        self.client.force_authenticate(user=self.owner_user)
        
        response = self.client.get('/api/organizations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should only see organizations where user is a member
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Organization 1')
    
    def test_get_organization_details(self):
        """Test getting organization details."""
        self.client.force_authenticate(user=self.owner_user)
        
        response = self.client.get(f'/api/organizations/{self.org1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data
        self.assertEqual(data['name'], 'Organization 1')
        self.assertEqual(data['slug'], 'org1')
        self.assertEqual(data['user_role'], 'owner')
        self.assertTrue(data['is_owner'])
    
    def test_update_organization_as_owner(self):
        """Test updating organization as owner."""
        self.client.force_authenticate(user=self.owner_user)
        
        data = {
            'name': 'Updated Organization 1',
            'description': 'Updated description',
            'website': 'https://updated.com'
        }
        
        response = self.client.patch(f'/api/organizations/{self.org1.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that organization was updated
        self.org1.refresh_from_db()
        self.assertEqual(self.org1.name, 'Updated Organization 1')
        self.assertEqual(self.org1.description, 'Updated description')
    
    def test_update_organization_as_designer(self):
        """Test updating organization as designer (should fail)."""
        self.client.force_authenticate(user=self.designer_user)
        
        data = {
            'name': 'Updated Organization 1',
            'description': 'Updated description'
        }
        
        response = self.client.patch(f'/api/organizations/{self.org1.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_delete_organization_as_owner(self):
        """Test deleting organization as owner."""
        self.client.force_authenticate(user=self.owner_user)
        
        response = self.client.delete(f'/api/organizations/{self.org1.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Check that organization was deleted
        self.assertFalse(Organization.objects.filter(id=self.org1.id).exists())
    
    def test_delete_organization_as_admin(self):
        """Test deleting organization as admin (should fail)."""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.delete(f'/api/organizations/{self.org1.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_get_organization_members(self):
        """Test getting organization members."""
        self.client.force_authenticate(user=self.owner_user)
        
        response = self.client.get(f'/api/organizations/{self.org1.id}/members/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should see all active members
        self.assertEqual(len(response.data), 4)  # owner, admin, manager, designer
    
    def test_invite_member_as_admin(self):
        """Test inviting a member as admin."""
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'email': 'newmember@test.com',
            'role': 'designer'
        }
        
        response = self.client.post(f'/api/organizations/{self.org1.id}/invite_member/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that invitation was created
        invitation = OrganizationInvitation.objects.get(email='newmember@test.com')
        self.assertEqual(invitation.organization, self.org1)
        self.assertEqual(invitation.role, 'designer')
        self.assertEqual(invitation.invited_by, self.admin_user)
    
    def test_invite_member_as_designer(self):
        """Test inviting a member as designer (should fail)."""
        self.client.force_authenticate(user=self.designer_user)
        
        data = {
            'email': 'newmember@test.com',
            'role': 'designer'
        }
        
        response = self.client.post(f'/api/organizations/{self.org1.id}/invite_member/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_get_organization_invitations(self):
        """Test getting organization invitations."""
        # Create an invitation
        invitation = OrganizationInvitation.objects.create(
            organization=self.org1,
            email='invited@test.com',
            role='designer',
            invited_by=self.admin_user,
            token='test-token',
            expires_at=timezone.now() + timedelta(days=7)
        )
        
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(f'/api/organizations/{self.org1.id}/invitations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should see the invitation
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['email'], 'invited@test.com')
    
    def test_get_organization_usage(self):
        """Test getting organization usage statistics."""
        self.client.force_authenticate(user=self.owner_user)
        
        response = self.client.get(f'/api/organizations/{self.org1.id}/usage/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data
        self.assertIn('ai_generations_used', data)
        self.assertIn('ai_generations_limit', data)
        self.assertIn('usage_percentage', data)
        self.assertIn('subscription_plan', data)
        self.assertIn('subscription_status', data)
    
    def test_accept_invitation(self):
        """Test accepting an organization invitation."""
        # Create an invitation
        invitation = OrganizationInvitation.objects.create(
            organization=self.org1,
            email='invited@test.com',
            role='designer',
            invited_by=self.admin_user,
            token='test-token',
            expires_at=timezone.now() + timedelta(days=7)
        )
        
        # Create user for invitation
        invited_user = User.objects.create(
            username='invited@test.com',
            email='invited@test.com',
            first_name='Invited',
            last_name='User'
        )
        
        self.client.force_authenticate(user=invited_user)
        
        response = self.client.post(f'/api/invitations/{invitation.id}/accept/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that membership was created
        membership = OrganizationMember.objects.get(
            organization=self.org1,
            user=invited_user
        )
        self.assertEqual(membership.role, 'designer')
        
        # Check that invitation status was updated
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, 'accepted')
    
    def test_decline_invitation(self):
        """Test declining an organization invitation."""
        # Create an invitation
        invitation = OrganizationInvitation.objects.create(
            organization=self.org1,
            email='invited@test.com',
            role='designer',
            invited_by=self.admin_user,
            token='test-token',
            expires_at=timezone.now() + timedelta(days=7)
        )
        
        # Create user for invitation
        invited_user = User.objects.create(
            username='invited@test.com',
            email='invited@test.com',
            first_name='Invited',
            last_name='User'
        )
        
        self.client.force_authenticate(user=invited_user)
        
        response = self.client.post(f'/api/invitations/{invitation.id}/decline/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that invitation status was updated
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, 'declined')
        
        # Check that no membership was created
        self.assertFalse(OrganizationMember.objects.filter(
            organization=self.org1,
            user=invited_user
        ).exists())
    
    def test_cross_organization_access_denied(self):
        """Test that users cannot access other organizations."""
        self.client.force_authenticate(user=self.owner_user)
        
        # Try to access org2 (user is not a member)
        response = self.client.get(f'/api/organizations/{self.org2.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Try to get members of org2
        response = self.client.get(f'/api/organizations/{self.org2.id}/members/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OrganizationDataIsolationTestCase(TestCase):
    """
    Test cases for organization data isolation.
    """
    
    def setUp(self):
        """Set up test data."""
        # Create organizations
        self.org1 = Organization.objects.create(
            name='Organization 1',
            slug='org1',
            description='First organization'
        )
        self.org2 = Organization.objects.create(
            name='Organization 2',
            slug='org2',
            description='Second organization'
        )
        
        # Create users
        self.user1 = User.objects.create(
            username='user1@org1.com',
            email='user1@org1.com',
            first_name='User',
            last_name='One'
        )
        self.user2 = User.objects.create(
            username='user2@org2.com',
            email='user2@org2.com',
            first_name='User',
            last_name='Two'
        )
        
        # Create organization memberships
        self.membership1 = OrganizationMember.objects.create(
            organization=self.org1,
            user=self.user1,
            role='admin'
        )
        self.membership2 = OrganizationMember.objects.create(
            organization=self.org2,
            user=self.user2,
            role='admin'
        )
    
    def test_design_isolation(self):
        """Test that designs are isolated between organizations."""
        # Create designs for both organizations
        design1 = Design.objects.create(
            title='Design 1',
            organization=self.org1,
            created_by=self.user1
        )
        design2 = Design.objects.create(
            title='Design 2',
            organization=self.org2,
            created_by=self.user2
        )
        
        # Mock organization context for org1
        with patch('organizations.middleware.get_current_organization', return_value=self.org1):
            designs = Design.objects.all()
            self.assertEqual(designs.count(), 1)
            self.assertEqual(designs.first(), design1)
        
        # Mock organization context for org2
        with patch('organizations.middleware.get_current_organization', return_value=self.org2):
            designs = Design.objects.all()
            self.assertEqual(designs.count(), 1)
            self.assertEqual(designs.first(), design2)
    
    def test_template_isolation(self):
        """Test that templates are isolated between organizations."""
        # Create templates for both organizations
        template1 = DesignTemplate.objects.create(
            name='Template 1',
            organization=self.org1,
            created_by=self.user1
        )
        template2 = DesignTemplate.objects.create(
            name='Template 2',
            organization=self.org2,
            created_by=self.user2
        )
        
        # Mock organization context for org1
        with patch('organizations.middleware.get_current_organization', return_value=self.org1):
            templates = DesignTemplate.objects.all()
            self.assertEqual(templates.count(), 1)
            self.assertEqual(templates.first(), template1)
        
        # Mock organization context for org2
        with patch('organizations.middleware.get_current_organization', return_value=self.org2):
            templates = DesignTemplate.objects.all()
            self.assertEqual(templates.count(), 1)
            self.assertEqual(templates.first(), template2)
    
    def test_catalog_isolation(self):
        """Test that catalogs are isolated between organizations."""
        # Create catalogs for both organizations
        catalog1 = DesignCatalog.objects.create(
            name='Catalog 1',
            organization=self.org1,
            created_by=self.user1
        )
        catalog2 = DesignCatalog.objects.create(
            name='Catalog 2',
            organization=self.org2,
            created_by=self.user2
        )
        
        # Mock organization context for org1
        with patch('organizations.middleware.get_current_organization', return_value=self.org1):
            catalogs = DesignCatalog.objects.all()
            self.assertEqual(catalogs.count(), 1)
            self.assertEqual(catalogs.first(), catalog1)
        
        # Mock organization context for org2
        with patch('organizations.middleware.get_current_organization', return_value=self.org2):
            catalogs = DesignCatalog.objects.all()
            self.assertEqual(catalogs.count(), 1)
            self.assertEqual(catalogs.first(), catalog2)
    
    def test_user_profile_isolation(self):
        """Test that user profiles are isolated between organizations."""
        # Create user profiles
        profile1 = UserProfile.objects.create(
            user=self.user1,
            current_organization=self.org1
        )
        profile2 = UserProfile.objects.create(
            user=self.user2,
            current_organization=self.org2
        )
        
        # Mock organization context for org1
        with patch('organizations.middleware.get_current_organization', return_value=self.org1):
            profiles = UserProfile.objects.all()
            self.assertEqual(profiles.count(), 1)
            self.assertEqual(profiles.first(), profile1)
        
        # Mock organization context for org2
        with patch('organizations.middleware.get_current_organization', return_value=self.org2):
            profiles = UserProfile.objects.all()
            self.assertEqual(profiles.count(), 1)
            self.assertEqual(profiles.first(), profile2)
    
    def test_organization_member_isolation(self):
        """Test that organization members are isolated between organizations."""
        # Mock organization context for org1
        with patch('organizations.middleware.get_current_organization', return_value=self.org1):
            members = OrganizationMember.objects.all()
            self.assertEqual(members.count(), 1)
            self.assertEqual(members.first(), self.membership1)
        
        # Mock organization context for org2
        with patch('organizations.middleware.get_current_organization', return_value=self.org2):
            members = OrganizationMember.objects.all()
            self.assertEqual(members.count(), 1)
            self.assertEqual(members.first(), self.membership2)
