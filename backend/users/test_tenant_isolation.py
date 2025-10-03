"""
Comprehensive tests for tenant isolation and role-based permissions.
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from rest_framework.test import APITestCase, force_authenticate
from rest_framework import status
from unittest.mock import patch

from organizations.models import Organization, OrganizationMember, OrganizationInvitation
from users.models import User, UserProfile, UserActivity
from users.views import UserViewSet, UserProfileViewSet
from users.permissions import (
    IsOrganizationMember, IsOrganizationAdmin, IsOrganizationManager,
    CanManageUsers, CanManageBilling, CanExportData, get_user_organization_permissions
)
from designs.models import Design, DesignTemplate, DesignCatalog
from organizations.mixins import TenantScopedModel, TenantScopedManager

User = get_user_model()


class TenantIsolationTestCase(TestCase):
    """
    Test cases for tenant isolation functionality.
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
            role='admin',
            can_invite_users=True,
            can_manage_billing=True,
            can_export_data=True
        )
        self.membership2 = OrganizationMember.objects.create(
            organization=self.org2,
            user=self.user2,
            role='designer',
            can_invite_users=False,
            can_manage_billing=False,
            can_export_data=False
        )
    
    def test_tenant_scoped_model_organization_assignment(self):
        """Test that TenantScopedModel automatically assigns organization."""
        # Mock the current organization context
        with patch('organizations.mixins.get_current_organization', return_value=self.org1):
            # Create a design without specifying organization
            design = Design.objects.create(
                title='Test Design',
                created_by=self.user1
            )
            
            # The organization should be automatically assigned
            self.assertEqual(design.organization, self.org1)
    
    def test_tenant_scoped_manager_filtering(self):
        """Test that TenantScopedManager filters by organization."""
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
        
        # Test filtering by organization using the for_organization method
        designs_org1 = Design.objects.for_organization(self.org1)
        self.assertEqual(designs_org1.count(), 1)
        self.assertEqual(designs_org1.first(), design1)
        
        designs_org2 = Design.objects.for_organization(self.org2)
        self.assertEqual(designs_org2.count(), 1)
        self.assertEqual(designs_org2.first(), design2)
    
    def test_cross_tenant_data_isolation(self):
        """Test that users cannot access data from other tenants."""
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
        
        # Test that designs are properly isolated by organization
        designs_org1 = Design.objects.for_organization(self.org1)
        self.assertEqual(designs_org1.count(), 1)
        self.assertEqual(designs_org1.first(), design1)
        
        designs_org2 = Design.objects.for_organization(self.org2)
        self.assertEqual(designs_org2.count(), 1)
        self.assertEqual(designs_org2.first(), design2)
        
        # Test that cross-organization access is prevented
        self.assertNotIn(design2, designs_org1)
        self.assertNotIn(design1, designs_org2)
    
    def test_organization_member_access_control(self):
        """Test that organization members can only access their organization's data."""
        # Create user profiles
        profile1 = UserProfile.objects.create(
            user=self.user1,
            current_organization=self.org1
        )
        profile2 = UserProfile.objects.create(
            user=self.user2,
            current_organization=self.org2
        )
        
        # Test that profiles are properly isolated by organization
        profiles_org1 = UserProfile.objects.filter(
            user__organization_memberships__organization=self.org1,
            user__organization_memberships__is_active=True
        ).distinct()
        self.assertEqual(profiles_org1.count(), 1)
        self.assertEqual(profiles_org1.first(), profile1)
        
        profiles_org2 = UserProfile.objects.filter(
            user__organization_memberships__organization=self.org2,
            user__organization_memberships__is_active=True
        ).distinct()
        self.assertEqual(profiles_org2.count(), 1)
        self.assertEqual(profiles_org2.first(), profile2)
    
    def test_tenant_scoped_viewset_mixin(self):
        """Test TenantScopedViewSetMixin functionality."""
        factory = RequestFactory()
        request = factory.get('/api/users/')
        request.organization = self.org1
        request.user = self.user1
        
        viewset = UserViewSet()
        viewset.request = request
        
        # Test get_queryset filtering
        queryset = viewset.get_queryset()
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first(), self.user1)
    
    def test_ensure_tenant_access_function(self):
        """Test the ensure_tenant_access helper function."""
        from organizations.mixins import ensure_tenant_access
        
        # Valid access should not raise exception
        ensure_tenant_access(self.user1, self.org1)
        
        # Invalid access should raise PermissionDenied
        with self.assertRaises(PermissionDenied):
            ensure_tenant_access(self.user1, self.org2)


class RoleBasedPermissionsTestCase(TestCase):
    """
    Test cases for role-based permissions.
    """
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name='Test Organization',
            slug='test-org',
            description='Test organization'
        )
        
        # Create users with different roles
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
    
    def test_organization_member_permission(self):
        """Test IsOrganizationMember permission."""
        permission = IsOrganizationMember()
        factory = RequestFactory()
        
        # Create request with organization context
        request = factory.get('/api/users/')
        request.organization = self.organization
        
        # Test with admin user
        request.user = self.admin_user
        self.assertTrue(permission.has_permission(request, None))
        
        # Test with non-member user
        non_member = User.objects.create(
            username='nonmember@test.com',
            email='nonmember@test.com'
        )
        request.user = non_member
        self.assertFalse(permission.has_permission(request, None))
    
    def test_organization_admin_permission(self):
        """Test IsOrganizationAdmin permission."""
        permission = IsOrganizationAdmin()
        factory = RequestFactory()
        
        request = factory.get('/api/users/')
        request.organization = self.organization
        
        # Admin should have permission
        request.user = self.admin_user
        self.assertTrue(permission.has_permission(request, None))
        
        # Manager should not have admin permission
        request.user = self.manager_user
        self.assertFalse(permission.has_permission(request, None))
        
        # Designer should not have admin permission
        request.user = self.designer_user
        self.assertFalse(permission.has_permission(request, None))
    
    def test_organization_manager_permission(self):
        """Test IsOrganizationManager permission."""
        permission = IsOrganizationManager()
        factory = RequestFactory()
        
        request = factory.get('/api/users/')
        request.organization = self.organization
        
        # Admin should have manager permission
        request.user = self.admin_user
        self.assertTrue(permission.has_permission(request, None))
        
        # Manager should have manager permission
        request.user = self.manager_user
        self.assertTrue(permission.has_permission(request, None))
        
        # Designer should not have manager permission
        request.user = self.designer_user
        self.assertFalse(permission.has_permission(request, None))
    
    def test_can_manage_users_permission(self):
        """Test CanManageUsers permission."""
        permission = CanManageUsers()
        factory = RequestFactory()
        
        request = factory.get('/api/users/')
        request.organization = self.organization
        
        # Admin should be able to manage users
        request.user = self.admin_user
        self.assertTrue(permission.has_permission(request, None))
        
        # Manager should be able to manage users
        request.user = self.manager_user
        self.assertTrue(permission.has_permission(request, None))
        
        # Designer should not be able to manage users
        request.user = self.designer_user
        self.assertFalse(permission.has_permission(request, None))
    
    def test_can_manage_billing_permission(self):
        """Test CanManageBilling permission."""
        permission = CanManageBilling()
        factory = RequestFactory()
        
        request = factory.get('/api/billing/')
        request.organization = self.organization
        
        # Admin should be able to manage billing
        request.user = self.admin_user
        self.assertTrue(permission.has_permission(request, None))
        
        # Manager should not be able to manage billing
        request.user = self.manager_user
        self.assertFalse(permission.has_permission(request, None))
        
        # Designer should not be able to manage billing
        request.user = self.designer_user
        self.assertFalse(permission.has_permission(request, None))
    
    def test_can_export_data_permission(self):
        """Test CanExportData permission."""
        permission = CanExportData()
        factory = RequestFactory()
        
        request = factory.get('/api/export/')
        request.organization = self.organization
        
        # Admin should be able to export data
        request.user = self.admin_user
        self.assertTrue(permission.has_permission(request, None))
        
        # Manager should be able to export data
        request.user = self.manager_user
        self.assertTrue(permission.has_permission(request, None))
        
        # Designer should not be able to export data
        request.user = self.designer_user
        self.assertFalse(permission.has_permission(request, None))
    
    def test_get_user_organization_permissions(self):
        """Test get_user_organization_permissions function."""
        # Test admin permissions
        admin_perms = get_user_organization_permissions(self.admin_user, self.organization)
        self.assertIsNotNone(admin_perms)
        self.assertEqual(admin_perms['role'], 'admin')
        self.assertTrue(admin_perms['can_invite_users'])
        self.assertTrue(admin_perms['can_manage_billing'])
        self.assertTrue(admin_perms['can_export_data'])
        self.assertTrue(admin_perms['is_admin'])
        self.assertTrue(admin_perms['is_manager'])
        self.assertTrue(admin_perms['is_designer'])
        
        # Test manager permissions
        manager_perms = get_user_organization_permissions(self.manager_user, self.organization)
        self.assertIsNotNone(manager_perms)
        self.assertEqual(manager_perms['role'], 'manager')
        self.assertTrue(manager_perms['can_invite_users'])
        self.assertFalse(manager_perms['can_manage_billing'])
        self.assertTrue(manager_perms['can_export_data'])
        self.assertFalse(manager_perms['is_admin'])
        self.assertTrue(manager_perms['is_manager'])
        self.assertTrue(manager_perms['is_designer'])
        
        # Test designer permissions
        designer_perms = get_user_organization_permissions(self.designer_user, self.organization)
        self.assertIsNotNone(designer_perms)
        self.assertEqual(designer_perms['role'], 'designer')
        self.assertFalse(designer_perms['can_invite_users'])
        self.assertFalse(designer_perms['can_manage_billing'])
        self.assertFalse(designer_perms['can_export_data'])
        self.assertFalse(designer_perms['is_admin'])
        self.assertFalse(designer_perms['is_manager'])
        self.assertTrue(designer_perms['is_designer'])
        
        # Test non-member
        non_member = User.objects.create(
            username='nonmember@test.com',
            email='nonmember@test.com'
        )
        non_member_perms = get_user_organization_permissions(non_member, self.organization)
        self.assertIsNone(non_member_perms)


class UserManagementAPITestCase(APITestCase):
    """
    Test cases for user management APIs.
    """
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name='Test Organization',
            slug='test-org',
            description='Test organization'
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
    
    def test_list_users_as_admin(self):
        """Test listing users as admin."""
        self.client.force_authenticate(user=self.admin_user)
        
        # Mock organization context in the request
        response = self.client.get('/api/users/', HTTP_X_ORGANIZATION=self.organization.slug)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)  # All 3 users
    
    def test_list_users_as_designer(self):
        """Test listing users as designer (should fail)."""
        self.client.force_authenticate(user=self.designer_user)
        
        # Mock organization context in the request
        response = self.client.get('/api/users/', HTTP_X_ORGANIZATION=self.organization.slug)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_invite_user_as_admin(self):
        """Test inviting user as admin."""
        self.client.force_authenticate(user=self.admin_user)
        
        # Mock organization context in the request
        data = {
            'email': 'newuser@test.com',
            'role': 'designer',
            'message': 'Welcome to our organization!'
        }
        response = self.client.post('/api/users/invite_user/', data, HTTP_X_ORGANIZATION=self.organization.slug)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that invitation was created
        invitation = OrganizationInvitation.objects.get(email='newuser@test.com')
        self.assertEqual(invitation.organization, self.organization)
        self.assertEqual(invitation.role, 'designer')
    
    def test_invite_user_as_designer(self):
        """Test inviting user as designer (should fail)."""
        self.client.force_authenticate(user=self.designer_user)
        
        # Mock organization context in the request
        data = {
            'email': 'newuser@test.com',
            'role': 'designer',
            'message': 'Welcome to our organization!'
        }
        response = self.client.post('/api/users/invite_user/', data, HTTP_X_ORGANIZATION=self.organization.slug)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_user_role_as_admin(self):
        """Test updating user role as admin."""
        self.client.force_authenticate(user=self.admin_user)
        
        # Mock organization context in the request
        data = {'role': 'manager'}
        response = self.client.post(f'/api/users/{self.designer_user.id}/update_role/', data, HTTP_X_ORGANIZATION=self.organization.slug)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that role was updated
        self.designer_membership.refresh_from_db()
        self.assertEqual(self.designer_membership.role, 'manager')
    
    def test_update_user_role_as_designer(self):
        """Test updating user role as designer (should fail)."""
        self.client.force_authenticate(user=self.designer_user)
        
        # Mock organization context in the request
        data = {'role': 'manager'}
        response = self.client.post(f'/api/users/{self.manager_user.id}/update_role/', data, HTTP_X_ORGANIZATION=self.organization.slug)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_remove_user_from_organization_as_admin(self):
        """Test removing user from organization as admin."""
        self.client.force_authenticate(user=self.admin_user)
        
        # Mock organization context in the request
        response = self.client.post(f'/api/users/{self.designer_user.id}/remove_from_organization/', HTTP_X_ORGANIZATION=self.organization.slug)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that membership was deactivated
        self.designer_membership.refresh_from_db()
        self.assertFalse(self.designer_membership.is_active)
    
    def test_remove_last_admin_should_fail(self):
        """Test that removing the last admin should fail."""
        self.client.force_authenticate(user=self.admin_user)
        
        # Mock organization context in the request
        response = self.client.post(f'/api/users/{self.admin_user.id}/remove_from_organization/', HTTP_X_ORGANIZATION=self.organization.slug)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('last admin', response.data['error'])
    
    def test_get_user_permissions(self):
        """Test getting user permissions."""
        self.client.force_authenticate(user=self.admin_user)
        
        # Mock organization context in the request
        response = self.client.get('/api/users/permissions/', HTTP_X_ORGANIZATION=self.organization.slug)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        permissions = response.data
        self.assertEqual(permissions['role'], 'admin')
        self.assertTrue(permissions['can_invite_users'])
        self.assertTrue(permissions['can_manage_billing'])
        self.assertTrue(permissions['can_export_data'])
    
    def test_cross_tenant_user_access_denied(self):
        """Test that users cannot access users from other organizations."""
        # Create another organization and user
        other_org = Organization.objects.create(
            name='Other Organization',
            slug='other-org',
            description='Other organization'
        )
        other_user = User.objects.create(
            username='other@test.com',
            email='other@test.com',
            first_name='Other',
            last_name='User'
        )
        OrganizationMember.objects.create(
            organization=other_org,
            user=other_user,
            role='admin'
        )
        
        self.client.force_authenticate(user=self.admin_user)
        
        # Mock organization context in the request
        response = self.client.get(f'/api/users/{other_user.id}/', HTTP_X_ORGANIZATION=self.organization.slug)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
