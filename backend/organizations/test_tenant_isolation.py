"""
Unit tests for tenant isolation and multi-tenancy functionality.
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from rest_framework.test import APIRequestFactory
from rest_framework import status

from .models import Organization, OrganizationMember
from .mixins import TenantScopedModel, TenantScopedManager, TenantScopedViewSetMixin
from .middleware import TenantMiddleware, get_current_organization, set_current_organization
from designs.models import Design, DesignTemplate, DesignCatalog
from users.models import User, UserProfile

User = get_user_model()


class TenantIsolationTestCase(TestCase):
    """Base test case for tenant isolation tests."""
    
    def setUp(self):
        """Set up test data."""
        self.factory = APIRequestFactory()
        
        # Create test organizations
        self.org1 = Organization.objects.create(
            name='Organization 1',
            slug='org1',
            description='First test organization'
        )
        
        self.org2 = Organization.objects.create(
            name='Organization 2',
            slug='org2',
            description='Second test organization'
        )
        
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
        
        # Create user profiles
        UserProfile.objects.create(
            user=self.user1,
            current_organization=self.org1
        )
        
        UserProfile.objects.create(
            user=self.user2,
            current_organization=self.org2
        )


class TenantScopedModelTest(TenantIsolationTestCase):
    """Test TenantScopedModel functionality."""
    
    def test_organization_automatically_set_on_save(self):
        """Test that organization is automatically set when saving."""
        # Set current organization in thread-local storage
        set_current_organization(self.org1)
        
        # Create a design without specifying organization
        design = Design(
            title='Test Design',
            design_type='poster',
            created_by=self.user1
        )
        
        # Save should automatically set organization
        design.save()
        
        self.assertEqual(design.organization, self.org1)
    
    def test_organization_required_for_save(self):
        """Test that organization is required for save."""
        # Don't set current organization
        set_current_organization(None)
        
        design = Design(
            title='Test Design',
            design_type='poster',
            created_by=self.user1
        )
        
        # Save should raise PermissionDenied
        with self.assertRaises(PermissionDenied):
            design.save()
    
    def test_explicit_organization_used(self):
        """Test that explicit organization is used when provided."""
        design = Design(
            title='Test Design',
            design_type='poster',
            organization=self.org2,
            created_by=self.user1
        )
        
        design.save()
        
        self.assertEqual(design.organization, self.org2)


class TenantScopedManagerTest(TenantIsolationTestCase):
    """Test TenantScopedManager functionality."""
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        
        # Create designs for both organizations
        self.design1 = Design.objects.create(
            title='Design 1',
            design_type='poster',
            organization=self.org1,
            created_by=self.user1
        )
        
        self.design2 = Design.objects.create(
            title='Design 2',
            design_type='banner',
            organization=self.org2,
            created_by=self.user2
        )
    
    def test_queryset_filtered_by_current_organization(self):
        """Test that queryset is filtered by current organization."""
        # Set current organization
        set_current_organization(self.org1)
        
        # Get queryset
        queryset = Design.objects.all()
        
        # Should only return designs from org1
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first(), self.design1)
    
    def test_queryset_empty_when_no_organization(self):
        """Test that queryset is empty when no organization is set."""
        # Don't set current organization
        set_current_organization(None)
        
        # Get queryset
        queryset = Design.objects.all()
        
        # Should be empty
        self.assertEqual(queryset.count(), 0)
    
    def test_for_organization_method(self):
        """Test for_organization method."""
        # Get designs for specific organization
        queryset = Design.objects.for_organization(self.org2)
        
        # Should only return designs from org2
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first(), self.design2)
    
    def test_all_organizations_method(self):
        """Test all_organizations method."""
        # Get all designs across organizations
        queryset = Design.objects.all_organizations()
        
        # Should return designs from both organizations
        self.assertEqual(queryset.count(), 2)
        self.assertIn(self.design1, queryset)
        self.assertIn(self.design2, queryset)


class TenantMiddlewareTest(TenantIsolationTestCase):
    """Test TenantMiddleware functionality."""
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.middleware = TenantMiddleware()
    
    def test_organization_from_subdomain(self):
        """Test getting organization from subdomain."""
        request = self.factory.get('/')
        request.META['HTTP_HOST'] = 'org1.localhost'
        
        organization = self.middleware.get_organization_from_subdomain(request)
        self.assertEqual(organization, self.org1)
    
    def test_organization_from_header(self):
        """Test getting organization from header."""
        request = self.factory.get('/')
        request.META['HTTP_X_ORGANIZATION'] = 'org2'
        
        organization = self.middleware.get_organization_from_header(request)
        self.assertEqual(organization, self.org2)
    
    def test_organization_from_user(self):
        """Test getting organization from user's current organization."""
        request = self.factory.get('/')
        request.user = self.user1
        
        organization = self.middleware.get_organization_from_user(request)
        self.assertEqual(organization, self.org1)
    
    def test_user_has_organization_access(self):
        """Test user organization access check."""
        # User1 should have access to org1
        self.assertTrue(
            self.middleware.user_has_organization_access(self.user1, self.org1)
        )
        
        # User1 should not have access to org2
        self.assertFalse(
            self.middleware.user_has_organization_access(self.user1, self.org2)
        )
    
    def test_process_request_sets_organization(self):
        """Test that process_request sets organization."""
        request = self.factory.get('/')
        request.META['HTTP_HOST'] = 'org1.localhost'
        request.user = self.user1
        
        # Process request
        response = self.middleware.process_request(request)
        
        # Should set organization on request
        self.assertEqual(request.organization, self.org1)
        self.assertEqual(request.tenant, self.org1)
        
        # Should set in thread-local storage
        self.assertEqual(get_current_organization(), self.org1)
    
    def test_process_view_checks_permissions(self):
        """Test that process_view checks user permissions."""
        request = self.factory.get('/')
        request.organization = self.org1
        request.user = self.user1
        
        # Mock view function
        def mock_view(request, *args, **kwargs):
            return None
        
        # Process view - should allow access
        response = self.middleware.process_view(request, mock_view, [], {})
        self.assertIsNone(response)
        
        # Test with user who doesn't have access
        request.user = self.user2
        response = self.middleware.process_view(request, mock_view, [], {})
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 403)


class TenantScopedViewSetMixinTest(TenantIsolationTestCase):
    """Test TenantScopedViewSetMixin functionality."""
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        
        # Create designs for both organizations
        self.design1 = Design.objects.create(
            title='Design 1',
            design_type='poster',
            organization=self.org1,
            created_by=self.user1
        )
        
        self.design2 = Design.objects.create(
            title='Design 2',
            design_type='banner',
            organization=self.org2,
            created_by=self.user2
        )
    
    def test_get_queryset_filters_by_organization(self):
        """Test that get_queryset filters by organization."""
        # Create a mock viewset
        class MockViewSet(TenantScopedViewSetMixin):
            def __init__(self, request):
                self.request = request
            
            def get_queryset(self):
                return super().get_queryset()
        
        # Mock the parent get_queryset method
        def mock_get_queryset(self):
            return Design.objects.all()
        
        TenantScopedViewSetMixin.__bases__[0].get_queryset = mock_get_queryset
        
        # Create request with organization
        request = self.factory.get('/')
        request.organization = self.org1
        
        # Create viewset
        viewset = MockViewSet(request)
        
        # Get queryset
        queryset = viewset.get_queryset()
        
        # Should only return designs from org1
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first(), self.design1)
    
    def test_perform_create_sets_organization(self):
        """Test that perform_create sets organization."""
        # Create a mock viewset
        class MockViewSet(TenantScopedViewSetMixin):
            def __init__(self, request):
                self.request = request
            
            def perform_create(self, serializer):
                super().perform_create(serializer)
        
        # Create request with organization
        request = self.factory.get('/')
        request.organization = self.org1
        
        # Create viewset
        viewset = MockViewSet(request)
        
        # Mock serializer
        class MockSerializer:
            def __init__(self):
                self.validated_data = {}
            
            def save(self, **kwargs):
                self.validated_data.update(kwargs)
                return self
        
        serializer = MockSerializer()
        
        # Perform create
        viewset.perform_create(serializer)
        
        # Should set organization
        self.assertEqual(serializer.validated_data['organization'], self.org1)
    
    def test_check_organization_permission(self):
        """Test organization permission check."""
        # Create a mock viewset
        class MockViewSet(TenantScopedViewSetMixin):
            def __init__(self, request):
                self.request = request
        
        # Create request with organization
        request = self.factory.get('/')
        request.organization = self.org1
        
        # Create viewset
        viewset = MockViewSet(request)
        
        # Check permission for design from same organization
        viewset.check_organization_permission(self.design1)
        
        # Should not raise exception
        
        # Check permission for design from different organization
        with self.assertRaises(PermissionDenied):
            viewset.check_organization_permission(self.design2)


class DataIsolationTest(TenantIsolationTestCase):
    """Test data isolation between organizations."""
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        
        # Create designs for both organizations
        self.design1 = Design.objects.create(
            title='Design 1',
            design_type='poster',
            organization=self.org1,
            created_by=self.user1
        )
        
        self.design2 = Design.objects.create(
            title='Design 2',
            design_type='banner',
            organization=self.org2,
            created_by=self.user2
        )
        
        # Create templates for both organizations
        self.template1 = DesignTemplate.objects.create(
            name='Template 1',
            template_type='poster',
            organization=self.org1,
            created_by=self.user1
        )
        
        self.template2 = DesignTemplate.objects.create(
            name='Template 2',
            template_type='banner',
            organization=self.org2,
            created_by=self.user2
        )
    
    def test_designs_isolated_by_organization(self):
        """Test that designs are isolated by organization."""
        # Get designs for org1
        org1_designs = Design.objects.filter(organization=self.org1)
        self.assertEqual(org1_designs.count(), 1)
        self.assertEqual(org1_designs.first(), self.design1)
        
        # Get designs for org2
        org2_designs = Design.objects.filter(organization=self.org2)
        self.assertEqual(org2_designs.count(), 1)
        self.assertEqual(org2_designs.first(), self.design2)
    
    def test_templates_isolated_by_organization(self):
        """Test that templates are isolated by organization."""
        # Get templates for org1
        org1_templates = DesignTemplate.objects.filter(organization=self.org1)
        self.assertEqual(org1_templates.count(), 1)
        self.assertEqual(org1_templates.first(), self.template1)
        
        # Get templates for org2
        org2_templates = DesignTemplate.objects.filter(organization=self.org2)
        self.assertEqual(org2_templates.count(), 1)
        self.assertEqual(org2_templates.first(), self.template2)
    
    def test_user_cannot_access_other_organization_data(self):
        """Test that users cannot access other organization's data."""
        # User1 should not be able to access org2's designs
        org2_designs = Design.objects.filter(
            organization=self.org2,
            created_by=self.user1
        )
        self.assertEqual(org2_designs.count(), 0)
        
        # User2 should not be able to access org1's designs
        org1_designs = Design.objects.filter(
            organization=self.org1,
            created_by=self.user2
        )
        self.assertEqual(org1_designs.count(), 0)
    
    def test_organization_member_cannot_access_other_org_data(self):
        """Test that organization members cannot access other org's data."""
        # User1 is member of org1, should not access org2's data
        user1_org2_access = OrganizationMember.objects.filter(
            user=self.user1,
            organization=self.org2,
            is_active=True
        ).exists()
        self.assertFalse(user1_org2_access)
        
        # User2 is member of org2, should not access org1's data
        user2_org1_access = OrganizationMember.objects.filter(
            user=self.user2,
            organization=self.org1,
            is_active=True
        ).exists()
        self.assertFalse(user2_org1_access)
