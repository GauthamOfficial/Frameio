from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import User, UserSession, UserActivity

User = get_user_model()


class UserModelTest(TestCase):
    """Test cases for User model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_user_creation(self):
        """Test user creation."""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.first_name, 'Test')
        self.assertEqual(self.user.last_name, 'User')
    
    def test_user_full_name(self):
        """Test user full name property."""
        self.assertEqual(self.user.full_name, 'Test User')
        
        # Test with only first name
        self.user.last_name = ''
        self.user.save()
        self.assertEqual(self.user.full_name, 'Test')
        
        # Test with only last name
        self.user.first_name = ''
        self.user.last_name = 'User'
        self.user.save()
        self.assertEqual(self.user.full_name, 'User')
    
    def test_user_organizations(self):
        """Test user organization access."""
        # Initially no organizations
        self.assertEqual(len(self.user.get_organizations()), 0)
        
        # Create organization and membership
        from organizations.models import Organization, OrganizationMember
        org = Organization.objects.create(
            name='Test Organization',
            slug='test-org'
        )
        OrganizationMember.objects.create(
            organization=org,
            user=self.user,
            role='owner'
        )
        
        # Now should have one organization
        orgs = self.user.get_organizations()
        self.assertEqual(len(orgs), 1)
        self.assertIn(org, orgs)
    
    def test_user_organization_access(self):
        """Test user organization access control."""
        from organizations.models import Organization, OrganizationMember
        
        # Create organizations
        org1 = Organization.objects.create(name='Org 1', slug='org-1')
        org2 = Organization.objects.create(name='Org 2', slug='org-2')
        
        # User is member of org1 only
        OrganizationMember.objects.create(
            organization=org1,
            user=self.user,
            role='owner'
        )
        
        # Test access
        self.assertTrue(self.user.can_access_organization(org1))
        self.assertFalse(self.user.can_access_organization(org2))


class UserSessionModelTest(TestCase):
    """Test cases for UserSession model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        from django.utils import timezone
        from datetime import timedelta
        
        self.session = UserSession.objects.create(
            user=self.user,
            session_key='test-session-key',
            ip_address='127.0.0.1',
            user_agent='Test User Agent',
            expires_at=timezone.now() + timedelta(hours=24)
        )
    
    def test_session_creation(self):
        """Test session creation."""
        self.assertEqual(self.session.user, self.user)
        self.assertEqual(self.session.session_key, 'test-session-key')
        self.assertEqual(self.session.ip_address, '127.0.0.1')
        self.assertTrue(self.session.is_active)
    
    def test_session_deactivation(self):
        """Test session deactivation."""
        self.assertTrue(self.session.is_active)
        self.session.deactivate()
        self.assertFalse(self.session.is_active)


class UserActivityModelTest(TestCase):
    """Test cases for UserActivity model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.activity = UserActivity.objects.create(
            user=self.user,
            action='login',
            description='User logged in',
            ip_address='127.0.0.1'
        )
    
    def test_activity_creation(self):
        """Test activity creation."""
        self.assertEqual(self.activity.user, self.user)
        self.assertEqual(self.activity.action, 'login')
        self.assertEqual(self.activity.description, 'User logged in')
        self.assertEqual(self.activity.ip_address, '127.0.0.1')
    
    def test_activity_metadata(self):
        """Test activity metadata."""
        activity = UserActivity.objects.create(
            user=self.user,
            action='design_created',
            description='User created a design',
            ip_address='127.0.0.1',
            metadata={'design_id': '123', 'design_type': 'poster'}
        )
        
        self.assertEqual(activity.metadata['design_id'], '123')
        self.assertEqual(activity.metadata['design_type'], 'poster')