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
        # TODO: Implement Clerk authentication
        # For now, return None to fall back to other authentication methods
        return None