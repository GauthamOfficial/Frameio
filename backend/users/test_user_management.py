"""
Unit tests for user management APIs.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import User, UserProfile
from .views import UserViewSet, UserProfileViewSet
from organizations.models import Organization, OrganizationMember, OrganizationInvitation

User = get_user_model()


class UserManagementAPITestCase(APITestCase):
    """Base test case for user management API tests."""
    
    def setUp(self):
        """Set up test data."""
        # Create test organization
        self.organization = Organization.objects.create(
            name='Test Organization',
            slug='test-org',
            description='Test organization for API tests'
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
        
        # Set up API client
        self.client = APIClient()
        
        # Mock organization context
        self.client.force_authenticate(user=self.admin_user)
        self.client.defaults['HTTP_X_ORGANIZATION'] = 'test-org'


class UserListViewTest(UserManagementAPITestCase):
    """Test user list view."""
    
    def test_list_users_success(self):
        """Test successful user list retrieval."""
        url = reverse('user-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # admin, manager, designer
        
        # Check that only organization members are returned
        user_emails = [user['email'] for user in response.data]
        self.assertIn('admin@test.com', user_emails)
        self.assertIn('manager@test.com', user_emails)
        self.assertIn('designer@test.com', user_emails)
        self.assertNotIn('other@test.com', user_emails)
    
    def test_list_users_without_organization_context(self):
        """Test user list without organization context."""
        # Remove organization header
        self.client.defaults.pop('HTTP_X_ORGANIZATION', None)
        
        url = reverse('user-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # No organization context
    
    def test_list_users_unauthorized(self):
        """Test user list without authentication."""
        self.client.force_authenticate(user=None)
        
        url = reverse('user-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserDetailViewTest(UserManagementAPITestCase):
    """Test user detail view."""
    
    def test_retrieve_user_success(self):
        """Test successful user retrieval."""
        url = reverse('user-detail', kwargs={'pk': self.manager_user.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'manager@test.com')
        self.assertEqual(response.data['role'], 'manager')
    
    def test_retrieve_user_not_in_organization(self):
        """Test retrieving user not in organization."""
        url = reverse('user-detail', kwargs={'pk': self.other_user.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_retrieve_nonexistent_user(self):
        """Test retrieving nonexistent user."""
        url = reverse('user-detail', kwargs={'pk': '00000000-0000-0000-0000-000000000000'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UserUpdateViewTest(UserManagementAPITestCase):
    """Test user update view."""
    
    def test_update_own_profile_success(self):
        """Test user updating their own profile."""
        url = reverse('user-detail', kwargs={'pk': self.admin_user.id})
        data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')
        self.assertEqual(response.data['last_name'], 'Name')
    
    def test_admin_update_other_user_success(self):
        """Test admin updating another user's profile."""
        url = reverse('user-detail', kwargs={'pk': self.manager_user.id})
        data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')
        self.assertEqual(response.data['last_name'], 'Name')
    
    def test_non_admin_cannot_update_other_user(self):
        """Test non-admin cannot update another user's profile."""
        # Login as manager
        self.client.force_authenticate(user=self.manager_user)
        
        url = reverse('user-detail', kwargs={'pk': self.designer_user.id})
        data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UserRoleUpdateTest(UserManagementAPITestCase):
    """Test user role update functionality."""
    
    def test_admin_update_user_role_success(self):
        """Test admin updating user role."""
        url = reverse('user-update-role', kwargs={'pk': self.manager_user.id})
        data = {
            'role': 'designer',
            'can_invite_users': False,
            'can_export_data': False
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['role'], 'designer')
        self.assertFalse(response.data['permissions']['can_invite_users'])
        self.assertFalse(response.data['permissions']['can_export_data'])
    
    def test_manager_cannot_assign_admin_role(self):
        """Test manager cannot assign admin role."""
        # Login as manager
        self.client.force_authenticate(user=self.manager_user)
        
        url = reverse('user-update-role', kwargs={'pk': self.designer_user.id})
        data = {
            'role': 'admin'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Only admins can assign admin role', str(response.data))
    
    def test_update_nonexistent_user_role(self):
        """Test updating role for nonexistent user."""
        url = reverse('user-update-role', kwargs={'pk': '00000000-0000-0000-0000-000000000000'})
        data = {
            'role': 'designer'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UserInviteTest(UserManagementAPITestCase):
    """Test user invitation functionality."""
    
    def test_admin_invite_user_success(self):
        """Test admin inviting a new user."""
        url = reverse('user-invite-user')
        data = {
            'email': 'newuser@test.com',
            'role': 'designer',
            'message': 'Welcome to our organization!'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Invitation sent successfully')
        
        # Check that invitation was created
        invitation = OrganizationInvitation.objects.get(
            organization=self.organization,
            email='newuser@test.com'
        )
        self.assertEqual(invitation.role, 'designer')
        self.assertEqual(invitation.invited_by, self.admin_user)
    
    def test_invite_existing_member_fails(self):
        """Test inviting existing member fails."""
        url = reverse('user-invite-user')
        data = {
            'email': 'manager@test.com',  # Already a member
            'role': 'designer'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already a member', str(response.data))
    
    def test_designer_cannot_invite_users(self):
        """Test designer cannot invite users."""
        # Login as designer
        self.client.force_authenticate(user=self.designer_user)
        
        url = reverse('user-invite-user')
        data = {
            'email': 'newuser@test.com',
            'role': 'designer'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UserRemoveTest(UserManagementAPITestCase):
    """Test user removal functionality."""
    
    def test_admin_remove_user_success(self):
        """Test admin removing a user."""
        url = reverse('user-remove-from-organization', kwargs={'pk': self.designer_user.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'User removed from organization successfully')
        
        # Check that membership was deactivated
        membership = OrganizationMember.objects.get(
            organization=self.organization,
            user=self.designer_user
        )
        self.assertFalse(membership.is_active)
    
    def test_cannot_remove_last_admin(self):
        """Test cannot remove the last admin."""
        url = reverse('user-remove-from-organization', kwargs={'pk': self.admin_user.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Cannot remove the last admin', str(response.data))
    
    def test_remove_nonexistent_user(self):
        """Test removing nonexistent user."""
        url = reverse('user-remove-from-organization', kwargs={'pk': '00000000-0000-0000-0000-000000000000'})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UserInvitationsListTest(UserManagementAPITestCase):
    """Test user invitations list functionality."""
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        
        # Create some invitations
        self.invitation1 = OrganizationInvitation.objects.create(
            organization=self.organization,
            email='invite1@test.com',
            role='designer',
            invited_by=self.admin_user,
            token='token1'
        )
        
        self.invitation2 = OrganizationInvitation.objects.create(
            organization=self.organization,
            email='invite2@test.com',
            role='manager',
            invited_by=self.admin_user,
            token='token2'
        )
    
    def test_list_invitations_success(self):
        """Test successful invitations list retrieval."""
        url = reverse('user-invitations')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # Check invitation data
        invitation_emails = [inv['email'] for inv in response.data]
        self.assertIn('invite1@test.com', invitation_emails)
        self.assertIn('invite2@test.com', invitation_emails)
    
    def test_list_invitations_without_organization_context(self):
        """Test invitations list without organization context."""
        # Remove organization header
        self.client.defaults.pop('HTTP_X_ORGANIZATION', None)
        
        url = reverse('user-invitations')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('No organization context', str(response.data))


class UserPermissionsTest(UserManagementAPITestCase):
    """Test user permissions functionality."""
    
    def test_get_user_permissions_success(self):
        """Test successful user permissions retrieval."""
        url = reverse('user-permissions')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['role'], 'admin')
        self.assertTrue(response.data['can_invite_users'])
        self.assertTrue(response.data['can_manage_billing'])
        self.assertTrue(response.data['can_export_data'])
        self.assertTrue(response.data['is_admin'])
    
    def test_get_permissions_without_organization_context(self):
        """Test permissions without organization context."""
        # Remove organization header
        self.client.defaults.pop('HTTP_X_ORGANIZATION', None)
        
        url = reverse('user-permissions')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('No organization context', str(response.data))


class UserProfileViewTest(UserManagementAPITestCase):
    """Test user profile view functionality."""
    
    def test_retrieve_own_profile_success(self):
        """Test user retrieving their own profile."""
        url = reverse('profile-detail', kwargs={'pk': self.admin_user.profile.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user_email'], 'admin@test.com')
    
    def test_admin_retrieve_other_profile_success(self):
        """Test admin retrieving another user's profile."""
        url = reverse('profile-detail', kwargs={'pk': self.manager_user.profile.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user_email'], 'manager@test.com')
    
    def test_non_admin_cannot_retrieve_other_profile(self):
        """Test non-admin cannot retrieve another user's profile."""
        # Login as manager
        self.client.force_authenticate(user=self.manager_user)
        
        url = reverse('profile-detail', kwargs={'pk': self.designer_user.profile.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_own_profile_success(self):
        """Test user updating their own profile."""
        url = reverse('profile-detail', kwargs={'pk': self.admin_user.profile.pk})
        data = {
            'job_title': 'Senior Administrator',
            'department': 'IT'
        }
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['job_title'], 'Senior Administrator')
        self.assertEqual(response.data['department'], 'IT')
