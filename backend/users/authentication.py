"""
Custom authentication classes for the Framio application.
"""

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
from organizations.models import Organization, OrganizationMember
from .clerk_utils import get_or_create_user_from_clerk
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
        
        # In DEBUG mode, always try to authenticate even without CLERK_SECRET_KEY
        # In production, require CLERK_SECRET_KEY
        if not settings.DEBUG and not settings.CLERK_SECRET_KEY:
            # logger.warning("Clerk secret key not configured")  # Disabled - keys are configured
            return None
        
        # Get the authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        # Extract the token
        token = auth_header.split(' ')[1]
        
        # Check for Clerk user info in custom headers (sent from frontend)
        clerk_email = request.META.get('HTTP_X_CLERK_EMAIL')
        clerk_id = request.META.get('HTTP_X_CLERK_ID')
        clerk_first_name = request.META.get('HTTP_X_CLERK_FIRST_NAME')
        clerk_last_name = request.META.get('HTTP_X_CLERK_LAST_NAME')
        
        try:
            # For now, implement a basic token validation
            # In production, this should use Clerk's backend SDK
            user = self.validate_clerk_token(token, clerk_email, clerk_id, clerk_first_name, clerk_last_name)
            if user:
                logger.info(f"ClerkAuthentication: Successfully authenticated user {user.email}")
                return (user, None)
            else:
                logger.debug(f"ClerkAuthentication: Token validation returned None for token {token[:10]}...")
        except Exception as e:
            logger.error(f"Clerk authentication error: {e}")
            # In DEBUG mode, don't raise exception, just return None to allow fallback
            if not settings.DEBUG:
                raise AuthenticationFailed('Invalid authentication token')
        
        return None
    
    def validate_clerk_token(
        self, token, clerk_email=None, clerk_id=None,
        clerk_first_name=None, clerk_last_name=None
    ):
        """
        DEVELOPMENT MODE:
        Accept ANY valid-looking Bearer token and authenticate
        as the first user in the database.
        """
        from django.conf import settings
        User = get_user_model()

        # Only allow in DEBUG mode
        if settings.DEBUG:
            try:
                # Try returning the first user
                user = User.objects.first()
                if user:
                    logger.info(f"[DEV AUTH] Using first user: {user.email}")
                    return user

                # If no users exist, create fallback user
                logger.warning("[DEV AUTH] No users found, creating default user.")
                user = User.objects.create_user(
                    username="dev_user",
                    email="dev@example.com",
                    password="dev_password"
                )
                return user

            except Exception as e:
                logger.error(f"[DEV AUTH] Error: {e}", exc_info=True)
                return None

        # Production (Clerk real validation to be implemented later)
        # TODO: Implement proper Clerk JWT validation using clerk-backend-python
        # When implementing, decode JWT to get user info and auto-create users
        return None