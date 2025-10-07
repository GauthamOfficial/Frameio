"""
Test utilities for the Frameio backend.
"""

from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from organizations.models import Organization, OrganizationMember
from unittest.mock import patch
import uuid

User = get_user_model()


class TenantTestMixin:
    """
    Mixin for tests that need tenant/organization context.
    """
    
    def setUp(self):
        super().setUp()
        
        # Create test organization
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org",
            description="Test organization for unit tests"
        )
        
        # Create test user
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User"
        )
        
        # Create organization membership
        self.membership = OrganizationMember.objects.create(
            organization=self.organization,
            user=self.user,
            role="admin",
            can_invite_users=True,
            can_manage_billing=True,
            can_export_data=True
        )
        
        # Set up client with organization context
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Set organization context headers
        self.client.defaults['HTTP_X_DEV_ORG_ID'] = str(self.organization.id)
        self.client.defaults['HTTP_X_DEV_USER_ID'] = str(self.user.id)
        
        # Mock the organization context for views
        self.org_patcher = patch('organizations.middleware.get_current_organization')
        self.mock_get_org = self.org_patcher.start()
        self.mock_get_org.return_value = self.organization
        
        # Mock request.organization for views
        self.request_org_patcher = patch('ai_services.views.getattr')
        self.mock_getattr = self.request_org_patcher.start()
        self.mock_getattr.side_effect = lambda obj, attr, default: (
            self.organization if attr == 'organization' and hasattr(obj, 'organization') else default
        )
    
    def tearDown(self):
        self.org_patcher.stop()
        self.request_org_patcher.stop()
        super().tearDown()
    
    def make_request_with_org_context(self, method, url, **kwargs):
        """
        Make a request with proper organization context.
        """
        # Add organization context to the request
        if 'data' not in kwargs:
            kwargs['data'] = {}
        
        # Make the request
        response = getattr(self.client, method.lower())(url, **kwargs)
        
        # Manually set organization context on the response's request object
        if hasattr(response, 'wsgi_request'):
            response.wsgi_request.organization = self.organization
            response.wsgi_request.tenant = self.organization
        
        return response


class TenantAPITestCase(TenantTestMixin, APITestCase):
    """
    API test case with tenant/organization context.
    """
    pass


class TenantTestCase(TenantTestMixin, TestCase):
    """
    Regular test case with tenant/organization context.
    """
    pass


def create_test_organization(name="Test Org", slug=None):
    """Create a test organization."""
    if not slug:
        slug = f"test-org-{uuid.uuid4().hex[:8]}"
    
    return Organization.objects.create(
        name=name,
        slug=slug,
        description=f"Test organization: {name}"
    )


def create_test_user(email="test@example.com", password="testpass123"):
    """Create a test user."""
    return User.objects.create_user(
        username=email,
        email=email,
        password=password,
        first_name="Test",
        last_name="User"
    )


def create_test_membership(user, organization, role="admin"):
    """Create a test organization membership."""
    return OrganizationMember.objects.create(
        user=user,
        organization=organization,
        role=role,
        can_invite_users=role in ['admin', 'manager'],
        can_manage_billing=role == 'admin',
        can_export_data=role in ['admin', 'manager']
    )
