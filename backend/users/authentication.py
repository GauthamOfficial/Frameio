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
        
        try:
            # For now, implement a basic token validation
            # In production, this should use Clerk's backend SDK
            user = self.validate_clerk_token(token)
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
    
    def validate_clerk_token(self, token):
        """
        Validate Clerk JWT token and return user.
        This is a simplified implementation - in production, use Clerk's backend SDK.
        """
        from django.conf import settings
        
        # For development/testing, create a mock validation
        if settings.DEBUG:
            # Accept test_clerk_token or any token in development
            if token == 'test_clerk_token' or token:
                try:
                    logger.info(f"Development Clerk auth: Validating token {token[:10]}...")
                    # Try to get the first user
                    user = User.objects.first()
                    if not user:
                        # If no user exists, create a default development user
                        logger.warning("No users found, creating default development user")
                        try:
                            user = User.objects.create_user(
                                username='dev_user',
                                email='dev@example.com',
                                password='dev_password'
                            )
                            logger.info(f"Created default development user: {user.email}")
                        except Exception as create_error:
                            logger.error(f"Failed to create default development user: {create_error}")
                            # Try to get any user that might exist
                            user = User.objects.first()
                            if not user:
                                logger.error("No users exist and cannot create one. Please run: python create_test_user.py")
                                return None
                    else:
                        logger.info(f"Development Clerk auth: Found existing user {user.email}")
                    
                    logger.info(f"Development Clerk auth: Successfully authenticated user {user.email} with token {token[:10]}...")
                    return user
                except Exception as e:
                    logger.error(f"Development Clerk auth error: {e}", exc_info=True)
                    import traceback
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    return None
        
        # TODO: Implement proper Clerk JWT validation using clerk-backend-python
        # For now, return None to fall back to other authentication methods
        return None