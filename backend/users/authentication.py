"""
Custom authentication classes for the Framio application.
"""

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
from organizations.models import Organization, OrganizationMember
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


class DevelopmentAuthentication(BaseAuthentication):
    """
    Development authentication that bypasses Clerk for testing.
    This should only be used in development environments.
    """
    
    def authenticate(self, request):
        # Check if we're in development mode
        from django.conf import settings
        if not settings.DEBUG:
            return None
        
        # Look for development headers
        dev_user_id = request.META.get('HTTP_X_DEV_USER_ID')
        dev_org_id = request.META.get('HTTP_X_DEV_ORG_ID')
        
        logger.info(f"Development auth attempt: user_id={dev_user_id}, org_id={dev_org_id}")
        
        if not dev_user_id or not dev_org_id:
            logger.info("No development headers found")
            return None
        
        try:
            # Get the user
            user = User.objects.get(id=dev_user_id)
            
            # Get the organization
            organization = Organization.objects.get(id=dev_org_id)
            
            # Check if user is a member of the organization
            try:
                membership = OrganizationMember.objects.get(
                    user=user,
                    organization=organization,
                    is_active=True
                )
                request.organization = organization
                request.organization_membership = membership
                
                logger.info(f"Development auth: {user.email} -> {organization.name}")
                return (user, None)
                
            except OrganizationMember.DoesNotExist:
                logger.warning(f"User {user.email} not found in organization {organization.name}")
                return None
                
        except (User.DoesNotExist, Organization.DoesNotExist) as e:
            logger.warning(f"Development auth failed: {e}")
            return None


class ClerkAuthentication(BaseAuthentication):
    """
    Clerk authentication for production use.
    """
    
    def authenticate(self, request):
        from django.conf import settings
        
        # Check if Clerk is configured
        if not settings.CLERK_SECRET_KEY:
            # logger.warning("Clerk secret key not configured")  # Disabled - keys are configured
            return None
        
        # Get the authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        # Extract the token
        token = auth_header.split(' ')[1]
        
        try:
            # For now, implement a basic token validation
            # In production, this should use Clerk's backend SDK
            user = self.validate_clerk_token(token)
            if user:
                return (user, None)
        except Exception as e:
            logger.error(f"Clerk authentication error: {e}")
            raise AuthenticationFailed('Invalid authentication token')
        
        return None
    
    def validate_clerk_token(self, token):
        """
        Validate Clerk JWT token and return user.
        This is a simplified implementation - in production, use Clerk's backend SDK.
        """
        from django.conf import settings
        
        # For development/testing, create a mock validation
        if settings.DEBUG:
            # For development, accept any token and return the first user
            # This is a temporary solution for development
            try:
                user = User.objects.first()
                if user:
                    logger.info(f"Development Clerk auth: Using user {user.email}")
                    return user
            except Exception as e:
                logger.error(f"Development Clerk auth error: {e}")
                return None
        
        # TODO: Implement proper Clerk JWT validation using clerk-backend-python
        # For now, return None to fall back to other authentication methods
        return None