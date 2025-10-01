from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Organization, OrganizationMember, OrganizationInvitation

User = get_user_model()


class OrganizationModelTest(TestCase):
    """Test cases for Organization model."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name='Test Organization',
            slug='test-org',
            description='Test organization description'
        )
    
    def test_organization_creation(self):
        """Test organization creation."""
        self.assertEqual(self.organization.name, 'Test Organization')
        self.assertEqual(self.organization.slug, 'test-org')
        self.assertTrue(self.organization.is_active)
    
    def test_ai_usage_tracking(self):
        """Test AI usage tracking."""
        # Test initial usage
        self.assertEqual(self.organization.ai_generations_used, 0)
        self.assertTrue(self.organization.can_generate_ai)
        
        # Test incrementing usage
        self.organization.increment_ai_usage()
        self.assertEqual(self.organization.ai_generations_used, 1)
        
        # Test usage limit
        self.organization.ai_generations_used = self.organization.ai_generations_limit
        self.organization.save()
        self.assertFalse(self.organization.can_generate_ai)


class OrganizationMemberModelTest(TestCase):
    """Test cases for OrganizationMember model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.organization = Organization.objects.create(
            name='Test Organization',
            slug='test-org'
        )
        self.membership = OrganizationMember.objects.create(
            organization=self.organization,
            user=self.user,
            role='owner'
        )
    
    def test_membership_creation(self):
        """Test membership creation."""
        self.assertEqual(self.membership.organization, self.organization)
        self.assertEqual(self.membership.user, self.user)
        self.assertEqual(self.membership.role, 'owner')
        self.assertTrue(self.membership.is_owner)
        self.assertTrue(self.membership.is_admin)
    
    def test_role_permissions(self):
        """Test role-based permissions."""
        # Test owner permissions
        self.assertTrue(self.membership.is_owner)
        self.assertTrue(self.membership.is_admin)
        
        # Test admin role
        admin_membership = OrganizationMember.objects.create(
            organization=self.organization,
            user=User.objects.create_user(username='admin', email='admin@test.com'),
            role='admin'
        )
        self.assertFalse(admin_membership.is_owner)
        self.assertTrue(admin_membership.is_admin)


class OrganizationInvitationModelTest(TestCase):
    """Test cases for OrganizationInvitation model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.organization = Organization.objects.create(
            name='Test Organization',
            slug='test-org'
        )
        self.invitation = OrganizationInvitation.objects.create(
            organization=self.organization,
            email='invitee@example.com',
            role='designer',
            invited_by=self.user,
            token='test-token'
        )
    
    def test_invitation_creation(self):
        """Test invitation creation."""
        self.assertEqual(self.invitation.organization, self.organization)
        self.assertEqual(self.invitation.email, 'invitee@example.com')
        self.assertEqual(self.invitation.role, 'designer')
        self.assertEqual(self.invitation.status, 'pending')
    
    def test_invitation_acceptance(self):
        """Test invitation acceptance."""
        new_user = User.objects.create_user(
            username='newuser',
            email='invitee@example.com',
            password='testpass123'
        )
        
        # Accept invitation
        self.assertTrue(self.invitation.accept(new_user))
        
        # Check if membership was created
        membership = OrganizationMember.objects.get(
            organization=self.organization,
            user=new_user
        )
        self.assertEqual(membership.role, 'designer')
        
        # Check invitation status
        self.invitation.refresh_from_db()
        self.assertEqual(self.invitation.status, 'accepted')
    
    def test_invitation_decline(self):
        """Test invitation decline."""
        self.assertTrue(self.invitation.decline())
        
        # Check invitation status
        self.invitation.refresh_from_db()
        self.assertEqual(self.invitation.status, 'declined')


class OrganizationAPITest(APITestCase):
    """Test cases for Organization API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.organization = Organization.objects.create(
            name='Test Organization',
            slug='test-org'
        )
        self.membership = OrganizationMember.objects.create(
            organization=self.organization,
            user=self.user,
            role='owner',
            can_invite_users=True,
            can_manage_billing=True,
            can_export_data=True
        )
        self.client = APIClient()
    
    def test_organization_list_authenticated(self):
        """Test organization list for authenticated user."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/organizations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_organization_list_unauthenticated(self):
        """Test organization list for unauthenticated user."""
        response = self.client.get('/api/organizations/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_organization_creation(self):
        """Test organization creation."""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'name': 'New Organization',
            'description': 'New organization description',
            'website': 'https://example.com',
            'industry': 'Technology'
        }
        
        response = self.client.post('/api/organizations/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check if organization was created
        org = Organization.objects.get(name='New Organization')
        self.assertEqual(org.name, 'New Organization')
        
        # Check if user became owner
        membership = OrganizationMember.objects.get(
            organization=org,
            user=self.user
        )
        self.assertEqual(membership.role, 'owner')
    
    def test_organization_members(self):
        """Test organization members endpoint."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get(f'/api/organizations/{self.organization.id}/members/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_organization_usage(self):
        """Test organization usage endpoint."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get(f'/api/organizations/{self.organization.id}/usage/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check usage data
        self.assertIn('ai_generations_used', response.data)
        self.assertIn('ai_generations_limit', response.data)
        self.assertIn('usage_percentage', response.data)
    
    def test_organization_invitation(self):
        """Test organization invitation."""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'email': 'newuser@example.com',
            'role': 'designer'
        }
        
        response = self.client.post(f'/api/organizations/{self.organization.id}/invite_member/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check if invitation was created
        invitation = OrganizationInvitation.objects.get(
            organization=self.organization,
            email='newuser@example.com'
        )
        self.assertEqual(invitation.role, 'designer')
    
    def test_tenant_isolation(self):
        """Test tenant isolation - users can only access their organizations."""
        # Create another user and organization
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        other_org = Organization.objects.create(
            name='Other Organization',
            slug='other-org'
        )
        
        # Authenticate as other user
        self.client.force_authenticate(user=other_user)
        
        # Try to access first user's organization
        response = self.client.get(f'/api/organizations/{self.organization.id}/members/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)