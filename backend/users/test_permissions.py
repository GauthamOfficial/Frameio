"""
Unit tests for user permissions and role-based access control.
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from rest_framework.test import APIRequestFactory
from rest_framework import status
from unittest.mock import patch

from .models import User, UserProfile
from .permissions import (
    IsOrganizationMember, IsOrganizationAdmin, IsOrganizationManager,
    IsOrganizationDesigner, CanManageUsers, CanManageBilling, CanExportData,
    RoleBasedPermission, get_user_organization_permissions
)
from organizations.models import Organization, OrganizationMember

User = get_user_model()


class PermissionTestCase(TestCase):
    """Base test case for permission tests."""
    
    def setUp(self):
        """Set up test data."""
        self.factory = APIRequestFactory()
        
        # Create test organization
        self.organization = Organization.objects.create(
            name='Test Organization',
            slug='test-org',
            description='Test organization for unit tests'
        )
        
        # Create test users
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123'
        )
        
        self.manager_user = User.objects.create_user(
            username='manager',
            email='manager@test.com',
            password='testpass123'
        )
        
        self.designer_user = User.objects.create_user(
            username='designer',
            email='designer@test.com',
            password='testpass123'
        )
        
        self.other_user = User.objects.create_user(
            username='other',
            email='other@test.com',
            password='testpass123'
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
        
        # Create user profiles
        UserProfile.objects.create(
            user=self.admin_user,
            current_organization=self.organization
        )
        
        UserProfile.objects.create(
            user=self.manager_user,
            current_organization=self.organization
        )
        
        UserProfile.objects.create(
            user=self.designer_user,
            current_organization=self.organization
        )


class IsOrganizationMemberTest(PermissionTestCase):
    """Test IsOrganizationMember permission class."""
    
    def test_authenticated_member_has_permission(self):
        """Test that authenticated organization members have permission."""
        request = self.factory.get('/')
        request.user = self.admin_user
        request.organization = self.organization
        
        permission = IsOrganizationMember()
        self.assertTrue(permission.has_permission(request, None))
    
    def test_unauthenticated_user_no_permission(self):
        """Test that unauthenticated users don't have permission."""
        request = self.factory.get('/')
        request.user = None
        request.organization = self.organization
        
        permission = IsOrganizationMember()
        self.assertFalse(permission.has_permission(request, None))
    
    def test_non_member_no_permission(self):
        """Test that non-members don't have permission."""
        request = self.factory.get('/')
        request.user = self.other_user
        request.organization = self.organization
        
        permission = IsOrganizationMember()
        self.assertFalse(permission.has_permission(request, None))
    
    def test_no_organization_context_no_permission(self):
        """Test that users without organization context don't have permission."""
        request = self.factory.get('/')
        request.user = self.admin_user
        request.organization = None
        
        permission = IsOrganizationMember()
        self.assertFalse(permission.has_permission(request, None))


class IsOrganizationAdminTest(PermissionTestCase):
    """Test IsOrganizationAdmin permission class."""
    
    def test_admin_has_permission(self):
        """Test that admin users have permission."""
        request = self.factory.get('/')
        request.user = self.admin_user
        request.organization = self.organization
        
        permission = IsOrganizationAdmin()
        self.assertTrue(permission.has_permission(request, None))
    
    def test_manager_no_permission(self):
        """Test that manager users don't have admin permission."""
        request = self.factory.get('/')
        request.user = self.manager_user
        request.organization = self.organization
        
        permission = IsOrganizationAdmin()
        self.assertFalse(permission.has_permission(request, None))
    
    def test_designer_no_permission(self):
        """Test that designer users don't have admin permission."""
        request = self.factory.get('/')
        request.user = self.designer_user
        request.organization = self.organization
        
        permission = IsOrganizationAdmin()
        self.assertFalse(permission.has_permission(request, None))


class IsOrganizationManagerTest(PermissionTestCase):
    """Test IsOrganizationManager permission class."""
    
    def test_admin_has_permission(self):
        """Test that admin users have manager permission."""
        request = self.factory.get('/')
        request.user = self.admin_user
        request.organization = self.organization
        
        permission = IsOrganizationManager()
        self.assertTrue(permission.has_permission(request, None))
    
    def test_manager_has_permission(self):
        """Test that manager users have permission."""
        request = self.factory.get('/')
        request.user = self.manager_user
        request.organization = self.organization
        
        permission = IsOrganizationManager()
        self.assertTrue(permission.has_permission(request, None))
    
    def test_designer_no_permission(self):
        """Test that designer users don't have manager permission."""
        request = self.factory.get('/')
        request.user = self.designer_user
        request.organization = self.organization
        
        permission = IsOrganizationManager()
        self.assertFalse(permission.has_permission(request, None))


class IsOrganizationDesignerTest(PermissionTestCase):
    """Test IsOrganizationDesigner permission class."""
    
    def test_admin_has_permission(self):
        """Test that admin users have designer permission."""
        request = self.factory.get('/')
        request.user = self.admin_user
        request.organization = self.organization
        
        permission = IsOrganizationDesigner()
        self.assertTrue(permission.has_permission(request, None))
    
    def test_manager_has_permission(self):
        """Test that manager users have designer permission."""
        request = self.factory.get('/')
        request.user = self.manager_user
        request.organization = self.organization
        
        permission = IsOrganizationDesigner()
        self.assertTrue(permission.has_permission(request, None))
    
    def test_designer_has_permission(self):
        """Test that designer users have permission."""
        request = self.factory.get('/')
        request.user = self.designer_user
        request.organization = self.organization
        
        permission = IsOrganizationDesigner()
        self.assertTrue(permission.has_permission(request, None))


class CanManageUsersTest(PermissionTestCase):
    """Test CanManageUsers permission class."""
    
    def test_admin_can_manage_users(self):
        """Test that admin users can manage users."""
        request = self.factory.get('/')
        request.user = self.admin_user
        request.organization = self.organization
        
        permission = CanManageUsers()
        self.assertTrue(permission.has_permission(request, None))
    
    def test_manager_can_manage_users(self):
        """Test that manager users can manage users."""
        request = self.factory.get('/')
        request.user = self.manager_user
        request.organization = self.organization
        
        permission = CanManageUsers()
        self.assertTrue(permission.has_permission(request, None))
    
    def test_designer_cannot_manage_users(self):
        """Test that designer users cannot manage users."""
        request = self.factory.get('/')
        request.user = self.designer_user
        request.organization = self.organization
        
        permission = CanManageUsers()
        self.assertFalse(permission.has_permission(request, None))


class CanManageBillingTest(PermissionTestCase):
    """Test CanManageBilling permission class."""
    
    def test_admin_can_manage_billing(self):
        """Test that admin users can manage billing."""
        request = self.factory.get('/')
        request.user = self.admin_user
        request.organization = self.organization
        
        permission = CanManageBilling()
        self.assertTrue(permission.has_permission(request, None))
    
    def test_manager_cannot_manage_billing(self):
        """Test that manager users cannot manage billing."""
        request = self.factory.get('/')
        request.user = self.manager_user
        request.organization = self.organization
        
        permission = CanManageBilling()
        self.assertFalse(permission.has_permission(request, None))
    
    def test_designer_cannot_manage_billing(self):
        """Test that designer users cannot manage billing."""
        request = self.factory.get('/')
        request.user = self.designer_user
        request.organization = self.organization
        
        permission = CanManageBilling()
        self.assertFalse(permission.has_permission(request, None))


class CanExportDataTest(PermissionTestCase):
    """Test CanExportData permission class."""
    
    def test_admin_can_export_data(self):
        """Test that admin users can export data."""
        request = self.factory.get('/')
        request.user = self.admin_user
        request.organization = self.organization
        
        permission = CanExportData()
        self.assertTrue(permission.has_permission(request, None))
    
    def test_manager_can_export_data(self):
        """Test that manager users can export data."""
        request = self.factory.get('/')
        request.user = self.manager_user
        request.organization = self.organization
        
        permission = CanExportData()
        self.assertTrue(permission.has_permission(request, None))
    
    def test_designer_cannot_export_data(self):
        """Test that designer users cannot export data."""
        request = self.factory.get('/')
        request.user = self.designer_user
        request.organization = self.organization
        
        permission = CanExportData()
        self.assertFalse(permission.has_permission(request, None))


class RoleBasedPermissionTest(PermissionTestCase):
    """Test RoleBasedPermission class."""
    
    def test_allowed_roles_have_permission(self):
        """Test that users with allowed roles have permission."""
        request = self.factory.get('/')
        request.user = self.admin_user
        request.organization = self.organization
        
        permission = RoleBasedPermission(allowed_roles=['admin', 'manager'])
        self.assertTrue(permission.has_permission(request, None))
    
    def test_disallowed_roles_no_permission(self):
        """Test that users with disallowed roles don't have permission."""
        request = self.factory.get('/')
        request.user = self.designer_user
        request.organization = self.organization
        
        permission = RoleBasedPermission(allowed_roles=['admin', 'manager'])
        self.assertFalse(permission.has_permission(request, None))


class GetUserOrganizationPermissionsTest(PermissionTestCase):
    """Test get_user_organization_permissions function."""
    
    def test_admin_permissions(self):
        """Test admin user permissions."""
        permissions = get_user_organization_permissions(
            self.admin_user, self.organization
        )
        
        self.assertIsNotNone(permissions)
        self.assertEqual(permissions['role'], 'admin')
        self.assertTrue(permissions['can_invite_users'])
        self.assertTrue(permissions['can_manage_billing'])
        self.assertTrue(permissions['can_export_data'])
        self.assertTrue(permissions['is_admin'])
        self.assertTrue(permissions['is_manager'])
        self.assertTrue(permissions['is_designer'])
    
    def test_manager_permissions(self):
        """Test manager user permissions."""
        permissions = get_user_organization_permissions(
            self.manager_user, self.organization
        )
        
        self.assertIsNotNone(permissions)
        self.assertEqual(permissions['role'], 'manager')
        self.assertTrue(permissions['can_invite_users'])
        self.assertFalse(permissions['can_manage_billing'])
        self.assertTrue(permissions['can_export_data'])
        self.assertFalse(permissions['is_admin'])
        self.assertTrue(permissions['is_manager'])
        self.assertTrue(permissions['is_designer'])
    
    def test_designer_permissions(self):
        """Test designer user permissions."""
        permissions = get_user_organization_permissions(
            self.designer_user, self.organization
        )
        
        self.assertIsNotNone(permissions)
        self.assertEqual(permissions['role'], 'designer')
        self.assertFalse(permissions['can_invite_users'])
        self.assertFalse(permissions['can_manage_billing'])
        self.assertFalse(permissions['can_export_data'])
        self.assertFalse(permissions['is_admin'])
        self.assertFalse(permissions['is_manager'])
        self.assertTrue(permissions['is_designer'])
    
    def test_non_member_no_permissions(self):
        """Test that non-members have no permissions."""
        permissions = get_user_organization_permissions(
            self.other_user, self.organization
        )
        
        self.assertIsNone(permissions)
