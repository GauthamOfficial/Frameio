import jwt
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import authentication, exceptions
from rest_framework.authentication import BaseAuthentication
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class ClerkAuthentication(BaseAuthentication):
    """
    Custom authentication class for Clerk integration.
    """
    
    def authenticate(self, request):
        """
        Authenticate the request using Clerk JWT token.
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        
        try:
            # Verify the JWT token with Clerk
            user_data = self.verify_clerk_token(token)
            if not user_data:
                return None
            
            # Get or create user
            user = self.get_or_create_user(user_data)
            if not user:
                return None
            
            return (user, token)
            
        except Exception as e:
            logger.error(f"Clerk authentication error: {str(e)}")
            return None
    
    def verify_clerk_token(self, token):
        """
        Verify the JWT token with Clerk's public key.
        """
        try:
            # Get Clerk's public key
            jwks_url = f"https://api.clerk.com/v1/jwks"
            jwks_response = requests.get(jwks_url)
            jwks_response.raise_for_status()
            
            # Decode the JWT token
            header = jwt.get_unverified_header(token)
            kid = header.get('kid')
            
            if not kid:
                return None
            
            # Find the matching key
            jwks = jwks_response.json()
            key = None
            for jwk in jwks.get('keys', []):
                if jwk.get('kid') == kid:
                    key = jwt.algorithms.RSAAlgorithm.from_jwk(jwk)
                    break
            
            if not key:
                return None
            
            # Verify and decode the token
            payload = jwt.decode(
                token,
                key,
                algorithms=['RS256'],
                audience=settings.CLERK_PUBLISHABLE_KEY,
                issuer=f"https://clerk.{settings.CLERK_PUBLISHABLE_KEY.split('_')[1]}.lcl.dev"
            )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Clerk token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid Clerk token: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error verifying Clerk token: {str(e)}")
            return None
    
    def get_or_create_user(self, user_data):
        """
        Get or create user from Clerk user data.
        """
        try:
            clerk_id = user_data.get('sub')
            if not clerk_id:
                return None
            
            # Try to get existing user
            user = User.objects.filter(clerk_id=clerk_id).first()
            
            if user:
                # Update user data if needed
                self.update_user_from_clerk(user, user_data)
                return user
            
            # Create new user
            user = User.objects.create(
                clerk_id=clerk_id,
                username=user_data.get('username', ''),
                email=user_data.get('email', ''),
                first_name=user_data.get('given_name', ''),
                last_name=user_data.get('family_name', ''),
                is_verified=user_data.get('email_verified', False),
                clerk_created_at=user_data.get('iat'),
                clerk_updated_at=user_data.get('updated_at'),
            )
            
            return user
            
        except Exception as e:
            logger.error(f"Error getting/creating user: {str(e)}")
            return None
    
    def update_user_from_clerk(self, user, user_data):
        """
        Update user data from Clerk user data.
        """
        try:
            updated = False
            
            if user_data.get('email') and user.email != user_data['email']:
                user.email = user_data['email']
                updated = True
            
            if user_data.get('given_name') and user.first_name != user_data['given_name']:
                user.first_name = user_data['given_name']
                updated = True
            
            if user_data.get('family_name') and user.last_name != user_data['family_name']:
                user.last_name = user_data['family_name']
                updated = True
            
            if user_data.get('email_verified') is not None:
                user.is_verified = user_data['email_verified']
                updated = True
            
            if updated:
                user.clerk_updated_at = user_data.get('updated_at')
                user.save()
                
        except Exception as e:
            logger.error(f"Error updating user from Clerk: {str(e)}")


class ClerkWebhookAuthentication(BaseAuthentication):
    """
    Authentication for Clerk webhooks using webhook secrets.
    """
    
    def authenticate(self, request):
        """
        Authenticate Clerk webhook requests.
        """
        webhook_secret = request.META.get('HTTP_X_CLERK_WEBHOOK_SECRET')
        if not webhook_secret:
            return None
        
        # Verify webhook secret
        if webhook_secret != settings.CLERK_WEBHOOK_SECRET:
            return None
        
        # Create a system user for webhook operations
        system_user, created = User.objects.get_or_create(
            username='system',
            defaults={
                'email': 'system@frameio.com',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        
        return (system_user, None)
