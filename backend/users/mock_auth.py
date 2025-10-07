"""
Mock authentication service for development and testing.
This provides a fallback when Clerk authentication is not available.
"""

from django.contrib.auth import get_user_model
from organizations.models import Organization, OrganizationMember
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


class MockAuthService:
    """
    Mock authentication service for development and testing.
    """
    
    @staticmethod
    def create_test_user(email="test@example.com", password="testpass123"):
        """Create a test user for development."""
        try:
            # Use filter().first() to avoid MultipleObjectsReturned error
            user = User.objects.filter(email=email).first()
            if user:
                logger.info(f"Test user {email} already exists")
                return user
        except Exception as e:
            logger.warning(f"Error checking for existing user {email}: {e}")
        
        # Create new user
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name="Test",
            last_name="User"
        )
        logger.info(f"Created test user: {email}")
        return user
    
    @staticmethod
    def create_test_organization(name="Test Organization", slug="test-org"):
        """Create a test organization for development."""
        try:
            # Use filter().first() to avoid MultipleObjectsReturned error
            org = Organization.objects.filter(slug=slug).first()
            if org:
                logger.info(f"Test organization {slug} already exists")
                return org
        except Exception as e:
            logger.warning(f"Error checking for existing organization {slug}: {e}")
        
        # Create new organization
        org = Organization.objects.create(
            name=name,
            slug=slug,
            description="Test organization for development"
        )
        logger.info(f"Created test organization: {name}")
        return org
    
    @staticmethod
    def create_test_membership(user, organization, role="admin"):
        """Create a test organization membership."""
        try:
            membership = OrganizationMember.objects.get(
                user=user,
                organization=organization
            )
            logger.info(f"Membership already exists: {user.email} -> {organization.name}")
            return membership
        except OrganizationMember.DoesNotExist:
            membership = OrganizationMember.objects.create(
                user=user,
                organization=organization,
                role=role,
                can_invite_users=True,
                can_manage_billing=True,
                can_export_data=True
            )
            logger.info(f"Created membership: {user.email} -> {organization.name} ({role})")
            return membership
    
    @staticmethod
    def setup_test_environment():
        """Set up complete test environment with user, organization, and membership."""
        # Create test user
        user = MockAuthService.create_test_user()
        
        # Create test organization
        organization = MockAuthService.create_test_organization()
        
        # Create membership
        membership = MockAuthService.create_test_membership(user, organization)
        
        return {
            'user': user,
            'organization': organization,
            'membership': membership
        }
    
    @staticmethod
    def get_test_headers(user_id=None, org_id=None):
        """Get test headers for API requests."""
        if not user_id or not org_id:
            # Get default test data
            test_data = MockAuthService.setup_test_environment()
            user_id = str(test_data['user'].id)
            org_id = str(test_data['organization'].id)
        
        return {
            'HTTP_X_DEV_USER_ID': user_id,
            'HTTP_X_DEV_ORG_ID': org_id,
            'HTTP_AUTHORIZATION': f'Bearer dev_{user_id}',
        }


def setup_mock_auth():
    """
    Set up mock authentication for development.
    Call this function to create test users and organizations.
    """
    return MockAuthService.setup_test_environment()
